"""
Unified Configuration Management
Combines config.py and config_v2.py with backward compatibility
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
import logging
import os
from .security import (
    get_secure_config_value, 
    SecureConfigValidator, 
    ProductionSecrets,
    validate_production_config,
    SecurityError
)

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


class Settings(BaseSettings):
    """
    Unified application settings with validation and backward compatibility
    Supports both legacy (config.py) and new (config_v2.py) field names
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True  # Keep True for backward compatibility
    )
    
    # === CORE APPLICATION SETTINGS ===
    
    # Legacy naming (config.py) with new features
    ENV: str = Field(default="development", description="Environment (legacy name)")
    PROJECT_NAME: str = Field(default="StreamWorks-KI", description="Application name")
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    
    # New naming (config_v2.py) mapped to legacy
    @property
    def environment(self) -> Environment:
        """Map ENV to environment enum"""
        return Environment(self.ENV.lower())
    
    @property
    def app_name(self) -> str:
        """Alias for PROJECT_NAME"""
        return self.PROJECT_NAME
    
    @property
    def api_v1_prefix(self) -> str:
        """Alias for API_V1_STR"""
        return self.API_V1_STR
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1000, le=65535, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Security - PRODUCTION HARDENED
    secret_key: str = Field(
        default_factory=lambda: get_secure_config_value(
            "SECRET_KEY", 
            ProductionSecrets.generate_secret_key()
        ),
        min_length=32,
        description="Cryptographically secure secret key"
    )
    access_token_expire_minutes: int = Field(default=30, ge=1, le=10080)
    
    # Additional security settings
    jwt_algorithm: str = Field(default="HS256")
    password_reset_expire_minutes: int = Field(default=15, ge=5, le=60)
    max_login_attempts: int = Field(default=5, ge=3, le=10)
    lockout_duration_minutes: int = Field(default=30, ge=10, le=1440)
    
    # === CORS CONFIGURATION ===
    
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3001"
        ],
        description="Allowed CORS origins"
    )
    
    @property
    def allowed_origins(self) -> List[str]:
        """Alias for ALLOWED_ORIGINS"""
        return self.ALLOWED_ORIGINS
    
    # === DATABASE CONFIGURATION ===
    
    DATABASE_URL: str = Field(
        default_factory=lambda: get_secure_config_value(
            "DATABASE_URL", 
            "sqlite:///./streamworks_ki.db" if os.getenv("ENV", "development") == "development" else None
        ),
        description="Database connection URL with security validation"
    )
    
    # Database security settings
    db_ssl_required: bool = Field(
        default_factory=lambda: os.getenv("ENV", "development") == "production"
    )
    db_ssl_ca_cert: Optional[str] = Field(
        default_factory=lambda: get_secure_config_value("DB_SSL_CA_CERT")
    )
    db_ssl_client_cert: Optional[str] = Field(
        default_factory=lambda: get_secure_config_value("DB_SSL_CLIENT_CERT")
    )
    db_ssl_client_key: Optional[str] = Field(
        default_factory=lambda: get_secure_config_value("DB_SSL_CLIENT_KEY")
    )
    
    @property
    def database_url(self) -> str:
        """Alias for DATABASE_URL"""
        return self.DATABASE_URL
    
    # Database Connection Pool (new features)
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=1, le=300)
    db_pool_recycle: int = Field(default=3600, ge=300, le=86400)
    
    # === FILE STORAGE CONFIGURATION ===
    
    TRAINING_DATA_PATH: str = Field(default="./data/training_data")
    HELP_DATA_PATH: str = Field(default="./data/training_data/optimized/help_data")
    XML_TEMPLATE_PATH: str = Field(default="./data/training_data/stream_templates")
    VECTOR_DB_PATH: str = Field(default="./data/vector_db")
    
    @property
    def data_directory(self) -> Path:
        """Base data directory"""
        return Path("./data")
    
    @property
    def training_data_path(self) -> Path:
        """Path object for training data"""
        return Path(self.TRAINING_DATA_PATH)
    
    @property
    def vector_db_path(self) -> Path:
        """Path object for vector DB"""
        return Path(self.VECTOR_DB_PATH)
    
    upload_max_size: int = Field(default=50 * 1024 * 1024, description="Max upload size (50MB)")
    
    # === RAG SYSTEM CONFIGURATION ===
    
    # Embedding Model - Updated for better German language support
    EMBEDDING_MODEL: str = Field(
        default="intfloat/multilingual-e5-large",
        description="Multilingual E5 Large - excellent German support with 1024 dimensions"
    )
    embedding_device: str = Field(default="mps", description="Device for embeddings (MPS for Apple Silicon)")
    
    # Text Processing - OPTIMIZED FOR GERMAN PRODUCTION DOCUMENTS
    RAG_CHUNK_SIZE: int = Field(default=800, ge=100, le=2000, description="Larger chunks preserve context better")
    RAG_CHUNK_OVERLAP: int = Field(default=150, ge=0, le=500, description="Generous overlap prevents context loss")
    RAG_TOP_K: int = Field(default=7, ge=1, le=50, description="More results for better coverage")
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Lower threshold for better recall")
    
    # Property aliases for new naming
    @property
    def embedding_model(self) -> str:
        return self.EMBEDDING_MODEL
    
    @property
    def chunk_size(self) -> int:
        return self.RAG_CHUNK_SIZE
    
    @property
    def chunk_overlap(self) -> int:
        return self.RAG_CHUNK_OVERLAP
    
    @property
    def rag_top_k(self) -> int:
        return self.RAG_TOP_K
    
    # ChromaDB
    CHROMA_TELEMETRY_ENABLED: bool = Field(default=False)
    chroma_collection_name: str = Field(default="streamworks_docs")
    
    @property
    def chroma_telemetry(self) -> bool:
        return not self.CHROMA_TELEMETRY_ENABLED
    
    # === LLM CONFIGURATION ===
    
    # Ollama Connection
    OLLAMA_HOST: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="mistral:7b-instruct")
    ollama_timeout: int = Field(default=120, ge=30, le=600)
    
    @property
    def ollama_host(self) -> str:
        return self.OLLAMA_HOST
    
    @property
    def ollama_model(self) -> str:
        return self.OLLAMA_MODEL
    
    # Model Parameters (legacy naming)
    MODEL_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    MODEL_TOP_P: float = Field(default=0.95, ge=0.1, le=1.0)
    MODEL_TOP_K: int = Field(default=40, ge=1, le=100)
    MODEL_MAX_TOKENS: int = Field(default=2048, ge=100, le=8192)
    MODEL_REPEAT_PENALTY: float = Field(default=1.1, ge=1.0, le=2.0)
    MODEL_CONTEXT_WINDOW: int = Field(default=8192, ge=1024, le=32768)
    MODEL_BATCH_SIZE: int = Field(default=1, ge=1, le=10)
    MODEL_THREADS: int = Field(default=8, ge=1, le=32)
    
    # Property aliases for new naming
    @property
    def llm_temperature(self) -> float:
        return self.MODEL_TEMPERATURE
    
    @property
    def llm_top_p(self) -> float:
        return self.MODEL_TOP_P
    
    @property
    def llm_top_k(self) -> int:
        return self.MODEL_TOP_K
    
    @property
    def llm_max_tokens(self) -> int:
        return self.MODEL_MAX_TOKENS
    
    @property
    def llm_repeat_penalty(self) -> float:
        return self.MODEL_REPEAT_PENALTY
    
    @property
    def llm_context_window(self) -> int:
        return self.MODEL_CONTEXT_WINDOW
    
    @property
    def llm_batch_size(self) -> int:
        return self.MODEL_BATCH_SIZE
    
    @property
    def llm_threads(self) -> int:
        return self.MODEL_THREADS
    
    # Language Settings
    FORCE_GERMAN_RESPONSES: bool = Field(default=True)
    GERMAN_PROMPT_STYLE: str = Field(default="professional")
    USE_GERMAN_TECHNICAL_TERMS: bool = Field(default=True)
    
    @property
    def force_german(self) -> bool:
        return self.FORCE_GERMAN_RESPONSES
    
    @property
    def prompt_style(self) -> str:
        return self.GERMAN_PROMPT_STYLE
    
    @property
    def use_german_terms(self) -> bool:
        return self.USE_GERMAN_TECHNICAL_TERMS
    
    # === SERVICE TOGGLES ===
    
    LLM_ENABLED: bool = Field(default=True)
    RAG_ENABLED: bool = Field(default=True)
    TRAINING_ENABLED: bool = Field(default=True)
    XML_GENERATION_ENABLED: bool = Field(default=True)
    
    # Feature flags (new)
    enable_citation_service: bool = Field(default=True)
    enable_smart_search: bool = Field(default=True)
    enable_file_processing: bool = Field(default=True)
    experimental_features: bool = Field(default=False)
    
    # === LOGGING CONFIGURATION ===
    
    LOG_LEVEL: str = Field(default="INFO")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_file: Optional[str] = Field(default=None)
    log_rotation: bool = Field(default=True)
    log_max_size: str = Field(default="100MB")
    log_backup_count: int = Field(default=5, ge=1, le=20)
    
    @property
    def log_level(self) -> LogLevel:
        return LogLevel(self.LOG_LEVEL)
    
    # === PERFORMANCE & MONITORING ===
    
    CHAT_TIMEOUT_SECONDS: float = Field(default=30.0)
    API_REQUEST_TIMEOUT: float = Field(default=60.0)
    
    # New monitoring features
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=8001, ge=1000, le=65535)
    health_check_interval: int = Field(default=30, ge=10, le=300)
    slow_request_threshold: float = Field(default=2.0, ge=0.1, le=60.0)
    memory_warning_threshold: float = Field(default=0.8, ge=0.5, le=0.95)
    
    # === CACHING CONFIGURATION ===
    
    enable_caching: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=60, le=86400)
    cache_max_size: int = Field(default=1000, ge=10, le=10000)
    
    # === LEGACY COMPATIBILITY ===
    
    MAX_NEW_TOKENS: int = Field(default=512)  # Legacy
    TOP_P: float = Field(default=0.9)  # Legacy duplicate
    DEVICE: str = Field(default="mps")  # auto, cuda, cpu, mps
    
    # === VALIDATORS ===
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v, values):
        """Validate database URL format and security"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Database URL cannot be empty")
        
        # Get environment from values or ENV variable
        env = values.get('ENV') or os.getenv('ENV', 'development')
        
        # Security validation
        validator = SecureConfigValidator()
        if not validator.validate_database_url(v, env):
            raise ValueError(f"Database URL fails security validation for {env} environment")
        
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validate secret key strength"""
        validator = SecureConfigValidator()
        if not validator.validate_secret_key(v):
            raise ValueError("Secret key is too weak or uses default value. Use a cryptographically secure key.")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def validate_cors_origins(cls, v, values):
        """Validate CORS origins for security"""
        env = values.get('ENV') or os.getenv('ENV', 'development')
        validator = SecureConfigValidator()
        if not validator.validate_cors_origins(v, env):
            raise ValueError(f"CORS origins configuration not secure for {env} environment")
        return v
    
    @validator("TRAINING_DATA_PATH", "VECTOR_DB_PATH")
    def validate_paths(cls, v):
        """Ensure paths can be created"""
        try:
            Path(v).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create directory {v}: {e}")
        return v
    
    @validator("OLLAMA_HOST")
    def validate_ollama_host(cls, v):
        """Validate Ollama host URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Ollama host must be a valid HTTP/HTTPS URL")
        return v
    
    # === COMPUTED PROPERTIES ===
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENV.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENV.lower() == "production"
    
    @property
    def database_echo(self) -> bool:
        """Whether to echo SQL statements"""
        return self.is_development and self.debug
    
    # === CONFIGURATION METHODS ===
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dict"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.database_echo,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration dict"""
        return {
            "host": self.OLLAMA_HOST,
            "model": self.OLLAMA_MODEL,
            "timeout": self.ollama_timeout,
            "temperature": self.MODEL_TEMPERATURE,
            "top_p": self.MODEL_TOP_P,
            "top_k": self.MODEL_TOP_K,
            "max_tokens": self.MODEL_MAX_TOKENS,
            "repeat_penalty": self.MODEL_REPEAT_PENALTY,
            "context_window": self.MODEL_CONTEXT_WINDOW,
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration dict"""
        return {
            "embedding_model": self.EMBEDDING_MODEL,
            "chunk_size": self.RAG_CHUNK_SIZE,
            "chunk_overlap": self.RAG_CHUNK_OVERLAP,
            "top_k": self.RAG_TOP_K,
            "similarity_threshold": self.similarity_threshold,
            "vector_db_path": str(self.vector_db_path),
        }


# Create global settings instance
settings = Settings()