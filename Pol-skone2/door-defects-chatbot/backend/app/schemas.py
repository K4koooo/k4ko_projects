from pydantic import BaseModel, Field
from typing import Any


class HistoryMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4096)
    history: list[HistoryMessage] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceDocument(BaseModel):
    source_file: str
    sheet_name: str
    row_number: int
    content: str
    metadata: dict[str, Any]


class IngestResponse(BaseModel):
    status: str
    files_processed: int
    documents_added: int
    documents_skipped: int
    errors: list[str]


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded" | "error"
    ollama: bool
    chromadb: bool
    llm_model_ready: bool
    embed_model_ready: bool


class StatsResponse(BaseModel):
    total_documents: int
    source_files: list[str]
    collection_name: str
