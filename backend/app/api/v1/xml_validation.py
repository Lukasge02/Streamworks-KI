"""
XML Validation API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from app.services.xml_validator import xml_validator

logger = logging.getLogger(__name__)
router = APIRouter()

class XMLValidationRequest(BaseModel):
    xml_content: str

class XMLValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    error_count: int
    warning_count: int

class XMLTemplateRequest(BaseModel):
    stream_type: str = "daily_batch"

class XMLTemplateResponse(BaseModel):
    template: str
    stream_type: str

@router.post("/validate", response_model=XMLValidationResponse)
async def validate_xml(request: XMLValidationRequest):
    """Validate StreamWorks XML against schema and best practices"""
    try:
        logger.info("🔍 Validating XML stream")
        
        # Validate XML
        result = await xml_validator.validate_stream(request.xml_content)
        
        logger.info(f"✅ Validation complete: {'VALID' if result.is_valid else 'INVALID'}")
        
        return XMLValidationResponse(**result.to_dict())
        
    except Exception as e:
        logger.error(f"❌ XML Validation Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"XML validation failed: {str(e)}"
        )

@router.post("/suggest")
async def suggest_improvements(request: XMLValidationRequest):
    """Get improvement suggestions for XML stream"""
    try:
        logger.info("💡 Generating XML improvement suggestions")
        
        suggestions = await xml_validator.suggest_improvements(request.xml_content)
        
        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"❌ Suggestion Generation Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )

@router.get("/template/{stream_type}", response_model=XMLTemplateResponse)
async def get_xml_template(stream_type: str = "daily_batch"):
    """Get XML template for common stream types"""
    try:
        valid_types = ["daily_batch", "continuous_monitor", "weekly_report"]
        
        if stream_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stream type. Must be one of: {', '.join(valid_types)}"
            )
        
        template = xml_validator.create_template(stream_type)
        
        return XMLTemplateResponse(
            template=template,
            stream_type=stream_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Template Generation Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate template: {str(e)}"
        )

@router.get("/schema")
async def get_validation_schema():
    """Get StreamWorks XML validation schema information"""
    return {
        "required_elements": ["stream", "name", "schedule"],
        "valid_schedule_types": ["daily", "weekly", "monthly", "once", "continuous"],
        "valid_task_types": ["batch", "powershell", "python", "copy", "delete"],
        "best_practices": [
            "Include description element",
            "Add error handling to tasks",
            "Configure logging",
            "Set resource limits",
            "Use parallel execution for multiple tasks"
        ],
        "example": {
            "minimal": """<stream>
    <name>example_stream</name>
    <schedule>
        <type>daily</type>
        <time>02:00</time>
    </schedule>
    <tasks>
        <task type="batch">
            <command>example.bat</command>
        </task>
    </tasks>
</stream>"""
        }
    }