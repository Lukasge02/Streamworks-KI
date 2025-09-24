"""
Enterprise Response Cache Service für Streamworks RAG MVP
Redis-basiertes Caching mit TTL und Cache-Invalidation
"""

import asyncio
import json
import hashlib
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
import logging
import pickle
import gzip
from contextlib import asynccontextmanager

from config import settings

# Optional Redis dependency
try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover - handled at runtime if redis is missing
    aioredis = None

logger = logging.getLogger(__name__)

__all__ = ['EnterpriseCacheService', 'get_cache_service', 'cache_response']

class EnterpriseCacheService:
    """Enterprise-grade Redis caching service mit compression und TTL management"""
    
    def __init__(self):
        self.redis_client = None
        self.connection_pool = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
    async def initialize(self):
        """Initialize Redis connection mit enterprise features"""
        if aioredis is None:
            logger.warning("⚠️ redis.asyncio nicht verfügbar – Enterprise Cache läuft im In-Memory-Fallback.")
            self.redis_client = None
            return

        try:
            # Redis connection pool für enterprise performance
            self.connection_pool = aioredis.ConnectionPool(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                max_connections=50,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            self.redis_client = aioredis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=False  # Keep binary for compression
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("✅ Enterprise cache service initialized with Redis")
            
            # Set up cache monitoring
            await self._setup_cache_monitoring()
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {str(e)}")
            # Fallback to in-memory cache
            self.redis_client = None
            logger.warning("⚠️ Falling back to in-memory cache")
    
    async def _setup_cache_monitoring(self):
        """Setup cache monitoring and cleanup tasks"""
        # Start background task for cache statistics
        asyncio.create_task(self._cache_stats_monitor())
        
        # Start background task for cache cleanup
        asyncio.create_task(self._cache_cleanup_task())
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate deterministic cache key from parameters"""
        # Create hash from kwargs
        content = json.dumps(kwargs, sort_keys=True, default=str)
        hash_key = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"streamworks:{prefix}:{hash_key}"
    
    def _compress_data(self, data: Any) -> bytes:
        """Smart compression based on data size for optimal performance"""
        try:
            serialized = pickle.dumps(data)
            
            # Only compress if data is larger than 1KB to avoid compression overhead
            if len(serialized) > 1024:
                compressed = gzip.compress(serialized, compresslevel=3)  # Faster compression
                return compressed
            else:
                return serialized
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return pickle.dumps(data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data from cache"""
        try:
            # Try gzip decompression first
            try:
                decompressed = gzip.decompress(compressed_data)
                return pickle.loads(decompressed)
            except gzip.BadGzipFile:
                # Fallback to direct pickle loads
                return pickle.loads(compressed_data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return None

    async def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Get cached value with enterprise performance monitoring"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key(prefix, **kwargs)
            
            # Get from Redis with pipeline for performance
            async with self.redis_client.pipeline() as pipe:
                await pipe.get(cache_key)
                await pipe.ttl(cache_key)
                results = await pipe.execute()
                
            cached_data, ttl = results[0], results[1]
            
            if cached_data is None:
                self.cache_stats["misses"] += 1
                logger.debug(f"Cache MISS for key: {cache_key}")
                return None
            
            # Check TTL
            if ttl <= 0:
                self.cache_stats["misses"] += 1
                await self._delete_key(cache_key)
                return None
            
            # Decompress and return data
            data = self._decompress_data(cached_data)
            if data is not None:
                self.cache_stats["hits"] += 1
                logger.debug(f"Cache HIT for key: {cache_key} (TTL: {ttl}s)")
                return data
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache GET error: {str(e)}")
            return None
    
    async def set(self, prefix: str, value: Any, ttl_seconds: int = 3600, **kwargs) -> bool:
        """Set cached value mit compression und TTL"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key(prefix, **kwargs)
            compressed_data = self._compress_data(value)
            
            # Set with TTL
            success = await self.redis_client.setex(
                cache_key, ttl_seconds, compressed_data
            )
            
            if success:
                self.cache_stats["sets"] += 1
                logger.debug(f"Cache SET for key: {cache_key} (TTL: {ttl_seconds}s)")
                return True
            else:
                self.cache_stats["errors"] += 1
                return False
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache SET error: {str(e)}")
            return False
    
    async def delete(self, prefix: str, **kwargs) -> bool:
        """Delete specific cache entry"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key(prefix, **kwargs)
            result = await self.redis_client.delete(cache_key)
            
            if result:
                self.cache_stats["deletes"] += 1
                logger.debug(f"Cache DELETE for key: {cache_key}")
                return True
            return False
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache DELETE error: {str(e)}")
            return False
    
    async def _delete_key(self, cache_key: str) -> bool:
        """Internal method to delete key directly"""
        try:
            return bool(await self.redis_client.delete(cache_key))
        except Exception:
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate multiple cache entries by pattern"""
        if not self.redis_client:
            return 0
            
        try:
            # Use SCAN to find matching keys
            keys_deleted = 0
            async for key in self.redis_client.scan_iter(match=f"streamworks:{pattern}*"):
                if await self.redis_client.delete(key):
                    keys_deleted += 1
            
            self.cache_stats["deletes"] += keys_deleted
            logger.info(f"Cache invalidated {keys_deleted} keys for pattern: {pattern}")
            return keys_deleted
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache pattern invalidation error: {str(e)}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        redis_info = {}
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                redis_info = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B"),
                    "used_memory_peak": info.get("used_memory_peak_human", "0B"),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                }
            except Exception as e:
                logger.error(f"Failed to get Redis info: {e}")
        
        # Calculate hit rate
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_enabled": self.redis_client is not None,
            "cache_stats": {
                **self.cache_stats,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests
            },
            "redis_info": redis_info,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cache_stats_monitor(self):
        """Background task to monitor cache performance"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                stats = await self.get_stats()
                hit_rate = stats["cache_stats"]["hit_rate_percent"]
                
                if hit_rate < 50:  # Low hit rate warning
                    logger.warning(f"Low cache hit rate: {hit_rate}%")
                elif hit_rate > 80:  # High hit rate info
                    logger.info(f"Excellent cache hit rate: {hit_rate}%")
                
                # Reset stats every hour to prevent overflow
                if stats["cache_stats"]["total_requests"] > 10000:
                    self.cache_stats = {key: 0 for key in self.cache_stats}
                    
            except Exception as e:
                logger.error(f"Cache monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _cache_cleanup_task(self):
        """Background task for cache cleanup und maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                if self.redis_client:
                    # Clean up expired keys (Redis handles this automatically, but we can monitor)
                    info = await self.redis_client.info()
                    expired_keys = info.get("expired_keys", 0)
                    
                    if expired_keys > 1000:
                        logger.info(f"Redis cleaned up {expired_keys} expired keys")
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def health_check(self) -> Dict[str, Any]:
        """Enterprise health check für cache service"""
        if not self.redis_client:
            return {
                "status": "unhealthy",
                "error": "Redis client not initialized",
                "fallback": "in-memory cache"
            }
        
        try:
            # Test Redis connection
            start_time = datetime.now()
            await self.redis_client.ping()
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Get basic info
            info = await self.redis_client.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time_ms, 2),
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_connections_received": info.get("total_connections_received"),
                "cache_stats": self.cache_stats
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "cache_stats": self.cache_stats
            }
    
    @asynccontextmanager
    async def cached_or_compute(self, prefix: str, compute_fn, ttl_seconds: int = 3600, **kwargs):
        """Context manager for cache-or-compute pattern"""
        # Try to get from cache first
        cached_result = await self.get(prefix, **kwargs)
        
        if cached_result is not None:
            yield cached_result
            return
        
        # Compute the result
        try:
            result = await compute_fn(**kwargs) if asyncio.iscoroutinefunction(compute_fn) else compute_fn(**kwargs)
            
            # Cache the result
            await self.set(prefix, result, ttl_seconds, **kwargs)
            
            yield result
            
        except Exception as e:
            logger.error(f"Cache-or-compute error: {e}")
            raise
    
    async def close(self):
        """Clean shutdown of cache service"""
        if self.connection_pool:
            await self.connection_pool.disconnect()
        logger.info("✅ Enterprise cache service closed")

# Global cache service instance
cache_service = EnterpriseCacheService()

def get_cache_service() -> EnterpriseCacheService:
    """Get the global cache service instance"""
    return cache_service

# Cache decorators für common patterns
def cache_response(prefix: str, ttl_seconds: int = 3600):
    """Decorator für caching API responses"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function args
            cache_key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": kwargs
            }
            
            # Try cache first
            cached = await cache_service.get(prefix, **cache_key_data)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_service.set(prefix, result, ttl_seconds, **cache_key_data)
            
            return result
        return wrapper
    return decorator
