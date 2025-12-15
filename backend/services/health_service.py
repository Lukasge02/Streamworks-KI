"""
Health Service
Comprehensive health checks for all system dependencies.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthService:
    """
    Service for checking health of all system dependencies.
    """

    def __init__(self):
        self._qdrant_client = None
        self._minio_client = None
        self._supabase_client = None

    def set_qdrant_client(self, client):
        """Set Qdrant client for health checks"""
        self._qdrant_client = client

    def set_minio_client(self, client):
        """Set MinIO client for health checks"""
        self._minio_client = client

    def set_supabase_client(self, client):
        """Set Supabase client for health checks"""
        self._supabase_client = client

    def _check_qdrant(self) -> ComponentHealth:
        """Check Qdrant vector database connectivity"""
        if not self._qdrant_client:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY, message="Qdrant client not configured"
            )

        try:
            start = time.time()
            # Try to get collections list as health check
            self._qdrant_client.get_collections()
            latency = (time.time() - start) * 1000

            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=round(latency, 2),
                message="Connected",
            )
        except Exception as e:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY, message=f"Connection failed: {str(e)}"
            )

    def _check_minio(self) -> ComponentHealth:
        """Check MinIO object storage connectivity"""
        if not self._minio_client:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY, message="MinIO client not configured"
            )

        try:
            start = time.time()
            # Try to list buckets as health check
            self._minio_client.list_buckets()
            latency = (time.time() - start) * 1000

            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=round(latency, 2),
                message="Connected",
            )
        except Exception as e:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY, message=f"Connection failed: {str(e)}"
            )

    def _check_supabase(self) -> ComponentHealth:
        """Check Supabase database connectivity"""
        if not self._supabase_client:
            return ComponentHealth(
                status=HealthStatus.DEGRADED, message="Supabase client not configured"
            )

        try:
            start = time.time()
            # Simple query to check connectivity
            self._supabase_client.table("sessions").select("id").limit(1).execute()
            latency = (time.time() - start) * 1000

            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=round(latency, 2),
                message="Connected",
            )
        except Exception as e:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY, message=f"Connection failed: {str(e)}"
            )

    def check_all(self) -> Dict[str, Any]:
        """
        Check health of all components and return detailed status.

        Returns:
            Dict with overall status and per-component health info
        """
        qdrant_health = self._check_qdrant()
        minio_health = self._check_minio()
        supabase_health = self._check_supabase()

        components = {
            "qdrant": {
                "status": qdrant_health.status.value,
                "latency_ms": qdrant_health.latency_ms,
                "message": qdrant_health.message,
            },
            "minio": {
                "status": minio_health.status.value,
                "latency_ms": minio_health.latency_ms,
                "message": minio_health.message,
            },
            "supabase": {
                "status": supabase_health.status.value,
                "latency_ms": supabase_health.latency_ms,
                "message": supabase_health.message,
            },
        }

        # Determine overall status
        statuses = [qdrant_health.status, minio_health.status, supabase_health.status]

        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": components,
        }

    def quick_check(self) -> Dict[str, str]:
        """
        Quick health check - just returns status without checking dependencies.
        Used for load balancer health checks.
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Singleton instance
health_service = HealthService()
