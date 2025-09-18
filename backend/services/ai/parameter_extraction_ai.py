"""
Parameter Extraction AI Service - Phase 3+ Spezialisierter Service
Präzise OpenAI-basierte Parameter-Extraktion für Chat-zu-XML System
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from services.openai_llm_service import OpenAILLMService
from schemas.streamworks_schemas import get_schema_for_type, StreamType, get_missing_parameters

logger = logging.getLogger(__name__)

class ParameterExtractionMode(Enum):
    """Extraktions-Modi für verschiedene Genauigkeitsanforderungen"""
    PRECISE = "precise"           # Maximale Genauigkeit für kritische Parameter
    BALANCED = "balanced"         # Standard-Balance zwischen Speed und Accuracy
    FAST = "fast"                # Schnelle Extraktion für Bulk-Processing

@dataclass
class ExtractionContext:
    """Kontext-Informationen für Parameter-Extraktion"""
    job_type: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    extracted_parameters: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParameterExtractionResult:
    """Resultat einer Parameter-Extraktion"""
    extracted_parameters: Dict[str, Any]
    confidence_scores: Dict[str, float]
    extraction_method: str
    processing_time: float
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Quality Metrics
    precision_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0

class ParameterExtractionAI:
    """
    Spezialisierter OpenAI Service für präzise Parameter-Extraktion

    Features:
    - Multi-Mode Extraktion (Precise/Balanced/Fast)
    - Context-Aware Processing
    - Quality Scoring und Validation
    - Learning von User-Patterns
    """

    def __init__(self):
        """Initialize Parameter Extraction AI Service"""
        self.openai_service = None
        self.is_initialized = False

        # Extraction Configuration
        self.extraction_config = {
            "precise": {
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 1000,
                "retry_attempts": 3
            },
            "balanced": {
                "model": "gpt-4o",
                "temperature": 0.2,
                "max_tokens": 800,
                "retry_attempts": 2
            },
            "fast": {
                "model": "gpt-4o",
                "temperature": 0.3,
                "max_tokens": 500,
                "retry_attempts": 1
            }
        }

        # StreamWorks-spezifische Parameter Recognition Patterns
        self.streamworks_patterns = {
            "agents": [
                "gtlnmiwvm1636", "gtasswvv15778", "prodagent001", "testagent",
                "localhost", "nowindows", "fileserver"
            ],
            "sap_systems": ["ZTV", "PA1", "PRD", "QAS", "DEV"],
            "sap_mandants": ["100", "300", "500", "800"],
            "job_types": ["Windows", "Linux", "Unix", "AIX", "SLES12", "SLES15", "RH8", "DEB11"],
            "transfer_methods": ["COPY", "FTP", "SFTP", "RSYNC", "SCP"],
            "calendars": ["UATDefaultCalendar", "ProductionCalendar", "TestCalendar"],
            "common_paths": {
                "windows": ["C:\\", "D:\\", "\\\\server\\", "c:\\temp", "c:\\work"],
                "linux": ["/var/", "/opt/", "/home/", "/tmp/", "/data/"]
            }
        }

        # StreamWorks Content Keywords für bessere Erkennung
        self.content_keywords = {
            "sap_indicators": ["sap", "jexa4s", "mandant", "client", "report", "variant", "transaction"],
            "transfer_indicators": ["copy", "transfer", "file", "ftp", "sftp", "source", "target", "agent"],
            "standard_indicators": ["script", "batch", "exe", "run", "process", "command"]
        }

        logger.info("Parameter Extraction AI Service initialized")

    async def initialize(self) -> None:
        """Initialisiert den Parameter Extraction AI Service"""
        try:
            self.openai_service = OpenAILLMService()
            # OpenAI service doesn't need explicit initialization - test with health check
            health_status = await self.openai_service.health_check()
            if health_status.get("status") != "healthy":
                raise Exception(f"OpenAI service unhealthy: {health_status.get('error', 'Unknown error')}")

            self.is_initialized = True
            logger.info("Parameter Extraction AI Service fully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Parameter Extraction AI: {str(e)}")
            raise

    async def extract_parameters(
        self,
        user_message: str,
        context: ExtractionContext,
        mode: ParameterExtractionMode = ParameterExtractionMode.BALANCED
    ) -> ParameterExtractionResult:
        """
        Extrahiert Parameter aus User-Message mit KI-Power

        Args:
            user_message: Die zu analysierende Nachricht
            context: Kontext-Informationen
            mode: Extraktions-Modus (precise/balanced/fast)

        Returns:
            ParameterExtractionResult mit extrahierten Parametern und Metriken
        """
        if not self.is_initialized:
            await self.initialize()

        start_time = time.time()

        try:
            # 1. Context Analysis
            context_analysis = await self._analyze_extraction_context(context)

            # 2. Primary Extraction mit OpenAI
            primary_result = await self._extract_with_openai(
                user_message, context, mode, context_analysis
            )

            # 3. Validation & Quality Scoring
            validated_result = await self._validate_and_score(
                primary_result, context, context_analysis
            )

            # 4. Secondary Extraction (falls notwendig)
            if validated_result.confidence_scores and min(validated_result.confidence_scores.values()) < 0.7:
                secondary_result = await self._secondary_extraction(
                    user_message, context, validated_result
                )
                validated_result = self._merge_extraction_results(validated_result, secondary_result)

            # 5. Final Processing
            final_result = await self._finalize_extraction(validated_result, context)
            final_result.processing_time = time.time() - start_time

            logger.info(f"Parameter extraction completed in {final_result.processing_time:.2f}s")
            return final_result

        except Exception as e:
            logger.error(f"Parameter extraction failed: {str(e)}")
            return ParameterExtractionResult(
                extracted_parameters={},
                confidence_scores={},
                extraction_method="error",
                processing_time=time.time() - start_time,
                warnings=[f"Extraction failed: {str(e)}"]
            )

    async def _analyze_extraction_context(self, context: ExtractionContext) -> Dict[str, Any]:
        """Analysiert den Kontext für optimale StreamWorks-Extraktion"""

        # Use new StreamWorks schemas
        try:
            stream_type = StreamType(context.job_type)
            schema = get_schema_for_type(stream_type)
        except ValueError:
            # Fallback for unknown job types
            stream_type = StreamType.STANDARD
            schema = get_schema_for_type(stream_type)

        # Extract required and optional parameters from schema
        required_params = []
        optional_params = []

        # Base parameters
        if "required" in schema:
            required_params.extend(schema["required"].keys())
        if "optional" in schema:
            optional_params.extend(schema["optional"].keys())

        # Type-specific parameters
        specific_key = f"{stream_type.value.lower()}_specific"
        if specific_key in schema:
            if "required" in schema[specific_key]:
                required_params.extend(schema[specific_key]["required"].keys())
            if "optional" in schema[specific_key]:
                optional_params.extend(schema[specific_key]["optional"].keys())

        analysis = {
            "job_type": context.job_type,
            "stream_type": stream_type,
            "required_parameters": required_params,
            "optional_parameters": optional_params,
            "schema": schema,
            "conversation_length": len(context.conversation_history),
            "existing_parameters": list(context.extracted_parameters.keys()),
            "missing_required": get_missing_parameters(context.extracted_parameters, stream_type),
            "streamworks_patterns": self.streamworks_patterns,
            "content_keywords": self.content_keywords
        }

        return analysis

    async def _extract_with_openai(
        self,
        user_message: str,
        context: ExtractionContext,
        mode: ParameterExtractionMode,
        context_analysis: Dict[str, Any]
    ) -> ParameterExtractionResult:
        """Primäre Parameter-Extraktion mit OpenAI"""

        config = self.extraction_config[mode.value]

        # Spezialisierter Prompt für Parameter-Extraktion
        system_prompt = self._build_extraction_prompt(context, context_analysis)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analysiere diese Nachricht und extrahiere Parameter: {user_message}"}
        ]

        try:
            # Use chat_completion method with JSON mode for structured output
            response_data = await self.openai_service.chat_completion(
                messages=messages,
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                json_mode=True
            )

            # Extract the content from the response (chat_completion format)
            if "choices" in response_data and response_data["choices"]:
                response = response_data["choices"][0]["message"]["content"]
            else:
                response = response_data.get("response", "")

            # Parse JSON Response with robust extraction
            extracted_data = self._parse_json_response(response)

            # Build Result
            result = ParameterExtractionResult(
                extracted_parameters=extracted_data.get("parameters", {}),
                confidence_scores=extracted_data.get("confidence_scores", {}),
                extraction_method=f"openai_{mode.value}",
                processing_time=0.0,
                suggestions=extracted_data.get("suggestions", []),
                warnings=extracted_data.get("warnings", [])
            )

            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse OpenAI response as JSON: {str(e)}")
            return self._fallback_extraction(user_message, context)
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            return self._fallback_extraction(user_message, context)

    def _build_extraction_prompt(self, context: ExtractionContext, analysis: Dict[str, Any]) -> str:
        """Baut hochpräzisen StreamWorks-spezifischen Prompt"""

        stream_type = analysis.get("stream_type", StreamType.STANDARD)
        streamworks_patterns = analysis.get("streamworks_patterns", {})

        base_prompt = f"""Du bist ein StreamWorks-Experte für PRÄZISE Parameter-Extraktion aus natürlichen User-Nachrichten.

STREAM-TYP: {stream_type.value}

ERFORDERLICHE PARAMETER:
{json.dumps(analysis["required_parameters"], indent=2)}

OPTIONALE PARAMETER:
{json.dumps(analysis["optional_parameters"], indent=2)}

BEREITS EXTRAHIERTE PARAMETER:
{json.dumps(context.extracted_parameters, indent=2)}

STREAMWORKS-SPEZIFISCHE ERKENNUNGSPATTERNS:
- Bekannte Agents: {', '.join(streamworks_patterns.get('agents', []))}
- SAP-Systeme: {', '.join(streamworks_patterns.get('sap_systems', []))}
- Job-Types: {', '.join(streamworks_patterns.get('job_types', []))}
- Kalender: {', '.join(streamworks_patterns.get('calendars', []))}
"""

        # Stream-Type-spezifische Beispiele und Patterns
        if stream_type == StreamType.SAP:
            base_prompt += self._build_sap_extraction_examples()
        elif stream_type == StreamType.FILE_TRANSFER:
            base_prompt += self._build_transfer_extraction_examples()
        else:
            base_prompt += self._build_standard_extraction_examples()

        base_prompt += f"""

WICHTIGE EXTRAKTIONSREGELN:
1. Erkenne ALLE Parameter in einer Nachricht (Multi-Parameter-Extraktion)
2. Stream-Namen: Häufig nach "streamname:", "stream:", "heißt", "name"
3. Agents: Erkenne bekannte Agent-Namen oder Hostnames
4. Pfade: Windows (C:\\) und Linux (/var/) unterscheiden
5. SAP-Spezifisch: System (3 Zeichen), Mandant (3 Zahlen), Transaktionen
6. Confidence: 0.9+ für exakte Matches, 0.7+ für Pattern-Matches, 0.5+ für Interpretationen

ANTWORTE NUR mit diesem JSON-Format:
{{
  "parameters": {{
    "parameter_name": "extracted_value"
  }},
  "confidence_scores": {{
    "parameter_name": 0.95
  }},
  "suggestions": ["Hilfreiche Hinweise falls Parameter unklar"],
  "warnings": ["Warnungen bei unsicheren Extraktionen"],
  "extraction_reasoning": "Kurze Erklärung der Extraktion"
}}"""

        return base_prompt

    def _build_sap_extraction_examples(self) -> str:
        """SAP-spezifische Extraktionsbeispiele"""
        return """

SAP-STREAM EXTRAKTIONS-BEISPIELE:

Beispiel 1: "Ich brauche einen SAP Export von PA1_100 mit jexa4S für Kalender"
→ Extrahiert: sap_system="PA1", sap_mandant="100", sap_job_type="EXPORT", calendar_export=true

Beispiel 2: "streamname:PROD_SAP_Daily, läuft auf gtlnmiwvm1636, ZTV System"
→ Extrahiert: stream_name="PROD_SAP_Daily", agent_detail="gtlnmiwvm1636", sap_system="ZTV"

Beispiel 3: "Fabrikkalender aus SAP exportieren, System PRD Mandant 300"
→ Extrahiert: sap_system="PRD", sap_mandant="300", calendar_export=true, sap_job_type="EXPORT"

SAP-PATTERN-ERKENNUNG:
- SAP-Systeme: ZTV, PA1, PRD, QAS (meist 3 Zeichen)
- Mandanten: 100, 300, 500 (meist 3 Zahlen)
- jexa4S Keywords: jexa, export, import, calendar
- Transaktionen: EXE_CAL_EXPORT, SE16, SM37"""

    def _build_transfer_extraction_examples(self) -> str:
        """File Transfer-spezifische Extraktionsbeispiele"""
        return """

FILE-TRANSFER EXTRAKTIONS-BEISPIELE:

Beispiel 1: "streamname:WIN_TRANSFER, kopiere von C:\\temp zu \\\\backup\\archive"
→ Extrahiert: stream_name="WIN_TRANSFER", source_path="C:\\temp", target_path="\\\\backup\\archive", platform="Windows"

Beispiel 2: "Datei Transfer von gtlnmiwvm1636 zu gtasswvv15778, SFTP verwenden"
→ Extrahiert: source_agent="gtlnmiwvm1636", target_agent="gtasswvv15778", transfer_method="SFTP"

Beispiel 3: "XML Dateien kopieren, Quelle /var/export, Ziel /backup/data"
→ Extrahiert: source_path="/var/export", target_path="/backup/data", file_pattern="*.xml", platform="Linux"

TRANSFER-PATTERN-ERKENNUNG:
- Pfade Windows: C:\\, D:\\, \\\\server\\
- Pfade Linux: /var/, /opt/, /home/, /tmp/
- Transfer-Methoden: COPY, FTP, SFTP, RSYNC, SCP
- Agents: gtlnmiwvm1636, gtasswvv15778, localhost"""

    def _build_standard_extraction_examples(self) -> str:
        """Standard-Stream Extraktionsbeispiele"""
        return """

STANDARD-STREAM EXTRAKTIONS-BEISPIELE:

Beispiel 1: "streamname:BATCH_PROCESS, führe python process.py aus"
→ Extrahiert: stream_name="BATCH_PROCESS", main_script="python process.py", job_type="Linux"

Beispiel 2: "Windows Batch Job, batch_report.bat in C:\\scripts ausführen"
→ Extrahiert: main_script="batch_report.bat", working_directory="C:\\scripts", job_type="Windows"

Beispiel 3: "Shell Script /opt/daily_report.sh mit Parametern --verbose"
→ Extrahiert: main_script="/opt/daily_report.sh", parameters="--verbose", job_type="Linux"

STANDARD-PATTERN-ERKENNUNG:
- Scripts: .py, .bat, .sh, .exe
- Commands: python, java, powershell, bash
- Platforms: Windows (C:\\, .bat), Linux (/opt/, .sh)"""

        return base_prompt

    async def _validate_and_score(
        self,
        result: ParameterExtractionResult,
        context: ExtractionContext,
        analysis: Dict[str, Any]
    ) -> ParameterExtractionResult:
        """Validiert extrahierte Parameter und berechnet Quality Scores"""

        validated_parameters = {}
        confidence_scores = {}
        warnings = list(result.warnings)

        for param_name, param_value in result.extracted_parameters.items():

            # Pattern Validation using StreamWorks patterns
            pattern = None

            # Check for StreamWorks-specific validation patterns
            streamworks_patterns = analysis.get("streamworks_patterns", {})

            if param_name == "agent_detail" and streamworks_patterns.get("agents"):
                pattern = streamworks_patterns["agents"]
            elif param_name == "sap_system" and streamworks_patterns.get("sap_systems"):
                pattern = streamworks_patterns["sap_systems"]
            elif param_name == "sap_mandant" and streamworks_patterns.get("sap_mandants"):
                pattern = streamworks_patterns["sap_mandants"]
            elif param_name == "job_type" and streamworks_patterns.get("job_types"):
                pattern = streamworks_patterns["job_types"]
            elif param_name == "transfer_method" and streamworks_patterns.get("transfer_methods"):
                pattern = streamworks_patterns["transfer_methods"]
            elif param_name == "calendar_id" and streamworks_patterns.get("calendars"):
                pattern = streamworks_patterns["calendars"]

            if pattern:
                if isinstance(pattern, list):
                    # Enum validation
                    if param_value in pattern:
                        validated_parameters[param_name] = param_value
                        confidence_scores[param_name] = result.confidence_scores.get(param_name, 0.8)
                    else:
                        warnings.append(f"Parameter '{param_name}' value '{param_value}' not in allowed values: {pattern}")
                        confidence_scores[param_name] = 0.3
                elif isinstance(pattern, str):
                    # Regex validation
                    import re
                    if re.match(pattern, str(param_value)):
                        validated_parameters[param_name] = param_value
                        confidence_scores[param_name] = result.confidence_scores.get(param_name, 0.8)
                    else:
                        warnings.append(f"Parameter '{param_name}' value '{param_value}' doesn't match pattern: {pattern}")
                        confidence_scores[param_name] = 0.4
            else:
                # No pattern - accept with original confidence
                validated_parameters[param_name] = param_value
                confidence_scores[param_name] = result.confidence_scores.get(param_name, 0.7)

        # Quality Scores berechnen
        precision_score = self._calculate_precision_score(validated_parameters, analysis)
        completeness_score = self._calculate_completeness_score(validated_parameters, analysis)
        consistency_score = self._calculate_consistency_score(validated_parameters, context)

        result.extracted_parameters = validated_parameters
        result.confidence_scores = confidence_scores
        result.warnings = warnings
        result.precision_score = precision_score
        result.completeness_score = completeness_score
        result.consistency_score = consistency_score

        return result

    def _calculate_precision_score(
        self,
        parameters: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> float:
        """Berechnet Precision Score basierend auf Parameter-Qualität"""
        if not parameters:
            return 0.0

        total_score = 0.0
        for param_name, param_value in parameters.items():
            if param_name in analysis["required_parameters"]:
                total_score += 1.0  # Required parameters get full score
            elif param_name in analysis["optional_parameters"]:
                total_score += 0.8  # Optional parameters get reduced score
            else:
                total_score += 0.5  # Unknown parameters get low score

        return min(total_score / len(parameters), 1.0)

    def _calculate_completeness_score(
        self,
        parameters: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> float:
        """Berechnet Completeness Score basierend auf erforderlichen Parametern"""
        required_params = analysis["required_parameters"]
        if not required_params:
            return 1.0

        found_required = sum(1 for param in required_params if param in parameters)
        return found_required / len(required_params)

    def _calculate_consistency_score(
        self,
        parameters: Dict[str, Any],
        context: ExtractionContext
    ) -> float:
        """Berechnet Consistency Score basierend auf Kontext-Konsistenz"""
        if not context.extracted_parameters:
            return 1.0

        consistency_score = 1.0

        # Check for parameter conflicts
        for param_name, new_value in parameters.items():
            if param_name in context.extracted_parameters:
                old_value = context.extracted_parameters[param_name]
                if old_value != new_value:
                    consistency_score -= 0.2  # Penalty for conflicts

        return max(consistency_score, 0.0)

    async def _secondary_extraction(
        self,
        user_message: str,
        context: ExtractionContext,
        primary_result: ParameterExtractionResult
    ) -> ParameterExtractionResult:
        """Sekundäre Extraktion für niedrige Confidence Scores"""

        # Fokussierte Re-Extraktion mit anderem Ansatz
        focused_prompt = f"""
Fokussierte Parameter-Extraktion für unsichere Parameter.

NACHRICHT: {user_message}
JOB TYPE: {context.job_type}

UNSICHERE PARAMETER AUS PRIMÄRER EXTRAKTION:
{json.dumps({k: v for k, v in primary_result.confidence_scores.items() if v < 0.7}, indent=2)}

Analysiere die Nachricht erneut und extrahiere die unsicheren Parameter mit höchster Präzision.
Antworte nur mit JSON im gleichen Format.
"""

        try:
            messages = [
                {"role": "system", "content": "Du bist ein Experte für präzise Parameter-Extraktion."},
                {"role": "user", "content": focused_prompt}
            ]

            response_data = await self.openai_service.chat_completion(
                messages=messages,
                model="gpt-4o",  # Use consistent model with JSON mode support
                temperature=0.05,  # Very low temperature for precision
                max_tokens=500,
                json_mode=True
            )

            # Extract the content from the response (chat_completion format)
            if "choices" in response_data and response_data["choices"]:
                response = response_data["choices"][0]["message"]["content"]
            else:
                response = response_data.get("response", "")

            extracted_data = json.loads(response)

            return ParameterExtractionResult(
                extracted_parameters=extracted_data.get("parameters", {}),
                confidence_scores=extracted_data.get("confidence_scores", {}),
                extraction_method="openai_secondary",
                processing_time=0.0,
                suggestions=extracted_data.get("suggestions", [])
            )

        except Exception as e:
            logger.warning(f"Secondary extraction failed: {str(e)}")
            return ParameterExtractionResult(
                extracted_parameters={},
                confidence_scores={},
                extraction_method="secondary_failed",
                processing_time=0.0
            )

    def _merge_extraction_results(
        self,
        primary: ParameterExtractionResult,
        secondary: ParameterExtractionResult
    ) -> ParameterExtractionResult:
        """Merged primäre und sekundäre Extraktion intelligent"""

        merged_parameters = dict(primary.extracted_parameters)
        merged_confidence = dict(primary.confidence_scores)
        merged_suggestions = list(primary.suggestions)

        # Merge secondary results where confidence is higher
        for param_name, param_value in secondary.extracted_parameters.items():
            secondary_confidence = secondary.confidence_scores.get(param_name, 0.0)
            primary_confidence = primary.confidence_scores.get(param_name, 0.0)

            if secondary_confidence > primary_confidence:
                merged_parameters[param_name] = param_value
                merged_confidence[param_name] = secondary_confidence

        merged_suggestions.extend(secondary.suggestions)

        primary.extracted_parameters = merged_parameters
        primary.confidence_scores = merged_confidence
        primary.suggestions = merged_suggestions
        primary.extraction_method = f"{primary.extraction_method}+secondary"

        return primary

    async def _finalize_extraction(
        self,
        result: ParameterExtractionResult,
        context: ExtractionContext
    ) -> ParameterExtractionResult:
        """Finalisiert die Extraktion mit intelligenter Post-Processing"""

        # CRITICAL: Stream-Name Post-Processing für alle Job-Types
        result = self._postprocess_stream_names(result, context)

        # Job-Type specific post-processing
        if context.job_type == "FILE_TRANSFER":
            result = self._postprocess_file_transfer(result)
        elif context.job_type == "SAP":
            result = self._postprocess_sap(result)

        # Generate suggestions for missing required parameters using StreamWorks schemas
        try:
            stream_type = StreamType(context.job_type)
            missing_params = get_missing_parameters(result.extracted_parameters, stream_type)

            for param in missing_params:
                result.suggestions.append(f"Erforderlicher Parameter '{param}' fehlt noch")
        except (ValueError, ImportError) as e:
            logger.warning(f"Could not generate missing parameter suggestions: {e}")

        return result

    def _postprocess_stream_names(
        self,
        result: ParameterExtractionResult,
        context: ExtractionContext
    ) -> ParameterExtractionResult:
        """Intelligente Post-Processing für Stream-Namen"""

        if "stream_name" not in result.extracted_parameters:
            return result

        stream_name = result.extracted_parameters["stream_name"]
        original_name = stream_name
        confidence = result.confidence_scores.get("stream_name", 0.0)

        # Pattern 1: "streamname:VALUE" → "VALUE"
        if ":" in stream_name:
            parts = stream_name.split(":")
            if len(parts) >= 2:
                cleaned_name = parts[-1].strip()
                if cleaned_name and len(cleaned_name) > 0:
                    stream_name = cleaned_name
                    confidence = max(confidence, 0.9)  # High confidence for clear pattern
                    result.suggestions.append(f"Stream-Name aus Pattern 'streamname:VALUE' extrahiert")

        # Pattern 2: Entferne deutsche Stopwörter
        german_stopwords = ["der", "die", "das", "ein", "eine", "ist", "sind", "soll", "sollte", "wird", "werden", "für", "zu", "mit", "von", "nach", "bei", "auf", "in", "an", "über", "unter", "durch", "gegen", "ohne", "um"]
        words = stream_name.split()

        # Entferne Stopwörter nur wenn mehr als ein Wort vorhanden
        if len(words) > 1:
            filtered_words = []
            for word in words:
                clean_word = word.strip(".,!?;:()[]{}\"'").lower()
                if clean_word not in german_stopwords and len(clean_word) > 0:
                    # Behalte das erste alphanumerische Wort
                    if clean_word.replace("_", "").replace("-", "").isalnum():
                        filtered_words.append(word.strip(".,!?;:()[]{}\"'"))

            if filtered_words:
                stream_name = filtered_words[0]  # Nimm das erste gefilterte Wort
                confidence = max(confidence, 0.85)
                result.suggestions.append(f"Stream-Name durch Stopwort-Entfernung bereinigt")

        # Pattern 3: Entferne Satzzeichen am Ende
        stream_name = stream_name.strip(".,!?;:()[]{}\"' ")

        # Pattern 4: Validiere dass es ein gültiger Stream-Name ist
        if stream_name and self._is_valid_stream_name(stream_name):
            result.extracted_parameters["stream_name"] = stream_name
            result.confidence_scores["stream_name"] = confidence

            if original_name != stream_name:
                result.suggestions.append(f"Stream-Name von '{original_name}' zu '{stream_name}' bereinigt")
        else:
            # Fallback: Versuche aus der Original-Nachricht zu extrahieren
            extracted_from_message = self._extract_stream_name_regex(context)
            if extracted_from_message:
                result.extracted_parameters["stream_name"] = extracted_from_message
                result.confidence_scores["stream_name"] = 0.8
                result.suggestions.append(f"Stream-Name durch Regex-Fallback extrahiert: '{extracted_from_message}'")
            else:
                # Entferne den Parameter wenn er ungültig ist
                result.warnings.append(f"Ungültiger Stream-Name '{stream_name}' entfernt")
                del result.extracted_parameters["stream_name"]
                if "stream_name" in result.confidence_scores:
                    del result.confidence_scores["stream_name"]

        return result

    def _is_valid_stream_name(self, name: str) -> bool:
        """Validiert ob ein Stream-Name gültig ist"""
        if not name or len(name) < 2:
            return False

        # Darf nur alphanumerische Zeichen, Unterstriche und Bindestriche enthalten
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False

        # Darf nicht nur aus Zahlen bestehen (zu generisch)
        if name.isdigit():
            return False

        # Darf keine deutschen Stopwörter sein
        german_stopwords = ["der", "die", "das", "ein", "eine", "ist", "sind", "soll", "wird", "für", "zu", "mit", "von", "nach", "bei", "auf", "in", "an", "über", "unter", "durch", "gegen", "ohne", "um", "und", "oder", "aber", "denn", "doch", "noch", "nur", "auch", "nicht", "kein", "keine", "kann", "muss", "darf", "sollte", "könnte", "hätte", "wäre", "würde"]
        if name.lower() in german_stopwords:
            return False

        return True

    def _extract_stream_name_regex(self, context: ExtractionContext) -> Optional[str]:
        """Fallback: Extrahiert Stream-Namen mit Regex aus der letzten Nachricht"""

        if not context.conversation_history:
            return None

        # Hole die letzte User-Nachricht
        last_message = None
        for msg in reversed(context.conversation_history):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break

        if not last_message:
            return None

        import re

        # Pattern 1: "streamname:VALUE"
        match = re.search(r'streamname\s*:\s*([a-zA-Z0-9_-]+)', last_message, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern 2: "stream name VALUE" oder "stream VALUE"
        match = re.search(r'stream\s+(?:name\s+)?([a-zA-Z0-9_-]+)', last_message, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if self._is_valid_stream_name(candidate):
                return candidate

        # Pattern 3: Alphanumerische Sequenz nach "stream" oder vor Keywords
        keywords = ["transfer", "daten", "job", "soll", "ist", "für"]
        for keyword in keywords:
            pattern = rf'([a-zA-Z0-9_-]+).*?{keyword}'
            match = re.search(pattern, last_message, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                if self._is_valid_stream_name(candidate) and len(candidate) > 2:
                    return candidate

        return None

    def _postprocess_file_transfer(self, result: ParameterExtractionResult) -> ParameterExtractionResult:
        """Post-Processing speziell für FILE_TRANSFER Jobs"""

        # Auto-detect job type if stream indicates file transfer
        if "stream_name" in result.extracted_parameters:
            stream_name = result.extracted_parameters["stream_name"]
            if any(keyword in stream_name.lower() for keyword in ["transfer", "file", "copy", "move"]):
                if "job_type" not in result.extracted_parameters:
                    result.extracted_parameters["job_type"] = "FILE_TRANSFER"
                    result.confidence_scores["job_type"] = 0.8
                    result.suggestions.append("Job-Type 'FILE_TRANSFER' automatisch erkannt")

        return result

    def _postprocess_sap(self, result: ParameterExtractionResult) -> ParameterExtractionResult:
        """Post-Processing speziell für SAP Jobs"""

        # SAP system validation
        if "sap_system" in result.extracted_parameters:
            sap_system = result.extracted_parameters["sap_system"].upper()
            if len(sap_system) == 3 and sap_system.isalnum():
                result.extracted_parameters["sap_system"] = sap_system
                result.confidence_scores["sap_system"] = min(
                    result.confidence_scores.get("sap_system", 0.7) + 0.1, 1.0
                )

        return result

    def _parse_json_response(self, response: str) -> dict:
        """Robust JSON parsing with advanced fallback extraction"""
        if not response or response.strip() == "":
            logger.warning("Empty response received from OpenAI")
            return {
                "parameters": {},
                "confidence_scores": {},
                "suggestions": [],
                "warnings": ["Empty response from OpenAI"]
            }

        response = response.strip()

        try:
            # Try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {str(e)}")

            # Advanced fallback extraction
            import re

            # Method 1: Look for JSON blocks with nested structures
            json_patterns = [
                r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}',  # Nested JSON
                r'\{[^{}]*\}',  # Simple JSON
                r'```json\s*(\{.*?\})\s*```',  # Markdown JSON blocks
                r'```\s*(\{.*?\})\s*```',  # Generic code blocks
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                for match in matches:
                    try:
                        # Clean up common issues
                        cleaned_match = match.strip()
                        # Remove trailing commas before closing braces
                        cleaned_match = re.sub(r',(\s*[}\]])', r'\1', cleaned_match)

                        parsed = json.loads(cleaned_match)
                        logger.info(f"Successfully parsed JSON using pattern: {pattern[:20]}...")
                        return parsed
                    except json.JSONDecodeError:
                        continue

            # Method 2: Extract key-value pairs manually
            logger.warning("Attempting manual key-value extraction")
            extracted_data = self._manual_parameter_extraction(response)
            if extracted_data:
                return extracted_data

            # Method 3: Last resort - return structured empty response
            logger.error(f"Could not extract valid JSON from response: {response[:200]}...")
            return {
                "parameters": {},
                "confidence_scores": {},
                "suggestions": ["JSON parsing failed - manual review needed"],
                "warnings": [f"Failed to parse response: {response[:100]}..."]
            }

    def _manual_parameter_extraction(self, response: str) -> Optional[dict]:
        """Manual parameter extraction when JSON parsing fails"""
        import re

        # Initialize result structure
        result = {
            "parameters": {},
            "confidence_scores": {},
            "suggestions": [],
            "warnings": ["Manual extraction used due to JSON parsing failure"]
        }

        try:
            # Extract stream_name patterns
            stream_patterns = [
                r'"stream_name"\s*:\s*"([^"]+)"',
                r"'stream_name'\s*:\s*'([^']+)'",
                r'stream_name[:\s]+([a-zA-Z0-9_-]+)',
                r'streamname[:\s]+([a-zA-Z0-9_-]+)',
            ]

            for pattern in stream_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    stream_name = match.group(1).strip()
                    if self._is_valid_stream_name(stream_name):
                        result["parameters"]["stream_name"] = stream_name
                        result["confidence_scores"]["stream_name"] = 0.7
                        break

            # Extract confidence scores
            confidence_pattern = r'"([^"]+)"\s*:\s*([0-9]*\.?[0-9]+)'
            confidence_matches = re.findall(confidence_pattern, response)
            for param, score in confidence_matches:
                try:
                    score_val = float(score)
                    if 0.0 <= score_val <= 1.0:
                        result["confidence_scores"][param] = score_val
                except ValueError:
                    continue

            # Extract other common parameters
            param_patterns = {
                "job_type": r'"job_type"\s*:\s*"([^"]+)"',
                "description": r'"description"\s*:\s*"([^"]+)"',
                "priority": r'"priority"\s*:\s*"([^"]+)"',
                "source_path": r'"source_path"\s*:\s*"([^"]+)"',
                "destination_path": r'"destination_path"\s*:\s*"([^"]+)"',
            }

            for param_name, pattern in param_patterns.items():
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    result["parameters"][param_name] = match.group(1).strip()
                    if param_name not in result["confidence_scores"]:
                        result["confidence_scores"][param_name] = 0.6

            # Only return if we extracted something
            if result["parameters"]:
                logger.info(f"Manual extraction recovered {len(result['parameters'])} parameters")
                return result

        except Exception as e:
            logger.error(f"Manual extraction failed: {str(e)}")

        return None

    def _fallback_extraction(
        self,
        user_message: str,
        context: ExtractionContext
    ) -> ParameterExtractionResult:
        """Fallback-Extraktion ohne OpenAI (Rule-based)"""

        logger.info("Using fallback extraction (rule-based)")

        extracted_params = {}
        confidence_scores = {}

        # Simple keyword-based extraction
        message_lower = user_message.lower()

        # Stream name extraction
        stream_keywords = ["stream", "name", "heißt", "genannt"]
        for keyword in stream_keywords:
            if keyword in message_lower:
                # Look for stream name patterns
                words = user_message.split()
                for i, word in enumerate(words):
                    if keyword in word.lower() and i + 1 < len(words):
                        potential_name = words[i + 1].strip("\"'")
                        if potential_name and len(potential_name) > 2:
                            extracted_params["stream_name"] = potential_name
                            confidence_scores["stream_name"] = 0.6
                            break

        # Job type detection
        job_type_keywords = {
            "FILE_TRANSFER": ["transfer", "datei", "file", "kopieren", "verschieben"],
            "SAP": ["sap", "tabelle", "table"],
            "STANDARD": ["standard", "normal"]
        }

        for job_type, keywords in job_type_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted_params["job_type"] = job_type
                confidence_scores["job_type"] = 0.5
                break

        return ParameterExtractionResult(
            extracted_parameters=extracted_params,
            confidence_scores=confidence_scores,
            extraction_method="fallback_rules",
            processing_time=0.0,
            warnings=["Fallback extraction used - consider reviewing parameters"]
        )


# Singleton instance
_parameter_extraction_ai = None

def get_parameter_extraction_ai() -> ParameterExtractionAI:
    """Get Parameter Extraction AI singleton"""
    global _parameter_extraction_ai
    if _parameter_extraction_ai is None:
        _parameter_extraction_ai = ParameterExtractionAI()
    return _parameter_extraction_ai