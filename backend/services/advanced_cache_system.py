"""
Advanced Multi-Level Cache System for Streamworks RAG
Performance-optimized caching with semantic similarity and intelligent TTL
"""

import asyncio
import hashlib
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
import numpy as np
from threading import RLock

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata and analytics"""
    key: str
    value: Any
    timestamp: float
    ttl: float
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    access_pattern: List[float] = field(default_factory=list)
    semantic_vector: Optional[List[float]] = None
    confidence_score: float = 1.0
    tags: List[str] = field(default_factory=list)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return (time.time() - self.timestamp) > self.ttl

    def update_access(self):
        """Update access statistics"""
        current_time = time.time()
        self.hit_count += 1
        self.last_accessed = current_time
        self.access_pattern.append(current_time)

        # Keep only last 10 access times for pattern analysis
        if len(self.access_pattern) > 10:
            self.access_pattern = self.access_pattern[-10:]

    def get_access_frequency(self) -> float:
        """Calculate access frequency (accesses per hour)"""
        if len(self.access_pattern) < 2:
            return 0.0

        time_span = self.access_pattern[-1] - self.access_pattern[0]
        if time_span == 0:
            return float('inf')

        return len(self.access_pattern) / (time_span / 3600)  # per hour

class SemanticCacheLayer:
    """Semantic similarity-based cache layer"""

    def __init__(self, max_size: int = 500, similarity_threshold: float = 0.85):
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.entries: Dict[str, CacheEntry] = {}
        self.vectors: Dict[str, np.ndarray] = {}
        self._lock = RLock()

    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0

    def find_similar(self, query_vector: np.ndarray, threshold: Optional[float] = None) -> Optional[CacheEntry]:
        """Find semantically similar cached entry"""
        if threshold is None:
            threshold = self.similarity_threshold

        with self._lock:
            best_similarity = 0.0
            best_entry = None

            for key, cached_vector in self.vectors.items():
                similarity = self._calculate_similarity(query_vector, cached_vector)

                if similarity > best_similarity and similarity >= threshold:
                    entry = self.entries.get(key)
                    if entry and not entry.is_expired():
                        best_similarity = similarity
                        best_entry = entry

            return best_entry

    def add(self, key: str, value: Any, vector: List[float], ttl: float = 3600, **kwargs) -> None:
        """Add entry to semantic cache"""
        with self._lock:
            # Convert to numpy array
            np_vector = np.array(vector)

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                semantic_vector=vector,
                **kwargs
            )

            # Add to caches
            self.entries[key] = entry
            self.vectors[key] = np_vector

            # Cleanup if needed
            self._cleanup_if_needed()

    def _cleanup_if_needed(self):
        """Remove old/expired entries if cache is full"""
        if len(self.entries) <= self.max_size:
            return

        # Remove expired entries first
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            self.entries.pop(key, None)
            self.vectors.pop(key, None)

        # If still too many, remove least recently used
        if len(self.entries) > self.max_size:
            # Sort by last accessed time
            sorted_entries = sorted(
                self.entries.items(),
                key=lambda x: x[1].last_accessed
            )

            # Remove oldest 20%
            remove_count = max(1, int(self.max_size * 0.2))
            for key, _ in sorted_entries[:remove_count]:
                self.entries.pop(key, None)
                self.vectors.pop(key, None)

class AdvancedCacheSystem:
    """
    Multi-level cache system with intelligent management

    Levels:
    1. L1 Cache: In-memory, fastest access (frequently used items)
    2. L2 Cache: Standard cache with TTL (regular items)
    3. L3 Cache: Semantic cache (similar queries)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize advanced cache system"""
        self.config = config or {}

        # Cache configuration
        self.l1_max_size = self.config.get('l1_max_size', 200)
        self.l2_max_size = self.config.get('l2_max_size', 1000)
        self.l3_max_size = self.config.get('l3_max_size', 500)

        self.default_ttl = self.config.get('default_ttl', 3600)
        self.semantic_threshold = self.config.get('semantic_threshold', 0.85)

        # Cache layers
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # LRU cache
        self.l2_cache: Dict[str, CacheEntry] = {}
        self.l3_cache = SemanticCacheLayer(self.l3_max_size, self.semantic_threshold)

        # Thread safety
        self._l1_lock = RLock()
        self._l2_lock = RLock()

        # Statistics
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'l3_hits': 0,
            'l3_misses': 0,
            'total_requests': 0,
            'semantic_matches': 0,
            'cache_promotions': 0,
            'evictions': 0
        }

        logger.info(f"🚀 Advanced Cache System initialized (L1:{self.l1_max_size}, L2:{self.l2_max_size}, L3:{self.l3_max_size})")

    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate consistent cache key"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    async def get(self,
                  key: str,
                  semantic_vector: Optional[List[float]] = None,
                  use_semantic: bool = True) -> Optional[Any]:
        """
        Get value from cache with multi-level lookup

        Args:
            key: Cache key
            semantic_vector: Vector for semantic search
            use_semantic: Whether to use semantic cache

        Returns:
            Cached value or None
        """
        self.stats['total_requests'] += 1

        # L1 Cache (fastest)
        with self._l1_lock:
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired():
                    entry.update_access()
                    # Move to end (most recently used)
                    self.l1_cache.move_to_end(key)
                    self.stats['l1_hits'] += 1
                    logger.debug(f"🎯 L1 Cache HIT: {key[:8]}...")
                    return entry.value
                else:
                    # Remove expired entry
                    del self.l1_cache[key]

        self.stats['l1_misses'] += 1

        # L2 Cache (standard)
        with self._l2_lock:
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if not entry.is_expired():
                    entry.update_access()
                    self.stats['l2_hits'] += 1

                    # Promote to L1 if frequently accessed
                    if entry.get_access_frequency() > 2.0:  # 2+ accesses per hour
                        await self._promote_to_l1(key, entry)

                    logger.debug(f"🎯 L2 Cache HIT: {key[:8]}...")
                    return entry.value
                else:
                    # Remove expired entry
                    del self.l2_cache[key]

        self.stats['l2_misses'] += 1

        # L3 Cache (semantic similarity)
        if use_semantic and semantic_vector:
            try:
                np_vector = np.array(semantic_vector)
                similar_entry = self.l3_cache.find_similar(np_vector)

                if similar_entry:
                    similar_entry.update_access()
                    self.stats['l3_hits'] += 1
                    self.stats['semantic_matches'] += 1

                    # Promote semantic match to L2
                    await self._promote_to_l2(key, similar_entry.value, similar_entry.ttl)

                    logger.debug(f"🎯 L3 Semantic HIT: {key[:8]}... (similarity match)")
                    return similar_entry.value
            except Exception as e:
                logger.warning(f"Semantic cache lookup failed: {str(e)}")

        self.stats['l3_misses'] += 1
        logger.debug(f"❌ Cache MISS: {key[:8]}...")
        return None

    async def set(self,
                  key: str,
                  value: Any,
                  ttl: Optional[float] = None,
                  semantic_vector: Optional[List[float]] = None,
                  confidence_score: float = 1.0,
                  tags: Optional[List[str]] = None) -> None:
        """
        Set value in appropriate cache level

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            semantic_vector: Vector for semantic caching
            confidence_score: Confidence in cached value (0-1)
            tags: Tags for categorization
        """
        if ttl is None:
            ttl = self.default_ttl

        tags = tags or []

        # Calculate estimated size
        try:
            size_bytes = len(json.dumps(value, default=str).encode())
        except:
            size_bytes = 1024  # Default estimate

        # Determine cache level based on various factors
        cache_level = await self._determine_cache_level(
            key, value, confidence_score, size_bytes, tags
        )

        if cache_level == 1:
            await self._set_l1(key, value, ttl, confidence_score, tags, size_bytes)
        elif cache_level == 2:
            await self._set_l2(key, value, ttl, confidence_score, tags, size_bytes)

        # Always add to semantic cache if vector provided
        if semantic_vector and confidence_score > 0.7:
            self.l3_cache.add(
                key=key,
                value=value,
                vector=semantic_vector,
                ttl=ttl,
                confidence_score=confidence_score,
                tags=tags,
                size_bytes=size_bytes
            )
            logger.debug(f"💾 Added to L3 (semantic): {key[:8]}...")

    async def _determine_cache_level(self,
                                   key: str,
                                   value: Any,
                                   confidence_score: float,
                                   size_bytes: int,
                                   tags: List[str]) -> int:
        """Determine appropriate cache level for new entry"""

        # High confidence, small size -> L1
        if confidence_score > 0.9 and size_bytes < 5000:
            return 1

        # Special tags for L1 (frequently accessed items)
        priority_tags = ['user_query', 'frequent', 'hot']
        if any(tag in tags for tag in priority_tags):
            return 1

        # Default to L2
        return 2

    async def _set_l1(self, key: str, value: Any, ttl: float, confidence_score: float, tags: List[str], size_bytes: int):
        """Set value in L1 cache"""
        with self._l1_lock:
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                confidence_score=confidence_score,
                tags=tags,
                size_bytes=size_bytes
            )

            self.l1_cache[key] = entry

            # LRU eviction if needed
            if len(self.l1_cache) > self.l1_max_size:
                # Remove oldest item
                oldest_key, _ = self.l1_cache.popitem(last=False)
                self.stats['evictions'] += 1
                logger.debug(f"🗑️ L1 eviction: {oldest_key[:8]}...")

            logger.debug(f"💾 Added to L1: {key[:8]}...")

    async def _set_l2(self, key: str, value: Any, ttl: float, confidence_score: float, tags: List[str], size_bytes: int):
        """Set value in L2 cache"""
        with self._l2_lock:
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                confidence_score=confidence_score,
                tags=tags,
                size_bytes=size_bytes
            )

            self.l2_cache[key] = entry

            # Size-based eviction if needed
            if len(self.l2_cache) > self.l2_max_size:
                await self._evict_l2_entries()

            logger.debug(f"💾 Added to L2: {key[:8]}...")

    async def _evict_l2_entries(self):
        """Evict entries from L2 cache using intelligent strategy"""
        with self._l2_lock:
            if len(self.l2_cache) <= self.l2_max_size:
                return

            # Remove expired entries first
            expired_keys = [
                key for key, entry in self.l2_cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self.l2_cache[key]
                self.stats['evictions'] += 1

            # If still too many, remove by score (LFU + confidence)
            if len(self.l2_cache) > self.l2_max_size:
                # Calculate eviction scores (lower = more likely to evict)
                scored_entries = []
                for key, entry in self.l2_cache.items():
                    score = (
                        entry.hit_count * 0.4 +              # Access frequency
                        entry.confidence_score * 0.3 +       # Confidence
                        entry.get_access_frequency() * 0.3   # Recent access pattern
                    )
                    scored_entries.append((score, key))

                # Sort and remove lowest scored
                scored_entries.sort()
                remove_count = len(self.l2_cache) - self.l2_max_size + int(self.l2_max_size * 0.1)

                for _, key in scored_entries[:remove_count]:
                    del self.l2_cache[key]
                    self.stats['evictions'] += 1

    async def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote frequently accessed L2 entry to L1"""
        with self._l1_lock:
            self.l1_cache[key] = entry

            # Handle L1 overflow
            if len(self.l1_cache) > self.l1_max_size:
                oldest_key, oldest_entry = self.l1_cache.popitem(last=False)
                # Demote to L2
                with self._l2_lock:
                    self.l2_cache[oldest_key] = oldest_entry

        self.stats['cache_promotions'] += 1
        logger.debug(f"⬆️ Promoted to L1: {key[:8]}...")

    async def _promote_to_l2(self, key: str, value: Any, ttl: float):
        """Promote semantic match to L2 cache"""
        await self._set_l2(key, value, ttl, 0.8, ['semantic_match'], 1024)
        self.stats['cache_promotions'] += 1

    def invalidate(self, key: str) -> bool:
        """Remove key from all cache levels"""
        removed = False

        with self._l1_lock:
            if key in self.l1_cache:
                del self.l1_cache[key]
                removed = True

        with self._l2_lock:
            if key in self.l2_cache:
                del self.l2_cache[key]
                removed = True

        with self.l3_cache._lock:
            if key in self.l3_cache.entries:
                del self.l3_cache.entries[key]
                self.l3_cache.vectors.pop(key, None)
                removed = True

        if removed:
            logger.debug(f"🗑️ Invalidated: {key[:8]}...")

        return removed

    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Remove entries matching any of the given tags"""
        removed_count = 0

        # L1 cache
        with self._l1_lock:
            keys_to_remove = [
                key for key, entry in self.l1_cache.items()
                if any(tag in entry.tags for tag in tags)
            ]
            for key in keys_to_remove:
                del self.l1_cache[key]
                removed_count += 1

        # L2 cache
        with self._l2_lock:
            keys_to_remove = [
                key for key, entry in self.l2_cache.items()
                if any(tag in entry.tags for tag in tags)
            ]
            for key in keys_to_remove:
                del self.l2_cache[key]
                removed_count += 1

        # L3 cache
        with self.l3_cache._lock:
            keys_to_remove = [
                key for key, entry in self.l3_cache.entries.items()
                if any(tag in entry.tags for tag in tags)
            ]
            for key in keys_to_remove:
                del self.l3_cache.entries[key]
                self.l3_cache.vectors.pop(key, None)
                removed_count += 1

        logger.info(f"🗑️ Invalidated {removed_count} entries with tags: {tags}")
        return removed_count

    def clear_all(self) -> None:
        """Clear all cache levels"""
        with self._l1_lock:
            self.l1_cache.clear()

        with self._l2_lock:
            self.l2_cache.clear()

        with self.l3_cache._lock:
            self.l3_cache.entries.clear()
            self.l3_cache.vectors.clear()

        logger.info("🧹 Cleared all cache levels")

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.stats['total_requests']

        if total_requests == 0:
            hit_rate = 0.0
        else:
            total_hits = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['l3_hits']
            hit_rate = (total_hits / total_requests) * 100

        # Cache sizes
        l1_size = len(self.l1_cache)
        l2_size = len(self.l2_cache)
        l3_size = len(self.l3_cache.entries)

        # Memory usage estimation
        l1_memory = sum(entry.size_bytes for entry in self.l1_cache.values())
        l2_memory = sum(entry.size_bytes for entry in self.l2_cache.values())
        l3_memory = sum(entry.size_bytes for entry in self.l3_cache.entries.values())

        return {
            'performance': {
                'total_requests': total_requests,
                'overall_hit_rate': round(hit_rate, 2),
                'l1_hit_rate': round((self.stats['l1_hits'] / max(total_requests, 1)) * 100, 2),
                'l2_hit_rate': round((self.stats['l2_hits'] / max(total_requests, 1)) * 100, 2),
                'l3_hit_rate': round((self.stats['l3_hits'] / max(total_requests, 1)) * 100, 2),
                'semantic_match_rate': round((self.stats['semantic_matches'] / max(total_requests, 1)) * 100, 2)
            },
            'usage': {
                'l1_size': l1_size,
                'l2_size': l2_size,
                'l3_size': l3_size,
                'l1_utilization': round((l1_size / self.l1_max_size) * 100, 1),
                'l2_utilization': round((l2_size / self.l2_max_size) * 100, 1),
                'l3_utilization': round((l3_size / self.l3_max_size) * 100, 1)
            },
            'memory': {
                'l1_memory_kb': round(l1_memory / 1024, 2),
                'l2_memory_kb': round(l2_memory / 1024, 2),
                'l3_memory_kb': round(l3_memory / 1024, 2),
                'total_memory_kb': round((l1_memory + l2_memory + l3_memory) / 1024, 2)
            },
            'operations': {
                'cache_promotions': self.stats['cache_promotions'],
                'evictions': self.stats['evictions'],
                'semantic_matches': self.stats['semantic_matches']
            },
            'timestamp': datetime.now().isoformat()
        }

    async def optimize(self) -> Dict[str, Any]:
        """Run cache optimization and return results"""
        start_time = time.time()
        optimizations = []

        # Remove expired entries
        expired_l1 = []
        with self._l1_lock:
            expired_l1 = [key for key, entry in self.l1_cache.items() if entry.is_expired()]
            for key in expired_l1:
                del self.l1_cache[key]

        expired_l2 = []
        with self._l2_lock:
            expired_l2 = [key for key, entry in self.l2_cache.items() if entry.is_expired()]
            for key in expired_l2:
                del self.l2_cache[key]

        total_expired = len(expired_l1) + len(expired_l2)
        if total_expired > 0:
            optimizations.append(f"Removed {total_expired} expired entries")

        # Optimize cache levels if needed
        if len(self.l2_cache) > self.l2_max_size * 0.9:
            await self._evict_l2_entries()
            optimizations.append("Optimized L2 cache utilization")

        optimization_time = (time.time() - start_time) * 1000

        return {
            'optimization_time_ms': round(optimization_time, 2),
            'optimizations_applied': optimizations,
            'cache_stats': self.get_statistics()
        }

# Global advanced cache instance
_advanced_cache_system = None

async def get_advanced_cache() -> AdvancedCacheSystem:
    """Get or create global advanced cache system"""
    global _advanced_cache_system
    if _advanced_cache_system is None:
        from config import settings
        config = {
            'l1_max_size': 300,                    # Increased L1 for frequently used
            'l2_max_size': 2000,                   # Increased L2 for better coverage
            'l3_max_size': 800,                    # Increased L3 for semantic matching
            'default_ttl': settings.EMBEDDING_CACHE_TTL,
            'semantic_threshold': settings.SEMANTIC_SIMILARITY_THRESHOLD
        }
        _advanced_cache_system = AdvancedCacheSystem(config)
    return _advanced_cache_system