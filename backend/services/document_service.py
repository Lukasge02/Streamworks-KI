"""
Document Service (Legacy Compatibility)
Re-exports the modularized DocumentService from the document package
"""

# Import the service from the new modular structure
from .document import DocumentService

# Make the service available for import
__all__ = ["DocumentService"]