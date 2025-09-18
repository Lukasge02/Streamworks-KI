"""
Configuration Settings für Streamworks RAG MVP
Lädt alle Einstellungen aus .env Datei
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Project Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent  # Points to project root
    
    # OpenAI Configuration (kept for other services that still use it)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")  # Unused but kept for compatibility
    
    # Local Embedding Configuration (Gamma only) - No OpenAI dependencies
    EMBEDDING_PROVIDER: str = "gamma"  # Fixed to gamma only
    GAMMA_MODEL_NAME: str = os.getenv("GAMMA_MODEL_NAME", "google/embeddinggemma-300m")
    LOCAL_EMBEDDING_DEVICE: str = os.getenv("LOCAL_EMBEDDING_DEVICE", "auto")  # auto|cpu|cuda|mps
    BATCH_SIZE_LOCAL: int = int(os.getenv("BATCH_SIZE_LOCAL", "32"))
    
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
    
    # Central LLM Provider Configuration - Single Switch Point
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai|ollama

    # OpenAI Configuration - JSON Mode requires gpt-4o (not gpt-4o-mini)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")  # Use gpt-4o for JSON mode support
    OPENAI_STREAMING: bool = os.getenv("OPENAI_STREAMING", "true").lower() == "true"
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

    # Ollama Configuration (fallback)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    # Legacy settings (deprecated)
    LOCAL_LLM_PROVIDER: str = os.getenv("LOCAL_LLM_PROVIDER", "openai")  # ollama|openai|hybrid
    LLM_FALLBACK_ENABLED: bool = os.getenv("LLM_FALLBACK_ENABLED", "false").lower() == "true"
    
    # Unified Document Storage (New Clean Structure)
    DOCUMENTS_BASE_PATH: Path = Path(os.getenv("DOCUMENTS_BASE_PATH", "./Dokumente"))
    SYSTEM_PATH: Path = DOCUMENTS_BASE_PATH / ".system"
    
    # Vector Database (New Location)
    VECTOR_DB: str = os.getenv("VECTOR_DB", "qdrant")  # qdrant|chroma|weaviate

    # Qdrant Configuration (Local Setup)
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "streamworks_documents")
    QDRANT_VECTOR_SIZE: int = int(os.getenv("QDRANT_VECTOR_SIZE", "768"))  # BGE embedding size
    QDRANT_USE_GRPC: bool = os.getenv("QDRANT_USE_GRPC", "false").lower() == "true"

    # Hybrid Search Configuration
    ENABLE_HYBRID_SEARCH: bool = os.getenv("ENABLE_HYBRID_SEARCH", "true").lower() == "true"
    HYBRID_COLLECTION_NAME: str = os.getenv("HYBRID_COLLECTION_NAME", "streamworks_hybrid")
    HYBRID_DENSE_WEIGHT: float = float(os.getenv("HYBRID_DENSE_WEIGHT", "0.7"))  # Semantic similarity weight
    HYBRID_SPARSE_WEIGHT: float = float(os.getenv("HYBRID_SPARSE_WEIGHT", "0.3"))  # Keyword matching weight

    # BM25-style Text Processing Configuration
    BM25_LIKE_PROCESSING: bool = os.getenv("BM25_LIKE_PROCESSING", "true").lower() == "true"
    TEXT_PREPROCESSING_LANGUAGE: str = os.getenv("TEXT_PREPROCESSING_LANGUAGE", "auto")  # auto|de|en
    REMOVE_STOPWORDS: bool = os.getenv("REMOVE_STOPWORDS", "true").lower() == "true"
    MIN_TERM_FREQUENCY: int = int(os.getenv("MIN_TERM_FREQUENCY", "1"))  # Minimum term frequency for sparse vectors (lowered for better coverage)
    MAX_SPARSE_VECTOR_SIZE: int = int(os.getenv("MAX_SPARSE_VECTOR_SIZE", "10000"))  # Limit sparse vector dimensions

    # Hybrid Search Mode-Specific Weights
    HYBRID_FAST_DENSE_WEIGHT: float = float(os.getenv("HYBRID_FAST_DENSE_WEIGHT", "0.8"))  # More semantic for fast mode
    HYBRID_ACCURATE_DENSE_WEIGHT: float = float(os.getenv("HYBRID_ACCURATE_DENSE_WEIGHT", "0.6"))  # Balanced for accurate mode
    HYBRID_COMPREHENSIVE_DENSE_WEIGHT: float = float(os.getenv("HYBRID_COMPREHENSIVE_DENSE_WEIGHT", "0.5"))  # More keywords for comprehensive

    # Legacy ChromaDB path (kept for cleanup)
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
    
    # Chunking Settings - Phase 3 Optimized for Gamma Embeddings and Semantic Coherence
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "2000"))  # Increased from 1500 for better context
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "500"))  # Increased from 300 for better continuity
    
    # Advanced Chunking Configuration - Phase 3 Enhancements
    ENABLE_SEMANTIC_CHUNKING: bool = os.getenv("ENABLE_SEMANTIC_CHUNKING", "true").lower() == "true"
    SEMANTIC_BOUNDARY_DETECTION: bool = os.getenv("SEMANTIC_BOUNDARY_DETECTION", "true").lower() == "true"
    ADAPTIVE_CHUNK_SIZING: bool = os.getenv("ADAPTIVE_CHUNK_SIZING", "true").lower() == "true"
    
    # Document Type Specific Chunk Sizes - Optimized for Gamma Embeddings
    PDF_CHUNK_SIZE: int = int(os.getenv("PDF_CHUNK_SIZE", "2500"))  # Increased for better PDF context
    IMAGE_CHUNK_SIZE: int = int(os.getenv("IMAGE_CHUNK_SIZE", "1200"))  # Slightly increased for OCR
    TEXT_CHUNK_SIZE: int = int(os.getenv("TEXT_CHUNK_SIZE", "2000"))  # Increased for better text context
    TECHNICAL_DOC_CHUNK_SIZE: int = int(os.getenv("TECHNICAL_DOC_CHUNK_SIZE", "2800"))  # New: for technical docs
    
    # Chunk Quality Settings - Enhanced for Phase 3
    MIN_CHUNK_SIZE: int = int(os.getenv("MIN_CHUNK_SIZE", "200"))  # Increased from 100 for better quality
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "4000"))  # Increased from 3000 for complex content
    MIN_WORD_COUNT: int = int(os.getenv("MIN_WORD_COUNT", "30"))  # Increased from 20 for better semantic density
    OPTIMAL_CHUNK_WORDS: int = int(os.getenv("OPTIMAL_CHUNK_WORDS", "300"))  # New: target word count
    
    # Semantic Chunking Settings - New Phase 3 Features
    SENTENCE_BOUNDARY_WEIGHT: float = float(os.getenv("SENTENCE_BOUNDARY_WEIGHT", "0.8"))  # Prefer sentence boundaries
    PARAGRAPH_BOUNDARY_WEIGHT: float = float(os.getenv("PARAGRAPH_BOUNDARY_WEIGHT", "0.9"))  # Strong preference for paragraphs
    SECTION_BOUNDARY_WEIGHT: float = float(os.getenv("SECTION_BOUNDARY_WEIGHT", "1.0"))  # Highest preference for sections
    
    # Context Preservation Settings
    CONTEXT_PRESERVATION_RATIO: float = float(os.getenv("CONTEXT_PRESERVATION_RATIO", "0.25"))  # 25% overlap for context
    SEMANTIC_COHERENCE_THRESHOLD: float = float(os.getenv("SEMANTIC_COHERENCE_THRESHOLD", "0.7"))  # Coherence scoring
    
    # RAG Pipeline Settings - OPTIMIZED Based on Similarity Threshold Analysis (2025-09-15)
    # Analysis Results: avg_similarity_score: 0.5647, optimal_threshold: 0.01, balance_score: 0.82
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.01"))  # Optimized from analysis (was 0.25)

    # Advanced RAG Thresholds - Based on Qdrant Performance Analysis
    HIGH_QUALITY_THRESHOLD: float = float(os.getenv("HIGH_QUALITY_THRESHOLD", "0.025"))  # Optimized from analysis (was 0.18)
    FALLBACK_THRESHOLD: float = float(os.getenv("FALLBACK_THRESHOLD", "0.01"))  # Optimized from analysis (was 0.02)
    
    # Model Settings - Use gpt-4o for JSON mode compatibility
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")  # Changed from gpt-4o-mini for JSON mode support
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Phase 2: Query Enhancement Settings
    ENABLE_QUERY_ENHANCEMENT: bool = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"
    ENABLE_MULTI_QUERY: bool = os.getenv("ENABLE_MULTI_QUERY", "true").lower() == "true"
    MAX_QUERY_VARIATIONS: int = int(os.getenv("MAX_QUERY_VARIATIONS", "3"))
    
    # NLP Libraries Settings
    SPACY_MODEL_DE: str = os.getenv("SPACY_MODEL_DE", "de_core_news_sm")
    SPACY_MODEL_EN: str = os.getenv("SPACY_MODEL_EN", "en_core_web_sm")
    NLTK_DOWNLOAD_PATH: str = os.getenv("NLTK_DOWNLOAD_PATH", "")
    
    # Query Enhancement Confidence Thresholds
    MIN_ENHANCEMENT_CONFIDENCE: float = float(os.getenv("MIN_ENHANCEMENT_CONFIDENCE", "0.5"))
    SYNONYM_EXPANSION_ENABLED: bool = os.getenv("SYNONYM_EXPANSION_ENABLED", "true").lower() == "true"
    MULTI_QUERY_TIMEOUT: int = int(os.getenv("MULTI_QUERY_TIMEOUT", "30"))
    
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