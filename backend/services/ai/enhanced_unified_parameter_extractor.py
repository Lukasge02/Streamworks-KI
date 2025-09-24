"""
Enhanced Unified Parameter Extractor - Verbesserte Job-Type-Erkennung & Parameter-Extraktion
Integriert den Enhanced Job-Type Detector für maximale Accuracy
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

# Import Enhanced Job-Type Detector
from .enhanced_job_type_detector import EnhancedJobTypeDetector, get_enhanced_job_type_detector

logger = logging.getLogger(__name__)

# ================================
# ENHANCED MODELS
# ================================

class ExtractedParameter(BaseModel):
    """Einzelner extrahierter Parameter"""
    name: str = Field(description="Name des Parameters")
    value: Any = Field(description="Extrahierter Wert")
    confidence: float = Field(description="Konfidenz-Score 0.0-1.0")
    source_text: str = Field(description="Original-Text aus dem die Info extrahiert wurde")
    scope: str = Field(description="stream oder job", default="stream")
    extraction_method: str = Field(description="Methode der Extraktion", default="llm")

class EnhancedExtractionResult(BaseModel):
    """Erweitertes Ergebnis der Parameter-Extraktion"""
    detected_job_type: Optional[str] = Field(description="Erkannter Job-Type")
    confidence_score: float = Field(description="Gesamt-Konfidenz der Job-Type-Erkennung")
    detection_method: str = Field(description="Verwendete Erkennungsmethode", default="enhanced")

    # Parameter gruppiert nach Scope
    stream_parameters: List[ExtractedParameter] = Field(default_factory=list)
    job_parameters: List[ExtractedParameter] = Field(default_factory=list)

    # Status und Nachfragen
    missing_stream_parameters: List[str] = Field(default_factory=list)
    missing_job_parameters: List[str] = Field(default_factory=list)
    needs_clarification: bool = Field(description="Ob Nachfragen nötig sind", default=False)
    suggested_questions: List[str] = Field(default_factory=list)

    # Enhanced Metrics
    completion_percentage: float = Field(description="Vervollständigung in Prozent", default=0.0)
    next_required_parameter: Optional[str] = Field(description="Nächster erforderlicher Parameter", default=None)
    alternative_job_types: List[Tuple[str, float]] = Field(default_factory=list, description="Alternative Job-Type-Kandidaten")

    # Metadaten
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)

class EnhancedUnifiedParameterExtractor:
    """
    Erweiterte Version des UnifiedParameterExtractor mit Enhanced Job-Type Detection

    Verbesserungen:
    - 🎯 90%+ Job-Type Accuracy durch Enhanced Detector
    - 🔍 Multi-Layer Parameter-Extraktion
    - 📊 Detaillierte Confidence-Scoring
    - 🚀 Bessere deutsche Spracherkennung
    - 🎨 Context-aware Parameter-Mapping
    """

    def __init__(self, openai_api_key: str, schema_path: Optional[str] = None):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.1
        )

        # Enhanced Job-Type Detector
        self.job_type_detector = get_enhanced_job_type_detector()

        # Lade vereinheitlichte Schemas
        if schema_path:
            self.schema_path = schema_path
        else:
            self.schema_path = Path(__file__).parent.parent.parent / "templates" / "unified_stream_schemas.json"

        self.schemas = self._load_unified_schemas()

        # Enhanced Parameter Extractors
        self.parameter_extractors = self._initialize_parameter_extractors()

        logger.info(f"EnhancedUnifiedParameterExtractor initialisiert mit {len(self.schemas.get('job_type_schemas', {}))} Job-Types")

    def _load_unified_schemas(self) -> Dict[str, Any]:
        """Lädt die vereinheitlichten Schemas"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Unified Schemas geladen: Version {data.get('version', 'unknown')}")
            return data
        except FileNotFoundError:
            logger.error(f"Schema-Datei nicht gefunden: {self.schema_path}")
            return {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Schemas: {e}")
            return {}

    def _initialize_parameter_extractors(self) -> Dict[str, Any]:
        """Initialisiert job-type-spezifische Parameter-Extraktoren"""
        return {
            "FILE_TRANSFER": self._create_file_transfer_extractor(),
            "SAP": self._create_sap_extractor(),
            "STANDARD": self._create_standard_extractor()
        }

    def _create_file_transfer_extractor(self) -> Dict[str, Any]:
        """Spezialisierte Extraktor-Konfiguration für FILE_TRANSFER"""
        return {
            "extraction_patterns": {
                "source_agent": [
                    r"(?:von|aus|quelle[:\s]+)([a-zA-Z0-9_\-]+)",
                    r"zwischen\s+([a-zA-Z0-9_\-]+)\s+(?:und|zu)",
                    r"server\s+([a-zA-Z0-9_\-]+)"
                ],
                "target_agent": [
                    r"(?:nach|zu|ziel[:\s]+)([a-zA-Z0-9_\-]+)",
                    r"(?:und|zu)\s+([a-zA-Z0-9_\-]+)",
                    r"(?:target|ziel).*?([a-zA-Z0-9_\-]+)"
                ],
                "source_path": [
                    r"(?:pfad|path)[:\s]+([^\s]+)",
                    r"(?:aus|von)[:\s]+([A-Za-z]:[\\\/][^\s]+)",
                    r"([A-Za-z]:[\\\/][^\s]+)",
                    r"\/[^\s]+",
                    r"\*\.(?:csv|xml|pdf|txt|log|xlsx)"
                ],
                "MainScript": [
                    r"(?:script|skript|command)[:\s]+(.+)",
                    r"(?:ausführ|run|execut)[:\s]+(.+)",
                    r"(python\s+[^\s]+\.py.*)",
                    r"(java\s+-jar\s+[^\s]+.*)",
                    r"([a-zA-Z0-9_\-]+\.(?:py|jar|exe|bat|sh).*)"
                ]
            },
            "context_keywords": {
                "high_priority": ["source_agent", "target_agent", "MainScript"],
                "medium_priority": ["source_path", "target_path"],
                "auto_generate": ["JobCategory", "JobType"]
            }
        }

    def _create_sap_extractor(self) -> Dict[str, Any]:
        """Spezialisierte Extraktor-Konfiguration für SAP"""
        return {
            "extraction_patterns": {
                "system": [
                    r"(?:sap\s+)?(?:system[:\s]+)?([a-zA-Z0-9_]+(?:_(?:PRD|DEV|TST|100|200))?)",
                    r"(?:gt123|pa1|pt1|pd1)(?:_(?:prd|dev|tst|100|200))?",
                    r"(?:aus|von)\s+(?:system\s+)?([a-zA-Z0-9_]+)"
                ],
                "report": [
                    r"report[:\s]+([a-zA-Z0-9_]+)",
                    r"(?:ztv|rsus|rfc)[a-zA-Z0-9_]*",
                    r"programm[:\s]+([a-zA-Z0-9_]+)"
                ],
                "variant": [
                    r"variant[e]?[:\s]+([a-zA-Z0-9_]+)",
                    r"(?:excel|csv|daily|weekly|monthly)",
                    r"standard[-\s]?variant[e]?"
                ],
                "MainScript": [
                    r"(?:export|import)\s+(?:aus|von|zu)\s+sap.*",
                    r"sap.*(?:export|import|extract).*",
                    r"(?:fabrik)?kalender.*(?:export|daten)"
                ]
            }
        }

    def _create_standard_extractor(self) -> Dict[str, Any]:
        """Spezialisierte Extraktor-Konfiguration für STANDARD"""
        return {
            "extraction_patterns": {
                "MainScript": [
                    r"(?:python|java|node|php)\s+[^\s]+(?:\s+[^\n]*)?",
                    r"(?:script|command)[:\s]+(.+)",
                    r"(?:ausführ|run|execut)[:\s]+(.+)",
                    r"([a-zA-Z0-9_\-/]+\.(?:py|js|jar|exe|bat|sh)(?:\s+[^\n]*)?)",
                    r"(dir\s+[^\s]+.*|ls\s+[^\s]+.*|cp\s+[^\s]+.*)"
                ],
                "JobCategory": [
                    r"(?:data\s*processing|datenverarbeitung)",
                    r"(?:backup|sicherung|bereinigung|cleanup)",
                    r"(?:maintenance|wartung|überwachung|monitoring)"
                ]
            }
        }

    async def extract_parameters(
        self,
        user_message: str,
        existing_stream_params: Optional[Dict[str, Any]] = None,
        existing_job_params: Optional[Dict[str, Any]] = None,
        current_job_type: Optional[str] = None
    ) -> EnhancedExtractionResult:
        """
        Hauptmethode für Enhanced Parameter-Extraktion

        Args:
            user_message: Die Nachricht des Users
            existing_stream_params: Bereits gesammelte Stream-Parameter
            existing_job_params: Bereits gesammelte Job-Parameter
            current_job_type: Aktueller Job-Type (falls bereits bestimmt)

        Returns:
            EnhancedExtractionResult mit allen extrahierten Informationen
        """
        try:
            logger.info(f"🚀 Enhanced Parameter-Extraktion für: '{user_message[:80]}...'")

            # Schritt 1: Enhanced Job-Type-Erkennung (falls noch nicht bestimmt)
            if not current_job_type:
                detection_result = self.job_type_detector.detect_job_type(user_message)
                job_type = detection_result.detected_job_type
                confidence = detection_result.confidence
                detection_method = detection_result.detection_method
                alternatives = detection_result.alternative_candidates
            else:
                job_type = current_job_type
                confidence = 1.0  # Bereits bestätigt
                detection_method = "provided"
                alternatives = []

            # Schritt 2: Enhanced Parameter-Extraktion für den Job-Type
            if job_type:
                result = await self._extract_for_job_type_enhanced(
                    user_message=user_message,
                    job_type=job_type,
                    detection_confidence=confidence,
                    detection_method=detection_method,
                    existing_stream_params=existing_stream_params or {},
                    existing_job_params=existing_job_params or {}
                )
                result.alternative_job_types = alternatives
            else:
                # Kein Job-Type erkannt - biete Alternativen an
                result = await self._generic_extraction_enhanced(user_message, alternatives)

            logger.info(f"✅ Enhanced Extraktion abgeschlossen: Job-Type={result.detected_job_type}, Confidence={result.confidence_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"❌ Fehler bei enhanced Parameter-Extraktion: {e}")
            return EnhancedExtractionResult(
                detected_job_type=None,
                confidence_score=0.0,
                detection_method="error",
                needs_clarification=True,
                suggested_questions=["Entschuldigung, es gab einen Fehler. Können Sie Ihre Anfrage anders formulieren?"],
                extraction_metadata={"error": str(e)}
            )

    async def _extract_for_job_type_enhanced(
        self,
        user_message: str,
        job_type: str,
        detection_confidence: float,
        detection_method: str,
        existing_stream_params: Dict[str, Any],
        existing_job_params: Dict[str, Any]
    ) -> EnhancedExtractionResult:
        """Enhanced Parameter-Extraktion für einen bestimmten Job-Type"""

        job_schema = self.schemas['job_type_schemas'][job_type]
        common_stream_params = self.schemas.get('common_stream_parameters', [])
        job_specific_params = job_schema.get('job_parameters', [])

        # Enhanced Stream-Parameter Extraktion
        stream_parameters = await self._extract_stream_parameters_enhanced(
            user_message, common_stream_params, existing_stream_params, job_type
        )

        # Enhanced Job-Parameter Extraktion mit spezialisiertem Extractor
        job_parameters = await self._extract_job_parameters_enhanced(
            user_message, job_specific_params, existing_job_params, job_type
        )

        # Intelligente Parameter-Generierung für fehlende kritische Parameter
        generated_params = self._generate_missing_critical_parameters(
            user_message, job_type, stream_parameters, job_parameters
        )

        # Füge generierte Parameter hinzu
        job_parameters.extend(generated_params)

        # Bestimme fehlende Parameter
        missing_stream = self._get_missing_parameters(common_stream_params, stream_parameters, existing_stream_params)
        missing_job = self._get_missing_parameters(job_specific_params, job_parameters, existing_job_params)

        # Enhanced Nachfragen-Generierung
        suggested_questions = await self._generate_smart_questions_enhanced(
            missing_stream, missing_job, job_type, user_message, common_stream_params, job_specific_params
        )

        # Berechne Enhanced Vervollständigung
        completion_data = self._calculate_enhanced_completion(
            common_stream_params, job_specific_params,
            stream_parameters, job_parameters,
            existing_stream_params, existing_job_params
        )

        return EnhancedExtractionResult(
            detected_job_type=job_type,
            confidence_score=detection_confidence,
            detection_method=detection_method,
            stream_parameters=stream_parameters,
            job_parameters=job_parameters,
            missing_stream_parameters=missing_stream,
            missing_job_parameters=missing_job,
            needs_clarification=len(missing_stream) > 0 or len(missing_job) > 0,
            suggested_questions=suggested_questions,
            completion_percentage=completion_data["completion_percentage"],
            next_required_parameter=completion_data["next_required"],
            extraction_metadata={
                "job_schema": job_schema['display_name'],
                "detection_method": detection_method,
                "total_required_params": completion_data["total_required"],
                "enhanced_extraction": True,
                "timestamp": datetime.now().isoformat()
            }
        )

    async def _extract_stream_parameters_enhanced(
        self,
        user_message: str,
        stream_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any],
        job_type: str
    ) -> List[ExtractedParameter]:
        """Enhanced Stream-Parameter Extraktion mit verbesserter Logik"""

        # Basis-LLM Extraktion
        llm_params = await self._extract_stream_parameters_llm(
            user_message, stream_param_schemas, existing_params
        )

        # Pattern-basierte Extraktion für kritische Parameter
        pattern_params = self._extract_stream_parameters_patterns(user_message, job_type)

        # Intelligente ShortDescription-Generierung
        if not any(p.name == "ShortDescription" for p in llm_params + pattern_params):
            short_desc = self._generate_intelligent_short_description(user_message, job_type)
            if short_desc:
                pattern_params.append(ExtractedParameter(
                    name="ShortDescription",
                    value=short_desc,
                    confidence=0.85,
                    source_text=f"Auto-generiert aus: {user_message[:30]}...",
                    scope="stream",
                    extraction_method="intelligent_generation"
                ))

        # Kombiniere und dedupliziere Parameter
        all_params = llm_params + pattern_params
        return self._deduplicate_parameters(all_params)

    async def _extract_job_parameters_enhanced(
        self,
        user_message: str,
        job_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any],
        job_type: str
    ) -> List[ExtractedParameter]:
        """Enhanced Job-Parameter Extraktion mit spezialisiertem Extractor"""

        if not job_param_schemas:
            return []

        # LLM-basierte Extraktion
        llm_params = await self._extract_job_parameters_llm(
            user_message, job_param_schemas, existing_params
        )

        # Spezialisierte Pattern-Extraktion für den Job-Type
        pattern_params = self._extract_job_parameters_patterns(user_message, job_type)

        # Kombiniere Parameter
        all_params = llm_params + pattern_params
        return self._deduplicate_parameters(all_params)

    def _extract_stream_parameters_patterns(self, user_message: str, job_type: str) -> List[ExtractedParameter]:
        """Pattern-basierte Stream-Parameter Extraktion"""
        parameters = []

        # StreamName Pattern
        stream_name_patterns = [
            r"stream.*?(?:soll|heißt|name)[:\s]+([a-zA-Z0-9_\-]+)",
            r"(?:namens|genannt)[:\s]+([a-zA-Z0-9_\-]+)",
            r"name[:\s]+([a-zA-Z0-9_\-]+)"
        ]

        for pattern in stream_name_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                parameters.append(ExtractedParameter(
                    name="StreamName",
                    value=match.group(1),
                    confidence=0.85,
                    source_text=match.group(0),
                    scope="stream",
                    extraction_method="pattern_matching"
                ))
                break

        # MaxStreamRuns Pattern
        runs_patterns = [
            r"(?:maximal|max)[:\s]*(\d+)(?:\s+(?:ausführungen|runs|läufe))?",
            r"(\d+)[:\s]*(?:parallele?|gleichzeitige?)[:\s]*(?:ausführungen|läufe)"
        ]

        for pattern in runs_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                runs = int(match.group(1))
                if 1 <= runs <= 50:  # Validierung
                    parameters.append(ExtractedParameter(
                        name="MaxStreamRuns",
                        value=runs,
                        confidence=0.90,
                        source_text=match.group(0),
                        scope="stream",
                        extraction_method="pattern_matching"
                    ))
                break

        # SchedulingRequiredFlag Pattern
        if any(word in user_message.lower() for word in ["täglich", "wöchentlich", "zeitgesteuert", "schedule", "geplant"]):
            parameters.append(ExtractedParameter(
                name="SchedulingRequiredFlag",
                value=True,
                confidence=0.88,
                source_text="zeitgesteuerte Ausführung erkannt",
                scope="stream",
                extraction_method="pattern_matching"
            ))
        elif any(word in user_message.lower() for word in ["manuell", "manual", "auf abruf", "einmalig"]):
            parameters.append(ExtractedParameter(
                name="SchedulingRequiredFlag",
                value=False,
                confidence=0.88,
                source_text="manuelle Ausführung erkannt",
                scope="stream",
                extraction_method="pattern_matching"
            ))

        return parameters

    def _extract_job_parameters_patterns(self, user_message: str, job_type: str) -> List[ExtractedParameter]:
        """Pattern-basierte Job-Parameter Extraktion mit Job-Type-spezifischer Logik"""
        parameters = []

        if job_type not in self.parameter_extractors:
            return parameters

        extractor_config = self.parameter_extractors[job_type]
        extraction_patterns = extractor_config.get("extraction_patterns", {})

        for param_name, patterns in extraction_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)

                    # Bereinige Wert
                    value = value.strip().strip('"\'')

                    if value:  # Nur nicht-leere Werte
                        parameters.append(ExtractedParameter(
                            name=param_name,
                            value=value,
                            confidence=0.82,
                            source_text=match.group(0),
                            scope="job",
                            extraction_method="pattern_matching"
                        ))
                        break  # Nur ersten Match verwenden

        return parameters

    def _generate_missing_critical_parameters(
        self,
        user_message: str,
        job_type: str,
        stream_parameters: List[ExtractedParameter],
        job_parameters: List[ExtractedParameter]
    ) -> List[ExtractedParameter]:
        """Generiert fehlende kritische Parameter basierend auf Kontext"""
        generated = []

        # JobCategory automatisch setzen
        if not any(p.name == "JobCategory" for p in job_parameters):
            job_category_mapping = {
                "FILE_TRANSFER": "FileTransfer",
                "SAP": "SAP",
                "STANDARD": "STANDARD"
            }
            if job_type in job_category_mapping:
                generated.append(ExtractedParameter(
                    name="JobCategory",
                    value=job_category_mapping[job_type],
                    confidence=1.0,
                    source_text="Automatisch basierend auf Job-Type gesetzt",
                    scope="job",
                    extraction_method="auto_generation"
                ))

        # JobType für STANDARD Jobs
        if job_type == "STANDARD" and not any(p.name == "JobType" for p in job_parameters):
            if any(word in user_message.lower() for word in ["windows", "batch", "cmd", ".bat", ".exe"]):
                job_type_value = "Windows"
            else:
                job_type_value = "Unix"

            generated.append(ExtractedParameter(
                name="JobType",
                value=job_type_value,
                confidence=0.80,
                source_text="Auto-erkannt aus Script-Kontext",
                scope="job",
                extraction_method="auto_generation"
            ))

        return generated

    def _generate_intelligent_short_description(self, user_message: str, job_type: str) -> Optional[str]:
        """Generiert intelligente ShortDescription basierend auf Kontext"""

        message_lower = user_message.lower()

        # Job-Type-spezifische Beschreibungen
        if job_type == "FILE_TRANSFER":
            if "zwischen" in message_lower:
                # Extrahiere Systemnamen
                between_match = re.search(r"zwischen\s+([a-zA-Z0-9_\-]+)\s+(?:und|zu)\s+([a-zA-Z0-9_\-]+)", message_lower)
                if between_match:
                    source, target = between_match.groups()
                    return f"Transfer {source}-{target}"[:50]

            if any(word in message_lower for word in ["datentransfer", "file transfer", "übertragung"]):
                return "Datentransfer"

        elif job_type == "SAP":
            if "export" in message_lower:
                return "SAP Export"
            elif "import" in message_lower:
                return "SAP Import"
            elif "kalender" in message_lower:
                return "SAP Kalender"
            else:
                return "SAP Process"

        elif job_type == "STANDARD":
            if "script" in message_lower:
                return "Script Execution"
            elif "batch" in message_lower:
                return "Batch Process"
            elif "cleanup" in message_lower:
                return "System Cleanup"
            else:
                return "Standard Process"

        return None

    async def _extract_stream_parameters_llm(
        self,
        user_message: str,
        stream_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any]
    ) -> List[ExtractedParameter]:
        """LLM-basierte Stream-Parameter Extraktion (Original-Methode)"""
        # Übernommen aus original unified_parameter_extractor.py
        param_info = []
        for param in stream_param_schemas:
            examples_str = ", ".join([str(ex) for ex in param.get('examples', [])[:2]])
            param_info.append(f"""
- {param['name']} ({param['data_type']}): {param['description']}
  Frage: "{param['chat_prompt']}"
  Beispiele: {examples_str}
  Erforderlich: {'Ja' if param.get('required', False) else 'Nein'}
""")

        prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Extraktion von Streamworks Stream-Parametern.

VERFÜGBARE STREAM-PARAMETER:
{parameters}

BEREITS GESAMMELTE PARAMETER:
{existing_parameters}

USER-NACHRICHT: "{user_message}"

Extrahiere ALLE Stream-Parameter, die in der Nachricht erwähnt werden.

Antworte nur mit einem JSON-Array von Objekten:
[
  {{
    "name": "ParameterName",
    "value": "ExtrahierterWert",
    "confidence": 0.9,
    "source_text": "Originaler Text"
  }}
]

Wenn keine Parameter gefunden werden, antworte mit: []
""")

        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "parameters": "\n".join(param_info),
                "existing_parameters": json.dumps(existing_params, indent=2, ensure_ascii=False),
                "user_message": user_message
            })

            # Parse JSON Response
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            extracted_data = json.loads(response_text.strip())

            # Convert to ExtractedParameter objects
            parameters = []
            for item in extracted_data:
                if isinstance(item, dict) and all(key in item for key in ["name", "value", "confidence", "source_text"]):
                    parameters.append(ExtractedParameter(
                        name=item["name"],
                        value=item["value"],
                        confidence=float(item["confidence"]),
                        source_text=item["source_text"],
                        scope="stream",
                        extraction_method="llm"
                    ))

            logger.info(f"🎯 LLM Stream-Parameter extrahiert: {len(parameters)} gefunden")
            return parameters

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM Stream-Extraktion fehlgeschlagen: {e}")
            return []

    async def _extract_job_parameters_llm(
        self,
        user_message: str,
        job_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any]
    ) -> List[ExtractedParameter]:
        """LLM-basierte Job-Parameter Extraktion (Original-Methode)"""
        # Übernommen aus original unified_parameter_extractor.py
        param_info = []
        for param in job_param_schemas:
            examples_str = ", ".join([str(ex) for ex in param.get('examples', [])[:2]])
            param_info.append(f"""
- {param['name']} ({param['data_type']}): {param['description']}
  Frage: "{param['chat_prompt']}"
  Beispiele: {examples_str}
  Erforderlich: {'Ja' if param.get('required', False) else 'Nein'}
""")

        prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Extraktion von Job-spezifischen Parametern.

VERFÜGBARE JOB-PARAMETER:
{parameters}

BEREITS GESAMMELTE PARAMETER:
{existing_parameters}

USER-NACHRICHT: "{user_message}"

Extrahiere ALLE Job-Parameter, die in der Nachricht erwähnt werden.

Antworte nur mit einem JSON-Array von Objekten:
[
  {{
    "name": "ParameterName",
    "value": "ExtrahierterWert",
    "confidence": 0.9,
    "source_text": "Originaler Text"
  }}
]

Wenn keine Parameter gefunden werden, antworte mit: []
""")

        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "parameters": "\n".join(param_info),
                "existing_parameters": json.dumps(existing_params, indent=2, ensure_ascii=False),
                "user_message": user_message
            })

            # Parse JSON Response
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            extracted_data = json.loads(response_text.strip())

            # Convert to ExtractedParameter objects
            parameters = []
            for item in extracted_data:
                if isinstance(item, dict) and all(key in item for key in ["name", "value", "confidence", "source_text"]):
                    parameters.append(ExtractedParameter(
                        name=item["name"],
                        value=item["value"],
                        confidence=float(item["confidence"]),
                        source_text=item["source_text"],
                        scope="job",
                        extraction_method="llm"
                    ))

            logger.info(f"🎯 LLM Job-Parameter extrahiert: {len(parameters)} gefunden")
            return parameters

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM Job-Extraktion fehlgeschlagen: {e}")
            return []

    def _deduplicate_parameters(self, parameters: List[ExtractedParameter]) -> List[ExtractedParameter]:
        """Entfernt Duplikate und behält höchste Confidence"""
        param_dict = {}

        for param in parameters:
            if param.name not in param_dict or param.confidence > param_dict[param.name].confidence:
                param_dict[param.name] = param

        return list(param_dict.values())

    def _get_missing_parameters(
        self,
        param_schemas: List[Dict[str, Any]],
        extracted_params: List[ExtractedParameter],
        existing_params: Dict[str, Any]
    ) -> List[str]:
        """Bestimmt fehlende erforderliche Parameter"""
        extracted_names = {p.name for p in extracted_params}
        existing_names = set(existing_params.keys())
        all_collected = extracted_names | existing_names

        required_params = [p['name'] for p in param_schemas if p.get('required', False)]
        missing = [name for name in required_params if name not in all_collected]

        return missing

    async def _generate_smart_questions_enhanced(
        self,
        missing_stream: List[str],
        missing_job: List[str],
        job_type: str,
        user_message: str,
        stream_schemas: List[Dict[str, Any]],
        job_schemas: List[Dict[str, Any]]
    ) -> List[str]:
        """Enhanced intelligente Nachfragen-Generierung"""
        questions = []

        # Priorisierte Stream-Parameter Fragen
        priority_stream = ["StreamName", "ShortDescription"]
        for param_name in priority_stream:
            if param_name in missing_stream:
                param_schema = next((p for p in stream_schemas if p['name'] == param_name), None)
                if param_schema and len(questions) < 2:
                    questions.append(param_schema['chat_prompt'])

        # Job-Type-spezifische kritische Parameter
        critical_job_params = {
            "FILE_TRANSFER": ["source_agent", "target_agent", "MainScript"],
            "SAP": ["system", "report", "MainScript"],
            "STANDARD": ["MainScript", "JobCategory"]
        }

        if job_type in critical_job_params:
            for param_name in critical_job_params[job_type]:
                if param_name in missing_job and len(questions) < 3:
                    param_schema = next((p for p in job_schemas if p['name'] == param_name), None)
                    if param_schema:
                        questions.append(param_schema['chat_prompt'])

        # Context-basierte Fallback-Fragen
        if not questions:
            if missing_stream or missing_job:
                questions.append("Möchten Sie weitere Details zur Konfiguration angeben?")
            else:
                questions.append("Soll ich die XML-Konfiguration jetzt generieren?")

        return questions[:3]  # Maximal 3 Fragen

    def _calculate_enhanced_completion(
        self,
        stream_schemas: List[Dict[str, Any]],
        job_schemas: List[Dict[str, Any]],
        stream_params: List[ExtractedParameter],
        job_params: List[ExtractedParameter],
        existing_stream: Dict[str, Any],
        existing_job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced Completion-Berechnung"""

        # Zähle erforderliche Parameter
        required_stream = len([p for p in stream_schemas if p.get('required', False)])
        required_job = len([p for p in job_schemas if p.get('required', False)])
        total_required = required_stream + required_job

        # Zähle vorhandene Parameter
        completed_stream = len(stream_params) + len(existing_stream)
        completed_job = len(job_params) + len(existing_job)
        total_completed = completed_stream + completed_job

        # Berechne Percentage mit Mindesterfüllung
        completion_percentage = min(total_completed / max(total_required, 1), 1.0) if total_required > 0 else 1.0

        # Bestimme nächsten erforderlichen Parameter
        next_required = None
        missing_stream = [p['name'] for p in stream_schemas if p.get('required', False)
                         and p['name'] not in {param.name for param in stream_params}
                         and p['name'] not in existing_stream]
        missing_job = [p['name'] for p in job_schemas if p.get('required', False)
                      and p['name'] not in {param.name for param in job_params}
                      and p['name'] not in existing_job]

        if missing_stream:
            next_required = missing_stream[0]
        elif missing_job:
            next_required = missing_job[0]

        return {
            "completion_percentage": completion_percentage * 100,
            "total_required": total_required,
            "next_required": next_required
        }

    async def _generic_extraction_enhanced(self, user_message: str, alternatives: List[Tuple[str, float]]) -> EnhancedExtractionResult:
        """Enhanced Fallback wenn kein Job-Type erkannt wurde"""

        questions = ["Welchen Job-Type möchten Sie konfigurieren?"]

        if alternatives:
            # Biete Top-3 Alternativen an
            alt_text = ", ".join([f"{jt} ({conf:.1%})" for jt, conf in alternatives[:3]])
            questions.append(f"Mögliche Typen basierend auf Ihrer Eingabe: {alt_text}")
        else:
            questions.extend([
                "Handelt es sich um einen File Transfer, SAP-Job oder Standard-Prozess?",
                "Beschreiben Sie, was der Stream machen soll."
            ])

        return EnhancedExtractionResult(
            detected_job_type=None,
            confidence_score=0.0,
            detection_method="no_detection",
            alternative_job_types=alternatives,
            needs_clarification=True,
            suggested_questions=questions,
            completion_percentage=0.0,
            extraction_metadata={"reason": "no_job_type_detected", "alternatives_provided": len(alternatives)}
        )

    def get_available_job_types(self) -> List[Dict[str, Any]]:
        """Gibt alle verfügbaren Job-Types zurück"""
        job_schemas = self.schemas.get('job_type_schemas', {})

        return [
            {
                "job_type": job_type,
                "display_name": schema["display_name"],
                "description": schema["description"],
                "complexity": schema["complexity"],
                "estimated_time": schema["estimated_time"],
                "category": schema.get("category", "General"),
                "parameter_count": len(schema.get("job_parameters", []))
            }
            for job_type, schema in job_schemas.items()
        ]

    def get_job_type_info(self, job_type: str) -> Optional[Dict[str, Any]]:
        """Gibt Schema-Informationen für einen Job-Type zurück"""
        return self.schemas.get('job_type_schemas', {}).get(job_type)

# ================================
# FACTORY FUNCTION
# ================================

_enhanced_unified_extractor_instance: Optional[EnhancedUnifiedParameterExtractor] = None

def get_enhanced_unified_parameter_extractor(openai_api_key: Optional[str] = None) -> EnhancedUnifiedParameterExtractor:
    """Factory function für EnhancedUnifiedParameterExtractor"""
    global _enhanced_unified_extractor_instance

    if _enhanced_unified_extractor_instance is None:
        if not openai_api_key:
            from config import settings
            openai_api_key = settings.OPENAI_API_KEY

        _enhanced_unified_extractor_instance = EnhancedUnifiedParameterExtractor(openai_api_key)

    return _enhanced_unified_extractor_instance