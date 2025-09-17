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
    rag_service = Depends(get_rag_service_dep)
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