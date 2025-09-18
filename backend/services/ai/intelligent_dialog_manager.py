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

from services.ai.smart_parameter_extractor import SmartParameterExtractor, ParameterExtractionResult
from models.parameter_models import (
    JOB_TYPE_MODEL_MAPPING,
    ParameterValidationResult,
    create_parameter_instance
)

logger = logging.getLogger(__name__)

# ================================
# DIALOG STATE MANAGEMENT
# ================================

class DialogState(str, Enum):
    """Status des Dialog-Flows"""
    INITIAL = "initial"              # Neuer Dialog, Job-Type noch unbekannt
    JOB_TYPE_SELECTION = "job_type_selection"  # User wählt Job-Type
    PARAMETER_COLLECTION = "parameter_collection"  # Parameter werden gesammelt
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
        extracted_parameters: List[str] = None,
        next_parameter: str = None,
        completion_percentage: float = 0.0,
        validation_issues: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.message = message
        self.state = state
        self.priority = priority
        self.suggested_questions = suggested_questions or []
        self.extracted_parameters = extracted_parameters or []
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
        openai_api_key: str
    ):
        self.extractor = parameter_extractor
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.2  # Leicht kreativer für natürliche Dialoge
        )

        # Dialog Templates
        self.dialog_templates = self._load_dialog_templates()

        logger.info("IntelligentDialogManager initialisiert")

    def _load_dialog_templates(self) -> Dict[str, ChatPromptTemplate]:
        """Lädt vordefinierte Dialog-Templates"""

        templates = {}

        # Template für Job-Type Auswahl
        templates["job_type_selection"] = ChatPromptTemplate.from_template("""
Du bist ein freundlicher Assistent für Stream-Konfiguration.

Der User hat eine Anfrage gestellt, aber es ist noch nicht klar, welchen Job-Type er erstellen möchte.

User-Nachricht: "{user_message}"

Verfügbare Job-Types:
{job_types}

Aufgabe:
1. Analysiere die User-Nachricht
2. Schlage den wahrscheinlichsten Job-Type vor
3. Erkläre kurz, warum dieser Job-Type passend wäre
4. Frage freundlich nach Bestätigung oder Korrektur

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
        session_state: Dict[str, Any]
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

            # Extrahiere Parameter aus User-Nachricht
            extraction_result = await self.extractor.extract_parameters(
                user_message=user_message,
                current_job_type=session_state.get("job_type"),
                existing_parameters=session_state.get("parameters", {})
            )

            # Bestimme Dialog-State
            current_state = DialogState(session_state.get("state", DialogState.INITIAL))

            # Route zu spezifischer Handler-Methode
            if current_state == DialogState.INITIAL or not session_state.get("job_type"):
                response = await self._handle_initial_state(user_message, extraction_result)
            elif current_state == DialogState.JOB_TYPE_SELECTION:
                response = await self._handle_job_type_selection(user_message, extraction_result, session_state)
            elif current_state == DialogState.PARAMETER_COLLECTION:
                response = await self._handle_parameter_collection(user_message, extraction_result, session_state)
            elif current_state == DialogState.VALIDATION:
                response = await self._handle_validation(user_message, extraction_result, session_state)
            else:
                response = await self._handle_fallback(user_message, extraction_result, session_state)

            logger.info(f"Dialog Response: {response.state} | {response.priority}")
            return response

        except Exception as e:
            logger.error(f"Fehler bei Dialog-Verarbeitung: {e}")
            return DialogResponse(
                message="Entschuldigung, es ist ein Fehler aufgetreten. Könnten Sie Ihre Anfrage wiederholen?",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL,
                metadata={"error": str(e)}
            )

    async def _handle_initial_state(
        self,
        user_message: str,
        extraction: ParameterExtractionResult
    ) -> DialogResponse:
        """Behandelt initiale User-Nachricht"""

        if extraction.job_type:
            # Job-Type wurde erkannt
            job_types_info = self.extractor.get_available_job_types()
            job_type_details = next(
                (jt for jt in job_types_info if jt["job_type"] == extraction.job_type),
                None
            )

            if job_type_details:
                # Generiere Bestätigungs-Nachricht
                template = self.dialog_templates["job_type_selection"]
                chain = template | self.llm

                job_types_text = "\n".join([
                    f"- {jt['display_name']}: {jt['description']}"
                    for jt in job_types_info
                ])

                response = await chain.ainvoke({
                    "user_message": user_message,
                    "job_types": job_types_text
                })

                return DialogResponse(
                    message=response.content,
                    state=DialogState.JOB_TYPE_SELECTION,
                    priority=DialogPriority.IMPORTANT,
                    extracted_parameters=[extraction.job_type],
                    metadata={
                        "suggested_job_type": extraction.job_type,
                        "confidence": extraction.confidence_score
                    }
                )

        # Fallback: Job-Type Selection
        job_types_info = self.extractor.get_available_job_types()
        options_text = "\n".join([
            f"🔹 **{jt['display_name']}**: {jt['description']} (ca. {jt['estimated_time']})"
            for jt in job_types_info
        ])

        return DialogResponse(
            message=f"Gerne helfe ich Ihnen bei der Stream-Konfiguration! 🚀\n\nWelchen Job-Type möchten Sie erstellen?\n\n{options_text}",
            state=DialogState.JOB_TYPE_SELECTION,
            priority=DialogPriority.CRITICAL,
            suggested_questions=[
                "Ich möchte einen Standard-Stream erstellen",
                "Ich brauche einen SAP-Report",
                "Ich möchte Dateien übertragen",
                "Ich brauche eine benutzerdefinierte Konfiguration"
            ]
        )

    async def _handle_job_type_selection(
        self,
        user_message: str,
        extraction: ParameterExtractionResult,
        session_state: Dict[str, Any]
    ) -> DialogResponse:
        """Behandelt Job-Type Auswahl und beginnt Parameter-Sammlung"""

        job_type = extraction.job_type or session_state.get("suggested_job_type")

        if job_type:
            # Job-Type bestätigt, beginne Parameter-Sammlung
            job_schema = self.extractor.get_job_type_info(job_type)

            if not job_schema:
                return DialogResponse(
                    message="Entschuldigung, der gewählte Job-Type ist nicht verfügbar. Bitte wählen Sie einen anderen.",
                    state=DialogState.JOB_TYPE_SELECTION,
                    priority=DialogPriority.CRITICAL
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
                    context="Lassen Sie uns mit der Konfiguration beginnen!"
                )

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
                    }
                )
            else:
                # Keine erforderlichen Parameter - direkt zur Bestätigung
                return DialogResponse(
                    message=f"Perfekt! Der {job_schema['display_name']} ist konfiguriert. Soll ich die XML-Datei generieren?",
                    state=DialogState.CONFIRMATION,
                    priority=DialogPriority.COMPLETE,
                    completion_percentage=100.0
                )

        else:
            # Job-Type noch nicht klar
            return DialogResponse(
                message="Ich konnte nicht eindeutig bestimmen, welchen Job-Type Sie möchten. Könnten Sie es spezifischer formulieren?",
                state=DialogState.JOB_TYPE_SELECTION,
                priority=DialogPriority.IMPORTANT,
                suggested_questions=extraction.suggested_questions
            )

    async def _handle_parameter_collection(
        self,
        user_message: str,
        extraction: ParameterExtractionResult,
        session_state: Dict[str, Any]
    ) -> DialogResponse:
        """Behandelt Parameter-Sammlung"""

        job_type = session_state.get("job_type")
        current_parameters = session_state.get("parameters", {})

        if not job_type:
            return DialogResponse(
                message="Fehler: Job-Type ist nicht gesetzt. Bitte beginnen Sie von vorn.",
                state=DialogState.INITIAL,
                priority=DialogPriority.CRITICAL
            )

        # Aktualisiere Parameter mit extrahierten Werten
        updated_parameters = current_parameters.copy()

        for param in extraction.extracted_parameters:
            if param.confidence >= 0.5:  # Nur Parameter mit ausreichender Konfidenz
                updated_parameters[param.name] = param.value
                logger.info(f"Parameter aktualisiert: {param.name} = {param.value} (Konfidenz: {param.confidence})")

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
                    extracted_parameters=[p.name for p in extraction.extracted_parameters if p.confidence >= 0.5]
                )

        elif validation_result.errors:
            # Validierungsfehler behandeln
            feedback = await self._generate_validation_feedback(validation_result, updated_parameters)

            return DialogResponse(
                message=feedback,
                state=DialogState.VALIDATION,
                priority=DialogPriority.IMPORTANT,
                validation_issues=validation_result.errors,
                completion_percentage=validation_result.completion_percentage * 100
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
                extracted_parameters=[p.name for p in extraction.extracted_parameters if p.confidence >= 0.5]
            )

    async def _handle_validation(
        self,
        user_message: str,
        extraction: ParameterExtractionResult,
        session_state: Dict[str, Any]
    ) -> DialogResponse:
        """Behandelt Parameter-Validierung und Korrekturen"""

        job_type = session_state.get("job_type")
        current_parameters = session_state.get("parameters", {})

        # Aktualisiere Parameter mit Korrekturen
        for param in extraction.extracted_parameters:
            if param.confidence >= 0.7:  # Höhere Konfidenz für Korrekturen
                current_parameters[param.name] = param.value

        # Re-validiere
        validation_result = self._validate_parameters(job_type, current_parameters)

        if validation_result.is_valid:
            return DialogResponse(
                message="Perfekt! Alle Parameter sind jetzt korrekt. Soll ich die XML-Datei generieren?",
                state=DialogState.CONFIRMATION,
                priority=DialogPriority.COMPLETE,
                completion_percentage=100.0
            )
        else:
            feedback = await self._generate_validation_feedback(validation_result, current_parameters)
            return DialogResponse(
                message=feedback,
                state=DialogState.VALIDATION,
                priority=DialogPriority.IMPORTANT,
                validation_issues=validation_result.errors
            )

    async def _handle_fallback(
        self,
        user_message: str,
        extraction: ParameterExtractionResult,
        session_state: Dict[str, Any]
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
    openai_api_key: str = None
) -> IntelligentDialogManager:
    """Factory function für IntelligentDialogManager"""
    global _dialog_manager_instance

    if _dialog_manager_instance is None:
        if not parameter_extractor:
            from services.ai.smart_parameter_extractor import get_smart_parameter_extractor
            parameter_extractor = get_smart_parameter_extractor()

        if not openai_api_key:
            from backend.config import get_settings
            settings = get_settings()
            openai_api_key = settings.openai_api_key

        _dialog_manager_instance = IntelligentDialogManager(
            parameter_extractor=parameter_extractor,
            openai_api_key=openai_api_key
        )

    return _dialog_manager_instance