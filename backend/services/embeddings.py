"""
Embedding Service für Streamworks RAG MVP
Legacy wrapper for backward compatibility - imports from refactored modules
"""

# Import everything from the refactored modules for backward compatibility
from .embeddings.embedding_service import EmbeddingService
from .embeddings.local_embedder import LocalGammaEmbedder

# Re-export for backward compatibility
__all__ = ['EmbeddingService', 'LocalGammaEmbedder']

# Keep the old module-level imports for any code that might use them
import logging
logger = logging.getLogger(__name__)

# Preserve SENTENCE_TRANSFORMERS_AVAILABLE for backward compatibility
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, falling back to OpenAI only")