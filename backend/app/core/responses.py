"""
Standardized API Response System for StreamWorks-KI
Provides consistent response formats across all endpoints
"""
from typing import Any, Dict, Optional, List, Union, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid

T = TypeVar('T')


class ResponseStatus(str, Enum):
    """Response status types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")
    
    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> 'PaginationInfo':
        """Create pagination info from basic parameters"""
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
        
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class MetaInfo(BaseModel):
    """Response metadata"""
    request_id: str = Field(description="Unique request identifier")
    timestamp: datetime = Field(description="Response timestamp")
    version: str = Field(default="2.0", description="API version")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    @classmethod
    def create(cls, request_id: Optional[str] = None, processing_time_ms: Optional[int] = None) -> 'MetaInfo':
        """Create meta info with default values"""
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=processing_time_ms
        )


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    status: ResponseStatus = Field(description="Response status")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: Optional[T] = Field(None, description="Response data")
    meta: MetaInfo = Field(description="Response metadata")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standardized error response"""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Response status")
    message: str = Field(description="Main error message")
    errors: List[ErrorDetail] = Field(description="Detailed error information")
    meta: MetaInfo = Field(description="Response metadata")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# Response Builder Classes

class ResponseBuilder:
    """Builder for creating standardized API responses"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        pagination: Optional[PaginationInfo] = None,
        warnings: Optional[List[str]] = None
    ) -> ApiResponse:
        """Create a success response"""
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            message=message or "Operation completed successfully",
            data=data,
            meta=MetaInfo.create(request_id, processing_time_ms),
            pagination=pagination,
            warnings=warnings
        )
    
    @staticmethod
    def error(
        message: str,
        errors: Optional[List[ErrorDetail]] = None,
        request_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> ErrorResponse:
        """Create an error response"""
        
        return ErrorResponse(
            status=ResponseStatus.ERROR,
            message=message,
            errors=errors or [],
            meta=MetaInfo.create(request_id, processing_time_ms)
        )
    
    @staticmethod
    def partial(
        data: Any,
        message: str,
        warnings: List[str],
        request_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> ApiResponse:
        """Create a partial success response"""
        
        return ApiResponse(
            status=ResponseStatus.PARTIAL,
            message=message,
            data=data,
            meta=MetaInfo.create(request_id, processing_time_ms),
            warnings=warnings
        )
    
    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        page_size: int,
        total_items: int,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> ApiResponse:
        """Create a paginated response"""
        
        pagination = PaginationInfo.create(page, page_size, total_items)
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            message=message or f"Retrieved {len(data)} items",
            data=data,
            meta=MetaInfo.create(request_id, processing_time_ms),
            pagination=pagination
        )


# Specific Response Models

class HealthCheckResponse(BaseModel):
    """Health check response"""
    service: str = Field(description="Service name")
    status: str = Field(description="Service status")
    version: str = Field(description="Service version")
    uptime_seconds: float = Field(description="Service uptime in seconds")
    checks: Dict[str, Any] = Field(description="Individual health checks")
    timestamp: datetime = Field(description="Health check timestamp")
    
    @classmethod
    def create(
        cls,
        service: str,
        status: str,
        version: str,
        uptime_seconds: float,
        checks: Dict[str, Any]
    ) -> 'HealthCheckResponse':
        """Create health check response"""
        return cls(
            service=service,
            status=status,
            version=version,
            uptime_seconds=uptime_seconds,
            checks=checks,
            timestamp=datetime.now(timezone.utc)
        )


class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str = Field(description="Unique file identifier")
    filename: str = Field(description="Original filename")
    file_size: int = Field(description="File size in bytes")
    content_type: str = Field(description="File content type")
    status: str = Field(description="Upload status")
    processing_info: Optional[Dict[str, Any]] = Field(None, description="Processing information")


class ProcessingJobResponse(BaseModel):
    """Processing job response"""
    job_id: str = Field(description="Job identifier")
    job_type: str = Field(description="Type of processing job")
    status: str = Field(description="Job status")
    progress_percentage: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result data")


class ChatResponse(BaseModel):
    """Chat/Q&A response"""
    response: str = Field(description="Generated response text")
    mode_used: str = Field(description="Processing mode used")
    processing_time: float = Field(description="Processing time in seconds")
    sources: Optional[List[str]] = Field(None, description="Source documents used")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="Citation information")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Search results response"""
    query: str = Field(description="Original search query")
    results: List[Dict[str, Any]] = Field(description="Search results")
    total_results: int = Field(description="Total number of results")
    search_time_ms: int = Field(description="Search time in milliseconds")
    search_strategy: Optional[str] = Field(None, description="Search strategy used")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")


# Response Validation

class ResponseValidator:
    """Validates response objects before sending"""
    
    @staticmethod
    def validate_response(response: Union[ApiResponse, ErrorResponse]) -> bool:
        """Validate response structure"""
        try:
            # Basic validation - Pydantic handles most of this
            if isinstance(response, ApiResponse):
                # Ensure meta is present
                if not response.meta:
                    return False
                
                # Validate pagination if present
                if response.pagination:
                    if response.pagination.page < 1:
                        return False
                    if response.pagination.page_size < 1:
                        return False
                
            elif isinstance(response, ErrorResponse):
                # Ensure error response has required fields
                if not response.message:
                    return False
                if not response.meta:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def sanitize_data(data: Any) -> Any:
        """Sanitize data before including in response"""
        if isinstance(data, dict):
            # Remove any keys that start with underscore (private fields)
            return {k: ResponseValidator.sanitize_data(v) for k, v in data.items() if not k.startswith('_')}
        elif isinstance(data, list):
            return [ResponseValidator.sanitize_data(item) for item in data]
        else:
            return data


# Response Middleware Helpers

def create_success_response(
    data: Any = None,
    message: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Helper function for creating success responses"""
    response = ResponseBuilder.success(data=data, message=message, **kwargs)
    return response.dict()


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Helper function for creating error responses"""
    errors = []
    if error_code or details:
        errors.append(ErrorDetail(
            code=error_code or "UNKNOWN_ERROR",
            message=message,
            details=details
        ))
    
    response = ResponseBuilder.error(message=message, errors=errors, **kwargs)
    return response.dict()


def create_paginated_response(
    data: List[Any],
    page: int = 1,
    page_size: int = 20,
    total_items: int = 0,
    **kwargs
) -> Dict[str, Any]:
    """Helper function for creating paginated responses"""
    response = ResponseBuilder.paginated(
        data=data,
        page=page,
        page_size=page_size,
        total_items=total_items,
        **kwargs
    )
    return response.dict()