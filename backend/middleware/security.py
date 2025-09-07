"""
Security Middleware
Implements security headers, input validation, and rate limiting
"""

import os
import time
import hashlib
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self):
        # Rate limiting storage
        self.rate_limiter = defaultdict(lambda: deque())
        self.blocked_ips = set()
        
        # Security settings
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "100"))
        self.block_duration = int(os.getenv("BLOCK_DURATION_SECONDS", "300"))  # 5 minutes
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024  # 50MB
        
    async def __call__(self, request: Request, call_next):
        """Main middleware function"""
        
        # Security headers
        response = await self._add_security_headers(request, call_next)
        
        return response
    
    async def _add_security_headers(self, request: Request, call_next) -> Response:
        """Add comprehensive security headers"""
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        response.headers.update({
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Prevent MIME sniffing
            "X-Content-Type-Options": "nosniff",
            
            # XSS Protection
            "X-XSS-Protection": "1; mode=block",
            
            # Force HTTPS (in production)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains" if self._is_production() else "",
            
            # Content Security Policy
            "Content-Security-Policy": self._get_csp_policy(),
            
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
            
            # Server info
            "Server": "StreamWorks-API"
        })
        
        # Remove server header leak
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
    
    def _is_production(self) -> bool:
        """Check if running in production"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def _get_csp_policy(self) -> str:
        """Generate Content Security Policy"""
        if self._is_production():
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # More permissive for development
            return "default-src 'self' 'unsafe-inline' 'unsafe-eval' http: https: data:"

class RateLimiter:
    """Advanced rate limiting with different limits per user type"""
    
    def __init__(self):
        self.requests = defaultdict(lambda: deque())
        self.blocked_until = {}
    
    def is_allowed(self, identifier: str, limit: int = 100, window: int = 60) -> bool:
        """
        Check if request is allowed
        
        Args:
            identifier: IP address or user ID
            limit: Number of requests allowed in window
            window: Time window in seconds
        """
        now = time.time()
        
        # Check if currently blocked
        if identifier in self.blocked_until:
            if now < self.blocked_until[identifier]:
                return False
            else:
                # Unblock
                del self.blocked_until[identifier]
        
        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] < now - window:
            request_times.popleft()
        
        # Check rate limit
        if len(request_times) >= limit:
            # Block for 5 minutes
            self.blocked_until[identifier] = now + 300
            logger.warning(f"Rate limit exceeded for {identifier}, blocked for 5 minutes")
            return False
        
        # Add current request
        request_times.append(now)
        return True

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename or len(filename.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty"
            )
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:251-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def validate_file_content(content: bytes, max_size: int = 50 * 1024 * 1024) -> bool:
        """Validate file content"""
        
        # Check size
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB"
            )
        
        # Basic malware detection (check for suspicious patterns)
        suspicious_patterns = [
            b'eval(',
            b'exec(',
            b'<script',
            b'javascript:',
            b'<?php'
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                logger.warning(f"Suspicious pattern detected: {pattern}")
                # In production, you might want to block this
                # For now, just log
        
        return True
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize user query"""
        if not query or len(query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Limit query length
        if len(query) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query too long (max 5000 characters)"
            )
        
        # Remove control characters
        query = ''.join(char for char in query if ord(char) >= 32 or char in '\t\n\r')
        
        return query.strip()

# Global instances
security_middleware = SecurityMiddleware()
rate_limiter = RateLimiter()
input_validator = InputValidator()

async def security_middleware_func(request: Request, call_next):
    """Security middleware function for FastAPI"""
    return await security_middleware(request, call_next)

def get_client_ip(request: Request) -> str:
    """Get client IP address, considering proxies"""
    # Check for forwarded headers (when behind reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    forwarded = request.headers.get("X-Forwarded")
    if forwarded:
        return forwarded.strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

def check_rate_limit(request: Request, limit: int = 100, window: int = 60) -> bool:
    """Check rate limit for request"""
    client_ip = get_client_ip(request)
    
    # Use user ID if authenticated
    user = getattr(request.state, 'user', None)
    identifier = f"user_{user.id}" if user else f"ip_{client_ip}"
    
    return rate_limiter.is_allowed(identifier, limit, window)