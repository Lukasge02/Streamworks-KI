"""
RAG Cache Service
Enterprise-ready caching for embeddings and search results
"""

import hashlib
from typing import List, Dict, Any, Optional, Callable
from cachetools import TTLCache, LRUCache
from dataclasses import dataclass
import threading

from config import config


@dataclass
class CacheStats:
    """Cache statistics"""

    embedding_hits: int = 0
    embedding_misses: int = 0
    search_hits: int = 0
    search_misses: int = 0
    bm25_rebuilds: int = 0

    @property
    def embedding_hit_rate(self) -> float:
        total = self.embedding_hits + self.embedding_misses
        return self.embedding_hits / total if total > 0 else 0.0

    @property
    def search_hit_rate(self) -> float:
        total = self.search_hits + self.search_misses
        return self.search_hits / total if total > 0 else 0.0


class RAGCache:
    """
    Caching layer for RAG system performance optimization.

    Features:
    - Query embedding cache (LRU with TTL)
    - Search results cache (TTL-based)
    - BM25 index management
    - Thread-safe operations
    """

    def __init__(
        self,
        embedding_cache_size: int = None,
        search_cache_ttl: int = None,
        search_cache_size: int = 500,
    ):
        cache_size = embedding_cache_size or config.RAG_CACHE_MAX_SIZE
        cache_ttl = search_cache_ttl or config.RAG_CACHE_TTL

        # LRU cache for embeddings (no TTL needed, embeddings don't change)
        self._embedding_cache: LRUCache = LRUCache(maxsize=cache_size)

        # TTL cache for search results (results may change as docs change)
        self._search_cache: TTLCache = TTLCache(
            maxsize=search_cache_size, ttl=cache_ttl
        )

        # Lock for thread safety
        self._lock = threading.RLock()

        # Statistics
        self.stats = CacheStats()

        # BM25 index state
        self._bm25_corpus: Optional[List[List[str]]] = None
        self._bm25_doc_ids: Optional[List[str]] = None
        self._bm25_index = None
        self._bm25_dirty = True

    def _hash_key(self, *args) -> str:
        """Generate a hash key from arguments"""
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    # --- Embedding Cache ---

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        key = self._hash_key("emb", text)
        with self._lock:
            if key in self._embedding_cache:
                self.stats.embedding_hits += 1
                return self._embedding_cache[key]
            self.stats.embedding_misses += 1
            return None

    def set_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache embedding for text"""
        key = self._hash_key("emb", text)
        with self._lock:
            self._embedding_cache[key] = embedding

    def get_or_create_embedding(
        self, text: str, create_fn: Callable[[str], List[float]]
    ) -> List[float]:
        """Get cached embedding or create and cache it"""
        cached = self.get_embedding(text)
        if cached is not None:
            return cached

        embedding = create_fn(text)
        self.set_embedding(text, embedding)
        return embedding

    # --- Search Results Cache ---

    def get_search_results(
        self, query: str, limit: int, search_type: str = "hybrid"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        key = self._hash_key("search", query, limit, search_type)
        with self._lock:
            if key in self._search_cache:
                self.stats.search_hits += 1
                return self._search_cache[key]
            self.stats.search_misses += 1
            return None

    def set_search_results(
        self,
        query: str,
        limit: int,
        results: List[Dict[str, Any]],
        search_type: str = "hybrid",
    ) -> None:
        """Cache search results"""
        key = self._hash_key("search", query, limit, search_type)
        with self._lock:
            self._search_cache[key] = results

    # --- BM25 Index Management ---

    def get_bm25_index(self):
        """Get current BM25 index (may be None if dirty)"""
        return self._bm25_index if not self._bm25_dirty else None

    def set_bm25_index(
        self, index, corpus: List[List[str]], doc_ids: List[str]
    ) -> None:
        """Set BM25 index after rebuild"""
        with self._lock:
            self._bm25_index = index
            self._bm25_corpus = corpus
            self._bm25_doc_ids = doc_ids
            self._bm25_dirty = False
            self.stats.bm25_rebuilds += 1

    def get_bm25_doc_ids(self) -> Optional[List[str]]:
        """Get document IDs corresponding to BM25 index"""
        return self._bm25_doc_ids

    def invalidate_bm25(self) -> None:
        """Mark BM25 index as needing rebuild"""
        with self._lock:
            self._bm25_dirty = True

    def is_bm25_dirty(self) -> bool:
        """Check if BM25 needs rebuild"""
        return self._bm25_dirty

    # --- Cache Management ---

    def invalidate_all(self) -> None:
        """Clear all caches (call after document changes)"""
        with self._lock:
            self._search_cache.clear()
            self._bm25_dirty = True
            # Note: Embedding cache is NOT cleared - embeddings are stable

    def invalidate_search(self) -> None:
        """Clear search cache only"""
        with self._lock:
            self._search_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "embedding_cache_size": len(self._embedding_cache),
                "embedding_cache_max": self._embedding_cache.maxsize,
                "embedding_hit_rate": round(self.stats.embedding_hit_rate, 3),
                "search_cache_size": len(self._search_cache),
                "search_cache_max": self._search_cache.maxsize,
                "search_hit_rate": round(self.stats.search_hit_rate, 3),
                "bm25_dirty": self._bm25_dirty,
                "bm25_rebuilds": self.stats.bm25_rebuilds,
                "total_embedding_requests": self.stats.embedding_hits
                + self.stats.embedding_misses,
                "total_search_requests": self.stats.search_hits
                + self.stats.search_misses,
            }


# Singleton instance
rag_cache = RAGCache()
