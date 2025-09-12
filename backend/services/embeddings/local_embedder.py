"""
Local Gamma embedding model implementation
"""
import logging
from typing import List, Optional
import numpy as np
import torch
import threading

from .base import EmbeddingInterface, EmbeddingException

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, local embeddings disabled")


class LocalGammaEmbedder(EmbeddingInterface):
    """Local Gamma embedding model handler"""
    
    def __init__(self, model_name: str = None, device: str = "auto"):
        # Use configured model if not provided
        if model_name is None:
            from config import settings
            model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
        
        self.model_name = model_name
        self.model = None
        self.device = device
        self._initialized = False
        self._initialization_error = None
        self._lock = threading.Lock()
        
    def _initialize_sync(self) -> bool:
        """Synchronous initialization of local embedding model"""
        if self._initialized:
            return True
            
        if self._initialization_error:
            return False
            
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialization_error = "sentence-transformers not installed"
            return False
        
        with self._lock:
            if self._initialized:
                return True
                
            try:
                logger.info(f"Initializing local embedding model: {self.model_name}")
                
                # Determine device
                if self.device == "auto":
                    if torch.cuda.is_available():
                        device = "cuda"
                    elif torch.backends.mps.is_available():
                        device = "mps"
                    else:
                        device = "cpu"
                else:
                    device = self.device
                
                # Load model with specific parameters for EmbeddingGemma
                if "embeddinggemma" in self.model_name.lower():
                    # EmbeddingGemma-specific initialization
                    self.model = SentenceTransformer(
                        self.model_name,
                        device=device,
                        trust_remote_code=True
                    )
                else:
                    # Standard sentence-transformers model
                    self.model = SentenceTransformer(self.model_name, device=device)
                
                self._initialized = True
                logger.info(f"Local embedding model initialized on {device}")
                return True
                
            except Exception as e:
                self._initialization_error = str(e)
                logger.error(f"Failed to initialize local embedding model: {e}")
                return False
    
    async def initialize(self) -> None:
        """Initialize the embedding provider"""
        if not self._initialize_sync():
            raise EmbeddingException(f"Failed to initialize local embedder: {self._initialization_error}")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.model is not None:
            del self.model
            self.model = None
            self._initialized = False
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def embed_texts_sync(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Synchronous version of embed_texts for internal use
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self._initialize_sync():
            raise EmbeddingException(f"Local embedding model not initialized: {self._initialization_error}")
        
        try:
            # Process in batches to manage memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings - use appropriate method for EmbeddingGemma
                with torch.no_grad():
                    # Check if this is EmbeddingGemma model
                    if "embeddinggemma" in self.model_name.lower():
                        # EmbeddingGemma uses encode_document for document embeddings
                        embeddings = self.model.encode_document(
                            batch,
                            convert_to_tensor=False,
                            show_progress_bar=False
                        )
                    else:
                        # Standard sentence-transformers models
                        embeddings = self.model.encode(
                            batch,
                            convert_to_tensor=False,
                            show_progress_bar=False,
                            normalize_embeddings=True  # Normalize for better similarity
                        )
                
                # Convert to list of lists
                if isinstance(embeddings, np.ndarray):
                    embeddings = embeddings.tolist()
                elif hasattr(embeddings, 'cpu'):
                    embeddings = embeddings.cpu().numpy().tolist()
                
                all_embeddings.extend(embeddings)
                
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Local embedding generation failed: {str(e)}")
            raise EmbeddingException(f"Local embedding error: {str(e)}")
    
    async def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional arguments (batch_size)
            
        Returns:
            List of embedding vectors
        """
        batch_size = kwargs.get('batch_size', 32)
        return self.embed_texts_sync(texts, batch_size)
    
    def embed_query_sync(self, query: str) -> List[float]:
        """
        Synchronous version of embed_query for internal use
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        if not self._initialize_sync():
            raise EmbeddingException(f"Local embedding model not initialized: {self._initialization_error}")
        
        try:
            with torch.no_grad():
                # Check if this is EmbeddingGemma model
                if "embeddinggemma" in self.model_name.lower():
                    # EmbeddingGemma uses encode_query for query embeddings
                    embedding = self.model.encode_query(
                        query,
                        convert_to_tensor=False
                    )
                else:
                    # Standard sentence-transformers models
                    embedding = self.model.encode(
                        [query],
                        convert_to_tensor=False,
                        show_progress_bar=False,
                        normalize_embeddings=True
                    )[0]
                
                # Convert to list
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                elif hasattr(embedding, 'cpu'):
                    embedding = embedding.cpu().numpy().tolist()
                    
                return embedding
                
        except Exception as e:
            logger.error(f"Local query embedding generation failed: {str(e)}")
            raise EmbeddingException(f"Local query embedding error: {str(e)}")
    
    async def embed_query(self, query: str, **kwargs) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text to embed
            **kwargs: Additional arguments
            
        Returns:
            Query embedding vector
        """
        return self.embed_query_sync(query)