"""
Unified Configuration Management for StreamWorks-KI
Consolidates all configuration into a single, environment-aware settings system
"""
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environments"""
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
    Unified application settings with environment-based configuration
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields for backward compatibility
    )
    
    # ===== APPLICATION =====
    APP_NAME: str = Field(default="StreamWorks-KI", description="Application name")
    VERSION: str = Field(default="2.0.0", description="Application version")
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, description="Environment")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    
    # ===== DATABASE (PostgreSQL) =====
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="streamworks_ki", description="Database name")
    POSTGRES_USER: str = Field(default="streamworks", description="Database user")
    POSTGRES_PASSWORD: str = Field(default="streamworks_secure_2025", description="Database password")
    
    # Database Pool Configuration
    DB_POOL_SIZE: int = Field(default=20, ge=1, le=100, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=40, ge=0, le=100, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, ge=300, le=86400, description="Connection recycle time")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")
    
    # ===== AI/ML CONFIGURATION =====
    # Ollama/LLM Settings
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="Ollama API host")
    OLLAMA_MODEL: str = Field(default="mistral:7b-instruct", description="LLM model name")
    LLM_TIMEOUT: int = Field(default=30, ge=5, le=300, description="LLM request timeout")
    LLM_MAX_TOKENS: int = Field(default=2048, ge=100, le=8192, description="Max tokens for generation")
    LLM_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    LLM_TOP_P: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling")
    LLM_TOP_K: int = Field(default=50, ge=1, le=100, description="Top-k sampling")
    
    # RAG Configuration
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model for RAG"
    )
    CHUNK_SIZE: int = Field(default=500, ge=100, le=2000, description="Text chunk size")
    CHUNK_OVERLAP: int = Field(default=50, ge=0, le=500, description="Chunk overlap")
    TOP_K_CHUNKS: int = Field(default=5, ge=1, le=50, description="Number of chunks to retrieve")
    MIN_RELEVANCE_SCORE: float = Field(default=0.7, ge=0.0, le=1.0, description="Min relevance threshold")
    
    # ===== API CONFIGURATION =====
    API_HOST: str = Field(default="127.0.0.1", description="API host")
    API_PORT: int = Field(default=8000, ge=1000, le=65535, description="API port")
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173"
        ],
        description="Allowed CORS origins"
    )
    
    # ===== SECURITY =====
    SECRET_KEY: str = Field(
        default="development-secret-key-change-in-production",
        min_length=32,
        description="Secret key for security"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=1, le=10080, description="Token expiry")
    
    # ===== STORAGE =====
    DATA_PATH: Path = Field(default=Path("./data"), description="Base data directory")
    UPLOAD_MAX_SIZE: int = Field(default=50 * 1024 * 1024, description="Max upload size (bytes)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".txt", ".md", ".docx", ".xml", ".json"],
        description="Allowed file extensions"
    )
    
    # ===== MONITORING =====
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    ENABLE_ANALYTICS: bool = Field(default=True, description="Enable analytics")
    SLOW_QUERY_THRESHOLD: float = Field(default=1.0, ge=0.1, le=10.0, description="Slow query threshold")
    
    # ===== DERIVED PROPERTIES =====
    @property
    def database_url(self) -> str:
        """Synchronous database URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def async_database_url(self) -> str:
        """Asynchronous database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def vector_db_path(self) -> Path:
        """Path to vector database"""
        return self.DATA_PATH / "vector_db"
    
    @property
    def training_data_path(self) -> Path:
        """Path to training data"""
        return self.DATA_PATH / "training"
    
    @property
    def upload_path(self) -> Path:
        """Path for file uploads"""
        return self.DATA_PATH / "uploads"
    
    @property
    def converted_path(self) -> Path:
        """Path for converted documents"""
        return self.DATA_PATH / "converted"
    
    # ===== ENVIRONMENT-SPECIFIC OVERRIDES =====
    @validator("DEBUG", pre=True, always=True)
    def set_debug(cls, v, values):
        """Set debug based on environment"""
        env = values.get("ENVIRONMENT", Environment.DEVELOPMENT)
        if env == Environment.PRODUCTION:
            return False
        return v if v is not None else True
    
    @validator("LOG_LEVEL", pre=True, always=True)
    def set_log_level(cls, v, values):
        """Set log level based on environment"""
        env = values.get("ENVIRONMENT", Environment.DEVELOPMENT)
        if v:
            return v
        return LogLevel.DEBUG if env == Environment.DEVELOPMENT else LogLevel.INFO
    
    @validator("API_HOST", pre=True, always=True)
    def set_api_host(cls, v, values):
        """Set API host based on environment"""
        env = values.get("ENVIRONMENT", Environment.DEVELOPMENT)
        if env == Environment.PRODUCTION:
            return "0.0.0.0"
        return v or "127.0.0.1"
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Ensure secret key is secure in production"""
        env = values.get("ENVIRONMENT", Environment.DEVELOPMENT)
        if env == Environment.PRODUCTION and v == "development-secret-key-change-in-production":
            raise ValueError("Must set a secure SECRET_KEY in production")
        return v
    
    # ===== LEGACY COMPATIBILITY =====
    # These properties maintain backward compatibility with old code
    
    @property
    def ENV(self) -> str:
        """Legacy environment property"""
        return self.ENVIRONMENT.value
    
    @property
    def PROJECT_NAME(self) -> str:
        """Legacy project name"""
        return self.APP_NAME
    
    @property
    def DATABASE_URL(self) -> str:
        """Legacy database URL"""
        return self.async_database_url
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Legacy CORS origins"""
        return self.CORS_ORIGINS
    
    @property
    def VECTOR_DB_PATH(self) -> str:
        """Legacy vector DB path"""
        return str(self.vector_db_path)
    
    @property
    def TRAINING_DATA_PATH(self) -> str:
        """Legacy training data path"""
        return str(self.training_data_path)
    
    # Feature flags (legacy)
    RAG_ENABLED: bool = Field(default=True, description="Enable RAG system")
    LLM_ENABLED: bool = Field(default=True, description="Enable LLM")
    TRAINING_ENABLED: bool = Field(default=True, description="Enable training features")
    XML_GENERATION_ENABLED: bool = Field(default=True, description="Enable XML generation")
    FORCE_GERMAN_RESPONSES: bool = Field(default=True, description="Force German responses")
    
    # Additional legacy model parameters
    MODEL_TEMPERATURE: float = Field(default=0.7, description="Legacy temperature")
    MODEL_TOP_P: float = Field(default=0.9, description="Legacy top-p")
    MODEL_TOP_K: int = Field(default=50, description="Legacy top-k")
    MODEL_MAX_TOKENS: int = Field(default=2048, description="Legacy max tokens")
    MODEL_REPEAT_PENALTY: float = Field(default=1.1, description="Legacy repeat penalty")
    MODEL_CONTEXT_WINDOW: int = Field(default=4096, description="Legacy context window")
    MODEL_THREADS: int = Field(default=4, description="Legacy threads")
    
    # Legacy RAG parameters
    RAG_CHUNK_SIZE: int = Field(default=500, description="Legacy chunk size")
    RAG_CHUNK_OVERLAP: int = Field(default=50, description="Legacy chunk overlap")
    RAG_TOP_K: int = Field(default=5, description="Legacy top-k")
    
    # Legacy misc
    MAX_NEW_TOKENS: int = Field(default=2048, description="Legacy max new tokens")
    TEMPERATURE: float = Field(default=0.7, description="Legacy temperature")
    DEVICE: str = Field(default="cpu", description="Legacy device")
    
    def get_db_config(self) -> dict:
        """Get database configuration for SQLAlchemy"""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "echo": self.DB_ECHO,
            "pool_pre_ping": True,
            "connect_args": {
                "server_settings": {
                    "application_name": f"{self.APP_NAME}-{self.ENVIRONMENT.value}"
                }
            }
        }
    
    def create_directories(self) -> None:
        """Create required directories"""
        directories = [
            self.DATA_PATH,
            self.vector_db_path,
            self.training_data_path,
            self.upload_path,
            self.converted_path,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Environment-specific settings classes
class DevelopmentSettings(Settings):
    """Development-specific settings"""
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DB_ECHO: bool = True


class ProductionSettings(Settings):
    """Production-specific settings"""
    ENVIRONMENT: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = LogLevel.INFO
    DB_ECHO: bool = False
    API_HOST: str = "0.0.0.0"
    
    # Production-specific validations
    @validator("SECRET_KEY")
    def validate_production_secret(cls, v):
        if len(v) < 64:
            raise ValueError("Production SECRET_KEY must be at least 64 characters")
        return v
    
    @validator("CORS_ORIGINS")
    def validate_production_cors(cls, v):
        for origin in v:
            if origin.startswith("http://") and "localhost" not in origin:
                raise ValueError(f"Production CORS must use HTTPS: {origin}")
        return v


# Factory function to get environment-specific settings
def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "development":
        return DevelopmentSettings()
    else:
        # Default settings with environment from env var
        return Settings(ENVIRONMENT=Environment(env))


# Global settings instance
settings = get_settings()

# Create required directories on import
settings.create_directories()