"""
Performance Monitoring Middleware for StreamWorks-KI
Tracks request times, errors, and performance metrics
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json
from collections import defaultdict, deque
from datetime import datetime
import threading
import psutil

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Advanced Performance Monitoring Middleware with detailed analytics"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Basic counters
        self.request_count = 0
        self.error_count = 0
        self.total_request_time = 0.0
        
        # Advanced metrics
        self.endpoint_metrics = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "errors": 0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "recent_times": deque(maxlen=100)  # Last 100 requests
        })
        
        # System metrics tracking
        self.system_metrics = {
            "cpu_percent": deque(maxlen=60),  # Last 60 readings
            "memory_percent": deque(maxlen=60),
            "active_connections": 0
        }
        
        # Slow request tracking
        self.slow_requests = deque(maxlen=50)  # Keep last 50 slow requests
        self.slow_threshold = 2.0  # seconds
        
        # Periodic system monitoring
        self._start_system_monitoring()
        
        logger.info("📊 Advanced Performance Monitoring initialized")
    
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while True:
                try:
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent
                    
                    self.system_metrics["cpu_percent"].append(cpu_percent)
                    self.system_metrics["memory_percent"].append(memory_percent)
                    
                    time.sleep(10)  # Update every 10 seconds
                except Exception as e:
                    logger.warning(f"System monitoring error: {e}")
                    time.sleep(30)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request with performance monitoring"""
        # Start timer
        start_time = time.time()
        self.request_count += 1
        
        # Generate request ID
        request_id = f"req_{self.request_count}_{int(start_time)}"
        
        # Log request details
        logger.info(f"📥 [{request_id}] {request.method} {request.url.path}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            self.total_request_time += process_time
            
            # Add performance headers
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            response.headers["X-Request-ID"] = request_id
            
            # Update endpoint metrics
            self._update_endpoint_metrics(request.url.path, process_time, response.status_code)
            
            # Track slow requests
            if process_time > self.slow_threshold:
                self._track_slow_request(request_id, request, process_time)
            
            # Log response details
            self._log_request_complete(request_id, request, response, process_time)
            
            return response
            
        except Exception as e:
            # Track errors
            self.error_count += 1
            process_time = time.time() - start_time
            
            # Update endpoint error metrics
            self._update_endpoint_metrics(request.url.path, process_time, 500, is_error=True)
            
            logger.error(f"❌ [{request_id}] Error after {process_time:.2f}s: {str(e)}")
            
            # Re-raise the exception
            raise
    
    def _log_request_complete(self, request_id: str, request: Request, response: Response, process_time: float):
        """Log completed request with metrics"""
        # Determine log level based on status code
        status = response.status_code
        
        if 200 <= status < 300:
            emoji = "✅"
            log_func = logger.info
        elif 400 <= status < 500:
            emoji = "⚠️"
            log_func = logger.warning
        else:
            emoji = "❌"
            log_func = logger.error
        
        # Log with appropriate level
        log_func(
            f"{emoji} [{request_id}] "
            f"{request.method} {request.url.path} "
            f"-> {status} in {process_time:.3f}s"
        )
        
        # Additional metrics for specific endpoints
        if request.url.path == "/api/v1/chat/" and process_time > 0:
            self._log_chat_metrics(request_id, process_time)
    
    def _log_chat_metrics(self, request_id: str, process_time: float):
        """Log specific metrics for chat endpoint"""
        avg_time = self.total_request_time / self.request_count if self.request_count > 0 else 0
        
        logger.info(
            f"📊 Chat Metrics: "
            f"Total Requests: {self.request_count}, "
            f"Avg Time: {avg_time:.3f}s, "
            f"Errors: {self.error_count}"
        )
    
    def _update_endpoint_metrics(self, path: str, process_time: float, status_code: int, is_error: bool = False):
        """Update metrics for specific endpoint"""
        metrics = self.endpoint_metrics[path]
        metrics["count"] += 1
        metrics["total_time"] += process_time
        
        if is_error or status_code >= 400:
            metrics["errors"] += 1
        
        # Update timing stats
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]
        metrics["min_time"] = min(metrics["min_time"], process_time)
        metrics["max_time"] = max(metrics["max_time"], process_time)
        metrics["recent_times"].append(process_time)
    
    def _track_slow_request(self, request_id: str, request: Request, process_time: float):
        """Track slow requests for analysis"""
        slow_request = {
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "process_time": process_time,
            "timestamp": datetime.now().isoformat(),
            "query_params": dict(request.query_params) if request.query_params else {},
        }
        
        self.slow_requests.append(slow_request)
        logger.warning(f"🐌 Slow request [{request_id}]: {process_time:.3f}s on {request.method} {request.url.path}")
    
    def get_metrics(self) -> dict:
        """Get comprehensive performance metrics"""
        avg_time = self.total_request_time / self.request_count if self.request_count > 0 else 0
        
        # Calculate system metrics averages
        cpu_avg = sum(self.system_metrics["cpu_percent"]) / len(self.system_metrics["cpu_percent"]) if self.system_metrics["cpu_percent"] else 0
        memory_avg = sum(self.system_metrics["memory_percent"]) / len(self.system_metrics["memory_percent"]) if self.system_metrics["memory_percent"] else 0
        
        return {
            "overview": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
                "average_response_time": avg_time,
                "total_processing_time": self.total_request_time,
                "slow_requests_count": len(self.slow_requests)
            },
            "system": {
                "cpu_percent": cpu_avg,
                "memory_percent": memory_avg,
                "active_connections": self.system_metrics["active_connections"]
            },
            "endpoints": {
                path: {
                    "count": metrics["count"],
                    "avg_time": metrics["avg_time"],
                    "min_time": metrics["min_time"] if metrics["min_time"] != float('inf') else 0,
                    "max_time": metrics["max_time"],
                    "error_rate": metrics["errors"] / metrics["count"] if metrics["count"] > 0 else 0,
                    "recent_avg": sum(list(metrics["recent_times"])) / len(metrics["recent_times"]) if metrics["recent_times"] else 0
                }
                for path, metrics in self.endpoint_metrics.items()
            },
            "slow_requests": list(self.slow_requests)
        }
    
    def get_endpoint_metrics(self, path: str = None) -> dict:
        """Get metrics for specific endpoint or all endpoints"""
        if path:
            return self.endpoint_metrics.get(path, {})
        return dict(self.endpoint_metrics)
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.request_count = 0
        self.error_count = 0
        self.total_request_time = 0.0
        self.endpoint_metrics.clear()
        self.slow_requests.clear()
        logger.info("📊 Performance metrics reset")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Additional middleware for detailed request/response logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details"""
        # Log request body for POST requests (excluding file uploads)
        if request.method == "POST" and request.url.path != "/api/v1/upload":
            try:
                body = await request.body()
                if body and len(body) < 1000:  # Only log small bodies
                    logger.debug(f"📝 Request Body: {body.decode('utf-8')[:200]}...")
                # Reset body for downstream processing
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except Exception as e:
                logger.debug(f"Could not log request body: {e}")
        
        # Process request
        response = await call_next(request)
        
        return response


class StreamWorksMetricsMiddleware(BaseHTTPMiddleware):
    """StreamWorks-specific metrics collection"""
    
    def __init__(self, app):
        super().__init__(app)
        self.endpoint_metrics = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect StreamWorks-specific metrics"""
        endpoint = request.url.path
        
        # Initialize endpoint metrics if needed
        if endpoint not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "errors": 0,
                "last_error": None
            }
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Update metrics
            self.endpoint_metrics[endpoint]["count"] += 1
            self.endpoint_metrics[endpoint]["total_time"] += process_time
            
            # Track specific StreamWorks operations
            if endpoint == "/api/v1/streams/generate-stream":
                logger.info(f"🔧 Stream Generation completed in {process_time:.2f}s")
            elif endpoint == "/api/v1/chat/" and response.status_code == 200:
                logger.info(f"💬 Chat Response generated in {process_time:.2f}s")
            
            return response
            
        except Exception as e:
            # Track errors by endpoint
            self.endpoint_metrics[endpoint]["errors"] += 1
            self.endpoint_metrics[endpoint]["last_error"] = str(e)
            raise
    
    def get_endpoint_metrics(self) -> dict:
        """Get metrics by endpoint"""
        metrics = {}
        
        for endpoint, data in self.endpoint_metrics.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            metrics[endpoint] = {
                "requests": data["count"],
                "avg_time": round(avg_time, 3),
                "errors": data["errors"],
                "error_rate": round(data["errors"] / data["count"], 3) if data["count"] > 0 else 0,
                "last_error": data["last_error"]
            }
        
        return metrics