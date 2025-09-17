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
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 1000,
                "retry_attempts": 3
            },
            "balanced": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.2,
                "max_tokens": 800,
                "retry_attempts": 2
            },
            "fast": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 500,
                "retry_attempts": 1
            }
        }

        # Parameter Templates für verschiedene Job-Types
        self.parameter_templates = {
            "STANDARD": {
                "required": ["stream_name", "description"],
                "optional": ["priority", "schedule"],
                "patterns": {
                    "stream_name": r"^[A-Za-z0-9_-]+$",
                    "priority": ["low", "medium", "high", "critical"]
                }
            },
            "SAP": {
                "required": ["sap_system", "table_name", "stream_name"],
                "optional": ["filter_conditions", "schedule"],
                "patterns": {
                    "sap_system": r"^[A-Z]{3}$",
                    "table_name": r"^[A-Z][A-Z0-9_]*$"
                }
            },
            "FILE_TRANSFER": {
                "required": ["source_path", "destination_path", "stream_name"],
                "optional": ["file_pattern", "schedule", "compression"],
                "patterns": {
                    "file_pattern": r".*\.(txt|csv|xml|json)$"
                }
            },
            "CUSTOM": {
                "required": ["stream_name", "custom_logic"],
                "optional": ["parameters", "schedule"],
                "patterns": {}
            }
        }

        logger.info("Parameter Extraction AI Service initialized")

    async def initialize(self) -> None:
        """Initialisiert den Parameter Extraction AI Service"""
        try:
            self.openai_service = OpenAILLMService()
            await self.openai_service.initialize()
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
        """Analysiert den Kontext für optimale Extraktion"""

        job_template = self.parameter_templates.get(context.job_type, {})

        analysis = {
            "job_type": context.job_type,
            "required_parameters": job_template.get("required", []),
            "optional_parameters": job_template.get("optional", []),
            "parameter_patterns": job_template.get("patterns", {}),
            "conversation_length": len(context.conversation_history),
            "existing_parameters": list(context.extracted_parameters.keys()),
            "missing_required": []
        }

        # Fehlende erforderliche Parameter identifizieren
        for param in analysis["required_parameters"]:
            if param not in context.extracted_parameters:
                analysis["missing_required"].append(param)

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
            response = await self.openai_service.generate_completion(
                messages=messages,
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

            # Parse JSON Response
            extracted_data = json.loads(response)

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
        """Baut spezialisierten Prompt für Parameter-Extraktion"""

        prompt = f"""Du bist ein Experte für Parameter-Extraktion aus StreamWorks Job-Konfigurationen.

JOB TYPE: {context.job_type}

ERFORDERLICHE PARAMETER:
{json.dumps(analysis["required_parameters"], indent=2)}

OPTIONALE PARAMETER:
{json.dumps(analysis["optional_parameters"], indent=2)}

PARAMETER PATTERNS:
{json.dumps(analysis["parameter_patterns"], indent=2)}

BEREITS EXTRAHIERTE PARAMETER:
{json.dumps(context.extracted_parameters, indent=2)}

AUFGABE:
Analysiere die User-Nachricht und extrahiere alle relevanten Parameter mit maximaler Präzision.

BEISPIELE FÜR {context.job_type}:
"""

        # Job-Type spezifische Beispiele
        if context.job_type == "FILE_TRANSFER":
            prompt += """
"der stream 123cool soll ein daten transfer sein"
→ {"stream_name": "123cool", "job_type": "FILE_TRANSFER"}

"transfer von /source/data.csv nach /dest/ mit kompression"
→ {"source_path": "/source/data.csv", "destination_path": "/dest/", "compression": true}
"""
        elif context.job_type == "SAP":
            prompt += """
"SAP System P01 Tabelle BKPF für stream sap_accounting"
→ {"sap_system": "P01", "table_name": "BKPF", "stream_name": "sap_accounting"}
"""
        elif context.job_type == "STANDARD":
            prompt += """
"standard stream daily_reports mit hoher priorität"
→ {"stream_name": "daily_reports", "priority": "high"}
"""

        prompt += """

ANTWORT FORMAT (IMMER VALID JSON):
{
  "parameters": {
    "parameter_name": "extracted_value",
    ...
  },
  "confidence_scores": {
    "parameter_name": 0.95,
    ...
  },
  "suggestions": [
    "Optional: Suggest missing required parameters",
    "Optional: Suggest improvements"
  ],
  "warnings": [
    "Optional: Warn about potential issues"
  ]
}

REGELN:
1. Extrahiere NUR die Parameter, die EINDEUTIG aus der Nachricht ersichtlich sind
2. Verwende EXAKTE Werte, keine Interpretationen
3. Confidence Score: 0.0-1.0 (1.0 = absolut sicher)
4. Bei Unsicherheit: niedrigerer Confidence Score
5. IMMER valid JSON zurückgeben
"""

        return prompt

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

            # Pattern Validation
            if param_name in analysis["parameter_patterns"]:
                pattern = analysis["parameter_patterns"][param_name]
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

            response = await self.openai_service.generate_completion(
                messages=messages,
                model="gpt-4",  # Use best model for secondary extraction
                temperature=0.05,  # Very low temperature for precision
                max_tokens=500
            )

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
        """Finalisiert die Extraktion mit letzten Optimierungen"""

        # Job-Type specific post-processing
        if context.job_type == "FILE_TRANSFER":
            result = self._postprocess_file_transfer(result)
        elif context.job_type == "SAP":
            result = self._postprocess_sap(result)

        # Generate suggestions for missing required parameters
        job_template = self.parameter_templates.get(context.job_type, {})
        required_params = job_template.get("required", [])

        for param in required_params:
            if param not in result.extracted_parameters:
                result.suggestions.append(f"Erforderlicher Parameter '{param}' fehlt noch")

        return result

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