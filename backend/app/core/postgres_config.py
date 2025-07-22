"""
PostgreSQL Configuration - Production-ready Setup
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class PostgreSQLSettings(BaseSettings):
    """PostgreSQL-optimierte Konfiguration für Enterprise-Einsatz"""
    
    # === APPLICATION ===
    APP_NAME: str = "Streamworks-KI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # === DATABASE (PostgreSQL) ===
    # Connection
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "streamworks_ki"
    POSTGRES_USER: str = "streamworks"
    POSTGRES_PASSWORD: str = "streamworks_secure_2025"
    
    # Connection Pool (optimiert für RAG workloads)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # === STORAGE ===
    DATA_PATH: str = "./data"
    UPLOAD_MAX_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".md", ".docx", ".xml", ".json"]
    
    # === LLM CONFIGURATION ===
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b-instruct"
    LLM_TIMEOUT: int = 30
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.7
    
    # === RAG SYSTEM ===
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_CHUNKS: int = 5
    MIN_RELEVANCE_SCORE: float = 0.7
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # === PERFORMANCE MONITORING ===
    ENABLE_METRICS: bool = True
    METRICS_RETENTION_DAYS: int = 30
    SLOW_QUERY_THRESHOLD: float = 1.0
    ENABLE_PERFORMANCE_TRACKING: bool = True
    
    # === API CONFIGURATION ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173"  # Vite dev server
    ]
    
    # Legacy compatibility attributes
    ALLOWED_ORIGINS: List[str] = CORS_ORIGINS
    ENV: str = "development"
    RAG_ENABLED: bool = True
    LLM_ENABLED: bool = True
    TRAINING_ENABLED: bool = True
    XML_GENERATION_ENABLED: bool = True
    FORCE_GERMAN_RESPONSES: bool = True
    
    # LLM Model Parameters
    MODEL_TEMPERATURE: float = LLM_TEMPERATURE
    MODEL_TOP_P: float = 0.9
    MODEL_TOP_K: int = 50
    MODEL_MAX_TOKENS: int = LLM_MAX_TOKENS
    MODEL_REPEAT_PENALTY: float = 1.1
    MODEL_CONTEXT_WINDOW: int = 4096
    MODEL_THREADS: int = 4
    
    # RAG Parameters
    RAG_CHUNK_SIZE: int = CHUNK_SIZE
    RAG_CHUNK_OVERLAP: int = CHUNK_OVERLAP
    RAG_TOP_K: int = TOP_K_CHUNKS
    
    # Additional Legacy
    MAX_NEW_TOKENS: int = LLM_MAX_TOKENS
    TEMPERATURE: float = LLM_TEMPERATURE
    DEVICE: str = "cpu"
    PROJECT_NAME: str = APP_NAME
    
    # Legacy Path Settings
    TRAINING_DATA_PATH: str = "./data/training"
    HELP_DATA_PATH: str = "./data/help"
    XML_TEMPLATE_PATH: str = "./data/xml_templates"
    
    # === ANALYTICS (für Bachelor-Arbeit) ===
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_BATCH_SIZE: int = 100
    ANALYTICS_FLUSH_INTERVAL: int = 60  # seconds
    
    # === SECURITY ===
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def database_url(self) -> str:
        """Konstruiere Database URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def async_database_url(self) -> str:
        """Async Database URL für SQLAlchemy"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Legacy compatibility
    @property
    def DATABASE_URL(self) -> str:
        """Legacy database URL property"""
        return self.async_database_url
    
    def get_db_config(self) -> dict:
        """Database Engine Configuration"""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "echo": self.DB_ECHO,
            "pool_pre_ping": True
        }

# Global settings instance
settings = PostgreSQLSettings()