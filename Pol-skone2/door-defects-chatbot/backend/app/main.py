import asyncio
import json
import logging

import chromadb
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.ingest import ingest_excel_files
from app.rag import stream_rag_response, get_vectorstore
from app.schemas import ChatRequest, IngestResponse, HealthResponse, StatsResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Door Defects RAG API",
    description="Lokalny chatbot RAG do analizy wad produkcyjnych drzwi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Zaindeksowanie plików Excel przy starcie...")
    try:
        # Uruchom w wątku żeby nie blokować event loop
        result = await asyncio.get_event_loop().run_in_executor(
            None, ingest_excel_files
        )
        logger.info(
            "Indeksowanie zakończone: %d dodanych, %d pominiętych, %d błędów",
            result.documents_added,
            result.documents_skipped,
            len(result.errors),
        )
    except Exception as e:
        logger.error("Błąd podczas indeksowania przy starcie: %s", e)


@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        try:
            async for event in stream_rag_response(
                question=request.question,
                history=request.history,
                top_k=request.top_k,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error("Błąd strumienia czatu: %s", e)
            error_event = {"type": "error", "content": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest():
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, ingest_excel_files
        )
        return result
    except Exception as e:
        logger.error("Błąd ręcznego indeksowania: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    ollama_ok = False
    llm_ready = False
    embed_ready = False

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                ollama_ok = True
                tags_data = resp.json()
                model_names = [m["name"].lower() for m in tags_data.get("models", [])]
                llm_ready = any(settings.llm_model.lower() in n for n in model_names)
                embed_ready = any(settings.embed_model.lower() in n for n in model_names)
    except Exception as e:
        logger.warning("Ollama niedostępna: %s", e)

    chroma_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"http://{settings.chroma_host}:{settings.chroma_port}/api/v1/heartbeat"
            )
            chroma_ok = resp.status_code == 200
    except Exception as e:
        logger.warning("ChromaDB niedostępna: %s", e)

    overall = "ok" if (ollama_ok and chroma_ok) else "degraded"
    return HealthResponse(
        status=overall,
        ollama=ollama_ok,
        chromadb=chroma_ok,
        llm_model_ready=llm_ready,
        embed_model_ready=embed_ready,
    )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    try:
        vs = get_vectorstore()
        collection = vs._collection
        count = collection.count()
        # Pobierz unikalne pliki źródłowe
        results = collection.get(include=["metadatas"])
        source_files = list({
            m.get("source_file", "")
            for m in (results.get("metadatas") or [])
            if m.get("source_file")
        })
        return StatsResponse(
            total_documents=count,
            source_files=sorted(source_files),
            collection_name=settings.chroma_collection,
        )
    except Exception as e:
        logger.error("Błąd pobierania statystyk: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
