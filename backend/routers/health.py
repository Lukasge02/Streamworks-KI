"""
Comprehensive Health Check Router
Provides detailed health status for all system components
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging

from services.service_initializer import get_service_health
from database import check_database_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def comprehensive_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for all system components
    Returns detailed status for database, services, and overall system health
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Check database health
        db_health = await check_database_health()
        
        # Check service health
        services_health = get_service_health()
        
        # Determine overall system status
        db_healthy = db_health.get("status") == "healthy"
        services_healthy = services_health.get("status") == "healthy"
        
        overall_status = "healthy" if (db_healthy and services_healthy) else "degraded"
        
        # If any critical component is unhealthy, mark as unhealthy
        if not db_healthy:
            overall_status = "unhealthy"
        
        # Detailed component status
        components = {
            "database": db_health,
            "services": services_health,
            "overall_status": overall_status,
            "timestamp": timestamp
        }
        
        # Add service-specific details
        if services_health.get("services"):
            components["service_details"] = services_health["services"]
        
        return components
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/simple")
async def simple_health_check() -> Dict[str, str]:
    """
    Simple health check for load balancers and monitoring
    Returns minimal status information
    """
    try:
        # Quick database check
        db_health = await check_database_health()
        
        if db_health.get("status") == "healthy":
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Simple health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - indicates if the system is ready to serve traffic
    More thorough than the simple health check
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Check database
        db_health = await check_database_health()
        db_ready = db_health.get("status") == "healthy"
        
        # Check services
        services_health = get_service_health()
        services_ready = services_health.get("status") == "healthy"
        
        # Additional readiness checks
        ready_checks = {
            "database": db_ready,
            "services": services_ready,
            "all_ready": db_ready and services_ready
        }
        
        overall_ready = db_ready and services_ready
        
        return {
            "ready": overall_ready,
            "checks": ready_checks,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check - indicates if the application is running
    Should return quickly with minimal processing
    """
    return {
        "alive": "true",
        "timestamp": datetime.utcnow().isoformat()
    }