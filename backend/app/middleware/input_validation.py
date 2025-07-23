"""
Input validation middleware for production security
"""
import json
import time
from typing import Any, Dict, List
from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from app.core.validators import SecurityValidator, ContentSecurityValidator
from app.core.logging_config import security_logger, get_logger
from app.core.settings import settings

logger = get_logger(__name__)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating and sanitizing all input"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.max_request_size = production_settings.MAX_REQUEST_SIZE
        self.validate_json = True
        self.validate_query_params = True
        self.validate_form_data = True
        
        # Endpoints that require special validation
        self.sensitive_endpoints = [
            '/api/v1/chunks/search',
            '/api/v1/training/upload',
            '/api/v1/chat',
        ]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        try:
            # Validate request size
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_request_size:
                security_logger.log_suspicious_activity(
                    activity_type="oversized_request",
                    description=f"Request size {content_length} exceeds limit",
                    ip_address=self._get_client_ip(request),
                    severity="medium"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request size exceeds maximum allowed size of {self.max_request_size} bytes"
                )
            
            # Validate Content-Type for POST/PUT requests
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_content_type(request)
            
            # Validate query parameters
            if self.validate_query_params:
                await self._validate_query_parameters(request)
            
            # Validate JSON body for sensitive endpoints
            if (request.method in ["POST", "PUT", "PATCH"] and 
                any(endpoint in str(request.url.path) for endpoint in self.sensitive_endpoints)):
                await self._validate_json_body(request)
            
            # Add security headers to request state
            request.state.validation_start_time = start_time
            request.state.client_ip = self._get_client_ip(request)
            
            response = await call_next(request)
            
            # Log successful validation
            validation_time = time.time() - start_time
            if validation_time > 0.1:  # Log slow validations
                logger.warning(
                    "Slow input validation",
                    path=request.url.path,
                    method=request.method,
                    validation_time_ms=round(validation_time * 1000, 2)
                )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Input validation error",
                path=request.url.path,
                method=request.method,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request format"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return getattr(request.client, 'host', 'unknown')
    
    async def _validate_content_type(self, request: Request):
        """Validate Content-Type header"""
        content_type = request.headers.get("content-type", "")
        
        if not content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content-Type header is required"
            )
        
        # Allow only specific content types
        allowed_content_types = [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
            "text/plain"
        ]
        
        content_type_main = content_type.split(';')[0].strip()
        if not any(allowed_type in content_type_main for allowed_type in allowed_content_types):
            security_logger.log_suspicious_activity(
                activity_type="invalid_content_type",
                description=f"Invalid Content-Type: {content_type}",
                ip_address=self._get_client_ip(request),
                severity="low"
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content-Type '{content_type}' is not allowed"
            )
    
    async def _validate_query_parameters(self, request: Request):
        """Validate query parameters"""
        for key, value in request.query_params.items():
            # Validate parameter name
            if not key.replace('_', '').replace('-', '').isalnum():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parameter name: {key}"
                )
            
            # Validate parameter value
            if isinstance(value, str):
                try:
                    SecurityValidator.validate_text_input(value, f"query parameter '{key}'")
                except ValueError as e:
                    security_logger.log_suspicious_activity(
                        activity_type="malicious_query_param",
                        description=f"Malicious query parameter detected: {key}={value[:50]}",
                        ip_address=self._get_client_ip(request),
                        severity="high"
                    )
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid query parameter: {str(e)}"
                    )
    
    async def _validate_json_body(self, request: Request):
        """Validate JSON request body"""
        if not request.headers.get("content-type", "").startswith("application/json"):
            return
        
        try:
            # Read body
            body = await request.body()
            if not body:
                return
            
            # Parse JSON
            try:
                json_data = json.loads(body)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid JSON format: {str(e)}"
                )
            
            # Validate JSON structure
            self._validate_json_structure(json_data, request)
            
            # Check for suspicious content
            content_str = json.dumps(json_data)
            self._scan_for_suspicious_content(content_str, request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"JSON validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body validation failed"
            )
    
    def _validate_json_structure(self, data: Any, request: Request):
        """Validate JSON structure and content"""
        max_depth = 10
        max_keys = 100
        max_string_length = 10000
        
        def validate_recursive(obj: Any, depth: int = 0):
            if depth > max_depth:
                raise ValueError("JSON structure too deeply nested")
            
            if isinstance(obj, dict):
                if len(obj) > max_keys:
                    raise ValueError("Too many keys in JSON object")
                
                for key, value in obj.items():
                    # Validate key
                    if not isinstance(key, str):
                        raise ValueError("JSON keys must be strings")
                    
                    if len(key) > 255:
                        raise ValueError("JSON key too long")
                    
                    try:
                        SecurityValidator.validate_text_input(key, "JSON key")
                    except ValueError:
                        raise ValueError(f"Invalid JSON key: {key}")
                    
                    # Validate value recursively
                    validate_recursive(value, depth + 1)
            
            elif isinstance(obj, list):
                if len(obj) > 1000:
                    raise ValueError("JSON array too large")
                
                for item in obj:
                    validate_recursive(item, depth + 1)
            
            elif isinstance(obj, str):
                if len(obj) > max_string_length:
                    raise ValueError("JSON string too long")
                
                try:
                    SecurityValidator.validate_text_input(obj, "JSON string")
                except ValueError as e:
                    raise ValueError(f"Invalid JSON string content: {e}")
        
        try:
            validate_recursive(data)
        except ValueError as e:
            security_logger.log_suspicious_activity(
                activity_type="malicious_json",
                description=str(e),
                ip_address=self._get_client_ip(request),
                severity="medium"
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    def _scan_for_suspicious_content(self, content: str, request: Request):
        """Scan content for suspicious patterns"""
        # Check for secrets
        secrets = ContentSecurityValidator.scan_content_for_secrets(content)
        if secrets:
            security_logger.log_suspicious_activity(
                activity_type="potential_secret_exposure",
                description=f"Potential secrets detected in request: {len(secrets)} findings",
                ip_address=self._get_client_ip(request),
                severity="high"
            )
            
            logger.warning(
                "Potential secrets detected in request",
                path=request.url.path,
                findings_count=len(secrets),
                client_ip=self._get_client_ip(request)
            )
        
        # Check for suspicious URLs
        suspicious_urls = ContentSecurityValidator.validate_urls_in_content(content)
        if suspicious_urls:
            security_logger.log_suspicious_activity(
                activity_type="suspicious_urls",
                description=f"Suspicious URLs detected: {suspicious_urls}",
                ip_address=self._get_client_ip(request),
                severity="medium"
            )


class FileUploadValidationMiddleware(BaseHTTPMiddleware):
    """Specialized middleware for file upload validation"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.upload_endpoints = [
            '/api/v1/training/upload',
            '/api/v1/training/upload-batch',
            '/api/v1/chat/upload-docs',
        ]
        self.max_file_size = production_settings.UPLOAD_MAX_SIZE
        self.allowed_extensions = production_settings.UPLOAD_ALLOWED_EXTENSIONS
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only process file upload endpoints
        if not any(endpoint in str(request.url.path) for endpoint in self.upload_endpoints):
            return await call_next(request)
        
        # Check if it's a multipart request
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("multipart/form-data"):
            return await call_next(request)
        
        try:
            # Pre-validate content length
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_file_size:
                security_logger.log_suspicious_activity(
                    activity_type="oversized_upload",
                    description=f"Upload size {content_length} exceeds limit",
                    ip_address=self._get_client_ip(request),
                    severity="medium"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds maximum allowed size of {self.max_file_size} bytes"
                )
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File upload validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File upload validation failed"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return getattr(request.client, 'host', 'unknown')


def setup_input_validation_middleware(app: FastAPI):
    """Setup input validation middleware"""
    app.add_middleware(InputValidationMiddleware)
    app.add_middleware(FileUploadValidationMiddleware)
    
    logger.info("Input validation middleware setup completed")