from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data_quality.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ALGORITHM: str = "HS256"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Data Quality Guardian"
    DEBUG: bool = False
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    ALLOWED_EXTENSIONS: str = "csv,xlsx,xls"
    
    # Ollama/LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2:2b"
    OLLAMA_TIMEOUT: int = 1000  # in seconds
    
    # Cleanup
    CLEANUP_DAYS: int = 1
    CLEANUP_EMPTY_CHATS_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False
    )

settings = Settings()
