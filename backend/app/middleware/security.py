"""
Security middleware for production deployment
"""
import time
import hashlib
import logging
from typing import Callable, Optional, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse
import redis
from app.core.production_config import production_settings, SecurityConfig

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.security_headers = SecurityConfig.get_security_headers()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add request ID for tracing
        request_id = getattr(request.state, "request_id", "unknown")
        response.headers["X-Request-ID"] = request_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app: FastAPI, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client or self._create_redis_client()
        self.enabled = production_settings.RATE_LIMIT_ENABLED
        
        # Rate limit configurations
        self.rate_limits = {
            "/api/v1/chunks": self._parse_rate_limit(production_settings.RATE_LIMIT_CHUNKS),
            "/api/v1/chunks/search": self._parse_rate_limit(production_settings.RATE_LIMIT_SEARCH),
            "/api/v1/training/upload": self._parse_rate_limit(production_settings.RATE_LIMIT_UPLOAD),
            "default": self._parse_rate_limit(production_settings.RATE_LIMIT_DEFAULT),
        }
    
    def _create_redis_client(self) -> redis.Redis:
        """Create Redis client for rate limiting"""
        try:
            return redis.from_url(
                production_settings.REDIS_URL,
                decode_responses=True,
                health_check_interval=30,
                retry_on_timeout=True,
            )
        except Exception as e:
            logger.warning(f"Could not connect to Redis for rate limiting: {e}")
            return None
    
    def _parse_rate_limit(self, rate_string: str) -> tuple[int, int]:
        """Parse rate limit string like '100/hour' to (requests, seconds)"""
        try:
            requests, period = rate_string.split("/")
            requests = int(requests)
            
            period_seconds = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400,
            }.get(period, 3600)
            
            return requests, period_seconds
        except:
            return 1000, 3600  # Default fallback
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from auth header or session
        auth_header = request.headers.get("authorization")
        if auth_header:
            return hashlib.sha256(auth_header.encode()).hexdigest()[:16]
        
        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return client_ip
    
    def _get_rate_limit_key(self, client_id: str, endpoint: str) -> str:
        """Generate rate limit key for Redis"""
        return f"rate_limit:{endpoint}:{client_id}"
    
    def _get_rate_limit_for_path(self, path: str) -> tuple[int, int]:
        """Get rate limit configuration for specific path"""
        for endpoint_path, rate_limit in self.rate_limits.items():
            if endpoint_path != "default" and path.startswith(endpoint_path):
                return rate_limit
        return self.rate_limits["default"]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self.enabled or not self.redis_client:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        path = request.url.path
        requests_limit, window_seconds = self._get_rate_limit_for_path(path)
        
        # Create rate limit key
        rate_key = self._get_rate_limit_key(client_id, path)
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            # Use Redis sorted set for sliding window rate limiting
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(rate_key, window_seconds)
            
            results = pipe.execute()
            current_requests = results[1]
            
            # Check if rate limit exceeded
            if current_requests >= requests_limit:
                logger.warning(
                    f"Rate limit exceeded for {client_id} on {path}: "
                    f"{current_requests}/{requests_limit} requests"
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Too many requests. Limit: {requests_limit} per {window_seconds}s",
                        "retry_after": window_seconds,
                    },
                    headers={
                        "Retry-After": str(window_seconds),
                        "X-RateLimit-Limit": str(requests_limit),
                        "X-RateLimit-Remaining": str(max(0, requests_limit - current_requests - 1)),
                        "X-RateLimit-Reset": str(current_time + window_seconds),
                    },
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(requests_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, requests_limit - current_requests - 1))
            response.headers["X-RateLimit-Reset"] = str(current_time + window_seconds)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if Redis fails
            return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize incoming requests"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.max_request_size = production_settings.MAX_REQUEST_SIZE
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Request too large",
                    "detail": f"Request size exceeds maximum allowed size of {self.max_request_size} bytes",
                    "max_size": self.max_request_size,
                },
            )
        
        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Missing Content-Type header",
                        "detail": "Content-Type header is required for this request",
                    },
                )
        
        # Add request timestamp and ID
        request.state.start_time = time.time()
        request.state.request_id = hashlib.sha256(
            f"{time.time()}{request.client.host}{request.method}{request.url.path}".encode()
        ).hexdigest()[:16]
        
        response = await call_next(request)
        
        # Add response time header
        if hasattr(request.state, "start_time"):
            process_time = time.time() - request.state.start_time
            response.headers["X-Response-Time"] = f"{process_time:.4f}"
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for sensitive endpoints"""
    
    def __init__(self, app: FastAPI, whitelist: Optional[list] = None):
        super().__init__(app)
        self.whitelist = whitelist or []
        self.protected_paths = [
            "/api/v1/monitoring",
            "/metrics",
            "/health/detailed",
        ]
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self.whitelist:
            return await call_next(request)
        
        path = request.url.path
        
        # Check if path is protected
        if any(path.startswith(protected) for protected in self.protected_paths):
            client_ip = self._get_client_ip(request)
            
            if client_ip not in self.whitelist:
                logger.warning(f"Access denied for IP {client_ip} to protected path {path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "Access denied",
                        "detail": "Your IP address is not authorized to access this endpoint",
                    },
                )
        
        return await call_next(request)


def setup_security_middleware(app: FastAPI) -> None:
    """Setup all security middleware"""
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add request validation
    app.add_middleware(RequestValidationMiddleware)
    
    # Add rate limiting if enabled
    if production_settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)
    
    # Add IP whitelist for monitoring endpoints
    monitoring_whitelist = [
        "127.0.0.1",
        "::1",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]
    app.add_middleware(IPWhitelistMiddleware, whitelist=monitoring_whitelist)
    
    logger.info("Security middleware setup completed")