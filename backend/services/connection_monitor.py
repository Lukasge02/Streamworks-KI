"""
Connection Pool Monitoring and Health Checks
Enterprise-grade database connection management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import Pool
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ConnectionPoolMonitor:
    """Monitor connection pool health and performance metrics"""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.metrics = {
            'pool_size': 0,
            'checked_in': 0,
            'checked_out': 0,
            'overflow': 0,
            'total_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'connection_errors': 0,
            'last_error': None,
            'uptime_start': datetime.utcnow()
        }
        self._monitoring = False
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status"""
        try:
            pool: Pool = self.engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'total_connections': pool.checkedin() + pool.checkedout(),
                'pool_utilization': (pool.checkedout() / (pool.size() + pool.overflow())) * 100,
                'health_status': self._get_health_status(pool),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get pool status: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def _get_health_status(self, pool: Pool) -> str:
        """Determine pool health status"""
        utilization = pool.checkedout() / (pool.size() + pool.overflow())
        
        if utilization > 0.9:
            return 'critical'
        elif utilization > 0.7:
            return 'warning'
        elif utilization > 0.5:
            return 'good'
        else:
            return 'excellent'
    
    async def start_monitoring(self, interval: int = 60):
        """Start background pool monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        logger.info("Starting connection pool monitoring")
        
        while self._monitoring:
            try:
                status = self.get_pool_status()
                
                # Log warnings for high utilization
                if 'pool_utilization' in status and status['pool_utilization'] > 80:
                    logger.warning(f"High pool utilization: {status['pool_utilization']:.1f}%")
                
                # Log metrics for monitoring systems
                logger.info(f"Pool metrics: {status}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in pool monitoring: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        logger.info("Stopping connection pool monitoring")

class OptimizedConnectionManager:
    """Optimized connection management with health checks and failover"""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.monitor = ConnectionPoolMonitor(engine)
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = datetime.utcnow()
        
    @asynccontextmanager
    async def get_session(self):
        """Get database session with connection health verification"""
        from database_supabase import AsyncSessionLocal
        
        # Periodic health check
        if datetime.utcnow() - self._last_health_check > timedelta(seconds=self._health_check_interval):
            await self._health_check()
            self._last_health_check = datetime.utcnow()
        
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
    
    async def _health_check(self):
        """Perform connection pool health check"""
        try:
            async with self.get_session() as session:
                # Simple query to verify connection
                await session.execute("SELECT 1")
                logger.debug("Database health check passed")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            await self._handle_connection_failure(e)
    
    async def _handle_connection_failure(self, error: Exception):
        """Handle connection failures with recovery strategies"""
        logger.warning(f"Handling connection failure: {error}")
        
        # Strategy 1: Close all idle connections
        try:
            self.engine.dispose()
            logger.info("Disposed engine connections for recovery")
        except Exception as e:
            logger.error(f"Failed to dispose connections: {e}")
        
        # Strategy 2: Wait and retry
        await asyncio.sleep(5)
        
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            logger.info("Connection recovery successful")
        except Exception as e:
            logger.error(f"Connection recovery failed: {e}")
            # Could implement additional fallback strategies here
    
    def get_connection_metrics(self) -> Dict[str, Any]:
        """Get detailed connection metrics for monitoring"""
        pool_status = self.monitor.get_pool_status()
        
        return {
            'pool_status': pool_status,
            'health_metrics': {
                'last_health_check': self._last_health_check.isoformat(),
                'health_check_interval': self._health_check_interval,
                'engine_disposed': self.engine.pool.disposed if hasattr(self.engine.pool, 'disposed') else False
            },
            'recommendations': self._generate_recommendations(pool_status)
        }
    
    def _generate_recommendations(self, pool_status: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if 'pool_utilization' in pool_status:
            utilization = pool_status['pool_utilization']
            
            if utilization > 90:
                recommendations.append("Consider increasing pool_size or max_overflow")
            elif utilization < 10:
                recommendations.append("Pool may be oversized - consider reducing pool_size")
            
        if 'health_status' in pool_status:
            if pool_status['health_status'] in ['warning', 'critical']:
                recommendations.append("Monitor database performance and consider scaling")
        
        return recommendations

# Global connection manager instance
_connection_manager: Optional[OptimizedConnectionManager] = None

def get_connection_manager() -> OptimizedConnectionManager:
    """Get singleton connection manager"""
    global _connection_manager
    if not _connection_manager:
        from database_supabase import async_engine
        _connection_manager = OptimizedConnectionManager(async_engine)
    return _connection_manager

async def start_connection_monitoring():
    """Start connection pool monitoring"""
    manager = get_connection_manager()
    await manager.monitor.start_monitoring()

def stop_connection_monitoring():
    """Stop connection pool monitoring"""
    if _connection_manager:
        _connection_manager.monitor.stop_monitoring()