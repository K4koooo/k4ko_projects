from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    ollama_base_url: str = "http://ollama:11434"
    llm_model: str = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
    embed_model: str = "nomic-embed-text"
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "door_defects"
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    temperature: float = 0.2
    excel_dir: Path = Path("/app/data/excel")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
