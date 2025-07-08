"""
PostgreSQL-optimized configuration for StreamWorks-KI
Replaces SQLite with high-performance PostgreSQL setup
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class PostgreSQLSettings(BaseSettings):
    """PostgreSQL-specific configuration for production performance"""
    
    # Environment
    ENV: str = "development"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StreamWorks-KI"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ]
    
    # PostgreSQL Database Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "streamworks_ki"
    POSTGRES_USER: str = "streamworks"
    POSTGRES_PASSWORD: str = "streamworks_secure_2025"
    
    # Connection Pool Settings (optimized for RAG workloads)
    DB_POOL_SIZE: int = 20
    DB_POOL_MAX_OVERFLOW: int = 40  # Match env var name
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # 1 hour
    DB_POOL_PRE_PING: bool = True
    
    # PostgreSQL feature flag
    USE_POSTGRESQL: bool = True
    
    # Database URL for SQLAlchemy
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Synchronous database URL for migrations"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # RAG Settings (Q&A System)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DB_PATH: str = "./data/vector_db"
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    
    # ChromaDB Settings (disable telemetry)
    CHROMA_TELEMETRY_ENABLED: bool = False
    
    # === MISTRAL 7B OPTIMIERUNG ===
    OLLAMA_MODEL: str = "mistral:7b-instruct"
    LLM_ENABLED: bool = True
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Mistral-spezifische Parameter (performance-optimized)
    MODEL_TEMPERATURE: float = 0.3    # Reduced for consistency
    MODEL_TOP_P: float = 0.9          # Focused responses
    MODEL_TOP_K: int = 25             # Reduced for speed
    MODEL_MAX_TOKENS: int = 512       # Reduced for speed
    MODEL_REPEAT_PENALTY: float = 1.2 # Increased
    
    # Performance-Optimierung
    MODEL_THREADS: int = 8            # Für M4 MacBook optimal
    MODEL_BATCH_SIZE: int = 1         # Einzelne Requests
    MODEL_CONTEXT_WINDOW: int = 4096  # Reduced for performance
    
    # Deutsche Spezialisierung
    FORCE_GERMAN_RESPONSES: bool = True
    GERMAN_PROMPT_STYLE: str = "professional"
    USE_GERMAN_TECHNICAL_TERMS: bool = True
    
    # XML Generation Settings (RAG-basiert)  
    XML_GENERATION_ENABLED: bool = True
    
    # Legacy Generation Parameters (für Kompatibilität)
    MAX_NEW_TOKENS: int = 512
    TOP_P: float = 0.9
    DEVICE: str = "mps"  # auto, cuda, cpu, mps
    
    # Training Data Paths
    TRAINING_DATA_PATH: str = "./data/training_data"
    HELP_DATA_PATH: str = "./data/training_data/optimized/help_data"
    XML_TEMPLATE_PATH: str = "./data/training_data/stream_templates"
    
    # Services Toggle
    RAG_ENABLED: bool = True
    TRAINING_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Chat & API Settings (PostgreSQL-optimized)
    CHAT_TIMEOUT_SECONDS: float = 15.0   # Reduced with PostgreSQL
    API_REQUEST_TIMEOUT: float = 30.0    # Reduced with PostgreSQL
    
    # Performance Monitoring
    ENABLE_QUERY_LOGGING: bool = True
    SLOW_QUERY_THRESHOLD: float = 1.0    # Log queries > 1s
    
    # Citation System (JSON-optimized)
    MAX_CITATIONS_PER_RESPONSE: int = 5
    CITATION_RELEVANCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
postgres_settings = PostgreSQLSettings()

# Backward compatibility - expose as 'settings' 
settings = postgres_settings