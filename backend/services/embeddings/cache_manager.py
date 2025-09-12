"""
Multi-tier caching system for embedding services
"""
import hashlib
import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict, OrderedDict
import numpy as np
import threading

logger = logging.getLogger(__name__)


class EmbeddingCacheManager:
    """Multi-tier caching system for embeddings with semantic similarity matching"""
    
    def __init__(self, 
                 max_cache_size: int = 10000,
                 cache_ttl: int = 3600,
                 semantic_cache_size: int = 1000,
                 similarity_threshold: float = 0.95):
        # L1 Cache: Exact text matches
        self._exact_cache: OrderedDict[str, Tuple[List[float], float]] = OrderedDict()
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl
        
        # L2 Cache: Semantic similarity matches  
        self._semantic_cache: Dict[str, Tuple[List[float], str, float]] = {}
        self._semantic_embeddings: List[List[float]] = []
        self._semantic_keys: List[str] = []
        self.semantic_cache_size = semantic_cache_size
        self.similarity_threshold = similarity_threshold
        
        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.semantic_hits = 0
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info(f"Initialized cache manager (max_size={max_cache_size}, ttl={cache_ttl}s)")
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding from cache (exact or semantic match)
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding if found, None otherwise
        """
        cache_key = self._generate_cache_key(text)
        
        with self._lock:
            # Check L1 exact cache
            if cache_key in self._exact_cache:
                embedding, timestamp = self._exact_cache[cache_key]
                
                # Check if cache entry is still valid
                if time.time() - timestamp < self.cache_ttl:
                    # Move to end (LRU)
                    self._exact_cache.move_to_end(cache_key)
                    self.cache_hits += 1
                    logger.debug(f"L1 cache hit for key {cache_key[:8]}...")
                    return embedding
                else:
                    # Remove expired entry
                    del self._exact_cache[cache_key]
            
            # Check L2 semantic cache if we have a query embedding
            # This would require the query embedding to be passed in
            # For now, we'll skip semantic matching in the get method
            
            self.cache_misses += 1
            return None
    
    def cache_embedding(self, text: str, embedding: List[float]) -> None:
        """
        Cache an embedding
        
        Args:
            text: Original text
            embedding: Embedding vector
        """
        cache_key = self._generate_cache_key(text)
        
        with self._lock:
            # Add to L1 exact cache
            self._exact_cache[cache_key] = (embedding, time.time())
            
            # Enforce cache size limit (LRU eviction)
            while len(self._exact_cache) > self.max_cache_size:
                evicted_key = next(iter(self._exact_cache))
                del self._exact_cache[evicted_key]
                logger.debug(f"Evicted cache entry {evicted_key[:8]}...")
            
            # Optionally add to semantic cache if it's a significant embedding
            if len(self._semantic_cache) < self.semantic_cache_size:
                self._add_to_semantic_cache(cache_key, embedding, text)
    
    def _add_to_semantic_cache(self, cache_key: str, embedding: List[float], text: str) -> None:
        """Add embedding to semantic cache"""
        # Store in semantic cache
        self._semantic_cache[cache_key] = (embedding, text, time.time())
        self._semantic_embeddings.append(embedding)
        self._semantic_keys.append(cache_key)
        
        # Enforce semantic cache size
        if len(self._semantic_cache) > self.semantic_cache_size:
            # Remove oldest entry
            oldest_key = self._semantic_keys.pop(0)
            self._semantic_embeddings.pop(0)
            del self._semantic_cache[oldest_key]
    
    def find_semantic_match(self, query_embedding: List[float]) -> Optional[Tuple[str, List[float]]]:
        """
        Find semantically similar cached embedding
        
        Args:
            query_embedding: Query embedding to match
            
        Returns:
            Tuple of (original_text, cached_embedding) if match found
        """
        if not self._semantic_embeddings:
            return None
        
        with self._lock:
            # Calculate similarities
            similarities = [
                self._calculate_cosine_similarity(query_embedding, cached_emb)
                for cached_emb in self._semantic_embeddings
            ]
            
            # Find best match
            if similarities:
                max_similarity = max(similarities)
                if max_similarity >= self.similarity_threshold:
                    best_idx = similarities.index(max_similarity)
                    cache_key = self._semantic_keys[best_idx]
                    
                    if cache_key in self._semantic_cache:
                        embedding, text, timestamp = self._semantic_cache[cache_key]
                        
                        # Check if still valid
                        if time.time() - timestamp < self.cache_ttl:
                            self.semantic_hits += 1
                            logger.debug(f"Semantic cache hit (similarity={max_similarity:.3f})")
                            return text, embedding
            
            return None
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy for efficient calculation
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def clear_cache(self) -> None:
        """Clear all caches"""
        with self._lock:
            self._exact_cache.clear()
            self._semantic_cache.clear()
            self._semantic_embeddings.clear()
            self._semantic_keys.clear()
            logger.info("Cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "exact_cache_size": len(self._exact_cache),
                "semantic_cache_size": len(self._semantic_cache),
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "semantic_hits": self.semantic_hits,
                "hit_rate": f"{hit_rate:.1f}%",
                "total_requests": total_requests
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        with self._lock:
            current_time = time.time()
            expired_count = 0
            
            # Clean exact cache
            expired_keys = [
                key for key, (_, timestamp) in self._exact_cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            
            for key in expired_keys:
                del self._exact_cache[key]
                expired_count += 1
            
            # Clean semantic cache
            semantic_expired = [
                key for key, (_, _, timestamp) in self._semantic_cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            
            for key in semantic_expired:
                if key in self._semantic_keys:
                    idx = self._semantic_keys.index(key)
                    self._semantic_keys.pop(idx)
                    self._semantic_embeddings.pop(idx)
                del self._semantic_cache[key]
                expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            return expired_count