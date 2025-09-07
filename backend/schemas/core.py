"""
Pydantic Schemas for API Validation
Enterprise-grade request/response models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    READY = "ready"
    SKIPPED = "skipped"
    ERROR = "error"


# Folder Schemas
class FolderBase(BaseModel):
    """Base folder schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[UUID] = None


class FolderCreate(FolderBase):
    """Schema for creating folders"""
    pass


class FolderUpdate(BaseModel):
    """Schema for updating folders"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[UUID] = None


class FolderResponse(FolderBase):
    """Schema for folder responses"""
    id: UUID
    path: List[str]
    created_at: datetime
    updated_at: datetime
    document_count: int = 0  # Will be populated by service
    children_count: int = 0  # Will be populated by service
    
    class Config:
        from_attributes = True


class FolderTree(FolderResponse):
    """Schema for hierarchical folder tree"""
    children: List['FolderTree'] = []
    documents: List['DocumentResponse'] = []


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str = Field(..., min_length=1, max_length=255)
    folder_id: UUID
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(None, max_length=1000)


class DocumentCreate(DocumentBase):
    """Schema for document upload"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for document updates"""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    folder_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = Field(None, max_length=1000)


class DocumentResponse(DocumentBase):
    """Schema for document responses"""
    id: UUID
    original_filename: str
    file_hash: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentWithFolder(DocumentResponse):
    """Document response with folder information"""
    folder: FolderResponse


# Upload Schemas
class UploadResponse(BaseModel):
    """Response for successful upload"""
    document: DocumentResponse
    message: str
    upload_time: float  # seconds


class UploadError(BaseModel):
    """Response for upload errors"""
    error: str
    details: Optional[str] = None
    upload_id: Optional[str] = None


# List/Pagination Schemas
class FolderList(BaseModel):
    """Paginated folder list"""
    items: List[FolderResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class DocumentList(BaseModel):
    """Paginated document list"""
    items: List[DocumentWithFolder]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Statistics Schemas
class FolderStats(BaseModel):
    """Folder statistics"""
    total_folders: int
    max_depth: int
    folders_with_documents: int
    empty_folders: int


class DocumentStats(BaseModel):
    """Document statistics"""
    total_documents: int
    total_size_bytes: int
    documents_by_status: Dict[str, int]
    documents_by_mime_type: Dict[str, int]
    average_file_size: float


class SystemStats(BaseModel):
    """Overall system statistics"""
    folder_stats: FolderStats
    document_stats: DocumentStats
    last_updated: datetime


# Search/Filter Schemas
class DocumentFilter(BaseModel):
    """Document filtering options"""
    folder_id: Optional[UUID] = None
    status: Optional[DocumentStatus] = None
    mime_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None


class DocumentSort(str, Enum):
    """Document sorting options"""
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    SIZE_ASC = "size_asc"
    SIZE_DESC = "size_desc"


# Bulk Operations
class BulkDeleteRequest(BaseModel):
    """Bulk delete request"""
    document_ids: List[UUID] = Field(..., min_items=1)


class BulkDeleteResponse(BaseModel):
    """Bulk delete response"""
    deleted: List[UUID]
    failed: List[Dict[str, Any]]  # {id: UUID, error: str}
    total_requested: int
    total_deleted: int
    total_failed: int


class BulkMoveRequest(BaseModel):
    """Bulk move documents request"""
    document_ids: List[UUID] = Field(..., min_items=1)
    target_folder_id: UUID


class BulkMoveResponse(BaseModel):
    """Bulk move response"""
    moved: List[UUID]
    failed: List[Dict[str, Any]]
    total_requested: int
    total_moved: int
    total_failed: int


class BulkReprocessRequest(BaseModel):
    """Bulk reprocess documents request"""
    document_ids: List[UUID] = Field(..., min_items=1)


class BulkReprocessResponse(BaseModel):
    """Bulk reprocess response"""
    reprocessed: List[UUID]
    failed: List[Dict[str, Any]]
    total_requested: int
    total_reprocessed: int
    total_failed: int


# Forward reference updates
FolderTree.model_rebuild()
DocumentWithFolder.model_rebuild()