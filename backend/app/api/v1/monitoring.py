"""
Monitoring API Endpoints for StreamWorks-KI
Provides comprehensive monitoring, metrics, and health check endpoints
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

# Legacy production monitoring removed - keeping endpoint for backward compatibility
# from app.middleware.production_monitoring import (
#     get_monitoring_summary,
#     get_prometheus_metrics as get_prometheus_metrics_service,
#     monitoring_middleware
# )
from app.core.async_manager import task_manager
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    checks: Dict[str, Any] = Field(..., description="Individual health checks")


class MetricsSummaryResponse(BaseModel):
    """Metrics summary response model"""
    overview: Dict[str, Any] = Field(..., description="Overview metrics")
    endpoints: Dict[str, Any] = Field(..., description="Endpoint-specific metrics")
    system: Optional[Dict[str, Any]] = Field(None, description="System metrics")
    timestamp: datetime = Field(..., description="Metrics timestamp")


class SystemStatusResponse(BaseModel):
    """System status response model"""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_mb: float = Field(..., description="Memory usage in MB")
    disk_usage_percent: float = Field(..., description="Disk usage percentage")
    active_connections: int = Field(..., description="Active network connections")
    task_manager_stats: Dict[str, Any] = Field(..., description="Task manager statistics")
    timestamp: datetime = Field(..., description="Status timestamp")


class AlertsResponse(BaseModel):
    """Alerts response model"""
    active_alerts: List[Dict[str, Any]] = Field(..., description="Currently active alerts")
    alert_history: List[Dict[str, Any]] = Field(..., description="Recent alert history")
    alert_thresholds: Dict[str, float] = Field(..., description="Current alert thresholds")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    🏥 Comprehensive health check endpoint
    
    Checks all critical system components and returns detailed status
    """
    start_time = datetime.now(timezone.utc)
    checks = {}
    overall_status = "healthy"
    
    # Database health check
    try:
        from app.models.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "details": "Connection successful"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "details": str(e)}
        overall_status = "degraded"
    
    # Task manager health check
    try:
        if task_manager._running:
            stats = task_manager.get_stats()
            checks["task_manager"] = {
                "status": "healthy",
                "details": f"Running with {stats['current_tasks']} active tasks"
            }
        else:
            checks["task_manager"] = {"status": "unhealthy", "details": "Not running"}
            overall_status = "degraded"
    except Exception as e:
        checks["task_manager"] = {"status": "unhealthy", "details": str(e)}
        overall_status = "degraded"
    
    # RAG service health check
    try:
        from app.services.rag_service import rag_service
        if rag_service.is_initialized:
            # Test basic functionality
            test_docs = await rag_service.search_documents("test", top_k=1)
            checks["rag_service"] = {
                "status": "healthy",
                "details": f"Initialized and responsive"
            }
        else:
            checks["rag_service"] = {"status": "degraded", "details": "Not initialized"}
            overall_status = "degraded"
    except Exception as e:
        checks["rag_service"] = {"status": "unhealthy", "details": str(e)}
        overall_status = "degraded"
    
    # LLM service health check
    try:
        from app.services.mistral_llm_service import mistral_llm_service
        if mistral_llm_service.is_initialized:
            checks["llm_service"] = {
                "status": "healthy",
                "details": "Initialized and ready"
            }
        else:
            checks["llm_service"] = {"status": "degraded", "details": "Not initialized"}
            overall_status = "degraded"
    except Exception as e:
        checks["llm_service"] = {"status": "unhealthy", "details": str(e)}
        overall_status = "degraded"
    
    # File system health check
    try:
        import os
        from pathlib import Path
        
        # Check training data directory
        training_path = Path(settings.TRAINING_DATA_PATH)
        if training_path.exists() and os.access(training_path, os.R_OK | os.W_OK):
            checks["filesystem"] = {
                "status": "healthy",
                "details": "Training data directory accessible"
            }
        else:
            checks["filesystem"] = {"status": "unhealthy", "details": "Training data directory not accessible"}
            overall_status = "degraded"
    except Exception as e:
        checks["filesystem"] = {"status": "unhealthy", "details": str(e)}
        overall_status = "degraded"
    
    # System resources check
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check if resources are under stress
        resource_status = "healthy"
        details = []
        
        if cpu_percent > 90:
            resource_status = "stressed"
            details.append(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > 90:
            resource_status = "stressed"
            details.append(f"High memory usage: {memory.percent}%")
        
        if disk.percent > 95:
            resource_status = "stressed"
            details.append(f"High disk usage: {disk.percent}%")
        
        checks["system_resources"] = {
            "status": resource_status,
            "details": "; ".join(details) if details else "Resources within normal limits",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
        
        if resource_status == "stressed":
            overall_status = "degraded"
            
    except Exception as e:
        checks["system_resources"] = {"status": "unknown", "details": str(e)}
    
    # Calculate uptime
    uptime_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version=getattr(settings, 'VERSION', '1.0.0'),
        uptime_seconds=uptime_seconds,
        checks=checks
    )


@router.get("/health/simple")
async def simple_health_check():
    """
    ⚡ Simple health check endpoint for load balancers
    
    Returns 200 OK if the service is responding
    """
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}


@router.get("/metrics", response_model=MetricsSummaryResponse)
async def get_metrics():
    """
    📊 Get comprehensive application metrics
    
    Returns detailed performance and usage metrics
    """
    try:
        # Legacy monitoring removed - return basic metrics
        return MetricsSummaryResponse(
            overview={"status": "legacy_monitoring_removed"},
            endpoints={},
            system=None,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    📈 Get Prometheus-compatible metrics
    
    Returns metrics in Prometheus text exposition format
    """
    try:
        # Legacy monitoring removed - return basic metrics
        return "# Legacy monitoring removed\n# streamworks_ki_status 1\n"
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Prometheus metrics")


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    🖥️ Get current system status and resource usage
    
    Returns real-time system metrics and task manager status
    """
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        try:
            active_connections = len(psutil.net_connections(kind='inet'))
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            active_connections = 0
        
        # Task manager stats
        task_stats = task_manager.get_stats() if task_manager._running else {}
        
        return SystemStatusResponse(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_usage_percent=disk.percent,
            active_connections=active_connections,
            task_manager_stats=task_stats,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts():
    """
    🚨 Get current alerts and alert configuration
    
    Returns active alerts, alert history, and thresholds
    """
    try:
        # Legacy monitoring removed - return empty alerts
        active_alerts = []
        alert_history = []
        alert_thresholds = {"status": "legacy_monitoring_removed"}
        
        return AlertsResponse(
            active_alerts=active_alerts,
            alert_history=alert_history,  # TODO: Implement alert history storage
            alert_thresholds=alert_thresholds
        )
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.get("/performance/endpoints")
async def get_endpoint_performance():
    """
    🎯 Get detailed performance metrics for all endpoints
    
    Returns response times, error rates, and request counts per endpoint
    """
    try:
        # Legacy monitoring removed - return empty endpoints
        endpoints = {}
        
        return {
            "endpoints": endpoints,
            "total_endpoints": 0,
            "timestamp": datetime.now(timezone.utc),
            "status": "legacy_monitoring_removed"
        }
        
    except Exception as e:
        logger.error(f"Failed to get endpoint performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve endpoint performance")


@router.get("/performance/slowest")
async def get_slowest_endpoints(limit: int = 10):
    """
    🐌 Get slowest endpoints by average response time
    
    Returns the endpoints with highest average response times
    """
    try:
        # Legacy monitoring removed - return empty data
        return {
            "slowest_endpoints": [],
            "timestamp": datetime.now(timezone.utc),
            "status": "legacy_monitoring_removed"
        }
        
    except Exception as e:
        logger.error(f"Failed to get slowest endpoints: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve slowest endpoints")


@router.get("/performance/errors")
async def get_error_metrics():
    """
    ❌ Get error metrics and error-prone endpoints
    
    Returns endpoints with highest error rates and recent error patterns
    """
    try:
        # Legacy monitoring removed - return empty data
        return {
            "error_endpoints": [],
            "total_endpoints_with_errors": 0,
            "timestamp": datetime.now(timezone.utc),
            "status": "legacy_monitoring_removed"
        }
        
    except Exception as e:
        logger.error(f"Failed to get error metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve error metrics")


@router.post("/alerts/test")
async def test_alert_system():
    """
    🧪 Test the alert system by triggering a test alert
    
    Useful for verifying alert handlers and notification systems
    """
    try:
        # Legacy monitoring removed - return warning
        return {
            "status": "warning",
            "message": "Legacy monitoring removed - alert system not available",
            "timestamp": datetime.now(timezone.utc)
        }
            
    except Exception as e:
        logger.error(f"Failed to test alert system: {e}")
        raise HTTPException(status_code=500, detail="Failed to test alert system")


@router.post("/maintenance/gc")
async def trigger_garbage_collection(background_tasks: BackgroundTasks):
    """
    🧹 Trigger garbage collection and cleanup
    
    Forces Python garbage collection and cleanup of monitoring data
    """
    def run_gc():
        import gc
        collected = gc.collect()
        logger.info(f"Garbage collection completed: {collected} objects collected")
        return collected
    
    background_tasks.add_task(run_gc)
    
    return {
        "status": "scheduled",
        "message": "Garbage collection scheduled",
        "timestamp": datetime.now(timezone.utc)
    }


@router.get("/performance/history")
async def get_performance_history(minutes: int = 60):
    """
    📈 Get performance history for the specified time period
    
    Returns historical performance data for analysis and trending
    """
    try:
        # Legacy monitoring removed - return message
        return {
            "message": "Legacy monitoring removed - no historical data available",
            "minutes_requested": minutes,
            "timestamp": datetime.now(timezone.utc),
            "status": "legacy_monitoring_removed"
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance history")


@router.get("/debug/middleware")
async def get_middleware_debug_info():
    """
    🔍 Get debug information about the monitoring middleware
    
    Returns internal state and configuration for troubleshooting
    """
    try:
        # Legacy monitoring removed - return debug info
        return {
            "status": "legacy_monitoring_removed",
            "message": "Legacy monitoring middleware was removed during cleanup",
            "timestamp": datetime.now(timezone.utc),
            "middleware_active": False,
            "prometheus_enabled": False,
            "alert_manager_enabled": False,
            "system_monitor_enabled": False
        }
        
    except Exception as e:
        logger.error(f"Failed to get middleware debug info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve debug information")