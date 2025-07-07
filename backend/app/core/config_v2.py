"""
Clean Configuration Management v2.0
Production-ready configuration with validation and environment handling
"""
from pydantic import BaseSettings, validator, Field
from pydantic_settings import SettingsConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseType(str, Enum):
    """Database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class Settings(BaseSettings):
    """
    Comprehensive application settings with validation
    
    Environment variables override default values
    Use .env files for local development
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False
    )
    
    # === CORE APPLICATION SETTINGS ===
    
    app_name: str = Field(default="StreamWorks-KI", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1000, le=65535, description="API port")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", min_length=32)
    access_token_expire_minutes: int = Field(default=30, ge=1, le=10080)  # Max 1 week
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3001"
        ],
        description="Allowed CORS origins"
    )
    
    # === DATABASE CONFIGURATION ===
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./streamworks_ki.db",
        description="Database connection URL"
    )
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE, description="Database type")
    
    # Database Connection Pool
    db_pool_size: int = Field(default=10, ge=1, le=100, description="Database pool size")
    db_max_overflow: int = Field(default=20, ge=0, le=100, description="Database max overflow")
    db_pool_timeout: int = Field(default=30, ge=1, le=300, description="Database pool timeout")
    db_pool_recycle: int = Field(default=3600, ge=300, le=86400, description="Database pool recycle time")
    
    # === FILE STORAGE CONFIGURATION ===
    
    data_directory: Path = Field(default=Path("./data"), description="Base data directory")
    training_data_path: Path = Field(default=Path("./data/training_data"), description="Training data path")
    vector_db_path: Path = Field(default=Path("./data/vector_db"), description="Vector database path")
    upload_max_size: int = Field(default=50 * 1024 * 1024, description="Max upload size (50MB)")  # 50MB
    
    # === RAG SYSTEM CONFIGURATION ===
    
    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    embedding_device: str = Field(default="cpu", description="Device for embeddings (cpu/cuda)")
    
    # Text Processing
    chunk_size: int = Field(default=500, ge=100, le=2000, description="Text chunk size")
    chunk_overlap: int = Field(default=50, ge=0, le=500, description="Text chunk overlap")
    
    # Retrieval
    rag_top_k: int = Field(default=5, ge=1, le=50, description="Top K documents for RAG")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    
    # ChromaDB
    chroma_telemetry: bool = Field(default=False, description="ChromaDB telemetry")
    chroma_collection_name: str = Field(default="streamworks_docs", description="ChromaDB collection name")
    
    # === LLM CONFIGURATION ===
    
    # Ollama Connection
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama server URL")
    ollama_model: str = Field(default="mistral:7b-instruct", description="Ollama model name")
    ollama_timeout: int = Field(default=120, ge=30, le=600, description="Ollama request timeout")
    
    # Model Parameters
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="LLM temperature")
    llm_top_p: float = Field(default=0.9, ge=0.1, le=1.0, description="LLM top-p")
    llm_top_k: int = Field(default=25, ge=1, le=100, description="LLM top-k")
    llm_max_tokens: int = Field(default=2048, ge=100, le=8192, description="LLM max tokens")
    llm_repeat_penalty: float = Field(default=1.2, ge=1.0, le=2.0, description="LLM repeat penalty")
    
    # Performance
    llm_context_window: int = Field(default=8192, ge=1024, le=32768, description="LLM context window")
    llm_batch_size: int = Field(default=1, ge=1, le=10, description="LLM batch size")
    llm_threads: int = Field(default=8, ge=1, le=32, description="LLM threads")
    
    # Language Settings
    force_german: bool = Field(default=True, description="Force German responses")
    prompt_style: str = Field(default="professional", description="Prompt style")
    use_german_terms: bool = Field(default=True, description="Use German technical terms")
    
    # === LOGGING CONFIGURATION ===
    
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_rotation: bool = Field(default=True, description="Enable log rotation")
    log_max_size: str = Field(default="100MB", description="Max log file size")
    log_backup_count: int = Field(default=5, ge=1, le=20, description="Log backup files count")
    
    # === MONITORING CONFIGURATION ===
    
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=8001, ge=1000, le=65535, description="Metrics server port")
    health_check_interval: int = Field(default=30, ge=10, le=300, description="Health check interval")
    
    # Performance monitoring
    slow_request_threshold: float = Field(default=2.0, ge=0.1, le=60.0, description="Slow request threshold")
    memory_warning_threshold: float = Field(default=0.8, ge=0.5, le=0.95, description="Memory warning threshold")
    
    # === CACHING CONFIGURATION ===
    
    enable_caching: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, ge=60, le=86400, description="Cache TTL seconds")
    cache_max_size: int = Field(default=1000, ge=10, le=10000, description="Cache max size")
    
    # === FEATURE FLAGS ===
    
    enable_xml_generation: bool = Field(default=True, description="Enable XML generation")
    enable_citation_service: bool = Field(default=True, description="Enable citation service")
    enable_smart_search: bool = Field(default=True, description="Enable smart search")
    enable_file_processing: bool = Field(default=True, description="Enable file processing")
    
    # === EXPERIMENTAL FEATURES ===
    
    experimental_features: bool = Field(default=False, description="Enable experimental features")
    
    # === VALIDATORS ===
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Database URL cannot be empty")
        return v
    
    @validator("data_directory", "training_data_path", "vector_db_path")
    def validate_paths(cls, v):
        """Ensure paths exist or can be created"""
        if isinstance(v, str):
            v = Path(v)
        
        try:
            v.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create directory {v}: {e}")
        
        return v
    
    @validator("ollama_host")
    def validate_ollama_host(cls, v):
        """Validate Ollama host URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Ollama host must be a valid HTTP/HTTPS URL")
        return v
    
    @validator("allowed_origins")
    def validate_cors_origins(cls, v):
        """Validate CORS origins"""
        if not v:
            return ["*"]  # Allow all if none specified
        
        for origin in v:
            if not origin.startswith(("http://", "https://")) and origin != "*":
                raise ValueError(f"Invalid CORS origin: {origin}")
        
        return v
    
    # === COMPUTED PROPERTIES ===
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def database_echo(self) -> bool:
        """Whether to echo SQL statements"""
        return self.is_development and self.debug
    
    @property
    def training_data_absolute(self) -> Path:
        """Get absolute path to training data"""
        return self.training_data_path.resolve()
    
    @property
    def vector_db_absolute(self) -> Path:
        """Get absolute path to vector database"""
        return self.vector_db_path.resolve()
    
    # === CONFIGURATION METHODS ===
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dict"""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration dict"""
        return {
            "host": self.ollama_host,
            "model": self.ollama_model,
            "timeout": self.ollama_timeout,
            "temperature": self.llm_temperature,
            "top_p": self.llm_top_p,
            "top_k": self.llm_top_k,
            "max_tokens": self.llm_max_tokens,
            "repeat_penalty": self.llm_repeat_penalty,
            "context_window": self.llm_context_window,
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration dict"""
        return {
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.rag_top_k,
            "similarity_threshold": self.similarity_threshold,
            "vector_db_path": str(self.vector_db_absolute),
        }
    
    def validate_runtime_config(self) -> List[str]:
        """Validate runtime configuration and return warnings"""
        warnings = []
        
        # Check critical paths
        if not self.training_data_absolute.exists():
            warnings.append(f"Training data path does not exist: {self.training_data_absolute}")
        
        # Check production settings
        if self.is_production:
            if self.secret_key == "dev-secret-key-change-in-production":
                warnings.append("Using default secret key in production!")
            
            if self.debug:
                warnings.append("Debug mode enabled in production!")
        
        # Check performance settings
        if self.llm_max_tokens > self.llm_context_window:
            warnings.append("LLM max tokens exceeds context window")
        
        return warnings


# Create global settings instance
def get_settings() -> Settings:
    """Get validated settings instance"""
    settings = Settings()
    
    # Validate runtime configuration
    warnings = settings.validate_runtime_config()
    for warning in warnings:
        logger.warning(f"Configuration warning: {warning}")
    
    return settings


# Global settings instance
settings = get_settings()