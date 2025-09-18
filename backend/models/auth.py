"""
Auth Models for Streamworks-KI RBAC System
User, Company, and Session models with enterprise-grade features
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, INET
from sqlalchemy.orm import relationship
from enum import Enum

from models.core import Base


class UserRole(str, Enum):
    """User roles for RBAC system"""
    OWNER = "owner"
    STREAMWORKS_ADMIN = "streamworks_admin"
    KUNDE = "kunde"

    @property
    def german_label(self) -> str:
        """German label for UI display"""
        labels = {
            "owner": "System-Eigentümer",
            "streamworks_admin": "Streamworks Admin",
            "kunde": "Kunde"
        }
        return labels.get(self.value, self.value)

    @property
    def hierarchy_level(self) -> int:
        """Hierarchy level for permission checks (higher = more permissions)"""
        levels = {
            "owner": 100,
            "streamworks_admin": 50,
            "kunde": 10
        }
        return levels.get(self.value, 0)


class Company(Base):
    """
    Company/Tenant model for multi-tenant architecture
    Each company has its own data isolation
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True, unique=True)

    # Settings and metadata
    settings = Column(JSONB, nullable=False, default=dict)
    created_by_owner = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="company", foreign_keys="[User.company_id]")
    created_by = relationship("User", foreign_keys=[created_by_owner], post_update=True)

    # Related entities (will be added when extending existing models)
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="company", cascade="all, delete-orphan")
    xml_streams = relationship("XMLStream", back_populates="company", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="company", cascade="all, delete-orphan")
    chat_xml_sessions = relationship("ChatXMLSession", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', domain='{self.domain}')>"

    @property
    def display_name(self) -> str:
        """Display name for UI"""
        return self.name

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "domain": self.domain,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class User(Base):
    """
    User model with RBAC support
    Supports three-tier role hierarchy: owner, streamworks_admin, kunde
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.KUNDE.value, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=True, index=True)

    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'streamworks_admin', 'kunde')", name='check_user_role'),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='check_email_format'),
    )

    # Relationships
    company = relationship("Company", back_populates="users", foreign_keys=[company_id])
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # Related entities (will be added when extending existing models)
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="user", cascade="all, delete-orphan")
    xml_streams = relationship("XMLStream", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def full_name(self) -> str:
        """Full name for display"""
        return f"{self.first_name} {self.last_name}"

    @property
    def role_enum(self) -> UserRole:
        """Get role as enum"""
        return UserRole(self.role)

    @property
    def role_display_name(self) -> str:
        """German role name for UI"""
        return self.role_enum.german_label

    @property
    def hierarchy_level(self) -> int:
        """Role hierarchy level for permission checks"""
        return self.role_enum.hierarchy_level

    def has_role(self, required_role: str) -> bool:
        """Check if user has required role or higher"""
        required_level = UserRole(required_role).hierarchy_level
        return self.hierarchy_level >= required_level

    def can_manage_user(self, target_user: 'User') -> bool:
        """Check if this user can manage target user"""
        # Owner can manage everyone
        if self.role == UserRole.OWNER.value:
            return True

        # Streamworks Admin can manage customers in their companies
        if self.role == UserRole.STREAMWORKS_ADMIN.value:
            return (
                target_user.role == UserRole.KUNDE.value and
                target_user.company_id == self.company_id
            )

        # Customers can only manage themselves
        return self.id == target_user.id

    def can_access_company(self, company_id: str) -> bool:
        """Check if user can access data from specific company"""
        # Owner can access all companies
        if self.role == UserRole.OWNER.value:
            return True

        # Other roles can only access their own company
        return str(self.company_id) == company_id

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary for API responses"""
        data = {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "role_display_name": self.role_display_name,
            "company_id": str(self.company_id) if self.company_id else None,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        if include_sensitive:
            data.update({
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "hierarchy_level": self.hierarchy_level
            })

        return data


class UserSession(Base):
    """
    User session model for JWT token tracking
    Optional - can be used for token blacklisting and session management
    """
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    jwt_token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    # Security metadata
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"

    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)

    @property
    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)"""
        return not self.is_expired and not self.is_revoked

    def revoke(self):
        """Revoke this session"""
        self.is_revoked = True

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "is_revoked": self.is_revoked,
            "is_expired": self.is_expired,
            "is_valid": self.is_valid
        }


# Export models for easy importing
__all__ = [
    "UserRole",
    "User",
    "Company",
    "UserSession"
]