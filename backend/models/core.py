"""
Core Database Models for StreamWorks Document Management
Enterprise-grade SQLAlchemy models with Supabase integration
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, BigInteger, ForeignKey, Enum as SQLEnum, Boolean, ARRAY, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum

Base = declarative_base()


class DocumentStatus(str, Enum):
    """Document processing status with German labels"""
    UPLOADING = "uploading"      # Wird hochgeladen
    ANALYZING = "analyzing"      # Wird analysiert  
    PROCESSING = "processing"    # Wird verarbeitet
    READY = "ready"             # Bereit
    SKIPPED = "skipped"         # Übersprungen
    ERROR = "error"             # Fehler
    
    @property
    def german_label(self) -> str:
        """German label for UI display"""
        labels = {
            "uploading": "Wird hochgeladen",
            "analyzing": "Wird analysiert", 
            "processing": "Wird verarbeitet",
            "ready": "Bereit",
            "skipped": "Übersprungen", 
            "error": "Fehler"
        }
        return labels.get(self.value, self.value)


class ChunkType(str, Enum):
    """Document chunk content type"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CODE = "code"


class Folder(Base):
    """
    Hierarchical folder structure for document organization
    Supports nested folders with efficient path queries
    """
    __tablename__ = "folders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('folders.id'), nullable=True)
    path = Column(ARRAY(String), nullable=False, default=list)  # For efficient hierarchy queries
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Multi-user support (for future)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    parent = relationship("Folder", remote_side=[id])
    children = relationship("Folder", back_populates="parent")
    documents = relationship("Document", back_populates="folder")
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', path={self.path})>"


class Document(Base):
    """
    Document metadata with required folder association
    Enterprise-grade tracking with file integrity and audit trail
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    
    # Required folder association
    folder_id = Column(UUID(as_uuid=True), ForeignKey('folders.id', ondelete='CASCADE'), nullable=False)
    
    # File metadata
    file_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_path = Column(String(500), nullable=False)  # Physical file path
    
    # Processing status
    status = Column(ENUM('uploading', 'analyzing', 'processing', 'ready', 'skipped', 'error', name='documentstatus'), default=DocumentStatus.UPLOADING.value, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Multi-user support (for future)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Search and categorization
    tags = Column(ARRAY(String), nullable=False, default=list)
    description = Column(Text, nullable=True)
    
    # Processing metadata for Docling
    chunk_count = Column(Integer, default=0, nullable=False)
    processing_metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    folder = relationship("Folder", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', folder_id={self.folder_id})>"


class DocumentChunk(Base):
    """
    Document chunks from Docling processing
    Structured content with layout-aware metadata and cascade deletion
    """
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    
    # Chunk ordering and content
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    # Layout-aware metadata
    heading = Column(Text, nullable=True)
    section_name = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    chunk_type = Column(SQLEnum(ChunkType), default=ChunkType.TEXT, nullable=False)
    
    # Processing metadata and analytics
    chunk_metadata = Column(JSONB, default=dict, nullable=False)
    word_count = Column(Integer, nullable=True)
    char_count = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index}, type={self.chunk_type})>"
    
    @property
    def content_preview(self) -> str:
        """Get a preview of the chunk content (first 100 chars)"""
        if not self.content:
            return ""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content


# Export models for easy importing
__all__ = ["Base", "Folder", "Document", "DocumentChunk", "DocumentStatus", "ChunkType"]