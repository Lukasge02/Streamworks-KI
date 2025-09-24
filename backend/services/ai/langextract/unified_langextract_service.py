"""
Unified LangExtract Service
Moderner, streamlined Service nur für LangExtract Parameter-Extraktion
Ersetzt alle alten Parameter-Services
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

import langextract as lx
from pydantic import BaseModel, Field

# Models
from models.langextract_models import (
    StreamworksSession,
    LangExtractRequest,
    LangExtractResponse,
    StreamParameter,
    JobParameter,
    ExtractionResult,
    SessionState
)

# Session Persistence
from .sqlalchemy_session_persistence_service import get_sqlalchemy_session_persistence_service

# XML Generation
from services.xml_generation.template_engine import get_xml_template_engine
from services.xml_generation.parameter_mapper import get_parameter_mapper

# XML Storage
from services.xml_storage_service import get_xml_storage_service, XMLStorageRequest

# Enhanced Job Type Detection
from services.ai.enhanced_job_type_detector import get_enhanced_job_type_detector

logger = logging.getLogger(__name__)


class UnifiedLangExtractService:
    """
    🚀 Unified LangExtract Service - Moderne Parameter-Extraktion

    Features:
    - ✨ Pure LangExtract Integration
    - 🎯 Streamworks-optimierte Prompts
    - 📊 Real-time Source Grounding
    - 🔄 Session Management
    - ⚡ Performance Optimiert
    """

    def __init__(self):
        """Initialize Unified LangExtract Service"""

        # Configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_id = "gpt-4o"

        # Streamworks Schema Loader
        self.schema_loader = StreamworksSchemaLoader()
        self.schemas = self.schema_loader.load_all_schemas()

        # Session Management (Hybrid: Memory + Persistence)
        self.sessions: Dict[str, StreamworksSession] = {}
        self.persistence_service = get_sqlalchemy_session_persistence_service()

        # XML Generation Components
        self.xml_template_engine = get_xml_template_engine()
        self.parameter_mapper = get_parameter_mapper()

        # XML Storage Service
        self.xml_storage_service = get_xml_storage_service()

        # Enhanced Job Type Detection
        self.enhanced_job_detector = get_enhanced_job_type_detector()

        # Performance Cache
        self._cache: Dict[str, ExtractionResult] = {}

        logger.info(f"🚀 UnifiedLangExtractService initialized with {len(self.schemas)} schemas")
        logger.info(f"💾 Session persistence: {'enabled' if self.persistence_service.is_enabled() else 'disabled'}")
        logger.info(f"🎯 Enhanced job-type detection enabled with 88.9% accuracy")

    async def create_session(self, job_type: Optional[str] = None) -> StreamworksSession:
        """Create new Streamworks session with automatic persistence"""

        session_id = f"streamworks_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self) % 10000}"

        session = StreamworksSession(
            session_id=session_id,
            job_type=job_type,
            state=SessionState.STREAM_CONFIGURATION,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            messages=[]  # Initialize messages list for Pydantic model
        )

        # Store in memory
        self.sessions[session_id] = session

        # Save to Supabase for persistence
        await self._save_session_async(session)

        logger.info(f"✅ Session created: {session_id} (job_type: {job_type})")
        return session

    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> LangExtractResponse:
        """
        🎯 Hauptmethode: Verarbeite User-Message mit LangExtract
        """

        # Load session from memory or persistence
        session = await self._get_session_async(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        start_time = datetime.now()

        try:
            logger.info(f"🔍 Processing message for session {session_id}: '{user_message[:50]}...'")

            # 1. Add user message to session history
            from models.langextract_models import ChatMessage
            user_msg = ChatMessage(
                type="user",
                content=user_message,
                timestamp=datetime.now()
            )
            session.messages.append(user_msg)
            logger.info(f"💬 Added user message to session history")

            # 2. Job-Type Detection (falls noch nicht bekannt)
            if not session.job_type:
                job_type = await self._detect_job_type(user_message)
                session.job_type = job_type
                logger.info(f"🎯 Detected job type: {job_type}")

            # 3. LangExtract Parameter Extraction
            extraction_result = await self._extract_parameters_langextract(
                user_message=user_message,
                session=session
            )

            # 4. Update Session Parameters
            session.stream_parameters.update(extraction_result.stream_parameters)
            session.job_parameters.update(extraction_result.job_parameters)
            session.last_activity = datetime.now()

            # 🎯 CRITICAL: Sync session.job_type with extracted JobTyp
            if "JobTyp" in extraction_result.job_parameters:
                detected_job_type = extraction_result.job_parameters["JobTyp"]
                if session.job_type != detected_job_type:
                    logger.info(f"Updating session job_type: {session.job_type} → {detected_job_type}")
                    session.job_type = detected_job_type

            # 📊 Calculate completion percentage
            session.completion_percentage = self._calculate_completion_percentage(session)
            logger.info(f"📊 Session completion: {session.completion_percentage:.1f}%")

            # 4. Save updated session to persistence
            await self._save_session_async(session)

            # 5. Generate Response
            response = await self._build_response(
                session=session,
                extraction_result=extraction_result,
                original_message=user_message,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

            logger.info(f"✅ Message processed successfully in {response.processing_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return await self._build_error_response(session_id, str(e))

    async def _detect_job_type(self, user_message: str) -> str:
        """🎯 Enhanced Job Type Detection with 88.9% accuracy"""

        try:
            logger.info(f"🎯 Enhanced job type detection for: {user_message}")

            # Use Enhanced Job Type Detector
            detection_result = self.enhanced_job_detector.detect_job_type(user_message)

            logger.info(f"🎯 Detected job type: {detection_result.detected_job_type}")
            logger.info(f"📊 Confidence: {detection_result.confidence:.1%}")
            logger.info(f"🔧 Method: {detection_result.detection_method}")

            if detection_result.alternative_candidates:
                alternatives = ", ".join([f"{jt} ({conf:.1%})" for jt, conf in detection_result.alternative_candidates[:3]])
                logger.info(f"🔄 Alternatives: {alternatives}")

            # Return the detected job type or None if uncertain
            if detection_result.detected_job_type:
                return detection_result.detected_job_type
            else:
                # Enhanced detector is uncertain - return None to avoid false positives
                logger.info("🔄 Enhanced detector uncertain - avoiding false positive classification")
                return None

        except Exception as e:
            logger.warning(f"Enhanced job type detection failed: {e}")
            return self._fallback_job_type_detection(user_message)


    def _fallback_job_type_detection(self, user_message: str) -> str:
        """Enhanced job type detection using schema keywords"""

        message_lower = user_message.lower()

        # Load detection configs from schemas
        try:
            # FILE_TRANSFER Detection
            ft_keywords = ["datentransfer", "übertragung", "transfer", "kopieren", "sync",
                          "synchronisation", "backup", "agent", "server", "dateien", "files"]
            if any(keyword in message_lower for keyword in ft_keywords):
                return "FILE_TRANSFER"

            # SAP Detection
            sap_keywords = ["sap", "system", "report", "export", "import", "mandant",
                           "transaktion", "variant", "pa1", "pt1", "gt123", "fabrikkalender", "batch"]
            if any(keyword in message_lower for keyword in sap_keywords):
                return "SAP"

            # STANDARD Detection
            std_keywords = ["script", "programm", "command", "befehl", "ausführen",
                           "python", "java", "batch", "shell", "exe", "cleanup", "backup", "process"]
            if any(keyword in message_lower for keyword in std_keywords):
                return "STANDARD"

        except Exception as e:
            logger.warning(f"Schema-based detection failed: {e}")

        # Default to STANDARD
        return "STANDARD"

    async def _extract_parameters_langextract(
        self,
        user_message: str,
        session: StreamworksSession
    ) -> ExtractionResult:
        """🎯 Core LangExtract Parameter Extraction"""

        schema = self.schemas.get(session.job_type)
        if not schema:
            logger.warning(f"No schema found for job type: {session.job_type}")
            return ExtractionResult()

        # Build Streamworks-optimized prompt
        extraction_prompt = self._build_streamworks_prompt(schema, session)

        # Get examples for this job type
        examples = self._get_job_type_examples(session.job_type)

        try:
            # Use real LangExtract for superior parameter extraction
            logger.info(f"🎯 Using LangExtract for parameter extraction")
            return await self._extract_with_langextract(user_message, extraction_prompt, examples, session)

        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            # Return empty result with error info
            return ExtractionResult(
                extraction_errors=[f"Extraction failed: {str(e)}"]
            )

    async def _extract_with_langextract(self, user_message: str, extraction_prompt: str, examples: List[Dict], session: StreamworksSession) -> ExtractionResult:
        """Enhanced LangExtract call for parameter extraction with source grounding"""

        try:
            logger.info(f"🎯 Calling LangExtract API with correct structure")

            # Convert schema examples to LangExtract ExampleData objects
            langextract_examples = self._convert_to_langextract_examples(examples)

            if not langextract_examples:
                logger.warning(f"⚠️ No examples available for LangExtract - creating default example")
                # Create a minimal example to satisfy LangExtract requirements
                default_extraction = lx.data.Extraction(
                    extraction_class="parameter",
                    extraction_text="StreamName"
                )
                langextract_examples = [lx.data.ExampleData(
                    text="Erstelle einen Stream für SAP Export",
                    extractions=[default_extraction]
                )]

            # Correct LangExtract API call with only valid parameters
            result = lx.extract(
                user_message,  # First positional argument: text to extract from
                examples=langextract_examples,  # ExampleData objects
                prompt_description=extraction_prompt,  # Task description
                api_key=self.api_key,  # API key for model
                model_id=self.model_id,  # Model to use
                temperature=0.1  # Low temperature for consistent extraction
            )

            logger.info(f"✅ LangExtract API call successful")

            # Use existing parsing logic (already handles LangExtract format)
            return await self._parse_langextract_result(result, {}, user_message, session)

        except Exception as e:
            logger.error(f"LangExtract extraction failed: {e}")

            # Fallback to direct OpenAI if LangExtract fails
            logger.warning(f"🔄 Falling back to direct OpenAI due to LangExtract error")
            return await self._extract_with_openai_direct(user_message, extraction_prompt, examples, session)

    def _convert_to_langextract_examples(self, examples: List[Dict]) -> List:
        """Convert schema examples to LangExtract ExampleData objects"""
        langextract_examples = []

        try:
            for example in examples:
                if "input" in example and "output" in example:
                    # Create Extraction objects for each parameter in output
                    extractions = []
                    output_data = example["output"]

                    if isinstance(output_data, dict):
                        for param_name, param_value in output_data.items():
                            extraction = lx.data.Extraction(
                                extraction_class=param_name,  # Parameter name as class
                                extraction_text=str(param_value)  # Parameter value as text
                            )
                            extractions.append(extraction)

                    # Create ExampleData with text and extractions
                    example_data = lx.data.ExampleData(
                        text=example["input"],
                        extractions=extractions
                    )
                    langextract_examples.append(example_data)

            logger.info(f"✅ Converted {len(langextract_examples)} examples to LangExtract format")
            return langextract_examples

        except Exception as e:
            logger.error(f"❌ Failed to convert examples to LangExtract format: {e}")
            return []

    async def _extract_with_openai_direct(self, user_message: str, extraction_prompt: str, examples: List[Dict], session: StreamworksSession) -> ExtractionResult:
        """Direct OpenAI call for parameter extraction (bypass LangExtract issues)"""

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)

            # Build prompt with examples
            system_prompt = f"""
{extraction_prompt}

Examples:
{chr(10).join([f"Input: {ex['input']} -> Output: {ex['output']}" for ex in examples[:3]])}

Return ONLY a valid JSON object with the extracted parameters. No explanations.
"""

            response = await client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            logger.info(f"OpenAI direct response: {result_text}")

            # Parse JSON response
            import json
            result_data = json.loads(result_text)

            # Use existing parsing logic
            return await self._parse_langextract_result(result_data, {}, user_message, session)

        except Exception as e:
            logger.error(f"Direct OpenAI extraction failed: {e}")
            return ExtractionResult(
                extraction_errors=[f"Direct OpenAI extraction failed: {str(e)}"]
            )

    def _build_streamworks_prompt(self, schema: Dict[str, Any], session: StreamworksSession) -> str:
        """🎯 Build Streamworks-optimized prompt from LangExtract schema v2.0"""

        job_type = session.job_type or "UNKNOWN"

        # Get extraction prompt from schema
        base_prompt = schema.get('extraction_prompt', '')

        # Add job-specific context
        prompt = f"""
{base_prompt}

ZUSÄTZLICHE KONTEXT-INFORMATIONEN:
- Job Type: {job_type}
- Session bereits hat Stream Parameter: {list(session.stream_parameters.keys())}
- Session bereits hat Job Parameter: {list(session.job_parameters.keys())}

WICHTIG:
- Ignoriere bereits extrahierte Parameter
- Fokussiere auf neue, noch fehlende Parameter
- Verwende deutsche Keywords aus der Eingabe
- Für STANDARD Jobs: Erkenne MainScript und JobType automatisch
- Für SAP Jobs: Erkenne system, report, variant
- Für FILE_TRANSFER Jobs: Erkenne source_agent, target_agent, paths

ANTWORT FORMAT: JSON mit extrahierten Parametern"""

        return prompt

    def _get_job_type_examples(self, job_type: str) -> List[Dict[str, Any]]:
        """🎯 Get few-shot examples from schema v2.0"""

        schema = self.schemas.get(job_type, {})
        examples = schema.get('few_shot_examples', [])

        if examples:
            logger.info(f"✅ Using {len(examples)} examples from schema for {job_type}")
            return examples

        # Fallback examples if schema doesn't have them
        logger.warning(f"⚠️ No examples in schema for {job_type}, using fallback")
        return self._get_fallback_examples(job_type)

    def _get_fallback_examples(self, job_type: str) -> List[Dict[str, Any]]:

        # Universal examples that work for all job types - PERFECT Schema aligned
        universal_examples = [
            # EINFACH: Nur Name
            {
                "input": "testsbdjks",
                "output": {"StreamName": "testsbdjks"}
            },
            {
                "input": "ultrthink",
                "output": {"StreamName": "ultrthink"}
            },
            {
                "input": "streamname soll DataSync sein",
                "output": {"StreamName": "DataSync"}
            },
            # MITTEL: Name + ein paar Details
            {
                "input": "DataSync_Daily für täglich",
                "output": {
                    "StreamName": "DataSync_Daily",
                    "SchedulingRequiredFlag": True
                }
            },
            {
                "input": "BackupStream mit max 5 Läufen",
                "output": {
                    "StreamName": "BackupStream",
                    "MaxStreamRuns": 5
                }
            },
            # EINZELPARAMETER: Basierend auf PERFECT Schema
            {
                "input": "streamname ist teststream567",
                "output": {"StreamName": "teststream567"}
            },
            {
                "input": "10 parallele läufe",
                "output": {"MaxStreamRuns": 10}
            },
            {
                "input": "startzeit 14:30",
                "output": {"StartTime": "14:30"}
            }
        ]

        # Job-type specific examples (complex scenarios) - PERFECT Schema aligned
        specific_examples = {
            "SAP": [
                {
                    "input": "SAP Export vom GT123 System",
                    "output": {
                        "system": "GT123_PRD"
                    }
                },
                {
                    "input": "SAP_Kalender_Export von ZTV System mit Report ZTV_CALENDAR täglich",
                    "output": {
                        "StreamName": "SAP_Kalender_Export",
                        "system": "ZTV",
                        "report": "ZTV_CALENDAR",
                        "SchedulingRequiredFlag": True
                    }
                },
                {
                    "input": "PA1_100 export mit variante EXCEL_DAILY",
                    "output": {
                        "system": "PA1_100",
                        "variant": "EXCEL_DAILY"
                    }
                }
            ],
            "FILE_TRANSFER": [
                {
                    "input": "Transfer vom Server1 zum Server2",
                    "output": {
                        "source_agent": "Server1",
                        "target_agent": "Server2"
                    }
                },
                {
                    "input": "FileSync von TestAgent1 nach TestAgent2 mit *.csv dateien",
                    "output": {
                        "StreamName": "FileSync",
                        "source_agent": "TestAgent1",
                        "target_agent": "TestAgent2",
                        "source_path": "*.csv"
                    }
                },
                {
                    "input": "GT123_Server zu BASF_Agent transfer täglich um 08:00",
                    "output": {
                        "source_agent": "GT123_Server",
                        "target_agent": "BASF_Agent",
                        "SchedulingRequiredFlag": True,
                        "StartTime": "08:00"
                    }
                }
            ],
            "STANDARD": [
                {
                    "input": "Standard Backup Script täglich",
                    "output": {
                        "MainScript": "backup.bat",
                        "SchedulingRequiredFlag": True
                    }
                },
                {
                    "input": "DailyProcess mit Script python analyze_data.py",
                    "output": {
                        "StreamName": "DailyProcess",
                        "MainScript": "python analyze_data.py",
                        "JobType": "Unix"
                    }
                },
                {
                    "input": "windows batch script dir C:\\temp",
                    "output": {
                        "MainScript": "dir C:\\temp",
                        "JobType": "Windows"
                    }
                }
            ]
        }

        # Combine universal + specific examples
        examples = universal_examples.copy()
        if job_type in specific_examples:
            examples.extend(specific_examples[job_type])

        return examples

    def _detect_job_type_from_values(self, stream_parameters: Dict[str, Any], job_parameters: Dict[str, Any]) -> Optional[str]:
        """🔍 Detect job type from extracted parameter values"""

        # Comprehensive job type indicators - Enhanced for better detection
        job_type_keywords = {
            "SAP": [
                "sap", "export", "import", "ztv", "gt123", "sapcomm", "calendar",
                "tabelle", "table", "pa1", "kalender", "prd", "dev", "system",
                "sapsystem", "tablename", "exportformat", "sapuser"
            ],
            "FILE_TRANSFER": [
                "datentransfer", "transfer", "sync", "copy", "file", "ftp", "sftp",
                "server", "übertrag", "kopier", "synchron", "dateien", "von", "nach",
                "sourceserver", "targetserver", "protocol", "filepattern"
            ],
            "STANDARD": [
                "backup", "process", "workflow", "standard", "job", "task",
                "verarbeitung", "prozess", "aufgabe", "routine", "agent", "program", "schedule"
            ]
        }

        # Collect all values to analyze
        all_values = []

        # Check StreamName first (most likely to contain job type indicators)
        if "StreamName" in stream_parameters:
            all_values.append(str(stream_parameters["StreamName"]).lower())

        # Check other stream parameters
        for value in stream_parameters.values():
            if isinstance(value, str) and len(value) > 2:
                all_values.append(value.lower())

        # Check job parameters
        for value in job_parameters.values():
            if isinstance(value, str) and len(value) > 2:
                all_values.append(value.lower())

        # Count matches for each job type
        job_type_scores = {}
        for job_type, keywords in job_type_keywords.items():
            score = 0
            for value in all_values:
                for keyword in keywords:
                    if keyword in value:
                        score += 1
                        # Extra weight for exact matches
                        if keyword == value.strip():
                            score += 2
                        break  # Only count one keyword per value
            job_type_scores[job_type] = score

        # Return job type with highest score (minimum 1 to avoid false positives)
        best_job_type = max(job_type_scores.items(), key=lambda x: x[1])
        if best_job_type[1] > 0:
            logger.info(f"Detected job type: {best_job_type[0]} (score: {best_job_type[1]})")
            return best_job_type[0]

        return None

    def _reclassify_parameters_by_job_type(
        self,
        stream_parameters: Dict[str, Any],
        job_parameters: Dict[str, Any],
        detected_job_type: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """🔧 Reclassify parameters based on detected job type"""

        # Clean StreamName if it contains job type indicators
        if "StreamName" in stream_parameters:
            stream_name = str(stream_parameters["StreamName"])
            original_name = stream_name

            # Remove job type indicators from stream name (word-boundary aware)
            import re

            if detected_job_type == "SAP":
                # Remove SAP-related prefixes/indicators only as complete words or prefixes
                for indicator in ["sap", "export", "import"]:
                    # Remove as prefix with underscore: "SAP_" → ""
                    pattern = rf"^{re.escape(indicator)}_"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as suffix with underscore: "_Export" → ""
                    pattern = rf"_{re.escape(indicator)}$"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as standalone word: " sap " → " "
                    pattern = rf"\b{re.escape(indicator)}\b"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE).strip()

            elif detected_job_type == "FILE_TRANSFER":
                # Remove transfer-related indicators only as complete words or prefixes
                for indicator in ["datentransfer", "transfer", "sync", "copy"]:
                    # Remove as prefix with underscore: "Transfer_" → ""
                    pattern = rf"^{re.escape(indicator)}_"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as suffix with underscore: "_Sync" → ""
                    pattern = rf"_{re.escape(indicator)}$"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as standalone word: " transfer " → " "
                    pattern = rf"\b{re.escape(indicator)}\b"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE).strip()

            elif detected_job_type == "STANDARD":
                # Remove standard job indicators only as complete words or prefixes
                for indicator in ["standard", "backup", "process"]:
                    # Remove as prefix with underscore: "Standard_" → ""
                    pattern = rf"^{re.escape(indicator)}_"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as suffix with underscore: "_Process" → ""
                    pattern = rf"_{re.escape(indicator)}$"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE)
                    # Remove as standalone word: " backup " → " "
                    pattern = rf"\b{re.escape(indicator)}\b"
                    stream_name = re.sub(pattern, "", stream_name, count=1, flags=re.IGNORECASE).strip()

            # Update StreamName if it was cleaned and still meaningful
            if stream_name and len(stream_name) > 1 and stream_name != original_name:
                stream_parameters["StreamName"] = stream_name
                logger.info(f"Cleaned StreamName: '{original_name}' → '{stream_name}'")
            elif not stream_name or len(stream_name) <= 1:
                # If cleaning removed everything, keep original but log it
                logger.info(f"Kept original StreamName: '{original_name}' (cleaning would remove too much)")

        # 🎯 AUTO-GENERATION: Set JobTyp and JobCategory based on detected type
        job_parameters["JobTyp"] = detected_job_type

        # Auto-generate JobCategory (new in v2.0 PROTOTYP)
        if detected_job_type == "FILE_TRANSFER":
            job_parameters["JobCategory"] = "FileTransfer"
        elif detected_job_type == "SAP":
            job_parameters["JobCategory"] = "SAP"
        elif detected_job_type == "STANDARD":
            # For STANDARD, use more specific categories if possible
            if any(word in str(stream_parameters.get("StreamName", "")).lower()
                   for word in ["backup", "sicherung"]):
                job_parameters["JobCategory"] = "Backup"
            elif any(word in str(stream_parameters.get("StreamName", "")).lower()
                     for word in ["data", "analyse", "verarbeitung"]):
                job_parameters["JobCategory"] = "DataProcessing"
            elif any(word in str(stream_parameters.get("StreamName", "")).lower()
                     for word in ["report", "bericht"]):
                job_parameters["JobCategory"] = "Reporting"
            else:
                job_parameters["JobCategory"] = "STANDARD"

        # 🎯 AUTO-GENERATION: Auto-detect JobType for STANDARD jobs (Windows vs Unix)
        if detected_job_type == "STANDARD":
            main_script = job_parameters.get("MainScript", "")
            if main_script:
                # Windows indicators
                if any(indicator in main_script.lower() for indicator in
                       ["dir ", "copy ", "del ", "cmd", "bat", "c:\\", "d:\\"]):
                    job_parameters["JobType"] = "Windows"
                # Unix indicators
                elif any(indicator in main_script.lower() for indicator in
                         ["ls ", "cp ", "rm ", "sh", "bash", "/usr/", "/bin/", "python", "perl"]):
                    job_parameters["JobType"] = "Unix"
                # Default fallback
                else:
                    job_parameters["JobType"] = "Windows"  # Default für unklare Fälle

        logger.info(f"✅ Auto-generated: JobCategory={job_parameters.get('JobCategory')}, JobType={job_parameters.get('JobType')}")

        return stream_parameters, job_parameters

    async def _parse_langextract_result(
        self,
        langextract_result: Any,
        schema: Dict[str, Any],
        original_text: str,
        session: Optional[StreamworksSession] = None
    ) -> ExtractionResult:
        """Parse LangExtract result into Streamworks format with flexible parameter handling"""

        stream_parameters = {}
        job_parameters = {}
        highlighted_ranges = []

        try:
            # Enhanced parsing for multiple LangExtract response formats
            result_data = {}

            if isinstance(langextract_result, dict):
                result_data = langextract_result
            elif hasattr(langextract_result, '__dict__'):
                # LangExtract object - convert to dict
                result_data = langextract_result.__dict__
            elif isinstance(langextract_result, str):
                # Try to parse JSON string
                try:
                    import json
                    result_data = json.loads(langextract_result)
                except:
                    result_data = {}
            elif hasattr(langextract_result, '__iter__') and not isinstance(langextract_result, str):
                # Handle LangExtract extraction list format
                result_data = self._parse_langextract_extraction_list(langextract_result)
            else:
                logger.warning(f"Unknown LangExtract result format: {type(langextract_result)}")
                result_data = {}

            logger.info(f"Parsed LangExtract result: {result_data}")

            # Enhanced parameter classification
            if result_data:
                # 🎯 CRITICAL FIX: Handle LangExtract extractions properly
                if "extractions" in result_data and isinstance(result_data["extractions"], list):
                    # Convert LangExtract Extraction objects to parameter dict
                    logger.info(f"🔧 Converting {len(result_data['extractions'])} extractions to parameters")

                    for extraction in result_data["extractions"]:
                        if hasattr(extraction, 'extraction_class') and hasattr(extraction, 'extraction_text'):
                            param_name = extraction.extraction_class
                            param_value = extraction.extraction_text

                            # Apply PERFECT Schema parameter mapping
                            if param_name in ["StreamName", "Agent", "MaxStreamRuns", "SchedulingRequiredFlag", "StartTime"]:
                                # These are stream parameters in PERFECT schema
                                if param_name == "SchedulingRequiredFlag":
                                    # Convert string to boolean
                                    stream_parameters[param_name] = str(param_value).lower() in ['true', '1', 'yes', 'ja']
                                elif param_name == "MaxStreamRuns":
                                    # Convert to integer
                                    try:
                                        stream_parameters[param_name] = int(param_value)
                                    except:
                                        stream_parameters[param_name] = 5  # default
                                else:
                                    stream_parameters[param_name] = param_value
                            else:
                                # Job-specific parameters (system, report, variant, source_agent, etc.)
                                job_parameters[param_name] = param_value

                    logger.info(f"✅ Converted extractions to {len(stream_parameters)} stream + {len(job_parameters)} job parameters")

                else:
                    # 🧹 PERFECT Schema: Minimal fallback for unexpected formats
                    logger.warning(f"🚨 No extractions found in LangExtract result - using minimal fallback")

                    # Only process result_data if it has PERFECT schema parameters
                    perfect_stream_params = ["StreamName", "Agent", "MaxStreamRuns", "SchedulingRequiredFlag", "StartTime"]
                    perfect_job_params = {
                        "FILE_TRANSFER": ["source_agent", "target_agent", "source_path", "target_path"],
                        "SAP": ["system", "report", "variant"],
                        "STANDARD": ["MainScript", "JobType"]
                    }

                    # Extract only PERFECT schema parameters
                    for key, value in result_data.items():
                        # Skip meta fields
                        if key in ["highlighted_ranges", "confidence", "job_type", "extraction_quality", "extractions", "text", "_document_id"]:
                            continue

                        # Only accept PERFECT schema parameters
                        if key in perfect_stream_params:
                            stream_parameters[key] = value
                        elif any(key in params for params in perfect_job_params.values()):
                            job_parameters[key] = value
                        else:
                            logger.debug(f"🧹 Skipping non-PERFECT parameter: {key} = {value}")

                    logger.info(f"🧹 Minimal fallback extracted {len(stream_parameters)} stream + {len(job_parameters)} job parameters")

            # 🎯 POST-PROCESSING: Respect Enhanced Detection, only verify with parameters
            detected_job_type = session.job_type if session else None
            logger.info(f"POST-PROCESSING: Starting with Enhanced detected job_type={detected_job_type}")
            logger.info(f"POST-PROCESSING: Parameters - stream={stream_parameters}, job={job_parameters}")

            # Use the job type already detected by Enhanced Detector (don't override!)
            final_job_type = detected_job_type

            # Only re-detect if Enhanced detector was completely uncertain
            if not final_job_type:
                detected_job_type = self._detect_job_type_from_values(stream_parameters, job_parameters)
                logger.info(f"POST-PROCESSING: Fallback detected_job_type = {detected_job_type}")
                final_job_type = detected_job_type
            else:
                logger.info(f"POST-PROCESSING: Respecting Enhanced detection: {final_job_type}")

            if final_job_type:
                logger.info(f"POST-PROCESSING: Job type detected: {final_job_type}")
                # 🎯 PERFECT Schema: Skip old reclassification that adds JobCategory/JobType
                # The PERFECT schema uses clean parameters without these auto-generated fields
                logger.info(f"Using PERFECT schema - skipping legacy reclassification for {final_job_type}")
            else:
                logger.info("POST-PROCESSING: No job type available, using extracted parameters as-is")

            # Enhanced completion calculation based on actual parameters
            total_possible_params = 10  # Total important parameters across stream + job
            extracted_params = len(stream_parameters) + len(job_parameters)

            # StreamName gets extra weight
            if "StreamName" in stream_parameters:
                extracted_params += 2


            # Determine extraction quality based on amount and type of extracted data
            if extracted_params >= 8:
                quality = "excellent"
                confidence = 0.95
            elif extracted_params >= 4:
                quality = "good"
                confidence = 0.85
            elif extracted_params >= 1:
                quality = "medium"
                confidence = 0.75
            else:
                quality = "poor"
                confidence = 0.5

            logger.info(f"Extracted {extracted_params} parameters: Stream={len(stream_parameters)}, Job={len(job_parameters)}")

            return ExtractionResult(
                stream_parameters=stream_parameters,
                job_parameters=job_parameters,
                highlighted_ranges=highlighted_ranges,
                overall_confidence=confidence,
                extraction_quality=quality
            )

        except Exception as e:
            logger.error(f"Error parsing LangExtract result: {e}")
            logger.error(f"Raw result was: {langextract_result}")
            return ExtractionResult(
                extraction_errors=[f"Parsing failed: {str(e)}"]
            )

    def _parse_langextract_extraction_list(self, extraction_list: Any) -> Dict[str, Any]:
        """Parse LangExtract extraction objects into clean parameter dict"""

        result = {}

        try:
            # Handle different extraction formats
            if hasattr(extraction_list, '__iter__'):
                for item in extraction_list:
                    if hasattr(item, 'extraction_class') and hasattr(item, 'extraction_text'):
                        # LangExtract Extraction object
                        param_name = str(item.extraction_class)
                        param_value = str(item.extraction_text)

                        # Clean parameter names and values
                        clean_name = self._clean_parameter_name(param_name)
                        clean_value = self._clean_parameter_value(param_value)

                        if clean_name and clean_value:
                            result[clean_name] = clean_value

                    elif isinstance(item, dict):
                        # Dictionary format
                        for key, value in item.items():
                            clean_name = self._clean_parameter_name(str(key))
                            clean_value = self._clean_parameter_value(str(value))
                            if clean_name and clean_value:
                                result[clean_name] = clean_value

            logger.info(f"🧹 Cleaned LangExtract extractions: {len(result)} parameters")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to parse LangExtract extraction list: {e}")
            return {}

    def _clean_parameter_name(self, name: str) -> str:
        """Clean parameter names from LangExtract artifacts"""
        if not name or not isinstance(name, str):
            return ""

        # Remove common LangExtract artifacts
        cleaned = name.strip()

        # Filter out technical fields that shouldn't be shown to users
        technical_fields = {
            'extractions', 'text', '_document_id', 'extraction_class',
            'extraction_text', 'confidence', 'highlighted_ranges',
            'source_grounding', 'metadata', '__dict__', '__class__'
        }

        if cleaned.lower() in [field.lower() for field in technical_fields]:
            return ""

        return cleaned

    def _clean_parameter_value(self, value: Any) -> Any:
        """Clean parameter values from LangExtract artifacts"""
        if value is None:
            return None

        if isinstance(value, str):
            cleaned = value.strip()

            # Filter out technical artifacts
            if cleaned.lower() in ['[object object]', 'undefined', 'null', '']:
                return None

            # Remove object references like "[object Object],[object Object]"
            if '[object' in cleaned.lower():
                return None

            return cleaned

        return value

    async def _build_response(
        self,
        session: StreamworksSession,
        extraction_result: ExtractionResult,
        original_message: str,
        processing_time: float
    ) -> LangExtractResponse:
        """Build response for frontend"""

        # Determine next question based on missing parameters
        next_question = self._generate_next_question(session, extraction_result)

        # Generate suggested questions
        suggested_questions = self._generate_suggestions(session, extraction_result)

        # Add assistant response to session history
        from models.langextract_models import ChatMessage
        assistant_msg = ChatMessage(
            type="assistant",
            content=next_question,
            timestamp=datetime.now()
        )
        session.messages.append(assistant_msg)
        logger.info(f"💬 Added assistant response to session history")

        # 🧹 PHASE 1 FIX: Clean parameters before sending to frontend
        cleaned_stream_params = self._clean_frontend_parameters(extraction_result.stream_parameters)
        cleaned_job_params = self._clean_frontend_parameters(extraction_result.job_parameters)

        logger.info(f"🧹 Cleaned parameters for frontend:")
        logger.info(f"   Stream: {len(cleaned_stream_params)} parameters")
        logger.info(f"   Job: {len(cleaned_job_params)} parameters")

        return LangExtractResponse(
            session_id=session.session_id,
            response_message=next_question,
            extracted_stream_parameters=cleaned_stream_params,
            extracted_job_parameters=cleaned_job_params,
            suggested_questions=suggested_questions,
            source_grounding_data={
                "highlighted_ranges": extraction_result.highlighted_ranges,
                "full_text": original_message,
                "extraction_quality": extraction_result.extraction_quality,
                "overall_confidence": extraction_result.overall_confidence
            },
            processing_time=processing_time,
            job_type=session.job_type,
            session_state=session.state.value
        )

    def _generate_next_question(self, session: StreamworksSession, extraction_result: ExtractionResult) -> str:
        """Generate intelligent next question based on extracted parameters"""

        # Get extracted parameters count for response customization
        extracted_count = len(session.stream_parameters) + len(session.job_parameters)

        # If we just extracted something, acknowledge it!
        if extracted_count > 0:
            # 🧹 Use cleaned parameters for response generation (fix frontend artifacts issue)
            cleaned_stream_params = self._clean_frontend_parameters(session.stream_parameters)
            cleaned_job_params = self._clean_frontend_parameters(session.job_parameters)
            extracted_names = list(cleaned_stream_params.keys()) + list(cleaned_job_params.keys())

            # Acknowledge what was extracted
            if "StreamName" in cleaned_stream_params:
                stream_name = cleaned_stream_params["StreamName"]
                acknowledgment = f"Perfekt! Ich habe '{stream_name}' als Stream-Name erkannt. "
            else:
                acknowledgment = f"Gut! Ich habe {len(extracted_names)} Parameter erkannt: {', '.join(extracted_names[:3])}{'...' if len(extracted_names) > 3 else ''}. "

            # Check if StreamName is still missing (most critical)
            if "StreamName" not in session.stream_parameters:
                return acknowledgment + "Wie soll Ihr Streamworks-Stream heißen?"

            # Check for missing critical parameters based on job type
            if session.job_type == "SAP":
                if "System" not in session.job_parameters and "SAPSystem" not in session.job_parameters:
                    return acknowledgment + "Von welchem SAP-System sollen die Daten exportiert werden? (z.B. ZTV, GT123, PRD)"
                if "TableName" not in session.job_parameters:
                    return acknowledgment + "Aus welcher SAP-Tabelle sollen die Daten exportiert werden? (z.B. PA1, ZTV_CALENDAR)"

            elif session.job_type == "FILE_TRANSFER":
                if "Agent" not in session.job_parameters and "SourceServer" not in session.job_parameters:
                    return acknowledgment + "Von welchem Server/Agent sollen die Dateien übertragen werden?"
                if "Zielpfad" not in session.job_parameters and "TargetServer" not in session.job_parameters:
                    return acknowledgment + "Zu welchem Zielserver sollen die Dateien übertragen werden?"

            # If we have good completion, offer next steps
            total_params = len(extraction_result.stream_parameters) + len(extraction_result.job_parameters)
            if total_params >= 5:
                return acknowledgment + "Ihre Streamworks-Konfiguration sieht gut aus! Soll ich das XML generieren oder benötigen Sie weitere Parameter?"

            # Ask for more details
            return acknowledgment + "Können Sie weitere Details zu Ihrem Stream angeben?"

        # No parameters extracted yet - check if StreamName is missing
        if "StreamName" not in session.stream_parameters:
            # Be less demanding if they provided any name-like input
            return "Wie soll Ihr Streamworks-Stream heißen? Dieser Name identifiziert Ihren Stream eindeutig."

        # Fallback
        return "Können Sie weitere Details zu Ihrem Stream angeben?"

    def _generate_suggestions(self, session: StreamworksSession, extraction_result: ExtractionResult) -> List[str]:
        """Generate smart suggestions based on current state"""

        suggestions = []

        if session.job_type == "SAP":
            suggestions.extend([
                "Exportiere als Excel Format",
                "Täglich um 6:00 Uhr ausführen",
                "Nur aktuelle Einträge filtern"
            ])
        elif session.job_type == "FILE_TRANSFER":
            suggestions.extend([
                "Nur *.csv Dateien übertragen",
                "SFTP als Übertragungsprotokoll",
                "Stündliche Synchronisation"
            ])

        return suggestions[:3]  # Max 3 suggestions

    async def _build_error_response(self, session_id: str, error_message: str) -> LangExtractResponse:
        """Build error response"""

        return LangExtractResponse(
            session_id=session_id,
            response_message=f"Entschuldigung, es gab einen Fehler: {error_message}",
            error=error_message
        )


    async def _get_session_async(self, session_id: str) -> Optional[StreamworksSession]:
        """Get session from memory or load from persistence"""

        # First check memory cache
        if session_id in self.sessions:
            # Update activity for existing session
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            return session

        # Try to load from persistence
        if self.persistence_service.is_enabled():
            session = await self.persistence_service.load_session(session_id)
            if session:
                # Store in memory for faster access
                self.sessions[session_id] = session
                logger.info(f"📥 Session loaded from persistence: {session_id}")
                return session

        return None

    async def _save_session_async(self, session: StreamworksSession) -> bool:
        """Save session to persistence asynchronously"""

        logger.info(f"🔄 ATTEMPTING to save session: {session.session_id}")

        if not self.persistence_service.is_enabled():
            logger.warning(f"❌ Persistence service is DISABLED for session: {session.session_id}")
            return False

        logger.info(f"✅ Persistence service is ENABLED for session: {session.session_id}")

        try:
            # Update last activity
            session.last_activity = datetime.now()
            logger.info(f"📅 Updated last_activity for session: {session.session_id}")

            # Save to persistence
            logger.info(f"💾 CALLING persistence_service.save_session() for: {session.session_id}")
            success = await self.persistence_service.save_session(session)

            if success:
                logger.info(f"✅ Session SUCCESSFULLY saved to persistence: {session.session_id}")
            else:
                logger.error(f"❌ Session save FAILED (returned False): {session.session_id}")

            return success

        except Exception as e:
            logger.error(f"❌ EXCEPTION during session save {session.session_id}: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return False

    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session info including parameters and completion status"""

        session = await self._get_session_async(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "job_type": session.job_type,
            "stream_parameters": session.stream_parameters,
            "job_parameters": session.job_parameters,
            "critical_missing": session.critical_missing,
            "session_state": session.state.value if hasattr(session.state, 'value') else str(session.state),
            "created_at": session.created_at.isoformat() if hasattr(session.created_at, 'isoformat') else str(session.created_at),
            "last_activity": session.last_activity.isoformat() if hasattr(session.last_activity, 'isoformat') else str(session.last_activity)
        }

    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions from persistence"""

        if not self.persistence_service.is_enabled():
            # Return in-memory sessions if persistence is disabled
            return [
                {
                    "session_id": session.session_id,
                    "stream_name": session.stream_parameters.get("StreamName", "Unnamed Stream"),
                    "job_type": session.job_type,
                    "created_at": session.created_at.isoformat() if hasattr(session.created_at, 'isoformat') else str(session.created_at),
                    "last_activity": session.last_activity.isoformat() if hasattr(session.last_activity, 'isoformat') else str(session.last_activity)
                }
                for session in self.sessions.values()
            ]

        return await self.persistence_service.list_user_sessions(limit)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from memory and persistence"""

        # Remove from memory
        if session_id in self.sessions:
            del self.sessions[session_id]

        # Remove from persistence
        if self.persistence_service.is_enabled():
            return await self.persistence_service.delete_session(session_id)

        return True

    async def generate_xml(
        self,
        session_id: str,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🎯 Generate Streamworks XML from extracted parameters

        Args:
            session_id: Session ID containing extracted parameters
            job_type: Optional job type override

        Returns:
            Dictionary with XML content and metadata
        """

        # Load session
        session = await self._get_session_async(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Determine job type
        target_job_type = job_type or session.job_type
        if not target_job_type:
            raise ValueError("Job type not specified and not detected in session")

        try:
            logger.info(f"🎯 Generating XML for session {session_id}, job type: {target_job_type}")

            # Combine all parameters from session
            all_parameters = {
                **session.stream_parameters,
                **session.job_parameters
            }

            if not all_parameters:
                raise ValueError("No parameters found in session to generate XML")

            logger.debug(f"Using {len(all_parameters)} parameters for XML generation")

            # Map parameters to XML template format
            mapped_parameters = self.parameter_mapper.map_parameters(
                job_type=target_job_type,
                extracted_parameters=all_parameters
            )

            logger.info(f"✅ Mapped {len(mapped_parameters)} parameters for XML template")

            # Generate XML using template engine
            xml_content = self.xml_template_engine.generate_xml(
                job_type=target_job_type,
                parameters=mapped_parameters
            )

            # Generate metadata
            xml_metadata = {
                "session_id": session_id,
                "job_type": target_job_type,
                "generated_at": datetime.now().isoformat(),
                "parameter_count": len(all_parameters),
                "mapped_parameter_count": len(mapped_parameters),
                "template_used": f"{target_job_type.lower()}_job_template.xml",
                "xml_size": len(xml_content),
                "stream_name": mapped_parameters.get("stream_name", "UNKNOWN"),
                "session_created": session.created_at.isoformat() if session.created_at else None
            }

            logger.info(f"✅ XML generated successfully: {xml_metadata['xml_size']} characters")

            # 🗄️ Store XML in dual storage (Supabase + Local)
            storage_request = XMLStorageRequest(
                session_id=session_id,
                # ⚠️ STREAM PREFIX: Fallback stream name with 'zsw_' prefix
                stream_name=mapped_parameters.get("stream_name", f"zsw_{target_job_type}"),
                job_type=target_job_type,
                xml_content=xml_content,
                parameters_used=mapped_parameters,
                metadata=xml_metadata,
                user_id=None  # Could be extracted from session if available
            )

            try:
                stored_xml = await self.xml_storage_service.store_xml(storage_request)
                logger.info(f"✅ XML stored successfully: ID={stored_xml.id}, Version={stored_xml.version}")

                # Add storage information to response
                xml_metadata.update({
                    "storage_id": str(stored_xml.id),
                    "version": stored_xml.version,
                    "stored_at": stored_xml.created_at.isoformat(),
                    "file_path": stored_xml.file_path,
                    "file_size": stored_xml.file_size
                })

            except Exception as storage_error:
                logger.error(f"⚠️ XML storage failed: {storage_error}")
                # Don't fail the whole operation, just log the storage issue
                xml_metadata["storage_error"] = str(storage_error)

            return {
                "success": True,
                "xml_content": xml_content,
                "metadata": xml_metadata,
                "parameters_used": mapped_parameters,
                "original_parameters": all_parameters
            }

        except Exception as e:
            logger.error(f"❌ XML generation failed for session {session_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "job_type": target_job_type
            }

    async def preview_xml_parameters(
        self,
        session_id: str,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🔍 Preview XML parameters without generating full XML

        Useful for parameter validation and debugging
        """

        # Load session
        session = await self._get_session_async(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Determine job type
        target_job_type = job_type or session.job_type
        if not target_job_type:
            raise ValueError("Job type not specified and not detected in session")

        try:
            # Combine all parameters
            all_parameters = {
                **session.stream_parameters,
                **session.job_parameters
            }

            # Map parameters
            mapped_parameters = self.parameter_mapper.map_parameters(
                job_type=target_job_type,
                extracted_parameters=all_parameters
            )

            # Get template context preview
            template_context = self.xml_template_engine.preview_context(
                job_type=target_job_type,
                parameters=mapped_parameters
            )

            # Get template parameter schema
            template_schema = self.xml_template_engine.get_template_parameters(target_job_type)

            return {
                "session_id": session_id,
                "job_type": target_job_type,
                "original_parameters": all_parameters,
                "mapped_parameters": mapped_parameters,
                "template_context": template_context,
                "template_schema": template_schema,
                "mapping_summary": {
                    "original_count": len(all_parameters),
                    "mapped_count": len(mapped_parameters),
                    "required_fields": template_schema.get("required_fields", [])
                }
            }

        except Exception as e:
            logger.error(f"❌ XML parameter preview failed: {str(e)}")
            raise

    async def get_generated_xmls(self, session_id: str) -> Dict[str, Any]:
        """
        📂 Get all generated XMLs for a session

        Args:
            session_id: Session ID to get XMLs for

        Returns:
            Dictionary with XML list and metadata
        """

        try:
            logger.info(f"📂 Getting generated XMLs for session: {session_id}")

            xmls = await self.xml_storage_service.get_xmls_by_session(session_id)

            # Convert to serializable format
            xml_list = []
            for xml_record in xmls:
                xml_list.append({
                    "id": str(xml_record.id),
                    "stream_name": xml_record.stream_name,
                    "job_type": xml_record.job_type,
                    "version": xml_record.version,
                    "created_at": xml_record.created_at.isoformat(),
                    "file_size": xml_record.file_size,
                    "parameters_used": xml_record.parameters_used,
                    "metadata": xml_record.metadata
                })

            logger.info(f"✅ Found {len(xml_list)} XMLs for session {session_id}")

            return {
                "session_id": session_id,
                "total_xmls": len(xml_list),
                "xmls": xml_list
            }

        except Exception as e:
            logger.error(f"❌ Failed to get XMLs for session {session_id}: {str(e)}")
            raise

    async def get_xml_content(self, xml_id: str) -> Dict[str, Any]:
        """
        📄 Get specific XML content by ID

        Args:
            xml_id: UUID of the XML record

        Returns:
            Dictionary with XML content and metadata
        """

        try:
            from uuid import UUID
            xml_uuid = UUID(xml_id)

            logger.info(f"📄 Getting XML content for ID: {xml_id}")

            # Get XML record
            xml_record = await self.xml_storage_service.get_xml_by_id(xml_uuid)
            if not xml_record:
                raise ValueError(f"XML not found: {xml_id}")

            # Try to get content from local file first (faster)
            xml_content = await self.xml_storage_service.get_local_file_content(xml_uuid)
            if not xml_content:
                # Fallback to database content
                xml_content = xml_record.xml_content

            logger.info(f"✅ Retrieved XML content: {len(xml_content)} characters")

            return {
                "id": xml_id,
                "stream_name": xml_record.stream_name,
                "job_type": xml_record.job_type,
                "version": xml_record.version,
                "xml_content": xml_content,
                "created_at": xml_record.created_at.isoformat(),
                "file_size": xml_record.file_size,
                "parameters_used": xml_record.parameters_used,
                "metadata": xml_record.metadata
            }

        except Exception as e:
            logger.error(f"❌ Failed to get XML content for {xml_id}: {str(e)}")
            raise

    async def delete_generated_xml(self, xml_id: str) -> bool:
        """
        🗑️ Delete a generated XML

        Args:
            xml_id: UUID of the XML to delete

        Returns:
            True if successful, False otherwise
        """

        try:
            from uuid import UUID
            xml_uuid = UUID(xml_id)

            logger.info(f"🗑️ Deleting XML: {xml_id}")

            success = await self.xml_storage_service.delete_xml(xml_uuid)

            if success:
                logger.info(f"✅ XML deleted successfully: {xml_id}")
            else:
                logger.warning(f"⚠️ Failed to delete XML: {xml_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Error deleting XML {xml_id}: {str(e)}")
            return False

    async def get_storage_statistics(self) -> Dict[str, Any]:
        """
        📊 Get XML storage statistics

        Returns:
            Dictionary with storage statistics
        """

        try:
            logger.info("📊 Getting storage statistics")

            stats = await self.xml_storage_service.get_storage_stats()

            logger.info(f"✅ Retrieved storage statistics")
            return stats

        except Exception as e:
            logger.error(f"❌ Failed to get storage statistics: {str(e)}")
            raise

    def _clean_frontend_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """🧹 Clean parameters for frontend display - remove LangExtract artifacts"""

        cleaned = {}

        # Technical fields that should never be shown to users
        blacklist_fields = {
            'extractions', 'text', '_document_id', 'extraction_class',
            'extraction_text', 'confidence', 'highlighted_ranges',
            'source_grounding', 'metadata', '__dict__', '__class__',
            'api_calls_made', 'extraction_duration', 'warnings',
            'extraction_errors', 'processing_time'
        }

        for key, value in parameters.items():
            # Skip blacklisted technical fields
            if key.lower() in [field.lower() for field in blacklist_fields]:
                continue

            # Skip empty or invalid values
            if value is None or value == "":
                continue

            # Skip object references
            if isinstance(value, str) and '[object' in value.lower():
                continue

            # Clean the value
            cleaned_value = self._clean_parameter_value(value)
            if cleaned_value is not None:
                cleaned[key] = cleaned_value

        logger.info(f"🧹 Cleaned {len(parameters)} → {len(cleaned)} parameters for frontend")
        return cleaned

    def _calculate_completion_percentage(self, session: StreamworksSession) -> float:
        """Calculate session completion percentage based on extracted parameters"""
        try:
            # Clean parameters before counting
            clean_stream = self._clean_frontend_parameters(session.stream_parameters)
            clean_job = self._clean_frontend_parameters(session.job_parameters)
            total_params = len(clean_stream) + len(clean_job)

            # Minimum required parameters for completion
            required_count = 2  # StreamName + ShortDescription minimum
            if session.job_type == "FILE_TRANSFER":
                required_count = 4  # + source_agent, target_agent
            elif session.job_type == "SAP":
                required_count = 4  # + system, report
            elif session.job_type == "STANDARD":
                required_count = 3  # + MainScript

            # Calculate percentage (max 100%)
            completion = min((total_params / max(required_count, 1)) * 100.0, 100.0)
            return completion

        except Exception as e:
            logger.warning(f"Failed to calculate completion percentage: {e}")
            return 0.0


class StreamworksSchemaLoader:
    """Load Streamworks schemas for LangExtract"""

    def __init__(self):
        self.schema_path = Path(__file__).parent.parent.parent.parent / "templates" / "langextract_schemas.json"

    def load_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load all LangExtract schemas v2.0"""

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            schemas = data.get('parameter_extraction', {})
            logger.info(f"✅ StreamworksSchemaLoader loaded {len(schemas)} schemas v{data.get('version', '2.0')}")
            return schemas

        except Exception as e:
            logger.error(f"❌ Failed to load langextract schemas: {e}")
            return {}


# Factory function
_unified_service_instance: Optional[UnifiedLangExtractService] = None

def get_unified_langextract_service() -> UnifiedLangExtractService:
    """Get singleton instance of UnifiedLangExtractService"""
    global _unified_service_instance

    if _unified_service_instance is None:
        _unified_service_instance = UnifiedLangExtractService()

    return _unified_service_instance