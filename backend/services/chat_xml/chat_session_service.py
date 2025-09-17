"""
Chat Session Service - Phase 1.1
Session-Management für Chat-zu-XML Konversationen mit persistentem Zustand
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from services.chat_xml.parameter_extractor import get_parameter_extractor, ParameterChecklist, ParameterStatus
from services.chat_xml.xml_chat_validator import ChatXMLValidator
from services.xml_template_engine import get_template_engine

logger = logging.getLogger(__name__)

class ChatSessionState(Enum):
    """Status einer Chat-Session"""
    CREATED = "created"
    JOB_TYPE_SELECTION = "job_type_selection"
    PARAMETER_COLLECTION = "parameter_collection"
    VALIDATION = "validation"
    XML_GENERATION = "xml_generation"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class MessageType(Enum):
    """Typ einer Chat-Nachricht"""
    USER_MESSAGE = "user_message"
    SYSTEM_PROMPT = "system_prompt"
    PARAMETER_REQUEST = "parameter_request"
    VALIDATION_ERROR = "validation_error"
    SUCCESS_CONFIRMATION = "success_confirmation"
    XML_PREVIEW = "xml_preview"

@dataclass
class ChatMessage:
    """Eine Chat-Nachricht mit Metadaten"""
    id: str
    message_type: MessageType
    content: str
    timestamp: datetime

    # Chat-spezifische Eigenschaften
    parameter_name: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatSession:
    """Persistente Chat-Session für XML-Generierung"""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime

    # Session-Status
    state: ChatSessionState
    job_type: Optional[str] = None

    # Chat-Historie
    messages: List[ChatMessage] = field(default_factory=list)

    # Parameter-Sammlung
    parameter_checklist: Optional[ParameterChecklist] = None
    collected_parameters: Dict[str, Any] = field(default_factory=dict)

    # XML-Generation
    generated_xml: Optional[str] = None
    validation_issues: List[str] = field(default_factory=list)

    # Metadaten
    completion_percentage: float = 0.0
    estimated_remaining_time: Optional[int] = None  # Minuten
    retry_count: int = 0

class ChatSessionService:
    """Service für Session-Management in Chat-zu-XML System"""

    def __init__(self):
        """Initialize the chat session service"""
        self.sessions: Dict[str, ChatSession] = {}
        self.parameter_extractor = get_parameter_extractor()
        self.xml_validator = ChatXMLValidator()
        self.template_engine = get_template_engine()

        # Session-Konfiguration
        self.session_timeout_minutes = 60
        self.max_retry_count = 3

        logger.info("Chat Session Service initialized")

    async def initialize(self) -> None:
        """Initialisiert den Session Service"""
        try:
            await self.parameter_extractor.initialize()
            logger.info("Chat Session Service fully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Chat Session Service: {str(e)}")
            raise

    def create_session(self, user_id: Optional[str] = None, job_type: Optional[str] = None, initial_context: Optional[str] = None) -> ChatSession:
        """Erstellt eine neue Chat-Session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            state=ChatSessionState.CREATED,
            job_type=job_type
        )

        self.sessions[session_id] = session

        # Willkommensnachricht hinzufügen
        welcome_message = self._create_message(
            MessageType.SYSTEM_PROMPT,
            "Willkommen beim XML-Generator! Ich helfe Ihnen dabei, eine StreamWorks XML-Konfiguration zu erstellen. "
            "Welchen Job-Type möchten Sie erstellen?",
            session
        )
        session.messages.append(welcome_message)
        session.state = ChatSessionState.JOB_TYPE_SELECTION

        # If job type is provided, set appropriate checklist
        if job_type:
            session.parameter_checklist = self.parameter_extractor.get_parameter_checklist(job_type)
            session.state = ChatSessionState.PARAMETER_COLLECTION

        logger.info(f"Created new chat session: {session_id} with job_type: {job_type}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Gibt eine Session zurück"""
        session = self.sessions.get(session_id)
        if session:
            # Prüfe Session-Timeout
            if self._is_session_expired(session):
                self._cleanup_session(session_id)
                return None
        return session

    def set_job_type(self, session_id: str, job_type: str) -> Tuple[bool, str, Optional[str]]:
        """Setzt den Job-Type und startet Parameter-Sammlung"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found", None

        # Validiere Job-Type
        available_types = self.parameter_extractor.get_job_types()
        if job_type not in available_types:
            available_list = ", ".join(available_types.keys())
            error_msg = f"Unbekannter Job-Type '{job_type}'. Verfügbare Typen: {available_list}"
            return False, error_msg, None

        # Setze Job-Type und lade Parameter-Checkliste
        session.job_type = job_type
        session.parameter_checklist = self.parameter_extractor.get_parameter_checklist(job_type)
        session.state = ChatSessionState.PARAMETER_COLLECTION
        session.last_activity = datetime.now()

        # Erstelle Job-Type Bestätigung
        job_info = available_types[job_type]
        confirmation_msg = self._create_message(
            MessageType.SUCCESS_CONFIRMATION,
            f"✅ Job-Type '{job_info['display_name']}' ausgewählt.\n"
            f"📋 {job_info['parameter_count']} Parameter zu sammeln "
            f"({job_info['required_parameters']} erforderlich)\n"
            f"⏱️ Geschätzte Zeit: {job_info['estimated_time']}",
            session
        )
        session.messages.append(confirmation_msg)

        # Bestimme ersten Parameter
        next_param_info = self.parameter_extractor.get_next_parameter_prompt(job_type)
        if next_param_info:
            param, prompt = next_param_info
            param_msg = self._create_message(
                MessageType.PARAMETER_REQUEST,
                prompt,
                session,
                parameter_name=param.name
            )
            session.messages.append(param_msg)
            return True, "Job-Type gesetzt", prompt
        else:
            # Keine Parameter erforderlich
            session.state = ChatSessionState.XML_GENERATION
            return True, "Job-Type gesetzt, keine Parameter erforderlich", None

    def collect_parameter(self, session_id: str, parameter_name: str, value: Any) -> Tuple[bool, str, Optional[str]]:
        """Sammelt einen Parameter-Wert"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found", None

        if session.state != ChatSessionState.PARAMETER_COLLECTION:
            return False, f"Ungültiger Session-Status: {session.state.value}", None

        if not session.job_type:
            return False, "Kein Job-Type gesetzt", None

        # Aktualisiere Parameter
        success = self.parameter_extractor.update_parameter_value(session.job_type, parameter_name, value)
        session.collected_parameters[parameter_name] = value
        session.last_activity = datetime.now()

        if success:
            # Parameter erfolgreich gesetzt
            session.parameter_checklist = self.parameter_extractor.get_parameter_checklist(session.job_type)
            session.completion_percentage = session.parameter_checklist.completion_percentage

            success_msg = self._create_message(
                MessageType.SUCCESS_CONFIRMATION,
                f"✅ Parameter '{parameter_name}' gesetzt: {value}",
                session,
                parameter_name=parameter_name
            )
            session.messages.append(success_msg)

            # Prüfe ob weitere Parameter benötigt werden
            next_param_info = self.parameter_extractor.get_next_parameter_prompt(session.job_type)
            if next_param_info:
                param, prompt = next_param_info
                param_msg = self._create_message(
                    MessageType.PARAMETER_REQUEST,
                    prompt,
                    session,
                    parameter_name=param.name
                )
                session.messages.append(param_msg)
                return True, f"Parameter gesetzt", prompt
            else:
                # Alle Parameter gesammelt - starte XML-Generierung
                session.state = ChatSessionState.XML_GENERATION
                return True, "Alle Parameter gesammelt", "XML wird generiert..."

        else:
            # Validierungsfehler
            checklist = self.parameter_extractor.get_parameter_checklist(session.job_type)
            param = next((p for p in checklist.parameters if p.name == parameter_name), None)

            if param and param.validation_error:
                error_msg = self._create_message(
                    MessageType.VALIDATION_ERROR,
                    f"❌ {param.validation_error}",
                    session,
                    parameter_name=parameter_name,
                    validation_errors=[param.validation_error]
                )
                session.messages.append(error_msg)

                # Wiederhole Parameter-Anfrage
                next_param_info = self.parameter_extractor.get_next_parameter_prompt(session.job_type)
                if next_param_info:
                    _, prompt = next_param_info
                    return False, param.validation_error, prompt

            return False, "Validierungsfehler", None

    def generate_xml(self, session_id: str) -> Tuple[bool, str, Optional[str]]:
        """Generiert XML aus gesammelten Parametern"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found", None

        if not session.job_type:
            return False, "Kein Job-Type gesetzt", None

        try:
            # Extrahiere gesammelte Parameter
            parameters = self.parameter_extractor.extract_collected_parameters(session.job_type)

            # Generiere XML mit Template Engine
            xml_content = self.template_engine.generate_xml(session.job_type, parameters)

            # Validiere generiertes XML
            validation_result = self.xml_validator.validate_chat_xml(
                xml_content,
                {"job_type": session.job_type, "parameters": parameters}
            )

            session.generated_xml = xml_content
            session.validation_issues = [issue.human_message for issue in validation_result.issues]
            session.last_activity = datetime.now()

            if validation_result.is_valid:
                session.state = ChatSessionState.COMPLETED
                session.completion_percentage = 100.0

                completion_msg = self._create_message(
                    MessageType.SUCCESS_CONFIRMATION,
                    f"🎉 XML erfolgreich generiert!\n"
                    f"📄 {len(xml_content)} Zeichen\n"
                    f"✅ Validierung bestanden",
                    session
                )
                session.messages.append(completion_msg)

                return True, "XML erfolgreich generiert", xml_content

            else:
                session.state = ChatSessionState.VALIDATION

                validation_msg = self._create_message(
                    MessageType.VALIDATION_ERROR,
                    f"⚠️ XML generiert, aber mit Validierungsfehlern:\n" +
                    "\n".join(f"• {issue}" for issue in session.validation_issues[:5]),
                    session,
                    validation_errors=session.validation_issues
                )
                session.messages.append(validation_msg)

                return False, "XML hat Validierungsfehler", xml_content

        except Exception as e:
            session.state = ChatSessionState.ERROR
            session.retry_count += 1

            error_msg = self._create_message(
                MessageType.VALIDATION_ERROR,
                f"❌ Fehler bei XML-Generierung: {str(e)}",
                session,
                validation_errors=[str(e)]
            )
            session.messages.append(error_msg)

            logger.error(f"XML generation failed for session {session_id}: {str(e)}")
            return False, f"XML-Generierung fehlgeschlagen: {str(e)}", None

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Gibt detaillierten Session-Status zurück"""
        session = self.get_session(session_id)
        if not session:
            return None

        status = {
            "session_id": session.session_id,
            "state": session.state.value,
            "job_type": session.job_type,
            "completion_percentage": session.completion_percentage,
            "collected_parameters": len(session.collected_parameters),
            "total_messages": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "has_validation_issues": len(session.validation_issues) > 0
        }

        if session.parameter_checklist:
            status.update({
                "required_parameters": len([p for p in session.parameter_checklist.parameters if p.required]),
                "missing_parameters": len(session.parameter_checklist.missing_parameters),
                "invalid_parameters": len(session.parameter_checklist.invalid_parameters),
                "next_parameter": session.parameter_checklist.next_parameter
            })

        return status

    def get_chat_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Gibt Chat-Historie zurück"""
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session.messages
        if limit:
            messages = messages[-limit:]

        return [
            {
                "id": msg.id,
                "type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "parameter_name": msg.parameter_name,
                "validation_errors": msg.validation_errors,
                "metadata": msg.metadata
            }
            for msg in messages
        ]

    def cancel_session(self, session_id: str) -> bool:
        """Bricht eine Session ab"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.state = ChatSessionState.CANCELLED
        session.last_activity = datetime.now()

        cancel_msg = self._create_message(
            MessageType.SYSTEM_PROMPT,
            "Session wurde abgebrochen",
            session
        )
        session.messages.append(cancel_msg)

        return True

    def cleanup_expired_sessions(self) -> int:
        """Räumt abgelaufene Sessions auf"""
        now = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self._cleanup_session(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def _create_message(
        self,
        message_type: MessageType,
        content: str,
        session: ChatSession,
        parameter_name: Optional[str] = None,
        validation_errors: List[str] = None
    ) -> ChatMessage:
        """Erstellt eine neue Chat-Nachricht"""
        return ChatMessage(
            id=str(uuid.uuid4()),
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            parameter_name=parameter_name,
            validation_errors=validation_errors or [],
            metadata={"session_state": session.state.value}
        )

    def _is_session_expired(self, session: ChatSession) -> bool:
        """Prüft ob Session abgelaufen ist"""
        timeout = timedelta(minutes=self.session_timeout_minutes)
        return datetime.now() - session.last_activity > timeout

    def _cleanup_session(self, session_id: str) -> None:
        """Räumt eine Session auf"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Cleaned up session: {session_id}")

# Singleton instance
_chat_session_service = None

def get_chat_session_service() -> ChatSessionService:
    """Get chat session service singleton"""
    global _chat_session_service
    if _chat_session_service is None:
        _chat_session_service = ChatSessionService()
        # Initialize the service synchronously
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_chat_session_service.initialize())
        except RuntimeError:
            # If no loop is running, create one
            asyncio.run(_chat_session_service.initialize())
    return _chat_session_service