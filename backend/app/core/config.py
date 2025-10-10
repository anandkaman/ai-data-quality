from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Data Quality Guardian"
    
    # Database Settings (SQLite for local development)
    DATABASE_URL: str = "sqlite:///./data_quality.db"
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2:2b"
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # File Upload Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # ML Settings
    ANOMALY_CONTAMINATION: float = 0.1
    RANDOM_STATE: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()