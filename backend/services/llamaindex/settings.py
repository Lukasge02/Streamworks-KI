"""
LlamaIndex Global Settings Configuration

Configures LlamaIndex to use:
- OpenAI GPT-4o-mini as LLM
- OpenAI text-embedding-3-small for embeddings (1536 dimensions)
- Optimal chunk sizes for RAG
"""

from typing import Optional
from functools import lru_cache

from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from config import config


class LlamaIndexSettings:
    """
    Centralized LlamaIndex configuration
    
    Matches existing embedding dimensions (1536) for Qdrant compatibility.
    Uses same OpenAI key as rest of the application.
    """
    
    # Model settings
    LLM_MODEL = config.LLM_MODEL  # gpt-4o-mini
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536  # Matches existing Qdrant collection
    
    # Chunking settings
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 200
    
    # Retrieval settings
    TOP_K = 5
    SIMILARITY_THRESHOLD = 0.3
    
    # Qdrant settings
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333
    COLLECTION_NAME = "streamworks_documents"
    
    @classmethod
    def configure(cls) -> None:
        """
        Configure LlamaIndex global settings
        
        Must be called before using any LlamaIndex functionality.
        """
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured!")
        
        # Configure LLM
        Settings.llm = OpenAI(
            model=cls.LLM_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.1,
            max_tokens=1024,
        )
        
        # Configure Embeddings (matching existing 1536 dimensions)
        Settings.embed_model = OpenAIEmbedding(
            model=cls.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY,
            dimensions=cls.EMBEDDING_DIMENSION,
        )
        
        # Configure chunking
        Settings.chunk_size = cls.CHUNK_SIZE
        Settings.chunk_overlap = cls.CHUNK_OVERLAP
        
        print(f"✅ LlamaIndex configured: LLM={cls.LLM_MODEL}, Embeddings={cls.EMBEDDING_MODEL}")
    
    @classmethod
    def get_llm(cls) -> OpenAI:
        """Get configured LLM instance"""
        return OpenAI(
            model=cls.LLM_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.1,
        )
    
    @classmethod
    def get_embed_model(cls) -> OpenAIEmbedding:
        """Get configured embedding model"""
        return OpenAIEmbedding(
            model=cls.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY,
            dimensions=cls.EMBEDDING_DIMENSION,
        )


def configure_llamaindex() -> None:
    """Configure LlamaIndex with OpenAI models"""
    LlamaIndexSettings.configure()


@lru_cache(maxsize=1)
def get_settings() -> LlamaIndexSettings:
    """Get singleton settings instance"""
    return LlamaIndexSettings()
