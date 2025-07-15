# backend/app/api/v1/__init__.py
from fastapi import APIRouter

# Create main API router
router = APIRouter()

@router.get("/status")
async def api_status():
    """API Status endpoint"""
    return {
        "status": "operational",
        "endpoints": {
            "chat": "/chat",
            "streams": "/streams", 
            "training": "/training"
        },
        "version": "1.0.0"
    }