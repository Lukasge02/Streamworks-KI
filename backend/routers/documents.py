"""
Document Management API Router (Legacy Compatibility)
Re-exports the modularized router from the documents package
"""

# Import the router from the new modular structure
from .documents import router

# Make the router available for import by main.py
__all__ = ["router"]