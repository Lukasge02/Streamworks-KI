"""
Document Service Package
Re-exports the main DocumentService for backward compatibility
"""

from .document_service import DocumentService

# Make DocumentService available for import
__all__ = ["DocumentService"]