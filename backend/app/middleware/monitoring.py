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

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance and logging metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.total_request_time = 0.0
        
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
            
            # Log response details
            self._log_request_complete(request_id, request, response, process_time)
            
            # BA-specific: Log performance for analysis
            if process_time > 2.0:  # Log slow requests
                logger.warning(f"⚠️ [{request_id}] Slow request: {process_time:.2f}s")
            
            return response
            
        except Exception as e:
            # Track errors
            self.error_count += 1
            process_time = time.time() - start_time
            
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
    
    def get_metrics(self) -> dict:
        """Get current performance metrics"""
        avg_time = self.total_request_time / self.request_count if self.request_count > 0 else 0
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "average_response_time": avg_time,
            "total_processing_time": self.total_request_time
        }


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