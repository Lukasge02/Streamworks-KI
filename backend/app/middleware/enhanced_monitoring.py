"""
Enhanced monitoring middleware with comprehensive metrics
"""
import time
import psutil
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
import structlog
from app.core.logging_config import performance_logger, security_logger, business_logger

logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

CONCURRENT_REQUESTS = Gauge(
    'http_requests_concurrent',
    'Number of concurrent HTTP requests'
)

# System metrics
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage_percent', 'System disk usage percentage')
SYSTEM_LOAD_AVERAGE = Gauge('system_load_average', 'System load average')

# Application metrics
CHUNKS_TOTAL = Gauge('chunks_total', 'Total number of chunks in database')
CHUNKS_SEARCHES_TOTAL = Counter('chunks_searches_total', 'Total number of chunk searches')
CHUNKS_UPLOADS_TOTAL = Counter('chunks_uploads_total', 'Total number of chunk uploads')

# LLM metrics
LLM_REQUESTS_TOTAL = Counter('llm_requests_total', 'Total LLM requests', ['model', 'operation'])
LLM_REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'LLM request duration', ['model', 'operation'])
LLM_TOKENS_PROCESSED = Counter('llm_tokens_processed_total', 'Total tokens processed', ['model', 'type'])

# Error metrics
ERROR_COUNT = Counter('errors_total', 'Total number of errors', ['type', 'endpoint'])
RATE_LIMIT_HITS = Counter('rate_limit_hits_total', 'Total rate limit hits', ['endpoint', 'client_type'])

# Service info
SERVICE_INFO = Info('service_info', 'Information about the service')


class EnhancedMonitoringMiddleware(BaseHTTPMiddleware):
    """Comprehensive monitoring middleware"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.concurrent_requests = 0
        
        # Set service info
        SERVICE_INFO.info({
            'version': '2.1.0',
            'environment': 'production',
            'service': 'streamworks-ki-backend'
        })
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Start timing
        start_time = time.time()
        
        # Increment concurrent requests
        self.concurrent_requests += 1
        CONCURRENT_REQUESTS.set(self.concurrent_requests)
        
        # Get request info
        method = request.method
        path = request.url.path
        endpoint = self._normalize_path(path)
        
        # Get request size
        request_size = int(request.headers.get('content-length', 0))
        REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(request_size)
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Get response size
            response_size = 0
            if hasattr(response, 'body'):
                response_size = len(response.body)
            
            RESPONSE_SIZE.labels(method=method, endpoint=endpoint).observe(response_size)
            
        except Exception as e:
            # Log error
            logger.error("Request processing error", error=str(e), path=path, method=method)
            ERROR_COUNT.labels(type=type(e).__name__, endpoint=endpoint).inc()
            raise
        finally:
            # Decrement concurrent requests
            self.concurrent_requests -= 1
            CONCURRENT_REQUESTS.set(self.concurrent_requests)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Log performance
        performance_logger.log_request_performance(
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            request_size=request_size,
            response_size=response_size
        )
        
        # Log slow requests
        if duration > 5.0:  # 5 seconds threshold
            logger.warning(
                "Slow request detected",
                method=method,
                path=path,
                duration=duration,
                status_code=status_code
            )
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics to avoid high cardinality"""
        # Replace UUIDs and IDs with placeholders
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace file names
        path = re.sub(r'/[^/]+\.(txt|pdf|docx|md|json)', '/{filename}', path)
        
        return path


class SystemMetricsCollector:
    """Collect system metrics"""
    
    @staticmethod
    def update_system_metrics():
        """Update system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            SYSTEM_DISK_USAGE.set(disk_percent)
            
            # Load average
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            SYSTEM_LOAD_AVERAGE.set(load_avg)
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))


class BusinessMetricsCollector:
    """Collect business metrics"""
    
    def __init__(self):
        self.rag_service = None
        self.db_session = None
    
    def set_services(self, rag_service, db_session):
        """Set service dependencies"""
        self.rag_service = rag_service
        self.db_session = db_session
    
    async def update_business_metrics(self):
        """Update business metrics"""
        try:
            if self.rag_service:
                # Get chunk count from ChromaDB
                stats = await self.rag_service.get_stats()
                if stats and 'documents_count' in stats:
                    CHUNKS_TOTAL.set(stats['documents_count'])
                    
        except Exception as e:
            logger.error("Error collecting business metrics", error=str(e))


class LLMMetricsLogger:
    """Logger for LLM-specific metrics"""
    
    @staticmethod
    def log_llm_request(
        model: str,
        operation: str,
        duration: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        success: bool = True
    ):
        """Log LLM request metrics"""
        LLM_REQUESTS_TOTAL.labels(model=model, operation=operation).inc()
        LLM_REQUEST_DURATION.labels(model=model, operation=operation).observe(duration)
        
        if tokens_input > 0:
            LLM_TOKENS_PROCESSED.labels(model=model, type='input').inc(tokens_input)
        
        if tokens_output > 0:
            LLM_TOKENS_PROCESSED.labels(model=model, type='output').inc(tokens_output)
        
        # Log to structured logger
        performance_logger.log_llm_performance(
            model=model,
            operation=operation,
            duration=duration,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            success=success
        )


class SearchMetricsLogger:
    """Logger for search-specific metrics"""
    
    @staticmethod
    def log_search_request(
        query: str,
        results_count: int,
        duration: float,
        user_id: Optional[str] = None
    ):
        """Log search request metrics"""
        CHUNKS_SEARCHES_TOTAL.inc()
        
        # Log to business logger
        business_logger.log_search_operation(
            query=query,
            results_count=results_count,
            duration=duration,
            user_id=user_id
        )


class UploadMetricsLogger:
    """Logger for upload-specific metrics"""
    
    @staticmethod
    def log_upload_request(
        filename: str,
        file_size: int,
        file_type: str,
        success: bool,
        duration: float,
        user_id: Optional[str] = None
    ):
        """Log upload request metrics"""
        CHUNKS_UPLOADS_TOTAL.inc()
        
        # Log to business logger
        business_logger.log_upload_operation(
            filename=filename,
            file_size=file_size,
            file_type=file_type,
            success=success,
            duration=duration,
            user_id=user_id
        )


class HealthCheckMetrics:
    """Health check metrics and endpoints"""
    
    def __init__(self):
        self.service_status = Gauge('service_health_status', 'Service health status', ['service'])
        self.dependency_status = Gauge('dependency_health_status', 'Dependency health status', ['dependency'])
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {},
            'system': {}
        }
        
        try:
            # Check system resources
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status['system'] = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
            
            # Set service status
            self.service_status.labels(service='backend').set(1)
            
        except Exception as e:
            logger.error("Health check error", error=str(e))
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
            self.service_status.labels(service='backend').set(0)
        
        return health_status


# Create global instances
system_metrics_collector = SystemMetricsCollector()
business_metrics_collector = BusinessMetricsCollector()
llm_metrics_logger = LLMMetricsLogger()
search_metrics_logger = SearchMetricsLogger()
upload_metrics_logger = UploadMetricsLogger()
health_check_metrics = HealthCheckMetrics()


def setup_monitoring_middleware(app: FastAPI):
    """Setup monitoring middleware"""
    app.add_middleware(EnhancedMonitoringMiddleware)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        # Update system metrics before serving
        system_metrics_collector.update_system_metrics()
        
        # Update business metrics
        await business_metrics_collector.update_business_metrics()
        
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    @app.get("/health/detailed")
    async def detailed_health():
        """Detailed health check endpoint"""
        return await health_check_metrics.check_service_health()
    
    logger.info("Enhanced monitoring middleware setup completed")