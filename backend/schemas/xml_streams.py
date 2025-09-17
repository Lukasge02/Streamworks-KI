"""
Pydantic schemas for XML Stream API
Request/Response models for XML stream operations
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from models.core import XMLStreamStatus, JobType


class StreamFilters(BaseModel):
    """Filters for stream list queries"""
    search: Optional[str] = None
    job_types: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class XMLStreamBase(BaseModel):
    """Base XML Stream model"""
    stream_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    xml_content: Optional[str] = None
    wizard_data: Optional[Dict[str, Any]] = None
    job_type: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = "system"
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = False
    template_id: Optional[Union[str, UUID]] = None


class XMLStreamCreate(XMLStreamBase):
    """Schema for creating XML streams"""
    pass


class XMLStreamUpdate(BaseModel):
    """Schema for updating XML streams"""
    stream_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    xml_content: Optional[str] = None
    wizard_data: Optional[Dict[str, Any]] = None
    job_type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    template_id: Optional[Union[str, UUID]] = None


class XMLStreamResponse(BaseModel):
    """Schema for XML stream responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    stream_name: str
    description: Optional[str]
    xml_content: Optional[str]
    wizard_data: Optional[Dict[str, Any]]
    job_type: Optional[str]
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_generated_at: Optional[datetime]
    tags: List[str] = []
    is_favorite: bool
    version: int
    template_id: Optional[UUID]


class XMLStreamListResponse(BaseModel):
    """Schema for paginated stream list responses"""
    streams: List[XMLStreamResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool


class BulkStreamOperation(BaseModel):
    """Schema for bulk operations on streams"""
    stream_ids: List[str] = Field(..., min_length=1)


class DuplicateStreamRequest(BaseModel):
    """Schema for stream duplication requests"""
    stream_id: str
    new_name: str = Field(..., min_length=1, max_length=255)


class StreamOperationResponse(BaseModel):
    """Schema for operation responses"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class StreamExportRequest(BaseModel):
    """Schema for stream export requests"""
    stream_id: str
    format: str = Field(default="xml", pattern="^(xml|json)$")


# Workflow-specific schemas
class StreamWorkflowUpdate(BaseModel):
    """Schema for workflow status updates"""
    status: str = Field(..., pattern="^(draft|zur_freigabe|freigegeben|abgelehnt|published)$")
    reason: Optional[str] = None  # Required for rejection


class StreamSubmitForReview(BaseModel):
    """Schema for submitting streams for review"""
    stream_id: str


class StreamApproval(BaseModel):
    """Schema for stream approval/rejection"""
    stream_id: str
    approved: bool
    reason: Optional[str] = None  # Required when approved=False


class StreamPublish(BaseModel):
    """Schema for publishing streams"""
    stream_id: str
    publish_notes: Optional[str] = None