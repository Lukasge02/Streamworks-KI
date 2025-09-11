"""
Document Management API Router Package
Re-exports the combined router from all document sub-modules
"""

from fastapi import APIRouter

# Import all sub-routers
from .crud import router as crud_router
from .bulk_operations import router as bulk_router
from .chunks import router as chunks_router
from .analytics import router as analytics_router

# Create the main router with the same prefix and tags as the original
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# Include all sub-routers
router.include_router(crud_router)
router.include_router(bulk_router)
router.include_router(chunks_router)
router.include_router(analytics_router)

# Make the router available for import by main.py
__all__ = ["router"]