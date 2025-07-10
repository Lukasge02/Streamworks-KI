"""
Production-Grade Monitoring Middleware for StreamWorks-KI
Comprehensive monitoring with metrics, alerting, and performance tracking
"""
import time
import logging
import asyncio
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json
import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import uvicorn

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    request_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    error_count: int = 0
    last_request_time: Optional[datetime] = None
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    @property
    def avg_duration(self) -> float:
        return self.total_duration / self.request_count if self.request_count > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return self.error_count / self.request_count if self.request_count > 0 else 0.0


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_mb': self.memory_mb,
            'disk_usage_percent': self.disk_usage_percent,
            'network_bytes_sent': self.network_bytes_sent,
            'network_bytes_recv': self.network_bytes_recv,
            'active_connections': self.active_connections
        }


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alert_thresholds = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'error_rate_threshold': 0.05,  # 5%
            'response_time_threshold': 5.0,  # 5 seconds
            'disk_threshold': 90.0
        }
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=5)
        self.alert_handlers: List[Callable] = []
    
    def add_alert_handler(self, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
    
    def check_and_alert(self, metric_name: str, value: float, threshold: float, context: Dict[str, Any] = None) -> None:
        """Check metric against threshold and trigger alerts"""
        if value > threshold:
            alert_key = f"{metric_name}_high"
            
            # Check cooldown
            if alert_key in self.active_alerts:
                if datetime.utcnow() - self.active_alerts[alert_key] < self.alert_cooldown:
                    return
            
            # Trigger alert
            self.active_alerts[alert_key] = datetime.utcnow()
            
            alert_data = {
                'metric': metric_name,
                'value': value,
                'threshold': threshold,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context or {}
            }
            
            logger.warning(f"🚨 ALERT: {metric_name} = {value} exceeds threshold {threshold}")
            
            # Call custom handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert_key, alert_data)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")
    
    def check_system_alerts(self, system_metrics: SystemMetrics) -> None:
        """Check system metrics for alerts"""
        self.check_and_alert('cpu_usage', system_metrics.cpu_percent, self.alert_thresholds['cpu_threshold'])
        self.check_and_alert('memory_usage', system_metrics.memory_percent, self.alert_thresholds['memory_threshold'])
        self.check_and_alert('disk_usage', system_metrics.disk_usage_percent, self.alert_thresholds['disk_threshold'])
    
    def check_performance_alerts(self, endpoint: str, metrics: PerformanceMetrics) -> None:
        """Check performance metrics for alerts"""
        context = {'endpoint': endpoint}
        
        if metrics.error_rate > self.alert_thresholds['error_rate_threshold']:
            self.check_and_alert('error_rate', metrics.error_rate, self.alert_thresholds['error_rate_threshold'], context)
        
        if metrics.avg_duration > self.alert_thresholds['response_time_threshold']:
            self.check_and_alert('response_time', metrics.avg_duration, self.alert_thresholds['response_time_threshold'], context)


class PrometheusMetrics:
    """Prometheus metrics collector"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        
        # HTTP Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.request_size = Histogram(
            'http_request_size_bytes',
            'HTTP request size',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.response_size = Histogram(
            'http_response_size_bytes',
            'HTTP response size',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.memory_total = Gauge(
            'system_memory_total_bytes',
            'Total memory in bytes',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        # Application metrics
        self.active_connections = Gauge(
            'app_active_connections',
            'Active connections',
            registry=self.registry
        )
        
        self.rag_queries = Counter(
            'rag_queries_total',
            'Total RAG queries',
            ['status'],
            registry=self.registry
        )
        
        self.rag_query_duration = Histogram(
            'rag_query_duration_seconds',
            'RAG query duration',
            registry=self.registry
        )
        
        self.llm_requests = Counter(
            'llm_requests_total',
            'Total LLM requests',
            ['model', 'status'],
            registry=self.registry
        )
        
        self.llm_request_duration = Histogram(
            'llm_request_duration_seconds',
            'LLM request duration',
            ['model'],
            registry=self.registry
        )
        
        self.file_uploads = Counter(
            'file_uploads_total',
            'Total file uploads',
            ['status'],
            registry=self.registry
        )
        
        self.file_processing_duration = Histogram(
            'file_processing_duration_seconds',
            'File processing duration',
            ['processor'],
            registry=self.registry
        )
    
    def update_system_metrics(self, system_metrics: SystemMetrics) -> None:
        """Update system metrics"""
        self.cpu_usage.set(system_metrics.cpu_percent)
        self.memory_usage.set(system_metrics.memory_percent)
        self.memory_total.set(system_metrics.memory_mb * 1024 * 1024)  # Convert to bytes
        self.disk_usage.set(system_metrics.disk_usage_percent)
        self.active_connections.set(system_metrics.active_connections)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')


class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self, collection_interval: float = 10.0):
        self.collection_interval = collection_interval
        self.running = False
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 measurements
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Initialize psutil for network monitoring
        self.network_io = psutil.net_io_counters()
    
    async def start(self) -> None:
        """Start system monitoring"""
        if self.running:
            return
        
        self.running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"📊 System monitor started (interval: {self.collection_interval}s)")
    
    async def stop(self) -> None:
        """Stop system monitoring"""
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("System monitor stopped")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Update Prometheus metrics if available
                if hasattr(self, 'prometheus_metrics'):
                    self.prometheus_metrics.update_system_metrics(metrics)
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network I/O
            current_network_io = psutil.net_io_counters()
            bytes_sent = current_network_io.bytes_sent
            bytes_recv = current_network_io.bytes_recv
            
            # Active connections (approximate)
            try:
                active_connections = len(psutil.net_connections(kind='inet'))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                active_connections = 0
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                disk_usage_percent=disk_usage_percent,
                network_bytes_sent=bytes_sent,
                network_bytes_recv=bytes_recv,
                active_connections=active_connections
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_mb=0.0,
                disk_usage_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                active_connections=0
            )
    
    def get_recent_metrics(self, minutes: int = 5) -> List[SystemMetrics]:
        """Get metrics from the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    def get_average_metrics(self, minutes: int = 5) -> Optional[Dict[str, float]]:
        """Get average metrics for the last N minutes"""
        recent_metrics = self.get_recent_metrics(minutes)
        
        if not recent_metrics:
            return None
        
        return {
            'avg_cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory_mb': sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            'avg_disk_usage_percent': sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            'max_cpu_percent': max(m.cpu_percent for m in recent_metrics),
            'max_memory_percent': max(m.memory_percent for m in recent_metrics)
        }


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for performance monitoring"""
    
    def __init__(self, app, 
                 enable_prometheus: bool = True,
                 enable_alerts: bool = True,
                 enable_system_monitoring: bool = True,
                 system_monitor_interval: float = 10.0):
        super().__init__(app)
        
        # Performance tracking
        self.endpoint_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.request_history: deque = deque(maxlen=10000)  # Keep last 10k requests
        
        # Components
        self.prometheus_metrics = PrometheusMetrics() if enable_prometheus else None
        self.alert_manager = AlertManager() if enable_alerts else None
        self.system_monitor = SystemMonitor(system_monitor_interval) if enable_system_monitoring else None
        
        # Connect components
        if self.system_monitor and self.prometheus_metrics:
            self.system_monitor.prometheus_metrics = self.prometheus_metrics
        
        # Request tracking
        self.active_requests = 0
        self.peak_concurrent_requests = 0
        
        logger.info("📊 Performance monitoring middleware initialized")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with monitoring"""
        start_time = time.time()
        request_size = int(request.headers.get('content-length', 0))
        
        # Track active requests
        self.active_requests += 1
        if self.active_requests > self.peak_concurrent_requests:
            self.peak_concurrent_requests = self.active_requests
        
        # Extract endpoint info
        method = request.method
        path = request.url.path
        endpoint = self._normalize_endpoint(path)
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
            # Calculate duration
            duration = time.time() - start_time
            response_size = int(response.headers.get('content-length', 0))
            
            # Update metrics
            await self._update_metrics(
                method, endpoint, status_code, duration, request_size, response_size
            )
            
            # Add monitoring headers
            response.headers['X-Response-Time'] = f"{duration:.3f}"
            response.headers['X-Request-ID'] = str(id(request))
            
            return response
            
        except Exception as e:
            # Handle errors
            duration = time.time() - start_time
            await self._update_metrics(
                method, endpoint, 500, duration, request_size, 0, error=True
            )
            raise
        
        finally:
            self.active_requests -= 1
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path for metrics"""
        # Replace IDs and parameters with placeholders
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '/{id}', path)
        
        # Replace other IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Limit path length
        if len(path) > 100:
            path = path[:97] + "..."
        
        return path
    
    async def _update_metrics(self, method: str, endpoint: str, status_code: int, 
                            duration: float, request_size: int, response_size: int,
                            error: bool = False) -> None:
        """Update performance metrics"""
        # Update endpoint metrics
        metrics = self.endpoint_metrics[endpoint]
        metrics.request_count += 1
        metrics.total_duration += duration
        metrics.min_duration = min(metrics.min_duration, duration)
        metrics.max_duration = max(metrics.max_duration, duration)
        metrics.last_request_time = datetime.utcnow()
        metrics.status_codes[status_code] += 1
        
        if error or status_code >= 400:
            metrics.error_count += 1
        
        # Store request history
        self.request_history.append({
            'timestamp': datetime.utcnow(),
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'request_size': request_size,
            'response_size': response_size,
            'error': error
        })
        
        # Update Prometheus metrics
        if self.prometheus_metrics:
            self.prometheus_metrics.request_count.labels(
                method=method, 
                endpoint=endpoint, 
                status_code=status_code
            ).inc()
            
            self.prometheus_metrics.request_duration.labels(
                method=method, 
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                self.prometheus_metrics.request_size.labels(
                    method=method, 
                    endpoint=endpoint
                ).observe(request_size)
            
            if response_size > 0:
                self.prometheus_metrics.response_size.labels(
                    method=method, 
                    endpoint=endpoint
                ).observe(response_size)
        
        # Check alerts
        if self.alert_manager:
            self.alert_manager.check_performance_alerts(endpoint, metrics)
    
    async def start_monitoring(self) -> None:
        """Start background monitoring"""
        if self.system_monitor:
            await self.system_monitor.start()
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        if self.system_monitor:
            await self.system_monitor.stop()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        summary = {
            'overview': {
                'total_requests': sum(m.request_count for m in self.endpoint_metrics.values()),
                'total_errors': sum(m.error_count for m in self.endpoint_metrics.values()),
                'active_requests': self.active_requests,
                'peak_concurrent_requests': self.peak_concurrent_requests,
                'average_response_time': self._calculate_global_avg_response_time(),
                'uptime_hours': self._calculate_uptime_hours()
            },
            'endpoints': {},
            'system': None
        }
        
        # Endpoint metrics
        for endpoint, metrics in self.endpoint_metrics.items():
            summary['endpoints'][endpoint] = {
                'request_count': metrics.request_count,
                'avg_duration': metrics.avg_duration,
                'min_duration': metrics.min_duration,
                'max_duration': metrics.max_duration,
                'error_rate': metrics.error_rate,
                'status_codes': dict(metrics.status_codes),
                'last_request': metrics.last_request_time.isoformat() if metrics.last_request_time else None
            }
        
        # System metrics
        if self.system_monitor:
            recent_avg = self.system_monitor.get_average_metrics(5)
            if recent_avg:
                summary['system'] = recent_avg
        
        return summary
    
    def _calculate_global_avg_response_time(self) -> float:
        """Calculate global average response time"""
        total_duration = sum(m.total_duration for m in self.endpoint_metrics.values())
        total_requests = sum(m.request_count for m in self.endpoint_metrics.values())
        return total_duration / total_requests if total_requests > 0 else 0.0
    
    def _calculate_uptime_hours(self) -> float:
        """Calculate approximate uptime in hours"""
        if not self.request_history:
            return 0.0
        
        first_request = min(req['timestamp'] for req in self.request_history)
        uptime = datetime.utcnow() - first_request
        return uptime.total_seconds() / 3600
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics"""
        if self.prometheus_metrics:
            return self.prometheus_metrics.get_metrics()
        return ""


# Global monitoring instance
monitoring_middleware: Optional[PerformanceMonitoringMiddleware] = None


def create_monitoring_middleware(app, **kwargs) -> PerformanceMonitoringMiddleware:
    """Create and configure monitoring middleware"""
    global monitoring_middleware
    monitoring_middleware = PerformanceMonitoringMiddleware(app, **kwargs)
    return monitoring_middleware


async def start_monitoring() -> None:
    """Start global monitoring"""
    if monitoring_middleware:
        await monitoring_middleware.start_monitoring()


async def stop_monitoring() -> None:
    """Stop global monitoring"""
    if monitoring_middleware:
        await monitoring_middleware.stop_monitoring()


def get_monitoring_summary() -> Dict[str, Any]:
    """Get global monitoring summary"""
    if monitoring_middleware:
        return monitoring_middleware.get_metrics_summary()
    return {}


def get_prometheus_metrics() -> str:
    """Get Prometheus metrics"""
    if monitoring_middleware:
        return monitoring_middleware.get_prometheus_metrics()
    return ""


# Alert handlers
def log_alert_handler(alert_key: str, alert_data: Dict[str, Any]) -> None:
    """Log alert to file"""
    try:
        alert_log_file = os.environ.get('ALERT_LOG_FILE', '/tmp/streamworks_alerts.log')
        with open(alert_log_file, 'a') as f:
            f.write(f"{json.dumps(alert_data)}\n")
    except Exception as e:
        logger.error(f"Failed to write alert log: {e}")


def webhook_alert_handler(alert_key: str, alert_data: Dict[str, Any]) -> None:
    """Send alert via webhook (placeholder)"""
    # In production, implement webhook notifications
    webhook_url = os.environ.get('ALERT_WEBHOOK_URL')
    if webhook_url:
        # TODO: Implement webhook sending
        logger.info(f"Would send alert to webhook: {webhook_url}")


# Context manager for performance monitoring
@asynccontextmanager
async def monitor_performance(operation_name: str):
    """Context manager for monitoring specific operations"""
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        
        if monitoring_middleware and monitoring_middleware.prometheus_metrics:
            # Record custom operation metrics
            # This would require creating custom metrics for operations
            logger.info(f"Operation {operation_name} completed in {duration:.3f}s")


# Utility functions for application-specific monitoring
def track_rag_query(duration: float, status: str = "success") -> None:
    """Track RAG query metrics"""
    if monitoring_middleware and monitoring_middleware.prometheus_metrics:
        monitoring_middleware.prometheus_metrics.rag_queries.labels(status=status).inc()
        monitoring_middleware.prometheus_metrics.rag_query_duration.observe(duration)


def track_llm_request(model: str, duration: float, status: str = "success") -> None:
    """Track LLM request metrics"""
    if monitoring_middleware and monitoring_middleware.prometheus_metrics:
        monitoring_middleware.prometheus_metrics.llm_requests.labels(model=model, status=status).inc()
        monitoring_middleware.prometheus_metrics.llm_request_duration.labels(model=model).observe(duration)


def track_file_upload(status: str = "success") -> None:
    """Track file upload metrics"""
    if monitoring_middleware and monitoring_middleware.prometheus_metrics:
        monitoring_middleware.prometheus_metrics.file_uploads.labels(status=status).inc()


def track_file_processing(processor: str, duration: float) -> None:
    """Track file processing metrics"""
    if monitoring_middleware and monitoring_middleware.prometheus_metrics:
        monitoring_middleware.prometheus_metrics.file_processing_duration.labels(processor=processor).observe(duration)