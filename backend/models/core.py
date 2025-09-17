"""
Core Database Models for StreamWorks Document Management
Enterprise-grade SQLAlchemy models with Supabase integration
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, BigInteger, ForeignKey, Enum as SQLEnum, Boolean, ARRAY, Integer, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum

Base = declarative_base()


class DocumentStatus(str, Enum):
    """Document processing status with German labels"""
    UPLOADED = "uploaded"        # Hochgeladen
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
            "uploaded": "Hochgeladen",
            "uploading": "Wird hochgeladen",
            "analyzing": "Wird analysiert",
            "processing": "Wird verarbeitet",
            "ready": "Bereit",
            "skipped": "Übersprungen",
            "error": "Fehler"
        }
        return labels.get(self.value, self.value)


class XMLStreamStatus(str, Enum):
    """XML Stream processing status with German labels"""
    DRAFT = "draft"                    # Entwurf
    ZUR_FREIGABE = "zur_freigabe"     # Zur Freigabe
    FREIGEGEBEN = "freigegeben"       # Freigegeben
    ABGELEHNT = "abgelehnt"           # Abgelehnt
    PUBLISHED = "published"           # Veröffentlicht
    COMPLETE = "complete"             # Vollständig (legacy)

    @property
    def german_label(self) -> str:
        """German label for UI display"""
        labels = {
            "draft": "Entwurf",
            "zur_freigabe": "Zur Freigabe",
            "freigegeben": "Freigegeben",
            "abgelehnt": "Abgelehnt",
            "published": "Veröffentlicht",
            "complete": "Vollständig"
        }
        return labels.get(self.value, self.value)


class JobType(str, Enum):
    """Job types for XML streams"""
    STANDARD = "standard"
    SAP = "sap"
    FILE_TRANSFER = "file_transfer"
    CUSTOM = "custom"


class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"




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
    status = Column(ENUM('uploaded', 'uploading', 'analyzing', 'processing', 'ready', 'skipped', 'error', name='documentstatus'), default=DocumentStatus.UPLOADING.value, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # AI Summary Caching
    ai_summary = Column(Text, nullable=True)
    summary_key_points = Column(JSONB, nullable=True)
    summary_generated_at = Column(DateTime, nullable=True)
    
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
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', folder_id={self.folder_id})>"


class XMLStream(Base):
    """
    XML Stream configuration for Streamworks
    Enterprise-grade stream management with versioning and workflow
    """
    __tablename__ = "xml_streams"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Basic stream information
    stream_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # XML and wizard data
    xml_content = Column(Text, nullable=True)
    wizard_data = Column(JSONB, nullable=True, default=dict)

    # Stream configuration
    job_type = Column(String(50), nullable=True, default="standard")
    status = Column(String(50), nullable=False, default="draft", index=True)

    # User and workflow
    created_by = Column(String(100), nullable=False, default="system")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_generated_at = Column(DateTime, nullable=True)

    # Metadata and organization
    tags = Column(ARRAY(String), nullable=False, default=list)
    is_favorite = Column(Boolean, default=False, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<XMLStream(id={self.id}, stream_name='{self.stream_name}', status='{self.status}')>"


class ChatSession(Base):
    """
    Chat session for conversational AI interactions
    Enterprise-grade session management with RAG configuration
    """
    __tablename__ = "chat_sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Session metadata
    title = Column(Text, nullable=False)
    user_id = Column(Text, nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), nullable=True, default=uuid.UUID('00000000-0000-0000-0000-000000000001'))

    # Session statistics
    message_count = Column(Integer, default=0, nullable=False)

    # RAG and filtering configuration
    rag_config = Column(JSONB, default=dict, nullable=False)
    context_filters = Column(JSONB, default=dict, nullable=False)

    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Timestamps with timezone
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}', user_id='{self.user_id}')>"


class ChatMessage(Base):
    """
    Individual chat message within a session
    Supports AI responses with metadata and source tracking
    """
    __tablename__ = "chat_messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Session relationship
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Text, nullable=False)

    # Message content
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    # AI response metadata
    confidence_score = Column(Numeric(precision=3, scale=2), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    sources = Column(JSONB, default=list, nullable=False)
    model_used = Column(Text, nullable=True)

    # Message ordering and timestamps
    sequence_number = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Add constraints
    __table_args__ = (
        CheckConstraint('role IN (\'user\', \'assistant\', \'system\')', name='check_message_role'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score_range'),
        CheckConstraint('processing_time_ms >= 0', name='check_processing_time_positive'),
    )

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}')>"


class ChatXMLSession(Base):
    """
    Chat-to-XML session for AI-powered parameter collection
    Enterprise-grade session management with parameter history
    """
    __tablename__ = "chat_xml_sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Session metadata
    session_name = Column(String(255), nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    job_type = Column(String(50), nullable=False, index=True)  # STANDARD, SAP, FILE_TRANSFER, CUSTOM

    # Session status and workflow
    status = Column(String(50), nullable=False, default="PARAMETER_COLLECTION", index=True)
    completion_percentage = Column(Numeric(precision=5, scale=2), default=0.0, nullable=False)

    # Parameter tracking with JSON storage
    collected_parameters = Column(JSONB, default=dict, nullable=False)
    parameter_history = Column(JSONB, default=list, nullable=False)  # Track all parameter changes
    validation_errors = Column(JSONB, default=list, nullable=False)

    # AI extraction quality metrics
    ai_extraction_metadata = Column(JSONB, default=dict, nullable=False)  # Quality scores, confidence, etc.

    # XML generation results
    generated_xml = Column(Text, nullable=True)
    xml_generation_metadata = Column(JSONB, default=dict, nullable=False)

    # Session lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Session management
    is_active = Column(Boolean, default=True, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    # Relationships
    xml_messages = relationship("ChatXMLMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatXMLSession(id={self.id}, job_type='{self.job_type}', status='{self.status}')>"


class ChatXMLMessage(Base):
    """
    Individual message in Chat-to-XML conversation
    Enhanced with parameter extraction metadata and AI intelligence
    """
    __tablename__ = "chat_xml_messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Session relationship
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_xml_sessions.id', ondelete='CASCADE'), nullable=False)

    # Message content and type
    message_type = Column(String(50), nullable=False)  # user_message, system_prompt, parameter_request, etc.
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system

    # Parameter extraction results
    extracted_parameters = Column(JSONB, default=dict, nullable=False)
    parameter_confidence_scores = Column(JSONB, default=dict, nullable=False)
    extraction_method = Column(String(50), nullable=True)  # openai_precise, openai_balanced, fallback_rules

    # AI processing metadata
    ai_processing_metadata = Column(JSONB, default=dict, nullable=False)
    suggestions = Column(JSONB, default=list, nullable=False)
    validation_errors = Column(JSONB, default=list, nullable=False)

    # Quality metrics
    precision_score = Column(Numeric(precision=3, scale=2), nullable=True)
    completeness_score = Column(Numeric(precision=3, scale=2), nullable=True)
    consistency_score = Column(Numeric(precision=3, scale=2), nullable=True)

    # Message context
    parameter_name = Column(String(100), nullable=True)  # If message targets specific parameter
    processing_time_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Add constraints
    __table_args__ = (
        CheckConstraint('role IN (\'user\', \'assistant\', \'system\')', name='check_xml_message_role'),
        CheckConstraint('precision_score >= 0 AND precision_score <= 1', name='check_precision_score_range'),
        CheckConstraint('completeness_score >= 0 AND completeness_score <= 1', name='check_completeness_score_range'),
        CheckConstraint('consistency_score >= 0 AND consistency_score <= 1', name='check_consistency_score_range'),
        CheckConstraint('processing_time_ms >= 0', name='check_xml_processing_time_positive'),
    )

    # Relationships
    session = relationship("ChatXMLSession", back_populates="xml_messages")

    def __repr__(self):
        return f"<ChatXMLMessage(id={self.id}, session_id={self.session_id}, message_type='{self.message_type}')>"


# Export models for easy importing
__all__ = ["Base", "Folder", "Document", "DocumentStatus", "XMLStream", "XMLStreamStatus", "JobType", "MessageRole", "ChatSession", "ChatMessage", "ChatXMLSession", "ChatXMLMessage"]