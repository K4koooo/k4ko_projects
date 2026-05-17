import logging
from typing import AsyncGenerator

import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.documents import Document

from app.config import settings
from app.schemas import HistoryMessage, SourceDocument

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Jesteś asystentem ds. jakości produkcji drzwi i okien.
Odpowiadasz WYŁĄCZNIE na podstawie dostarczonych danych z bazy wiedzy.

Zasady:
1. Jeśli informacja nie wynika z kontekstu, odpowiedz: "Nie znalazłem tej informacji w zaindeksowanych danych."
2. Cytuj konkretne dane: podaj plik źródłowy, arkusz i numer wiersza.
3. Odpowiadaj po polsku, technicznie ale zrozumiale.
4. Formatuj odpowiedzi w Markdown: używaj list (-), pogrubień (**tekst**) i nagłówków (##) gdzie stosowne.
5. Nie wymyślaj danych – operuj wyłącznie na faktach z kontekstu."""


def _build_context(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        header = (
            f"[Dokument {i}] "
            f"Plik: {meta.get('source_file', 'nieznany')} | "
            f"Arkusz: {meta.get('sheet_name', '?')} | "
            f"Wiersz: {meta.get('row_number', '?')}"
        )
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _format_history(history: list[HistoryMessage]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:  # Ostatnie 3 tury (6 wiadomości)
        role = "Użytkownik" if msg.role == "user" else "Asystent"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def _build_prompt(question: str, context: str, history: list[HistoryMessage]) -> str:
    history_str = _format_history(history)
    history_section = f"\nHistoria rozmowy:\n{history_str}\n" if history_str else ""
    return f"""{SYSTEM_PROMPT}

Dane z bazy wiedzy:
{context}
{history_section}
Użytkownik: {question}
Asystent:"""


def get_vectorstore() -> Chroma:
    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )
    return Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
        client=client,
    )


async def stream_rag_response(
    question: str,
    history: list[HistoryMessage],
    top_k: int,
) -> AsyncGenerator[dict, None]:
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )

    try:
        docs: list[Document] = await retriever.ainvoke(question)
    except Exception as e:
        logger.error("Błąd retrievalu: %s", e)
        yield {"type": "error", "content": f"Błąd wyszukiwania w bazie: {e}"}
        return

    if not docs:
        yield {"type": "token", "content": "Nie znalazłem żadnych pasujących danych w bazie wiedzy."}
        yield {"type": "sources", "content": []}
        return

    context = _build_context(docs)
    prompt = _build_prompt(question, context, history)

    llm = OllamaLLM(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature,
    )

    try:
        async for chunk in llm.astream(prompt):
            if chunk:
                yield {"type": "token", "content": chunk}
    except Exception as e:
        logger.error("Błąd generowania LLM: %s", e)
        yield {"type": "error", "content": f"Błąd modelu językowego: {e}"}
        return

    sources = [
        SourceDocument(
            source_file=doc.metadata.get("source_file", ""),
            sheet_name=doc.metadata.get("sheet_name", ""),
            row_number=doc.metadata.get("row_number", 0),
            content=doc.page_content,
            metadata=doc.metadata,
        ).model_dump()
        for doc in docs
    ]
    yield {"type": "sources", "content": sources}
