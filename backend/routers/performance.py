"""
Performance API Router
Real-time performance metrics and analytics for the RAG system
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from services.performance_monitor import performance_monitor
from services.ai_response_cache import get_ai_cache_stats
from services.rag.unified_rag_service import get_unified_rag_service
from services.qdrant_rag_service import get_rag_service
from services.advanced_cache_system import get_advanced_cache
from services.rag_metrics_service import get_rag_metrics_service
from models.rag_metrics import LiveMetricsResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/performance",
    tags=["performance"],
    responses={404: {"description": "Not found"}},
)

@router.get("/metrics/realtime")
async def get_realtime_metrics() -> Dict[str, Any]:
    """
    Get real-time performance metrics for RAG system

    Returns:
        Real-time performance statistics including response times,
        cache hit rates, and component-specific metrics
    """
    try:
        # Get performance monitor stats
        performance_stats = performance_monitor.get_realtime_stats()

        # Get cache statistics
        cache_stats = get_ai_cache_stats()

        # Get advanced cache statistics
        advanced_cache = await get_advanced_cache()
        advanced_cache_stats = advanced_cache.get_statistics()

        # Get RAG service health
        unified_rag = await get_unified_rag_service()
        rag_health = await unified_rag.health_check()
        rag_performance = await unified_rag.get_performance_metrics()

        # Get base RAG service health
        base_rag = await get_rag_service()
        base_health = await base_rag.health_check()

        # Get enhanced RAG metrics
        try:
            rag_metrics_service = await get_rag_metrics_service()
            rag_live_metrics = await rag_metrics_service.get_live_metrics()
            rag_enhanced_data = LiveMetricsResponse(**rag_live_metrics).dict()
        except Exception as e:
            logger.warning(f"RAG metrics service not available: {str(e)}")
            rag_enhanced_data = {
                "status": "initializing",
                "window_minutes": 15,
                "updated_at": datetime.now().isoformat(),
                "totals": {
                    "queries": 0,
                    "successful": 0,
                    "failed": 0,
                    "cache_hit_rate": 0.0,
                },
                "latency": {
                    "average_ms": 0.0,
                    "p95_ms": 0.0,
                    "p99_ms": 0.0,
                },
                "quality": {
                    "avg_relevance": 0.0,
                    "avg_sources_per_query": 0.0,
                    "unique_sources": 0,
                },
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "performance": performance_stats,
            "cache": cache_stats,
            "advanced_cache": advanced_cache_stats,
            "rag_services": {
                "unified_rag": rag_health,
                "unified_rag_performance": rag_performance,
                "base_rag": base_health
            },
            "rag_metrics": rag_enhanced_data,
            "system_status": _determine_system_status(performance_stats, cache_stats)
        }

    except Exception as e:
        logger.error(f"Failed to get realtime metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")

@router.get("/metrics/dashboard")
async def get_dashboard_metrics(
    time_window_minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes")
) -> Dict[str, Any]:
    """
    Get formatted metrics for the performance dashboard

    Args:
        time_window_minutes: Time window for metrics aggregation

    Returns:
        Dashboard-formatted performance metrics
    """
    try:
        # Get base metrics
        realtime_data = await get_realtime_metrics()
        performance_stats = realtime_data["performance"]
        rag_metrics = realtime_data.get("rag_metrics", {})

        rag_latency = rag_metrics.get("latency", {})
        rag_quality = rag_metrics.get("quality", {})
        rag_totals = rag_metrics.get("totals", {})

        # Use RAG metrics if available, otherwise fall back to performance stats
        current_response_time = rag_latency.get("average_ms", 0) or performance_stats.get("overall", {}).get("avg_response_time_ms", 0)
        source_quality_percentage = (
            rag_quality.get("avg_relevance", 0) * 100
            if rag_quality.get("avg_relevance", 0) > 0
            else _calculate_source_quality(performance_stats)
        )
        cache_hit_rate = (
            rag_totals.get("cache_hit_rate", 0) * 100
            if rag_totals.get("cache_hit_rate", 0) > 0
            else realtime_data["cache"].get("hit_rate", 0)
        )

        # Calculate dashboard-specific metrics
        dashboard_metrics = {
            "processing_time": {
                "current_ms": current_response_time,
                "target_ms": 2000,
                "status": _get_performance_status(current_response_time),
                "trend": "stable"  # TODO: Implement trend calculation
            },
            "source_quality": {
                "percentage": source_quality_percentage,
                "target_percentage": 80,
                "status": _get_quality_status(source_quality_percentage),
                "total_sources": rag_quality.get("unique_sources", _get_total_sources_count(performance_stats))
            },
            "cache_performance": {
                "hit_rate_percentage": cache_hit_rate,
                "target_percentage": 95,
                "status": _get_cache_status(cache_hit_rate),
                "total_requests": rag_totals.get("queries", realtime_data["cache"].get("total_requests", 0))
            },
            "system_health": {
                "overall_status": rag_metrics.get("status", realtime_data.get("system_status", "unknown")),
                "components": _get_component_health(performance_stats.get("components", {})),
                "bottlenecks": performance_stats.get("bottlenecks", []),
                "alerts": performance_stats.get("recent_alerts", [])
            }
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "dashboard_metrics": dashboard_metrics,
            "raw_performance_data": realtime_data
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard metrics: {str(e)}")

@router.get("/optimization/recommendations")
async def get_optimization_recommendations() -> Dict[str, Any]:
    """
    Get AI-powered optimization recommendations based on current performance

    Returns:
        Optimization recommendations and auto-tuning suggestions
    """
    try:
        # Get performance optimization analysis
        optimization_analysis = await performance_monitor.optimize_performance()

        return {
            "timestamp": datetime.now().isoformat(),
            "optimization_analysis": optimization_analysis,
            "actionable_recommendations": _format_recommendations(optimization_analysis.get("recommendations", [])),
            "priority_actions": [
                rec for rec in optimization_analysis.get("recommendations", [])
                if rec.get("priority") == "high"
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get optimization recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/cache/optimize")
async def optimize_cache() -> Dict[str, Any]:
    """
    Optimize all cache systems and return optimization results

    Returns:
        Optimization results and statistics
    """
    try:
        results = {}

        # Optimize advanced cache
        advanced_cache = await get_advanced_cache()
        advanced_optimization = await advanced_cache.optimize()
        results["advanced_cache"] = advanced_optimization

        # Optimize unified RAG cache
        unified_rag = await get_unified_rag_service()
        rag_optimization = await unified_rag.optimize_cache()
        results["rag_cache"] = rag_optimization

        # Basic cache cleanup
        cache = get_ai_cache()
        expired_cleaned = cache.cleanup_expired()
        results["basic_cache"] = {
            "expired_entries_removed": expired_cleaned,
            "stats_after": cache.get_stats()
        }

        logger.info("Cache optimization completed successfully")

        return {
            "message": "Cache optimization completed",
            "timestamp": datetime.now().isoformat(),
            "optimization_results": results
        }

    except Exception as e:
        logger.error(f"Failed to optimize cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize cache: {str(e)}")

@router.post("/cache/clear")
async def clear_cache(tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Clear cache by tags or completely

    Args:
        tags: Optional list of tags to filter cache entries

    Returns:
        Cache clearing results
    """
    try:
        results = {}

        # Clear advanced cache
        advanced_cache = await get_advanced_cache()
        if tags:
            removed_count = advanced_cache.invalidate_by_tags(tags)
            results["advanced_cache"] = {
                "removed_entries": removed_count,
                "tags": tags
            }
        else:
            advanced_cache.clear_all()
            results["advanced_cache"] = {
                "message": "All advanced cache levels cleared"
            }

        # Clear unified RAG cache
        unified_rag = await get_unified_rag_service()
        rag_clear_result = await unified_rag.clear_cache(tags)
        results["rag_cache"] = rag_clear_result

        # Clear basic cache if no tags specified
        if not tags:
            cache = get_ai_cache()
            cache.clear()
            results["basic_cache"] = {"message": "Basic cache cleared"}

        logger.info(f"Cache cleared successfully (tags: {tags})")

        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat(),
            "clear_results": results
        }

    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/cache/statistics")
async def get_cache_statistics() -> Dict[str, Any]:
    """
    Get detailed cache statistics across all cache systems

    Returns:
        Comprehensive cache statistics
    """
    try:
        # Advanced cache stats
        advanced_cache = await get_advanced_cache()
        advanced_stats = advanced_cache.get_statistics()

        # Basic cache stats
        basic_cache = get_ai_cache()
        basic_stats = basic_cache.get_stats()

        # RAG service cache stats
        unified_rag = await get_unified_rag_service()
        rag_performance = await unified_rag.get_performance_metrics()

        return {
            "timestamp": datetime.now().isoformat(),
            "advanced_cache": advanced_stats,
            "basic_cache": basic_stats,
            "rag_cache": rag_performance.get("advanced_cache", {}),
            "summary": {
                "total_cache_hit_rate": _calculate_overall_hit_rate(advanced_stats, basic_stats),
                "total_memory_usage_mb": _calculate_total_memory_usage(advanced_stats, basic_stats),
                "cache_health": _assess_cache_health(advanced_stats, basic_stats)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get cache statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cache statistics: {str(e)}")

@router.get("/metrics/rag-unified")
async def get_unified_rag_metrics() -> Dict[str, Any]:
    """
    Get unified RAG metrics compatible with both RAGMetrics and EnhancedRAGMetrics components

    Returns:
        Unified metrics format that works with both frontend systems
    """
    try:
        # Get realtime data
        realtime_data = await get_realtime_metrics()
        rag_metrics = realtime_data.get("rag_metrics", {})

        unified_response = {
            "timestamp": datetime.now().isoformat(),
            "live_metrics": rag_metrics,
            "performance": realtime_data.get("performance", {}),
            "cache": realtime_data.get("cache", {}),
            "rag_services": realtime_data.get("rag_services", {}),
            "system_status": realtime_data.get("system_status", "unknown"),
            "is_connected": rag_metrics.get("status") in {"ok", "degraded"},
            "last_activity": datetime.now().isoformat(),
        }

        logger.info(
            "Unified RAG metrics served - status %s",
            rag_metrics.get("status", "unknown"),
        )
        return unified_response

    except Exception as e:
        logger.error(f"❌ Failed to get unified RAG metrics: {str(e)}")
        # Return empty but valid structure
        return {
            "timestamp": datetime.now().isoformat(),
            "live_metrics": {
                "status": "error",
                "window_minutes": 15,
                "updated_at": datetime.now().isoformat(),
                "totals": {
                    "queries": 0,
                    "successful": 0,
                    "failed": 0,
                    "cache_hit_rate": 0.0,
                },
                "latency": {
                    "average_ms": 0.0,
                    "p95_ms": 0.0,
                    "p99_ms": 0.0,
                },
                "quality": {
                    "avg_relevance": 0.0,
                    "avg_sources_per_query": 0.0,
                    "unique_sources": 0,
                },
            },
            "performance": {"status": "no_data"},
            "cache": {"hit_rate": 0, "hits": 0, "misses": 0},
            "rag_services": {},
            "system_status": "error",
            "is_connected": False,
            "last_activity": datetime.now().isoformat(),
            "error": str(e),
        }

@router.post("/reset-stats")
async def reset_performance_stats() -> Dict[str, str]:
    """
    Reset all performance statistics (admin operation)

    Returns:
        Confirmation message
    """
    try:
        performance_monitor.reset_stats()

        # Clear all caches
        advanced_cache = await get_advanced_cache()
        advanced_cache.clear_all()

        cache = get_ai_cache()
        cache.clear()

        # Reset RAG cache
        unified_rag = await get_unified_rag_service()
        await unified_rag.clear_cache()

        logger.info("Performance statistics and all caches reset by admin request")

        return {
            "message": "Performance statistics and all caches reset successfully",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to reset performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset stats: {str(e)}")

# Helper functions

def _determine_system_status(performance_stats: Dict, cache_stats: Dict) -> str:
    """Determine overall system health status"""
    if performance_stats.get("status") == "no_data":
        return "initializing"

    overall_perf = performance_stats.get("overall", {})
    avg_response_time = overall_perf.get("avg_response_time_ms", 0)
    cache_hit_rate = cache_stats.get("hit_rate", 0)

    if avg_response_time > 5000 or cache_hit_rate < 50:
        return "degraded"
    elif avg_response_time > 2000 or cache_hit_rate < 80:
        return "acceptable"
    else:
        return "excellent"

def _get_performance_status(response_time_ms: float) -> str:
    """Get performance status based on response time"""
    if response_time_ms < 1000:
        return "excellent"
    elif response_time_ms < 2000:
        return "good"
    elif response_time_ms < 5000:
        return "acceptable"
    else:
        return "poor"

def _get_cache_status(hit_rate: float) -> str:
    """Get cache status based on hit rate"""
    if hit_rate >= 95:
        return "excellent"
    elif hit_rate >= 85:
        return "good"
    elif hit_rate >= 70:
        return "acceptable"
    else:
        return "poor"

def _get_quality_status(quality_percentage: float) -> str:
    """Get quality status based on source quality percentage"""
    if quality_percentage >= 85:
        return "excellent"
    elif quality_percentage >= 75:
        return "good"
    elif quality_percentage >= 60:
        return "acceptable"
    else:
        return "poor"

def _calculate_source_quality(performance_stats: Dict) -> float:
    """Calculate overall source quality percentage"""
    # TODO: Implement actual source quality calculation based on relevance scores
    # For now, return a reasonable default based on system health
    if performance_stats.get("status") == "no_data":
        return 0.0

    overall_perf = performance_stats.get("overall", {})
    if overall_perf.get("performance_status") == "excellent":
        return 85.0
    elif overall_perf.get("performance_status") == "acceptable":
        return 70.0
    else:
        return 60.0

def _get_total_sources_count(performance_stats: Dict) -> int:
    """Get total number of sources processed"""
    # TODO: Implement actual source counting
    return performance_stats.get("overall", {}).get("total_queries", 0) * 5

def _get_component_health(components: Dict) -> Dict[str, str]:
    """Get health status for each component"""
    component_health = {}

    for component, stats in components.items():
        avg_ms = stats.get("avg_ms", 0)
        error_rate = stats.get("error_rate", 0)

        if error_rate > 10:
            component_health[component] = "unhealthy"
        elif avg_ms > 1000:
            component_health[component] = "slow"
        else:
            component_health[component] = "healthy"

    return component_health

def _format_recommendations(recommendations: list) -> list:
    """Format recommendations for better display"""
    formatted = []

    for rec in recommendations:
        formatted.append({
            "title": rec.get("description", ""),
            "priority": rec.get("priority", "medium"),
            "component": rec.get("component", "system"),
            "action": rec.get("action", ""),
            "implementation": rec.get("implementation", ""),
            "type": rec.get("type", "optimization")
        })

    return formatted

def _calculate_overall_hit_rate(advanced_stats: Dict, basic_stats: Dict) -> float:
    """Calculate overall cache hit rate across all cache systems"""
    try:
        # Advanced cache hit rate
        advanced_hit_rate = advanced_stats.get("performance", {}).get("overall_hit_rate", 0)

        # Basic cache hit rate
        basic_hit_rate = basic_stats.get("hit_rate", 0) * 100

        # Weight by total requests
        advanced_requests = advanced_stats.get("performance", {}).get("total_requests", 0)
        basic_requests = basic_stats.get("total_requests", 0)

        total_requests = advanced_requests + basic_requests
        if total_requests == 0:
            return 0.0

        # Weighted average
        weighted_hit_rate = (
            (advanced_hit_rate * advanced_requests) +
            (basic_hit_rate * basic_requests)
        ) / total_requests

        return round(weighted_hit_rate, 2)
    except Exception:
        return 0.0

def _calculate_total_memory_usage(advanced_stats: Dict, basic_stats: Dict) -> float:
    """Calculate total memory usage across all cache systems"""
    try:
        advanced_memory = advanced_stats.get("memory", {}).get("total_memory_kb", 0)
        basic_memory = basic_stats.get("memory_usage_mb", 0) * 1024  # Convert MB to KB

        total_memory_kb = advanced_memory + basic_memory
        return round(total_memory_kb / 1024, 2)  # Return as MB
    except Exception:
        return 0.0

def _assess_cache_health(advanced_stats: Dict, basic_stats: Dict) -> str:
    """Assess overall cache system health"""
    try:
        overall_hit_rate = _calculate_overall_hit_rate(advanced_stats, basic_stats)
        total_memory_mb = _calculate_total_memory_usage(advanced_stats, basic_stats)

        # Health criteria
        if overall_hit_rate >= 90 and total_memory_mb < 100:
            return "excellent"
        elif overall_hit_rate >= 80 and total_memory_mb < 200:
            return "good"
        elif overall_hit_rate >= 60 and total_memory_mb < 500:
            return "acceptable"
        else:
            return "needs_optimization"
    except Exception:
        return "unknown"
