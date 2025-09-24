"""
Unified Dialog Manager - Vereinfachte, schema-basierte Dialog-Logik
Elegante Lösung mit direkter Job-Type-Erkennung und linearem Parameter-Flow
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from services.ai.unified_parameter_extractor import UnifiedParameterExtractor, UnifiedExtractionResult
from services.ai.parameter_state_manager import HierarchicalParameterStateManager

logger = logging.getLogger(__name__)

# ================================
# DIALOG STATE MANAGEMENT
# ================================

class UnifiedDialogState(str, Enum):
    """Vereinfachte Dialog-States für linearen Flow"""
    INITIAL = "initial"                    # Neue Session - Job-Type-Erkennung
    COLLECTING_PARAMETERS = "collecting"   # Parameter sammeln (Stream + Job)
    CONFIRMATION = "confirmation"          # Finale Bestätigung
    COMPLETED = "completed"               # Dialog abgeschlossen

class DialogPriority(str, Enum):
    """Priorität der nächsten Aktion"""
    CRITICAL = "critical"      # Erforderliche Parameter fehlen
    IMPORTANT = "important"    # Empfohlene Parameter fehlen
    OPTIONAL = "optional"      # Optionale Parameter
    COMPLETE = "complete"      # Alle Parameter vorhanden

# ================================
# DIALOG RESPONSE MODEL
# ================================

class UnifiedDialogResponse:
    """Vereinfachte Dialog-Antwort"""

    def __init__(
        self,
        message: str,
        state: UnifiedDialogState,
        priority: DialogPriority,
        detected_job_type: Optional[str] = None,
        suggested_questions: List[str] = None,
        extracted_parameters: Optional[Dict[str, Any]] = None,
        completion_percentage: float = 0.0,
        next_parameter: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.message = message
        self.state = state
        self.priority = priority
        self.detected_job_type = detected_job_type
        self.suggested_questions = suggested_questions or []
        self.extracted_parameters = extracted_parameters or {}
        self.completion_percentage = completion_percentage
        self.next_parameter = next_parameter
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

# ================================
# UNIFIED DIALOG MANAGER
# ================================

class UnifiedDialogManager:
    """
    Vereinfachter Dialog Manager mit schema-basierter Logik

    Vorteile der neuen Architektur:
    - Direkte Job-Type-Erkennung aus Schema
    - Linearer Parameter-Flow (Stream → Job → Fertig)
    - Keine komplexe State-Verwaltung
    - Schema-gesteuerte Intelligenz
    """

    def __init__(
        self,
        unified_extractor: UnifiedParameterExtractor,
        state_manager: HierarchicalParameterStateManager,
        openai_api_key: str
    ):
        self.extractor = unified_extractor
        self.state_manager = state_manager
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.2
        )

        # Dialog Templates für natürliche Antworten
        self.templates = self._initialize_templates()

        logger.info("UnifiedDialogManager initialisiert mit schema-basierter Architektur")

    def _initialize_templates(self) -> Dict[str, ChatPromptTemplate]:
        """Initialisiert Dialog-Templates für natürliche Antworten"""

        templates = {}

        # Job-Type-Erkennung Template
        templates["job_type_detected"] = ChatPromptTemplate.from_template("""
Du bist ein freundlicher Streamworks-Assistent.

Ich habe den Job-Type '{job_type}' ({display_name}) erkannt! 🎯

Situation:
- Job-Type: {job_type} - {description}
- Konfidenz: {confidence:.0%}
- Geschätzte Zeit: {estimated_time}

Nächste Schritte:
{next_steps}

Antworte mit einer kurzen, freundlichen Bestätigung (max. 2-3 Sätze) und stelle die nächste Frage.
""")

        # Parameter-Sammlung Template
        templates["parameter_collection"] = ChatPromptTemplate.from_template("""
Du bist ein hilfsreicher Streamworks-Assistent.

Status:
- Job-Type: {job_type}
- Vervollständigung: {completion:.0%}
- Gesammelte Parameter: {collected_count}
- Nächster Parameter: {next_parameter}

Parameter-Details:
{parameter_details}

Erstelle eine natürliche, hilfreiche Nachfrage für den nächsten Parameter.
Maximal 2 Sätze, freundlich und klar.
""")

        # Completion Template
        templates["completion"] = ChatPromptTemplate.from_template("""
Du bist ein erfolgreicher Streamworks-Assistent.

Perfekt! Die Konfiguration ist vollständig! ✅

Gesammelte Parameter:
- Stream: {stream_params}
- Job: {job_params}
- Job-Type: {job_type}

Erstelle eine kurze, positive Abschlussnachricht (max. 2 Sätze) und frage, ob die XML-Datei generiert werden soll.
""")

        return templates

    async def process_message(
        self,
        user_message: str,
        session_id: str,
        session_state: Optional[Dict[str, Any]] = None
    ) -> UnifiedDialogResponse:
        """
        Hauptmethode für Message-Verarbeitung mit vereinfachter Logik

        Args:
            user_message: Nachricht des Users
            session_id: Session-ID
            session_state: Aktueller Session-State (optional)

        Returns:
            UnifiedDialogResponse mit nächster Aktion
        """
        try:
            logger.info(f"🚀 Verarbeite Message: '{user_message[:80]}...'")

            # Hole oder erstelle Session
            session = self.state_manager.get_hierarchical_session(session_id)
            if not session:
                session = self.state_manager.create_hierarchical_session(session_id)

            # Bestimme aktuellen Job-Type
            current_job_type = None
            if session.jobs:
                current_job_type = session.jobs[0].job_type

            # Parameter-Extraktion mit vereinheitlichtem System
            extraction_result = await self.extractor.extract_parameters(
                user_message=user_message,
                existing_stream_params=session.stream_parameters,
                existing_job_params=session.jobs[0].parameters if session.jobs else {},
                current_job_type=current_job_type
            )

            # Aktualisiere Session mit extrahierten Parametern
            self._update_session_with_extraction(session, extraction_result)

            # Bestimme Dialog-Response basierend auf Completion-Status
            if extraction_result.completion_percentage >= 1.0:
                response = await self._handle_completion(extraction_result, session)
            elif extraction_result.detected_job_type and not current_job_type:
                response = await self._handle_job_type_detected(extraction_result, session)
            else:
                response = await self._handle_parameter_collection(extraction_result, session)

            # Speichere Session
            self.state_manager.save_hierarchical_session(session)

            logger.info(f"✅ Dialog Response: {response.state} | {response.priority}")
            return response

        except Exception as e:
            logger.error(f"❌ Fehler bei Dialog-Verarbeitung: {e}")
            return UnifiedDialogResponse(
                message="Entschuldigung, es ist ein Fehler aufgetreten. Könnten Sie Ihre Anfrage wiederholen?",
                state=UnifiedDialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                metadata={"error": str(e)}
            )

    def _update_session_with_extraction(
        self,
        session,
        extraction: UnifiedExtractionResult
    ) -> None:
        """Aktualisiert Session mit extrahierten Parametern"""

        # Stream-Parameter aktualisieren
        for param in extraction.stream_parameters:
            session.stream_parameters[param.name] = param.value
            logger.info(f"📝 Stream-Parameter aktualisiert: {param.name} = {param.value}")

        # Job-Parameter aktualisieren
        if extraction.detected_job_type:
            # Erstelle oder aktualisiere Job
            if not session.jobs:
                job_id = session.add_or_update_job(
                    job_type=extraction.detected_job_type,
                    parameters={},
                    job_name=f"{extraction.detected_job_type}_Job"
                )
            else:
                job_id = session.jobs[0].job_id

            # Aktualisiere Job-Parameter
            for param in extraction.job_parameters:
                session.jobs[0].parameters[param.name] = param.value
                logger.info(f"🔧 Job-Parameter aktualisiert: {param.name} = {param.value}")

    async def _handle_job_type_detected(
        self,
        extraction: UnifiedExtractionResult,
        session
    ) -> UnifiedDialogResponse:
        """Behandelt erstmalige Job-Type-Erkennung"""

        job_type = extraction.detected_job_type
        job_info = self.extractor.get_job_type_info(job_type)

        if not job_info:
            return UnifiedDialogResponse(
                message="Entschuldigung, der erkannte Job-Type ist nicht verfügbar. Welchen Job-Type möchten Sie verwenden?",
                state=UnifiedDialogState.INITIAL,
                priority=DialogPriority.CRITICAL
            )

        # Bestimme nächste Schritte
        if extraction.next_required_parameter:
            next_steps = f"Als nächstes benötige ich: {extraction.next_required_parameter}"
        else:
            next_steps = "Alle erforderlichen Parameter sind bereits vorhanden!"

        # Generiere natürliche Antwort
        template = self.templates["job_type_detected"]
        response = await template.ainvoke({
            "job_type": job_type,
            "display_name": job_info["display_name"],
            "description": job_info["description"],
            "confidence": extraction.confidence_score,
            "estimated_time": job_info["estimated_time"],
            "next_steps": next_steps
        })

        # Bestimme nächste Frage
        if extraction.suggested_questions:
            next_question = extraction.suggested_questions[0]
            full_message = f"{response.content}\n\n{next_question}"
        else:
            full_message = response.content

        return UnifiedDialogResponse(
            message=full_message,
            state=UnifiedDialogState.COLLECTING_PARAMETERS,
            priority=DialogPriority.IMPORTANT if extraction.needs_clarification else DialogPriority.COMPLETE,
            detected_job_type=job_type,
            suggested_questions=extraction.suggested_questions,
            completion_percentage=extraction.completion_percentage,
            next_parameter=extraction.next_required_parameter,
            metadata={
                "job_info": job_info,
                "confidence": extraction.confidence_score
            }
        )

    async def _handle_parameter_collection(
        self,
        extraction: UnifiedExtractionResult,
        session
    ) -> UnifiedDialogResponse:
        """Behandelt laufende Parameter-Sammlung"""

        job_type = extraction.detected_job_type or (session.jobs[0].job_type if session.jobs else "Unknown")

        # Bestimme Parameter-Details für Template
        if extraction.next_required_parameter:
            job_info = self.extractor.get_job_type_info(job_type)
            param_details = "Parameter wird benötigt für die Konfiguration."

            # Finde Parameter-Schema
            if job_info:
                all_params = job_info.get("job_parameters", [])
                param_schema = next((p for p in all_params if p["name"] == extraction.next_required_parameter), None)
                if param_schema:
                    param_details = f"{param_schema['description']} (Beispiele: {', '.join(map(str, param_schema.get('examples', [])[:2]))})"
        else:
            param_details = "Alle Parameter sind gesammelt."

        # Generiere natürliche Antwort für Parameter-Sammlung
        template = self.templates["parameter_collection"]
        response = await template.ainvoke({
            "job_type": job_type,
            "completion": extraction.completion_percentage * 100,
            "collected_count": len(extraction.stream_parameters) + len(extraction.job_parameters),
            "next_parameter": extraction.next_required_parameter or "Keiner",
            "parameter_details": param_details
        })

        # Füge Nachfrage hinzu
        if extraction.suggested_questions:
            full_message = f"{response.content}\n\n{extraction.suggested_questions[0]}"
        else:
            full_message = response.content

        return UnifiedDialogResponse(
            message=full_message,
            state=UnifiedDialogState.COLLECTING_PARAMETERS,
            priority=DialogPriority.IMPORTANT if extraction.needs_clarification else DialogPriority.COMPLETE,
            detected_job_type=job_type,
            suggested_questions=extraction.suggested_questions,
            completion_percentage=extraction.completion_percentage,
            next_parameter=extraction.next_required_parameter,
            metadata={"extraction_metadata": extraction.extraction_metadata}
        )

    async def _handle_completion(
        self,
        extraction: UnifiedExtractionResult,
        session
    ) -> UnifiedDialogResponse:
        """Behandelt vollständige Parameter-Sammlung"""

        job_type = extraction.detected_job_type or (session.jobs[0].job_type if session.jobs else "Unknown")

        # Sammle alle Parameter für Anzeige
        stream_params = list(session.stream_parameters.keys())
        job_params = list(session.jobs[0].parameters.keys()) if session.jobs else []

        # Generiere Abschlussnachricht
        template = self.templates["completion"]
        response = await template.ainvoke({
            "stream_params": ", ".join(stream_params),
            "job_params": ", ".join(job_params),
            "job_type": job_type
        })

        return UnifiedDialogResponse(
            message=response.content,
            state=UnifiedDialogState.CONFIRMATION,
            priority=DialogPriority.COMPLETE,
            detected_job_type=job_type,
            completion_percentage=1.0,
            suggested_questions=["Soll ich die XML-Datei jetzt generieren?"],
            metadata={
                "ready_for_xml": True,
                "stream_parameters": session.stream_parameters,
                "job_parameters": session.jobs[0].parameters if session.jobs else {}
            }
        )

    def get_available_job_types(self) -> List[Dict[str, Any]]:
        """Gibt verfügbare Job-Types zurück"""
        return self.extractor.get_available_job_types()

# ================================
# FACTORY FUNCTION
# ================================

def create_unified_dialog_manager(
    unified_extractor: UnifiedParameterExtractor,
    state_manager: HierarchicalParameterStateManager,
    openai_api_key: str
) -> UnifiedDialogManager:
    """Factory function für UnifiedDialogManager"""
    return UnifiedDialogManager(unified_extractor, state_manager, openai_api_key)