"""
RAG Services Package
Enterprise-ready Retrieval-Augmented Generation v2.0

Enhanced features:
- Hybrid Search (Semantic + BM25 with RRF)
- Cross-Encoder Reranking
- Citation Generation
- Confidence Scoring
"""

from .vector_store import VectorStore
from .document_service import DocumentService

# Enhanced RAG Components
from .cache import RAGCache
from .hybrid_search import HybridSearchEngine
from .reranker import RerankerService, reranker

__all__ = [
    # Core
    "VectorStore",
    "DocumentService",
    # Enhanced
    "RAGCache",
    "HybridSearchEngine",
    "RerankerService",
    "reranker",
]
