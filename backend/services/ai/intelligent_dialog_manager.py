"""
Intelligent Dialog Manager - MVP Implementation
Intelligente Chat-Logik für systematische Parameter-Sammlung
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from services.ai.smart_parameter_extractor import SmartParameterExtractor, ParameterExtractionResult, HierarchicalExtractionResult
from services.ai.parameter_state_manager import HierarchicalParameterStateManager
from models.parameter_models import (
    JOB_TYPE_MODEL_MAPPING,
    ParameterValidationResult,
    create_parameter_instance,
    HierarchicalStreamSession,
    ParameterScope
)

logger = logging.getLogger(__name__)

# ================================
# DIALOG STATE MANAGEMENT
# ================================

class DialogState(str, Enum):
    """Status des Dialog-Flows für vollständige Stream-Konfiguration"""
    INITIAL = "initial"              # Neuer Dialog, beginnt immer mit Stream-Parametern
    STREAM_CONFIGURATION = "stream_configuration"      # Stream-Level Parameter sammeln (Name, Beschreibung, etc.)
    JOB_TYPE_SELECTION = "job_type_selection"          # User wählt Job-Type für den Stream
    PARAMETER_COLLECTION = "parameter_collection"      # Job-Parameter werden gesammelt
    VALIDATION = "validation"        # Parameter werden validiert
    CONFIRMATION = "confirmation"    # Finale Bestätigung
    COMPLETED = "completed"         # Dialog abgeschlossen

class DialogPriority(str, Enum):
    """Priorität der nächsten Aktion"""
    CRITICAL = "critical"    # Erforderliche Parameter fehlen
    IMPORTANT = "important"  # Empfohlene Parameter fehlen
    OPTIONAL = "optional"    # Optionale Parameter können gesammelt werden
    COMPLETE = "complete"    # Alle Parameter vorhanden

# ================================
# DIALOG RESPONSE MODELS
# ================================

class DialogResponse:
    """Antwort des Dialog Managers"""

    def __init__(
        self,
        message: str,
        state: DialogState,
        priority: DialogPriority,
        suggested_questions: List[str] = None,
        extracted_parameters: Optional[Dict[str, Any]] = None,
        next_parameter: str = None,
        completion_percentage: float = 0.0,
        validation_issues: List[str] = None,
        metadata: Dict[str, Any] = None,
        parameter_confidences: Optional[Dict[str, float]] = None
    ) -> None:
        self.message = message
        self.state = state
        self.priority = priority
        self.suggested_questions = suggested_questions or []
        self.extracted_parameters = extracted_parameters or {}
        self.parameter_confidences = parameter_confidences or {}
        self.next_parameter = next_parameter
        self.completion_percentage = completion_percentage
        self.validation_issues = validation_issues or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

# ================================
# INTELLIGENT DIALOG MANAGER
# ================================

class IntelligentDialogManager:
    """
    Intelligenter Dialog Manager für systematische Parameter-Sammlung

    Hauptfunktionen:
    - Erkennt User-Intent und extrahiert Parameter
    - Stellt gezielt Nachfragen für fehlende Parameter
    - Priorisiert Parameter-Sammlung
    - Validiert Parameter und gibt Feedback
    """

    def __init__(
        self,
        parameter_extractor: SmartParameterExtractor,
        hierarchical_state_manager: HierarchicalParameterStateManager,
        openai_api_key: str
    ):
        self.extractor = parameter_extractor
        self.hierarchical_manager = hierarchical_state_manager
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.2,  # Leicht kreativer für natürliche Dialoge
            timeout=30.0,     # 30 Sekunden Timeout
            max_retries=2     # Maximal 2 Versuche
        )

        # Dialog Templates
        self.dialog_templates = self._load_dialog_templates()

        logger.info("IntelligentDialogManager mit hierarchischer Unterstützung initialisiert")

    def _load_dialog_templates(self) -> Dict[str, ChatPromptTemplate]:
        """Lädt vordefinierte Dialog-Templates"""

        templates = {}

        # Template für Session-Type Auswahl (Stream vs Job)
        templates["session_type_selection"] = ChatPromptTemplate.from_template("""
Du bist ein intelligenter Assistent für StreamWorks-Konfiguration.

Der User hat eine Anfrage gestellt. Analysiere, ob er einen vollständigen Stream oder nur einen einzelnen Job konfigurieren möchte.

User-Nachricht: "{user_message}"

Optionen:
🎯 **Stream-Konfiguration**: Vollständiger Stream mit Metadaten (Name, Beschreibung, Scheduling) und einem oder mehreren Jobs
🔧 **Job-Konfiguration**: Einzelner Job ohne Stream-Container

Aufgabe:
1. Analysiere die User-Absicht
2. Schlage die passende Konfigurationsart vor
3. Erkläre kurz den Unterschied
4. Frage nach Bestätigung

Stil: Klar, hilfreich, strukturiert. Maximal 3 Sätze.
""")

        # Template für Stream-Parameter Sammlung
        templates["stream_configuration"] = ChatPromptTemplate.from_template("""
Du bist ein Assistent für Stream-Metadaten-Konfiguration.

Situation:
- Konfiguriere Stream-Level Parameter
- Bereits gesammelt: {collected_stream_parameters}
- Nächster Parameter: {next_parameter}
- Parameter-Beschreibung: {parameter_description}

Aufgabe:
Stelle eine natürliche Frage nach dem benötigten Stream-Parameter.

Richtlinien:
- Fokussiere auf Stream-Eigenschaften (Name, Beschreibung, Scheduling)
- Erkläre kurz, wofür der Parameter verwendet wird
- Maximal 2 Sätze

Frage:
""")

        # Template für Job-Type Auswahl
        templates["job_type_selection"] = ChatPromptTemplate.from_template("""
Du bist ein freundlicher Assistent für Job-Konfiguration.

Der Stream ist bereits konfiguriert. Jetzt wählen wir den Job-Type für den ersten Job.

User-Nachricht: "{user_message}"

Verfügbare Job-Types:
{job_types}

Aufgabe:
1. Analysiere die User-Nachricht
2. Schlage den wahrscheinlichsten Job-Type vor
3. Erkläre kurz, warum dieser Job-Type passend wäre
4. Frage freundlich nach Bestätigung

Stil: Freundlich, hilfreich, präzise. Maximal 3 Sätze.
""")

        # Template für Parameter-Nachfragen
        templates["parameter_question"] = ChatPromptTemplate.from_template("""
Du bist ein hilfsreicher Assistent für Stream-Konfiguration.

Situation:
- Job-Type: {job_type}
- Bereits gesammelte Parameter: {collected_parameters}
- Nächster benötigter Parameter: {next_parameter}
- Parameter-Beschreibung: {parameter_description}
- Beispielwerte: {examples}

Aufgabe:
Stelle eine natürliche, hilfreiche Frage nach dem benötigten Parameter.

Richtlinien:
- Nutze den vordefinierten chat_prompt als Basis: "{chat_prompt}"
- Erwähne Beispiele wenn sie hilfreich sind
- Sei spezifisch und klar
- Maximal 2 Sätze

Frage:
""")

        # Template für Parameter-Validierung
        templates["validation_feedback"] = ChatPromptTemplate.from_template("""
Du bist ein Qualitäts-Assistent für Stream-Konfiguration.

Der User hat Parameter-Werte angegeben, die validiert werden müssen.

Validierungsergebnis:
- Gültige Parameter: {valid_parameters}
- Fehlerhafte Parameter: {invalid_parameters}
- Fehlende erforderliche Parameter: {missing_parameters}
- Warnungen: {warnings}

Aufgabe:
Gib konstruktives Feedback zu den Parametern.

Stil:
- Positiv beginnen (falls etwas korrekt ist)
- Klar die Probleme benennen
- Konkrete Verbesserungsvorschläge
- Maximal 4 Sätze

Feedback:
""")

        # Template für Completion-Status
        templates["completion_status"] = ChatPromptTemplate.from_template("""
Du bist ein Status-Assistent für Stream-Konfiguration.

Aktuelle Situation:
- Job-Type: {job_type}
- Vervollständigung: {completion_percentage}%
- Gesammelte Parameter: {collected_count}/{total_count}
- Status: {status}

Aufgabe:
Gib eine motivierende Status-Nachricht mit nächsten Schritten.

Stil: Ermutigend, klar, handlungsorientiert. Maximal 3 Sätze.
""")

        return templates

    async def process_user_message(
        self,
        user_message: str,
        session_id: str,
        session_state: Optional[Dict[str, Any]] = None
    ) -> DialogResponse:
        """
        Verarbeitet User-Nachricht und gibt intelligente Antwort

        Args:
            user_message: Nachricht des Users
            session_state: Aktueller Session-State mit Job-Type, Parameter, etc.

        Returns:
            DialogResponse mit nächster Aktion
        """
        try:
            logger.info(f"Verarbeite User-Nachricht: '{user_message[:100]}...'")

            # Hole oder erstelle hierarchische Session
            hierarchical_session = self.hierarchical_manager.get_hierarchical_session(session_id)
            if not hierarchical_session:
                hierarchical_session = self.hierarchical_manager.create_hierarchical_session(session_id)

            # Führe hierarchische Parameter-Extraktion durch
            extraction_result = await self.extractor.extract_hierarchical_parameters(
                user_message=user_message,
                session_context={
                    "session_type": hierarchical_session.session_type,
                    "stream_parameters": hierarchical_session.stream_parameters,
                    "jobs": [job.model_dump() for job in hierarchical_session.jobs]
                }
            )

            # Bestimme Dialog-State basierend auf session_state oder hierarchical_session
            if session_state:
                current_state = DialogState(session_state.get("state", DialogState.INITIAL))
            else:
                current_state = self._determine_state_from_session(hierarchical_session)

            # Route zu spezifischer Handler-Methode (vereinfachter Flow: immer Stream)
            if current_state == DialogState.INITIAL:
                response = await self._handle_initial_state(user_message, extraction_result, session_id)
            elif current_state == DialogState.STREAM_CONFIGURATION:
                response = await self._handle_stream_configuration(user_message, extraction_result, session_id)
            elif current_state == DialogState.JOB_TYPE_SELECTION:
                response = await self._handle_job_type_selection(user_message, extraction_result, session_id)
            elif current_state == DialogState.PARAMETER_COLLECTION:
                response = await self._handle_parameter_collection(user_message, extraction_result, session_id)
            elif current_state == DialogState.VALIDATION:
                response = await self._handle_validation(user_message, extraction_result, session_id)
            else:
                response = await self._handle_fallback(user_message, extraction_result, session_id)

            logger.info(f"Dialog Response: {response.state} | {response.priority}")
            return response

        except Exception as e:
            logger.error(f"Fehler bei Dialog-Verarbeitung: {e}")
            return DialogResponse(
                message="Entschuldigung, es ist ein Fehler aufgetreten. Könnten Sie Ihre Anfrage wiederholen?",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                metadata={"error": str(e)},
                extracted_parameters={}
            )

    def _determine_state_from_session(self, session: HierarchicalStreamSession) -> DialogState:
        """Bestimmt den Dialog-State basierend auf der aktuellen Session (alle Sessions sind Streams)"""

        # Alle Sessions sind vollständige Streams - prüfe Stream-Parameter zuerst
        required_stream_params = ["StreamName", "ShortDescription"]
        missing_stream_params = [p for p in required_stream_params if p not in session.stream_parameters]

        if missing_stream_params:
            return DialogState.STREAM_CONFIGURATION
        elif not session.jobs:
            return DialogState.JOB_TYPE_SELECTION
        else:
            # Prüfe Job-Parameter Vollständigkeit
            incomplete_jobs = [job for job in session.jobs if job.completion_percentage < 1.0]
            if incomplete_jobs:
                return DialogState.PARAMETER_COLLECTION
            else:
                return DialogState.CONFIRMATION

        return DialogState.INITIAL

    def _build_extraction_maps(
        self,
        extraction: HierarchicalExtractionResult,
        min_confidence: float = 0.5
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, float]]:
        stream_params: Dict[str, Any] = {}
        job_params: Dict[str, Any] = {}
        confidence_map: Dict[str, float] = {}

        if extraction:
            # Stream-Parameter
            for param in extraction.stream_parameters:
                if param.confidence >= min_confidence and param.value not in (None, ""):
                    stream_params[param.name] = param.value
                    confidence_map[param.name] = param.confidence

            # Job-Parameter (alle Job-Types)
            for job_type, job_param_list in extraction.job_parameters.items():
                job_params[job_type] = {}
                for param in job_param_list:
                    if param.confidence >= min_confidence and param.value not in (None, ""):
                        job_params[job_type][param.name] = param.value
                        confidence_map[param.name] = param.confidence

        return stream_params, job_params, confidence_map

    async def _handle_initial_state(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Behandelt initiale User-Nachricht - beginnt immer mit Stream-Konfiguration"""

        # Alle Sessions sind vollständige Streams - starte direkt mit Stream-Parameter Sammlung
        session = self.hierarchical_manager.get_hierarchical_session(session_id)
        stream_params, _, confidence_map = self._build_extraction_maps(extraction)

        # Aktualisiere erkannte Stream-Parameter
        if stream_params:
            for param_name, value in stream_params.items():
                session.stream_parameters[param_name] = value

        # Prüfe ob bereits Job-Parameter erkannt wurden
        detected_job_types = []
        if extraction.job_parameters:
            detected_job_types = list(extraction.job_parameters.keys())

        if detected_job_types:
            # Job-Parameter wurden erkannt - weiter zur Job-Konfiguration nach Stream-Parametern
            return DialogResponse(
                message="Perfect! Ich erkenne bereits Job-Parameter in Ihrer Nachricht. 🎯\n\nLassen Sie uns zuerst den Stream konfigurieren und dann die Job-Details verfeinern.\n\nWie soll der Stream heißen?",
                state=DialogState.STREAM_CONFIGURATION,
                priority=DialogPriority.CRITICAL,
                next_parameter="StreamName",
                completion_percentage=10.0,
                extracted_parameters=stream_params,
                parameter_confidences=confidence_map,
                metadata={"detected_job_types": detected_job_types}
            )
        else:
            # Starte mit Stream-Parameter Sammlung
            return DialogResponse(
                message="Willkommen! Ich helfe Ihnen bei der Konfiguration eines StreamWorks-Streams. 🚀\n\nJeder Stream benötigt zuerst grundlegende Eigenschaften. Wie soll Ihr Stream heißen?",
                state=DialogState.STREAM_CONFIGURATION,
                priority=DialogPriority.CRITICAL,
                next_parameter="StreamName",
                completion_percentage=0.0,
                extracted_parameters=stream_params,
                parameter_confidences=confidence_map,
                suggested_questions=[
                    "Der Stream soll 'Datentransfer_Test' heißen",
                    "Ich möchte einen FILE_TRANSFER Stream erstellen",
                    "Zeig mir die benötigten Parameter"
                ]
            )


    async def _handle_stream_configuration(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Behandelt Stream-Parameter Sammlung"""

        session = self.hierarchical_manager.get_hierarchical_session(session_id)
        stream_params, _, confidence_map = self._build_extraction_maps(extraction)

        # Aktualisiere Stream-Parameter
        if stream_params:
            for param_name, value in stream_params.items():
                session.stream_parameters[param_name] = value
                logger.info(f"Stream-Parameter aktualisiert: {param_name} = {value}")

        # Bestimme nächsten fehlenden Parameter
        required_stream_params = {
            "StreamName": "Name des Streams",
            "ShortDescription": "Kurze Beschreibung für die Übersicht"
        }

        missing_params = [name for name, desc in required_stream_params.items()
                         if name not in session.stream_parameters or not session.stream_parameters[name]]

        if missing_params:
            next_param = missing_params[0]
            description = required_stream_params[next_param]

            # Generiere Frage für nächsten Parameter
            question = await self._generate_stream_parameter_question(
                parameter_name=next_param,
                parameter_description=description,
                collected_parameters=session.stream_parameters
            )

            completion = (len(required_stream_params) - len(missing_params)) / len(required_stream_params) * 100

            self.hierarchical_manager.save_hierarchical_session(session)

            return DialogResponse(
                message=question,
                state=DialogState.STREAM_CONFIGURATION,
                priority=DialogPriority.CRITICAL,
                next_parameter=next_param,
                completion_percentage=completion,
                extracted_parameters=stream_params,
                parameter_confidences=confidence_map,
                metadata={"session_type": "STREAM_CONFIGURATION"}
            )
        else:
            # Stream-Parameter vollständig - weiter zu Job-Konfiguration
            self.hierarchical_manager.save_hierarchical_session(session)

            return DialogResponse(
                message=f"Excellent! Stream '{session.stream_parameters.get('StreamName')}' ist konfiguriert. 🎉\n\nJetzt konfigurieren wir den ersten Job. Welchen Job-Type benötigen Sie?",
                state=DialogState.JOB_TYPE_SELECTION,
                priority=DialogPriority.IMPORTANT,
                completion_percentage=100.0,
                extracted_parameters=stream_params,
                suggested_questions=[
                    "Ich brauche einen FILE_TRANSFER Job",
                    "Ich möchte einen STANDARD Job",
                    "Zeig mir alle verfügbaren Job-Types"
                ],
                metadata={"session_type": "STREAM_CONFIGURATION"}
            )

    async def _handle_job_type_selection(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Behandelt Job-Type Auswahl und beginnt Parameter-Sammlung"""

        # Erkenne Job-Type aus hierarchischer Extraktion
        detected_job_type = None
        if extraction.job_parameters:
            # Nimm den ersten erkannten Job-Type
            detected_job_type = list(extraction.job_parameters.keys())[0]

        job_type = detected_job_type

        if job_type:
            # Job-Type bestätigt, beginne Parameter-Sammlung
            job_schema = self.extractor.get_job_type_info(job_type)

            if not job_schema:
                return DialogResponse(
                    message="Entschuldigung, der gewählte Job-Type ist nicht verfügbar. Bitte wählen Sie einen anderen.",
                    state=DialogState.JOB_TYPE_SELECTION,
                    priority=DialogPriority.CRITICAL,
                    extracted_parameters={},
                    metadata={"job_type": job_type}
                )

            # Finde den ersten erforderlichen Parameter
            required_params = [p for p in job_schema["parameters"] if p["required"]]

            if required_params:
                first_param = required_params[0]

                # Generiere natürliche Frage für ersten Parameter
                question = await self._generate_parameter_question(
                    job_type=job_type,
                    parameter_info=first_param,
                    collected_parameters={},
                    context=f"Ich habe '{job_schema['display_name']}' erkannt. Lassen Sie uns mit der Konfiguration beginnen!"
                )

                stream_params, job_params, confidence_map = self._build_extraction_maps(extraction)

                # Speichere Job-Type in Session
                session = self.hierarchical_manager.get_hierarchical_session(session_id)
                job_id = session.add_or_update_job(
                    job_type=job_type,
                    job_parameters=job_params.get(job_type, {}),
                    job_name=f"{job_type}_Job"
                )
                self.hierarchical_manager.save_hierarchical_session(session)

                return DialogResponse(
                    message=question,
                    state=DialogState.PARAMETER_COLLECTION,
                    priority=DialogPriority.CRITICAL,
                    next_parameter=first_param["name"],
                    completion_percentage=0.0,
                    metadata={
                        "job_type": job_type,
                        "total_parameters": len(job_schema["parameters"]),
                        "required_parameters": len(required_params)
                    },
                    extracted_parameters=job_params.get(job_type, {}),
                    parameter_confidences=confidence_map
                )
            else:
                # Keine erforderlichen Parameter - direkt zur Bestätigung
                return DialogResponse(
                    message=f"Perfekt! Der {job_schema['display_name']} ist konfiguriert. Soll ich die XML-Datei generieren?",
                    state=DialogState.CONFIRMATION,
                    priority=DialogPriority.COMPLETE,
                    completion_percentage=100.0,
                    extracted_parameters={},
                    metadata={"job_type": job_type}
                )

        else:
            # Job-Type noch nicht klar - zeige verfügbare Optionen
            job_types_info = self.extractor.get_available_job_types()
            options_text = "\n".join([
                f"🔹 **{jt['display_name']}**: {jt['description']}"
                for jt in job_types_info[:3]  # Nur die ersten 3 zeigen
            ])

            return DialogResponse(
                message=f"Welchen Job-Type möchten Sie konfigurieren?\n\n{options_text}\n\n...oder beschreiben Sie Ihr Vorhaben?",
                state=DialogState.JOB_TYPE_SELECTION,
                priority=DialogPriority.IMPORTANT,
                suggested_questions=[
                    "Ich möchte Dateien übertragen (FILE_TRANSFER)",
                    "Ich brauche einen Standard-Job (STANDARD)",
                    "Zeig mir alle verfügbaren Job-Types"
                ],
                extracted_parameters={}
            )

    async def _handle_parameter_collection(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Behandelt Parameter-Sammlung"""

        session = self.hierarchical_manager.get_hierarchical_session(session_id)
        if not session or not session.jobs:
            return DialogResponse(
                message="Fehler: Kein aktiver Job gefunden. Bitte beginnen Sie von vorn.",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                extracted_parameters={}
            )

        # Finde aktuellen unvollständigen Job
        current_job = None
        for job in session.jobs:
            if job.completion_percentage < 1.0:
                current_job = job
                break

        if not current_job:
            return DialogResponse(
                message="Alle Jobs sind bereits vollständig konfiguriert. Soll ich die XML-Datei generieren?",
                state=DialogState.CONFIRMATION,
                priority=DialogPriority.COMPLETE,
                completion_percentage=100.0,
                extracted_parameters={}
            )

        job_type = current_job.job_type
        current_parameters = current_job.parameters

        # Aktualisiere Parameter mit extrahierten Werten
        updated_parameters = current_parameters.copy()
        stream_params, job_params, confidence_map = self._build_extraction_maps(extraction)

        # Aktualisiere relevante Job-Parameter
        if job_type in job_params:
            for param_name, value in job_params[job_type].items():
                updated_parameters[param_name] = value
                logger.info(
                    "Job-Parameter aktualisiert: %s = %s", param_name, value
                )

        # Speichere aktualisierte Parameter in Session
        current_job.parameters = updated_parameters
        self.hierarchical_manager.save_hierarchical_session(session)

        # Validiere aktuelle Parameter
        validation_result = self._validate_parameters(job_type, updated_parameters)

        # Bestimme nächsten Schritt
        if validation_result.missing_required_parameters:
            # Frage nach nächstem fehlenden Parameter
            next_param_name = validation_result.missing_required_parameters[0]
            job_schema = self.extractor.get_job_type_info(job_type)
            next_param_info = next((p for p in job_schema["parameters"] if p["name"] == next_param_name), None)

            if next_param_info:
                question = await self._generate_parameter_question(
                    job_type=job_type,
                    parameter_info=next_param_info,
                    collected_parameters=updated_parameters
                )

                return DialogResponse(
                    message=question,
                    state=DialogState.PARAMETER_COLLECTION,
                    priority=DialogPriority.CRITICAL,
                    next_parameter=next_param_name,
                    completion_percentage=validation_result.completion_percentage * 100,
                    extracted_parameters=job_params.get(job_type, {}),
                    parameter_confidences=confidence_map,
                    metadata={
                        "job_type": job_type,
                        "parameter_confidences": confidence_map,
                    }
                )

        elif validation_result.errors:
            # Validierungsfehler behandeln
            feedback = await self._generate_validation_feedback(validation_result, updated_parameters)

            return DialogResponse(
                message=feedback,
                state=DialogState.VALIDATION,
                priority=DialogPriority.IMPORTANT,
                validation_issues=validation_result.errors,
                completion_percentage=validation_result.completion_percentage * 100,
                extracted_parameters=job_params.get(job_type, {}),
                parameter_confidences=confidence_map,
                metadata={
                    "job_type": job_type,
                    "parameter_confidences": confidence_map,
                }
            )

        else:
            # Alle erforderlichen Parameter vorhanden
            completion_msg = await self._generate_completion_message(
                job_type, updated_parameters, validation_result
            )

            return DialogResponse(
                message=completion_msg,
                state=DialogState.CONFIRMATION,
                priority=DialogPriority.COMPLETE,
                completion_percentage=100.0,
                extracted_parameters=job_params.get(job_type, {}),
                parameter_confidences=confidence_map,
                metadata={
                    "job_type": job_type,
                    "parameter_confidences": confidence_map,
                }
            )

    async def _handle_validation(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Behandelt Parameter-Validierung und Korrekturen"""

        session = self.hierarchical_manager.get_hierarchical_session(session_id)
        if not session or not session.jobs:
            return DialogResponse(
                message="Fehler: Keine aktive Session gefunden. Bitte beginnen Sie von vorn.",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                extracted_parameters={}
            )

        # Finde aktuellen Job
        current_job = session.jobs[0] if session.jobs else None
        if not current_job:
            return DialogResponse(
                message="Fehler: Kein Job gefunden. Bitte beginnen Sie von vorn.",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                extracted_parameters={}
            )

        job_type = current_job.job_type
        current_parameters = current_job.parameters.copy()

        # Aktualisiere Parameter mit Korrekturen
        stream_params, job_params, confidence_map = self._build_extraction_maps(
            extraction,
            min_confidence=0.7
        )

        # Aktualisiere relevante Job-Parameter
        if job_type in job_params:
            for param_name, value in job_params[job_type].items():
                current_parameters[param_name] = value

        # Speichere aktualisierte Parameter
        current_job.parameters = current_parameters
        self.hierarchical_manager.save_hierarchical_session(session)

        # Re-validiere
        validation_result = self._validate_parameters(job_type, current_parameters)

        if validation_result.is_valid:
            return DialogResponse(
                message="Perfekt! Alle Parameter sind jetzt korrekt. Soll ich die XML-Datei generieren?",
                state=DialogState.CONFIRMATION,
                priority=DialogPriority.COMPLETE,
                completion_percentage=100.0,
                extracted_parameters=job_params.get(job_type, {}),
                parameter_confidences=confidence_map,
                metadata={
                    "job_type": job_type,
                    "parameter_confidences": confidence_map,
                }
            )
        else:
            feedback = await self._generate_validation_feedback(validation_result, current_parameters)
            return DialogResponse(
                message=feedback,
                state=DialogState.VALIDATION,
                priority=DialogPriority.IMPORTANT,
                validation_issues=validation_result.errors,
                extracted_parameters=job_params.get(job_type, {}),
                parameter_confidences=confidence_map,
                metadata={
                    "job_type": job_type,
                    "parameter_confidences": confidence_map,
                }
            )

    async def _handle_fallback(
        self,
        user_message: str,
        extraction: HierarchicalExtractionResult,
        session_id: str
    ) -> DialogResponse:
        """Fallback-Handler für unerwartete Situationen"""

        return DialogResponse(
            message="Entschuldigung, ich bin unsicher wie ich fortfahren soll. Können Sie Ihre Anfrage anders formulieren?",
            state=DialogState.PARAMETER_COLLECTION,
            priority=DialogPriority.IMPORTANT,
            suggested_questions=[
                "Können Sie den Parameter nochmal angeben?",
                "Soll ich von vorne beginnen?",
                "Zeigen Sie mir die verfügbaren Optionen"
            ]
        )

    async def _generate_stream_parameter_question(
        self,
        parameter_name: str,
        parameter_description: str,
        collected_parameters: Dict[str, Any]
    ) -> str:
        """Generiert natürliche Frage für einen Stream-Parameter"""

        template = self.dialog_templates["stream_configuration"]
        chain = template | self.llm

        try:
            response = await chain.ainvoke({
                "collected_stream_parameters": collected_parameters,
                "next_parameter": parameter_name,
                "parameter_description": parameter_description
            })

            return response.content.strip()

        except Exception as e:
            logger.error(f"Fehler bei Stream-Parameter-Frage-Generierung: {e}")
            # Fallback zu einfacher Frage
            if parameter_name == "StreamName":
                return "Wie soll Ihr Stream heißen? Wählen Sie einen aussagekräftigen Namen."
            elif parameter_name == "StreamDocumentation":
                return "Bitte beschreiben Sie ausführlich, was dieser Stream tut und welchen Zweck er erfüllt."
            elif parameter_name == "ShortDescription":
                return "Geben Sie eine kurze, prägnante Beschreibung für die Übersicht an."
            else:
                return f"Bitte geben Sie {parameter_name} an."

    async def _generate_parameter_question(
        self,
        job_type: str,
        parameter_info: Dict[str, Any],
        collected_parameters: Dict[str, Any],
        context: str = ""
    ) -> str:
        """Generiert natürliche Frage für einen Parameter"""

        template = self.dialog_templates["parameter_question"]
        chain = template | self.llm

        examples_text = ", ".join([str(ex) for ex in parameter_info.get("examples", [])[:3]])

        try:
            response = await chain.ainvoke({
                "job_type": job_type,
                "collected_parameters": json.dumps(collected_parameters, indent=2, ensure_ascii=False),
                "next_parameter": parameter_info["name"],
                "parameter_description": parameter_info["description"],
                "examples": examples_text,
                "chat_prompt": parameter_info.get("chat_prompt", f"Bitte geben Sie {parameter_info['name']} an:")
            })

            question = response.content.strip()
            if context:
                return f"{context}\n\n{question}"
            return question

        except Exception as e:
            logger.error(f"Fehler bei Frage-Generierung: {e}")
            # Fallback zur vordefinierten Frage
            base_question = parameter_info.get("chat_prompt", f"Bitte geben Sie {parameter_info['name']} an:")
            if examples_text:
                base_question += f" (z.B. {examples_text})"
            return base_question

    async def _generate_validation_feedback(
        self,
        validation_result: ParameterValidationResult,
        parameters: Dict[str, Any]
    ) -> str:
        """Generiert Validierungs-Feedback"""

        template = self.dialog_templates["validation_feedback"]
        chain = template | self.llm

        try:
            response = await chain.ainvoke({
                "valid_parameters": [k for k, v in parameters.items() if v is not None],
                "invalid_parameters": validation_result.errors,
                "missing_parameters": validation_result.missing_required_parameters,
                "warnings": validation_result.warnings
            })

            return response.content.strip()

        except Exception as e:
            logger.error(f"Fehler bei Feedback-Generierung: {e}")
            # Fallback zu einfachem Feedback
            if validation_result.errors:
                return f"Es gibt Probleme mit folgenden Parametern: {', '.join(validation_result.errors[:3])}. Bitte korrigieren Sie diese."
            return "Bitte überprüfen Sie Ihre Angaben."

    async def _generate_completion_message(
        self,
        job_type: str,
        parameters: Dict[str, Any],
        validation_result: ParameterValidationResult
    ) -> str:
        """Generiert Completion-Nachricht"""

        template = self.dialog_templates["completion_status"]
        chain = template | self.llm

        try:
            response = await chain.ainvoke({
                "job_type": job_type,
                "completion_percentage": int(validation_result.completion_percentage * 100),
                "collected_count": len([v for v in parameters.values() if v is not None]),
                "total_count": len(parameters),
                "status": "completed" if validation_result.is_valid else "needs_review"
            })

            return response.content.strip()

        except Exception as e:
            logger.error(f"Fehler bei Completion-Nachricht: {e}")
            return f"Konfiguration für {job_type} ist abgeschlossen! Soll ich die XML-Datei generieren?"

    def _validate_parameters(
        self,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> ParameterValidationResult:
        """Validiert Parameter gegen Job-Type Schema"""

        try:
            # Hole Schema
            job_schema = self.extractor.get_job_type_info(job_type)
            if not job_schema:
                return ParameterValidationResult(
                    is_valid=False,
                    errors=[f"Unbekannter Job-Type: {job_type}"],
                    completion_percentage=0.0,
                    missing_required_parameters=[]
                )

            # Prüfe erforderliche Parameter
            required_params = [p["name"] for p in job_schema["parameters"] if p["required"]]
            missing_required = [name for name in required_params if parameters.get(name) is None]

            # Prüfe Validierungsregeln
            errors = []
            warnings = []

            for param_schema in job_schema["parameters"]:
                param_name = param_schema["name"]
                param_value = parameters.get(param_name)

                if param_value is not None:
                    # Typ-Validierung
                    expected_type = param_schema.get("data_type", "string")
                    if not self._validate_parameter_type(param_value, expected_type):
                        errors.append(f"{param_name}: Falscher Datentyp (erwartet: {expected_type})")

                    # Enum-Validierung
                    enum_values = param_schema.get("enum_values")
                    if enum_values and param_value not in enum_values:
                        errors.append(f"{param_name}: Wert muss einer von {enum_values} sein")

                    # Pattern-Validierung (simpel)
                    pattern = param_schema.get("validation_pattern")
                    if pattern and isinstance(param_value, str):
                        import re
                        if not re.match(pattern, param_value):
                            warnings.append(f"{param_name}: Format entspricht nicht dem erwarteten Muster")

            # Berechne Completion-Percentage
            total_params = len(job_schema["parameters"])
            filled_params = len([v for v in parameters.values() if v is not None])
            completion_percentage = filled_params / total_params if total_params > 0 else 0.0

            is_valid = len(errors) == 0 and len(missing_required) == 0

            return ParameterValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                completion_percentage=completion_percentage,
                missing_required_parameters=missing_required
            )

        except Exception as e:
            logger.error(f"Fehler bei Parameter-Validierung: {e}")
            return ParameterValidationResult(
                is_valid=False,
                errors=[f"Validierungsfehler: {str(e)}"],
                completion_percentage=0.0,
                missing_required_parameters=[]
            )

    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validiert Datentyp eines Parameters"""

        try:
            if expected_type == "string":
                return isinstance(value, str)
            elif expected_type == "integer":
                return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            elif expected_type == "boolean":
                return isinstance(value, bool) or (isinstance(value, str) and value.lower() in ["true", "false", "ja", "nein", "yes", "no"])
            elif expected_type == "enum":
                return isinstance(value, str)  # Enum-Werte werden separat validiert
            else:
                return True  # Unbekannte Typen durchlassen

        except Exception:
            return False

# ================================
# FACTORY FUNCTION
# ================================

_dialog_manager_instance: Optional[IntelligentDialogManager] = None

def get_intelligent_dialog_manager(
    parameter_extractor: SmartParameterExtractor = None,
    hierarchical_state_manager: HierarchicalParameterStateManager = None,
    openai_api_key: str = None
) -> IntelligentDialogManager:
    """Factory function für IntelligentDialogManager"""
    global _dialog_manager_instance

    if _dialog_manager_instance is None:
        if not parameter_extractor:
            from services.ai.smart_parameter_extractor import get_smart_parameter_extractor
            parameter_extractor = get_smart_parameter_extractor()

        if not hierarchical_state_manager:
            from services.ai.parameter_state_manager import get_hierarchical_parameter_state_manager
            hierarchical_state_manager = get_hierarchical_parameter_state_manager()

        if not openai_api_key:
            from config import settings
            openai_api_key = settings.OPENAI_API_KEY

        _dialog_manager_instance = IntelligentDialogManager(
            parameter_extractor=parameter_extractor,
            hierarchical_state_manager=hierarchical_state_manager,
            openai_api_key=openai_api_key
        )

    return _dialog_manager_instance
