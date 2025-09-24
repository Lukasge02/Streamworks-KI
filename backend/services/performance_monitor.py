"""
Advanced Performance Monitoring Service for Streamworks RAG
Real-time metrics, bottleneck detection, and auto-optimization
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import statistics
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    component: str  # embedding, vectorsearch, llm, cache, etc.
    operation: str
    duration_ms: float
    cache_hit: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class PerformanceMonitor:
    """
    Advanced performance monitoring with:
    - Real-time bottleneck detection
    - Cache effectiveness tracking
    - Response time optimization alerts
    - Component-level performance analysis
    """
    
    def __init__(self, target_response_time: float = 1.5, target_cache_hit_rate: float = 92.0):
        self.target_response_time = target_response_time
        self.target_cache_hit_rate = target_cache_hit_rate
        
        # Rolling window for real-time metrics
        self.metrics_window = deque(maxlen=1000)
        self.component_metrics = defaultdict(lambda: deque(maxlen=500))
        
        # Performance targets and alerts
        self.performance_alerts = []
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes
        
        # Cache statistics
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "hit_rate": 0.0
        }
        
        # Component benchmarks
        self.component_benchmarks = {
            "embedding": 200,      # ms
            "vectorsearch": 100,   # ms  
            "llm_generation": 800, # ms
            "cache_get": 5,        # ms
            "cache_set": 10        # ms
        }

    async def record_metric(self, 
                           component: str,
                           operation: str, 
                           duration_ms: float,
                           cache_hit: bool = False,
                           error: Optional[str] = None,
                           metadata: Optional[Dict] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            component=component,
            operation=operation,
            duration_ms=duration_ms,
            cache_hit=cache_hit,
            error=error,
            metadata=metadata or {}
        )
        
        self.metrics_window.append(metric)
        self.component_metrics[component].append(metric)
        
        # Update cache stats
        if component == "cache":
            if cache_hit:
                self.cache_stats["hits"] += 1
            else:
                self.cache_stats["misses"] += 1
            self.cache_stats["total_queries"] += 1
            
            if self.cache_stats["total_queries"] > 0:
                self.cache_stats["hit_rate"] = (
                    self.cache_stats["hits"] / self.cache_stats["total_queries"] * 100
                )
        
        # Check for performance issues
        await self._check_performance_alerts(metric)

    async def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance issues and generate alerts"""
        now = datetime.now()
        alert_key = f"{metric.component}_{metric.operation}"
        
        # Avoid spam alerts
        if alert_key in self.last_alert_time:
            if (now - self.last_alert_time[alert_key]).seconds < self.alert_cooldown:
                return
        
        # Check component-specific performance
        benchmark = self.component_benchmarks.get(metric.component)
        if benchmark and metric.duration_ms > benchmark * 2:  # 2x slower than benchmark
            alert = {
                "timestamp": now,
                "type": "performance_degradation",
                "component": metric.component,
                "operation": metric.operation,
                "actual_ms": metric.duration_ms,
                "benchmark_ms": benchmark,
                "severity": "warning"
            }
            self.performance_alerts.append(alert)
            self.last_alert_time[alert_key] = now
            logger.warning(f"Performance degradation detected: {metric.component} took {metric.duration_ms:.2f}ms (benchmark: {benchmark}ms)")

    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        if not self.metrics_window:
            return {"status": "no_data"}
        
        # Recent metrics (last 5 minutes)
        cutoff = datetime.now() - timedelta(minutes=5)
        recent_metrics = [m for m in self.metrics_window if m.timestamp > cutoff]
        
        if not recent_metrics:
            return {"status": "no_recent_data"}
        
        # Overall performance
        durations = [m.duration_ms for m in recent_metrics if not m.error]
        avg_response_time = statistics.mean(durations) if durations else 0
        p95_response_time = statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else 0
        
        # Component breakdown
        component_stats = {}
        for component, metrics in self.component_metrics.items():
            recent_component = [m for m in metrics if m.timestamp > cutoff and not m.error]
            if recent_component:
                component_durations = [m.duration_ms for m in recent_component]
                component_stats[component] = {
                    "avg_ms": statistics.mean(component_durations),
                    "p95_ms": statistics.quantiles(component_durations, n=20)[18] if len(component_durations) > 20 else 0,
                    "count": len(recent_component),
                    "error_rate": sum(1 for m in metrics if m.error and m.timestamp > cutoff) / len(recent_component) * 100
                }
        
        # Performance assessment
        performance_status = "excellent"
        if avg_response_time > self.target_response_time * 1000:
            performance_status = "degraded"
        elif avg_response_time > self.target_response_time * 800:
            performance_status = "acceptable"
        
        cache_status = "excellent"
        if self.cache_stats["hit_rate"] < self.target_cache_hit_rate:
            cache_status = "needs_improvement"
        elif self.cache_stats["hit_rate"] < self.target_cache_hit_rate * 1.1:
            cache_status = "good"
        
        return {
            "status": "active",
            "overall": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "p95_response_time_ms": round(p95_response_time, 2),
                "target_response_time_ms": self.target_response_time * 1000,
                "performance_status": performance_status,
                "total_queries": len(recent_metrics)
            },
            "cache": {
                "hit_rate_percent": round(self.cache_stats["hit_rate"], 1),
                "target_hit_rate_percent": self.target_cache_hit_rate,
                "cache_status": cache_status,
                "total_hits": self.cache_stats["hits"],
                "total_misses": self.cache_stats["misses"]
            },
            "components": component_stats,
            "bottlenecks": self._identify_bottlenecks(),
            "recent_alerts": self.performance_alerts[-5:],  # Last 5 alerts
            "timestamp": datetime.now().isoformat()
        }

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify current performance bottlenecks"""
        bottlenecks = []
        
        for component, metrics in self.component_metrics.items():
            if not metrics:
                continue
                
            recent = [m for m in metrics if (datetime.now() - m.timestamp).seconds < 300]
            if not recent:
                continue
            
            avg_duration = statistics.mean([m.duration_ms for m in recent if not m.error])
            benchmark = self.component_benchmarks.get(component)
            
            if benchmark and avg_duration > benchmark * 1.5:
                bottlenecks.append({
                    "component": component,
                    "avg_duration_ms": round(avg_duration, 2),
                    "benchmark_ms": benchmark,
                    "slowdown_factor": round(avg_duration / benchmark, 1),
                    "impact": "high" if avg_duration > benchmark * 2 else "medium"
                })
        
        # Sort by impact
        bottlenecks.sort(key=lambda x: x["slowdown_factor"], reverse=True)
        return bottlenecks

    async def optimize_performance(self) -> Dict[str, Any]:
        """Auto-optimization recommendations based on metrics"""
        stats = self.get_realtime_stats()
        recommendations = []
        
        # Cache optimization
        if stats["cache"]["hit_rate_percent"] < self.target_cache_hit_rate:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "high",
                "action": "increase_ttl",
                "description": f"Cache hit rate is {stats['cache']['hit_rate_percent']}%, target is {self.target_cache_hit_rate}%",
                "implementation": "Increase cache TTL values in optimized_rag_pipeline.py"
            })
        
        # Component optimization
        for bottleneck in stats["bottlenecks"]:
            if bottleneck["impact"] == "high":
                recommendations.append({
                    "type": "component_optimization", 
                    "priority": "high",
                    "component": bottleneck["component"],
                    "action": "optimize_component",
                    "description": f"{bottleneck['component']} is {bottleneck['slowdown_factor']}x slower than benchmark",
                    "implementation": f"Optimize {bottleneck['component']} processing pipeline"
                })
        
        # Vector search optimization
        if "vectorsearch" in [b["component"] for b in stats["bottlenecks"]]:
            recommendations.append({
                "type": "vectorsearch_optimization",
                "priority": "medium", 
                "action": "adjust_similarity_threshold",
                "description": "Vector search performance can be improved",
                "implementation": "Lower similarity threshold or add more aggressive filtering"
            })
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "performance_status": stats["overall"]["performance_status"],
            "recommendations": recommendations,
            "auto_optimizable": len([r for r in recommendations if r["priority"] == "high"]),
            "stats_snapshot": stats
        }

    def reset_stats(self):
        """Reset all performance statistics"""
        self.metrics_window.clear()
        self.component_metrics.clear()
        self.cache_stats = {"hits": 0, "misses": 0, "total_queries": 0, "hit_rate": 0.0}
        self.performance_alerts.clear()
        self.last_alert_time.clear()
        logger.info("Performance statistics reset")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Context manager for easy metric recording
class PerformanceTracker:
    """Context manager for automatic performance tracking"""
    
    def __init__(self, component: str, operation: str, metadata: Optional[Dict] = None):
        self.component = component
        self.operation = operation
        self.metadata = metadata
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        error = str(exc_val) if exc_val else None
        
        await performance_monitor.record_metric(
            component=self.component,
            operation=self.operation,
            duration_ms=duration_ms,
            error=error,
            metadata=self.metadata
        )