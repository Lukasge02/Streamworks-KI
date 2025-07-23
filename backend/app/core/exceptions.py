"""
Standardized Exception Handling for StreamWorks-KI
Provides consistent error handling across all services
"""
import logging
from enum import Enum
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes"""
    
    # System errors (1000-1999)
    SYSTEM_ERROR = "SYSTEM_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INITIALIZATION_ERROR = "INITIALIZATION_ERROR"
    
    # Authentication/Authorization (2000-2999)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # Validation errors (3000-3999)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Resource errors (4000-4999)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    RESOURCE_QUOTA_EXCEEDED = "RESOURCE_QUOTA_EXCEEDED"
    
    # Database errors (5000-5999)
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    
    # File operations (6000-6999)
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_PERMISSION_ERROR = "FILE_PERMISSION_ERROR"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_FORMAT_UNSUPPORTED = "FILE_FORMAT_UNSUPPORTED"
    FILE_PROCESSING_ERROR = "FILE_PROCESSING_ERROR"
    
    # LLM/AI operations (7000-7999)
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    
    # RAG operations (8000-8999)
    RAG_SEARCH_ERROR = "RAG_SEARCH_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    INDEXING_ERROR = "INDEXING_ERROR"
    
    # Business logic (9000-9999)
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class StreamWorksException(Exception):
    """Base exception for all StreamWorks-KI errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_error = original_error
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
        
        if self.original_error:
            result["original_error"] = str(self.original_error)
            result["original_error_type"] = type(self.original_error).__name__
        
        return result


# Specific exception classes

class ValidationError(StreamWorksException):
    """Validation error"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)


class ResourceNotFoundError(StreamWorksException):
    """Resource not found error"""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, details)


class ServiceUnavailableError(StreamWorksException):
    """Service unavailable error"""
    def __init__(self, service_name: str, reason: Optional[str] = None):
        message = f"Service '{service_name}' is unavailable"
        if reason:
            message += f": {reason}"
        
        details = {"service_name": service_name}
        if reason:
            details["reason"] = reason
            
        super().__init__(message, ErrorCode.SERVICE_UNAVAILABLE, details)


class FileProcessingError(StreamWorksException):
    """File processing error"""
    def __init__(self, filename: str, operation: str, reason: str):
        message = f"Failed to {operation} file '{filename}': {reason}"
        details = {
            "filename": filename,
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, ErrorCode.FILE_PROCESSING_ERROR, details)


class LLMServiceError(StreamWorksException):
    """LLM service error"""
    def __init__(self, model: str, operation: str, reason: str):
        message = f"LLM operation '{operation}' failed for model '{model}': {reason}"
        details = {
            "model": model,
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, ErrorCode.LLM_SERVICE_ERROR, details)


class DatabaseError(StreamWorksException):
    """Database operation error"""
    def __init__(self, operation: str, table: Optional[str] = None, reason: Optional[str] = None):
        message = f"Database operation '{operation}' failed"
        if table:
            message += f" on table '{table}'"
        if reason:
            message += f": {reason}"
        
        details = {"operation": operation}
        if table:
            details["table"] = table
        if reason:
            details["reason"] = reason
            
        super().__init__(message, ErrorCode.DATABASE_ERROR, details)


# HTTP Exception Mapping

def map_to_http_exception(error: StreamWorksException) -> HTTPException:
    """Map StreamWorks exceptions to HTTP exceptions"""
    
    # Define error code to HTTP status mapping
    status_mapping = {
        # System errors -> 500
        ErrorCode.SYSTEM_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.CONFIGURATION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.INITIALIZATION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # Auth errors -> 401/403
        ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
        
        # Validation errors -> 400
        ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_INPUT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.MISSING_PARAMETER: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_FORMAT: status.HTTP_400_BAD_REQUEST,
        
        # Resource errors -> 404/409/429
        ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.RESOURCE_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_LOCKED: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_QUOTA_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        
        # Database errors -> 500
        ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.DATABASE_CONNECTION_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.DATABASE_TRANSACTION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # File operations -> 400/404/413
        ErrorCode.FILE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.FILE_PERMISSION_ERROR: status.HTTP_403_FORBIDDEN,
        ErrorCode.FILE_SIZE_EXCEEDED: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ErrorCode.FILE_FORMAT_UNSUPPORTED: status.HTTP_400_BAD_REQUEST,
        ErrorCode.FILE_PROCESSING_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # LLM/AI operations -> 500/503/429
        ErrorCode.LLM_SERVICE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.LLM_TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
        ErrorCode.LLM_RATE_LIMIT: status.HTTP_429_TOO_MANY_REQUESTS,
        ErrorCode.EMBEDDING_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # RAG operations -> 500
        ErrorCode.RAG_SEARCH_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.VECTOR_DB_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.INDEXING_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # Business logic -> 400/422
        ErrorCode.OPERATION_NOT_ALLOWED: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.WORKFLOW_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.PROCESSING_FAILED: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    http_status = status_mapping.get(error.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=http_status,
        detail=error.to_dict()
    )


# Error Handler Decorator

def handle_service_errors(operation: str, service_name: str = "Unknown"):
    """Decorator to handle service errors consistently"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except StreamWorksException:
                # Re-raise StreamWorks exceptions as-is
                raise
            except ValueError as e:
                raise ValidationError(f"Invalid value in {operation}: {str(e)}")
            except FileNotFoundError as e:
                raise ResourceNotFoundError("File", str(e))
            except PermissionError as e:
                raise FileProcessingError("unknown", operation, f"Permission denied: {str(e)}")
            except ConnectionError as e:
                raise ServiceUnavailableError(service_name, f"Connection error: {str(e)}")
            except TimeoutError as e:
                raise ServiceUnavailableError(service_name, f"Timeout: {str(e)}")
            except Exception as e:
                logger.exception(f"Unexpected error in {operation}")
                raise StreamWorksException(
                    message=f"Unexpected error in {operation}: {str(e)}",
                    error_code=ErrorCode.SYSTEM_ERROR,
                    original_error=e
                )
        
        return wrapper
    return decorator


# Global Error Response Format

class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create(
        error_code: Union[ErrorCode, str],
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        
        if isinstance(error_code, ErrorCode):
            error_code = error_code.value
        
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": None,  # Will be set by middleware
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        if request_id:
            response["error"]["request_id"] = request_id
        
        return response
    
    @staticmethod
    def from_exception(error: StreamWorksException, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Create error response from exception"""
        return ErrorResponse.create(
            error_code=error.error_code,
            message=error.message,
            details=error.details,
            request_id=request_id
        )