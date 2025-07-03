from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

from app.models.schemas import StreamConfig, StreamResponse
from app.utils.xml_utils import generate_xml_from_config, validate_xml

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-stream", response_model=StreamResponse)
async def generate_stream(config: StreamConfig):
    """Generate XML stream from configuration"""
    try:
        logger.info(f"🔄 Generating stream: {config.streamName}")
        
        # Generate XML
        xml_content = generate_xml_from_config(config)
        
        # Validate XML
        if not validate_xml(xml_content):
            raise HTTPException(status_code=400, detail="Generated XML is invalid")
        
        logger.info(f"✅ Generated XML stream: {config.streamName}")
        
        return StreamResponse(
            xml=xml_content,
            config=config,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream generation error: {str(e)}")

@router.post("/validate")
async def validate_stream(xml_content: str):
    """Validate XML stream"""
    try:
        is_valid = validate_xml(xml_content)
        return {"valid": is_valid}
    except Exception as e:
        logger.error(f"❌ Error validating XML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"XML validation error: {str(e)}")

@router.get("/health")
async def streams_health():
    """Streams service health check"""
    return {
        "status": "healthy",
        "service": "streams"
    }