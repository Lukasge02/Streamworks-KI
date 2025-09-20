"""
AI Response Cache System
Simple in-memory caching for OpenAI API responses to improve performance
"""

import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    response: Any
    timestamp: float
    hit_count: int = 0
    method: str = "unknown"

class AIResponseCache:
    """Thread-safe in-memory cache for AI responses"""

    def __init__(self, max_size: int = 2000, ttl_seconds: int = 7200):
        """Initialize cache with size limit and TTL - PERFORMANCE OPTIMIZED"""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        logger.info(f"🎯 Initialized AI Response Cache (max_size={max_size}, ttl={ttl_seconds}s)")

    def _generate_cache_key(self, prompt: str, context: str = "", method: str = "openai") -> str:
        """Generate deterministic cache key from prompt and context"""
        # Create normalized string for hashing
        normalized_input = f"{method}:{prompt}:{context}".strip().lower()
        # Generate hash
        return hashlib.sha256(normalized_input.encode('utf-8')).hexdigest()[:16]

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        return (time.time() - entry.timestamp) > self.ttl_seconds

    def _evict_oldest(self):
        """Evict oldest cache entries when at capacity"""
        if len(self._cache) >= self.max_size:
            # Sort by timestamp and remove oldest 20%
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].timestamp)
            evict_count = max(1, int(self.max_size * 0.2))

            for i in range(evict_count):
                key, _ = sorted_items[i]
                del self._cache[key]
                self._stats['evictions'] += 1

            logger.info(f"🗑️ Evicted {evict_count} oldest cache entries")

    def get(self, prompt: str, context: str = "", method: str = "openai") -> Optional[Any]:
        """Get cached response if available and not expired"""
        self._stats['total_requests'] += 1

        cache_key = self._generate_cache_key(prompt, context, method)

        if cache_key in self._cache:
            entry = self._cache[cache_key]

            if not self._is_expired(entry):
                # Cache hit - update hit count and return response
                entry.hit_count += 1
                self._stats['hits'] += 1

                logger.debug(f"🎯 Cache HIT for {method} (key: {cache_key[:8]}...)")
                return entry.response
            else:
                # Expired entry - remove it
                del self._cache[cache_key]
                logger.debug(f"⏰ Cache entry expired and removed (key: {cache_key[:8]}...)")

        # Cache miss
        self._stats['misses'] += 1
        logger.debug(f"❌ Cache MISS for {method} (key: {cache_key[:8]}...)")
        return None

    def set(self, prompt: str, response: Any, context: str = "", method: str = "openai") -> None:
        """Cache AI response with metadata"""
        # Evict old entries if necessary
        self._evict_oldest()

        cache_key = self._generate_cache_key(prompt, context, method)

        # Create cache entry
        entry = CacheEntry(
            response=response,
            timestamp=time.time(),
            method=method
        )

        self._cache[cache_key] = entry
        logger.debug(f"💾 Cached {method} response (key: {cache_key[:8]}...)")

    def clear(self) -> None:
        """Clear all cache entries"""
        cleared_count = len(self._cache)
        self._cache.clear()
        logger.info(f"🧹 Cleared {cleared_count} cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        if self._stats['total_requests'] > 0:
            hit_rate = self._stats['hits'] / self._stats['total_requests']

        return {
            **self._stats,
            'cache_size': len(self._cache),
            'hit_rate': hit_rate,
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'memory_usage_mb': self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB (rough approximation)"""
        try:
            import sys
            total_size = 0
            for key, entry in self._cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(entry)
                total_size += sys.getsizeof(entry.response)
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0.0

    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if (current_time - entry.timestamp) > self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

# Global cache instance
_global_cache = None

def get_ai_cache() -> AIResponseCache:
    """Get or create global AI response cache - PERFORMANCE OPTIMIZED"""
    global _global_cache
    if _global_cache is None:
        _global_cache = AIResponseCache(
            max_size=2000,      # Doubled for better hit rate
            ttl_seconds=7200    # 2 hours for longer retention
        )
    return _global_cache

def cache_ai_response(prompt: str, response: Any, context: str = "", method: str = "openai") -> None:
    """Cache AI response using global cache"""
    cache = get_ai_cache()
    cache.set(prompt, response, context, method)

def get_cached_ai_response(prompt: str, context: str = "", method: str = "openai") -> Optional[Any]:
    """Get cached AI response using global cache"""
    cache = get_ai_cache()
    return cache.get(prompt, context, method)

def clear_ai_cache() -> None:
    """Clear global AI cache"""
    cache = get_ai_cache()
    cache.clear()

def get_ai_cache_stats() -> Dict[str, Any]:
    """Get global AI cache statistics"""
    cache = get_ai_cache()
    return cache.get_stats()