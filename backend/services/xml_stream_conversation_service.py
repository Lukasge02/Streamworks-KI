"""
XML Stream Conversation Service
Orchestrates complete stream creation through natural language conversation
Integrates ConversationEngine, RAG Service, and XML Stream Management
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .conversation_engine import ConversationEngine
from .rag.unified_rag_service import get_unified_rag_service
from .xml_streams.xml_stream_service import XMLStreamService
from schemas.xml_streams import JobType, ConversationState

logger = logging.getLogger(__name__)

class StreamCreationPhase(Enum):
    """Phases in stream creation workflow"""
    INITIALIZATION = "initialization"
    JOB_CONFIGURATION = "job_configuration"
    STREAM_PROPERTIES = "stream_properties"
    SCHEDULING = "scheduling"
    VALIDATION = "validation"
    CREATION = "creation"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class StreamConversationState:
    """Enhanced conversation state for stream creation"""
    phase: StreamCreationPhase
    job_type: Optional[JobType]
    collected_data: Dict[str, Any]
    missing_required_fields: List[str]
    validation_errors: List[Dict[str, Any]]
    stream_id: Optional[str] = None
    xml_content: Optional[str] = None
    completion_percentage: float = 0.0
    last_user_message: Optional[str] = None
    context_history: List[Dict[str, Any]] = None

@dataclass
class ConversationResponse:
    """Response from stream conversation processing"""
    message: str
    suggestions: List[str]
    state: StreamConversationState
    requires_user_input: bool = True
    action_taken: Optional[str] = None
    errors: List[str] = None

class XMLStreamConversationService:
    """
    Orchestrates complete XML stream creation through conversational AI

    Features:
    - Natural language stream configuration
    - Intelligent entity extraction and validation
    - RAG-enhanced responses for complex questions
    - Complete stream lifecycle management
    - Error handling with helpful clarifications
    """

    def __init__(self):
        self._initialized = False
        self.conversation_engine = None
        self.rag_service = None
        self.xml_stream_service = None

        # Stream creation templates and validation rules
        self.required_fields_by_job_type = {
            JobType.SAP: [
                "streamProperties.streamName",
                "jobForm.sapSystem",
                "jobForm.reportName"
            ],
            JobType.FILE_TRANSFER: [
                "streamProperties.streamName",
                "jobForm.sourcePath",
                "jobForm.targetPath"
            ],
            JobType.STANDARD: [
                "streamProperties.streamName",
                "jobForm.scriptPath",
                "jobForm.agentName"
            ]
        }

    async def initialize(self) -> bool:
        """Initialize conversation service with dependencies"""
        if self._initialized:
            return True

        try:
            logger.info("🚀 Initializing XML Stream Conversation Service...")

            # Initialize ConversationEngine
            self.conversation_engine = ConversationEngine()
            logger.info("✅ ConversationEngine initialized")

            # Initialize RAG Service
            self.rag_service = await get_unified_rag_service()
            await self.rag_service.initialize()
            logger.info("✅ RAG Service initialized")

            # Initialize XML Stream Service
            self.xml_stream_service = XMLStreamService()
            logger.info("✅ XML Stream Service initialized")

            self._initialized = True
            logger.info("✅ XML Stream Conversation Service ready")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize XML Stream Conversation Service: {str(e)}")
            return False

    async def process_conversation(
        self,
        message: str,
        session_id: str,
        user_id: str = "default",
        current_state: Optional[StreamConversationState] = None
    ) -> ConversationResponse:
        """
        Process user message and orchestrate stream creation conversation

        Args:
            message: User's natural language message
            session_id: Conversation session ID
            user_id: User identifier
            current_state: Current conversation state (if continuing conversation)

        Returns:
            ConversationResponse with bot message, suggestions, and updated state
        """
        if not await self.initialize():
            return ConversationResponse(
                message="Entschuldigung, der Service ist nicht verfügbar. Bitte versuchen Sie es später erneut.",
                suggestions=[],
                state=StreamConversationState(
                    phase=StreamCreationPhase.ERROR,
                    job_type=None,
                    collected_data={},
                    missing_required_fields=[],
                    validation_errors=[]
                )
            )

        try:
            logger.info(f"🔍 Processing conversation: {message[:100]}...")

            # Initialize state if new conversation
            if current_state is None:
                current_state = StreamConversationState(
                    phase=StreamCreationPhase.INITIALIZATION,
                    job_type=None,
                    collected_data={},
                    missing_required_fields=[],
                    validation_errors=[],
                    context_history=[]
                )

            # Update context history
            if current_state.context_history is None:
                current_state.context_history = []
            current_state.context_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            current_state.last_user_message = message

            # Extract entities from user message
            entities = self.conversation_engine.extract_entities_from_message(message)
            logger.info(f"📝 Extracted {len(entities)} entities")

            # Update collected data with extracted entities
            await self._update_collected_data_from_entities(current_state, entities)

            # Determine or update job type
            if current_state.job_type is None:
                job_type, confidence = self.conversation_engine.detect_job_type(
                    message,
                    current_state.context_history
                )
                if job_type and confidence > 0.3:
                    current_state.job_type = job_type
                    logger.info(f"🎯 Job type detected: {job_type.value} (confidence: {confidence:.2f})")

            # Process based on current phase
            response = await self._process_by_phase(current_state, message, session_id, user_id)

            # Update completion percentage
            current_state.completion_percentage = self._calculate_completion_percentage(current_state)

            # Add bot response to context
            current_state.context_history.append({
                "role": "assistant",
                "content": response.message,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"✅ Conversation processed - Phase: {current_state.phase.value}, Completion: {current_state.completion_percentage:.1%}")
            return response

        except Exception as e:
            logger.error(f"❌ Error processing conversation: {str(e)}")
            return ConversationResponse(
                message="Es ist ein Fehler aufgetreten. Können Sie Ihre Anfrage bitte wiederholen?",
                suggestions=["Stream erstellen", "Hilfe anzeigen"],
                state=current_state or StreamConversationState(
                    phase=StreamCreationPhase.ERROR,
                    job_type=None,
                    collected_data={},
                    missing_required_fields=[],
                    validation_errors=[]
                ),
                errors=[str(e)]
            )

    async def _process_by_phase(
        self,
        state: StreamConversationState,
        message: str,
        session_id: str,
        user_id: str
    ) -> ConversationResponse:
        """Process conversation based on current phase"""

        if state.phase == StreamCreationPhase.INITIALIZATION:
            return await self._handle_initialization_phase(state, message)
        elif state.phase == StreamCreationPhase.JOB_CONFIGURATION:
            return await self._handle_job_configuration_phase(state, message)
        elif state.phase == StreamCreationPhase.STREAM_PROPERTIES:
            return await self._handle_stream_properties_phase(state, message)
        elif state.phase == StreamCreationPhase.SCHEDULING:
            return await self._handle_scheduling_phase(state, message)
        elif state.phase == StreamCreationPhase.VALIDATION:
            return await self._handle_validation_phase(state, message)
        elif state.phase == StreamCreationPhase.CREATION:
            return await self._handle_creation_phase(state, message, session_id, user_id)
        else:
            # Fallback to RAG-enhanced response
            return await self._handle_complex_question(state, message, session_id, user_id)

    async def _handle_initialization_phase(
        self,
        state: StreamConversationState,
        message: str
    ) -> ConversationResponse:
        """Handle stream initialization phase"""

        # Check if job type is detected
        if state.job_type:
            state.phase = StreamCreationPhase.JOB_CONFIGURATION
            return ConversationResponse(
                message=f"Perfekt! Ich erstelle einen {self._get_job_type_display_name(state.job_type)} Stream für Sie. Lassen Sie uns die Details konfigurieren.",
                suggestions=self._get_job_configuration_suggestions(state.job_type),
                state=state
            )
        else:
            return ConversationResponse(
                message="Hallo! Ich helfe Ihnen beim Erstellen eines XML Streams. Welche Art von Job möchten Sie konfigurieren?",
                suggestions=[
                    "SAP Report ausführen",
                    "Dateien zwischen Servern transferieren",
                    "Standard Script ausführen",
                    "Benutzerdefinierte Aufgabe"
                ],
                state=state
            )

    async def _handle_job_configuration_phase(
        self,
        state: StreamConversationState,
        message: str
    ) -> ConversationResponse:
        """Handle job configuration phase"""

        # Analyze missing required fields
        missing_fields = self._get_missing_required_fields(state)

        if missing_fields:
            # Generate specific questions for missing fields
            question, suggestions = self._generate_job_configuration_question(state, missing_fields[0])
            return ConversationResponse(
                message=question,
                suggestions=suggestions,
                state=state
            )
        else:
            # Job configuration complete, move to stream properties
            state.phase = StreamCreationPhase.STREAM_PROPERTIES
            return ConversationResponse(
                message="Ausgezeichnet! Die Job-Konfiguration ist vollständig. Jetzt definieren wir die Stream-Eigenschaften.",
                suggestions=[
                    "Stream Name festlegen",
                    "Beschreibung hinzufügen",
                    "Environment wählen"
                ],
                state=state
            )

    async def _handle_stream_properties_phase(
        self,
        state: StreamConversationState,
        message: str
    ) -> ConversationResponse:
        """Handle stream properties configuration"""

        # Check if stream name is set
        if not self._get_nested_value(state.collected_data, "streamProperties.streamName"):
            return ConversationResponse(
                message="Wie soll Ihr Stream heißen? Wählen Sie einen aussagekräftigen Namen.",
                suggestions=[
                    f"{state.job_type.value.title()}_Daily_Export" if state.job_type else "My_Stream",
                    "Custom_Stream_Name",
                    "Automatisch generieren"
                ],
                state=state
            )
        else:
            # Stream properties complete, move to scheduling
            state.phase = StreamCreationPhase.SCHEDULING
            return ConversationResponse(
                message="Stream-Eigenschaften sind konfiguriert! Wann und wie oft soll der Stream ausgeführt werden?",
                suggestions=[
                    "Täglich um 06:00",
                    "Wöchentlich montags",
                    "Manuell starten",
                    "Zeitplan später festlegen"
                ],
                state=state
            )

    async def _handle_scheduling_phase(
        self,
        state: StreamConversationState,
        message: str
    ) -> ConversationResponse:
        """Handle scheduling configuration"""

        # Move to validation phase
        state.phase = StreamCreationPhase.VALIDATION

        # Validate all collected data
        validation_errors = await self._validate_stream_configuration(state)
        state.validation_errors = validation_errors

        if validation_errors:
            error_summary = self._format_validation_errors(validation_errors)
            return ConversationResponse(
                message=f"Ich habe einige Punkte gefunden, die wir klären sollten:\n\n{error_summary}\n\nWelchen Punkt möchten Sie zuerst korrigieren?",
                suggestions=[error["field"] for error in validation_errors[:3]],
                state=state
            )
        else:
            state.phase = StreamCreationPhase.CREATION
            return ConversationResponse(
                message="Perfekt! Die Stream-Konfiguration ist vollständig und gültig. Soll ich den Stream jetzt erstellen?",
                suggestions=[
                    "Ja, Stream erstellen",
                    "Vorher XML anzeigen",
                    "Konfiguration nochmal prüfen"
                ],
                state=state
            )

    async def _handle_validation_phase(
        self,
        state: StreamConversationState,
        message: str
    ) -> ConversationResponse:
        """Handle validation and error correction"""

        # Re-validate after user input
        validation_errors = await self._validate_stream_configuration(state)
        state.validation_errors = validation_errors

        if not validation_errors:
            state.phase = StreamCreationPhase.CREATION
            return ConversationResponse(
                message="Excellent! Alle Validierungsprobleme sind gelöst. Soll ich den Stream erstellen?",
                suggestions=[
                    "Ja, Stream erstellen",
                    "XML Vorschau anzeigen"
                ],
                state=state
            )
        else:
            # Still have errors - ask for specific correction
            first_error = validation_errors[0]
            return ConversationResponse(
                message=f"Danke für die Information! Es gibt noch einen Punkt: {first_error['message']} Können Sie das korrigieren?",
                suggestions=first_error.get("suggestions", ["Korrigieren"]),
                state=state
            )

    async def _handle_creation_phase(
        self,
        state: StreamConversationState,
        message: str,
        session_id: str,
        user_id: str
    ) -> ConversationResponse:
        """Handle final stream creation"""

        try:
            # Create stream using XML Stream Service
            stream_result = await self.xml_stream_service.create_stream_from_conversation_data(
                job_type=state.job_type.value,
                collected_data=state.collected_data,
                user_id=user_id
            )

            state.stream_id = stream_result.get("stream_id")
            state.xml_content = stream_result.get("xml_content")
            state.phase = StreamCreationPhase.COMPLETED
            state.completion_percentage = 1.0

            return ConversationResponse(
                message=f"🎉 Stream erfolgreich erstellt!\n\n**Stream ID:** {state.stream_id}\n**Name:** {self._get_nested_value(state.collected_data, 'streamProperties.streamName')}\n\nDer Stream ist bereit und kann aktiviert werden.",
                suggestions=[
                    "Stream aktivieren",
                    "XML anzeigen",
                    "Neuen Stream erstellen",
                    "Stream bearbeiten"
                ],
                state=state,
                action_taken="stream_created",
                requires_user_input=False
            )

        except Exception as e:
            logger.error(f"❌ Stream creation failed: {str(e)}")
            state.phase = StreamCreationPhase.ERROR
            return ConversationResponse(
                message=f"Entschuldigung, beim Erstellen des Streams ist ein Fehler aufgetreten: {str(e)}\n\nMöchten Sie es nochmal versuchen?",
                suggestions=[
                    "Nochmal versuchen",
                    "Konfiguration prüfen",
                    "Neu starten"
                ],
                state=state,
                errors=[str(e)]
            )

    async def _handle_complex_question(
        self,
        state: StreamConversationState,
        message: str,
        session_id: str,
        user_id: str
    ) -> ConversationResponse:
        """Handle complex questions using RAG service"""

        try:
            # Use RAG service for complex questions
            rag_response = await self.rag_service.query(
                query=message,
                mode="accurate",
                conversation_context=state.context_history[-3:] if state.context_history else None,
                session_id=session_id,
                user_id=user_id
            )

            # Combine RAG response with conversation flow suggestions
            suggestions = rag_response.metadata.get("follow_up_suggestions", [])
            if not suggestions:
                suggestions = self._get_contextual_suggestions(state)

            return ConversationResponse(
                message=rag_response.answer,
                suggestions=suggestions[:4],  # Limit to 4 suggestions
                state=state
            )

        except Exception as e:
            logger.warning(f"RAG query failed: {str(e)}")
            return ConversationResponse(
                message="Das ist eine interessante Frage! Können Sie sie spezifischer stellen oder mir mehr Kontext geben?",
                suggestions=self._get_contextual_suggestions(state),
                state=state
            )

    # Helper Methods

    async def _update_collected_data_from_entities(
        self,
        state: StreamConversationState,
        entities: List[Any]
    ) -> None:
        """Update collected data based on extracted entities"""

        for entity in entities:
            field_path = self._map_entity_to_field_path(entity.field_name, state.job_type)
            if field_path:
                self._set_nested_value(state.collected_data, field_path, entity.value)
                logger.info(f"📝 Entity mapped: {entity.field_name} -> {field_path} = {entity.value}")

    def _map_entity_to_field_path(self, entity_field: str, job_type: Optional[JobType]) -> Optional[str]:
        """Map entity field names to form data paths"""

        mapping = {
            "sap_system": "jobForm.sapSystem",
            "report_name": "jobForm.reportName",
            "file_path": "jobForm.sourcePath",  # Default to source path
            "server_name": "jobForm.targetServer",
            "script_name": "jobForm.scriptPath",
            "agent_name": "jobForm.agentName",
            "time": "scheduling.startTime",
            "frequency": "scheduling.frequency"
        }

        return mapping.get(entity_field)

    def _get_missing_required_fields(self, state: StreamConversationState) -> List[str]:
        """Get list of missing required fields for current job type"""

        if not state.job_type:
            return []

        required_fields = self.required_fields_by_job_type.get(state.job_type, [])
        missing = []

        for field_path in required_fields:
            if not self._get_nested_value(state.collected_data, field_path):
                missing.append(field_path)

        return missing

    def _generate_job_configuration_question(
        self,
        state: StreamConversationState,
        missing_field: str
    ) -> Tuple[str, List[str]]:
        """Generate specific question for missing job configuration field"""

        questions = {
            "jobForm.sapSystem": (
                "Welches SAP-System soll verwendet werden?",
                ["P01 (Produktiv)", "T01 (Test)", "Q01 (Qualität)"]
            ),
            "jobForm.reportName": (
                "Welcher SAP-Report soll ausgeführt werden?",
                ["Z_CUSTOM_REPORT", "Standard Report eingeben"]
            ),
            "jobForm.sourcePath": (
                "Von welchem Pfad sollen die Dateien transferiert werden?",
                ["C:\\Data\\Export\\", "/var/exports/", "\\\\server\\share\\"]
            ),
            "jobForm.targetPath": (
                "Wohin sollen die Dateien transferiert werden?",
                ["Gleicher Server", "Anderer Server"]
            ),
            "jobForm.scriptPath": (
                "Welches Script soll ausgeführt werden?",
                ["batch_process.bat", "data_sync.ps1", "Eigenes Script"]
            ),
            "jobForm.agentName": (
                "Auf welchem Agent soll das Script ausgeführt werden?",
                ["AGENT01", "AGENT02", "Agent-Name eingeben"]
            ),
            "streamProperties.streamName": (
                "Wie soll Ihr Stream heißen?",
                ["Auto-generieren", "Eigenen Namen eingeben"]
            )
        }

        return questions.get(missing_field, ("Weitere Details benötigt.", ["Eingeben"]))

    async def _validate_stream_configuration(
        self,
        state: StreamConversationState
    ) -> List[Dict[str, Any]]:
        """Validate complete stream configuration"""

        errors = []

        # Check required fields
        missing_fields = self._get_missing_required_fields(state)
        for field in missing_fields:
            errors.append({
                "type": "missing_field",
                "field": field,
                "message": f"Pflichtfeld {field} fehlt",
                "suggestions": ["Wert eingeben"]
            })

        # Job-type specific validations
        if state.job_type == JobType.SAP:
            errors.extend(await self._validate_sap_configuration(state))
        elif state.job_type == JobType.FILE_TRANSFER:
            errors.extend(await self._validate_file_transfer_configuration(state))
        elif state.job_type == JobType.STANDARD:
            errors.extend(await self._validate_standard_configuration(state))

        return errors

    async def _validate_sap_configuration(self, state: StreamConversationState) -> List[Dict[str, Any]]:
        """Validate SAP-specific configuration"""
        errors = []

        sap_system = self._get_nested_value(state.collected_data, "jobForm.sapSystem")
        if sap_system and not sap_system.match(r"^[A-Z]\d{2}$"):
            errors.append({
                "type": "invalid_format",
                "field": "jobForm.sapSystem",
                "message": "SAP-System muss Format haben: z.B. P01, T01",
                "suggestions": ["P01", "T01", "Q01"]
            })

        return errors

    async def _validate_file_transfer_configuration(self, state: StreamConversationState) -> List[Dict[str, Any]]:
        """Validate file transfer configuration"""
        errors = []

        source_path = self._get_nested_value(state.collected_data, "jobForm.sourcePath")
        if source_path and not source_path.startswith(("/", "C:", "\\\\")):
            errors.append({
                "type": "invalid_path",
                "field": "jobForm.sourcePath",
                "message": "Quell-Pfad scheint ungültig zu sein",
                "suggestions": ["Pfad korrigieren"]
            })

        return errors

    async def _validate_standard_configuration(self, state: StreamConversationState) -> List[Dict[str, Any]]:
        """Validate standard job configuration"""
        errors = []

        script_path = self._get_nested_value(state.collected_data, "jobForm.scriptPath")
        if script_path and not any(script_path.endswith(ext) for ext in [".bat", ".sh", ".ps1", ".py"]):
            errors.append({
                "type": "invalid_script",
                "field": "jobForm.scriptPath",
                "message": "Script-Datei sollte eine gültige Endung haben (.bat, .sh, .ps1, .py)",
                "suggestions": ["Dateiendung hinzufügen"]
            })

        return errors

    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Format validation errors for user display"""

        formatted = []
        for i, error in enumerate(errors[:3], 1):  # Show max 3 errors
            formatted.append(f"{i}. {error['message']}")

        return "\n".join(formatted)

    def _calculate_completion_percentage(self, state: StreamConversationState) -> float:
        """Calculate completion percentage based on collected data"""

        if not state.job_type:
            return 0.0

        required_fields = self.required_fields_by_job_type.get(state.job_type, [])
        if not required_fields:
            return 0.0

        completed_fields = 0
        for field_path in required_fields:
            if self._get_nested_value(state.collected_data, field_path):
                completed_fields += 1

        base_completion = completed_fields / len(required_fields)

        # Adjust based on phase
        phase_weights = {
            StreamCreationPhase.INITIALIZATION: 0.0,
            StreamCreationPhase.JOB_CONFIGURATION: 0.4,
            StreamCreationPhase.STREAM_PROPERTIES: 0.6,
            StreamCreationPhase.SCHEDULING: 0.8,
            StreamCreationPhase.VALIDATION: 0.9,
            StreamCreationPhase.CREATION: 0.95,
            StreamCreationPhase.COMPLETED: 1.0
        }

        phase_weight = phase_weights.get(state.phase, 0.0)
        return min(base_completion * 0.7 + phase_weight * 0.3, 1.0)

    def _get_contextual_suggestions(self, state: StreamConversationState) -> List[str]:
        """Get contextual suggestions based on current state"""

        base_suggestions = []

        if state.phase == StreamCreationPhase.INITIALIZATION:
            base_suggestions = ["SAP Job", "File Transfer", "Standard Script"]
        elif state.phase == StreamCreationPhase.JOB_CONFIGURATION:
            if state.job_type == JobType.SAP:
                base_suggestions = ["SAP System angeben", "Report Namen eingeben"]
            elif state.job_type == JobType.FILE_TRANSFER:
                base_suggestions = ["Quell-Pfad eingeben", "Ziel-Pfad eingeben"]
            else:
                base_suggestions = ["Script-Pfad eingeben", "Agent auswählen"]
        elif state.phase == StreamCreationPhase.STREAM_PROPERTIES:
            base_suggestions = ["Stream Name eingeben", "Beschreibung hinzufügen"]
        elif state.phase == StreamCreationPhase.SCHEDULING:
            base_suggestions = ["Täglich", "Wöchentlich", "Manuell"]
        else:
            base_suggestions = ["Stream erstellen", "Hilfe", "Neu starten"]

        return base_suggestions

    def _get_job_type_display_name(self, job_type: JobType) -> str:
        """Get user-friendly display name for job type"""

        names = {
            JobType.SAP: "SAP",
            JobType.FILE_TRANSFER: "File Transfer",
            JobType.STANDARD: "Standard",
            JobType.CUSTOM: "Benutzerdefinierten"
        }
        return names.get(job_type, "Unbekannten")

    def _get_job_configuration_suggestions(self, job_type: JobType) -> List[str]:
        """Get initial suggestions for job configuration"""

        suggestions = {
            JobType.SAP: ["SAP System P01 Report Z_EXPORT", "System und Report eingeben"],
            JobType.FILE_TRANSFER: ["Von Server1 zu Server2", "Pfade eingeben"],
            JobType.STANDARD: ["batch_process.bat auf AGENT01", "Script Details eingeben"],
            JobType.CUSTOM: ["Benutzerdefinierte Konfiguration", "Details eingeben"]
        }
        return suggestions.get(job_type, ["Details eingeben"])

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        current = data
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation"""
        keys = path.split('.')
        current = data

        # Create nested structure if needed
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value


# Global service instance
_xml_stream_conversation_service = None

async def get_xml_stream_conversation_service() -> XMLStreamConversationService:
    """Get global XML stream conversation service instance"""
    global _xml_stream_conversation_service
    if _xml_stream_conversation_service is None:
        _xml_stream_conversation_service = XMLStreamConversationService()
    return _xml_stream_conversation_service