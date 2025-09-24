"""
Unified Parameter Extractor - Schema-basierte Job-Type Erkennung
Vereinfachte, elegante Lösung mit job-type-spezifischen Schemas
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

logger = logging.getLogger(__name__)

# ================================
# PYDANTIC MODELS
# ================================

class ExtractedParameter(BaseModel):
    """Einzelner extrahierter Parameter"""
    name: str = Field(description="Name des Parameters")
    value: Any = Field(description="Extrahierter Wert")
    confidence: float = Field(description="Konfidenz-Score 0.0-1.0")
    source_text: str = Field(description="Original-Text aus dem die Info extrahiert wurde")
    scope: str = Field(description="stream oder job", default="stream")

class UnifiedExtractionResult(BaseModel):
    """Ergebnis der vereinheitlichten Parameter-Extraktion"""
    detected_job_type: Optional[str] = Field(description="Erkannter Job-Type")
    confidence_score: float = Field(description="Gesamt-Konfidenz der Job-Type-Erkennung")

    # Parameter gruppiert nach Scope
    stream_parameters: List[ExtractedParameter] = Field(default_factory=list)
    job_parameters: List[ExtractedParameter] = Field(default_factory=list)

    # Status und Nachfragen
    missing_stream_parameters: List[str] = Field(default_factory=list)
    missing_job_parameters: List[str] = Field(default_factory=list)
    needs_clarification: bool = Field(description="Ob Nachfragen nötig sind", default=False)
    suggested_questions: List[str] = Field(default_factory=list)

    # Metadaten
    completion_percentage: float = Field(description="Vervollständigung in Prozent", default=0.0)
    next_required_parameter: Optional[str] = Field(description="Nächster erforderlicher Parameter", default=None)
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)

# ================================
# UNIFIED PARAMETER EXTRACTOR
# ================================

class UnifiedParameterExtractor:
    """
    Eleganter, schema-basierter Parameter-Extraktor

    Hauptvorteile:
    - Ein Schema pro Job-Type mit Keywords
    - Direkte Job-Type-Erkennung aus Schema
    - Vereinfachte Dialog-Logik
    - Konsistente Parameter-Struktur
    """

    def __init__(self, openai_api_key: str, schema_path: Optional[str] = None):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.1
        )

        # Lade vereinheitlichte Schemas
        if schema_path:
            self.schema_path = schema_path
        else:
            self.schema_path = Path(__file__).parent.parent.parent / "templates" / "unified_stream_schemas.json"

        self.schemas = self._load_unified_schemas()

        logger.info(f"UnifiedParameterExtractor initialisiert mit {len(self.schemas.get('job_type_schemas', {}))} Job-Types")

    def _load_unified_schemas(self) -> Dict[str, Any]:
        """Lädt die vereinheitlichten Schemas"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Vereinheitlichte Schemas geladen: Version {data.get('version', 'unknown')}")
            return data
        except FileNotFoundError:
            logger.error(f"Schema-Datei nicht gefunden: {self.schema_path}")
            return {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Schemas: {e}")
            return {}

    async def extract_parameters(
        self,
        user_message: str,
        existing_stream_params: Optional[Dict[str, Any]] = None,
        existing_job_params: Optional[Dict[str, Any]] = None,
        current_job_type: Optional[str] = None
    ) -> UnifiedExtractionResult:
        """
        Hauptmethode für Parameter-Extraktion

        Args:
            user_message: Die Nachricht des Users
            existing_stream_params: Bereits gesammelte Stream-Parameter
            existing_job_params: Bereits gesammelte Job-Parameter
            current_job_type: Aktueller Job-Type (falls bereits bestimmt)

        Returns:
            UnifiedExtractionResult mit allen extrahierten Informationen
        """
        try:
            logger.info(f"Starte vereinheitlichte Extraktion für: '{user_message[:80]}...'")

            # Schritt 1: Job-Type-Erkennung (falls noch nicht bestimmt)
            if not current_job_type:
                job_type, confidence = await self._detect_job_type_unified(user_message)
            else:
                job_type = current_job_type
                confidence = 1.0  # Bereits bestätigt

            # Schritt 2: Parameter-Extraktion für den Job-Type
            if job_type:
                result = await self._extract_for_job_type(
                    user_message=user_message,
                    job_type=job_type,
                    detection_confidence=confidence,
                    existing_stream_params=existing_stream_params or {},
                    existing_job_params=existing_job_params or {}
                )
            else:
                # Kein Job-Type erkannt - generische Extraktion
                result = await self._generic_extraction(user_message)

            logger.info(f"Extraktion abgeschlossen: Job-Type={result.detected_job_type}, Confidence={result.confidence_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"Fehler bei vereinheitlichter Parameter-Extraktion: {e}")
            return UnifiedExtractionResult(
                detected_job_type=None,
                confidence_score=0.0,
                needs_clarification=True,
                suggested_questions=["Entschuldigung, ich konnte Ihre Anfrage nicht verstehen. Könnten Sie sie anders formulieren?"],
                extraction_metadata={"error": str(e)}
            )

    async def _detect_job_type_unified(self, user_message: str) -> Tuple[Optional[str], float]:
        """
        Intelligente Job-Type-Erkennung basierend auf Schema-Keywords und Patterns

        Returns:
            Tuple[job_type, confidence_score]
        """
        message_lower = user_message.lower()
        job_schemas = self.schemas.get('job_type_schemas', {})
        detection_settings = self.schemas.get('detection_settings', {})

        confidence_scores = {}

        # Analysiere jeden Job-Type
        for job_type, schema in job_schemas.items():
            detection_config = schema.get('detection_config', {})

            # 1. Keyword-basierte Erkennung
            keywords = detection_config.get('keywords', [])
            keyword_matches = sum(1 for keyword in keywords if keyword in message_lower)
            keyword_confidence = min(0.4 + (0.2 * keyword_matches), 0.9) if keyword_matches > 0 else 0.0

            # 2. Pattern-basierte Erkennung
            patterns = detection_config.get('patterns', [])
            pattern_confidence = 0.0
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    pattern_confidence = max(pattern_confidence, 0.8)
                    logger.info(f"🎯 Pattern-Match für {job_type}: {pattern}")

            # 3. Kombiniere Scores mit Gewichtung
            pattern_weight = detection_settings.get('pattern_weight', 0.6)
            keyword_weight = detection_settings.get('keyword_weight', 0.4)

            combined_confidence = (
                pattern_confidence * pattern_weight +
                keyword_confidence * keyword_weight
            )

            # 4. Schema-spezifische Confidence-Boost
            confidence_boost = detection_config.get('confidence_boost', 1.0)
            final_confidence = min(combined_confidence * confidence_boost, 1.0)

            if final_confidence > 0:
                confidence_scores[job_type] = final_confidence
                logger.info(f"🔍 {job_type}: keywords={keyword_matches}, pattern={pattern_confidence:.2f}, final={final_confidence:.2f}")

        # Bestimme besten Job-Type
        if not confidence_scores:
            logger.info("❓ Kein Job-Type erkannt")
            return None, 0.0

        best_job_type = max(confidence_scores.items(), key=lambda x: x[1])
        job_type, confidence = best_job_type

        # Konfidenz-Schwellenwerte prüfen
        thresholds = detection_settings.get('confidence_thresholds', {})
        high_threshold = thresholds.get('high_confidence', 0.85)

        if confidence >= high_threshold:
            logger.info(f"✅ Hohe Konfidenz: {job_type} ({confidence:.2f})")
            return job_type, confidence
        elif confidence >= thresholds.get('medium_confidence', 0.65):
            logger.info(f"⚠️ Mittlere Konfidenz: {job_type} ({confidence:.2f})")
            return job_type, confidence
        else:
            logger.info(f"❌ Niedrige Konfidenz: {job_type} ({confidence:.2f}) - keine automatische Auswahl")
            return None, confidence

    async def _extract_for_job_type(
        self,
        user_message: str,
        job_type: str,
        detection_confidence: float,
        existing_stream_params: Dict[str, Any],
        existing_job_params: Dict[str, Any]
    ) -> UnifiedExtractionResult:
        """Extrahiert Parameter für einen bestimmten Job-Type"""

        job_schema = self.schemas['job_type_schemas'][job_type]
        common_stream_params = self.schemas.get('common_stream_parameters', [])
        job_specific_params = job_schema.get('job_parameters', [])

        # Extrahiere Stream-Parameter
        stream_parameters = await self._extract_stream_parameters(
            user_message, common_stream_params, existing_stream_params
        )

        # Extrahiere Job-Parameter
        job_parameters = await self._extract_job_parameters(
            user_message, job_specific_params, existing_job_params
        )

        # Bestimme fehlende Parameter
        missing_stream = self._get_missing_parameters(common_stream_params, stream_parameters, existing_stream_params)
        missing_job = self._get_missing_parameters(job_specific_params, job_parameters, existing_job_params)

        # Generiere intelligente Nachfragen
        suggested_questions = await self._generate_smart_questions(
            missing_stream, missing_job, job_type, common_stream_params, job_specific_params
        )

        # Berechne Vervollständigung
        total_required = len([p for p in common_stream_params if p.get('required', False)])
        total_required += len([p for p in job_specific_params if p.get('required', False)])

        completed_params = len(stream_parameters) + len(job_parameters)
        existing_count = len(existing_stream_params) + len(existing_job_params)
        total_completed = completed_params + existing_count

        completion_percentage = min(total_completed / max(total_required, 1), 1.0) if total_required > 0 else 1.0

        # Bestimme nächsten erforderlichen Parameter
        next_param = None
        if missing_stream:
            next_param = missing_stream[0]
        elif missing_job:
            next_param = missing_job[0]

        return UnifiedExtractionResult(
            detected_job_type=job_type,
            confidence_score=detection_confidence,
            stream_parameters=stream_parameters,
            job_parameters=job_parameters,
            missing_stream_parameters=missing_stream,
            missing_job_parameters=missing_job,
            needs_clarification=len(missing_stream) > 0 or len(missing_job) > 0,
            suggested_questions=suggested_questions,
            completion_percentage=completion_percentage,
            next_required_parameter=next_param,
            extraction_metadata={
                "job_schema": job_schema['display_name'],
                "total_required_params": total_required,
                "timestamp": datetime.now().isoformat()
            }
        )

    async def _extract_stream_parameters(
        self,
        user_message: str,
        stream_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any]
    ) -> List[ExtractedParameter]:
        """Extrahiert Stream-Parameter mit LLM"""

        # Stream-Parameter Extraction Prompt
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
                        scope="stream"
                    ))

            logger.info(f"🎯 Stream-Parameter extrahiert: {len(parameters)} gefunden")
            return parameters

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM Stream-Extraktion fehlgeschlagen: {e}")
            return []

    async def _extract_job_parameters(
        self,
        user_message: str,
        job_param_schemas: List[Dict[str, Any]],
        existing_params: Dict[str, Any]
    ) -> List[ExtractedParameter]:
        """Extrahiert Job-spezifische Parameter mit LLM"""

        if not job_param_schemas:
            return []

        # Job-Parameter Extraction Prompt
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
                        scope="job"
                    ))

            logger.info(f"🎯 Job-Parameter extrahiert: {len(parameters)} gefunden")
            return parameters

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM Job-Extraktion fehlgeschlagen: {e}")
            return []

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

    async def _generate_smart_questions(
        self,
        missing_stream: List[str],
        missing_job: List[str],
        job_type: str,
        stream_schemas: List[Dict[str, Any]],
        job_schemas: List[Dict[str, Any]]
    ) -> List[str]:
        """Generiert intelligente Nachfragen für fehlende Parameter"""

        questions = []

        # Stream-Parameter Fragen (Priorität)
        if missing_stream:
            for param_name in missing_stream[:2]:  # Maximal 2 Stream-Fragen
                param_schema = next((p for p in stream_schemas if p['name'] == param_name), None)
                if param_schema:
                    questions.append(param_schema['chat_prompt'])

        # Job-Parameter Fragen
        if missing_job and len(questions) < 2:
            for param_name in missing_job[:2]:  # Maximal 2 Job-Fragen
                param_schema = next((p for p in job_schemas if p['name'] == param_name), None)
                if param_schema:
                    questions.append(param_schema['chat_prompt'])

        # Fallback-Fragen
        if not questions:
            if missing_stream or missing_job:
                questions.append("Möchten Sie weitere Parameter für die Konfiguration angeben?")
            else:
                questions.append("Soll ich die XML-Datei jetzt generieren?")

        return questions[:3]  # Maximal 3 Fragen

    async def _generic_extraction(self, user_message: str) -> UnifiedExtractionResult:
        """Fallback wenn kein Job-Type erkannt wurde"""

        return UnifiedExtractionResult(
            detected_job_type=None,
            confidence_score=0.0,
            needs_clarification=True,
            suggested_questions=[
                "Welchen Job-Type möchten Sie konfigurieren?",
                "Handelt es sich um einen File Transfer, SAP-Job oder Standard-Prozess?",
                "Beschreiben Sie, was der Stream machen soll."
            ],
            completion_percentage=0.0,
            extraction_metadata={"reason": "no_job_type_detected"}
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

_unified_extractor_instance: Optional[UnifiedParameterExtractor] = None

def get_unified_parameter_extractor(openai_api_key: Optional[str] = None) -> UnifiedParameterExtractor:
    """Factory function für UnifiedParameterExtractor"""
    global _unified_extractor_instance

    if _unified_extractor_instance is None:
        if not openai_api_key:
            from config import settings
            openai_api_key = settings.OPENAI_API_KEY

        _unified_extractor_instance = UnifiedParameterExtractor(openai_api_key)

    return _unified_extractor_instance