"""
Enhanced Dialog Manager - Phase 3.1
OpenAI-powered intelligent XML conversation with context-aware intelligence
and advanced conversation management capabilities
"""

import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from services.chat_xml.chat_session_service import get_chat_session_service, ChatSessionState, MessageType
from services.chat_xml.parameter_extractor import get_parameter_extractor, ParameterStatus
from services.llm_factory import get_llm_service
from services.xml_template_engine import get_template_engine
from services.ai.parameter_extraction_ai import get_parameter_extraction_ai, ExtractionContext, ParameterExtractionMode
from services.ai.chat_xml_database_service import get_chat_xml_database_service
from services.enterprise_cache import get_cache_service
from schemas.streamworks_schemas import (
    get_schema_for_type, StreamType, get_missing_parameters,
    generate_prompt_for_parameter, get_parameter_examples
)

logger = logging.getLogger(__name__)

class DialogIntent(Enum):
    """Dialog-Absichten für intelligente Antwort-Generierung"""
    JOB_TYPE_SELECTION = "job_type_selection"
    PARAMETER_REQUEST = "parameter_request"
    PARAMETER_VALIDATION = "parameter_validation"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    ERROR_EXPLANATION = "error_explanation"
    COMPLETION = "completion"

class DialogContext(Enum):
    """Dialog-Kontext für situative Anpassung"""
    INITIAL_GREETING = "initial_greeting"
    JOB_TYPE_DECISION = "job_type_decision"
    ACTIVE_COLLECTION = "active_collection"
    VALIDATION_ERROR = "validation_error"
    NEAR_COMPLETION = "near_completion"
    FINAL_REVIEW = "final_review"

@dataclass
class ConversationMemory:
    """Advanced conversation memory system for context-aware intelligence"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    extracted_parameters: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_patterns: List[str] = field(default_factory=list)
    context_keywords: List[str] = field(default_factory=list)
    job_type_hints: List[str] = field(default_factory=list)

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation memory"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })

        # Keep only last 15 messages for context
        if len(self.messages) > 15:
            self.messages = self.messages[-15:]

    def get_conversation_context(self) -> str:
        """Generate conversation context string for OpenAI prompts"""
        if not self.messages:
            return "Neue Konversation gestartet."

        recent_messages = self.messages[-10:]  # Last 10 messages for context
        context_lines = []

        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role}: {msg['content']}")

        return "\n".join(context_lines)

    def extract_context_keywords(self, text: str):
        """Extract keywords from conversation for context awareness"""
        keywords = []

        # Extract technical terms
        tech_patterns = ["SAP", "PA1", "script", "batch", "transfer", "file", "system", "report"]
        for pattern in tech_patterns:
            if pattern.lower() in text.lower():
                keywords.append(pattern)

        # Add to context keywords (keep unique)
        for keyword in keywords:
            if keyword not in self.context_keywords:
                self.context_keywords.append(keyword)

        # Keep only last 20 keywords
        if len(self.context_keywords) > 20:
            self.context_keywords = self.context_keywords[-20:]

@dataclass
class IntelligentPromptTemplate:
    """Advanced prompt templates for different conversation scenarios"""
    base_system_prompt: str
    job_type_prompts: Dict[str, str] = field(default_factory=dict)
    parameter_extraction_prompts: Dict[str, str] = field(default_factory=dict)
    clarification_prompts: Dict[str, str] = field(default_factory=dict)
    error_recovery_prompts: Dict[str, str] = field(default_factory=dict)

@dataclass
class DialogResponse:
    """Enhanced Dialog Response with OpenAI intelligence metadata"""
    content: str
    intent: DialogIntent
    context: DialogContext

    # Aktions-Metadaten
    requires_user_input: bool = True
    next_parameter: Optional[str] = None
    suggested_values: List[str] = None
    confidence: float = 1.0

    # UI-Hinweise
    show_progress: bool = False
    highlight_validation: bool = False
    enable_suggestions: bool = False

    # Validation
    validation_issues: Optional[List[str]] = None

    # OpenAI Intelligence Metadata
    extracted_parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_predictions: Dict[str, List[str]] = field(default_factory=dict)
    conversation_quality_score: float = 1.0
    context_understanding_score: float = 1.0
    recovery_suggestions: List[str] = field(default_factory=list)

    # Advanced Features
    detected_intent_confidence: float = 1.0
    alternative_interpretations: List[str] = field(default_factory=list)
    proactive_warnings: List[str] = field(default_factory=list)

class DialogManager:
    """Enhanced OpenAI-powered intelligent conversation manager"""

    def __init__(self):
        """Initialize the enhanced dialog manager"""
        self.session_service = get_chat_session_service()
        self.parameter_extractor = get_parameter_extractor()
        self.llm_service = None  # Will be initialized on first use
        self.template_engine = get_template_engine()
        self.db_service = None  # Will be initialized on first use

        # Enhanced Configuration
        self.max_retry_attempts = 3
        self.context_memory_length = 15  # Increased for better context awareness
        self.conversation_memories: Dict[str, ConversationMemory] = {}

        # Advanced Prompt Engineering
        self.intelligent_prompts = self._initialize_intelligent_prompts()
        self.dialog_prompts = self._load_dialog_prompts()

        # Intelligence Metrics
        self.conversation_metrics = {
            "total_conversations": 0,
            "successful_extractions": 0,
            "error_recoveries": 0,
            "average_conversation_length": 0
        }

        logger.info("Enhanced Dialog Manager with OpenAI intelligence initialized")

    async def _get_llm_service(self):
        """Get LLM service instance (lazy initialization) - Prefer OpenAI for intelligence"""
        if self.llm_service is None:
            # Prefer OpenAI for intelligent conversation management
            try:
                self.llm_service = await get_llm_service("openai")
                logger.info("OpenAI service initialized for intelligent dialog management")
            except Exception as e:
                logger.warning(f"OpenAI not available, falling back to default LLM: {e}")
                self.llm_service = await get_llm_service()
        return self.llm_service

    async def _get_db_service(self):
        """Get Database service instance (lazy initialization) - Temporarily disabled"""
        # Temporarily disabled due to foreign key schema mismatch
        # TODO: Fix database schema and re-enable
        logger.debug("Database service temporarily disabled due to schema issues")
        return None

    def _initialize_intelligent_prompts(self) -> IntelligentPromptTemplate:
        """Initialize advanced prompt templates for OpenAI intelligence"""
        base_system_prompt = """Du bist ein Experte für StreamWorks XML-Generierung. Du hilfst Benutzern dabei, perfekte XML-Konfigurationen durch natürliche Konversation zu erstellen.

Deine Aufgaben:
1. Verstehe den Kontext und die Absichten des Benutzers
2. Stelle intelligente, zielgerichtete Fragen
3. Extrahiere Parameter aus natürlicher Sprache
4. Gib hilfreiche Vorschläge und Korrekturen
5. Führe den Benutzer sanft zur vollständigen XML-Konfiguration

Verhalte dich freundlich, professionell und effizient. Vermeide Redundanz und sei kontextbewusst."""

        job_type_prompts = {
            "STANDARD": """Fokussiere auf Standard-Script-Ausführung. Frage nach:
- Script-Pfad oder Befehl
- Arbeitsverzeichnis
- Parameter und Argumenten
- Ausführungsumgebung (Windows/Unix)""",

            "SAP": """Fokussiere auf SAP-spezifische Parameter. Frage nach:
- SAP System ID (z.B. PA1_100)
- Report Name oder Programm
- Variant (falls verwendet)
- Background/Foreground Ausführung""",

            "FILE_TRANSFER": """Fokussiere auf Dateiübertragung. Frage nach:
- Quell-Agent und Pfad
- Ziel-Agent und Pfad
- Übertragungsmodus (FTP, SFTP, lokaler Copy)
- Archivierungs-Optionen""",

            "CUSTOM": """Erkunde die spezifischen Anforderungen. Frage nach:
- Zweck und Ziel des Jobs
- Besonderen Anforderungen
- Abhängigkeiten und Voraussetzungen
- Gewünschten Funktionen"""
        }

        parameter_extraction_prompts = {
            "extract_with_context": """Analysiere diese Benutzer-Nachricht und extrahiere alle relevanten Parameter für {job_type}:

Nachricht: "{user_message}"
Konversationskontext: {conversation_context}

Extrahiere:
1. Explizit genannte Parameter
2. Implizit erwähnte Werte
3. Hinweise auf weitere benötigte Parameter

Antworte im JSON-Format mit extrahierten Parametern und Confidence-Scores.""",

            "multi_parameter_extraction": """Der Benutzer hat möglicherweise mehrere Parameter in einer Nachricht genannt:

Nachricht: "{user_message}"
Gesuchte Parameter: {target_parameters}

Extrahiere alle erkennbaren Parameter-Werte und gib Confidence-Scores für jede Extraktion."""
        }

        clarification_prompts = {
            "context_aware_clarification": """Der Benutzer sagte: "{user_message}"

Basierend auf dem Konversationsverlauf: {conversation_context}

Ich konnte den Wert für '{parameter}' nicht eindeutig bestimmen.
Generiere eine präzise, hilfreiche Nachfrage auf Deutsch.
Berücksictige den bisherigen Konversationsfluss und vermeide Wiederholungen.""",

            "intelligent_suggestion": """Generiere intelligente Vorschläge für Parameter '{parameter}' basierend auf:

Kontext: {conversation_context}
Job Type: {job_type}
Bereits gesammelte Parameter: {existing_parameters}

Erstelle 2-3 wahrscheinliche Werte oder Beispiele."""
        }

        error_recovery_prompts = {
            "context_aware_recovery": """Ein Fehler ist aufgetreten während der Parametersammlung:

Fehler: {error_message}
Kontext: {conversation_context}
Aktueller Parameter: {current_parameter}

Analysiere den Fehler und erstelle eine hilfreiche Antwort auf Deutsch, die:
1. Den Fehler erklärt
2. Eine Lösung vorschlägt
3. Den Konversationsfluss aufrechterhält""",

            "intelligent_retry": """Die vorherige Extraktion ist fehlgeschlagen:

Fehlgeschlagene Extraktion: {failed_extraction}
Grund: {failure_reason}
Benutzer-Input: {user_input}

Erstelle eine verbesserte Extraktionsstrategie und eine höfliche Nachfrage."""
        }

        return IntelligentPromptTemplate(
            base_system_prompt=base_system_prompt,
            job_type_prompts=job_type_prompts,
            parameter_extraction_prompts=parameter_extraction_prompts,
            clarification_prompts=clarification_prompts,
            error_recovery_prompts=error_recovery_prompts
        )

    def _get_conversation_memory(self, session_id: str) -> ConversationMemory:
        """Get or create conversation memory for session"""
        if session_id not in self.conversation_memories:
            self.conversation_memories[session_id] = ConversationMemory()
        return self.conversation_memories[session_id]

    async def initialize(self) -> None:
        """Initialisiert den Dialog Manager"""
        try:
            await self.session_service.initialize()
            logger.info("Dialog Manager fully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Dialog Manager: {str(e)}")
            raise

    async def process_user_message(self, session_id: str, user_message: str) -> DialogResponse:
        """Enhanced message processing with OpenAI intelligence and context awareness"""

        try:
            # Get conversation memory for context
            memory = self._get_conversation_memory(session_id)
            memory.add_message("user", user_message)
            memory.extract_context_keywords(user_message)

            session = self.session_service.get_session(session_id)
            if not session:
                return DialogResponse(
                    content="❌ Session nicht gefunden. Bitte starten Sie eine neue Session.",
                    intent=DialogIntent.ERROR_EXPLANATION,
                    context=DialogContext.INITIAL_GREETING,
                    requires_user_input=False
                )

            # Enhanced context and intent analysis with OpenAI
            context = self._determine_dialog_context(session)

            # PERFORMANCE OPTIMIZATION: Parallelize AI operations
            import asyncio
            intent_task = asyncio.create_task(self._analyze_user_intent_with_ai(
                user_message, context, session, memory
            ))
            extraction_task = asyncio.create_task(self._intelligent_parameter_extraction(
                user_message, session, memory
            ))

            # Wait for both AI operations to complete in parallel
            (intent, intent_confidence), extracted_data = await asyncio.gather(
                intent_task,
                extraction_task,
                return_exceptions=True
            )

            # Handle potential exceptions from parallel execution
            if isinstance((intent, intent_confidence), Exception):
                logger.warning(f"Intent analysis failed: {(intent, intent_confidence)}")
                intent, intent_confidence = DialogIntent.PARAMETER_REQUEST, 0.5

            if isinstance(extracted_data, Exception):
                logger.warning(f"Parameter extraction failed: {extracted_data}")
                extracted_data = None

            # Update conversation memory with extracted parameters and metadata
            if extracted_data and extracted_data.get("parameters"):
                extracted_params = extracted_data["parameters"]
                ai_metadata = extracted_data.get("ai_metadata", {})

                # Store in conversation memory
                memory.extracted_parameters.update(extracted_params)

                # PERFORMANCE OPTIMIZATION: Parallelize database and session operations
                async def update_database():
                    try:
                        db_service = await self._get_db_service()
                        if db_service:
                            await db_service.update_session_parameters(
                                session_id=uuid.UUID(session_id),
                                parameters=extracted_params,
                                extraction_metadata=ai_metadata,
                                completion_percentage=session.completion_percentage
                            )
                            logger.info(f"Stored {len(extracted_params)} parameters in database")
                        else:
                            logger.warning("Database service not available for parameter storage")
                    except Exception as e:
                        logger.warning(f"Failed to store parameters in database: {str(e)}")

                async def update_session_service():
                    # PERFORMANCE OPTIMIZATION: Parallelize parameter collection
                    async def collect_single_parameter(param_name, value):
                        try:
                            success, message, next_prompt = self.session_service.collect_parameter(
                                session_id, param_name, value
                            )
                            if success:
                                confidence = extracted_data.get("confidence_scores", {}).get(param_name, "N/A")
                                logger.info(f"✅ Parameter '{param_name}' = '{value}' (confidence: {confidence})")
                                return (param_name, True, message)
                            else:
                                logger.warning(f"❌ Failed to collect parameter '{param_name}': {message}")
                                return (param_name, False, message)
                        except Exception as e:
                            logger.warning(f"Exception collecting parameter {param_name}: {str(e)}")
                            return (param_name, False, str(e))

                    # Run all parameter collections in parallel
                    if extracted_params:
                        parameter_tasks = [
                            collect_single_parameter(param_name, value)
                            for param_name, value in extracted_params.items()
                        ]
                        await asyncio.gather(*parameter_tasks, return_exceptions=True)

                # Run database and session updates in parallel
                await asyncio.gather(
                    update_database(),
                    update_session_service(),
                    return_exceptions=True
                )

                # Store AI suggestions and warnings
                if extracted_data.get("suggestions"):
                    memory.user_preferences["ai_suggestions"] = extracted_data["suggestions"]
                if extracted_data.get("warnings"):
                    memory.user_preferences["ai_warnings"] = extracted_data["warnings"]
            else:
                extracted_params = None

            # Process based on session state with enhanced intelligence
            response = None
            if session.state == ChatSessionState.JOB_TYPE_SELECTION:
                response = await self._handle_job_type_selection_enhanced(
                    session_id, user_message, intent, memory, extracted_params
                )

            elif session.state == ChatSessionState.PARAMETER_COLLECTION:
                response = await self._handle_parameter_collection_enhanced(
                    session_id, user_message, intent, memory, extracted_params
                )

            elif session.state == ChatSessionState.VALIDATION:
                response = await self._handle_validation_issues_enhanced(
                    session_id, user_message, intent, memory
                )

            elif session.state == ChatSessionState.COMPLETED:
                response = await self._handle_completed_session(session_id, user_message, intent)

            else:
                response = await self._handle_fallback_response_enhanced(
                    session_id, user_message, context, memory
                )

            # Add response to conversation memory
            if response:
                memory.add_message("assistant", response.content, {
                    "intent": response.intent.value,
                    "context": response.context.value,
                    "confidence": response.confidence
                })

                # Add intelligence metadata
                response.detected_intent_confidence = intent_confidence
                response.extracted_parameters = extracted_params or {}
                response.conversation_quality_score = self._calculate_conversation_quality(memory)
                response.context_understanding_score = self._calculate_context_understanding(memory)

            # Update metrics
            self.conversation_metrics["total_conversations"] += 1
            if extracted_params:
                self.conversation_metrics["successful_extractions"] += 1

            return response

        except Exception as e:
            logger.error(f"Error processing user message in session {session_id}: {str(e)}")

            # Enhanced error recovery with context
            memory = self._get_conversation_memory(session_id)
            error_response = await self._intelligent_error_recovery(
                session_id, user_message, str(e), memory
            )

            self.conversation_metrics["error_recoveries"] += 1
            return error_response

    async def _handle_job_type_selection(self, session_id: str, user_message: str, intent: DialogIntent) -> DialogResponse:
        """Behandelt Job-Type-Auswahl mit KI-Unterstützung"""

        # Extrahiere Job-Type aus Benutzer-Nachricht
        job_type = await self._extract_job_type_from_message(user_message)

        if job_type:
            # Versuche Job-Type zu setzen
            success, message, next_prompt = self.session_service.set_job_type(session_id, job_type)

            if success:
                if next_prompt:
                    return DialogResponse(
                        content=f"{message}\n\n{next_prompt}",
                        intent=DialogIntent.PARAMETER_REQUEST,
                        context=DialogContext.ACTIVE_COLLECTION,
                        show_progress=True,
                        enable_suggestions=True
                    )
                else:
                    return DialogResponse(
                        content=f"{message}\n\nAlle Parameter sind gesammelt. Generiere XML...",
                        intent=DialogIntent.COMPLETION,
                        context=DialogContext.FINAL_REVIEW,
                        requires_user_input=False
                    )
            else:
                # Job-Type ungültig - zeige verfügbare Optionen
                available_types = self.parameter_extractor.get_job_types()
                options_text = self._format_job_type_options(available_types)

                return DialogResponse(
                    content=f"{message}\n\n{options_text}",
                    intent=DialogIntent.JOB_TYPE_SELECTION,
                    context=DialogContext.JOB_TYPE_DECISION,
                    suggested_values=list(available_types.keys())
                )
        else:
            # Kein Job-Type erkannt - bitte um Klarstellung
            return await self._generate_clarification_response(session_id, user_message, "job_type")

    # ===== ENHANCED INTELLIGENT METHODS =====

    async def _analyze_user_intent_with_ai(
        self, user_message: str, context: DialogContext, session, memory: ConversationMemory
    ) -> Tuple[DialogIntent, float]:
        """Analyze user intent with OpenAI intelligence and conversation context"""

        try:
            llm_service = await self._get_llm_service()
            conversation_context = memory.get_conversation_context()

            intent_prompt = f"""Analysiere die Benutzer-Absicht in dieser StreamWorks XML-Dialog-Situation:

Aktuelle Nachricht: "{user_message}"
Dialog-Kontext: {context.value}
Konversationsverlauf: {conversation_context}
Session-Status: {session.state.value if session else 'unknown'}

Bestimme die wahrscheinlichste Absicht aus:
- JOB_TYPE_SELECTION: Benutzer wählt oder nennt Job-Typ
- PARAMETER_REQUEST: Benutzer gibt Parameter-Werte an
- CLARIFICATION: Benutzer braucht Hilfe oder Klarstellung
- CONFIRMATION: Benutzer bestätigt oder stimmt zu
- ERROR_EXPLANATION: Problem oder Fehler

Antworte nur mit JSON: {{"intent": "INTENT_NAME", "confidence": 0.8, "reasoning": "kurze Erklärung"}}"""

            response = await llm_service.generate(intent_prompt)

            try:
                result = json.loads(response)
                intent_name = result.get("intent", "CLARIFICATION")
                confidence = result.get("confidence", 0.5)

                # Convert string to enum
                intent = DialogIntent(intent_name.lower())

                logger.info(f"AI Intent Analysis: {intent_name} (confidence: {confidence})")
                return intent, confidence

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse AI intent response: {e}")
                return self._analyze_user_intent(user_message, context, session), 0.5

        except Exception as e:
            logger.warning(f"AI intent analysis failed: {e}")
            return self._analyze_user_intent(user_message, context, session), 0.5

    async def _intelligent_parameter_extraction(
        self, user_message: str, session, memory: ConversationMemory
    ) -> Optional[Dict[str, Any]]:
        """Extract parameters with specialized Parameter AI - Phase 3+ Enhancement"""

        if not session or not session.parameter_checklist:
            return None

        try:
            # Use specialized Parameter Extraction AI
            parameter_ai = get_parameter_extraction_ai()

            # Build extraction context
            extraction_context = ExtractionContext(
                job_type=getattr(session, 'job_type', 'UNKNOWN'),
                conversation_history=memory.messages[-5:],  # Last 5 messages for context
                extracted_parameters=session.collected_parameters or {},
                user_preferences=memory.user_preferences,
                business_context={
                    "session_id": session.session_id,
                    "completion_percentage": session.completion_percentage,
                    "missing_parameters": session.parameter_checklist.missing_parameters
                }
            )

            # Use balanced mode for real-time extraction
            extraction_result = await parameter_ai.extract_parameters(
                user_message=user_message,
                context=extraction_context,
                mode=ParameterExtractionMode.BALANCED
            )

            # Store AI metadata for analytics
            memory.user_preferences["last_extraction_metadata"] = {
                "extraction_method": extraction_result.extraction_method,
                "processing_time": extraction_result.processing_time,
                "precision_score": extraction_result.precision_score,
                "completeness_score": extraction_result.completeness_score,
                "confidence_scores": extraction_result.confidence_scores
            }

            # Return extracted parameters if any found
            if extraction_result.extracted_parameters:
                logger.info(f"Parameter AI extracted: {list(extraction_result.extracted_parameters.keys())} "
                           f"(precision: {extraction_result.precision_score:.2f})")
                return {
                    "parameters": extraction_result.extracted_parameters,
                    "confidence_scores": extraction_result.confidence_scores,
                    "suggestions": extraction_result.suggestions,
                    "warnings": extraction_result.warnings,
                    "ai_metadata": {
                        "extraction_method": extraction_result.extraction_method,
                        "precision_score": extraction_result.precision_score,
                        "completeness_score": extraction_result.completeness_score,
                        "processing_time": extraction_result.processing_time
                    }
                }

            return None

        except Exception as e:
            logger.warning(f"Parameter AI extraction failed, falling back to legacy: {str(e)}")
            # Fallback to legacy extraction
            return await self._legacy_parameter_extraction(user_message, session, memory)

    async def _legacy_parameter_extraction(
        self, user_message: str, session, memory: ConversationMemory
    ) -> Optional[Dict[str, Any]]:
        """Legacy parameter extraction method as fallback"""

        if not session or not session.parameter_checklist:
            return None

        try:
            llm_service = await self._get_llm_service()
            job_type = getattr(session, 'job_type', 'UNKNOWN')
            conversation_context = memory.get_conversation_context()

            # Get current target parameters
            current_param = session.parameter_checklist.next_parameter
            all_params = [p.name for p in session.parameter_checklist.parameters]

            extraction_prompt = self.intelligent_prompts.parameter_extraction_prompts["extract_with_context"].format(
                user_message=user_message,
                job_type=job_type,
                conversation_context=conversation_context[:500]  # Limit context length
            )

            response = await llm_service.generate(extraction_prompt)

            try:
                extracted = json.loads(response)

                # Validate extracted parameters
                valid_params = {}
                confidence_scores = {}
                for param_name, param_data in extracted.items():
                    if param_name in all_params:
                        value = param_data.get("value") if isinstance(param_data, dict) else param_data
                        if value and str(value).strip():
                            valid_params[param_name] = str(value).strip()
                            confidence_scores[param_name] = 0.7  # Default confidence for legacy

                if valid_params:
                    return {
                        "parameters": valid_params,
                        "confidence_scores": confidence_scores,
                        "suggestions": [],
                        "warnings": [],
                        "ai_metadata": {
                            "extraction_method": "legacy_openai",
                            "precision_score": 0.7,
                            "completeness_score": 0.8,
                            "processing_time": 0.0
                        }
                    }

                return None

            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse AI extraction response: {e}")
                return None

        except Exception as e:
            logger.warning(f"AI parameter extraction failed: {e}")
            return None

    async def _handle_job_type_selection_enhanced(
        self, session_id: str, user_message: str, intent: DialogIntent,
        memory: ConversationMemory, extracted_params: Optional[Dict[str, Any]]
    ) -> DialogResponse:
        """Enhanced job type selection with OpenAI intelligence"""

        # Try intelligent job type extraction first
        job_type = await self._extract_job_type_with_ai(user_message, memory)

        if job_type:
            success, message, next_prompt = self.session_service.set_job_type(session_id, job_type)

            if success:
                # Generate intelligent welcome message for job type
                welcome_message = await self._generate_job_type_welcome(job_type, memory)

                if next_prompt:
                    combined_message = f"{welcome_message}\n\n{next_prompt}"
                    return DialogResponse(
                        content=combined_message,
                        intent=DialogIntent.PARAMETER_REQUEST,
                        context=DialogContext.ACTIVE_COLLECTION,
                        show_progress=True,
                        enable_suggestions=True,
                        parameter_predictions=await self._predict_likely_parameters(job_type, memory)
                    )
                else:
                    return DialogResponse(
                        content=f"{welcome_message}\n\nAlle Parameter sind gesammelt. Generiere XML...",
                        intent=DialogIntent.COMPLETION,
                        context=DialogContext.FINAL_REVIEW,
                        requires_user_input=False
                    )
            else:
                available_types = self.parameter_extractor.get_job_types()
                options_text = self._format_job_type_options(available_types)

                return DialogResponse(
                    content=f"{message}\n\n{options_text}",
                    intent=DialogIntent.JOB_TYPE_SELECTION,
                    context=DialogContext.JOB_TYPE_DECISION,
                    suggested_values=list(available_types.keys())
                )
        else:
            # Generate intelligent clarification
            return await self._generate_intelligent_clarification(
                session_id, user_message, "job_type", memory
            )

    async def _handle_parameter_collection_enhanced(
        self, session_id: str, user_message: str, intent: DialogIntent,
        memory: ConversationMemory, extracted_params: Optional[Dict[str, Any]]
    ) -> DialogResponse:
        """Enhanced parameter collection with multi-parameter extraction"""

        session = self.session_service.get_session(session_id)
        if not session or not session.parameter_checklist:
            return DialogResponse(
                content="❌ Session-Fehler. Parameter-Sammlung nicht möglich.",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.INITIAL_GREETING,
                requires_user_input=False
            )

        # Enhanced StreamWorks parameter collection with smart missing detection
        job_type = getattr(session, 'job_type', 'STANDARD')
        try:
            stream_type = StreamType(job_type)
        except ValueError:
            stream_type = StreamType.STANDARD

        # Process extracted parameters and store in session
        collected_params = getattr(session, 'collected_parameters', {})
        if extracted_params:
            collected_params.update(extracted_params)
            # Update session with new parameters
            for param_name, param_value in extracted_params.items():
                success, message, _ = self.session_service.collect_parameter(
                    session_id, param_name, param_value
                )
                if success:
                    logger.info(f"✅ Collected: {param_name} = {param_value}")

        # Check for missing required parameters using StreamWorks schemas
        missing_params = get_missing_parameters(collected_params, stream_type)

        if not missing_params:
            # All required parameters collected
            return await self._initiate_xml_generation(session_id)

        # Get next missing parameter to ask for
        next_param = missing_params[0]

        # Generate smart question using StreamWorks schema
        next_question = await self._generate_streamworks_question(
            next_param, stream_type, collected_params, memory
        )

        # Get examples for the parameter
        examples = get_parameter_examples(next_param, stream_type)

        return DialogResponse(
            content=next_question,
            intent=DialogIntent.PARAMETER_REQUEST,
            context=DialogContext.ACTIVE_COLLECTION,
            next_parameter=next_param,
            show_progress=True,
            enable_suggestions=True,
            suggested_values=examples[:3] if examples else [],  # Top 3 examples
            parameter_predictions={next_param: examples[:5]} if examples else {}
        )

    async def _handle_validation_issues_enhanced(
        self, session_id: str, user_message: str, intent: DialogIntent, memory: ConversationMemory
    ) -> DialogResponse:
        """Enhanced validation handling with intelligent recovery"""

        session = self.session_service.get_session(session_id)
        if not session:
            return DialogResponse(
                content="❌ Session nicht gefunden.",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.INITIAL_GREETING,
                requires_user_input=False
            )

        # Generate intelligent repair suggestions with AI
        repair_suggestions = await self._generate_intelligent_repair_suggestions(
            session.generated_xml, session.validation_issues, memory
        )

        validation_summary = "\n".join(f"• {issue}" for issue in session.validation_issues[:3])

        return DialogResponse(
            content=f"⚠️ XML wurde generiert, hat aber Validierungsfehler:\n\n{validation_summary}\n\n"
                   f"💡 Intelligente Vorschläge:\n{repair_suggestions}\n\n"
                   f"Möchten Sie die Fehler automatisch reparieren lassen oder Parameter überprüfen?",
            intent=DialogIntent.ERROR_EXPLANATION,
            context=DialogContext.VALIDATION_ERROR,
            suggested_values=["Automatisch reparieren", "Parameter überprüfen", "XML anzeigen"],
            highlight_validation=True,
            recovery_suggestions=repair_suggestions.split('\n')
        )

    async def _handle_fallback_response_enhanced(
        self, session_id: str, user_message: str, context: DialogContext, memory: ConversationMemory
    ) -> DialogResponse:
        """Enhanced fallback with intelligent help generation"""

        # Generate context-aware help with AI
        help_content = await self._generate_context_aware_help(user_message, context, memory)

        return DialogResponse(
            content=help_content,
            intent=DialogIntent.CLARIFICATION,
            context=context,
            suggested_values=["Neue Session", "Hilfe", "Status"],
            alternative_interpretations=await self._suggest_alternative_interpretations(user_message, memory)
        )

    async def _handle_parameter_collection(self, session_id: str, user_message: str, intent: DialogIntent) -> DialogResponse:
        """Behandelt Parameter-Sammlung mit intelligenter Werteextraktion"""

        session = self.session_service.get_session(session_id)
        if not session or not session.parameter_checklist:
            return DialogResponse(
                content="❌ Session-Fehler. Parameter-Sammlung nicht möglich.",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.INITIAL_GREETING,
                requires_user_input=False
            )

        # Bestimme aktuellen Parameter
        current_parameter = session.parameter_checklist.next_parameter
        if not current_parameter:
            # Alle Parameter gesammelt
            return await self._initiate_xml_generation(session_id)

        # Extrahiere Wert aus Benutzer-Nachricht
        extracted_value = await self._extract_parameter_value(user_message, current_parameter, session)

        if extracted_value:
            # Versuche Parameter zu setzen
            success, message, next_prompt = self.session_service.collect_parameter(
                session_id, current_parameter, extracted_value
            )

            if success:
                if next_prompt and next_prompt != "XML wird generiert...":
                    # Nächster Parameter
                    return DialogResponse(
                        content=f"{message}\n\n{next_prompt}",
                        intent=DialogIntent.PARAMETER_REQUEST,
                        context=DialogContext.ACTIVE_COLLECTION,
                        show_progress=True,
                        enable_suggestions=True
                    )
                else:
                    # Parameter-Sammlung abgeschlossen
                    return await self._initiate_xml_generation(session_id)
            else:
                # Validierungsfehler
                return DialogResponse(
                    content=f"{message}\n\n{next_prompt or 'Bitte versuchen Sie es erneut.'}",
                    intent=DialogIntent.PARAMETER_VALIDATION,
                    context=DialogContext.VALIDATION_ERROR,
                    highlight_validation=True
                )
        else:
            # Wert nicht erkannt - bitte um Klarstellung
            return await self._generate_clarification_response(session_id, user_message, current_parameter)

    async def _handle_validation_issues(self, session_id: str, user_message: str, intent: DialogIntent) -> DialogResponse:
        """Behandelt Validierungsfehler mit intelligenten Korrekturvorschlägen"""

        session = self.session_service.get_session(session_id)
        if not session:
            return DialogResponse(
                content="❌ Session nicht gefunden.",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.INITIAL_GREETING,
                requires_user_input=False
            )

        # Analysiere Validierungsfehler
        validation_summary = "\n".join(f"• {issue}" for issue in session.validation_issues[:3])

        # Generiere KI-unterstützte Reparatur-Vorschläge
        repair_suggestions = await self._generate_repair_suggestions(session.generated_xml, session.validation_issues)

        return DialogResponse(
            content=f"⚠️ XML wurde generiert, hat aber Validierungsfehler:\n\n{validation_summary}\n\n"
                   f"💡 Vorschläge:\n{repair_suggestions}\n\n"
                   f"Möchten Sie die Fehler automatisch reparieren lassen oder Parameter überprüfen?",
            intent=DialogIntent.ERROR_EXPLANATION,
            context=DialogContext.VALIDATION_ERROR,
            suggested_values=["Automatisch reparieren", "Parameter überprüfen", "XML anzeigen"],
            highlight_validation=True
        )

    async def _handle_completed_session(self, session_id: str, user_message: str, intent: DialogIntent) -> DialogResponse:
        """Behandelt abgeschlossene Sessions mit Export-Optionen"""

        if "neue session" in user_message.lower() or "neu starten" in user_message.lower():
            # Neue Session starten
            new_session_id = self.session_service.create_session()
            return DialogResponse(
                content=f"✨ Neue Session gestartet! Session-ID: {new_session_id}\n\n"
                       f"Welchen Job-Type möchten Sie erstellen?",
                intent=DialogIntent.JOB_TYPE_SELECTION,
                context=DialogContext.JOB_TYPE_DECISION
            )

        return DialogResponse(
            content="✅ XML-Generierung ist abgeschlossen!\n\n"
                   "Optionen:\n"
                   "• 'XML anzeigen' - Zeigt das generierte XML\n"
                   "• 'Neue Session' - Startet eine neue XML-Generierung\n"
                   "• 'Export' - Lädt das XML herunter",
            intent=DialogIntent.COMPLETION,
            context=DialogContext.FINAL_REVIEW,
            suggested_values=["XML anzeigen", "Neue Session", "Export"]
        )

    async def _extract_job_type_from_message(self, user_message: str) -> Optional[str]:
        """Extrahiert Job-Type aus Benutzer-Nachricht mit KI-Unterstützung"""

        available_types = self.parameter_extractor.get_job_types()
        user_message_lower = user_message.lower()

        # Direkte Übereinstimmung
        for job_type in available_types.keys():
            if job_type.lower() in user_message_lower:
                return job_type

        # Fuzzy Matching für häufige Varianten
        fuzzy_matches = {
            "standard": "STANDARD",
            "normal": "STANDARD",
            "basic": "STANDARD",
            "sap": "SAP",
            "file": "FILE_TRANSFER",
            "transfer": "FILE_TRANSFER",
            "copy": "FILE_TRANSFER",
            "custom": "CUSTOM",
            "special": "CUSTOM"
        }

        for variant, job_type in fuzzy_matches.items():
            if variant in user_message_lower and job_type in available_types:
                return job_type

        # KI-basierte Extraktion für komplexere Fälle
        try:
            llm_service = await self._get_llm_service()
            if llm_service:
                extraction_prompt = f"""
Extrahiere den Job-Type aus dieser Benutzer-Nachricht: "{user_message}"

Verfügbare Job-Types:
{chr(10).join(f"- {jt}: {info['description']}" for jt, info in available_types.items())}

Antworte nur mit dem exakten Job-Type Namen oder "NONE" falls keiner erkennbar ist.
"""

                response = await llm_service.generate(extraction_prompt)
                extracted = response.strip().upper()

                if extracted in available_types:
                    return extracted

        except Exception as e:
            logger.warning(f"KI-Job-Type-Extraktion fehlgeschlagen: {str(e)}")

        return None

    async def _extract_parameter_value(self, user_message: str, parameter_name: str, session) -> Optional[str]:
        """Extrahiert Parameter-Wert aus Benutzer-Nachricht"""

        # Finde Parameter-Definition
        param_def = None
        for param in session.parameter_checklist.parameters:
            if param.name == parameter_name:
                param_def = param
                break

        if not param_def:
            return user_message.strip()

        # Spezielle Extraktion für Enum-Parameter
        if param_def.enum_values:
            user_lower = user_message.lower()
            for enum_value in param_def.enum_values:
                if enum_value.lower() in user_lower:
                    return enum_value

        # Boolean-Parameter Extraktion
        if param_def.data_type == "boolean":
            user_lower = user_message.lower()
            if any(word in user_lower for word in ["ja", "yes", "true", "1", "aktivieren", "ein"]):
                return "true"
            elif any(word in user_lower for word in ["nein", "no", "false", "0", "deaktivieren", "aus"]):
                return "false"

        # Numerische Extraktion für Integer-Parameter
        if param_def.data_type == "integer":
            import re
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                return numbers[0]

        # Standard-Extraktion: Verwende die gesamte Nachricht als Wert
        return user_message.strip()

    async def _generate_clarification_response(self, session_id: str, user_message: str, context_param: str) -> DialogResponse:
        """Generiert Klarstellungs-Anfrage mit KI-Unterstützung"""

        try:
            llm_service = await self._get_llm_service()
            if llm_service:
                clarification_prompt = f"""
Der Benutzer hat gesagt: "{user_message}"

Ich konnte den Wert für Parameter '{context_param}' nicht eindeutig extrahieren.
Generiere eine höfliche, hilfreiche Nachfrage auf Deutsch.
Halte die Antwort kurz (max. 2 Sätze) und erkläre was genau benötigt wird.
"""

                response = await llm_service.generate(clarification_prompt)
                return DialogResponse(
                    content=f"🤔 {response.strip()}",
                    intent=DialogIntent.CLARIFICATION,
                    context=DialogContext.ACTIVE_COLLECTION
                )
        except Exception as e:
            logger.warning(f"KI-Klarstellung fehlgeschlagen: {str(e)}")

        # Fallback-Antwort
        return DialogResponse(
            content=f"🤔 Entschuldigung, ich konnte Ihre Eingabe nicht verstehen.\n"
                   f"Könnten Sie bitte den Wert für '{context_param}' klarer angeben?",
            intent=DialogIntent.CLARIFICATION,
            context=DialogContext.ACTIVE_COLLECTION
        )

    async def _initiate_xml_generation(self, session_id: str) -> DialogResponse:
        """Startet XML-Generierung und gibt Ergebnis zurück"""

        success, message, xml_content = self.session_service.generate_xml(session_id)

        if success:
            return DialogResponse(
                content=f"🎉 {message}\n\n📄 XML erfolgreich generiert ({len(xml_content)} Zeichen)!\n\n"
                       f"Möchten Sie das XML anzeigen oder exportieren?",
                intent=DialogIntent.COMPLETION,
                context=DialogContext.FINAL_REVIEW,
                suggested_values=["XML anzeigen", "Exportieren", "Neue Session"],
                requires_user_input=True
            )
        else:
            return DialogResponse(
                content=f"⚠️ {message}\n\nMöchten Sie die Fehler automatisch reparieren lassen?",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.VALIDATION_ERROR,
                suggested_values=["Automatisch reparieren", "Parameter überprüfen"],
                highlight_validation=True
            )

    def _determine_dialog_context(self, session) -> DialogContext:
        """Bestimmt den aktuellen Dialog-Kontext"""
        if session.state == ChatSessionState.CREATED:
            return DialogContext.INITIAL_GREETING
        elif session.state == ChatSessionState.JOB_TYPE_SELECTION:
            return DialogContext.JOB_TYPE_DECISION
        elif session.state == ChatSessionState.PARAMETER_COLLECTION:
            if session.completion_percentage > 80:
                return DialogContext.NEAR_COMPLETION
            else:
                return DialogContext.ACTIVE_COLLECTION
        elif session.state == ChatSessionState.VALIDATION:
            return DialogContext.VALIDATION_ERROR
        elif session.state == ChatSessionState.COMPLETED:
            return DialogContext.FINAL_REVIEW
        else:
            return DialogContext.INITIAL_GREETING

    def _analyze_user_intent(self, user_message: str, context: DialogContext, session) -> DialogIntent:
        """Analysiert Benutzer-Absicht basierend auf Nachricht und Kontext"""
        user_lower = user_message.lower()

        # Intent-Keywords
        if any(word in user_lower for word in ["help", "hilfe", "was", "wie"]):
            return DialogIntent.CLARIFICATION
        elif any(word in user_lower for word in ["ja", "ok", "bestätigen", "weiter"]):
            return DialogIntent.CONFIRMATION
        elif any(word in user_lower for word in ["nein", "abbruch", "stop", "cancel"]):
            return DialogIntent.ERROR_EXPLANATION
        elif context == DialogContext.JOB_TYPE_DECISION:
            return DialogIntent.JOB_TYPE_SELECTION
        elif context == DialogContext.ACTIVE_COLLECTION:
            return DialogIntent.PARAMETER_REQUEST
        else:
            return DialogIntent.CLARIFICATION

    def _format_job_type_options(self, available_types: Dict[str, Any]) -> str:
        """Formatiert verfügbare Job-Types für Benutzer-Auswahl"""
        options = []
        for job_type, info in available_types.items():
            options.append(f"🔹 **{info['display_name']}** ({job_type})")
            options.append(f"   {info['description']}")
            options.append(f"   ⏱️ {info['estimated_time']} | 📋 {info['parameter_count']} Parameter")
            options.append("")

        return "📋 **Verfügbare Job-Types:**\n\n" + "\n".join(options)

    async def _generate_repair_suggestions(self, xml_content: str, validation_issues: List[str]) -> str:
        """Generiert intelligente Reparatur-Vorschläge"""
        try:
            llm_service = await self._get_llm_service()
            if llm_service:
                repair_prompt = f"""
Analysiere diese XML-Validierungsfehler und gib 2-3 konkrete Reparatur-Vorschläge:

Fehler:
{chr(10).join(validation_issues[:3])}

Antworte nur mit nummerierten Vorschlägen auf Deutsch, max. 3 Zeilen.
"""

                response = await llm_service.generate(repair_prompt)
                return response.strip()
        except Exception as e:
            logger.warning(f"KI-Reparatur-Vorschläge fehlgeschlagen: {str(e)}")

        return "1. Parameter-Werte überprüfen\n2. XML-Schema validieren\n3. Automatische Reparatur versuchen"

    # ===== ADDITIONAL INTELLIGENT HELPER METHODS =====

    async def _extract_job_type_with_ai(self, user_message: str, memory: ConversationMemory) -> Optional[str]:
        """Enhanced job type extraction with OpenAI and conversation context"""

        # First try the existing method
        job_type = await self._extract_job_type_from_message(user_message)
        if job_type:
            return job_type

        # Try with AI and conversation context
        try:
            llm_service = await self._get_llm_service()
            available_types = self.parameter_extractor.get_job_types()
            conversation_context = memory.get_conversation_context()

            ai_prompt = f"""Analysiere diese Nachricht und den Konversationsverlauf, um den Job-Type zu bestimmen:

Aktuelle Nachricht: "{user_message}"
Konversationsverlauf: {conversation_context}

Verfügbare Job-Types:
{chr(10).join(f"- {jt}: {info['description']}" for jt, info in available_types.items())}

Context-Keywords: {', '.join(memory.context_keywords)}

Antworte nur mit dem exakten Job-Type Namen oder "NONE" falls keiner erkennbar ist.
Berücksichtige auch indirekte Hinweise aus dem Konversationsverlauf."""

            response = await llm_service.generate(ai_prompt)
            extracted = response.strip().upper()

            if extracted in available_types:
                logger.info(f"AI extracted job type: {extracted}")
                return extracted

        except Exception as e:
            logger.warning(f"AI job type extraction failed: {e}")

        return None

    async def _generate_job_type_welcome(self, job_type: str, memory: ConversationMemory) -> str:
        """Generate personalized welcome message for selected job type"""

        try:
            llm_service = await self._get_llm_service()
            job_prompts = self.intelligent_prompts.job_type_prompts
            context_keywords = ', '.join(memory.context_keywords) if memory.context_keywords else 'keine'

            welcome_prompt = f"""Erstelle eine freundliche Begrüßung für einen {job_type} Job in StreamWorks XML-Generator.

Job-Type: {job_type}
Job-Fokus: {job_prompts.get(job_type, 'Allgemeine Konfiguration')}
Kontext-Keywords: {context_keywords}

Erstelle eine 1-2 Sätze lange Begrüßung auf Deutsch, die:
1. Den Job-Type bestätigt
2. Kurz die nächsten Schritte erklärt
3. Enthusiastisch und hilfreich klingt

Beispiel: "Perfekt! Ich helfe Ihnen bei der Erstellung eines SAP Jobs. Lassen Sie uns die benötigten Parameter sammeln..."
"""

            response = await llm_service.generate(welcome_prompt)
            return response.strip()

        except Exception as e:
            logger.warning(f"Failed to generate AI welcome message: {e}")
            return f"Perfekt! Ich helfe Ihnen bei der Erstellung eines {job_type} Jobs."

    async def _predict_likely_parameters(self, job_type: str, memory: ConversationMemory) -> Dict[str, List[str]]:
        """Predict likely parameter values based on job type and conversation context"""

        try:
            llm_service = await self._get_llm_service()
            context_keywords = memory.context_keywords

            prediction_prompt = f"""Basierend auf dem Job-Type {job_type} und den Kontext-Keywords {context_keywords},
            erstelle wahrscheinliche Parameter-Werte für häufige Parameter.

Antworte im JSON-Format mit Parameter-Namen und 2-3 wahrscheinlichen Werten:
{{"parameter_name": ["wert1", "wert2", "wert3"]}}

Fokussiere auf realistische StreamWorks-Werte für {job_type}."""

            response = await llm_service.generate(prediction_prompt)

            try:
                predictions = json.loads(response)
                return predictions if isinstance(predictions, dict) else {}
            except json.JSONDecodeError:
                return {}

        except Exception as e:
            logger.warning(f"Parameter prediction failed: {e}")
            return {}

    async def _generate_streamworks_question(
        self, parameter_name: str, stream_type: StreamType, collected_params: Dict[str, Any],
        memory: ConversationMemory
    ) -> str:
        """Generate StreamWorks-specific intelligent question for parameter"""

        try:
            llm_service = await self._get_llm_service()

            # Get parameter info from StreamWorks schema
            schema_prompt = generate_prompt_for_parameter(parameter_name, stream_type)
            examples = get_parameter_examples(parameter_name, stream_type)
            conversation_context = memory.get_conversation_context()

            # Build context-aware question prompt
            question_prompt = f"""Du bist ein StreamWorks-Experte. Erstelle eine präzise, hilfreiche Frage für Parameter '{parameter_name}':

STREAM-TYP: {stream_type.value}
SCHEMA-PROMPT: {schema_prompt}
BEISPIELE: {', '.join(examples[:3]) if examples else 'Keine verfügbar'}

BEREITS GESAMMELTE PARAMETER:
{json.dumps(collected_params, indent=2)}

KONVERSATIONSKONTEXT:
{conversation_context}

ERSTELLE EINE FRAGE DIE:
1. StreamWorks-spezifisch und technisch korrekt ist
2. Passende Beispiele für {stream_type.value} enthält
3. Den Kontext der bereits gesammelten Parameter berücksichtigt
4. Kurz und präzise ist (1-2 Sätze)
5. Freundlich und hilfreich formuliert ist

Beispiele für gute Fragen:
- SAP: "Welches SAP-System verwenden Sie? (z.B. ZTV, PA1, PRD)"
- Transfer: "Von welchem Agent sollen die Dateien übertragen werden? (z.B. gtlnmiwvm1636)"
- Standard: "Welches Skript soll ausgeführt werden? (z.B. python process.py)"

ANTWORTE NUR mit der Frage, keine weiteren Erklärungen."""

            response = await llm_service.generate(question_prompt)
            return response.strip()

        except Exception as e:
            logger.warning(f"Failed to generate StreamWorks question: {e}")
            # Fallback to schema-based prompt
            return generate_prompt_for_parameter(parameter_name, stream_type)

    async def _generate_intelligent_question(
        self, parameter_name: str, session, memory: ConversationMemory
    ) -> str:
        """Legacy method - redirects to StreamWorks-specific version"""

        job_type = getattr(session, 'job_type', 'STANDARD')
        try:
            stream_type = StreamType(job_type)
        except ValueError:
            stream_type = StreamType.STANDARD

        collected_params = getattr(session, 'collected_parameters', {})
        return await self._generate_streamworks_question(parameter_name, stream_type, collected_params, memory)

    async def _predict_parameter_values(self, parameter_name: str, memory: ConversationMemory) -> Dict[str, List[str]]:
        """Predict likely values for specific parameter"""

        try:
            llm_service = await self._get_llm_service()
            context_keywords = memory.context_keywords
            extracted_params = memory.extracted_parameters

            prediction_prompt = f"""Basierend auf dem Parameter '{parameter_name}' und dem Kontext,
            erstelle 2-3 wahrscheinliche Werte:

Parameter: {parameter_name}
Kontext-Keywords: {context_keywords}
Bereits gesammelte Parameter: {extracted_params}

Antworte mit JSON: {{"suggestions": ["wert1", "wert2", "wert3"]}}

Fokussiere auf realistische, häufig verwendete Werte für StreamWorks."""

            response = await llm_service.generate(prediction_prompt)

            try:
                result = json.loads(response)
                suggestions = result.get("suggestions", [])
                return {parameter_name: suggestions} if suggestions else {}
            except json.JSONDecodeError:
                return {}

        except Exception as e:
            logger.warning(f"Parameter value prediction failed: {e}")
            return {}

    async def _generate_intelligent_clarification(
        self, session_id: str, user_message: str, context_param: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Generate intelligent clarification with conversation context"""

        try:
            llm_service = await self._get_llm_service()
            conversation_context = memory.get_conversation_context()

            clarification_prompt = self.intelligent_prompts.clarification_prompts["context_aware_clarification"].format(
                user_message=user_message,
                conversation_context=conversation_context[:300],
                parameter=context_param
            )

            response = await llm_service.generate(clarification_prompt)

            return DialogResponse(
                content=f"🤔 {response.strip()}",
                intent=DialogIntent.CLARIFICATION,
                context=DialogContext.ACTIVE_COLLECTION,
                alternative_interpretations=await self._suggest_alternative_interpretations(user_message, memory)
            )

        except Exception as e:
            logger.warning(f"Intelligent clarification failed: {e}")
            return DialogResponse(
                content=f"🤔 Entschuldigung, ich konnte Ihre Eingabe nicht verstehen.\n"
                       f"Könnten Sie bitte den Wert für '{context_param}' klarer angeben?",
                intent=DialogIntent.CLARIFICATION,
                context=DialogContext.ACTIVE_COLLECTION
            )

    async def _generate_intelligent_repair_suggestions(
        self, xml_content: str, validation_issues: List[str], memory: ConversationMemory
    ) -> str:
        """Generate intelligent repair suggestions using AI"""

        try:
            llm_service = await self._get_llm_service()

            repair_prompt = f"""Analysiere diese XML-Validierungsfehler und erstelle intelligente Reparatur-Vorschläge:

Fehler:
{chr(10).join(validation_issues[:3])}

XML-Kontext: {xml_content[:200] if xml_content else 'Nicht verfügbar'}...

Erstelle 3 konkrete, umsetzbare Reparatur-Vorschläge auf Deutsch.
Jeder Vorschlag sollte spezifisch und verständlich sein.
Format: "1. [Konkreter Vorschlag]" """

            response = await llm_service.generate(repair_prompt)
            return response.strip()

        except Exception as e:
            logger.warning(f"Intelligent repair suggestions failed: {e}")
            return "1. Parameter-Werte überprüfen\n2. XML-Schema validieren\n3. Automatische Reparatur versuchen"

    async def _generate_context_aware_help(
        self, user_message: str, context: DialogContext, memory: ConversationMemory
    ) -> str:
        """Generate context-aware help content"""

        try:
            llm_service = await self._get_llm_service()
            conversation_context = memory.get_conversation_context()

            help_prompt = f"""Der Benutzer braucht Hilfe in dieser Situation:

Benutzer-Nachricht: "{user_message}"
Dialog-Kontext: {context.value}
Konversationsverlauf: {conversation_context}

Erstelle eine hilfreiche Antwort auf Deutsch, die:
1. Die aktuelle Situation erklärt
2. Verfügbare Optionen aufzeigt
3. Nächste Schritte vorschlägt
4. Freundlich und ermutigend ist

Halte die Antwort kurz aber informativ (2-3 Sätze)."""

            response = await llm_service.generate(help_prompt)
            return response.strip()

        except Exception as e:
            logger.warning(f"Context-aware help generation failed: {e}")
            return "🤔 Ich bin hier, um Ihnen zu helfen! Verfügbare Kommandos:\n• 'Neue Session' - Startet XML-Generierung\n• 'Hilfe' - Zeigt verfügbare Optionen"

    async def _suggest_alternative_interpretations(
        self, user_message: str, memory: ConversationMemory
    ) -> List[str]:
        """Suggest alternative interpretations of user message"""

        try:
            llm_service = await self._get_llm_service()

            interpretation_prompt = f"""Analysiere diese Benutzer-Nachricht und erstelle 2-3 alternative Interpretationen:

Nachricht: "{user_message}"
Kontext: StreamWorks XML-Generierung

Mögliche Interpretationen könnten sein:
- Verschiedene Job-Types
- Verschiedene Parameter-Werte
- Verschiedene Aktionen

Antworte mit JSON: {{"alternatives": ["interpretation1", "interpretation2", "interpretation3"]}}"""

            response = await llm_service.generate(interpretation_prompt)

            try:
                result = json.loads(response)
                return result.get("alternatives", [])
            except json.JSONDecodeError:
                return []

        except Exception as e:
            logger.warning(f"Alternative interpretation suggestion failed: {e}")
            return []

    async def _intelligent_error_recovery(
        self, session_id: str, user_message: str, error_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Enhanced intelligent error recovery with smart strategy selection"""

        try:
            # Classify error type for targeted recovery
            error_type = await self._classify_error_type(error_message, memory.get_conversation_context())

            # Select optimal recovery strategy
            recovery_strategy = await self._select_recovery_strategy(
                error_type, error_message, memory.get_conversation_context()
            )

            logger.info(f"Error recovery: type={error_type}, strategy={recovery_strategy}")

            # Execute recovery strategy
            response = await self._execute_recovery_strategy(
                recovery_strategy, error_message, user_message, memory
            )

            # Track recovery attempt (success will be tracked when user responds positively)
            self._track_recovery_success(recovery_strategy, False)  # Assume failure initially

            # Add intelligence metadata
            response.recovery_suggestions.extend([
                f"Fehlertyp: {error_type}",
                f"Recovery-Strategie: {recovery_strategy}",
                "Bei wiederholten Problemen: Support kontaktieren"
            ])

            return response

        except Exception as e:
            logger.error(f"Enhanced error recovery failed: {e}")

            # Fallback to basic recovery
            return await self._recovery_general_guidance(error_message, user_message, memory)

    def _calculate_conversation_quality(self, memory: ConversationMemory) -> float:
        """Calculate conversation quality score based on context and parameters"""

        if not memory.messages:
            return 1.0

        # Factors for quality calculation
        message_count = len(memory.messages)
        extracted_params_count = len(memory.extracted_parameters)
        context_keywords_count = len(memory.context_keywords)

        # Base quality on conversation productivity
        quality_score = min(1.0, (extracted_params_count * 0.3) +
                           (context_keywords_count * 0.1) +
                           (min(message_count, 10) * 0.05))

        return max(0.1, quality_score)  # Minimum 0.1

    def _calculate_context_understanding(self, memory: ConversationMemory) -> float:
        """Calculate how well the system understands the conversation context"""

        if not memory.messages:
            return 1.0

        # Factors for context understanding
        has_job_type_hints = len(memory.job_type_hints) > 0
        has_context_keywords = len(memory.context_keywords) > 0
        has_extracted_params = len(memory.extracted_parameters) > 0
        conversation_length = len(memory.messages)

        understanding_score = 0.0
        if has_job_type_hints:
            understanding_score += 0.3
        if has_context_keywords:
            understanding_score += 0.3
        if has_extracted_params:
            understanding_score += 0.3
        if conversation_length > 2:
            understanding_score += 0.1

        return min(1.0, understanding_score)

    # ===== SMART ERROR RECOVERY SYSTEM =====

    async def _classify_error_type(self, error_message: str, context: str) -> str:
        """Classify error type for targeted recovery strategy"""

        # Common error patterns
        error_classifications = {
            "validation": ["validation", "invalid", "format", "pattern", "required"],
            "parsing": ["parse", "json", "syntax", "decode"],
            "network": ["connection", "timeout", "network", "unreachable"],
            "llm": ["api", "quota", "rate limit", "model"],
            "session": ["session", "expired", "not found"],
            "parameter": ["parameter", "missing", "value", "type"]
        }

        error_lower = error_message.lower()

        for error_type, keywords in error_classifications.items():
            if any(keyword in error_lower for keyword in keywords):
                return error_type

        return "unknown"

    async def _select_recovery_strategy(self, error_type: str, error_message: str, context: str) -> str:
        """Select optimal recovery strategy based on error type"""

        recovery_strategies = {
            "validation": "retry_with_correction",
            "parsing": "simplify_request",
            "network": "retry_with_delay",
            "llm": "fallback_provider",
            "session": "recreate_session",
            "parameter": "guided_parameter_collection",
            "unknown": "general_guidance"
        }

        return recovery_strategies.get(error_type, "general_guidance")

    async def _execute_recovery_strategy(
        self, strategy: str, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Execute specific recovery strategy"""

        try:
            if strategy == "retry_with_correction":
                return await self._recovery_retry_with_correction(error_message, user_message, memory)

            elif strategy == "simplify_request":
                return await self._recovery_simplify_request(error_message, user_message, memory)

            elif strategy == "retry_with_delay":
                await asyncio.sleep(1)  # Brief delay for network recovery
                return await self._recovery_general_guidance(error_message, user_message, memory)

            elif strategy == "fallback_provider":
                return await self._recovery_fallback_provider(error_message, user_message, memory)

            elif strategy == "recreate_session":
                return await self._recovery_recreate_session(error_message, user_message, memory)

            elif strategy == "guided_parameter_collection":
                return await self._recovery_guided_parameters(error_message, user_message, memory)

            else:  # general_guidance
                return await self._recovery_general_guidance(error_message, user_message, memory)

        except Exception as e:
            logger.error(f"Recovery strategy execution failed: {e}")
            return await self._recovery_general_guidance(error_message, user_message, memory)

    async def _recovery_retry_with_correction(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Retry with intelligent correction suggestions"""

        try:
            llm_service = await self._get_llm_service()

            correction_prompt = f"""Ein Validierungsfehler ist aufgetreten. Analysiere und erstelle Korrekturvorschläge:

Fehler: {error_message}
Benutzer-Eingabe: {user_message}
Kontext: {memory.get_conversation_context()[:300]}

Erstelle eine hilfreiche Antwort auf Deutsch, die:
1. Den Fehler einfach erklärt
2. Konkrete Korrekturschritte vorschlägt
3. Ein korrigiertes Beispiel zeigt
4. Ermutigend formuliert ist

Halte die Antwort präzise und actionable."""

            response = await llm_service.generate(correction_prompt)

            return DialogResponse(
                content=f"🔧 {response.strip()}",
                intent=DialogIntent.ERROR_EXPLANATION,
                context=DialogContext.VALIDATION_ERROR,
                recovery_suggestions=[
                    "Eingabe korrigieren und erneut versuchen",
                    "Format-Beispiel verwenden",
                    "Alternativen Parameter verwenden"
                ],
                requires_user_input=True
            )

        except Exception as e:
            logger.warning(f"Retry with correction failed: {e}")
            return await self._recovery_general_guidance(error_message, user_message, memory)

    async def _recovery_simplify_request(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Simplify complex requests that failed parsing"""

        return DialogResponse(
            content=f"🔄 Es gab ein Problem beim Verarbeiten Ihrer Anfrage.\n\n"
                   f"Lassen Sie uns das vereinfachen. Könnten Sie Ihre Anfrage in einfacheren Worten wiederholen?\n\n"
                   f"💡 Tipp: Geben Sie Parameter einzeln an, z.B. 'Mein SAP System ist PA1_100'",
            intent=DialogIntent.CLARIFICATION,
            context=DialogContext.ACTIVE_COLLECTION,
            recovery_suggestions=[
                "Parameter einzeln angeben",
                "Einfachere Formulierung verwenden",
                "Schritt für Schritt vorgehen"
            ],
            requires_user_input=True
        )

    async def _recovery_fallback_provider(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Fallback to alternative LLM provider"""

        try:
            # Try to switch to fallback provider
            fallback_service = await get_llm_service("ollama")  # or other fallback

            simple_prompt = f"Der Benutzer sagte: '{user_message}'. Bitte antworte freundlich auf Deutsch und bitte um Klarstellung."
            response = await fallback_service.generate(simple_prompt)

            return DialogResponse(
                content=f"🔄 {response.strip()}\n\n(Hinweis: Verwende lokales Backup-System)",
                intent=DialogIntent.CLARIFICATION,
                context=DialogContext.ACTIVE_COLLECTION,
                recovery_suggestions=[
                    "Erneut versuchen",
                    "Einfachere Formulierung",
                    "Technischen Support kontaktieren"
                ],
                requires_user_input=True
            )

        except Exception as e:
            logger.warning(f"Fallback provider failed: {e}")
            return await self._recovery_general_guidance(error_message, user_message, memory)

    async def _recovery_recreate_session(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Guide user through session recreation"""

        return DialogResponse(
            content=f"🔄 Es gab ein Session-Problem. Keine Sorge, das können wir beheben!\n\n"
                   f"Lassen Sie uns eine neue Session starten. Sagen Sie mir einfach:\n"
                   f"• Welchen Job-Type möchten Sie erstellen?\n"
                   f"• Was soll der Job machen?\n\n"
                   f"Ich werde Ihnen dabei helfen, alle Parameter neu zu sammeln.",
            intent=DialogIntent.JOB_TYPE_SELECTION,
            context=DialogContext.INITIAL_GREETING,
            suggested_values=["Standard Job", "SAP Job", "File Transfer", "Custom Job"],
            recovery_suggestions=[
                "Neue Session starten",
                "Job-Type angeben",
                "Von vorn beginnen"
            ],
            requires_user_input=True
        )

    async def _recovery_guided_parameters(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """Guide user through step-by-step parameter collection"""

        return DialogResponse(
            content=f"🎯 Lassen Sie uns das Schritt für Schritt angehen.\n\n"
                   f"Ich werde Sie durch die benötigten Parameter führen:\n\n"
                   f"Schritt 1: Welchen Job-Type möchten Sie erstellen?\n"
                   f"• Standard (Script ausführen)\n"
                   f"• SAP (SAP Report)\n"
                   f"• File Transfer (Dateien kopieren)\n"
                   f"• Custom (Spezielle Anforderungen)\n\n"
                   f"Wählen Sie einfach eine Option aus.",
            intent=DialogIntent.JOB_TYPE_SELECTION,
            context=DialogContext.JOB_TYPE_DECISION,
            suggested_values=["Standard", "SAP", "File Transfer", "Custom"],
            recovery_suggestions=[
                "Job-Type wählen",
                "Schritt für Schritt vorgehen",
                "Bei Fragen nachfragen"
            ],
            requires_user_input=True
        )

    async def _recovery_general_guidance(
        self, error_message: str, user_message: str, memory: ConversationMemory
    ) -> DialogResponse:
        """General recovery guidance when specific strategies fail"""

        return DialogResponse(
            content=f"🤝 Entschuldigung, es gab einen technischen Fehler.\n\n"
                   f"Aber keine Sorge - ich bin hier, um Ihnen zu helfen!\n\n"
                   f"Lassen Sie uns einfach weitermachen. Was möchten Sie als nächstes tun?\n\n"
                   f"💡 Optionen:\n"
                   f"• 'Neue Session' - Frisch starten\n"
                   f"• 'Hilfe' - Verfügbare Kommandos\n"
                   f"• Beschreiben Sie einfach, was Sie erreichen möchten",
            intent=DialogIntent.CLARIFICATION,
            context=DialogContext.INITIAL_GREETING,
            suggested_values=["Neue Session", "Hilfe", "Status"],
            recovery_suggestions=[
                "Frisch starten",
                "Hilfe anfordern",
                "Problem beschreiben"
            ],
            requires_user_input=True
        )

    def _track_recovery_success(self, strategy: str, was_successful: bool):
        """Track recovery strategy success rates for learning"""

        if not hasattr(self, 'recovery_metrics'):
            self.recovery_metrics = {
                "total_recoveries": 0,
                "successful_recoveries": 0,
                "strategy_success_rates": {}
            }

        self.recovery_metrics["total_recoveries"] += 1
        if was_successful:
            self.recovery_metrics["successful_recoveries"] += 1

        if strategy not in self.recovery_metrics["strategy_success_rates"]:
            self.recovery_metrics["strategy_success_rates"][strategy] = {"attempts": 0, "successes": 0}

        self.recovery_metrics["strategy_success_rates"][strategy]["attempts"] += 1
        if was_successful:
            self.recovery_metrics["strategy_success_rates"][strategy]["successes"] += 1

    def get_recovery_metrics(self) -> Dict[str, Any]:
        """Get error recovery performance metrics"""

        if not hasattr(self, 'recovery_metrics'):
            return {"recovery_system": "not_used_yet"}

        metrics = dict(self.recovery_metrics)

        # Calculate success rates
        for strategy, data in metrics["strategy_success_rates"].items():
            if data["attempts"] > 0:
                success_rate = data["successes"] / data["attempts"]
                data["success_rate"] = round(success_rate, 3)

        overall_success_rate = 0
        if metrics["total_recoveries"] > 0:
            overall_success_rate = metrics["successful_recoveries"] / metrics["total_recoveries"]

        metrics["overall_success_rate"] = round(overall_success_rate, 3)

        return metrics

    async def _handle_fallback_response(self, session_id: str, user_message: str, context: DialogContext) -> DialogResponse:
        """Behandelt unerwartete Situationen mit Fallback-Antworten"""
        return DialogResponse(
            content="🤔 Entschuldigung, ich konnte Ihre Anfrage nicht verstehen.\n\n"
                   "Verfügbare Kommandos:\n"
                   "• 'Neue Session' - Startet XML-Generierung\n"
                   "• 'Hilfe' - Zeigt verfügbare Optionen\n"
                   "• 'Status' - Zeigt aktuellen Session-Status",
            intent=DialogIntent.CLARIFICATION,
            context=context,
            suggested_values=["Neue Session", "Hilfe", "Status"]
        )

    def _load_dialog_prompts(self) -> Dict[str, str]:
        """Lädt Dialog-Prompt-Templates"""
        return {
            "welcome": "Willkommen beim StreamWorks XML-Generator! Ich helfe Ihnen bei der Erstellung von XML-Konfigurationen.",
            "job_type_selection": "Welchen Job-Type möchten Sie erstellen?",
            "parameter_collection": "Bitte geben Sie den Wert für {parameter} an:",
            "validation_error": "Der eingegebene Wert ist ungültig: {error}",
            "completion": "XML wurde erfolgreich generiert!"
        }

# Singleton instance
_dialog_manager = None

def get_dialog_manager() -> DialogManager:
    """Get dialog manager singleton"""
    global _dialog_manager
    if _dialog_manager is None:
        _dialog_manager = DialogManager()
    return _dialog_manager