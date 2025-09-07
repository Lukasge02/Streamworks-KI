"""
Unified Folder Management Models for Supabase Integration
Replaces file-system based folder management with database-backed solution
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database_supabase import Document
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FolderType(str, Enum):
    """Folder categories for organization"""
    FAQ = "faq"
    XML = "xml"
    MANUAL = "manual"
    API_DOCS = "api-docs"
    TRAINING = "training-docs"
    ARCHIVE = "archive"
    TEMP = "temp"

class FolderPermission(str, Enum):
    """Access levels for folders"""
    PUBLIC = "public"
    INTERNAL = "internal" 
    RESTRICTED = "restricted"
    ADMIN_ONLY = "admin-only"

# SQLAlchemy Models
class Folder(Base):
    """Database model for folder hierarchy"""
    __tablename__ = "folders"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    folder_type = Column(String(50), nullable=False, default=FolderType.FAQ.value)
    permission = Column(String(50), nullable=False, default=FolderPermission.INTERNAL.value)
    
    # Hierarchy
    parent_id = Column(String, ForeignKey("folders.id"), nullable=True)
    path = Column(String(1000), nullable=False)  # Materialized path for fast queries
    level = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System folders can't be deleted
    
    # Relationships
    parent = relationship("Folder", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_folder_path', 'path'),
        Index('idx_folder_parent', 'parent_id'),
        Index('idx_folder_type', 'folder_type'),
        Index('idx_folder_active', 'is_active'),
    )

class FolderStats(Base):
    """Cached statistics for folders"""
    __tablename__ = "folder_stats"
    
    folder_id = Column(String, ForeignKey("folders.id"), primary_key=True)
    document_count = Column(Integer, default=0, nullable=False)
    total_size_bytes = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    folder = relationship("Folder", backref="stats")

# Pydantic Models for API
class FolderBase(BaseModel):
    """Base folder model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    folder_type: FolderType = FolderType.FAQ
    permission: FolderPermission = FolderPermission.INTERNAL

class FolderCreate(FolderBase):
    """Create folder request"""
    parent_id: Optional[str] = None

class FolderUpdate(BaseModel):
    """Update folder request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    permission: Optional[FolderPermission] = None
    parent_id: Optional[str] = None

class FolderResponse(FolderBase):
    """Folder response model"""
    id: str
    path: str
    level: int
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool
    is_system: bool
    
    # Statistics
    document_count: int = 0
    total_size_bytes: int = 0
    last_activity: Optional[datetime] = None
    
    # Children for tree view
    children: List['FolderResponse'] = []

    class Config:
        from_attributes = True

class FolderTree(BaseModel):
    """Hierarchical folder tree structure"""
    folder: FolderResponse
    children: List['FolderTree'] = []
    expanded: bool = False

class FolderMoveRequest(BaseModel):
    """Move folder to new parent"""
    target_parent_id: Optional[str] = None
    
class BulkFolderOperation(BaseModel):
    """Bulk operations on folders"""
    folder_ids: List[str]
    operation: str  # 'delete', 'move', 'archive'
    target_parent_id: Optional[str] = None

# Enable forward references
FolderResponse.model_rebuild()
FolderTree.model_rebuild()