"""
Local Gamma embedding model implementation
"""
import logging
from typing import List, Optional
import numpy as np
import torch
import threading
import time
from functools import wraps

from .base import EmbeddingInterface, EmbeddingException

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, local embeddings disabled")


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


class LocalGammaEmbedder(EmbeddingInterface):
    """Robust local Gamma embedding model handler with optimizations"""
    
    def __init__(self, model_name: str = None, device: str = "auto", max_batch_size: int = 32):
        # Use configured model if not provided
        if model_name is None:
            from config import settings
            model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
            max_batch_size = getattr(settings, 'BATCH_SIZE_LOCAL', 32)
        
        self.model_name = model_name
        self.model = None
        self.device = device
        self.max_batch_size = max_batch_size
        self._initialized = False
        self._initialization_error = None
        self._lock = threading.Lock()
        self._device_name = None
        
        # Performance tracking
        self.stats = {
            "total_embeddings": 0,
            "total_batches": 0,
            "avg_batch_time": 0.0,
            "initialization_time": 0.0
        }
        
    @retry_on_failure(max_retries=3, delay=2.0)
    def _initialize_sync(self) -> bool:
        """Synchronous initialization of local embedding model with retry logic"""
        if self._initialized:
            return True
            
        if self._initialization_error and not hasattr(self, '_retry_initialization'):
            return False
            
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialization_error = "sentence-transformers not installed"
            return False
        
        with self._lock:
            if self._initialized:
                return True
                
            start_time = time.time()
            try:
                logger.info(f"Initializing local embedding model: {self.model_name}")
                
                # Determine device with better validation
                if self.device == "auto":
                    if torch.cuda.is_available():
                        device = "cuda"
                        logger.info(f"CUDA available: {torch.cuda.get_device_name()}")
                    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                        device = "mps"
                        logger.info("MPS (Apple Silicon) acceleration available")
                    else:
                        device = "cpu"
                        logger.info("Using CPU for embeddings")
                else:
                    device = self.device
                    # Validate custom device
                    if device == "cuda" and not torch.cuda.is_available():
                        logger.warning("CUDA requested but not available, falling back to CPU")
                        device = "cpu"
                
                self._device_name = device
                
                # Load model with optimized parameters
                model_kwargs = {
                    "device": device,
                    "trust_remote_code": True
                }
                
                # EmbeddingGemma-specific or standard initialization
                if "embeddinggemma" in self.model_name.lower():
                    logger.info("Loading EmbeddingGemma model with specialized configuration")
                    self.model = SentenceTransformer(self.model_name, **model_kwargs)
                else:
                    logger.info("Loading standard sentence-transformers model")
                    self.model = SentenceTransformer(self.model_name, **model_kwargs)
                
                # Optimize model for inference
                if hasattr(self.model, 'eval'):
                    self.model.eval()
                
                # Test with a simple embedding to validate
                test_embedding = self._generate_embedding_safe(["test"], is_query=True)
                if not test_embedding or len(test_embedding) == 0:
                    raise Exception("Model validation failed - empty embedding generated")
                
                self._initialized = True
                init_time = time.time() - start_time
                self.stats["initialization_time"] = init_time
                
                logger.info(f"✅ Local embedding model initialized on {device} in {init_time:.2f}s")
                logger.info(f"✅ Model produces {len(test_embedding[0])}-dimensional embeddings")
                return True
                
            except Exception as e:
                self._initialization_error = str(e)
                logger.error(f"❌ Failed to initialize local embedding model: {e}")
                return False
    
    async def initialize(self) -> None:
        """Initialize the embedding provider"""
        if not self._initialize_sync():
            raise EmbeddingException(f"Failed to initialize local embedder: {self._initialization_error}")
    
    async def cleanup(self) -> None:
        """Enhanced cleanup with better resource management"""
        if self.model is not None:
            logger.info("Cleaning up local embedding model resources")
            try:
                # Clear model from memory
                del self.model
                self.model = None
                self._initialized = False
                
                # Clear CUDA cache if available
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                # Clear MPS cache if available
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                    
                logger.info("✅ Local embedding model cleanup completed")
                
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
    
    def _generate_embedding_safe(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Safe embedding generation with proper error handling"""
        if not texts:
            return []
        
        try:
            with torch.no_grad():
                if "embeddinggemma" in self.model_name.lower():
                    if is_query:
                        # Single query embedding
                        embedding = self.model.encode_query(
                            texts[0] if len(texts) == 1 else texts,
                            convert_to_tensor=False
                        )
                        if len(texts) == 1:
                            # Ensure it's a list of lists
                            if isinstance(embedding, np.ndarray):
                                return [embedding.tolist()]
                            return [embedding]
                        else:
                            if isinstance(embedding, np.ndarray):
                                return embedding.tolist()
                            return embedding
                    else:
                        # Document embeddings
                        embeddings = self.model.encode_document(
                            texts,
                            convert_to_tensor=False,
                            show_progress_bar=False
                        )
                else:
                    # Standard sentence-transformers models
                    embeddings = self.model.encode(
                        texts,
                        convert_to_tensor=False,
                        show_progress_bar=False,
                        normalize_embeddings=True
                    )
                
                # Normalize output format
                if isinstance(embeddings, np.ndarray):
                    return embeddings.tolist()
                elif hasattr(embeddings, 'cpu'):
                    return embeddings.cpu().numpy().tolist()
                else:
                    return embeddings
                    
        except Exception as e:
            logger.error(f"Safe embedding generation failed: {e}")
            raise
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def embed_texts_sync(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """
        Optimized synchronous embedding generation with retry logic
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing (uses instance default if None)
            
        Returns:
            List of embedding vectors
        """
        if not self._initialize_sync():
            raise EmbeddingException(f"Local embedding model not initialized: {self._initialization_error}")
        
        if not texts:
            return []
        
        # Use instance batch size if not provided
        if batch_size is None:
            batch_size = self.max_batch_size
        
        try:
            start_time = time.time()
            all_embeddings = []
            
            # Process in optimized batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_start = time.time()
                
                # Generate embeddings with safe method
                batch_embeddings = self._generate_embedding_safe(batch, is_query=False)
                all_embeddings.extend(batch_embeddings)
                
                # Update stats
                batch_time = time.time() - batch_start
                self.stats["total_batches"] += 1
                self.stats["avg_batch_time"] = (
                    (self.stats["avg_batch_time"] * (self.stats["total_batches"] - 1) + batch_time) 
                    / self.stats["total_batches"]
                )
                
                # Memory cleanup for large batches
                if len(batch) > 16 and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            self.stats["total_embeddings"] += len(texts)
            total_time = time.time() - start_time
            
            logger.debug(f"Embedded {len(texts)} texts in {total_time:.2f}s ({len(texts)/total_time:.1f} texts/s)")
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
    
    @retry_on_failure(max_retries=2, delay=0.5) 
    def embed_query_sync(self, query: str) -> List[float]:
        """
        Optimized synchronous query embedding generation with retry logic
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        if not self._initialize_sync():
            raise EmbeddingException(f"Local embedding model not initialized: {self._initialization_error}")
        
        if not query.strip():
            raise EmbeddingException("Empty query provided")
        
        try:
            start_time = time.time()
            
            # Generate single query embedding
            embeddings = self._generate_embedding_safe([query], is_query=True)
            
            if not embeddings or len(embeddings) == 0:
                raise EmbeddingException("Empty embedding generated")
            
            embedding = embeddings[0]
            self.stats["total_embeddings"] += 1
            
            query_time = time.time() - start_time
            logger.debug(f"Query embedded in {query_time:.3f}s")
            
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
    
    def get_stats(self) -> dict:
        """Get embedder performance statistics"""
        return {
            "model_name": self.model_name,
            "device": self._device_name,
            "initialized": self._initialized,
            "max_batch_size": self.max_batch_size,
            **self.stats
        }
    
    def clear_stats(self) -> None:
        """Clear performance statistics"""
        self.stats = {
            "total_embeddings": 0,
            "total_batches": 0,
            "avg_batch_time": 0.0,
            "initialization_time": self.stats.get("initialization_time", 0.0)
        }