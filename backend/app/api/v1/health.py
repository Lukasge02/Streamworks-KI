"""
Comprehensive Health Check API for StreamWorks-KI
Provides detailed health monitoring for all system components
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time
import asyncio

from app.core.config import settings
from app.models.database import db_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class HealthStatus(BaseModel):
    """Health status model"""
    status: str  # healthy, degraded, unhealthy
    component: str
    timestamp: str
    details: Dict[str, Any]
    response_time_ms: Optional[float] = None

class SystemHealthResponse(BaseModel):
    """System health response model"""
    overall_status: str
    timestamp: str
    components: List[HealthStatus]
    summary: Dict[str, Any]

class ComponentHealthChecker:
    """Comprehensive health checker for all system components"""
    
    def __init__(self):
        self.timeout_seconds = 5.0
    
    async def check_database_health(self) -> HealthStatus:
        """Check database connectivity and health"""
        start_time = time.time()
        
        try:
            health_data = await db_manager.get_health_status()
            response_time = (time.time() - start_time) * 1000
            
            if health_data.get("status") == "healthy":
                status = "healthy"
            else:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                component="database",
                timestamp=datetime.now().isoformat(),
                details=health_data,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Database health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="database",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "connection": False
                },
                response_time_ms=response_time
            )
    
    async def check_rag_service_health(self) -> HealthStatus:
        """Check RAG service health"""
        start_time = time.time()
        
        try:
            from app.services.rag_service import rag_service
            
            # Get RAG service stats
            stats = await rag_service.get_stats()
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on stats
            if stats.get("status") == "healthy":
                status = "healthy"
            elif stats.get("status") == "not_initialized":
                status = "degraded"
            else:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                component="rag_service",
                timestamp=datetime.now().isoformat(),
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ RAG service health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="rag_service",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "initialized": False
                },
                response_time_ms=response_time
            )
    
    async def check_xml_generator_health(self) -> HealthStatus:
        """Check XML generator service health"""
        start_time = time.time()
        
        try:
            from app.services.xml_generator import xml_generator
            
            # Get XML generator stats
            stats = await xml_generator.get_stats()
            response_time = (time.time() - start_time) * 1000
            
            # Determine status
            if stats.get("status") == "healthy":
                status = "healthy"
            elif stats.get("status") == "not_initialized":
                status = "degraded"
            else:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                component="xml_generator",
                timestamp=datetime.now().isoformat(),
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ XML generator health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="xml_generator",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "initialized": False
                },
                response_time_ms=response_time
            )
    
    async def check_llm_service_health(self) -> HealthStatus:
        """Check LLM service health"""
        start_time = time.time()
        
        try:
            from app.services.mistral_llm_service import mistral_llm_service
            
            # Get LLM service stats
            stats = await mistral_llm_service.get_stats()
            
            # Also do a real health check
            is_healthy = await mistral_llm_service.health_check()
            stats["health_check_passed"] = is_healthy
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on initialization and health check
            if stats.get("status") == "ready" and is_healthy:
                status = "healthy"
            elif stats.get("status") == "initializing" or (stats.get("status") == "ready" and not is_healthy):
                status = "degraded"
            else:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                component="llm_service",
                timestamp=datetime.now().isoformat(),
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ LLM service health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="llm_service",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "initialized": False
                },
                response_time_ms=response_time
            )
    
    async def check_evaluation_service_health(self) -> HealthStatus:
        """Check evaluation service health"""
        start_time = time.time()
        
        try:
            from app.services.evaluation_service import evaluation_service
            
            # Get evaluation service stats
            stats = await evaluation_service.get_current_metrics()
            response_time = (time.time() - start_time) * 1000
            
            # Evaluation service is always available
            status = "healthy"
            
            return HealthStatus(
                status=status,
                component="evaluation_service",
                timestamp=datetime.now().isoformat(),
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Evaluation service health check failed: {e}")
            
            return HealthStatus(
                status="degraded",
                component="evaluation_service",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "metrics_available": False
                },
                response_time_ms=response_time
            )
    
    async def check_error_handler_health(self) -> HealthStatus:
        """Check error handler health"""
        start_time = time.time()
        
        try:
            from app.services.error_handler import error_handler
            
            # Get error handler stats
            stats = await error_handler.get_error_statistics()
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                status="healthy",
                component="error_handler",
                timestamp=datetime.now().isoformat(),
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Error handler health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="error_handler",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e),
                    "available": False
                },
                response_time_ms=response_time
            )
    
    async def check_system_resources(self) -> HealthStatus:
        """Check system resources"""
        start_time = time.time()
        
        try:
            import psutil
            
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on resource usage
            status = "healthy"
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                component="system_resources",
                timestamp=datetime.now().isoformat(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                response_time_ms=response_time
            )
            
        except ImportError:
            # psutil not available
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                status="degraded",
                component="system_resources",
                timestamp=datetime.now().isoformat(),
                details={
                    "warning": "psutil not available, cannot monitor system resources"
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ System resources health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                component="system_resources",
                timestamp=datetime.now().isoformat(),
                details={
                    "error": str(e)
                },
                response_time_ms=response_time
            )

# Global health checker instance
health_checker = ComponentHealthChecker()

@router.get("/", response_model=SystemHealthResponse)
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        logger.info("🔍 Running comprehensive health check...")
        
        # Run all health checks concurrently
        health_checks = await asyncio.gather(
            health_checker.check_database_health(),
            health_checker.check_rag_service_health(),
            health_checker.check_xml_generator_health(),
            health_checker.check_llm_service_health(),
            health_checker.check_evaluation_service_health(),
            health_checker.check_error_handler_health(),
            health_checker.check_system_resources(),
            return_exceptions=True
        )
        
        # Process results
        components = []
        for result in health_checks:
            if isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
                components.append(HealthStatus(
                    status="unhealthy",
                    component="unknown",
                    timestamp=datetime.now().isoformat(),
                    details={"error": str(result)}
                ))
            else:
                components.append(result)
        
        # Calculate overall status
        status_counts = {"healthy": 0, "degraded": 0, "unhealthy": 0}
        for component in components:
            status_counts[component.status] = status_counts.get(component.status, 0) + 1
        
        # Determine overall status
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["degraded"] > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Calculate summary
        total_components = len(components)
        avg_response_time = sum(c.response_time_ms for c in components if c.response_time_ms) / total_components
        
        summary = {
            "total_components": total_components,
            "healthy_components": status_counts["healthy"],
            "degraded_components": status_counts["degraded"],
            "unhealthy_components": status_counts["unhealthy"],
            "average_response_time_ms": round(avg_response_time, 2),
            "environment": settings.ENV,
            "version": "2.1.0"
        }
        
        logger.info(f"🏥 Health check completed: {overall_status} ({status_counts})")
        
        return SystemHealthResponse(
            overall_status=overall_status,
            timestamp=datetime.now().isoformat(),
            components=components,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"❌ System health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/quick")
async def get_quick_health():
    """Quick health check for load balancers"""
    try:
        # Test database connectivity only
        db_health = await health_checker.check_database_health()
        
        if db_health.status == "healthy":
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.1.0"
            }
        else:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": "Database connectivity issue"
            }
            
    except Exception as e:
        logger.error(f"❌ Quick health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/component/{component_name}")
async def get_component_health(component_name: str):
    """Get health status for a specific component"""
    try:
        health_method_map = {
            "database": health_checker.check_database_health,
            "rag_service": health_checker.check_rag_service_health,
            "xml_generator": health_checker.check_xml_generator_health,
            "llm_service": health_checker.check_llm_service_health,
            "evaluation_service": health_checker.check_evaluation_service_health,
            "error_handler": health_checker.check_error_handler_health,
            "system_resources": health_checker.check_system_resources
        }
        
        if component_name not in health_method_map:
            raise HTTPException(
                status_code=404,
                detail=f"Component '{component_name}' not found. Available: {list(health_method_map.keys())}"
            )
        
        health_status = await health_method_map[component_name]()
        
        return {
            "component": component_name,
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "details": health_status.details,
            "response_time_ms": health_status.response_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Component health check failed for {component_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed for component {component_name}: {str(e)}"
        )

@router.get("/metrics")
async def get_health_metrics():
    """Get health metrics for monitoring systems"""
    try:
        # Get basic health status
        system_health = await get_system_health()
        
        # Convert to metrics format
        metrics = {
            "streamworks_system_health_status": 1 if system_health.overall_status == "healthy" else 0,
            "streamworks_healthy_components": system_health.summary["healthy_components"],
            "streamworks_degraded_components": system_health.summary["degraded_components"],
            "streamworks_unhealthy_components": system_health.summary["unhealthy_components"],
            "streamworks_average_response_time_ms": system_health.summary["average_response_time_ms"],
            "streamworks_total_components": system_health.summary["total_components"]
        }
        
        # Add component-specific metrics
        for component in system_health.components:
            component_name = component.component.replace("_", "")
            metrics[f"streamworks_{component_name}_health_status"] = 1 if component.status == "healthy" else 0
            if component.response_time_ms:
                metrics[f"streamworks_{component_name}_response_time_ms"] = component.response_time_ms
        
        return {
            "timestamp": system_health.timestamp,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"❌ Health metrics generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Metrics generation failed: {str(e)}"
        )