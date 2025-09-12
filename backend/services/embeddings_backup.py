"""
Embedding Service für Streamworks RAG MVP
Erstellt OpenAI Embeddings für document chunks mit Performance-Optimierung und Caching
"""

import asyncio
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np
import openai
from openai import AsyncOpenAI
import tiktoken
import torch
import time
import hashlib
import threading
from collections import defaultdict

from config import settings
from .docling_ingest import DocumentChunk

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, falling back to OpenAI only")

class LocalGammaEmbedder:
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
        
    def _initialize(self):
        """Lazy initialization of local embedding model"""
        if self._initialized:
            return True
            
        if self._initialization_error:
            raise self._initialization_error
            
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
            
        try:
            # Auto-detect device if needed
            if self.device == "auto":
                if torch.backends.mps.is_available():
                    self.device = "mps"
                elif torch.cuda.is_available():
                    self.device = "cuda" 
                else:
                    self.device = "cpu"
            
            logger.info(f"Initializing local embedding model {self.model_name} on {self.device}")
            
            # Load the model with trust_remote_code for custom models
            self.model = SentenceTransformer(self.model_name, device=self.device, trust_remote_code=True)
            self.model.eval()  # Set to evaluation mode
            
            # Get model dimensions
            self.dimensions = self.model.get_sentence_embedding_dimension()
            
            self._initialized = True
            logger.info(f"✅ Local embedding model loaded: {self.model_name} ({self.dimensions}D) on {self.device}")
            return True
            
        except Exception as e:
            self._initialization_error = e
            logger.error(f"Failed to initialize local embedding model: {str(e)}")
            raise e
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Create embeddings for texts using local model
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self._initialize():
            raise RuntimeError("Local embedding model not initialized")
        
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
            raise Exception(f"Local embedding error: {str(e)}")
    
    def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query using local model
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        if not self._initialize():
            raise RuntimeError("Local embedding model not initialized")
        
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
            raise Exception(f"Local query embedding error: {str(e)}")


class EmbeddingService:
    """Hybrid embedding service with local Gamma and OpenAI support mit Performance-Caching"""
    
    def __init__(self):
        # OpenAI setup
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.openai_model = settings.EMBEDDING_MODEL
        self.encoding = tiktoken.encoding_for_model("text-embedding-3-large")
        self.max_tokens = 8191  # OpenAI embedding limit
        
        # Local model setup
        self.local_embedder = None
        self.provider = getattr(settings, 'EMBEDDING_PROVIDER', 'gamma')  # gamma|openai|hybrid
        self.enable_fallback = getattr(settings, 'ENABLE_EMBEDDING_FALLBACK', True)
        
        # Performance caching system - Enhanced with multiple tiers
        self.embedding_cache = {}
        self.semantic_cache = {}  # Cache for semantically similar queries
        self.cache_ttl = getattr(settings, 'EMBEDDING_CACHE_TTL', 3600)  # 1 hour
        self.semantic_cache_ttl = getattr(settings, 'SEMANTIC_CACHE_TTL', 1800)  # 30 minutes
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0, "semantic_hits": 0}
        self.cache_lock = threading.RLock()
        
        # Cache optimization settings - improved configuration
        self.max_cache_size = getattr(settings, 'EMBEDDING_CACHE_SIZE', 1500)  # Optimized
        self.semantic_threshold = getattr(settings, 'SEMANTIC_SIMILARITY_THRESHOLD', 0.80)  # Less restrictive
        self.enable_semantic_cache = getattr(settings, 'ENABLE_SEMANTIC_CACHE', True)
        self.cache_cleanup_interval = getattr(settings, 'CACHE_CLEANUP_INTERVAL', 300)  # 5 minutes
        self.enable_performance_logging = getattr(settings, 'CACHE_PERFORMANCE_LOGGING', True)
        
        # Performance monitoring
        self.performance_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "avg_time": 0})
        
        logger.info(f"EmbeddingService initialized with provider: {self.provider} and caching enabled")
        
    async def initialize(self):
        """Initialize the embedding service (for compatibility with ChatService)"""
        # Already initialized in __init__, but keep this for compatibility
        logger.info("EmbeddingService initialization called (no-op)")
    
    def _generate_cache_key(self, text: str, provider: str = None) -> str:
        """Generate cache key for text"""
        provider = provider or self.provider
        content = f"{provider}:{text}"
        return f"embed_{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_cached_embedding(self, cache_key: str) -> Optional[List[float]]:
        """Get cached embedding if available and not expired"""
        with self.cache_lock:
            if cache_key in self.embedding_cache:
                cached_data = self.embedding_cache[cache_key]
                if time.time() - cached_data["timestamp"] < self.cache_ttl:
                    self.cache_stats["hits"] += 1
                    return cached_data["embedding"]
                else:
                    # Remove expired cache entry
                    del self.embedding_cache[cache_key]
                    self.cache_stats["evictions"] += 1
            return None
    
    def _cache_embedding(self, cache_key: str, embedding: List[float]) -> None:
        """Cache embedding with timestamp - Enhanced with smarter eviction"""
        with self.cache_lock:
            # Smart LRU: if cache is full, remove oldest AND least recently used entries
            if len(self.embedding_cache) >= self.max_cache_size:
                # Remove multiple oldest entries to reduce frequency of eviction operations
                items_to_remove = max(1, len(self.embedding_cache) - int(self.max_cache_size * 0.9))
                oldest_keys = sorted(self.embedding_cache.keys(), 
                                   key=lambda k: self.embedding_cache[k]["timestamp"])[:items_to_remove]
                for key in oldest_keys:
                    del self.embedding_cache[key]
                    self.cache_stats["evictions"] += 1
            
            self.embedding_cache[cache_key] = {
                "embedding": embedding,
                "timestamp": time.time(),
                "access_count": 1  # Track access frequency for smarter eviction
            }
    
    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            import numpy as np
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception:
            # Fallback to simple calculation if numpy not available
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
    
    def _find_semantic_match(self, query_embedding: List[float]) -> Optional[str]:
        """Find semantically similar cached embeddings"""
        if not self.enable_semantic_cache or not self.semantic_cache:
            return None
        
        best_match_key = None
        best_similarity = 0.0
        
        for cache_key, cached_data in self.semantic_cache.items():
            similarity = self._calculate_cosine_similarity(query_embedding, cached_data["embedding"])
            
            if similarity >= self.semantic_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match_key = cache_key
        
        if best_match_key:
            # Update access count for the matched entry
            self.semantic_cache[best_match_key]["access_count"] = self.semantic_cache[best_match_key].get("access_count", 0) + 1
            self.cache_stats["semantic_hits"] += 1
            logger.debug(f"Semantic cache hit: similarity={best_similarity:.3f}")
        
        return best_match_key
    
    def _cache_semantic_embedding(self, cache_key: str, embedding: List[float], original_text: str) -> None:
        """Cache embedding for semantic matching"""
        if not self.enable_semantic_cache:
            return
        
        with self.cache_lock:
            # Clean expired entries
            current_time = time.time()
            expired_keys = [
                key for key, data in self.semantic_cache.items()
                if current_time - data["timestamp"] > self.semantic_cache_ttl
            ]
            for key in expired_keys:
                del self.semantic_cache[key]
            
            # Limit semantic cache size
            max_semantic_cache = getattr(settings, 'SEMANTIC_CACHE_SIZE', 500)
            if len(self.semantic_cache) >= max_semantic_cache:
                # Remove least recently used
                oldest_key = min(self.semantic_cache.keys(),
                                key=lambda k: self.semantic_cache[k].get("access_count", 0))
                del self.semantic_cache[oldest_key]
            
            self.semantic_cache[cache_key] = {
                "embedding": embedding,
                "timestamp": current_time,
                "original_text": original_text[:200],  # Store truncated original for debugging
                "access_count": 1
            }
    
    def _update_performance_stats(self, operation: str, processing_time: float) -> None:
        """Update performance statistics"""
        stats = self.performance_stats[operation]
        stats["count"] += 1
        stats["total_time"] += processing_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get enhanced cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        total_hits = self.cache_stats["hits"] + self.cache_stats["semantic_hits"]
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        semantic_hit_rate = (self.cache_stats["semantic_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_stats": self.cache_stats.copy(),
            "hit_rate": f"{hit_rate:.2f}%",
            "semantic_hit_rate": f"{semantic_hit_rate:.2f}%",
            "effective_hit_rate": f"{hit_rate:.2f}%",
            "cache_size": len(self.embedding_cache),
            "semantic_cache_size": len(self.semantic_cache),
            "total_cache_size": len(self.embedding_cache) + len(self.semantic_cache),
            "cache_config": {
                "max_cache_size": self.max_cache_size,
                "semantic_threshold": self.semantic_threshold,
                "enable_semantic_cache": self.enable_semantic_cache,
                "cache_ttl": self.cache_ttl,
                "semantic_cache_ttl": self.semantic_cache_ttl
            },
            "performance_stats": dict(self.performance_stats)
        }
        
    def _get_local_embedder(self) -> Optional[LocalGammaEmbedder]:
        """Get local embedder with lazy loading"""
        if self.local_embedder is None:
            try:
                # Let LocalGammaEmbedder use its configured model from settings
                device = getattr(settings, 'LOCAL_EMBEDDING_DEVICE', 'auto')
                self.local_embedder = LocalGammaEmbedder(device=device)
                logger.info("Local Gamma embedder initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize local embedder: {str(e)}")
                if not self.enable_fallback:
                    raise e
                return None
        return self.local_embedder
        
    async def embed_chunks(self, chunks: List[Union[DocumentChunk, Dict[str, Any]]]) -> List[Union[DocumentChunk, Dict[str, Any]]]:
        """
        Create embeddings for document chunks using selected provider
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Same chunks with embeddings added to metadata
        """
        try:
            # Prepare texts for embedding
            texts = []
            for chunk in chunks:
                # Combine content with metadata for better embeddings
                enhanced_text = self._enhance_text_for_embedding(chunk)
                texts.append(enhanced_text)
            
            # Choose embedding method based on provider
            if self.provider == "gamma":
                embeddings = await self._embed_with_local(texts)
                model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
            elif self.provider == "openai":
                embeddings = await self._embed_with_openai(texts)
                model_name = self.openai_model
            else:  # hybrid - try local first, fallback to OpenAI
                try:
                    embeddings = await self._embed_with_local(texts)
                    model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
                    logger.info("Used local Gamma embeddings")
                except Exception as e:
                    logger.warning(f"Local embedding failed, falling back to OpenAI: {str(e)}")
                    embeddings = await self._embed_with_openai(texts)
                    model_name = self.openai_model
            
            # Add embeddings to chunk metadata
            for i, embedding in enumerate(embeddings):
                if isinstance(chunks[i], dict):
                    # Dictionary format from unified storage
                    chunks[i]['metadata']['embedding'] = embedding
                    chunks[i]['metadata']['embedding_model'] = model_name
                    chunks[i]['metadata']['embedding_provider'] = self.provider
                else:
                    # DocumentChunk object format
                    chunks[i].metadata['embedding'] = embedding
                    chunks[i].metadata['embedding_model'] = model_name
                    chunks[i].metadata['embedding_provider'] = self.provider
            
            logger.info(f"✅ Created {len(embeddings)} embeddings using {model_name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            raise Exception(f"Embedding service error: {str(e)}")
    
    async def _embed_with_local(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using local Gamma model"""
        local_embedder = self._get_local_embedder()
        if not local_embedder:
            raise RuntimeError("Local embedder not available")
        
        # Truncate texts for local model (usually more permissive than OpenAI)
        processed_texts = []
        for text in texts:
            # Most local models can handle longer texts, but let's be conservative
            if len(text) > 8000:  # Conservative limit
                text = text[:8000] + "..."
            processed_texts.append(text)
        
        # Run in thread pool to avoid blocking
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        def run_local_embedding():
            batch_size = getattr(settings, 'BATCH_SIZE_LOCAL', 32)
            return local_embedder.embed_texts(processed_texts, batch_size=batch_size)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            embeddings = await loop.run_in_executor(executor, run_local_embedding)
        
        return embeddings
    
    async def _embed_with_openai(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using OpenAI API"""
        # Truncate texts for OpenAI token limits
        processed_texts = []
        for text in texts:
            processed_texts.append(self._truncate_text(text))
        
        embeddings = []
        batch_size = 100  # OpenAI recommendation
        
        for i in range(0, len(processed_texts), batch_size):
            batch_texts = processed_texts[i:i + batch_size]
            
            # Get embeddings from OpenAI
            response = await self.openai_client.embeddings.create(
                model=self.openai_model,
                input=batch_texts,
                encoding_format="float"
            )
            
            # Extract embeddings
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
            
            logger.info(f"✅ Created OpenAI embeddings for batch {i//batch_size + 1}/{(len(processed_texts)-1)//batch_size + 1}")
        
        return embeddings
    
    def _enhance_text_for_embedding(self, chunk: Union[DocumentChunk, Dict[str, Any]]) -> str:
        """
        Enhance text with context for better embeddings
        """
        parts = []
        
        # Handle both DocumentChunk objects and dictionary format
        if isinstance(chunk, dict):
            # Dictionary format from unified storage
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            doctype = metadata.get("doctype")
            heading = metadata.get("heading")
            page_number = metadata.get("page")
        else:
            # DocumentChunk object format
            text = chunk.content
            doctype = chunk.doctype
            heading = chunk.heading
            page_number = chunk.page_number
        
        # Add document type context
        if doctype and doctype != "general":
            parts.append(f"Document type: {doctype}")
        
        # Add section/heading context
        if heading:
            parts.append(f"Section: {heading}")
        
        # Add main content
        parts.append(text)
        
        # Add page context if available
        if page_number:
            parts.append(f"Page: {page_number}")
        
        return " | ".join(parts)
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to fit OpenAI embedding token limits
        """
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= self.max_tokens:
            return text
        
        # Truncate tokens and decode back to text
        truncated_tokens = tokens[:self.max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    async def _generate_temp_embedding(self, text: str) -> List[float]:
        """Generate a temporary embedding for semantic cache search - optimized for speed"""
        # Use local model if available for faster semantic search
        if self.provider == "gamma" or (self.provider == "hybrid" and self._get_local_embedder()):
            try:
                local_embedder = self._get_local_embedder()
                if local_embedder:
                    return local_embedder.embed_query(text)
            except Exception:
                pass
        
        # Fallback to generating full embedding (this is slower but ensures semantic cache works)
        try:
            # Use a shorter timeout for semantic search to avoid blocking
            if self.provider == "openai":
                embeddings = await self._embed_with_openai([text])
            else:
                embeddings = await self._embed_with_local([text])
            return embeddings[0]
        except Exception:
            # If all else fails, return a dummy embedding (this prevents semantic cache from breaking)
            logger.warning("Could not generate temp embedding for semantic search")
            return [0.0] * 1536  # Default OpenAI embedding size
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query using selected provider with enhanced caching
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        start_time = time.time()
        
        try:
            # Check exact cache first
            cache_key = self._generate_cache_key(query)
            cached_embedding = self._get_cached_embedding(cache_key)
            
            if cached_embedding is not None:
                self._update_performance_stats("query_embedding_cache_hit", time.time() - start_time)
                logger.debug(f"Query embedding cache hit for: {query[:50]}...")
                return cached_embedding
            
            # If semantic caching is enabled, try to find semantically similar queries
            if self.enable_semantic_cache:
                # Generate a temporary embedding for semantic search (using faster method if available)
                temp_embedding = await self._generate_temp_embedding(query)
                
                semantic_match_key = self._find_semantic_match(temp_embedding)
                if semantic_match_key:
                    semantic_embedding = self.semantic_cache[semantic_match_key]["embedding"]
                    self._update_performance_stats("query_embedding_semantic_hit", time.time() - start_time)
                    logger.debug(f"Query embedding semantic cache hit for: {query[:50]}...")
                    
                    # Also cache this exact query for future exact matches
                    self._cache_embedding(cache_key, semantic_embedding)
                    return semantic_embedding
            
            self.cache_stats["misses"] += 1
            
            # Choose embedding method based on provider
            if self.provider == "gamma":
                embeddings = await self._embed_with_local([query])
                result = embeddings[0]
                used_provider = "gamma"
            elif self.provider == "openai":
                embeddings = await self._embed_with_openai([query])
                result = embeddings[0]
                used_provider = "openai"
            else:  # hybrid - try local first, fallback to OpenAI
                try:
                    embeddings = await self._embed_with_local([query])
                    result = embeddings[0]
                    used_provider = "gamma"
                except Exception as e:
                    logger.warning(f"Local query embedding failed, falling back to OpenAI: {str(e)}")
                    embeddings = await self._embed_with_openai([query])
                    result = embeddings[0]
                    used_provider = "openai"
            
            # Cache the result with both exact and semantic caching
            result_cache_key = self._generate_cache_key(query, used_provider)
            self._cache_embedding(result_cache_key, result)
            self._cache_semantic_embedding(result_cache_key, result, query)
            
            processing_time = time.time() - start_time
            self._update_performance_stats(f"query_embedding_{used_provider}", processing_time)
            
            logger.debug(f"Query embedding generated in {processing_time:.3f}s using {used_provider}")
            return result
            
        except Exception as e:
            logger.error(f"Query embedding failed: {str(e)}")
            raise Exception(f"Query embedding error: {str(e)}")
    
    def get_embedding(self, query: str) -> List[float]:
        """
        Synchronous wrapper for embed_query - for use in LangGraph nodes
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        import asyncio
        try:
            # Get current event loop or create new one
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to use a different approach
                # This is a workaround for sync calls in async environments
                import concurrent.futures
                import threading
                
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.embed_query(query))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=30)  # 30 second timeout
            else:
                # No event loop running, we can run directly
                return loop.run_until_complete(self.embed_query(query))
        except Exception as e:
            print(f"❌ Sync embedding failed: {str(e)}")
            # Fallback: return a zero vector of appropriate size
            return [0.0] * 3072  # text-embedding-3-large dimension
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            a_array = np.array(a)
            b_array = np.array(b)
            
            dot_product = np.dot(a_array, b_array)
            norm_a = np.linalg.norm(a_array)
            norm_b = np.linalg.norm(b_array)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
            
        except Exception:
            return 0.0
    
    async def batch_similarity(
        self, 
        query_embedding: List[float], 
        chunk_embeddings: List[List[float]]
    ) -> List[float]:
        """
        Calculate similarities between query and multiple chunk embeddings
        """
        similarities = []
        
        for chunk_embedding in chunk_embeddings:
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append(similarity)
        
        return similarities