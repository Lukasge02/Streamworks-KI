"""
Parameter Extractor Service - Phase 0.2
Automatische Generierung von Job-Type spezifischen Parameter-Checklisten für die Chat-Führung
Lädt die generierten Schemas aus Phase 0.1 und wandelt sie in chat-optimierte Datenstrukturen um
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from services.schema_analyzer import get_schema_analyzer, JobTypeSchema, ParameterDefinition

logger = logging.getLogger(__name__)

class ParameterStatus(Enum):
    """Status eines Parameters während der Chat-Sammlung"""
    MISSING = "missing"
    PARTIAL = "partial"
    COMPLETE = "complete"
    INVALID = "invalid"

@dataclass
class ChatParameter:
    """Chat-optimierte Parameter-Darstellung"""
    name: str
    display_name: str
    data_type: str
    required: bool
    description: str
    chat_prompt: str
    examples: List[str]
    validation_pattern: Optional[str] = None
    enum_values: Optional[List[str]] = None
    default_value: Optional[str] = None

    # Chat-spezifische Eigenschaften
    status: ParameterStatus = ParameterStatus.MISSING
    current_value: Optional[Any] = None
    retry_count: int = 0
    collection_order: int = 0

    # Kontext für intelligente Sammlung
    depends_on: List[str] = None  # Parameter, die zuerst gesammelt werden müssen
    suggests: List[str] = None    # Parameter, die nach diesem sinnvoll sind
    validation_error: Optional[str] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.suggests is None:
            self.suggests = []

@dataclass
class ParameterChecklist:
    """Vollständige Checkliste für einen Job-Type"""
    job_type: str
    display_name: str
    description: str
    complexity: str
    estimated_time: str
    icon: str

    parameters: List[ChatParameter]
    completion_percentage: float = 0.0

    # Chat-Flow Eigenschaften
    next_parameter: Optional[str] = None
    completed_parameters: List[str] = None
    missing_parameters: List[str] = None
    invalid_parameters: List[str] = None

    def __post_init__(self):
        if self.completed_parameters is None:
            self.completed_parameters = []
        if self.missing_parameters is None:
            self.missing_parameters = []
        if self.invalid_parameters is None:
            self.invalid_parameters = []

class ParameterExtractor:
    """Service für Chat-optimierte Parameter-Extraktion und -Verwaltung"""

    def __init__(self):
        """Initialize the parameter extractor"""
        self.schema_analyzer = get_schema_analyzer()
        self.job_schemas: Dict[str, JobTypeSchema] = {}
        self.parameter_checklists: Dict[str, ParameterChecklist] = {}

        logger.info("Parameter Extractor initialized")

    async def initialize(self) -> None:
        """Lädt Schemas und erstellt Parameter-Checklisten"""
        try:
            # Lade Job-Type Schemas
            self.job_schemas = self.schema_analyzer.load_schemas()

            if not self.job_schemas:
                logger.info("No schemas found, generating new ones...")
                from services.schema_analyzer import analyze_schemas_if_needed
                self.job_schemas = await analyze_schemas_if_needed()

            # Erstelle Chat-optimierte Checklisten
            self._create_parameter_checklists()

            logger.info(f"Parameter Extractor initialized with {len(self.parameter_checklists)} job types")

        except Exception as e:
            logger.error(f"Failed to initialize Parameter Extractor: {str(e)}")
            raise

    def _create_parameter_checklists(self) -> None:
        """Konvertiert JobTypeSchemas zu ChatParameter-Checklisten"""

        for job_type, schema in self.job_schemas.items():
            # Konvertiere Parameter zu ChatParameter
            chat_parameters = []

            for i, param_def in enumerate(schema.parameters):
                chat_param = ChatParameter(
                    name=param_def.name,
                    display_name=self._humanize_parameter_name(param_def.name),
                    data_type=param_def.data_type,
                    required=param_def.required,
                    description=param_def.description,
                    chat_prompt=param_def.chat_prompt or self._generate_default_prompt(param_def),
                    examples=param_def.examples or [],
                    validation_pattern=param_def.validation_pattern,
                    enum_values=param_def.enum_values,
                    default_value=param_def.default_value,
                    collection_order=i * 10  # Leave space for re-ordering
                )

                # Setze Abhängigkeiten für intelligente Sammlung
                self._set_parameter_dependencies(chat_param, job_type)

                chat_parameters.append(chat_param)

            # Erstelle Checkliste
            checklist = ParameterChecklist(
                job_type=job_type,
                display_name=schema.display_name,
                description=schema.description,
                complexity=schema.complexity,
                estimated_time=schema.estimated_time,
                icon=schema.icon,
                parameters=chat_parameters
            )

            # Berechne initial missing parameters
            self._update_checklist_status(checklist)

            self.parameter_checklists[job_type] = checklist

    def _humanize_parameter_name(self, param_name: str) -> str:
        """Macht Parameter-Namen benutzerfreundlicher"""
        # Convert camelCase/snake_case to readable names
        import re

        # Split on camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', param_name)
        # Split on snake_case
        name = name.replace('_', ' ')
        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())

        return name

    def _generate_default_prompt(self, param_def: ParameterDefinition) -> str:
        """Generiert Standard-Chat-Prompt wenn keiner vorhanden"""
        human_name = self._humanize_parameter_name(param_def.name)

        if param_def.data_type == "enum" and param_def.enum_values:
            options = ", ".join(param_def.enum_values)
            return f"Welchen {human_name} möchten Sie wählen? ({options})"
        elif param_def.data_type == "boolean":
            return f"Soll {human_name} aktiviert werden? (ja/nein)"
        elif param_def.required:
            return f"Bitte geben Sie {human_name} an:"
        else:
            return f"Möchten Sie {human_name} festlegen? (optional)"

    def _set_parameter_dependencies(self, chat_param: ChatParameter, job_type: str) -> None:
        """Setzt intelligente Parameter-Abhängigkeiten"""

        # Job-Type spezifische Abhängigkeiten
        if job_type == "STANDARD":
            if chat_param.name == "job_name":
                chat_param.depends_on = ["stream_name"]
            elif chat_param.name == "script":
                chat_param.suggests = ["job_name"]

        elif job_type == "FILE_TRANSFER":
            if chat_param.name == "target_path":
                chat_param.depends_on = ["source_path", "target_agent"]
            elif chat_param.name == "target_agent":
                chat_param.depends_on = ["source_agent"]

        elif job_type == "SAP":
            if chat_param.name == "variant":
                chat_param.depends_on = ["system", "report"]
            elif chat_param.name == "batch_user":
                chat_param.depends_on = ["system"]

    def get_job_types(self) -> Dict[str, Dict[str, Any]]:
        """Gibt verfügbare Job-Types mit Metadaten zurück"""
        job_types = {}

        for job_type, checklist in self.parameter_checklists.items():
            job_types[job_type] = {
                "display_name": checklist.display_name,
                "description": checklist.description,
                "complexity": checklist.complexity,
                "estimated_time": checklist.estimated_time,
                "icon": checklist.icon,
                "parameter_count": len(checklist.parameters),
                "required_parameters": len([p for p in checklist.parameters if p.required])
            }

        return job_types

    def get_parameter_checklist(self, job_type: str) -> Optional[ParameterChecklist]:
        """Gibt Parameter-Checkliste für Job-Type zurück"""
        return self.parameter_checklists.get(job_type)

    def update_parameter_value(self, job_type: str, param_name: str, value: Any) -> bool:
        """Aktualisiert Parameter-Wert und Status"""
        checklist = self.parameter_checklists.get(job_type)
        if not checklist:
            return False

        # Finde Parameter
        parameter = None
        for param in checklist.parameters:
            if param.name == param_name:
                parameter = param
                break

        if not parameter:
            return False

        # Validiere Wert
        is_valid, error_msg = self._validate_parameter_value(parameter, value)

        if is_valid:
            parameter.current_value = value
            parameter.status = ParameterStatus.COMPLETE
            parameter.validation_error = None
        else:
            parameter.status = ParameterStatus.INVALID
            parameter.validation_error = error_msg
            parameter.retry_count += 1

        # Aktualisiere Checklisten-Status
        self._update_checklist_status(checklist)

        return is_valid

    def _validate_parameter_value(self, parameter: ChatParameter, value: Any) -> Tuple[bool, Optional[str]]:
        """Validiert Parameter-Wert"""

        if value is None or str(value).strip() == "":
            if parameter.required:
                return False, f"{parameter.display_name} ist ein Pflichtfeld"
            return True, None

        # Typ-spezifische Validierung
        if parameter.data_type == "integer":
            try:
                int(value)
            except ValueError:
                return False, f"{parameter.display_name} muss eine Zahl sein"

        elif parameter.data_type == "boolean":
            if str(value).lower() not in ["true", "false", "ja", "nein", "yes", "no", "1", "0"]:
                return False, f"{parameter.display_name} muss ja/nein sein"

        elif parameter.data_type == "enum" and parameter.enum_values:
            if str(value) not in parameter.enum_values:
                valid_options = ", ".join(parameter.enum_values)
                return False, f"{parameter.display_name} muss einer dieser Werte sein: {valid_options}"

        # Pattern-Validierung
        if parameter.validation_pattern:
            import re
            if not re.match(parameter.validation_pattern, str(value)):
                return False, f"{parameter.display_name} entspricht nicht dem erwarteten Format"

        return True, None

    def _update_checklist_status(self, checklist: ParameterChecklist) -> None:
        """Aktualisiert den Status der gesamten Checkliste"""

        completed = []
        missing = []
        invalid = []

        for param in checklist.parameters:
            if param.status == ParameterStatus.COMPLETE:
                completed.append(param.name)
            elif param.status == ParameterStatus.INVALID:
                invalid.append(param.name)
            elif param.required or param.current_value is not None:
                missing.append(param.name)

        checklist.completed_parameters = completed
        checklist.missing_parameters = missing
        checklist.invalid_parameters = invalid

        # Berechne Completion-Percentage (nur required parameters)
        required_params = [p for p in checklist.parameters if p.required]
        completed_required = [p for p in required_params if p.status == ParameterStatus.COMPLETE]

        if required_params:
            checklist.completion_percentage = len(completed_required) / len(required_params) * 100
        else:
            checklist.completion_percentage = 100

        # Bestimme nächsten Parameter
        checklist.next_parameter = self._determine_next_parameter(checklist)

    def _determine_next_parameter(self, checklist: ParameterChecklist) -> Optional[str]:
        """Bestimmt den nächsten Parameter, der gesammelt werden sollte"""

        # Sortiere Parameter nach Collection-Order und Abhängigkeiten
        available_params = []

        for param in checklist.parameters:
            if param.status in [ParameterStatus.MISSING, ParameterStatus.INVALID]:
                # Prüfe ob Abhängigkeiten erfüllt sind
                dependencies_met = True
                for dep_name in param.depends_on:
                    dep_param = next((p for p in checklist.parameters if p.name == dep_name), None)
                    if not dep_param or dep_param.status != ParameterStatus.COMPLETE:
                        dependencies_met = False
                        break

                if dependencies_met:
                    available_params.append(param)

        if not available_params:
            return None

        # Priorisiere: Required > Invalid (retry) > Optional, dann nach Collection-Order
        available_params.sort(key=lambda p: (
            not p.required,  # Required first
            p.status != ParameterStatus.INVALID,  # Invalid (retry) before missing
            p.collection_order  # Then by order
        ))

        return available_params[0].name

    def get_missing_parameters(self, job_type: str) -> List[ChatParameter]:
        """Gibt fehlende Parameter zurück"""
        checklist = self.parameter_checklists.get(job_type)
        if not checklist:
            return []

        return [p for p in checklist.parameters
                if p.status in [ParameterStatus.MISSING, ParameterStatus.INVALID]]

    def get_next_parameter_prompt(self, job_type: str) -> Optional[Tuple[ChatParameter, str]]:
        """Gibt den nächsten Parameter und optimierten Chat-Prompt zurück"""
        checklist = self.parameter_checklists.get(job_type)
        if not checklist or not checklist.next_parameter:
            return None

        param = next((p for p in checklist.parameters if p.name == checklist.next_parameter), None)
        if not param:
            return None

        # Erstelle kontextuellen Prompt
        prompt = param.chat_prompt

        # Füge Beispiele hinzu wenn verfügbar
        if param.examples:
            examples_str = ", ".join(str(ex) for ex in param.examples[:3])
            prompt += f"\n\nBeispiele: {examples_str}"

        # Füge Retry-Hinweise hinzu
        if param.status == ParameterStatus.INVALID and param.validation_error:
            prompt = f"❌ {param.validation_error}\n\n{prompt}"

        # Füge Progress-Info hinzu
        progress_info = f"\n\n📊 Fortschritt: {checklist.completion_percentage:.0f}% ({len(checklist.completed_parameters)}/{len([p for p in checklist.parameters if p.required])} Pflichtfelder)"
        prompt += progress_info

        return param, prompt

    def extract_collected_parameters(self, job_type: str) -> Dict[str, Any]:
        """Extrahiert alle gesammelten Parameter für XML-Generierung"""
        checklist = self.parameter_checklists.get(job_type)
        if not checklist:
            return {}

        extracted = {}
        for param in checklist.parameters:
            if param.status == ParameterStatus.COMPLETE and param.current_value is not None:
                # Konvertiere Werte entsprechend dem Datentyp
                value = param.current_value

                if param.data_type == "integer":
                    value = int(value)
                elif param.data_type == "boolean":
                    value = str(value).lower() in ["true", "ja", "yes", "1"]

                extracted[param.name] = value

        return extracted

    def reset_parameter_collection(self, job_type: str) -> None:
        """Setzt Parameter-Sammlung für Job-Type zurück"""
        checklist = self.parameter_checklists.get(job_type)
        if not checklist:
            return

        for param in checklist.parameters:
            param.status = ParameterStatus.MISSING
            param.current_value = None
            param.retry_count = 0
            param.validation_error = None

        self._update_checklist_status(checklist)

# Singleton instance
_parameter_extractor = None

def get_parameter_extractor() -> ParameterExtractor:
    """Get parameter extractor singleton"""
    global _parameter_extractor
    if _parameter_extractor is None:
        _parameter_extractor = ParameterExtractor()
    return _parameter_extractor