"""
XML Generator API Router
FastAPI endpoints for RAG-based XML generation
"""
import logging
import time
import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response

from schemas.xml_generation import (
    JobTypesResponse, JobTypeInfo, JobType,
    TemplateSearchQuery, TemplateSearchResponse, TemplateMatch,
    WizardFormData, XMLGenerationResult,
    ValidationResponse, ValidationResult,
    ScheduleParsingResponse, ScheduleRule
)
from services.xml_rag_service import get_rag_service, XMLTemplateRAG
from services.xml_validator import get_validator, XSDValidator
from services.xml_template_engine import get_template_engine, XMLTemplateEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/xml-generator", tags=["XML Generator"])


# Dependency injection
def get_rag_service_dep() -> XMLTemplateRAG:
    return get_rag_service()

def get_validator_dep() -> XSDValidator:
    return get_validator()

def get_template_engine_dep() -> XMLTemplateEngine:
    return get_template_engine()


@router.get("/job-types", response_model=JobTypesResponse)
async def get_available_job_types() -> JobTypesResponse:
    """
    Get available job types with metadata and examples
    """
    try:
        job_types = [
            JobTypeInfo(
                type=JobType.STANDARD,
                title="Standard Job",
                description="Windows oder Unix Script-Ausführung",
                complexity="simple",
                estimated_time="2-3 Minuten",
                icon="terminal",
                examples=[
                    "Batch-Datei ausführen",
                    "Shell-Script starten", 
                    "Programm mit Parametern aufrufen"
                ],
                template_count=15
            ),
            JobTypeInfo(
                type=JobType.SAP,
                title="SAP Job",
                description="SAP Report oder Programm mit Parametern",
                complexity="medium",
                estimated_time="4-6 Minuten",
                icon="database",
                examples=[
                    "SAP Report RBDAGAIN ausführen",
                    "Z-Programm mit Variante",
                    "Batch-Input Session verarbeiten"
                ],
                template_count=8
            ),
            JobTypeInfo(
                type=JobType.FILE_TRANSFER,
                title="File Transfer",
                description="Dateiübertragung zwischen Systemen",
                complexity="medium",
                estimated_time="3-4 Minuten",
                icon="file-transfer",
                examples=[
                    "Datei von Server A nach Server B kopieren",
                    "FTP-Upload mit Archivierung",
                    "Verzeichnis synchronisieren"
                ],
                template_count=12
            ),
            JobTypeInfo(
                type=JobType.CUSTOM,
                title="Custom Job",
                description="Benutzerdefinierte komplexe Workflows",
                complexity="complex",
                estimated_time="8-12 Minuten",
                icon="settings",
                examples=[
                    "Multi-Step Workflow",
                    "Kombinierte Operations",
                    "Spezielle Anforderungen"
                ],
                template_count=5
            )
        ]
        
        return JobTypesResponse(job_types=job_types)
        
    except Exception as e:
        logger.error(f"Failed to get job types: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job types")


@router.post("/templates/search", response_model=TemplateSearchResponse)
async def search_similar_templates(
    query: TemplateSearchQuery,
    rag_service: XMLTemplateRAG = Depends(get_rag_service_dep)
) -> TemplateSearchResponse:
    """
    Search for similar XML templates using RAG
    """
    try:
        start_time = time.time()
        
        # Validate query
        if not query.query or len(query.query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")
        
        # Search templates
        template_matches = await rag_service.search_similar_templates(query)
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return TemplateSearchResponse(
            templates=template_matches,
            total_found=len(template_matches),
            search_time_ms=search_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template search failed")


@router.post("/generate", response_model=XMLGenerationResult)
async def generate_xml_from_wizard(
    wizard_data: WizardFormData,
    use_template_engine: bool = True,
    rag_service: XMLTemplateRAG = Depends(get_rag_service_dep),
    template_engine: XMLTemplateEngine = Depends(get_template_engine_dep)
) -> XMLGenerationResult:
    """
    Generate StreamWorks XML from wizard form data using Template Engine (default) or RAG pipeline
    """
    try:
        logger.info(f"Starting XML generation for job type: {wizard_data.job_type}")
        
        # Validate wizard data
        if not wizard_data.stream_properties.stream_name:
            raise HTTPException(status_code=400, detail="Stream name is required")
        
        if not wizard_data.stream_properties.description:
            raise HTTPException(status_code=400, detail="Stream description is required")
        
        # Generate XML using Template Engine (faster, simpler) or RAG (more intelligent)
        if use_template_engine:
            logger.info("Using Template Engine for XML generation")
            result = template_engine.generate_xml(wizard_data)
        else:
            logger.info("Using RAG pipeline for XML generation")
            result = await rag_service.generate_xml(wizard_data)
        
        if not result.success:
            logger.error(f"XML generation failed: {result.error_message}")
            
        logger.info(f"XML generation completed - Success: {result.success}, "
                   f"Review required: {result.requires_human_review}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"XML generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"XML generation failed: {str(e)}")


@router.post("/generate-template", response_model=XMLGenerationResult)
async def generate_xml_template_only(
    wizard_data: WizardFormData,
    template_engine: XMLTemplateEngine = Depends(get_template_engine_dep)
) -> XMLGenerationResult:
    """
    Generate StreamWorks XML using only the Template Engine (fast, lightweight)
    """
    try:
        logger.info(f"Starting template-only XML generation for job type: {wizard_data.job_type}")
        
        # Validate wizard data
        if not wizard_data.stream_properties.stream_name:
            raise HTTPException(status_code=400, detail="Stream name is required")
        
        if not wizard_data.stream_properties.description:
            raise HTTPException(status_code=400, detail="Stream description is required")
        
        # Generate XML using Template Engine
        start_time = time.time()
        result = template_engine.generate_xml(wizard_data)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Update timing info
        if hasattr(result, 'generation_time_ms'):
            result.generation_time_ms = generation_time_ms
        
        if not result.success:
            logger.error(f"Template XML generation failed: {result.error_message}")
        else:
            logger.info(f"Template XML generation completed in {generation_time_ms}ms - "
                       f"Success: {result.success}, Review required: {result.requires_human_review}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template XML generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template XML generation failed: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_xml_content(
    xml_content: str,
    validator: XSDValidator = Depends(get_validator_dep)
) -> ValidationResponse:
    """
    Validate XML content against StreamWorks schema
    """
    try:
        start_time = time.time()
        
        if not xml_content or not xml_content.strip():
            raise HTTPException(status_code=400, detail="XML content is required")
        
        # Validate XML
        validation_result = validator.validate_xml_string(xml_content.strip())
        
        validation_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"XML validation completed in {validation_time_ms}ms - "
                   f"Valid: {validation_result.valid}, "
                   f"Errors: {len(validation_result.errors)}, "
                   f"Warnings: {len(validation_result.warnings)}")
        
        return ValidationResponse(
            validation_result=validation_result,
            validation_time_ms=validation_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"XML validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="XML validation failed")


@router.post("/natural-language/schedule", response_model=ScheduleParsingResponse)
async def parse_natural_schedule(
    description: str,
    rag_service: XMLTemplateRAG = Depends(get_rag_service_dep)
) -> ScheduleParsingResponse:
    """
    Convert natural language description to StreamWorks ScheduleRuleXml
    """
    try:
        start_time = time.time()
        
        if not description or len(description.strip()) < 5:
            raise HTTPException(status_code=400, detail="Schedule description must be at least 5 characters")
        
        # For now, return basic mapping - can be enhanced with more sophisticated NLP
        schedule_mappings = {
            "täglich": '<SchedulingRules><FixedDates><FixedDate>Daily</FixedDate></FixedDates></SchedulingRules>',
            "daily": '<SchedulingRules><FixedDates><FixedDate>Daily</FixedDate></FixedDates></SchedulingRules>',
            "wöchentlich": '<SchedulingRules><WeeklyPattern><DaysOfWeek>Monday,Tuesday,Wednesday,Thursday,Friday</DaysOfWeek></WeeklyPattern></SchedulingRules>',
            "weekly": '<SchedulingRules><WeeklyPattern><DaysOfWeek>Monday,Tuesday,Wednesday,Thursday,Friday</DaysOfWeek></WeeklyPattern></SchedulingRules>',
            "monatlich": '<SchedulingRules><MonthlyPattern><DayOfMonth>1</DayOfMonth></MonthlyPattern></SchedulingRules>',
            "monthly": '<SchedulingRules><MonthlyPattern><DayOfMonth>1</DayOfMonth></MonthlyPattern></SchedulingRules>',
            "arbeitstag": '<SchedulingRules><WeeklyPattern><DaysOfWeek>Monday,Tuesday,Wednesday,Thursday,Friday</DaysOfWeek></WeeklyPattern></SchedulingRules>',
            "workday": '<SchedulingRules><WeeklyPattern><DaysOfWeek>Monday,Tuesday,Wednesday,Thursday,Friday</DaysOfWeek></WeeklyPattern></SchedulingRules>'
        }
        
        description_lower = description.lower()
        schedule_rule_xml = '<SchedulingRules ShiftRule="3" ScheduleRuleDialogNotYetVisited="1" />'
        
        # Simple pattern matching - can be enhanced with RAG/LLM
        for pattern, rule_xml in schedule_mappings.items():
            if pattern in description_lower:
                schedule_rule_xml = rule_xml
                break
        
        # Extract time if present (basic regex)
        import re
        time_match = re.search(r'(\d{1,2}):(\d{2})', description)
        if time_match:
            hour, minute = time_match.groups()
            schedule_rule_xml = f'<SchedulingRules><FixedTime>{hour}:{minute}</FixedTime></SchedulingRules>'
        
        parsing_time_ms = int((time.time() - start_time) * 1000)
        
        schedule_rule = ScheduleRule(
            schedule_rule_xml=schedule_rule_xml,
            description=f"Parsed from: {description}",
            next_executions=[]  # Could be calculated based on rule
        )
        
        return ScheduleParsingResponse(
            schedule_rule=schedule_rule,
            parsing_time_ms=parsing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Schedule parsing failed")


@router.post("/templates/index")
async def index_xml_templates(
    background_tasks: BackgroundTasks,
    xml_directory: str = "Export-Streams",
    rag_service: XMLTemplateRAG = Depends(get_rag_service_dep)
):
    """
    Index XML templates from directory (admin endpoint)
    This runs in the background to avoid timeout
    """
    try:
        # Start indexing in background
        background_tasks.add_task(rag_service.index_xml_templates, xml_directory)
        
        return {
            "message": "Template indexing started",
            "directory": xml_directory,
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Failed to start template indexing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start template indexing")


@router.get("/status")
async def get_service_status(
    rag_service: XMLTemplateRAG = Depends(get_rag_service_dep),
    validator: XSDValidator = Depends(get_validator_dep)
):
    """
    Get XML generator service status
    """
    try:
        # Check RAG service
        rag_status = "available" if rag_service.collection else "unavailable"
        
        # Check template count
        template_count = 0
        if rag_service.collection:
            try:
                count_result = rag_service.collection.count()
                template_count = count_result
            except:
                template_count = 0
        
        # Check validator
        validator_status = "available" if validator.is_schema_available() else "basic_only"
        
        # Check Ollama
        ollama_status = "unknown"
        try:
            import ollama
            models = ollama.list()
            ollama_status = "available" if models else "unavailable"
        except:
            ollama_status = "unavailable"
        
        return {
            "rag_service": rag_status,
            "template_count": template_count,
            "validator": validator_status,
            "ollama": ollama_status,
            "overall_status": "ready" if all([
                rag_status == "available",
                validator_status in ["available", "basic_only"],
                ollama_status == "available"
            ]) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}")
        return {
            "overall_status": "error",
            "error": str(e)
        }


@router.get("/templates/{template_id}/download")
async def download_template(template_id: str, rag_service: XMLTemplateRAG = Depends(get_rag_service_dep)):
    """
    Download a specific XML template by ID
    """
    try:
        template = rag_service.template_cache.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if not template.xml_content:
            raise HTTPException(status_code=404, detail="Template content not available")
        
        return Response(
            content=template.xml_content,
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={template.filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template download failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template download failed")