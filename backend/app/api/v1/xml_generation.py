"""
XML Stream Generation API with Template System and Robust Validation
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ValidationError as PydanticValidationError
from typing import Optional, Dict, Any, List
import logging

from app.services.xml_generator import xml_generator
from app.services.error_handler import error_handler
from app.models.validation import XMLGenerationRequestValidator, validate_request_size
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
async def generate_xml_stream(request: XMLGenerationRequestValidator, raw_request: Request):
    """Generate XML Stream with robust validation and error handling"""
    try:
        # Request size validation
        content_length = raw_request.headers.get("content-length")
        if content_length and not validate_request_size(int(content_length)):
            raise HTTPException(
                status_code=413,
                detail="Request too large. Maximum size is 10MB."
            )
        
        logger.info(f"🔧 Validated XML Generation Request für: {request.name}")
        
        # Prepare requirements with validated data
        requirements = {
            "name": request.name,
            "description": request.description,
            "schedule": request.schedule,
            "data_source": request.data_source,
            "output_path": request.output_path,
            "template_type": request.template_type,
        }
        
        # Add optional fields if provided
        if request.memory:
            requirements["memory"] = request.memory
        if request.timeout:
            requirements["timeout"] = request.timeout
        if request.retry_attempts:
            requirements["retry_attempts"] = request.retry_attempts
        
        # Generate XML using template system
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
        
    except PydanticValidationError as ve:
        logger.warning(f"📝 XML Generation validation error: {ve}")
        raise HTTPException(
            status_code=422,
            detail=f"Input validation failed: {str(ve)}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"❌ XML Generation Error: {str(e)}")
        
        # Use error handler for graceful fallback
        try:
            fallback_response = await error_handler.handle_xml_error(e, {"requirements": requirements})
            
            # Extract XML from fallback if available
            if "```xml" in fallback_response.message:
                import re
                xml_match = re.search(r'```xml\n(.*?)\n```', fallback_response.message, re.DOTALL)
                if xml_match:
                    fallback_xml = xml_match.group(1)
                    
                    logger.info("🔧 Using fallback XML from error handler")
                    return StreamGenerationResponse(
                        xml_content=fallback_xml,
                        generation_mode="fallback_template",
                        is_fine_tuned=False,
                        metadata={
                            "stream_name": request.name,
                            "generation_timestamp": "2025-07-04T01:30:00Z",
                            "fallback_type": fallback_response.fallback_type.value,
                            "error": str(e)
                        }
                    )
            
            # If no XML in fallback, provide error details
            raise HTTPException(
                status_code=500,
                detail=fallback_response.message
            )
            
        except HTTPException:
            raise
        except Exception as fallback_error:
            logger.error(f"❌ XML Generation fallback also failed: {fallback_error}")
            raise HTTPException(
                status_code=500,
                detail="XML generation completely failed. Please try again or contact support."
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