"""
LlamaIndex Services Package
Production-ready RAG with LlamaIndex framework

This package provides:
- settings: Global LlamaIndex configuration with OpenAI
- index_service: Qdrant VectorStoreIndex management
- ingestion_service: Document parsing, chunking, and indexing
- query_service: Retrieval with reranking and hybrid search
- chat_service: Conversational RAG with memory
- streaming_service: Real-time token streaming
"""

from .settings import configure_llamaindex, get_settings
from .index_service import IndexService, get_index_service
from .ingestion_service import IngestionService, get_ingestion_service
from .query_service import QueryService, get_query_service
from .chat_service import ChatService, get_chat_service
from .streaming_service import StreamingQueryService, get_streaming_service

__all__ = [
    # Configuration
    "configure_llamaindex",
    "get_settings",
    # Services
    "IndexService",
    "get_index_service",
    "IngestionService",
    "get_ingestion_service",
    "QueryService",
    "get_query_service",
    "ChatService",
    "get_chat_service",
    "StreamingQueryService",
    "get_streaming_service",
]
