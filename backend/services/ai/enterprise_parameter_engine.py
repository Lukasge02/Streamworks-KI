"""
Enterprise Parameter Engine - Main AI Engine for Parameter Recognition
Coordinates all AI components for intelligent stream parameter extraction
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from collections import Counter

from .supabase_stream_loader import get_supabase_stream_loader
from .stream_schema_vector_store import get_stream_schema_vector_store
from .parameter_pattern_store import get_parameter_pattern_store
from .conversation_memory_store import get_conversation_memory_store
from .chroma_manager import get_chroma_manager

logger = logging.getLogger(__name__)

@dataclass
class ParameterExtractionRequest:
    """Request for parameter extraction"""
    session_id: str
    user_message: str
    conversation_context: List[Dict[str, Any]]
    current_parameters: Dict[str, Any]
    conversation_phase: str
    user_id: str = "default"

@dataclass
class ParameterExtractionResult:
    """Result of parameter extraction"""
    extracted_parameters: Dict[str, Any]
    confidence_scores: Dict[str, float]
    suggested_job_type: str
    missing_parameters: List[str]
    validation_errors: List[Dict[str, Any]]
    next_questions: List[str]
    conversation_phase: str
    completion_percentage: float
    ai_response: str

@dataclass
class AIEngineStats:
    """Statistics for the AI engine"""
    total_extractions: int
    successful_extractions: int
    average_confidence: float
    learned_patterns: int
    conversation_sessions: int
    schema_matches: int

class EnterpriseParameterEngine:
    """
    Main AI engine that coordinates all components for intelligent parameter extraction

    Features:
    - Multi-model consensus for parameter extraction
    - Schema-based job type detection
    - Context-aware conversation management
    - Self-learning from successful interactions
    - Enterprise-grade accuracy and reliability
    """

    def __init__(self):
        # Initialize all AI components
        self.stream_loader = get_supabase_stream_loader()
        self.schema_store = get_stream_schema_vector_store()
        self.pattern_store = get_parameter_pattern_store()
        self.conversation_store = get_conversation_memory_store()
        self.chroma_manager = get_chroma_manager()

        # Engine statistics
        self.stats = AIEngineStats(
            total_extractions=0,
            successful_extractions=0,
            average_confidence=0.0,
            learned_patterns=0,
            conversation_sessions=0,
            schema_matches=0
        )

        # Configuration
        self.min_confidence_threshold = 0.7
        self.consensus_threshold = 0.6
        self.max_extraction_methods = 3

        # Job type detection patterns
        self.job_type_indicators = {
            'sap': ['sap', 'system', 'report', 'programm', 'transaktion'],
            'file_transfer': ['datei', 'file', 'kopieren', 'übertragen', 'pfad', 'path'],
            'standard': ['script', 'batch', 'ausführen', 'agent', 'server'],
            'custom': ['custom', 'spezial', 'individuell']
        }

    async def initialize_engine(self) -> bool:
        """
        Initialize the AI engine and learn from existing data

        Returns:
            True if initialization successful
        """
        try:
            logger.info("🚀 Initializing Enterprise Parameter Engine...")

            # Migrate ChromaDB structure
            self.chroma_manager.migrate_existing_data()

            # Load existing stream data for learning
            streams = await self.stream_loader.get_all_streams()
            logger.info(f"📊 Loaded {len(streams)} existing streams for analysis")

            if streams:
                # Learn schemas from existing streams
                learned_schemas = await self.schema_store.learn_from_stream_data(streams)
                logger.info(f"🧠 Learned {len(learned_schemas)} stream schemas")

                # Generate training data
                training_data = await self.stream_loader.generate_ai_training_data()
                if training_data:
                    logger.info(f"📚 Generated training data with {len(training_data.get('training_examples', []))} examples")

            # Perform health check
            health_status = self.chroma_manager.health_check()
            if health_status["status"] != "healthy":
                logger.warning(f"⚠️ ChromaDB health check: {health_status['status']}")

            logger.info("✅ Enterprise Parameter Engine initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing AI engine: {str(e)}")
            return False

    async def extract_parameters(self, request: ParameterExtractionRequest) -> ParameterExtractionResult:
        """
        Main parameter extraction method using multi-model consensus

        Args:
            request: Parameter extraction request

        Returns:
            Comprehensive extraction result
        """
        try:
            logger.info(f"🎯 Processing parameter extraction for session {request.session_id}")
            self.stats.total_extractions += 1

            # Phase 1: Pattern-based parameter extraction
            pattern_results = await self.pattern_store.extract_parameters(
                request.user_message,
                {"conversation_phase": request.conversation_phase}
            )

            # Phase 2: Schema-based suggestions
            schema_suggestions = await self.schema_store.get_schema_suggestions(
                request.current_parameters,
                request.user_message
            )

            # Phase 3: Conversation context analysis
            conversation_context = await self.conversation_store.get_conversation_context(
                request.session_id
            )

            # Phase 4: Job type detection
            detected_job_type = await self._detect_job_type(
                request.user_message,
                request.current_parameters,
                pattern_results,
                schema_suggestions
            )

            # Phase 5: Multi-model consensus
            consensus_result = await self._achieve_consensus(
                request,
                pattern_results,
                schema_suggestions,
                detected_job_type
            )

            # Phase 6: Validation and completion assessment
            validation_result = await self._validate_and_assess(
                consensus_result,
                detected_job_type,
                request.current_parameters
            )

            # Phase 7: Generate AI response and next questions
            ai_response, next_questions = await self._generate_response(
                request,
                validation_result,
                conversation_context
            )

            # Create final result
            result = ParameterExtractionResult(
                extracted_parameters=consensus_result["parameters"],
                confidence_scores=consensus_result["confidence_scores"],
                suggested_job_type=detected_job_type,
                missing_parameters=validation_result["missing_parameters"],
                validation_errors=validation_result["validation_errors"],
                next_questions=next_questions,
                conversation_phase=self._determine_next_phase(validation_result),
                completion_percentage=validation_result["completion_percentage"],
                ai_response=ai_response
            )

            # Update statistics
            if result.completion_percentage >= 0.8:
                self.stats.successful_extractions += 1

            # Add conversation turn to memory
            await self.conversation_store.add_conversation_turn(
                session_id=request.session_id,
                user_message=request.user_message,
                ai_response=ai_response,
                extracted_parameters=consensus_result["parameters"],
                conversation_phase=request.conversation_phase,
                success_score=min(1.0, result.completion_percentage + 0.2)
            )

            logger.info(f"✅ Parameter extraction completed: {len(result.extracted_parameters)} params, {result.completion_percentage:.1%} complete")
            return result

        except Exception as e:
            logger.error(f"❌ Error in parameter extraction: {str(e)}")
            # Return error result
            return ParameterExtractionResult(
                extracted_parameters={},
                confidence_scores={},
                suggested_job_type="unknown",
                missing_parameters=[],
                validation_errors=[{"type": "extraction_error", "field": "", "message": str(e)}],
                next_questions=["Entschuldigung, es gab ein Problem. Können Sie Ihre Anfrage wiederholen?"],
                conversation_phase=request.conversation_phase,
                completion_percentage=0.0,
                ai_response="Es tut mir leid, aber ich konnte Ihre Anfrage nicht vollständig verarbeiten. Bitte versuchen Sie es erneut."
            )

    async def learn_from_successful_stream(self, stream_data: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        """
        Learn from a successfully created stream

        Args:
            stream_data: Data of the successfully created stream
            conversation_history: Complete conversation that led to the stream
        """
        try:
            logger.info(f"🧠 Learning from successful stream creation: {stream_data.get('stream_name', 'Unknown')}")

            # Extract final parameters
            wizard_data = stream_data.get('wizard_data', {})
            extracted_params = {}

            for section, params in wizard_data.items():
                if isinstance(params, dict):
                    for key, value in params.items():
                        if value:
                            extracted_params[f"{section}.{key}"] = value

            # Learn parameter patterns from each conversation turn
            for turn in conversation_history:
                user_message = turn.get('user_message', '')
                if user_message and extracted_params:
                    await self.pattern_store.learn_from_successful_extraction(
                        text=user_message,
                        extracted_params=extracted_params,
                        context={"job_type": stream_data.get('job_type')}
                    )

            # Update schema usage statistics
            schema_suggestions = await self.schema_store.get_schema_suggestions(wizard_data)
            if schema_suggestions.get('schema_id'):
                await self.schema_store.update_schema_usage(
                    schema_suggestions['schema_id'],
                    success=True
                )

            logger.info("✅ Successfully learned from stream creation")

        except Exception as e:
            logger.error(f"❌ Error learning from successful stream: {str(e)}")

    async def _detect_job_type(
        self,
        user_message: str,
        current_parameters: Dict[str, Any],
        pattern_results: List[Any],
        schema_suggestions: Dict[str, Any]
    ) -> str:
        """Detect job type using multiple signals"""
        try:
            job_type_scores = Counter()

            # Check schema suggestions first (highest priority)
            if schema_suggestions.get('job_type'):
                job_type_scores[schema_suggestions['job_type']] += 0.4

            # Check current parameters
            job_form = current_parameters.get('jobForm', {})
            if job_form.get('sapSystem') or job_form.get('reportName'):
                job_type_scores['sap'] += 0.3
            elif job_form.get('sourcePath') or job_form.get('targetPath'):
                job_type_scores['file_transfer'] += 0.3
            elif job_form.get('scriptPath') or job_form.get('agentName'):
                job_type_scores['standard'] += 0.3

            # Check pattern results
            for result in pattern_results:
                param_name = result.parameter_name
                if param_name in ['sap_system', 'report_name']:
                    job_type_scores['sap'] += 0.1
                elif param_name == 'file_path':
                    job_type_scores['file_transfer'] += 0.1
                elif param_name == 'agent_name':
                    job_type_scores['standard'] += 0.1

            # Check message content for indicators
            message_lower = user_message.lower()
            for job_type, indicators in self.job_type_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        job_type_scores[job_type] += 0.05

            # Return highest scoring job type
            if job_type_scores:
                return job_type_scores.most_common(1)[0][0]

            return "unknown"

        except Exception as e:
            logger.error(f"Error detecting job type: {str(e)}")
            return "unknown"

    async def _achieve_consensus(
        self,
        request: ParameterExtractionRequest,
        pattern_results: List[Any],
        schema_suggestions: Dict[str, Any],
        job_type: str
    ) -> Dict[str, Any]:
        """Achieve consensus between different extraction methods"""
        try:
            consensus_params = {}
            confidence_scores = {}

            # Process pattern-based results
            for result in pattern_results:
                param_name = result.parameter_name
                param_value = result.extracted_value
                confidence = result.confidence

                if confidence >= self.min_confidence_threshold:
                    if param_name not in consensus_params:
                        consensus_params[param_name] = param_value
                        confidence_scores[param_name] = confidence
                    else:
                        # Multiple extractions for same parameter - use highest confidence
                        if confidence > confidence_scores[param_name]:
                            consensus_params[param_name] = param_value
                            confidence_scores[param_name] = confidence

            # Process schema-based suggestions
            for suggestion in schema_suggestions.get('suggestions', []):
                field = suggestion['field']
                if field not in consensus_params and suggestion['type'] == 'required':
                    # Add as missing parameter that needs to be asked for
                    confidence_scores[f"missing_{field}"] = 0.8

            # Merge with existing parameters
            existing_params = request.current_parameters
            for section, params in existing_params.items():
                if isinstance(params, dict):
                    for key, value in params.items():
                        param_path = f"{section}.{key}"
                        if value and param_path not in consensus_params:
                            consensus_params[param_path] = value
                            confidence_scores[param_path] = 0.9  # High confidence for existing data

            return {
                "parameters": consensus_params,
                "confidence_scores": confidence_scores
            }

        except Exception as e:
            logger.error(f"Error achieving consensus: {str(e)}")
            return {"parameters": {}, "confidence_scores": {}}

    async def _validate_and_assess(
        self,
        consensus_result: Dict[str, Any],
        job_type: str,
        current_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate extracted parameters and assess completion"""
        try:
            parameters = consensus_result["parameters"]
            confidence_scores = consensus_result["confidence_scores"]

            # Get required fields for job type
            required_fields = await self._get_required_fields_for_job_type(job_type)

            # Check missing parameters
            missing_parameters = []
            validation_errors = []

            for field in required_fields:
                if field not in parameters:
                    missing_parameters.append(field)

            # Validate existing parameters
            for param_name, param_value in parameters.items():
                if param_name.startswith("missing_"):
                    continue

                validation_error = await self._validate_parameter(param_name, param_value)
                if validation_error:
                    validation_errors.append(validation_error)

            # Calculate completion percentage
            total_required = len(required_fields)
            completed_required = sum(1 for field in required_fields if field in parameters)

            if total_required > 0:
                completion_percentage = completed_required / total_required
            else:
                completion_percentage = 0.8 if parameters else 0.0

            # Adjust for confidence scores
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
            completion_percentage = completion_percentage * avg_confidence

            return {
                "missing_parameters": missing_parameters,
                "validation_errors": validation_errors,
                "completion_percentage": completion_percentage,
                "required_fields": required_fields
            }

        except Exception as e:
            logger.error(f"Error in validation and assessment: {str(e)}")
            return {
                "missing_parameters": [],
                "validation_errors": [],
                "completion_percentage": 0.0,
                "required_fields": []
            }

    async def _get_required_fields_for_job_type(self, job_type: str) -> List[str]:
        """Get required fields for a specific job type"""
        field_mappings = {
            'sap': [
                'jobForm.sapSystem',
                'jobForm.reportName',
                'streamProperties.streamName',
                'scheduling.frequency'
            ],
            'file_transfer': [
                'jobForm.sourcePath',
                'jobForm.targetPath',
                'streamProperties.streamName',
                'scheduling.frequency'
            ],
            'standard': [
                'jobForm.scriptPath',
                'jobForm.agentName',
                'streamProperties.streamName',
                'scheduling.frequency'
            ]
        }

        return field_mappings.get(job_type, [
            'streamProperties.streamName',
            'scheduling.frequency'
        ])

    async def _validate_parameter(self, param_name: str, param_value: Any) -> Optional[Dict[str, Any]]:
        """Validate a single parameter"""
        try:
            param_str = str(param_value).strip()

            # SAP System validation
            if 'sapSystem' in param_name:
                import re
                if not re.match(r'^[A-Z]\d{2}$', param_str):
                    return {
                        "type": "format_error",
                        "field": param_name,
                        "message": "SAP System muss im Format 'X00' sein (z.B. P01, D02)",
                        "suggestions": ["P01", "D02", "S01"]
                    }

            # Report name validation
            elif 'reportName' in param_name:
                if not param_str.startswith(('Z', 'Y')):
                    return {
                        "type": "format_error",
                        "field": param_name,
                        "message": "SAP Report Namen müssen mit Z oder Y beginnen",
                        "suggestions": [f"Z{param_str}", f"Y{param_str}"]
                    }

            # Time validation
            elif 'time' in param_name.lower():
                import re
                if not re.match(r'^\d{1,2}:\d{2}$', param_str):
                    return {
                        "type": "format_error",
                        "field": param_name,
                        "message": "Zeit muss im Format HH:MM sein",
                        "suggestions": ["08:00", "14:30", "20:00"]
                    }

            return None

        except Exception as e:
            logger.error(f"Error validating parameter {param_name}: {str(e)}")
            return None

    async def _generate_response(
        self,
        request: ParameterExtractionRequest,
        validation_result: Dict[str, Any],
        conversation_context: List[Any]
    ) -> Tuple[str, List[str]]:
        """Generate AI response and next questions"""
        try:
            missing_params = validation_result["missing_parameters"]
            validation_errors = validation_result["validation_errors"]
            completion_percentage = validation_result["completion_percentage"]

            # Generate response based on current state
            if validation_errors:
                # Handle validation errors first
                error = validation_errors[0]
                response = f"Es gibt ein Problem mit dem Feld '{error['field']}': {error['message']}"
                if error.get('suggestions'):
                    response += f" Vorschläge: {', '.join(error['suggestions'][:3])}"

                next_questions = [f"Können Sie {error['field']} korrigieren?"]

            elif missing_params:
                # Ask for missing parameters
                next_param = missing_params[0]
                field_name = next_param.split('.')[-1]

                response_templates = {
                    'sapSystem': "Für welches SAP System soll der Job konfiguriert werden? (z.B. P01, D02)",
                    'reportName': "Wie heißt der SAP Report, der ausgeführt werden soll? (z.B. Z_DAILY_SALES)",
                    'sourcePath': "Wo befindet sich die Quelldatei? (z.B. C:\\Data\\input.txt)",
                    'targetPath': "Wohin soll die Datei kopiert werden? (z.B. \\\\server\\share\\output.txt)",
                    'scriptPath': "Welches Script soll ausgeführt werden? (z.B. C:\\Scripts\\backup.bat)",
                    'agentName': "Auf welchem Agent soll der Job ausgeführt werden? (z.B. AGENT01)",
                    'streamName': "Wie soll der Stream heißen?",
                    'frequency': "Wie oft soll der Job ausgeführt werden? (täglich, wöchentlich, monatlich)"
                }

                response = response_templates.get(field_name, f"Bitte geben Sie {field_name} an.")
                next_questions = [response]

            elif completion_percentage >= 0.8:
                # Nearly complete or complete
                response = f"Sehr gut! Ihre Stream-Konfiguration ist zu {completion_percentage:.0%} vollständig. Soll ich den XML Stream jetzt erstellen?"
                next_questions = ["Stream erstellen", "Noch einmal überprüfen", "Änderungen vornehmen"]

            else:
                # General progress update
                response = f"Die Konfiguration ist zu {completion_percentage:.0%} vollständig. Was möchten Sie als nächstes konfigurieren?"
                next_questions = [
                    "Zeitplan festlegen",
                    "Weitere Parameter hinzufügen",
                    "Aktuellen Stand überprüfen"
                ]

            # Get suggestions from conversation memory
            memory_suggestions = await self.conversation_store.suggest_next_response(
                request.session_id,
                request.conversation_phase,
                request.user_message
            )

            if memory_suggestions.get("recommended_responses"):
                # Blend AI-generated response with memory suggestions
                recommended = memory_suggestions["recommended_responses"][0]
                if recommended.get("success_score", 0) > 0.8:
                    # Use high-confidence memory response
                    response = recommended["response"]

            return response, next_questions

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Wie kann ich Ihnen bei der Stream-Konfiguration helfen?", ["Neuen Stream erstellen"]

    def _determine_next_phase(self, validation_result: Dict[str, Any]) -> str:
        """Determine the next conversation phase"""
        completion_percentage = validation_result["completion_percentage"]
        missing_params = validation_result["missing_parameters"]
        validation_errors = validation_result["validation_errors"]

        if validation_errors:
            return "validation"
        elif missing_params:
            # Determine phase based on missing parameter types
            for param in missing_params:
                if 'jobForm' in param:
                    return "job_configuration"
                elif 'streamProperties' in param:
                    return "stream_properties"
                elif 'scheduling' in param:
                    return "scheduling"
            return "job_configuration"
        elif completion_percentage >= 0.8:
            return "creation"
        else:
            return "job_configuration"

    def get_engine_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        try:
            # Get stats from all components
            chroma_health = self.chroma_manager.health_check()
            schema_stats = self.schema_store.get_stats()
            pattern_stats = self.pattern_store.get_stats()
            conversation_stats = self.conversation_store.get_stats()

            # Update engine stats
            if self.stats.total_extractions > 0:
                self.stats.average_confidence = (
                    self.stats.successful_extractions / self.stats.total_extractions
                )

            return {
                "engine": asdict(self.stats),
                "chroma_health": chroma_health,
                "components": {
                    "schema_store": schema_stats,
                    "pattern_store": pattern_stats,
                    "conversation_store": conversation_stats
                }
            }

        except Exception as e:
            logger.error(f"Error getting engine stats: {str(e)}")
            return {"error": str(e)}

# Global instance
_enterprise_parameter_engine = None

def get_enterprise_parameter_engine() -> EnterpriseParameterEngine:
    """Get global enterprise parameter engine instance"""
    global _enterprise_parameter_engine
    if _enterprise_parameter_engine is None:
        _enterprise_parameter_engine = EnterpriseParameterEngine()
    return _enterprise_parameter_engine