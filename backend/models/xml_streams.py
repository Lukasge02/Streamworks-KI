"""
SQLAlchemy Models für XML Stream Management
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, ARRAY, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

# Import Base from models.core to avoid circular import
from .core import Base


class StreamStatus(enum.Enum):
    """Stream workflow status enumeration"""
    DRAFT = "draft"                    # Entwurf - Initiale Erstellung
    IN_BEARBEITUNG = "in_bearbeitung"   # In Bearbeitung - Wird aktiv bearbeitet  
    ZUR_FREIGABE = "zur_freigabe"       # Zur Freigabe - Bereit für Review
    FREIGEGEBEN = "freigegeben"         # Freigegeben - Review abgeschlossen
    PUBLISHED = "published"             # Veröffentlicht - Live/Produktiv
    ARCHIVIERT = "archiviert"           # Archiviert - Nicht mehr aktiv
    
    @classmethod
    def get_display_name(cls, status_value: str) -> str:
        """Get German display name for status"""
        display_names = {
            cls.DRAFT.value: "Entwurf",
            cls.IN_BEARBEITUNG.value: "In Bearbeitung", 
            cls.ZUR_FREIGABE.value: "Zur Freigabe",
            cls.FREIGEGEBEN.value: "Freigegeben",
            cls.PUBLISHED.value: "Veröffentlicht",
            cls.ARCHIVIERT.value: "Archiviert"
        }
        return display_names.get(status_value, "Unbekannt")


class XMLStream(Base):
    """XML Stream Model - Represents a saved XML stream configuration"""
    
    __tablename__ = "xml_streams"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    stream_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    xml_content = Column(Text)
    wizard_data = Column(JSONB)
    job_type = Column(String(50), index=True)  # STANDARD, SAP, FILE_TRANSFER
    status = Column(String(50), default="in_bearbeitung", index=True)
    created_by = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    last_generated_at = Column(DateTime(timezone=True))
    tags = Column(ARRAY(String))
    is_favorite = Column(Boolean, default=False, index=True)
    version = Column(Integer, default=1)
    template_id = Column(PG_UUID(as_uuid=True))
    
    # Relationships
    versions = relationship("StreamVersion", back_populates="stream", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<XMLStream(id={self.id}, name={self.stream_name}, type={self.job_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "stream_name": self.stream_name,
            "description": self.description,
            "xml_content": self.xml_content,
            "wizard_data": self.wizard_data,
            "job_type": self.job_type,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_generated_at": self.last_generated_at.isoformat() if self.last_generated_at else None,
            "tags": self.tags,
            "is_favorite": self.is_favorite,
            "version": self.version,
            "template_id": str(self.template_id) if self.template_id else None
        }


class StreamVersion(Base):
    """Stream Version Model - Represents versions of XML stream configurations"""
    
    __tablename__ = "stream_versions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    stream_id = Column(PG_UUID(as_uuid=True), ForeignKey("xml_streams.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    wizard_data = Column(JSONB)
    xml_content = Column(Text)
    changes_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stream = relationship("XMLStream", back_populates="versions")
    
    def __repr__(self) -> str:
        return f"<StreamVersion(id={self.id}, stream_id={self.stream_id}, version={self.version})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "stream_id": str(self.stream_id),
            "version": self.version,
            "wizard_data": self.wizard_data,
            "xml_content": self.xml_content,
            "changes_description": self.changes_description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }