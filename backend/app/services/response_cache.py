"""
Intelligent Response Cache für drastische Performance-Verbesserung
Cache Hit → <1s Response Time (statt 15-27s)
"""
import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

from app.core.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache Entry mit Metadaten"""
    response: str
    timestamp: datetime
    hit_count: int
    last_accessed: datetime
    query_hash: str
    context_hash: str
    response_time: float
    metadata: Dict[str, Any]
    
    def is_expired(self, ttl_seconds: int = 3600) -> bool:
        """Check if cache entry is expired"""
        return (datetime.now() - self.timestamp).total_seconds() > ttl_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }

@dataclass
class CacheStats:
    """Cache Performance Statistiken"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    avg_hit_response_time: float = 0.0
    avg_miss_response_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def time_saved(self) -> float:
        """Estimate total time saved by caching"""
        if self.cache_hits == 0:
            return 0.0
        return self.cache_hits * (self.avg_miss_response_time - self.avg_hit_response_time)

class ResponseCache:
    """
    Intelligent Response Cache für LLM Responses
    
    Features:
    - Semantic query similarity matching
    - Context-aware caching
    - Automatic cache cleanup
    - Performance monitoring
    - Configurable TTL
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 ttl_seconds: int = 3600,  # 1 hour default
                 similarity_threshold: float = 0.95):
        
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.similarity_threshold = similarity_threshold
        
        # Cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        
        # Performance tracking
        self.stats = CacheStats()
        self._hit_times = []
        self._miss_times = []
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_started = False
        
        logger.info(f"🗄️ Response Cache initialized (size: {max_size}, TTL: {ttl_seconds}s)")
    
    def _start_cleanup_task(self):
        """Start automatic cache cleanup task - only if event loop is running"""
        if self._cleanup_started:
            return
            
        try:
            async def cleanup_loop():
                while True:
                    try:
                        await asyncio.sleep(300)  # Cleanup every 5 minutes
                        await self._cleanup_expired()
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Cache cleanup error: {e}")
            
            self._cleanup_task = asyncio.create_task(cleanup_loop())
            self._cleanup_started = True
            logger.info("🧹 Cache cleanup task started")
        except RuntimeError:
            # No event loop running, cleanup task will be started later
            logger.debug("No event loop running, cleanup task will be started when needed")
    
    def _generate_cache_key(self, query: str, context: str = "") -> str:
        """Generate cache key from query and context"""
        # Normalize query
        normalized_query = query.lower().strip()
        normalized_context = context.lower().strip()[:500]  # Limit context for key
        
        # Create hash
        content = f"{normalized_query}:{normalized_context}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _compute_query_similarity(self, query1: str, query2: str) -> float:
        """Compute simple similarity between queries (can be enhanced with embeddings)"""
        # Normalize queries
        q1 = set(query1.lower().split())
        q2 = set(query2.lower().split())
        
        # Jaccard similarity
        if not q1 and not q2:
            return 1.0
        if not q1 or not q2:
            return 0.0
        
        intersection = len(q1.intersection(q2))
        union = len(q1.union(q2))
        
        return intersection / union if union > 0 else 0.0
    
    async def get(self, query: str, context: str = "") -> Optional[Tuple[str, CacheEntry]]:
        """
        Get cached response for query
        
        Returns:
            Tuple of (response, cache_entry) if found, None otherwise
        """
        # Start cleanup task if not already started
        if not self._cleanup_started:
            self._start_cleanup_task()
            
        start_time = time.time()
        self.stats.total_requests += 1
        
        async with self._lock:
            cache_key = self._generate_cache_key(query, context)
            
            # Direct cache hit
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                if not entry.is_expired(self.ttl_seconds):
                    # Update access statistics
                    entry.hit_count += 1
                    entry.last_accessed = datetime.now()
                    
                    # Update performance stats
                    hit_time = time.time() - start_time
                    self._hit_times.append(hit_time)
                    if len(self._hit_times) > 100:
                        self._hit_times.pop(0)
                    
                    self.stats.cache_hits += 1
                    self.stats.avg_hit_response_time = sum(self._hit_times) / len(self._hit_times)
                    
                    logger.debug(f"🎯 Cache HIT: {query[:50]}... ({hit_time:.3f}s)")
                    return entry.response, entry
                else:
                    # Expired entry
                    del self._cache[cache_key]
                    self.stats.cache_size = len(self._cache)
            
            # Check for similar queries (semantic similarity)
            for stored_key, entry in self._cache.items():
                if entry.is_expired(self.ttl_seconds):
                    continue
                
                # Extract original query from metadata if available
                original_query = entry.metadata.get('original_query', '')
                if original_query:
                    similarity = self._compute_query_similarity(query, original_query)
                    
                    if similarity >= self.similarity_threshold:
                        # Similar query found
                        entry.hit_count += 1
                        entry.last_accessed = datetime.now()
                        
                        # Update stats
                        hit_time = time.time() - start_time
                        self._hit_times.append(hit_time)
                        if len(self._hit_times) > 100:
                            self._hit_times.pop(0)
                        
                        self.stats.cache_hits += 1
                        self.stats.avg_hit_response_time = sum(self._hit_times) / len(self._hit_times)
                        
                        logger.debug(f"🔍 Similar query HIT: {similarity:.2f} similarity ({hit_time:.3f}s)")
                        return entry.response, entry
            
            # Cache miss
            miss_time = time.time() - start_time
            self._miss_times.append(miss_time)
            if len(self._miss_times) > 100:
                self._miss_times.pop(0)
            
            self.stats.cache_misses += 1
            if self._miss_times:
                self.stats.avg_miss_response_time = sum(self._miss_times) / len(self._miss_times)
            
            logger.debug(f"❌ Cache MISS: {query[:50]}...")
            return None
    
    async def set(self, 
                  query: str, 
                  response: str,
                  context: str = "",
                  response_time: float = 0.0,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store response in cache
        
        Args:
            query: Original query
            response: Generated response
            context: Context used for generation
            response_time: Time taken to generate response
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        # Start cleanup task if not already started
        if not self._cleanup_started:
            self._start_cleanup_task()
            
        if not response or len(response.strip()) == 0:
            return False
        
        async with self._lock:
            cache_key = self._generate_cache_key(query, context)
            
            # Create cache entry
            entry = CacheEntry(
                response=response,
                timestamp=datetime.now(),
                hit_count=0,
                last_accessed=datetime.now(),
                query_hash=cache_key,
                context_hash=hashlib.md5(context.encode('utf-8')).hexdigest(),
                response_time=response_time,
                metadata={
                    'original_query': query,
                    'context_length': len(context),
                    **(metadata or {})
                }
            )
            
            # Check cache size and evict if necessary
            if len(self._cache) >= self.max_size:
                await self._evict_lru()
            
            # Store entry
            self._cache[cache_key] = entry
            self.stats.cache_size = len(self._cache)
            
            logger.debug(f"💾 Cached response: {query[:50]}... (size: {len(self._cache)})")
            return True
    
    async def _evict_lru(self):
        """Evict least recently used cache entries"""
        if not self._cache:
            return
        
        # Find LRU entries (bottom 10%)
        entries = list(self._cache.items())
        entries.sort(key=lambda x: x[1].last_accessed)
        
        evict_count = max(1, len(entries) // 10)  # Evict 10%
        
        for i in range(evict_count):
            key, entry = entries[i]
            del self._cache[key]
            logger.debug(f"🗑️ Evicted LRU entry: {entry.metadata.get('original_query', 'unknown')[:30]}...")
    
    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        async with self._lock:
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_expired(self.ttl_seconds):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self.stats.cache_size = len(self._cache)
                logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self.stats.cache_size = 0
            logger.info("🗑️ Cache cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "cache_config": {
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "similarity_threshold": self.similarity_threshold
            },
            "performance": {
                "total_requests": self.stats.total_requests,
                "cache_hits": self.stats.cache_hits,
                "cache_misses": self.stats.cache_misses,
                "hit_rate": self.stats.hit_rate,
                "current_size": self.stats.cache_size,
                "avg_hit_response_time": self.stats.avg_hit_response_time,
                "avg_miss_response_time": self.stats.avg_miss_response_time,
                "estimated_time_saved": self.stats.time_saved
            },
            "cache_health": {
                "size_utilization": (self.stats.cache_size / self.max_size) * 100,
                "cleanup_task_running": self._cleanup_task and not self._cleanup_task.done()
            }
        }
    
    async def get_cache_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cache entries for debugging/monitoring"""
        async with self._lock:
            entries = []
            
            # Get most frequently used entries
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].hit_count,
                reverse=True
            )
            
            for key, entry in sorted_entries[:limit]:
                entries.append({
                    "query": entry.metadata.get('original_query', 'unknown')[:100],
                    "hit_count": entry.hit_count,
                    "timestamp": entry.timestamp.isoformat(),
                    "last_accessed": entry.last_accessed.isoformat(),
                    "response_time": entry.response_time,
                    "is_expired": entry.is_expired(self.ttl_seconds)
                })
            
            return entries
    
    def cleanup_task_shutdown(self):
        """Shutdown cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

# Global cache instance
response_cache = ResponseCache(
    max_size=1000,
    ttl_seconds=3600,  # 1 hour
    similarity_threshold=0.95
)