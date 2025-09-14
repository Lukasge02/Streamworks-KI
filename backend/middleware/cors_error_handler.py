"""
CORS Error Handler Middleware
Ensures CORS headers are present even on error responses
"""

import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response as StarletteResponse

logger = logging.getLogger(__name__)

class CORSErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure CORS headers are always present, even on error responses"""

    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3002"
        ]

    def _add_cors_headers(self, response: Response, origin: str = None) -> Response:
        """Add CORS headers to any response"""
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Vary"] = "Origin"

        return response

    async def dispatch(self, request: Request, call_next):
        """Process request and ensure CORS headers on all responses"""
        origin = request.headers.get("origin")

        try:
            response = await call_next(request)

            # Add CORS headers to successful responses
            if origin:
                response = self._add_cors_headers(response, origin)

            return response

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")

            # Create error response with CORS headers
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred"
                }
            )

            # Ensure CORS headers are present on error responses
            if origin:
                error_response = self._add_cors_headers(error_response, origin)

            return error_response