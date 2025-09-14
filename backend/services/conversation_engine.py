"""
Intelligent Conversation Engine for XML Stream Creation
Handles context-aware conversation flows and entity extraction
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from schemas.xml_streams import JobType, ConversationState

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
    """Intelligent conversation engine for XML stream creation"""

    # Required fields for each job type
    REQUIRED_FIELDS = {
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

    # Entity extraction patterns
    PATTERNS = {
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
            r"\b([A-Z]+[-_]?[A-Z]*[0-9]*)\b",  # SERVER01, APP-01
            r"server\s+([A-Za-z0-9-_]+)",
            r"von\s+([A-Za-z0-9-_]+)\s+(?:nach|zu)",
            r"nach\s+([A-Za-z0-9-_]+)"
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

    def __init__(self):
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

    def extract_entities_from_message(self, message: str) -> List[ExtractedEntity]:
        """Extract entities from user message using regex patterns"""
        entities = []
        message_lower = message.lower()

        for entity_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
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

        return entities

    def detect_job_type(self, message: str, conversation_context: List[Dict] = None) -> Tuple[Optional[JobType], float]:
        """Detect job type from message with confidence score"""
        message_lower = message.lower()

        # SAP keywords
        sap_keywords = ["sap", "report", "z_", "abap", "system", "transaktion"]
        sap_score = sum(1 for keyword in sap_keywords if keyword in message_lower)

        # File transfer keywords
        file_keywords = ["file", "transfer", "copy", "move", "pfad", "ordner", "verzeichnis", "kopieren"]
        file_score = sum(1 for keyword in file_keywords if keyword in message_lower)

        # Standard job keywords
        standard_keywords = ["standard", "script", "batch", "ausführen", "programm", ".bat", ".sh", ".ps1"]
        standard_score = sum(1 for keyword in standard_keywords if keyword in message_lower)

        # Determine best match
        scores = {
            JobType.SAP: sap_score / len(sap_keywords),
            JobType.FILE_TRANSFER: file_score / len(file_keywords),
            JobType.STANDARD: standard_score / len(standard_keywords)
        }

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

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
        """Generate contextual bot response and suggested questions"""

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

        # Job-specific responses
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
        """Get confirmation response for detected job type"""
        if job_type == JobType.SAP:
            return "Ich erkenne einen SAP Job! Welches SAP-System und welcher Report soll verwendet werden?"
        elif job_type == JobType.FILE_TRANSFER:
            return "Ein File Transfer Job! Von welcher Quelle zu welchem Ziel soll transferiert werden?"
        elif job_type == JobType.STANDARD:
            return "Ein Standard Job! Welches Script soll ausgeführt werden und auf welchem Agent?"
        return "Job-Typ erkannt. Weitere Details benötigt."

    def _generate_sap_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate SAP-specific response"""
        sap_system = next((e for e in entities if e.field_name == "sap_system"), None)
        report_name = next((e for e in entities if e.field_name == "report_name"), None)

        if state.current_step == "sap_system":
            if sap_system:
                return f"SAP-System {sap_system.value} erkannt. Welcher Report soll ausgeführt werden?", [
                    "Z_CUSTOM_REPORT_01",
                    "Standard Report eingeben"
                ]
            else:
                return "Welches SAP-System soll verwendet werden? (z.B. P01, T01, Q01)", [
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
                return "Welcher SAP-Report soll ausgeführt werden? (z.B. Z_CUSTOM_REPORT)", [
                    "Custom Z-Report",
                    "Standard SAP Report"
                ]

        return "SAP Job wird konfiguriert...", []

    def _generate_file_transfer_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate file transfer-specific response"""
        file_paths = [e for e in entities if e.field_name == "file_path"]

        if state.current_step == "file_source":
            if file_paths:
                source_path = file_paths[0].value
                return f"Quell-Pfad {source_path} erkannt. Wohin sollen die Dateien transferiert werden?", [
                    "Anderer Server",
                    "Lokaler Pfad eingeben"
                ]
            else:
                return "Von welchem Pfad sollen die Dateien transferiert werden?", [
                    "C:\\Daten\\Export\\",
                    "/var/data/export/",
                    "\\\\server\\share\\"
                ]
        elif state.current_step == "file_target":
            return "Ziel-Pfad für den Transfer eingeben:", [
                "Gleicher Server, anderer Ordner",
                "Anderer Server"
            ]

        return "File Transfer wird konfiguriert...", []

    def _generate_standard_response(self, entities: List[ExtractedEntity], state: ConversationState) -> Tuple[str, List[str]]:
        """Generate standard job-specific response"""
        scripts = [e for e in entities if e.field_name == "script_name"]

        if state.current_step == "standard_script":
            if scripts:
                script = scripts[0].value
                return f"Script {script} erkannt. Auf welchem Agent soll es ausgeführt werden?", [
                    "AGENT01",
                    "AGENT02",
                    "Agent eingeben"
                ]
            else:
                return "Welches Script oder Programm soll ausgeführt werden?", [
                    "batch_process.bat",
                    "data_sync.ps1",
                    "Script-Pfad eingeben"
                ]
        elif state.current_step == "standard_agent":
            return "Auf welchem Agent soll das Script ausgeführt werden?", [
                "AGENT01",
                "AGENT02",
                "Agent-Name eingeben"
            ]

        return "Standard Job wird konfiguriert...", []