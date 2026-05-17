import hashlib
import logging
from pathlib import Path

import chromadb
import pandas as pd
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from app.config import settings
from app.schemas import IngestResponse

logger = logging.getLogger(__name__)


def _make_doc_id(source_file: str, sheet_name: str, row_number: int) -> str:
    raw = f"{source_file}::{sheet_name}::{row_number}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _row_to_text(row: pd.Series, source_file: str, sheet_name: str, row_number: int) -> str:
    parts = [f"Plik: {source_file}", f"Arkusz: {sheet_name}", f"Wiersz: {row_number}"]
    for col, val in row.items():
        if pd.notna(val) and str(val).strip():
            parts.append(f"{col}: {val}")
    return " | ".join(parts)


def _parse_excel(file_path: Path) -> list[tuple[Document, str]]:
    """Zwraca listę (Document, doc_id) dla wszystkich niepustych wierszy."""
    results: list[tuple[Document, str]] = []
    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
    except Exception as e:
        logger.error("Nie można otworzyć pliku %s: %s", file_path.name, e)
        return results

    for sheet_name in xl.sheet_names:
        try:
            df = xl.parse(sheet_name)
            if df.empty:
                logger.info("Arkusz %s w %s jest pusty, pomijam.", sheet_name, file_path.name)
                continue

            df = df.dropna(how="all")
            df.columns = [str(c).strip() for c in df.columns]

            for idx, row in df.iterrows():
                row_number = int(idx) + 2  # +1 nagłówek, +1 bo 0-indexed
                if row.isna().all():
                    continue

                text = _row_to_text(row, file_path.name, sheet_name, row_number)
                doc_id = _make_doc_id(file_path.name, sheet_name, row_number)
                metadata = {
                    "source_file": file_path.name,
                    "sheet_name": sheet_name,
                    "row_number": row_number,
                }
                # Dodaj kolumny jako metadane (tylko skalarne wartości)
                for col, val in row.items():
                    if pd.notna(val):
                        metadata[str(col)] = str(val)

                results.append((Document(page_content=text, metadata=metadata), doc_id))

        except Exception as e:
            logger.error("Błąd parsowania arkusza %s w %s: %s", sheet_name, file_path.name, e)

    return results


def ingest_excel_files(excel_dir: Path | None = None) -> IngestResponse:
    if excel_dir is None:
        excel_dir = settings.excel_dir

    files = list(excel_dir.glob("*.xlsx"))
    if not files:
        logger.warning("Brak plików .xlsx w %s", excel_dir)
        return IngestResponse(
            status="ok",
            files_processed=0,
            documents_added=0,
            documents_skipped=0,
            errors=[]
        )

    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )

    chroma_client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )

    vectorstore = Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
        client=chroma_client,
    )

    total_added = 0
    total_skipped = 0
    errors: list[str] = []

    for file_path in files:
        logger.info("Przetwarzanie: %s", file_path.name)
        doc_pairs = _parse_excel(file_path)

        if not doc_pairs:
            errors.append(f"Brak danych w {file_path.name}")
            continue

        docs, doc_ids = zip(*doc_pairs)
        docs = list(docs)
        doc_ids = list(doc_ids)

        # Sprawdź które ID już istnieją
        try:
            existing = vectorstore._collection.get(ids=doc_ids, include=[])
            existing_ids = set(existing["ids"])
        except Exception:
            existing_ids = set()

        new_pairs = [(d, i) for d, i in zip(docs, doc_ids) if i not in existing_ids]

        if not new_pairs:
            logger.info("Wszystkie %d dokumentów z %s już zaindeksowane.", len(doc_ids), file_path.name)
            total_skipped += len(doc_ids)
            continue

        new_docs, new_ids = zip(*new_pairs)
        total_skipped += len(doc_ids) - len(new_pairs)

        try:
            vectorstore.add_documents(list(new_docs), ids=list(new_ids))
            total_added += len(new_pairs)
            logger.info("Zaindeksowano %d nowych dokumentów z %s.", len(new_pairs), file_path.name)
        except Exception as e:
            msg = f"Błąd indeksowania {file_path.name}: {e}"
            logger.error(msg)
            errors.append(msg)

    status = "ok" if not errors else "partial"
    return IngestResponse(
        status=status,
        files_processed=len(files),
        documents_added=total_added,
        documents_skipped=total_skipped,
        errors=errors,
    )
