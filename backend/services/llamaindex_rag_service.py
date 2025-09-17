"""
DEPRECATED: LlamaIndex RAG Service - Redirect to Qdrant RAG Service
This file maintains API compatibility only - all functionality moved to Qdrant implementation
"""

import logging
from .qdrant_rag_service import get_rag_service as get_qdrant_rag_service

logger = logging.getLogger(__name__)

async def get_rag_service():
    """
    DEPRECATED: Direct redirect to QdrantRAGService
    Maintains compatibility for legacy imports
    """
    logger.info("🔄 LlamaIndex RAG Service deprecated - redirecting to Qdrant RAG Service")
    return await get_qdrant_rag_service()