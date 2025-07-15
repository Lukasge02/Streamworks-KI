"""
Production-specific configuration settings
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, validator
from .config import Settings


class ProductionSettings(Settings):
    """Production environment settings with optimizations and security"""
    
    # Environment
    ENV: str = "production"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALLOWED_HOSTS: List[str] = ["streamworks-ki.com", "api.streamworks-ki.com", "localhost"]
    CORS_ORIGINS: List[str] = ["https://streamworks-ki.com", "https://app.streamworks-ki.com"]
    SECURE_SSL_REDIRECT: bool = True
    SECURE_HSTS_SECONDS: int = 31536000  # 1 year
    
    # Database optimizations
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # 1 hour
    DB_ECHO: bool = False  # Disable SQL logging in production
    
    # Redis/Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CACHE_TTL: int = 300  # 5 minutes default
    CACHE_MAX_SIZE: int = 1000
    
    # Performance settings
    WORKER_PROCESSES: int = int(os.getenv("WORKER_PROCESSES", "4"))
    WORKER_CONNECTIONS: int = 1000
    WORKER_TIMEOUT: int = 120
    KEEPALIVE: int = 5
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "1000/hour"
    RATE_LIMIT_CHUNKS: str = "500/hour"
    RATE_LIMIT_SEARCH: str = "200/hour"
    RATE_LIMIT_UPLOAD: str = "50/hour"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = "/var/log/streamworks-ki/app.log"
    LOG_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_BACKUP_COUNT: int = 5
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8001
    HEALTH_CHECK_INTERVAL: int = 30
    
    # API settings
    API_TIMEOUT: int = 30
    MAX_REQUEST_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_CHUNKS_PER_REQUEST: int = 100
    
    # LLM/AI settings
    OLLAMA_TIMEOUT: int = 60
    OLLAMA_MAX_RETRIES: int = 2
    MODEL_CACHE_SIZE: int = 2  # Number of models to keep in memory
    
    # ChromaDB settings
    CHROMADB_PERSIST_DIRECTORY: str = "/data/chromadb"
    CHROMADB_BACKUP_ENABLED: bool = True
    CHROMADB_BACKUP_INTERVAL: int = 21600  # 6 hours
    
    # File upload settings
    UPLOAD_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = [".txt", ".md", ".pdf", ".docx", ".json"]
    UPLOAD_SCAN_ENABLED: bool = True  # Virus scanning
    
    # Email notifications (for alerts)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    ALERT_EMAIL_FROM: str = "alerts@streamworks-ki.com"
    ALERT_EMAIL_TO: List[str] = []
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v):
        # Ensure all origins use HTTPS in production
        for origin in v:
            if not origin.startswith("https://") and origin != "http://localhost:3000":
                raise ValueError(f"Production CORS origin must use HTTPS: {origin}")
        return v
    
    @validator("WORKER_PROCESSES")
    def validate_worker_processes(cls, v):
        if v < 1 or v > 16:
            raise ValueError("WORKER_PROCESSES must be between 1 and 16")
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True


class DatabaseConfig:
    """Database-specific production configuration"""
    
    @staticmethod
    def get_connection_string(settings: ProductionSettings) -> str:
        """Get optimized database connection string"""
        base_url = settings.DATABASE_URL
        
        # Add connection pool parameters
        params = [
            f"pool_size={settings.DB_POOL_SIZE}",
            f"max_overflow={settings.DB_MAX_OVERFLOW}",
            f"pool_timeout={settings.DB_POOL_TIMEOUT}",
            f"pool_recycle={settings.DB_POOL_RECYCLE}",
        ]
        
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}{'&'.join(params)}"
    
    @staticmethod
    def get_engine_options(settings: ProductionSettings) -> dict:
        """Get SQLAlchemy engine options for production"""
        return {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": settings.DB_POOL_RECYCLE,
            "echo": settings.DB_ECHO,
            "pool_pre_ping": True,  # Validate connections
            "connect_args": {
                "connect_timeout": 10,
                "application_name": "streamworks-ki-api",
            }
        }


class CacheConfig:
    """Redis/caching configuration"""
    
    @staticmethod
    def get_redis_config(settings: ProductionSettings) -> dict:
        """Get Redis configuration for production"""
        return {
            "url": settings.REDIS_URL,
            "encoding": "utf-8",
            "decode_responses": True,
            "max_connections": 20,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
        }


class SecurityConfig:
    """Security-related configuration"""
    
    @staticmethod
    def get_cors_config(settings: ProductionSettings) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": settings.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Request-ID", "X-Response-Time"],
            "max_age": 3600,
        }
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }


# Export production settings instance
production_settings = ProductionSettings()