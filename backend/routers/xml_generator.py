"""
XML Generator API Router
FastAPI endpoints for RAG-based XML generation
"""
import logging
import time
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field

from schemas.xml_generation import (
    JobTypesResponse, JobTypeInfo, JobType,
    TemplateSearchQuery, TemplateSearchResponse, TemplateMatch,
    WizardFormData, XMLGenerationResult,
    ValidationResponse, ValidationResult,
    ScheduleParsingResponse, ScheduleRule
)
from services.qdrant_rag_service import get_rag_service
from services.xml_validator import get_validator, XSDValidator
from services.xml_template_engine import get_template_engine, XMLTemplateEngine
from services.chat_xml.dialog_manager import get_dialog_manager, DialogManager
from services.chat_xml.chat_session_service import get_chat_session_service, ChatSessionService
from services.chat_xml.xml_chat_validator import get_chat_xml_validator, ChatXMLValidator
from services.ai.langextract.unified_langextract_service import get_unified_langextract_service
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/xml-generator", tags=["XML Generator"])


# ================================
# CHAT-XML API SCHEMAS
# ================================

class CreateXMLSessionRequest(BaseModel):
    user_id: Optional[str] = Field(default="default-user")
    initial_context: Optional[str] = None
    job_type: Optional[str] = Field(default="STANDARD", description="Job type: STANDARD, SAP, FILE_TRANSFER, CUSTOM")

class CreateXMLSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str

class SendXMLMessageRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ParameterStatusItem(BaseModel):
    parameter_name: str
    current_value: Optional[Any] = None
    is_required: bool = True
    is_completed: bool = False
    validation_status: str = "pending"
    intelligent_suggestions: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0

class SendXMLMessageResponse(BaseModel):
    response: str
    updated_params: Dict[str, Any] = Field(default_factory=dict)
    parameter_statuses: List[ParameterStatusItem] = Field(default_factory=list)
    completion_percentage: float = 0.0
    next_required_params: List[str] = Field(default_factory=list)
    session_status: str = "ACTIVE"
    suggestions: Optional[List[str]] = None
    validation_errors: Optional[List[str]] = None

class GenerateXMLRequest(BaseModel):
    session_id: str
    force_generation: bool = Field(default=False)

class GenerateXMLResponse(BaseModel):
    xml_content: str
    is_valid: bool
    validation_errors: Optional[List[str]] = None
    template_used: str
    generation_time: float

class XMLSessionStatusResponse(BaseModel):
    session: Dict[str, Any]
    messages: List[Dict[str, Any]]
    parameter_progress: Dict[str, Any]

class ValidateParametersResponse(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    missing_required: List[str] = Field(default_factory=list)


# Dependency injection
async def get_rag_service_dep():
    return await get_rag_service()

def get_validator_dep() -> XSDValidator:
    return get_validator()

def get_template_engine_dep() -> XMLTemplateEngine:
    return get_template_engine()

def get_dialog_manager_dep() -> DialogManager:
    return get_dialog_manager()

def get_chat_session_service_dep() -> ChatSessionService:
    return get_chat_session_service()

def get_xml_chat_validator_dep() -> ChatXMLValidator:
    return get_chat_xml_validator()


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
    rag_service = Depends(get_rag_service_dep)
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
    rag_service = Depends(get_rag_service_dep),
    template_engine: XMLTemplateEngine = Depends(get_template_engine_dep)
) -> XMLGenerationResult:
    """
    Generate Streamworks XML from wizard form data using Template Engine (default) or RAG pipeline
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
    Generate Streamworks XML using only the Template Engine (fast, lightweight)
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


@router.post("/preview", response_model=XMLGenerationResult)
async def generate_xml_preview(
    wizard_data: Dict[str, Any],
    template_engine: XMLTemplateEngine = Depends(get_template_engine_dep)
) -> XMLGenerationResult:
    """
    Generate XML preview from partial wizard data with smart defaults
    Accepts incomplete/partial form data and generates preview with placeholders
    """
    try:
        logger.info("Starting XML preview generation")
        
        # Convert dict to WizardFormData with defaults for missing fields
        partial_wizard_data = _create_partial_wizard_data(wizard_data)
        
        # Generate XML using Template Engine in preview mode
        start_time = time.time()
        result = template_engine.generate_xml(partial_wizard_data, preview_mode=True)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Update timing info
        if hasattr(result, 'generation_time_ms'):
            result.generation_time_ms = generation_time_ms
        
        logger.info(f"XML preview generated in {generation_time_ms}ms - "
                   f"Success: {result.success}, Placeholders: {len(result.review_reasons)}")
        
        return result
        
    except Exception as e:
        logger.error(f"XML preview generation failed: {str(e)}")
        # Return a basic XML structure even on error
        return XMLGenerationResult(
            success=True,
            xml_content=_get_minimal_xml_template(),
            requires_human_review=True,
            review_reasons=[f"Error during preview: {str(e)}"],
            generation_time_ms=0
        )


def _create_partial_wizard_data(data: Dict[str, Any]) -> WizardFormData:
    """Convert partial dict data to WizardFormData with smart defaults"""
    from schemas.xml_generation import JobType, ScheduleMode
    
    # Default job type
    job_type_str = data.get('jobType', 'standard')
    try:
        job_type = JobType(job_type_str)
    except ValueError:
        job_type = JobType.STANDARD
    
    # Create minimal stream properties
    stream_props_data = data.get('streamProperties', {})
    contact_data = stream_props_data.get('contactPerson', {})
    
    # Use dynamic imports to avoid circular dependencies
    try:
        from schemas.xml_generation import StreamProperties, ContactPerson
        
        contact_person = ContactPerson(
            firstName=contact_data.get('firstName', ''),
            lastName=contact_data.get('lastName', ''),
            company=contact_data.get('company', 'Arvato Systems'),
            department=contact_data.get('department', '')
        )
        
        stream_properties = StreamProperties(
            streamName=stream_props_data.get('streamName', ''),
            description=stream_props_data.get('description', ''),
            documentation=stream_props_data.get('documentation', ''),
            contactPerson=contact_person
        )
    except ImportError:
        # Fallback: create simple objects
        class SimpleContact:
            def __init__(self, **kwargs):
                self.first_name = kwargs.get('firstName', '')
                self.last_name = kwargs.get('lastName', '') 
                self.company = kwargs.get('company', 'Arvato Systems')
                self.department = kwargs.get('department', '')
        
        class SimpleStreamProps:
            def __init__(self, **kwargs):
                self.stream_name = kwargs.get('streamName', '')
                self.description = kwargs.get('description', '')
                self.documentation = kwargs.get('documentation', '')
                self.contact_person = SimpleContact(**kwargs.get('contactPerson', {}))
        
        stream_properties = SimpleStreamProps(**stream_props_data)
    
    # Create minimal scheduling
    scheduling_data = data.get('scheduling', {})
    try:
        from schemas.xml_generation import SchedulingForm, SimpleSchedule
        
        scheduling = SchedulingForm(
            mode=ScheduleMode.SIMPLE,
            simple=SimpleSchedule(
                preset=scheduling_data.get('simple', {}).get('preset', 'manual'),
                weekdays=[True] * 7
            )
        )
    except ImportError:
        class SimpleScheduling:
            def __init__(self):
                self.mode = None
                self.simple = None
        
        scheduling = SimpleScheduling()
    
    # Create minimal wizard data
    class PartialWizardData:
        def __init__(self):
            self.job_type = job_type
            self.stream_properties = stream_properties
            self.job_form = data.get('jobForm', {})
            self.scheduling = scheduling
    
    return PartialWizardData()


def _get_minimal_xml_template() -> str:
    """Return minimal XML template for error cases"""
    return '''<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>{{Neuer_Stream}}</StreamName>
    <StreamDocumentation><![CDATA[{{Stream_wird_konfiguriert}}]]></StreamDocumentation>
    <ShortDescription><![CDATA[{{Bitte_Wizard_ausfuellen}}]]></ShortDescription>
    <Jobs>
      <Job>
        <JobName>{{Job_wird_erstellt}}</JobName>
        <JobType>{{Bitte_Job_Type_waehlen}}</JobType>
      </Job>
    </Jobs>
  </Stream>
</ExportableStream>'''


@router.post("/validate", response_model=ValidationResponse)
async def validate_xml_content(
    xml_content: str,
    validator: XSDValidator = Depends(get_validator_dep)
) -> ValidationResponse:
    """
    Validate XML content against Streamworks schema
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
    rag_service = Depends(get_rag_service_dep)
) -> ScheduleParsingResponse:
    """
    Convert natural language description to Streamworks ScheduleRuleXml
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
    rag_service = Depends(get_rag_service_dep)
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
    rag_service = Depends(get_rag_service_dep),
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
async def download_template(template_id: str, rag_service = Depends(get_rag_service_dep)):
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


# ================================
# CHAT-XML API ENDPOINTS
# ================================

@router.post("/chat-xml/session", response_model=CreateXMLSessionResponse)
async def create_xml_chat_session(
    request: CreateXMLSessionRequest,
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
) -> CreateXMLSessionResponse:
    """
    Create a new XML chat session for conversational XML generation
    """
    try:
        session = session_service.create_session(
            user_id=request.user_id,
            job_type=request.job_type,
            initial_context=request.initial_context
        )

        logger.info(f"Created XML chat session: {session.session_id}")

        return CreateXMLSessionResponse(
            session_id=session.session_id,
            status="created",
            message="XML chat session successfully created"
        )

    except Exception as e:
        logger.error(f"Failed to create XML chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/chat-xml/session/{session_id}", response_model=XMLSessionStatusResponse)
async def get_xml_chat_session(
    session_id: str,
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
) -> XMLSessionStatusResponse:
    """
    Get XML chat session details with messages and parameter progress
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert session to dict
        session_dict = {
            "id": session.session_id,
            "user_id": session.user_id,
            "status": session.state.value,
            "job_type": session.job_type,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "completion_percentage": session.completion_percentage
        }

        # Convert messages to dicts
        messages = []
        for msg in session.messages:
            messages.append({
                "id": msg.id,
                "type": "user" if msg.message_type.value == "user_message" else "assistant",
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            })

        # Calculate parameter progress
        total_params = len(session.parameter_checklist.parameters) if session.parameter_checklist else 0
        completed_params = len([p for p in session.collected_parameters.values() if p is not None])

        parameter_progress = {
            "total_parameters": total_params,
            "required_parameters": total_params,  # Simplified
            "completed_parameters": completed_params,
            "completion_percentage": session.completion_percentage
        }

        return XMLSessionStatusResponse(
            session=session_dict,
            messages=messages,
            parameter_progress=parameter_progress
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get XML chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session")


@router.delete("/chat-xml/session/{session_id}")
async def delete_xml_chat_session(
    session_id: str,
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
):
    """
    Delete an XML chat session
    """
    try:
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Deleted XML chat session: {session_id}")
        return {"message": "Session successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete XML chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.post("/chat-xml/message", response_model=SendXMLMessageResponse)
async def send_xml_chat_message(
    request: SendXMLMessageRequest,
    dialog_manager: DialogManager = Depends(get_dialog_manager_dep),
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
) -> SendXMLMessageResponse:
    """
    Send a message to XML chat session and get intelligent response
    """
    try:
        # Process message with OpenAI-powered dialog manager
        response = await dialog_manager.process_user_message(
            session_id=request.session_id,
            user_message=request.message
        )

        # Get updated session state
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert parameter statuses
        parameter_statuses = []
        if session.parameter_checklist:
            for param in session.parameter_checklist.parameters:
                current_value = session.collected_parameters.get(param.name)
                parameter_statuses.append(ParameterStatusItem(
                    parameter_name=param.name,
                    current_value=current_value,
                    is_required=param.required,
                    is_completed=current_value is not None,
                    validation_status="completed" if current_value else "pending",
                    intelligent_suggestions=response.suggested_values or [],
                    confidence_score=response.confidence
                ))

        # Determine next required parameters
        next_required = []
        if session.parameter_checklist:
            for param in session.parameter_checklist.parameters:
                if param.required and param.name not in session.collected_parameters:
                    next_required.append(param.name)

        return SendXMLMessageResponse(
            response=response.content,
            updated_params=session.collected_parameters,
            parameter_statuses=parameter_statuses,
            completion_percentage=session.completion_percentage,
            next_required_params=next_required[:3],  # Limit to 3
            session_status=session.state.value,
            suggestions=response.suggested_values,
            validation_errors=response.validation_issues
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process XML chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/chat-xml/generate", response_model=GenerateXMLResponse)
async def generate_xml_from_chat(
    request: GenerateXMLRequest,
    session_service: ChatSessionService = Depends(get_chat_session_service_dep),
    template_engine: XMLTemplateEngine = Depends(get_template_engine_dep)
) -> GenerateXMLResponse:
    """
    Generate XML from chat session parameters
    """
    try:
        import time
        start_time = time.time()

        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Generate XML using template engine
        result = session_service.generate_xml(
            session_id=request.session_id,
            force_generation=request.force_generation
        )

        generation_time = time.time() - start_time

        return GenerateXMLResponse(
            xml_content=result.get("xml_content", ""),
            is_valid=result.get("is_valid", False),
            validation_errors=result.get("validation_errors", []),
            template_used=result.get("template_used", "default"),
            generation_time=generation_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate XML from chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate XML: {str(e)}")


@router.get("/chat-xml/session/{session_id}/parameters", response_model=List[ParameterStatusItem])
async def get_xml_chat_parameters(
    session_id: str,
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
) -> List[ParameterStatusItem]:
    """
    Get parameter statuses for XML chat session
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        parameter_statuses = []
        if session.parameter_checklist:
            for param in session.parameter_checklist.parameters:
                current_value = session.collected_parameters.get(param.name)
                parameter_statuses.append(ParameterStatusItem(
                    parameter_name=param.name,
                    current_value=current_value,
                    is_required=param.required,
                    is_completed=current_value is not None,
                    validation_status="completed" if current_value else "pending",
                    intelligent_suggestions=[],
                    confidence_score=1.0
                ))

        return parameter_statuses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get XML chat parameters: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get parameters")


@router.post("/chat-xml/session/{session_id}/validate", response_model=ValidateParametersResponse)
async def validate_xml_chat_parameters(
    session_id: str,
    validator: ChatXMLValidator = Depends(get_xml_chat_validator_dep),
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
) -> ValidateParametersResponse:
    """
    Validate current parameters in XML chat session
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validate parameters using enhanced validator
        validation_result = validator.validate_collected_parameters(
            session.collected_parameters,
            session.job_type or "STANDARD"
        )

        # Find missing required parameters
        missing_required = []
        if session.parameter_checklist:
            for param in session.parameter_checklist.parameters:
                if param.required and param.name not in session.collected_parameters:
                    missing_required.append(param.name)

        return ValidateParametersResponse(
            is_valid=validation_result.is_valid,
            errors=validation_result.validation_errors,
            missing_required=missing_required
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate XML chat parameters: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate parameters")


@router.get("/chat-xml/status")
async def get_chat_xml_status(
    session_service: ChatSessionService = Depends(get_chat_session_service_dep)
):
    """
    Get Chat-XML system status
    """
    try:
        # Check service health
        active_sessions = len(session_service.sessions)

        return {
            "chat_xml_service": "available",
            "active_sessions": active_sessions,
            "openai_integration": "enabled",
            "overall_status": "ready"
        }

    except Exception as e:
        logger.error(f"Failed to get Chat-XML status: {str(e)}")
        return {
            "chat_xml_service": "error",
            "error": str(e),
            "overall_status": "degraded"
        }


# ================================
# TEMPLATE-BASED XML GENERATION API
# ================================

class GenerateTemplateXMLRequest(BaseModel):
    """Request model for template-based XML generation"""
    session_id: str = Field(..., description="LangExtract session ID containing extracted parameters")
    job_type: Optional[str] = Field(None, description="Override job type (STANDARD, FILE_TRANSFER, SAP)")
    force_regenerate: bool = Field(False, description="Force regeneration even if XML already exists")


class GenerateTemplateXMLResponse(BaseModel):
    """Response model for template-based XML generation"""
    success: bool
    xml_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    parameters_used: Optional[Dict[str, Any]] = None
    original_parameters: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PreviewXMLParametersRequest(BaseModel):
    """Request model for XML parameter preview"""
    session_id: str = Field(..., description="LangExtract session ID")
    job_type: Optional[str] = Field(None, description="Override job type")


class PreviewXMLParametersResponse(BaseModel):
    """Response model for XML parameter preview"""
    session_id: str
    job_type: str
    original_parameters: Dict[str, Any]
    mapped_parameters: Dict[str, Any]
    template_context: Dict[str, Any]
    template_schema: Dict[str, Any]
    mapping_summary: Dict[str, Any]


@router.post("/template/generate", response_model=GenerateTemplateXMLResponse)
async def generate_template_xml(
    request: GenerateTemplateXMLRequest,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    🚀 Generate Streamworks XML from extracted LangExtract parameters

    This endpoint uses the template-based approach:
    1. Retrieves extracted parameters from LangExtract session
    2. Maps parameters to XML template format
    3. Generates XML using Jinja2 templates
    4. Returns complete Streamworks XML

    **Template Types:**
    - STANDARD: General job automation
    - FILE_TRANSFER: File transfer between agents/servers
    - SAP: SAP system integration and reports

    **Example Usage:**
    ```python
    # After extracting parameters with LangExtract
    response = requests.post("/api/xml-generator/template/generate",
        json={"session_id": "streamworks_20250922_123456_1234"})
    ```
    """

    try:
        logger.info(f"🚀 Template XML generation requested for session: {request.session_id}")

        # Generate XML using the enhanced LangExtract service
        result = await langextract_service.generate_xml(
            session_id=request.session_id,
            job_type=request.job_type
        )

        if result.get("success"):
            logger.info(f"✅ Template XML generated successfully for session {request.session_id}")
            return GenerateTemplateXMLResponse(
                success=True,
                xml_content=result["xml_content"],
                metadata=result["metadata"],
                parameters_used=result["parameters_used"],
                original_parameters=result["original_parameters"]
            )
        else:
            logger.error(f"❌ Template XML generation failed: {result.get('error')}")
            return GenerateTemplateXMLResponse(
                success=False,
                error=result.get("error", "Unknown error during XML generation")
            )

    except ValueError as e:
        logger.error(f"❌ Template XML generation validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Template XML generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"XML generation failed: {str(e)}")


@router.post("/template/preview", response_model=PreviewXMLParametersResponse)
async def preview_xml_parameters(
    request: PreviewXMLParametersRequest,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    🔍 Preview XML parameters and template mapping

    This endpoint allows you to:
    - Inspect extracted parameters from LangExtract session
    - See how parameters map to XML template fields
    - Validate parameter completeness before XML generation
    - Debug parameter extraction and mapping issues

    **Use Cases:**
    - Parameter validation before XML generation
    - Debugging parameter extraction issues
    - Understanding template requirements
    - Testing parameter mapping logic

    **Returns:**
    - Original extracted parameters
    - Mapped template parameters
    - Template context with all resolved values
    - Template schema and requirements
    - Mapping summary statistics
    """

    try:
        logger.info(f"🔍 XML parameter preview requested for session: {request.session_id}")

        # Preview parameters using the enhanced LangExtract service
        result = await langextract_service.preview_xml_parameters(
            session_id=request.session_id,
            job_type=request.job_type
        )

        logger.info(f"✅ XML parameter preview completed for session {request.session_id}")
        return PreviewXMLParametersResponse(**result)

    except ValueError as e:
        logger.error(f"❌ XML parameter preview validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"❌ XML parameter preview error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parameter preview failed: {str(e)}")


@router.get("/template/info")
async def get_template_info():
    """
    📋 Get information about available XML templates

    Returns metadata about all available Streamworks XML templates including:
    - Supported job types
    - Template file locations
    - Required and optional parameters
    - Parameter mapping rules
    - Example usage patterns

    **Template Overview:**
    - **STANDARD**: General job automation with script execution
    - **FILE_TRANSFER**: File transfer with source/target agents
    - **SAP**: SAP system integration with report execution
    """

    try:
        from services.xml_generation.template_engine import get_xml_template_engine
        from services.xml_generation.parameter_mapper import get_parameter_mapper

        template_engine = get_xml_template_engine()
        parameter_mapper = get_parameter_mapper()

        # Get template information
        available_templates = template_engine.list_templates()

        template_info = {}
        for job_type, template_file in available_templates.items():
            template_schema = template_engine.get_template_parameters(job_type)

            template_info[job_type] = {
                "template_file": template_file,
                "job_type": job_type,
                "required_fields": template_schema.get("required_fields", []),
                "schema": template_schema.get("schema", {}),
                "description": {
                    "STANDARD": "General job automation with script execution",
                    "FILE_TRANSFER": "File transfer between agents/servers with comprehensive options",
                    "SAP": "SAP system integration with report and transaction support"
                }.get(job_type, "Unknown template type")
            }

        return {
            "available_templates": template_info,
            "total_templates": len(available_templates),
            "template_engine": "Jinja2-based XML generation",
            "parameter_mapping": "Intelligent field mapping with transformations",
            "supported_formats": ["Streamworks XML v2.0"],
            "documentation": "Template-first approach with 361 real-world examples"
        }

    except Exception as e:
        logger.error(f"❌ Template info retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template info retrieval failed: {str(e)}")


@router.get("/template/health")
async def check_template_system_health():
    """
    🏥 Health check for template-based XML generation system

    Verifies that all components are working correctly:
    - XML template files accessibility
    - Template engine initialization
    - Parameter mapper functionality
    - LangExtract service integration

    Returns detailed health status for monitoring and debugging.
    """

    try:
        from services.xml_generation.template_engine import get_xml_template_engine
        from services.xml_generation.parameter_mapper import get_parameter_mapper

        health_status = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": time.time()
        }

        # Check template engine
        try:
            template_engine = get_xml_template_engine()
            templates = template_engine.list_templates()
            health_status["components"]["template_engine"] = {
                "status": "healthy",
                "templates_available": len(templates),
                "templates": list(templates.keys())
            }
        except Exception as e:
            health_status["components"]["template_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"

        # Check parameter mapper
        try:
            parameter_mapper = get_parameter_mapper()
            mapping_configs = len(parameter_mapper.mapping_configs)
            health_status["components"]["parameter_mapper"] = {
                "status": "healthy",
                "mapping_configs": mapping_configs,
                "transformations": len(parameter_mapper.transformations)
            }
        except Exception as e:
            health_status["components"]["parameter_mapper"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"

        # Check LangExtract service
        try:
            langextract_service = get_unified_langextract_service()
            health_status["components"]["langextract_service"] = {
                "status": "healthy",
                "schemas_loaded": len(langextract_service.schemas),
                "xml_generation": "enabled"
            }
        except Exception as e:
            health_status["components"]["langextract_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"❌ Template system health check error: {str(e)}")
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


# ================================
# XML STORAGE & MANAGEMENT API
# ================================

class XMLListResponse(BaseModel):
    """Response model for XML list"""
    session_id: str
    total_xmls: int
    xmls: List[Dict[str, Any]]


class XMLContentResponse(BaseModel):
    """Response model for XML content"""
    id: str
    stream_name: str
    job_type: str
    version: int
    xml_content: str
    created_at: str
    file_size: Optional[int] = None
    parameters_used: Dict[str, Any]
    metadata: Dict[str, Any]


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics"""
    total_xmls_in_db: int
    total_local_files: int
    total_local_size_bytes: int
    total_local_size_mb: float
    base_path: str
    retention_days: int


@router.get("/xmls/{session_id}", response_model=XMLListResponse)
async def get_session_xmls(
    session_id: str,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    📂 Get all generated XMLs for a session

    Returns a list of all XML files generated for the specified LangExtract session.
    Each XML entry includes metadata like generation time, version, file size, and
    the parameters that were used for generation.

    **Use Cases:**
    - Review all XML versions for a session
    - Track XML generation history
    - Compare different XML generations
    - Manage session-specific XMLs

    **Example Response:**
    ```json
    {
        "session_id": "streamworks_20250122_143022_1234",
        "total_xmls": 3,
        "xmls": [
            {
                "id": "uuid-here",
                "stream_name": "DEMO_FT_STREAM",
                "job_type": "FILE_TRANSFER",
                "version": 3,
                "created_at": "2025-01-22T14:30:22",
                "file_size": 12398
            }
        ]
    }
    ```
    """

    try:
        logger.info(f"📂 Getting XMLs for session: {session_id}")

        result = await langextract_service.get_generated_xmls(session_id)

        logger.info(f"✅ Retrieved {result['total_xmls']} XMLs for session {session_id}")
        return XMLListResponse(**result)

    except Exception as e:
        logger.error(f"❌ Failed to get XMLs for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve XMLs: {str(e)}")


@router.get("/xml/{xml_id}", response_model=XMLContentResponse)
async def get_xml_content(
    xml_id: str,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    📄 Get specific XML content by ID

    Retrieves the complete XML content and metadata for a specific XML file.
    Content is served from local filesystem for performance, with database fallback.

    **Use Cases:**
    - Download specific XML version
    - View XML content for review
    - Get XML with generation metadata
    - Retrieve parameters used for generation

    **Performance:**
    - Local file access: ~1ms response time
    - Database fallback: ~10ms response time
    - Automatic content source optimization
    """

    try:
        logger.info(f"📄 Getting XML content for ID: {xml_id}")

        result = await langextract_service.get_xml_content(xml_id)

        logger.info(f"✅ Retrieved XML content: {len(result['xml_content'])} characters")
        return XMLContentResponse(**result)

    except ValueError as e:
        logger.error(f"❌ XML not found: {xml_id}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Failed to get XML content for {xml_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve XML: {str(e)}")


@router.get("/download/{xml_id}")
async def download_xml_file(
    xml_id: str,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    💾 Download XML as file

    Downloads the XML as a properly formatted .xml file with appropriate headers.
    File is served directly from local filesystem for optimal performance.

    **Response Headers:**
    - Content-Type: application/xml
    - Content-Disposition: attachment; filename="stream_name_v1.xml"
    - Content-Length: file size in bytes

    **Use Cases:**
    - Download XML for Streamworks import
    - Save XML to local filesystem
    - Integrate with external tools
    - Backup XML files
    """

    try:
        logger.info(f"💾 Preparing download for XML: {xml_id}")

        # Get XML metadata and content
        result = await langextract_service.get_xml_content(xml_id)

        # Generate safe filename
        stream_name = result["stream_name"]
        version = result["version"]
        safe_name = "".join(c for c in stream_name if c.isalnum() or c in ['_', '-', '.']).rstrip()
        if not safe_name:
            safe_name = "stream"

        filename = f"{safe_name}_v{version}.xml"

        # Create temporary file for download if local file doesn't exist
        from pathlib import Path
        import tempfile

        # Try to find local file first
        from services.xml_storage_service import get_xml_storage_service
        storage_service = get_xml_storage_service()

        from uuid import UUID
        xml_uuid = UUID(xml_id)
        xml_record = await storage_service.get_xml_by_id(xml_uuid)

        if xml_record and xml_record.file_path and Path(xml_record.file_path).exists():
            # Serve local file directly
            local_path = Path(xml_record.file_path)
            logger.info(f"💾 Serving local file: {local_path}")

            return FileResponse(
                path=str(local_path),
                filename=filename,
                media_type="application/xml",
                headers={"Content-Length": str(local_path.stat().st_size)}
            )
        else:
            # Create temporary file from database content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(result["xml_content"])
                temp_path = temp_file.name

            logger.info(f"💾 Serving temporary file: {temp_path}")

            return FileResponse(
                path=temp_path,
                filename=filename,
                media_type="application/xml",
                headers={"Content-Length": str(len(result["xml_content"].encode('utf-8')))}
            )

    except ValueError as e:
        logger.error(f"❌ XML not found for download: {xml_id}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Download failed for XML {xml_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.delete("/xml/{xml_id}")
async def delete_xml(
    xml_id: str,
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    🗑️ Delete a generated XML

    Permanently deletes an XML from both database and local filesystem.
    This action cannot be undone.

    **Security:**
    - Only the XML and its local file are deleted
    - Session data and parameters remain intact
    - Other XMLs from the same session are not affected

    **Use Cases:**
    - Clean up unwanted XML versions
    - Remove test/development XMLs
    - Manage storage space
    - Correct mistaken generations
    """

    try:
        logger.info(f"🗑️ Deleting XML: {xml_id}")

        success = await langextract_service.delete_generated_xml(xml_id)

        if success:
            logger.info(f"✅ XML deleted successfully: {xml_id}")
            return {"success": True, "message": f"XML {xml_id} deleted successfully"}
        else:
            logger.warning(f"⚠️ Failed to delete XML: {xml_id}")
            raise HTTPException(status_code=404, detail=f"XML not found or could not be deleted: {xml_id}")

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except Exception as e:
        logger.error(f"❌ Error deleting XML {xml_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/storage/stats", response_model=StorageStatsResponse)
async def get_storage_statistics(
    langextract_service: Any = Depends(get_unified_langextract_service)
):
    """
    📊 Get XML storage statistics

    Returns comprehensive statistics about XML storage usage including
    database records, local files, storage sizes, and retention policies.

    **Statistics Include:**
    - Total XML records in database
    - Total local files on filesystem
    - Storage size in bytes and MB
    - Storage path and retention settings

    **Use Cases:**
    - Monitor storage usage
    - Plan storage capacity
    - Debug storage issues
    - Generate storage reports
    """

    try:
        logger.info("📊 Getting storage statistics")

        stats = await langextract_service.get_storage_statistics()

        logger.info(f"✅ Retrieved storage statistics")
        return StorageStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Failed to get storage statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")


@router.post("/storage/cleanup")
async def cleanup_old_files():
    """
    🧹 Clean up old local XML files

    Removes local XML files older than the retention period (default: 7 days).
    Database records are preserved for reference.

    **Cleanup Policy:**
    - Files older than retention period are deleted
    - Database records remain intact
    - Only local filesystem is affected
    - Operation is logged for audit

    **Returns:**
    - Number of files deleted
    - Total space freed
    - Cleanup timestamp
    """

    try:
        logger.info("🧹 Starting storage cleanup")

        from services.xml_storage_service import get_xml_storage_service
        storage_service = get_xml_storage_service()

        deleted_count = await storage_service.cleanup_old_files()

        logger.info(f"✅ Cleanup completed: {deleted_count} files deleted")

        return {
            "success": True,
            "deleted_files": deleted_count,
            "message": f"Cleaned up {deleted_count} old XML files",
            "cleanup_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")