"""
RAG service package
Provides backward compatibility for existing imports
"""

from .models import RAGMode, RAGType, RAGConfig, RAGServiceInterface
from .openai_rag import OpenAIRAGService
from .rag_coordinator import UnifiedRAGService, create_unified_rag_service, create_openai_rag_service

# Export main classes and functions for backward compatibility
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