"""
LangExtract Parameter Service
Ersetzt UnifiedParameterExtractor mit Source-Grounded Parameter Extraction
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path

import langextract as lx
from pydantic import BaseModel

# Import our enhanced models
from models.source_grounded_models import (
    SourceGroundedParameter,
    JobTypeDetection,
    SourceGroundedExtractionResult,
    LangExtractConfig,
    ExtractionMetrics,
    StreamWorksSchema,
    calculate_highlight_coverage,
    merge_overlapping_ranges,
    validate_character_offsets
)

logger = logging.getLogger(__name__)


class LangExtractParameterService:
    """
    Hochmoderner Parameter-Extraktions-Service mit LangExtract

    Features:
    - Source-Grounded Parameter Extraction
    - Job-Type Detection mit Confidence
    - Interactive Parameter Correction
    - Comprehensive Error Handling
    - Performance Metrics
    """

    def __init__(self, config: Optional[LangExtractConfig] = None):
        """Initialize LangExtract Parameter Service"""

        # Load configuration
        if config is None:
            config = self._load_default_config()
        self.config = config

        # Initialize schema loader
        self.schema_loader = StreamWorksSchemaLoader()
        self.schemas = self.schema_loader.load_all_schemas()

        # Performance tracking
        self.metrics_collector = ExtractionMetricsCollector()

        # Cache für häufige Extraktionen
        self._extraction_cache: Dict[str, SourceGroundedExtractionResult] = {}

        logger.info(f"LangExtractParameterService initialized with {len(self.schemas)} schemas")

    def _load_default_config(self) -> LangExtractConfig:
        """Load default configuration from environment"""
        return LangExtractConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            enable_debug_logging=os.getenv("DEBUG", "false").lower() == "true"
        )

    async def extract_parameters_with_grounding(
        self,
        user_message: str,
        job_type: Optional[str] = None,
        existing_stream_params: Optional[Dict[str, Any]] = None,
        existing_job_params: Optional[Dict[str, Any]] = None
    ) -> SourceGroundedExtractionResult:
        """
        Hauptmethode für Source-Grounded Parameter Extraction

        Args:
            user_message: Die User-Nachricht
            job_type: Bekannter Job-Type (optional)
            existing_stream_params: Bereits gesammelte Stream-Parameter
            existing_job_params: Bereits gesammelte Job-Parameter

        Returns:
            SourceGroundedExtractionResult mit allen extrahierten Informationen
        """
        start_time = datetime.now()

        try:
            logger.info(f"🚀 Starting LangExtract parameter extraction for: '{user_message[:80]}...'")

            # 1. Job-Type Detection (falls nicht bekannt)
            if not job_type:
                job_type_detection = await self._detect_job_type_with_grounding(user_message)
                job_type = job_type_detection.detected_job_type
            else:
                # Create detection result for known job type
                job_type_detection = JobTypeDetection(
                    detected_job_type=job_type,
                    confidence=1.0,
                    detection_source_text=user_message,
                    detection_offsets=(0, len(user_message)),
                    detection_method="provided"
                )

            if not job_type:
                return await self._handle_no_job_type_detected(user_message)

            # 2. Load schema for job type
            schema = self.schemas.get(job_type)
            if not schema:
                logger.warning(f"No schema found for job type: {job_type}")
                return await self._handle_unknown_job_type(user_message, job_type)

            # 3. Parameter Extraction mit LangExtract
            extraction_result = await self._extract_parameters_langextract(
                user_message=user_message,
                schema=schema,
                existing_stream_params=existing_stream_params or {},
                existing_job_params=existing_job_params or {}
            )

            # 4. Result Assembly
            result = SourceGroundedExtractionResult(
                job_type_detection=job_type_detection,
                stream_parameters=extraction_result.get("stream_parameters", []),
                job_parameters=extraction_result.get("job_parameters", []),
                full_text=user_message,
                highlighted_ranges=extraction_result.get("highlighted_ranges", []),
                completion_percentage=extraction_result.get("completion_percentage", 0.0),
                missing_stream_parameters=extraction_result.get("missing_stream_parameters", []),
                missing_job_parameters=extraction_result.get("missing_job_parameters", []),
                next_required_parameter=extraction_result.get("next_required_parameter"),
                suggested_questions=extraction_result.get("suggested_questions", []),
                overall_confidence=extraction_result.get("overall_confidence", 0.0),
                extraction_quality=extraction_result.get("extraction_quality", "medium"),
                extraction_metadata={
                    "extraction_method": "langextract",
                    "job_type": job_type,
                    "schema_version": schema.schema_version,
                    "duration": (datetime.now() - start_time).total_seconds()
                }
            )

            # 5. Quality Assessment & Metrics
            await self._assess_extraction_quality(result)
            await self._record_metrics(result, start_time)

            logger.info(f"✅ Extraction completed: {len(result.stream_parameters + result.job_parameters)} parameters")
            return result

        except Exception as e:
            logger.error(f"❌ LangExtract extraction failed: {e}")
            return await self._handle_extraction_error(user_message, str(e))

    async def _detect_job_type_with_grounding(self, user_message: str) -> JobTypeDetection:
        """Enhanced Job-Type Detection mit Source Grounding"""

        logger.info("🔍 Detecting job type with source grounding...")

        # Prepare job type detection prompt for LangExtract
        job_types_info = []
        for job_type, schema in self.schemas.items():
            keywords = schema.detection_config.get("keywords", [])
            patterns = schema.detection_config.get("patterns", [])

            job_types_info.append({
                "job_type": job_type,
                "display_name": schema.schema_name,
                "description": getattr(schema, 'description', f"{job_type} stream configuration"),
                "keywords": keywords[:5],  # Top 5 keywords
                "patterns": patterns[:3]   # Top 3 patterns
            })

        # LangExtract job type detection
        try:
            result = await lx.extract(
                text=user_message,
                prompt_description=self._build_job_type_detection_prompt(),
                examples=self._get_job_type_examples(),
                model_id=self.config.model_id,
                api_key=self.config.api_key,
                fence_output=self.config.fence_output,
                use_schema_constraints=self.config.use_schema_constraints,
                enable_source_grounding=True
            )

            return self._parse_job_type_result(result, user_message)

        except Exception as e:
            logger.warning(f"LangExtract job type detection failed: {e}")
            return await self._fallback_job_type_detection(user_message)

    async def _extract_parameters_langextract(
        self,
        user_message: str,
        schema: StreamWorksSchema,
        existing_stream_params: Dict[str, Any],
        existing_job_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Core LangExtract Parameter Extraction"""

        logger.info(f"🎯 Extracting parameters for {schema.job_type} using LangExtract...")

        # Build extraction prompt
        extraction_prompt = self._build_parameter_extraction_prompt(
            schema,
            existing_stream_params,
            existing_job_params
        )

        # Get few-shot examples for this job type
        examples = schema.few_shot_examples

        try:
            # LangExtract API Call
            result = await lx.extract(
                text=user_message,
                prompt_description=extraction_prompt,
                examples=examples,
                model_id=self.config.model_id,
                api_key=self.config.api_key,
                fence_output=self.config.fence_output,
                use_schema_constraints=self.config.use_schema_constraints,
                enable_source_grounding=True
            )

            # Parse LangExtract result
            return await self._parse_extraction_result(result, schema, user_message)

        except Exception as e:
            logger.error(f"LangExtract parameter extraction failed: {e}")
            raise

    def _build_job_type_detection_prompt(self) -> str:
        """Build prompt for job type detection"""
        return """
        Identify the type of StreamWorks stream configuration from the user message.

        Available stream types:
        - FILE_TRANSFER: Data transfer between servers, file copying, synchronization
        - SAP: SAP system integration, data export/import, table operations
        - STANDARD: General process automation, standard job processing

        Return the most likely stream type based on keywords and context.
        """

    def _build_parameter_extraction_prompt(
        self,
        schema: StreamWorksSchema,
        existing_stream_params: Dict[str, Any],
        existing_job_params: Dict[str, Any]
    ) -> str:
        """Build parameter extraction prompt for specific job type"""

        # Stream parameters description
        stream_params_desc = []
        for param in schema.stream_parameters:
            stream_params_desc.append(
                f"- {param['name']} ({param['data_type']}): {param['description']}"
            )

        # Job parameters description
        job_params_desc = []
        for param in schema.job_parameters:
            job_params_desc.append(
                f"- {param['name']} ({param['data_type']}): {param['description']}"
            )

        prompt = f"""
        Extract {schema.job_type} stream configuration parameters from the user message.

        STREAM PARAMETERS (common to all streams):
        {chr(10).join(stream_params_desc)}

        JOB-SPECIFIC PARAMETERS ({schema.job_type}):
        {chr(10).join(job_params_desc)}

        EXISTING PARAMETERS:
        Stream: {json.dumps(existing_stream_params, indent=2)}
        Job: {json.dumps(existing_job_params, indent=2)}

        Extract all parameters mentioned in the message and provide source grounding.
        """

        return prompt

    def _get_job_type_examples(self) -> List[Dict[str, Any]]:
        """Get few-shot examples for job type detection"""
        return [
            {
                "input": "Ich brauche einen Datentransfer von Server001 nach Server002",
                "output": {"job_type": "FILE_TRANSFER", "confidence": 0.95}
            },
            {
                "input": "SAP Kalender Export von System ZTV",
                "output": {"job_type": "SAP", "confidence": 0.92}
            },
            {
                "input": "Standard Prozess für Datenverarbeitung",
                "output": {"job_type": "STANDARD", "confidence": 0.85}
            }
        ]

    async def _parse_extraction_result(
        self,
        langextract_result: Any,
        schema: StreamWorksSchema,
        original_text: str
    ) -> Dict[str, Any]:
        """Parse LangExtract result into our format"""

        logger.info("📊 Parsing LangExtract result...")

        # Extract parameters from LangExtract result
        stream_parameters = []
        job_parameters = []
        highlighted_ranges = []

        # Note: This depends on LangExtract's actual result format
        # We'll need to adapt this based on the real API response

        if hasattr(langextract_result, 'entities'):
            for entity in langextract_result.entities:
                # Create SourceGroundedParameter
                param = SourceGroundedParameter(
                    name=entity.get('name', ''),
                    value=entity.get('value', ''),
                    confidence=entity.get('confidence', 0.0),
                    source_text=entity.get('source_text', ''),
                    character_offsets=(
                        entity.get('start_offset', 0),
                        entity.get('end_offset', 0)
                    ),
                    extraction_confidence=entity.get('extraction_confidence', 0.0),
                    scope=self._determine_parameter_scope(entity.get('name', ''), schema),
                    extraction_method="langextract"
                )

                if param.scope == "stream":
                    stream_parameters.append(param)
                else:
                    job_parameters.append(param)

                # Add to highlighted ranges
                highlighted_ranges.append((
                    param.character_offsets[0],
                    param.character_offsets[1],
                    param.name
                ))

        # Calculate completion and missing parameters
        completion_data = self._calculate_completion_status(
            stream_parameters, job_parameters, schema
        )

        return {
            "stream_parameters": stream_parameters,
            "job_parameters": job_parameters,
            "highlighted_ranges": merge_overlapping_ranges(highlighted_ranges),
            "completion_percentage": completion_data["completion_percentage"],
            "missing_stream_parameters": completion_data["missing_stream"],
            "missing_job_parameters": completion_data["missing_job"],
            "next_required_parameter": completion_data["next_required"],
            "suggested_questions": await self._generate_smart_questions(completion_data),
            "overall_confidence": self._calculate_overall_confidence(stream_parameters + job_parameters),
            "extraction_quality": self._assess_quality(stream_parameters + job_parameters)
        }

    def _determine_parameter_scope(self, param_name: str, schema: StreamWorksSchema) -> str:
        """Determine if parameter is stream or job scope"""
        stream_param_names = [p['name'] for p in schema.stream_parameters]
        if param_name in stream_param_names:
            return "stream"
        return "job"

    def _calculate_completion_status(
        self,
        stream_params: List[SourceGroundedParameter],
        job_params: List[SourceGroundedParameter],
        schema: StreamWorksSchema
    ) -> Dict[str, Any]:
        """Calculate completion percentage and missing parameters"""

        # Get required parameters
        required_stream = [p['name'] for p in schema.stream_parameters if p.get('required', False)]
        required_job = [p['name'] for p in schema.job_parameters if p.get('required', False)]

        # Get extracted parameter names
        extracted_stream = [p.name for p in stream_params]
        extracted_job = [p.name for p in job_params]

        # Calculate missing
        missing_stream = [name for name in required_stream if name not in extracted_stream]
        missing_job = [name for name in required_job if name not in extracted_job]

        # Calculate completion percentage
        total_required = len(required_stream) + len(required_job)
        total_extracted = len(extracted_stream) + len(extracted_job)
        completion_percentage = (total_extracted / max(total_required, 1)) * 100

        # Next required parameter
        next_required = None
        if missing_stream:
            next_required = missing_stream[0]
        elif missing_job:
            next_required = missing_job[0]

        return {
            "completion_percentage": min(completion_percentage, 100.0),
            "missing_stream": missing_stream,
            "missing_job": missing_job,
            "next_required": next_required
        }

    def _calculate_overall_confidence(self, parameters: List[SourceGroundedParameter]) -> float:
        """Calculate overall confidence from all parameters"""
        if not parameters:
            return 0.0

        confidences = [p.confidence for p in parameters]
        return sum(confidences) / len(confidences)

    def _assess_quality(self, parameters: List[SourceGroundedParameter]) -> str:
        """Assess extraction quality"""
        if not parameters:
            return "needs_review"

        avg_confidence = self._calculate_overall_confidence(parameters)

        if avg_confidence >= 0.85:
            return "high"
        elif avg_confidence >= 0.65:
            return "medium"
        elif avg_confidence >= 0.45:
            return "low"
        else:
            return "needs_review"

    async def _generate_smart_questions(self, completion_data: Dict[str, Any]) -> List[str]:
        """Generate smart follow-up questions"""
        questions = []

        missing_stream = completion_data.get("missing_stream", [])
        missing_job = completion_data.get("missing_job", [])

        if missing_stream:
            questions.append(f"Wie soll der {missing_stream[0]} konfiguriert werden?")

        if missing_job:
            questions.append(f"Bitte spezifizieren Sie {missing_job[0]}.")

        if not missing_stream and not missing_job:
            questions.append("Soll ich die XML-Konfiguration jetzt generieren?")

        return questions[:3]  # Maximal 3 Fragen

    async def _assess_extraction_quality(self, result: SourceGroundedExtractionResult):
        """Assess and enhance extraction quality"""

        # Calculate highlight coverage
        if result.highlighted_ranges:
            coverage = calculate_highlight_coverage(result.full_text, result.highlighted_ranges)
            result.extraction_metadata["highlight_coverage"] = coverage

        # Validate character offsets
        for param in result.stream_parameters + result.job_parameters:
            if not validate_character_offsets(result.full_text, param.character_offsets):
                logger.warning(f"Invalid character offsets for parameter {param.name}")
                result.warnings.append(f"Invalid source grounding for {param.name}")

    async def _record_metrics(self, result: SourceGroundedExtractionResult, start_time: datetime):
        """Record performance metrics"""

        duration = (datetime.now() - start_time).total_seconds()

        metrics = ExtractionMetrics(
            extraction_duration=duration,
            api_call_duration=result.extraction_metadata.get("api_duration", 0.0),
            parameters_extracted=len(result.stream_parameters + result.job_parameters),
            parameters_with_high_confidence=len([
                p for p in result.stream_parameters + result.job_parameters
                if p.confidence >= 0.85
            ]),
            parameters_needing_review=len([
                p for p in result.stream_parameters + result.job_parameters
                if p.confidence < 0.65
            ]),
            job_type=result.job_type_detection.detected_job_type
        )

        await self.metrics_collector.record_metrics(metrics)

    # Error Handling Methods

    async def _handle_no_job_type_detected(self, user_message: str) -> SourceGroundedExtractionResult:
        """Handle case when no job type could be detected"""
        return SourceGroundedExtractionResult(
            job_type_detection=JobTypeDetection(
                detected_job_type="UNKNOWN",
                confidence=0.0,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message))
            ),
            full_text=user_message,
            suggested_questions=[
                "Welchen Stream-Typ möchten Sie konfigurieren?",
                "Handelt es sich um einen File Transfer, SAP-Job oder Standard-Prozess?",
                "Können Sie den gewünschten Stream genauer beschreiben?"
            ],
            extraction_errors=["Could not detect job type from user message"]
        )

    async def _handle_unknown_job_type(self, user_message: str, job_type: str) -> SourceGroundedExtractionResult:
        """Handle unknown job type"""
        return SourceGroundedExtractionResult(
            job_type_detection=JobTypeDetection(
                detected_job_type=job_type,
                confidence=0.5,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message))
            ),
            full_text=user_message,
            suggested_questions=[f"Schema für {job_type} ist nicht verfügbar. Bitte verwenden Sie FILE_TRANSFER, SAP oder STANDARD."],
            extraction_errors=[f"No schema available for job type: {job_type}"]
        )

    async def _handle_extraction_error(self, user_message: str, error: str) -> SourceGroundedExtractionResult:
        """Handle extraction errors gracefully"""
        return SourceGroundedExtractionResult(
            job_type_detection=JobTypeDetection(
                detected_job_type="ERROR",
                confidence=0.0,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message))
            ),
            full_text=user_message,
            suggested_questions=["Entschuldigung, es gab einen Fehler. Können Sie Ihre Anfrage anders formulieren?"],
            extraction_errors=[f"Extraction failed: {error}"]
        )

    async def _fallback_job_type_detection(self, user_message: str) -> JobTypeDetection:
        """Fallback job type detection using keywords"""

        message_lower = user_message.lower()

        # Simple keyword-based detection as fallback
        if any(keyword in message_lower for keyword in ["transfer", "datei", "copy", "sync"]):
            return JobTypeDetection(
                detected_job_type="FILE_TRANSFER",
                confidence=0.6,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message)),
                detection_method="keywords"
            )
        elif any(keyword in message_lower for keyword in ["sap", "export", "import", "tabelle"]):
            return JobTypeDetection(
                detected_job_type="SAP",
                confidence=0.6,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message)),
                detection_method="keywords"
            )
        else:
            return JobTypeDetection(
                detected_job_type="STANDARD",
                confidence=0.4,
                detection_source_text=user_message,
                detection_offsets=(0, len(user_message)),
                detection_method="keywords"
            )


class StreamWorksSchemaLoader:
    """Lädt und konvertiert StreamWorks Schemas für LangExtract"""

    def __init__(self, schema_path: Optional[str] = None):
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            self.schema_path = Path(__file__).parent.parent.parent / "templates" / "unified_stream_schemas.json"

    def load_all_schemas(self) -> Dict[str, StreamWorksSchema]:
        """Load all StreamWorks schemas"""

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            schemas = {}
            job_type_schemas = data.get('job_type_schemas', {})
            common_stream_params = data.get('common_stream_parameters', [])

            for job_type, schema_data in job_type_schemas.items():
                schemas[job_type] = StreamWorksSchema(
                    schema_name=schema_data.get('display_name', job_type),
                    schema_version=data.get('version', '2.0'),
                    job_type=job_type,
                    stream_parameters=common_stream_params,
                    job_parameters=schema_data.get('job_parameters', []),
                    few_shot_examples=self._generate_few_shot_examples(job_type, schema_data),
                    detection_config=schema_data.get('detection_config', {}),
                    required_parameters=self._extract_required_parameters(
                        common_stream_params,
                        schema_data.get('job_parameters', [])
                    )
                )

            logger.info(f"Loaded {len(schemas)} StreamWorks schemas")
            return schemas

        except Exception as e:
            logger.error(f"Failed to load schemas: {e}")
            return {}

    def _generate_few_shot_examples(self, job_type: str, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate few-shot examples for LangExtract"""

        # This would be populated with real examples for each job type
        examples_map = {
            "FILE_TRANSFER": [
                {
                    "input": "Datentransfer von Server001 nach Server002 für CSV Dateien",
                    "output": {
                        "SourceServer": "Server001",
                        "TargetServer": "Server002",
                        "FilePattern": "*.csv"
                    }
                }
            ],
            "SAP": [
                {
                    "input": "SAP Export von System ZTV Tabelle PA1 als Excel",
                    "output": {
                        "SAPSystem": "ZTV",
                        "TableName": "PA1",
                        "ExportFormat": "Excel"
                    }
                }
            ],
            "STANDARD": [
                {
                    "input": "Standard Prozess für Datenverarbeitung täglich um 6 Uhr",
                    "output": {
                        "ProcessType": "DataProcessing",
                        "Schedule": "daily_6am"
                    }
                }
            ]
        }

        return examples_map.get(job_type, [])

    def _extract_required_parameters(self, stream_params: List[Dict], job_params: List[Dict]) -> List[str]:
        """Extract required parameter names"""
        required = []

        for param in stream_params:
            if param.get('required', False):
                required.append(param['name'])

        for param in job_params:
            if param.get('required', False):
                required.append(param['name'])

        return required


class ExtractionMetricsCollector:
    """Sammelt und verwaltet Performance-Metriken"""

    def __init__(self):
        self.metrics: List[ExtractionMetrics] = []

    async def record_metrics(self, metrics: ExtractionMetrics):
        """Record extraction metrics"""
        self.metrics.append(metrics)

        # Log key metrics
        logger.info(f"📊 Extraction Metrics: "
                   f"Duration={metrics.extraction_duration:.2f}s, "
                   f"Parameters={metrics.parameters_extracted}, "
                   f"HighConf={metrics.parameters_with_high_confidence}")

    def get_recent_metrics(self, limit: int = 10) -> List[ExtractionMetrics]:
        """Get recent metrics"""
        return self.metrics[-limit:]

    def calculate_average_performance(self) -> Dict[str, float]:
        """Calculate average performance metrics"""
        if not self.metrics:
            return {}

        total_metrics = len(self.metrics)

        return {
            "avg_duration": sum(m.extraction_duration for m in self.metrics) / total_metrics,
            "avg_parameters_extracted": sum(m.parameters_extracted for m in self.metrics) / total_metrics,
            "success_rate": sum(1 for m in self.metrics if m.extraction_errors == 0) / total_metrics
        }


# Factory Functions

_langextract_service_instance: Optional[LangExtractParameterService] = None

def get_langextract_parameter_service(config: Optional[LangExtractConfig] = None) -> LangExtractParameterService:
    """Factory function für LangExtractParameterService"""
    global _langextract_service_instance

    if _langextract_service_instance is None:
        _langextract_service_instance = LangExtractParameterService(config)

    return _langextract_service_instance


async def quick_extract_test(message: str) -> SourceGroundedExtractionResult:
    """Quick test function für LangExtract"""
    service = get_langextract_parameter_service()
    return await service.extract_parameters_with_grounding(message)