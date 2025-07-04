"""
XML Stream Generation API with LoRA Fine-Tuning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.services.xml_generator import xml_generator
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class StreamGenerationRequest(BaseModel):
    name: str
    description: Optional[str] = "Data processing stream"
    schedule: str = "daily"
    source: str = "/data/input"
    target: str = "/data/output"
    additional_config: Optional[Dict[str, Any]] = {}

class StreamGenerationResponse(BaseModel):
    xml_content: str
    generation_mode: str  # "lora", "base_model", "mock"
    is_fine_tuned: bool
    metadata: Dict[str, Any]

@router.post("/generate", response_model=StreamGenerationResponse)
async def generate_xml_stream(request: StreamGenerationRequest):
    """Generate XML Stream using LoRA fine-tuned model or mock"""
    try:
        logger.info(f"🔧 XML Generation Request für: {request.name}")
        
        # Prepare requirements
        requirements = {
            "name": request.name,
            "description": request.description,
            "schedule": request.schedule,
            "source": request.source,
            "target": request.target,
            **request.additional_config
        }
        
        # Generate XML
        xml_content = await xml_generator.generate_xml_stream(requirements)
        
        # Get generation stats
        stats = await xml_generator.get_stats()
        
        # Determine generation mode
        if not settings.XML_GENERATION_ENABLED:
            generation_mode = "mock"
        elif stats.get("is_fine_tuned", False):
            generation_mode = "lora"
        else:
            generation_mode = "base_model"
        
        logger.info(f"✅ XML Generated (mode: {generation_mode})")
        
        return StreamGenerationResponse(
            xml_content=xml_content,
            generation_mode=generation_mode,
            is_fine_tuned=stats.get("is_fine_tuned", False),
            metadata={
                "stream_name": request.name,
                "generation_timestamp": "2025-07-04T01:30:00Z",
                "model_stats": stats
            }
        )
        
    except Exception as e:
        logger.error(f"❌ XML Generation Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"XML generation failed: {str(e)}"
        )

@router.get("/health")
async def xml_generation_health():
    """Health check for XML Generation Service"""
    try:
        stats = await xml_generator.get_stats()
        
        return {
            "status": "healthy",
            "service": "xml_generation",
            "xml_generation_enabled": settings.XML_GENERATION_ENABLED,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ XML Health Check Error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/initialize")
async def initialize_xml_generator():
    """Initialize XML Generator (dev endpoint)"""
    try:
        await xml_generator.initialize()
        stats = await xml_generator.get_stats()
        
        return {
            "message": "XML Generator initialized successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ XML Generator Initialization Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"XML Generator initialization failed: {str(e)}"
        )

@router.post("/train-lora")
async def train_lora_adapter():
    """Train LoRA adapter for XML generation (placeholder)"""
    try:
        if not settings.TRAINING_ENABLED:
            raise HTTPException(status_code=503, detail="Training is disabled")
        
        # This will be implemented in training pipeline
        logger.info("🔧 LoRA Training requested - will be implemented in training pipeline")
        
        return {
            "message": "LoRA Training will be implemented in future version",
            "status": "placeholder",
            "training_enabled": settings.TRAINING_ENABLED
        }
        
    except Exception as e:
        logger.error(f"❌ LoRA Training Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LoRA training failed: {str(e)}"
        )

@router.get("/templates")
async def get_xml_templates():
    """Get available XML templates"""
    return {
        "templates": [
            {
                "name": "basic_data_processing",
                "description": "Basic data processing stream",
                "example": {
                    "name": "DailyProcessing",
                    "schedule": "daily",
                    "source": "/data/input",
                    "target": "/data/output"
                }
            },
            {
                "name": "real_time_processing",
                "description": "Real-time stream processing",
                "example": {
                    "name": "RealtimeStream",
                    "schedule": "continuous",
                    "source": "/stream/input",
                    "target": "/stream/output"
                }
            },
            {
                "name": "batch_processing",
                "description": "Batch processing stream",
                "example": {
                    "name": "WeeklyBatch",
                    "schedule": "weekly",
                    "source": "/batch/input",
                    "target": "/batch/output"
                }
            }
        ]
    }