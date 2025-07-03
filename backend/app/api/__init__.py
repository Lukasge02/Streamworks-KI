# backend/app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1 import chat, streams, training

# Create main API router
router = APIRouter()

# Include all sub-routers
router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

router.include_router(
    streams.router,
    prefix="/streams", 
    tags=["streams"]
)

router.include_router(
    training.router,
    prefix="/training",
    tags=["training"]
)

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