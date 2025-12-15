"""
Configuration module for Streamworks-KI Backend
Loads environment variables from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root (one level up from backend/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Application configuration"""

    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # RAG Enhancement Settings
    RAG_HYBRID_ENABLED: bool = os.getenv("RAG_HYBRID_ENABLED", "true").lower() == "true"
    RAG_SEMANTIC_WEIGHT: float = float(os.getenv("RAG_SEMANTIC_WEIGHT", "0.6"))
    RAG_KEYWORD_WEIGHT: float = float(os.getenv("RAG_KEYWORD_WEIGHT", "0.4"))
    RAG_RERANK_ENABLED: bool = os.getenv("RAG_RERANK_ENABLED", "true").lower() == "true"
    RAG_RERANK_TOP_K: int = int(os.getenv("RAG_RERANK_TOP_K", "5"))
    RAG_HYDE_ENABLED: bool = os.getenv("RAG_HYDE_ENABLED", "true").lower() == "true"
    RAG_CONTEXT_COMPRESSION: bool = (
        False  # os.getenv("RAG_CONTEXT_COMPRESSION", "true").lower() == "true"
    )
    RAG_CACHE_TTL: int = int(os.getenv("RAG_CACHE_TTL", "3600"))
    RAG_CACHE_MAX_SIZE: int = int(os.getenv("RAG_CACHE_MAX_SIZE", "1000"))
    RAG_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.5")
    )

    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Check if required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print("⚠️ OPENAI_API_KEY not set in .env file!")
            return False
        return True


# Singleton instance
config = Config()
