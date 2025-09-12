"""
Configuration Settings für Streamworks RAG MVP
Lädt alle Einstellungen aus .env Datei
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Project Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent  # Points to project root
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    
    # Local Embedding Configuration (Gamma)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "gamma")  # gamma|openai|hybrid
    GAMMA_MODEL_NAME: str = os.getenv("GAMMA_MODEL_NAME", "google/embeddinggemma-300m")
    LOCAL_EMBEDDING_DEVICE: str = os.getenv("LOCAL_EMBEDDING_DEVICE", "auto")  # auto|cpu|cuda|mps
    BATCH_SIZE_LOCAL: int = int(os.getenv("BATCH_SIZE_LOCAL", "32"))
    ENABLE_EMBEDDING_FALLBACK: bool = os.getenv("ENABLE_EMBEDDING_FALLBACK", "true").lower() == "true"
    
    # Enhanced Embedding Cache Configuration - Optimized for better performance
    EMBEDDING_CACHE_SIZE: int = int(os.getenv("EMBEDDING_CACHE_SIZE", "1500"))  # Optimized size
    EMBEDDING_CACHE_TTL: int = int(os.getenv("EMBEDDING_CACHE_TTL", "7200"))  # 2 hours - longer retention
    ENABLE_SEMANTIC_CACHE: bool = os.getenv("ENABLE_SEMANTIC_CACHE", "true").lower() == "true"
    SEMANTIC_CACHE_SIZE: int = int(os.getenv("SEMANTIC_CACHE_SIZE", "300"))  # Smaller for efficiency
    SEMANTIC_CACHE_TTL: int = int(os.getenv("SEMANTIC_CACHE_TTL", "3600"))  # 1 hour - longer retention
    SEMANTIC_SIMILARITY_THRESHOLD: float = float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.80"))  # Less restrictive from 0.85
    
    # Advanced Cache Settings
    CACHE_CLEANUP_INTERVAL: int = int(os.getenv("CACHE_CLEANUP_INTERVAL", "300"))  # 5 minutes
    CACHE_PERFORMANCE_LOGGING: bool = os.getenv("CACHE_PERFORMANCE_LOGGING", "true").lower() == "true"
    
    
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Local LLM Configuration (Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    LOCAL_LLM_PROVIDER: str = os.getenv("LOCAL_LLM_PROVIDER", "ollama")  # ollama|openai|hybrid
    LLM_FALLBACK_ENABLED: bool = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"
    
    # Unified Document Storage (New Clean Structure)
    DOCUMENTS_BASE_PATH: Path = Path(os.getenv("DOCUMENTS_BASE_PATH", "./Dokumente"))
    SYSTEM_PATH: Path = DOCUMENTS_BASE_PATH / ".system"
    
    # Vector Database (New Location)
    VECTOR_DB: str = os.getenv("VECTOR_DB", "chroma")  # chroma|qdrant|weaviate
    CHROMA_PATH: Path = SYSTEM_PATH / "chroma"
    
    # Document Storage (New Clean Structure)
    DOC_STORE_PATH: Path = DOCUMENTS_BASE_PATH
    METADATA_PATH: Path = SYSTEM_PATH / "metadata"
    CHUNKS_PATH: Path = SYSTEM_PATH / "chunks"
    ALLOW_FILE_TYPES: str = os.getenv("ALLOW_FILE_TYPES", "pdf,docx,html,xml")
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "40"))
    
    # XML-RAG Specific Settings
    XML_STORE_PATH: Path = Path(os.getenv("XML_STORE_PATH", "./data/xml_streams"))
    XML_COLLECTION_NAME: str = os.getenv("XML_COLLECTION_NAME", "streamworks_xml_streams")
    XML_EMBEDDING_MODEL: str = os.getenv("XML_EMBEDDING_MODEL", "text-embedding-3-large")
    XML_SIMILARITY_THRESHOLD: float = float(os.getenv("XML_SIMILARITY_THRESHOLD", "0.15"))
    
    # XML Processing Settings
    XML_CHUNK_SIZE: int = int(os.getenv("XML_CHUNK_SIZE", "1000"))
    XML_CHUNK_OVERLAP: int = int(os.getenv("XML_CHUNK_OVERLAP", "100"))
    XML_MAX_CHUNK_TOKENS: int = int(os.getenv("XML_MAX_CHUNK_TOKENS", "1000"))
    
    # XML Pattern Detection
    ENABLE_PATTERN_DETECTION: bool = os.getenv("ENABLE_PATTERN_DETECTION", "true").lower() == "true"
    ENABLE_ANTI_PATTERN_DETECTION: bool = os.getenv("ENABLE_ANTI_PATTERN_DETECTION", "true").lower() == "true"
    MIN_PATTERN_OCCURRENCES: int = int(os.getenv("MIN_PATTERN_OCCURRENCES", "3"))
    
    # XML Template Generation
    ENABLE_XML_GENERATION: bool = os.getenv("ENABLE_XML_GENERATION", "true").lower() == "true"
    XML_GENERATION_MODEL: str = os.getenv("XML_GENERATION_MODEL", "gpt-4o")
    XML_GENERATION_TEMPERATURE: float = float(os.getenv("XML_GENERATION_TEMPERATURE", "0.1"))
    XML_GENERATION_MAX_TOKENS: int = int(os.getenv("XML_GENERATION_MAX_TOKENS", "4000"))
    
    @property
    def allowed_file_types(self) -> List[str]:
        """Get allowed file types as list"""
        return [t.strip() for t in self.ALLOW_FILE_TYPES.split(",")]
    
    @property
    def MAX_FILE_SIZE(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_UPLOAD_MB * 1024 * 1024
    
    # XSD Validation
    ENABLE_XSD_VALIDATION: bool = os.getenv("ENABLE_XSD_VALIDATION", "false").lower() == "true"
    XSD_SCHEMA_PATH: Path = Path(os.getenv("XSD_SCHEMA_PATH", "./backend/resources/streamworks.xsd"))
    
    # API Configuration
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Redis Cache Configuration (optional)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # Chunking Settings - Optimized for better context retention
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "300"))
    
    # Document Type Specific Chunk Sizes
    PDF_CHUNK_SIZE: int = int(os.getenv("PDF_CHUNK_SIZE", "2000"))  # Larger for PDFs
    IMAGE_CHUNK_SIZE: int = int(os.getenv("IMAGE_CHUNK_SIZE", "1000"))  # Smaller for OCR text
    TEXT_CHUNK_SIZE: int = int(os.getenv("TEXT_CHUNK_SIZE", "1500"))  # Standard for text files
    
    # Chunk Quality Settings
    MIN_CHUNK_SIZE: int = int(os.getenv("MIN_CHUNK_SIZE", "100"))  # Minimum viable chunk
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "3000"))  # Maximum chunk size
    MIN_WORD_COUNT: int = int(os.getenv("MIN_WORD_COUNT", "20"))  # Minimum words per chunk
    
    # RAG Pipeline Settings - Optimized for better quality
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))  # Improved from 0.1
    
    # Advanced RAG Thresholds
    HIGH_QUALITY_THRESHOLD: float = float(os.getenv("HIGH_QUALITY_THRESHOLD", "0.7"))  # For high-confidence answers
    FALLBACK_THRESHOLD: float = float(os.getenv("FALLBACK_THRESHOLD", "0.15"))  # Minimum for any answer
    
    # Model Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Global settings instance
settings = Settings()

# Validate critical settings (relaxed for local LLM integration)
if not settings.OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY nicht gesetzt - nur lokales LLM verfügbar")

# Create necessary directories
settings.DOC_STORE_PATH.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PATH.mkdir(parents=True, exist_ok=True)
settings.XML_STORE_PATH.mkdir(parents=True, exist_ok=True)

# Ensure XSD schema directory exists
if settings.ENABLE_XSD_VALIDATION:
    settings.XSD_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)