"""
Intelligent Conversation Engine for XML Stream Creation
Handles context-aware conversation flows and entity extraction with Multi-Language Support
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from schemas.xml_streams import JobType, ConversationState

logger = logging.getLogger(__name__)

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from user message"""
    field_name: str
    value: Any
    confidence: float
    source_text: str

class ConversationStep(Enum):
    """Steps in the conversation flow"""
    JOB_TYPE_DETECTION = "job_type_detection"
    SAP_SYSTEM = "sap_system"
    SAP_REPORT = "sap_report"
    FILE_SOURCE = "file_source"
    FILE_TARGET = "file_target"
    FILE_OPTIONS = "file_options"
    STANDARD_SCRIPT = "standard_script"
    STANDARD_AGENT = "standard_agent"
    SCHEDULE_SETUP = "schedule_setup"
    FINAL_REVIEW = "final_review"
    COMPLETED = "completed"

class ConversationEngine:
    """Enhanced intelligent conversation engine for XML stream creation with Multi-Language Support"""

    def __init__(self, template_config_path: Optional[str] = None):
        """Initialize with template configuration and conversation flows"""
        # Load template configuration
        self.template_config = self._load_template_config(template_config_path)
        self.confidence_weights = self.template_config.get("entity_patterns", {}).get("confidence_weights", {})

        # Initialize conversation flows
        self.conversation_flows = {
            JobType.SAP: [
                ConversationStep.SAP_SYSTEM,
                ConversationStep.SAP_REPORT,
                ConversationStep.SCHEDULE_SETUP,
                ConversationStep.FINAL_REVIEW
            ],
            JobType.FILE_TRANSFER: [
                ConversationStep.FILE_SOURCE,
                ConversationStep.FILE_TARGET,
                ConversationStep.FILE_OPTIONS,
                ConversationStep.SCHEDULE_SETUP,
                ConversationStep.FINAL_REVIEW
            ],
            JobType.STANDARD: [
                ConversationStep.STANDARD_SCRIPT,
                ConversationStep.STANDARD_AGENT,
                ConversationStep.SCHEDULE_SETUP,
                ConversationStep.FINAL_REVIEW
            ]
        }

    def _load_template_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load template configuration from file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "templates" / "template_config.json"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template config: {str(e)}")
            return {"job_types": {}, "entity_patterns": {}, "conversation_prompts": {}}

    # Required fields for each job type - dynamically loaded from config
    @property
    def REQUIRED_FIELDS(self) -> Dict[JobType, List[str]]:
        """Dynamic required fields based on template configuration"""
        return {
            JobType.SAP: [
                "jobForm.sapSystem",
                "jobForm.reportName",
                "streamProperties.streamName"
            ],
            JobType.FILE_TRANSFER: [
                "jobForm.sourcePath",
                "jobForm.targetPath",
                "streamProperties.streamName"
            ],
            JobType.STANDARD: [
                "jobForm.scriptPath",
                "jobForm.agentName",
                "streamProperties.streamName"
            ]
        }

    def _get_dynamic_patterns(self) -> Dict[str, List[str]]:
        """Get patterns from template configuration and base patterns"""
        base_patterns = {
            # SAP patterns
            "sap_system": [
                r"\b([A-Z]\d{2})\b",  # P01, T01, etc.
                r"system\s+([A-Z]\d{2})",
                r"SAP\s+([A-Z]\d{2})"
            ],
            "report_name": [
                r"\b(Z_[A-Z0-9_]+)\b",  # Custom reports
                r"report\s+([A-Z0-9_]+)",
                r"\b([A-Z]{2,}[0-9]{2,})\b"  # Standard reports
            ],

            # File transfer patterns
            "file_path": [
                r"([A-Za-z]:\\[^\\]+(?:\\[^\\]+)*)",  # Windows paths
                r"(/[^/\s]+(?:/[^/\s]+)*)",  # Unix paths
                r"\\\\[^\\]+\\[^\\]+(?:\\[^\\]+)*"  # Network paths
            ],
            "server_name": [
                r"\b([A-Z]{2,}[A-Z0-9]*[-_][A-Z0-9]+)\b",  # SERVER-01, APP-SERVER, DB_SERVER (mindestens 2 Großbuchstaben)
                r"\b([A-Z][A-Z0-9]*[0-9]{2,})\b",  # SERVER01, APP123 (Großbuchstabe + mind. 2 Ziffern)
                r"server\s+([A-Za-z]{3,}[0-9-_]+)",  # "server ABC123"
                r"von\s+([A-Z]{2,}[A-Z0-9-_]*)\s+(?:nach|zu)",  # "von SERVER01 nach"
                r"nach\s+([A-Z]{2,}[A-Z0-9-_]*)"  # "nach SERVER02"
            ],

            # Standard job patterns
            "script_name": [
                r"\b([a-zA-Z0-9_-]+\.(?:bat|sh|ps1|py))\b",  # Script files
                r"script\s+([a-zA-Z0-9_.-]+)",
                r"ausführen\s+([a-zA-Z0-9_.-]+)"
            ],
            "agent_name": [
                r"\bagent\s+([A-Za-z0-9-_]+)\b",
                r"\b(AGENT[A-Z0-9_]*)\b",
                r"auf\s+([A-Za-z0-9-_]+)\s+agent"
            ],

            # Schedule patterns
            "time": [
                r"\b(\d{1,2}):(\d{2})\b",  # 06:00
                r"\b(\d{1,2})\s*Uhr\b",  # 6 Uhr
                r"um\s+(\d{1,2}:\d{2})",  # um 06:00
            ],
            "frequency": [
                r"\b(täglich|daily)\b",
                r"\b(wöchentlich|weekly)\b",
                r"\b(monatlich|monthly)\b",
                r"\b(stündlich|hourly)\b"
            ]
        }

        # Merge with template patterns if available
        template_patterns = self.template_config.get("entity_patterns", {})
        for pattern_type, patterns in template_patterns.items():
            if pattern_type != "confidence_weights" and pattern_type != "job_type_detection":
                base_patterns.update(patterns)

        return base_patterns

    def extract_entities_from_message(self, message: str) -> List[ExtractedEntity]:
        """Extract entities from user message using regex patterns"""
        entities = []
        message_lower = message.lower()

        patterns_dict = self._get_dynamic_patterns()
        for entity_type, patterns in patterns_dict.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, message, re.IGNORECASE)
                    for match in matches:
                        confidence = 0.8  # Base confidence
                        value = match.group(1) if match.groups() else match.group(0)

                        # Adjust confidence based on context
                        if entity_type == "sap_system" and any(word in message_lower for word in ["system", "sap"]):
                            confidence = 0.9
                        elif entity_type == "file_path" and any(word in message_lower for word in ["pfad", "ordner", "verzeichnis"]):
                            confidence = 0.9

                        entities.append(ExtractedEntity(
                            field_name=entity_type,
                            value=value,
                            confidence=confidence,
                            source_text=match.group(0)
                        ))
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern}' for entity type '{entity_type}': {e}")
                    continue

        return entities

    def detect_job_type(self, message: str, conversation_context: List[Dict] = None) -> Tuple[Optional[JobType], float]:
        """Detect job type from message with confidence score using template-based patterns"""
        message_lower = message.lower()
        scores = {}

        # Get job types from template config
        job_types_config = self.template_config.get("job_types", {})

        for job_type_key, config in job_types_config.items():
            try:
                job_type = JobType(job_type_key)
            except ValueError:
                continue  # Skip unknown job types

            score = 0
            total_keywords = 0

            # Check German keywords
            keywords_de = config.get("keywords_de", [])
            for keyword in keywords_de:
                total_keywords += 1
                if keyword.lower() in message_lower:
                    score += 1

            # Check English keywords as fallback
            keywords_en = config.get("keywords", [])
            for keyword in keywords_en:
                total_keywords += 1
                if keyword.lower() in message_lower:
                    score += 0.8  # Slightly lower weight for English

            # Check regex patterns from entity_patterns
            job_type_patterns = self.template_config.get("entity_patterns", {}).get("job_type_detection", {}).get(job_type_key, [])
            for pattern in job_type_patterns:
                try:
                    if re.search(pattern, message, re.IGNORECASE | re.MULTILINE):
                        score += 2  # Higher weight for pattern matches
                        total_keywords += 2
                except re.error:
                    continue  # Skip invalid patterns

            # Calculate normalized score
            if total_keywords > 0:
                scores[job_type] = score / total_keywords
            else:
                scores[job_type] = 0

        # Fallback to legacy detection if no template matches
        if not scores or max(scores.values()) == 0:
            # SAP keywords
            sap_keywords = ["sap", "report", "z_", "abap", "system", "transaktion"]
            sap_score = sum(1 for keyword in sap_keywords if keyword in message_lower)

            # File transfer keywords
            file_keywords = ["file", "transfer", "copy", "move", "pfad", "ordner", "verzeichnis", "kopieren", "daten", "übertragen"]
            file_score = sum(1 for keyword in file_keywords if keyword in message_lower)

            # Standard job keywords
            standard_keywords = ["standard", "script", "batch", "ausführen", "programm", ".bat", ".sh", ".ps1"]
            standard_score = sum(1 for keyword in standard_keywords if keyword in message_lower)

            scores = {
                JobType.SAP: sap_score / len(sap_keywords),
                JobType.FILE_TRANSFER: file_score / len(file_keywords),
                JobType.STANDARD: standard_score / len(standard_keywords)
            }

        if not scores:
            return (None, 0.0)

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

        # Log detection result
        logger.info(f"🎯 Job type detected: {best_type.value if best_type else 'None'} (confidence: {confidence:.2f})")

        return (best_type if confidence > 0.2 else None, confidence)

    def analyze_current_state(self, current_data: Dict[str, Any], job_type: JobType) -> ConversationState:
        """Analyze what information we have vs what we need"""
        if not job_type:
            return ConversationState(
                current_step="job_type_detection",
                completion_percentage=0.0
            )

        required_fields = self.REQUIRED_FIELDS.get(job_type, [])
        collected_fields = []

        # Check which required fields are present
        for field_path in required_fields:
            if self._get_nested_value(current_data, field_path):
                collected_fields.append(field_path)

        missing_fields = [f for f in required_fields if f not in collected_fields]
        completion = len(collected_fields) / len(required_fields) if required_fields else 1.0

        # Determine current step
        current_step = self._determine_current_step(job_type, collected_fields, missing_fields)

        return ConversationState(
            job_type=job_type,
            collected_fields=collected_fields,
            missing_required_fields=missing_fields,
            current_step=current_step,
            completion_percentage=completion
        )

    def generate_contextual_response(self,
                                   entities: List[ExtractedEntity],
                                   state: ConversationState,
                                   user_message: str) -> Tuple[str, List[str]]:
        """Generate contextual bot response and suggested questions using template-based prompts"""

        if state.current_step == "job_type_detection":
            if state.job_type:
                return self._get_job_type_confirmation_response(state.job_type), []
            else:
                return ("Können Sie präziser beschreiben, welche Art von Job Sie erstellen möchten? "
                       "Soll es ein SAP Job, File Transfer oder Standard Job sein?"), [
                    "SAP Report ausführen",
                    "Dateien zwischen Servern kopieren",
                    "Script oder Programm ausführen"
                ]

        # Job-specific responses using template-based prompts
        if state.job_type == JobType.SAP:
            return self._generate_sap_response(entities, state)
        elif state.job_type == JobType.FILE_TRANSFER:
            return self._generate_file_transfer_response(entities, state)
        elif state.job_type == JobType.STANDARD:
            return self._generate_standard_response(entities, state)

        return "Wie kann ich Ihnen weiterhelfen?", []

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        current = data
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None

    def _determine_current_step(self, job_type: JobType, collected: List[str], missing: List[str]) -> str:
        """Determine current conversation step based on collected data"""
        if job_type == JobType.SAP:
            if not any("sapSystem" in field for field in collected):
                return "sap_system"
            elif not any("reportName" in field for field in collected):
                return "sap_report"
        elif job_type == JobType.FILE_TRANSFER:
            if not any("sourcePath" in field for field in collected):
                return "file_source"
            elif not any("targetPath" in field for field in collected):
                return "file_target"
        elif job_type == JobType.STANDARD:
            if not any("scriptPath" in field for field in collected):
                return "standard_script"
            elif not any("agentName" in field for field in collected):
                return "standard_agent"

        if missing:
            return "schedule_setup"
        else:
            return "completed"

    def _get_job_type_confirmation_response(self, job_type: JobType) -> str:
        """Get confirmation response for detected job type using template prompts"""
        prompts = self.template_config.get("conversation_prompts", {})

        if job_type == JobType.SAP:
            return prompts.get("sap", {}).get("initialization",
                "Ich erkenne einen SAP Job! Welches SAP-System und welcher Report soll verwendet werden?")
        elif job_type == JobType.FILE_TRANSFER:
            return prompts.get("file_transfer", {}).get("initialization",
                "Ein File Transfer Job! Von welcher Quelle zu welchem Ziel soll transferiert werden?")
        elif job_type == JobType.STANDARD:
            return prompts.get("standard", {}).get("initialization",
                "Ein Standard Job! Welches Script soll ausgeführt werden und auf welchem Agent?")

        return "Job-Typ erkannt. Weitere Details benötigt."

    def _generate_sap_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate SAP-specific response using template prompts"""
        sap_system = next((e for e in entities if e.field_name == "sap_system"), None)
        report_name = next((e for e in entities if e.field_name == "report_name"), None)

        prompts = self.template_config.get("conversation_prompts", {}).get("sap", {})

        if state.current_step == "sap_system":
            if sap_system:
                return f"SAP-System {sap_system.value} erkannt. Welcher Report soll ausgeführt werden?", [
                    "Z_CUSTOM_REPORT_01",
                    "Standard Report eingeben"
                ]
            else:
                return prompts.get("missing_system", "Welches SAP-System soll verwendet werden? (z.B. P01, T01, Q01)"), [
                    "P01 (Produktiv)",
                    "T01 (Test)",
                    "Q01 (Qualität)"
                ]
        elif state.current_step == "sap_report":
            if report_name:
                return f"Report {report_name.value} wird konfiguriert. Sollen Varianten verwendet werden?", [
                    "Ja, Varianten konfigurieren",
                    "Nein, Standard-Ausführung"
                ]
            else:
                return prompts.get("missing_report", "Welcher SAP-Report soll ausgeführt werden? (z.B. Z_CUSTOM_REPORT)"), [
                    "Custom Z-Report",
                    "Standard SAP Report"
                ]

        return "SAP Job wird konfiguriert...", []

    def _generate_file_transfer_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate file transfer-specific response using template prompts"""
        file_paths = [e for e in entities if e.field_name == "file_path"]

        prompts = self.template_config.get("conversation_prompts", {}).get("file_transfer", {})

        if state.current_step == "file_source":
            if file_paths:
                source_path = file_paths[0].value
                return f"Quell-Pfad {source_path} erkannt. Wohin sollen die Dateien transferiert werden?", [
                    "Anderer Server",
                    "Lokaler Pfad eingeben"
                ]
            else:
                return prompts.get("missing_source", "Von welchem Pfad sollen die Dateien transferiert werden?"), [
                    "C:\\Daten\\Export\\",
                    "/var/data/export/",
                    "\\\\server\\share\\"
                ]
        elif state.current_step == "file_target":
            return prompts.get("missing_target", "Ziel-Pfad für den Transfer eingeben:"), [
                "Gleicher Server, anderer Ordner",
                "Anderer Server"
            ]

        return "File Transfer wird konfiguriert...", []

    def _generate_standard_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate standard job-specific response using template prompts"""
        scripts = [e for e in entities if e.field_name == "script_name"]

        prompts = self.template_config.get("conversation_prompts", {}).get("standard", {})

        if state.current_step == "standard_script":
            if scripts:
                script = scripts[0].value
                return f"Script {script} erkannt. Auf welchem Agent soll es ausgeführt werden?", [
                    "AGENT01",
                    "AGENT02",
                    "Agent eingeben"
                ]
            else:
                return prompts.get("missing_script", "Welches Script oder Programm soll ausgeführt werden?"), [
                    "batch_process.bat",
                    "data_sync.ps1",
                    "Script-Pfad eingeben"
                ]
        elif state.current_step == "standard_agent":
            return prompts.get("missing_agent", "Auf welchem Agent soll das Script ausgeführt werden?"), [
                "AGENT01",
                "AGENT02",
                "Agent-Name eingeben"
            ]

        return "Standard Job wird konfiguriert...", []