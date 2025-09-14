"""
Pydantic Schemas für XML Stream API
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class JobType(str, Enum):
    """Job types for XML streams"""
    STANDARD = "standard"
    SAP = "sap"
    FILE_TRANSFER = "file_transfer"
    CUSTOM = "custom"


class StreamStatus(str, Enum):
    """Stream status options for workflow"""
    DRAFT = "draft"                    # Entwurf - User arbeitet daran
    ZUR_FREIGABE = "zur_freigabe"      # Zur Freigabe - User hat eingereicht
    FREIGEGEBEN = "freigegeben"        # Freigegeben - Experte hat genehmigt
    ABGELEHNT = "abgelehnt"           # Abgelehnt - Experte hat abgelehnt
    PUBLISHED = "published"            # Veröffentlicht - Live/Produktiv


class ChatEntityExtractionRequest(BaseModel):
    """Request schema for chat entity extraction"""
    message: str = Field(..., description="User message to extract entities from")
    conversation_context: Optional[List[Dict[str, Any]]] = Field(default=None, description="Previous conversation context")
    current_wizard_data: Optional[Dict[str, Any]] = Field(default=None, description="Current wizard data state")

class ConversationState(BaseModel):
    """Current state of the conversation"""
    job_type: Optional[JobType] = Field(default=None, description="Detected job type")
    collected_fields: List[str] = Field(default=[], description="Fields that have been collected")
    missing_required_fields: List[str] = Field(default=[], description="Required fields still missing")
    current_step: str = Field(default="job_type_detection", description="Current conversation step")
    completion_percentage: float = Field(default=0.0, description="How complete is the configuration")

class ChatEntityExtractionResponse(BaseModel):
    """Response schema for chat entity extraction"""
    extracted_entities: Optional[Dict[str, Any]] = Field(default=None, description="Extracted wizard data")
    suggested_job_type: Optional[JobType] = Field(default=None, description="Suggested job type")
    bot_response: str = Field(..., description="Bot response to user")
    confidence_score: float = Field(default=0.0, description="Confidence score for extraction")
    requires_clarification: bool = Field(default=False, description="Whether clarification is needed")
    conversation_state: Optional[ConversationState] = Field(default=None, description="Current conversation state")
    next_suggested_questions: List[str] = Field(default=[], description="Suggested follow-up questions")

class StreamSortBy(str, Enum):
    """Sorting options for stream lists"""
    UPDATED_DESC = "updated_desc"
    UPDATED_ASC = "updated_asc"
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    FAVORITES_FIRST = "favorites_first"


# Base schemas
class XMLStreamBase(BaseModel):
    """Base schema for XML streams"""
    stream_name: str = Field(..., min_length=1, max_length=255, description="Name of the XML stream")
    description: Optional[str] = Field(None, description="Description of the stream")
    xml_content: Optional[str] = Field(None, description="Generated XML content")
    wizard_data: Optional[Dict[str, Any]] = Field(None, description="Wizard form data")
    job_type: Optional[JobType] = Field(None, description="Type of job")
    status: StreamStatus = Field(StreamStatus.DRAFT, description="Stream status")
    tags: Optional[List[str]] = Field(default_factory=list, description="Stream tags")
    is_favorite: bool = Field(False, description="Whether stream is favorited")

    @validator('stream_name')
    def validate_stream_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Stream name cannot be empty')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [tag.strip() for tag in v if tag.strip()]
        return []


class XMLStreamCreate(XMLStreamBase):
    """Schema for creating XML streams"""
    pass


class XMLStreamUpdate(BaseModel):
    """Schema for updating XML streams"""
    stream_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    xml_content: Optional[str] = None
    wizard_data: Optional[Dict[str, Any]] = None
    job_type: Optional[JobType] = None
    status: Optional[StreamStatus] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

    @validator('stream_name')
    def validate_stream_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Stream name cannot be empty')
        return v.strip() if v else v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [tag.strip() for tag in v if tag.strip()]
        return v


class XMLStreamResponse(XMLStreamBase):
    """Schema for XML stream responses"""
    id: UUID
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_generated_at: Optional[datetime] = None
    version: int
    template_id: Optional[UUID] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object"""
        return cls(
            id=obj.id,
            stream_name=obj.stream_name,
            description=obj.description,
            xml_content=obj.xml_content,
            wizard_data=obj.wizard_data,
            job_type=obj.job_type,
            status=obj.status,
            created_by=obj.created_by,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            last_generated_at=obj.last_generated_at,
            tags=obj.tags or [],
            is_favorite=obj.is_favorite,
            version=obj.version,
            template_id=obj.template_id
        )


class XMLStreamListResponse(BaseModel):
    """Schema for paginated stream lists"""
    streams: List[XMLStreamResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool


class StreamFilters(BaseModel):
    """Schema for filtering streams"""
    search: Optional[str] = Field(None, description="Search term for name/description")
    job_types: Optional[List[JobType]] = Field(None, description="Filter by job types")
    statuses: Optional[List[StreamStatus]] = Field(None, description="Filter by statuses")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (AND operation)")
    is_favorite: Optional[bool] = Field(None, description="Filter by favorite status")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")


class StreamVersionResponse(BaseModel):
    """Schema for stream version responses"""
    id: UUID
    stream_id: UUID
    version: int
    wizard_data: Optional[Dict[str, Any]] = None
    xml_content: Optional[str] = None
    changes_description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class AutoSaveRequest(BaseModel):
    """Schema for auto-save requests"""
    wizard_data: Optional[Dict[str, Any]] = None
    xml_content: Optional[str] = None


class DuplicateStreamRequest(BaseModel):
    """Schema for stream duplication requests"""
    new_name: Optional[str] = Field(None, description="Name for the duplicated stream")


class BulkActionRequest(BaseModel):
    """Schema for bulk actions on streams"""
    stream_ids: List[UUID] = Field(..., description="List of stream IDs")
    action: str = Field(..., description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")


class StreamStatsResponse(BaseModel):
    """Schema for stream statistics"""
    total_streams: int
    draft_streams: int
    complete_streams: int
    published_streams: int
    favorite_streams: int
    recent_streams: int  # Streams updated in last 7 days
    job_type_distribution: Dict[str, int]
    
    
class ExportStreamResponse(BaseModel):
    """Schema for stream export responses"""
    stream_id: UUID
    export_format: str
    file_name: str
    content: str
    created_at: datetime