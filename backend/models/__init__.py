"""
Models Package for Streamworks Backend
Exports all database models including RBAC auth models
"""

from .core import (
    Base,
    DocumentStatus,
    XMLStreamStatus,
    JobType,
    MessageRole,
    Folder,
    Document,
    XMLStream,
    ChatSession,
    ChatMessage,
    ChatXMLSession,
    ChatXMLMessage
)

from .auth import (
    UserRole,
    User,
    Company,
    UserSession
)

__all__ = [
    # Core models
    "Base",
    "DocumentStatus",
    "XMLStreamStatus",
    "JobType",
    "MessageRole",
    "Folder",
    "Document",
    "XMLStream",
    "ChatSession",
    "ChatMessage",
    "ChatXMLSession",
    "ChatXMLMessage",

    # Auth models
    "UserRole",
    "User",
    "Company",
    "UserSession"
]