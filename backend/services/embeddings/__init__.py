"""
Embeddings service package
Provides backward compatibility for existing imports
"""

from .embedding_service import EmbeddingService
from .local_embedder import LocalGammaEmbedder
from .base import EmbeddingProvider, EmbeddingConfig, EmbeddingException

# Export main classes for backward compatibility
__all__ = [
    'EmbeddingService',
    'LocalGammaEmbedder', 
    'EmbeddingProvider',
    'EmbeddingConfig',
    'EmbeddingException'
]