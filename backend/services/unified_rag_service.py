"""
Unified RAG Service for StreamWorks
Legacy wrapper for backward compatibility - imports from refactored modules
"""

# Import everything from the refactored modules for backward compatibility
from .rag.models import RAGMode, RAGType, RAGConfig, RAGServiceInterface
from .rag.openai_rag import OpenAIRAGService
from .rag.rag_coordinator import UnifiedRAGService, create_unified_rag_service, create_openai_rag_service

# Re-export for backward compatibility
__all__ = [
    'RAGMode',
    'RAGType',
    'RAGConfig', 
    'RAGServiceInterface',
    'OpenAIRAGService',
    'UnifiedRAGService',
    'create_unified_rag_service',
    'create_openai_rag_service'
]

# Keep logging for compatibility
import logging
logger = logging.getLogger(__name__)