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

# import langextract as lx  # Temporarily disabled for debug
import asyncio
from pydantic import BaseModel, Field

# Models
from models.langextract_models import (
    StreamWorksSession,
    LangExtractRequest,
    LangExtractResponse,
    StreamParameter,
    JobParameter,
    ExtractionResult,
    SessionState
)

# Session Persistence
from .sqlalchemy_session_persistence_service import get_sqlalchemy_session_persistence_service

logger = logging.getLogger(__name__)


class UnifiedLangExtractService:
    """
    🚀 Unified LangExtract Service - Moderne Parameter-Extraktion

    Features:
    - ✨ Pure LangExtract Integration
    - 🎯 StreamWorks-optimierte Prompts
    - 📊 Real-time Source Grounding
    - 🔄 Session Management
    - ⚡ Performance Optimiert
    """

    def __init__(self):
        """Initialize Unified LangExtract Service"""

        # Configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_id = "gpt-4o"

        # StreamWorks Schema Loader
        self.schema_loader = StreamWorksSchemaLoader()
        self.schemas = self.schema_loader.load_all_schemas()

        # Session Management (Hybrid: Memory + Persistence)
        self.sessions: Dict[str, StreamWorksSession] = {}
        self.persistence_service = get_sqlalchemy_session_persistence_service()

        # Performance Cache
        self._cache: Dict[str, ExtractionResult] = {}

        logger.info(f"🚀 UnifiedLangExtractService initialized with {len(self.schemas)} schemas")
        logger.info(f"💾 Session persistence: {'enabled' if self.persistence_service.is_enabled() else 'disabled'}")

    async def create_session(self, job_type: Optional[str] = None) -> StreamWorksSession:
        """Create new StreamWorks session with automatic persistence"""

        session_id = f"streamworks_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self) % 10000}"

        session = StreamWorksSession(
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

            # 1. Job-Type Detection (falls noch nicht bekannt)
            if not session.job_type:
                job_type = await self._detect_job_type(user_message)
                session.job_type = job_type
                logger.info(f"🎯 Detected job type: {job_type}")

            # 2. LangExtract Parameter Extraction
            extraction_result = await self._extract_parameters_langextract(
                user_message=user_message,
                session=session
            )

            # 3. Update Session
            session.stream_parameters.update(extraction_result.stream_parameters)
            session.job_parameters.update(extraction_result.job_parameters)
            session.last_activity = datetime.now()

            # 🎯 CRITICAL: Sync session.job_type with extracted JobTyp
            if "JobTyp" in extraction_result.job_parameters:
                detected_job_type = extraction_result.job_parameters["JobTyp"]
                if session.job_type != detected_job_type:
                    logger.info(f"Updating session job_type: {session.job_type} → {detected_job_type}")
                    session.job_type = detected_job_type

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
        """🔍 Detect StreamWorks job type using LangExtract"""

        job_type_prompt = """
        Analyze this user message and determine the StreamWorks job type.

        Available job types:
        - SAP: SAP system integration, data export/import, table operations
        - FILE_TRANSFER: File transfer between servers, data synchronization
        - STANDARD: General process automation, standard workflows

        Keywords to consider:
        - SAP: "sap", "export", "import", "table", "system", "ztv", "pa1"
        - FILE_TRANSFER: "transfer", "copy", "sync", "file", "server", "ftp", "sftp"
        - STANDARD: "process", "workflow", "automation", "job", "task"

        Return only the job type name.
        """

        try:
            # MOCK langextract for debug - detect job type from keywords
            logger.info(f"🔍 MOCK langextract job type detection for: {user_message}")
            result = self._mock_langextract_job_detection(user_message)

            # Parse result - LangExtract returns structured data
            if isinstance(result, dict):
                # Extract job_type from dict
                detected_type = result.get("job_type", "").upper()
            elif hasattr(result, "job_type"):
                # Extract from object attribute
                detected_type = getattr(result, "job_type", "").upper()
            elif hasattr(result, '__dict__'):
                # Convert object to dict and try to get job_type
                result_dict = result.__dict__
                detected_type = result_dict.get("job_type", "").upper()
            else:
                # Fallback - try to convert to string
                detected_type = str(result).strip().upper()

            if detected_type in ["SAP", "FILE_TRANSFER", "STANDARD"]:
                return detected_type
            else:
                # Fallback zu keyword-basierter Erkennung
                return self._fallback_job_type_detection(user_message)

        except Exception as e:
            logger.warning(f"MOCK LangExtract job type detection failed: {e}")
            return self._fallback_job_type_detection(user_message)

    def _mock_langextract_job_detection(self, user_message: str) -> dict:
        """Mock langextract job type detection for debug"""
        message_lower = user_message.lower()

        if any(keyword in message_lower for keyword in ["sap", "export", "import", "ztv", "gt123"]):
            return {"job_type": "SAP"}
        elif any(keyword in message_lower for keyword in ["transfer", "copy", "sync", "server"]):
            return {"job_type": "FILE_TRANSFER"}
        else:
            return {"job_type": "STANDARD"}

    def _fallback_job_type_detection(self, user_message: str) -> str:
        """Fallback job type detection using keywords"""

        message_lower = user_message.lower()

        # SAP Keywords
        sap_keywords = ["sap", "export", "import", "table", "ztv", "pa1", "system"]
        if any(keyword in message_lower for keyword in sap_keywords):
            return "SAP"

        # FILE_TRANSFER Keywords
        transfer_keywords = ["transfer", "copy", "sync", "file", "server", "ftp", "sftp"]
        if any(keyword in message_lower for keyword in transfer_keywords):
            return "FILE_TRANSFER"

        # Default to STANDARD
        return "STANDARD"

    async def _extract_parameters_langextract(
        self,
        user_message: str,
        session: StreamWorksSession
    ) -> ExtractionResult:
        """🎯 Core LangExtract Parameter Extraction"""

        schema = self.schemas.get(session.job_type)
        if not schema:
            logger.warning(f"No schema found for job type: {session.job_type}")
            return ExtractionResult()

        # Build StreamWorks-optimized prompt
        extraction_prompt = self._build_streamworks_prompt(schema, session)

        # Get examples for this job type
        examples = self._get_job_type_examples(session.job_type)

        try:
            # TEMPORARY FIX: Use direct OpenAI call instead of LangExtract
            # since LangExtract has internal issues with extractions attribute
            return await self._extract_with_openai_direct(user_message, extraction_prompt, examples)

        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            # Return empty result with error info
            return ExtractionResult(
                extraction_errors=[f"Extraction failed: {str(e)}"]
            )

    async def _extract_with_openai_direct(self, user_message: str, extraction_prompt: str, examples: List[Dict]) -> ExtractionResult:
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
            return await self._parse_langextract_result(result_data, {}, user_message)

        except Exception as e:
            logger.error(f"Direct OpenAI extraction failed: {e}")
            return ExtractionResult(
                extraction_errors=[f"Direct OpenAI extraction failed: {str(e)}"]
            )

    def _build_streamworks_prompt(self, schema: Dict[str, Any], session: StreamWorksSession) -> str:
        """🎯 Build StreamWorks-optimized flexible extraction prompt"""

        job_type = session.job_type or "UNKNOWN"

        # Already extracted parameters
        existing_stream = list(session.stream_parameters.keys())
        existing_job = list(session.job_parameters.keys())

        prompt = f"""
Extrahiere ALLE verfügbaren StreamWorks Parameter aus diesem deutschen Text.

🎯 STREAM PARAMETER (immer verfügbar):
- StreamName: Eindeutiger Name für den Stream (erkenne: "namens X", "heißt X", "soll X sein", einzelne Wörter)
- Beschreibung: Ausführliche Beschreibung des Streams
- Kurzbeschreibung: Kurze Übersicht (max. 50 Zeichen)
- Max_Läufe: Maximale Stream-Ausführungen (Zahlen wie 5, 10, 20)
- Zeitplanung: Zeitplanung erforderlich (erkenne: "täglich", "stündlich", "geplant" → true)
- E_Mail: Benachrichtigungs-E-Mail Adresse

⚙️ JOB PARAMETER (je nach Kontext):
- JobName: Name des Jobs innerhalb des Streams
- JobTyp: Art des Jobs (SAP, FILE_TRANSFER, STANDARD - erkenne automatisch)
- System: Zielsystem (GT123, ZTV, PRD, DEV, etc.)
- Agent: Ausführender Agent (Server-Namen, Agent-IDs)
- Benutzername: System-Benutzername für Ausführung
- Programm: Auszuführendes Programm oder Script
- Quellpfad: Quellverzeichnis oder -pfad
- Zielpfad: Zielverzeichnis oder -pfad
- Dateimuster: Datei-Pattern (*.csv, *.xlsx, *.txt, etc.)
- Protokoll: Übertragungsprotokoll (SFTP, FTP, HTTP, etc.)

🎯 SPEZIELLE JOB-TYPE PARAMETER:
FILE_TRANSFER:
- SourceServer: Quellserver (erkenne "von X nach Y" → SourceServer: X)
- TargetServer: Zielserver (erkenne "von X nach Y" → TargetServer: Y)
- Protocol: Übertragungsprotokoll (SFTP, FTP, HTTP)
- FilePattern: Dateimuster (*.csv, *.xlsx, *.txt)

SAP:
- SAPSystem: SAP-System (ZTV, GT123, PRD, DEV)
- TableName: SAP-Tabelle (PA1, ZTV_CALENDAR)
- ExportFormat: Export-Format (CSV, XLSX, XML)
- SAPUser: SAP-Benutzer (SAPCOMM, etc.)

STANDARD:
- Agent: Ausführender Agent
- Program: Programm/Script
- Schedule: Zeitplanung

📋 BEREITS EXTRAHIERT:
Stream: {existing_stream}
Job: {existing_job}

🔍 DEUTSCHE SPRACH-PATTERN:
- Namen: "streamname soll X sein", "heißt X", "namens Y"
- Systeme: "vom X zum Y", "aus System Z", "nach Agent W"
- Dateien: "mit *.csv", "Dateien *.xlsx", "Pattern *.txt"
- Protokoll: "über SFTP", "per FTP", "via HTTP"
- Zeit: "täglich", "stündlich", "geplant" → Zeitplanung: true

WICHTIG:
- Extrahiere nur Parameter die eindeutig erkennbar sind
- Einzelne Wörter ohne Kontext können StreamName sein
- Bei wenig Input: wenig Output, bei viel Input: viel Output
- Flexibel von einfachen Namen bis komplexen Konfigurationen

Return JSON mit allen gefundenen Parametern.
        """

        return prompt

    def _get_job_type_examples(self, job_type: str) -> List[Dict[str, Any]]:
        """🎯 Flexible Examples von einfach bis komplex für alle Job-Types"""

        # Universal examples that work for all job types
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
                    "Zeitplanung": True
                }
            },
            {
                "input": "BackupStream mit max 5 Läufen",
                "output": {
                    "StreamName": "BackupStream",
                    "Max_Läufe": 5
                }
            }
        ]

        # Job-type specific examples (complex scenarios)
        specific_examples = {
            "SAP": [
                {
                    "input": "SAP Export vom GT123 System",
                    "output": {
                        "JobTyp": "SAP",
                        "System": "GT123"
                    }
                },
                {
                    "input": "SAP_Kalender_Export von ZTV System mit SAPCOMM User täglich",
                    "output": {
                        "StreamName": "SAP_Kalender_Export",
                        "JobTyp": "SAP",
                        "System": "ZTV",
                        "Benutzername": "SAPCOMM",
                        "Zeitplanung": True
                    }
                }
            ],
            "FILE_TRANSFER": [
                {
                    "input": "Transfer vom Server1 zum Server2",
                    "output": {
                        "JobTyp": "FILE_TRANSFER",
                        "Quellpfad": "Server1",
                        "Zielpfad": "Server2"
                    }
                },
                {
                    "input": "FileSync von TestAgent1 nach TestAgent2 mit *.csv über SFTP",
                    "output": {
                        "StreamName": "FileSync",
                        "JobTyp": "FILE_TRANSFER",
                        "Agent": "TestAgent1",
                        "Zielpfad": "TestAgent2",
                        "Dateimuster": "*.csv",
                        "Protokoll": "SFTP"
                    }
                }
            ],
            "STANDARD": [
                {
                    "input": "Standard Backup Job täglich",
                    "output": {
                        "JobTyp": "STANDARD",
                        "JobName": "Backup",
                        "Zeitplanung": True
                    }
                },
                {
                    "input": "DailyProcess mit Script backup.exe auf Agent degtluv3009",
                    "output": {
                        "StreamName": "DailyProcess",
                        "JobTyp": "STANDARD",
                        "Programm": "backup.exe",
                        "Agent": "degtluv3009"
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

            # Remove job type indicators from stream name
            if detected_job_type == "SAP":
                # Remove SAP-related prefixes/indicators
                for indicator in ["sap", "export", "import"]:
                    stream_name = stream_name.replace(indicator, "", 1).strip()
                    stream_name = stream_name.replace(indicator.upper(), "", 1).strip()

            elif detected_job_type == "FILE_TRANSFER":
                # Remove transfer-related indicators
                for indicator in ["datentransfer", "transfer", "sync", "copy"]:
                    stream_name = stream_name.replace(indicator, "", 1).strip()
                    stream_name = stream_name.replace(indicator.capitalize(), "", 1).strip()

            elif detected_job_type == "STANDARD":
                # Remove standard job indicators
                for indicator in ["standard", "backup", "process"]:
                    stream_name = stream_name.replace(indicator, "", 1).strip()
                    stream_name = stream_name.replace(indicator.capitalize(), "", 1).strip()

            # Update StreamName if it was cleaned and still meaningful
            if stream_name and len(stream_name) > 1 and stream_name != original_name:
                stream_parameters["StreamName"] = stream_name
                logger.info(f"Cleaned StreamName: '{original_name}' → '{stream_name}'")
            elif not stream_name or len(stream_name) <= 1:
                # If cleaning removed everything, keep original but log it
                logger.info(f"Kept original StreamName: '{original_name}' (cleaning would remove too much)")

        # Set JobTyp parameter
        job_parameters["JobTyp"] = detected_job_type

        return stream_parameters, job_parameters

    async def _parse_langextract_result(
        self,
        langextract_result: Any,
        schema: Dict[str, Any],
        original_text: str
    ) -> ExtractionResult:
        """Parse LangExtract result into StreamWorks format with flexible parameter handling"""

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
            else:
                logger.warning(f"Unknown LangExtract result format: {type(langextract_result)}")
                result_data = {}

            logger.info(f"Parsed LangExtract result: {result_data}")

            # Enhanced parameter classification
            if result_data:
                # Define expanded stream parameter names (deutsche Parameter)
                stream_param_names = [
                    "StreamName", "Beschreibung", "Kurzbeschreibung", "Max_Läufe",
                    "Zeitplanung", "E_Mail", "Description", "Schedule", "Owner", "Priority"
                ]

                # Define job parameter names (deutsche Parameter) - Enhanced with job-type-specific parameters
                job_param_names = [
                    # General Job Parameters
                    "JobName", "JobTyp", "System", "Agent", "Benutzername", "Programm",
                    "Quellpfad", "Zielpfad", "Dateimuster", "Protokoll",

                    # FILE_TRANSFER specific
                    "SourceServer", "TargetServer", "Protocol", "FilePattern",
                    "SourcePath", "TargetPath", "TransferMode",

                    # SAP specific
                    "SAPSystem", "TableName", "ExportFormat", "SAPUser",

                    # STANDARD specific
                    "Schedule", "ProcessType", "DataSource", "NotificationSettings"
                ]

                # Process all extracted data with smart classification
                for key, value in result_data.items():
                    # Skip meta fields
                    if key in ["highlighted_ranges", "confidence", "job_type", "extraction_quality"]:
                        continue

                    # Classify parameter type
                    if key in stream_param_names:
                        stream_parameters[key] = value
                    elif key in job_param_names:
                        job_parameters[key] = value
                    else:
                        # Smart classification based on parameter name patterns
                        key_lower = key.lower()
                        if any(stream_word in key_lower for stream_word in ["stream", "name", "beschreibung", "mail", "läufe", "zeitplan"]):
                            stream_parameters[key] = value
                        else:
                            # Default to job parameters for unknown fields
                            job_parameters[key] = value

            # 🎯 POST-PROCESSING: Value-based job type detection and parameter reclassification
            logger.info(f"POST-PROCESSING: Starting job type detection with stream={stream_parameters}, job={job_parameters}")
            detected_job_type = self._detect_job_type_from_values(stream_parameters, job_parameters)
            logger.info(f"POST-PROCESSING: detected_job_type = {detected_job_type}")

            if detected_job_type:
                logger.info(f"POST-PROCESSING: Applying reclassification for {detected_job_type}")
                # Reclassify parameters based on detected job type
                stream_parameters, job_parameters = self._reclassify_parameters_by_job_type(
                    stream_parameters, job_parameters, detected_job_type
                )
                logger.info(f"Applied job type reclassification: {detected_job_type}")
            else:
                logger.info("POST-PROCESSING: No job type detected, skipping reclassification")

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

    async def _build_response(
        self,
        session: StreamWorksSession,
        extraction_result: ExtractionResult,
        original_message: str,
        processing_time: float
    ) -> LangExtractResponse:
        """Build response for frontend"""

        # Determine next question based on missing parameters
        next_question = self._generate_next_question(session, extraction_result)

        # Generate suggested questions
        suggested_questions = self._generate_suggestions(session, extraction_result)

        return LangExtractResponse(
            session_id=session.session_id,
            response_message=next_question,
            extracted_stream_parameters=extraction_result.stream_parameters,
            extracted_job_parameters=extraction_result.job_parameters,
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

    def _generate_next_question(self, session: StreamWorksSession, extraction_result: ExtractionResult) -> str:
        """Generate intelligent next question based on extracted parameters"""

        # Get extracted parameters count for response customization
        extracted_count = len(session.stream_parameters) + len(session.job_parameters)

        # If we just extracted something, acknowledge it!
        if extracted_count > 0:
            extracted_names = list(session.stream_parameters.keys()) + list(session.job_parameters.keys())

            # Acknowledge what was extracted
            if "StreamName" in session.stream_parameters:
                stream_name = session.stream_parameters["StreamName"]
                acknowledgment = f"Perfekt! Ich habe '{stream_name}' als Stream-Name erkannt. "
            else:
                acknowledgment = f"Gut! Ich habe {extracted_count} Parameter erkannt: {', '.join(extracted_names[:3])}{'...' if len(extracted_names) > 3 else ''}. "

            # Check if StreamName is still missing (most critical)
            if "StreamName" not in session.stream_parameters:
                return acknowledgment + "Wie soll Ihr StreamWorks-Stream heißen?"

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
                return acknowledgment + "Ihre StreamWorks-Konfiguration sieht gut aus! Soll ich das XML generieren oder benötigen Sie weitere Parameter?"

            # Ask for more details
            return acknowledgment + "Können Sie weitere Details zu Ihrem Stream angeben?"

        # No parameters extracted yet - check if StreamName is missing
        if "StreamName" not in session.stream_parameters:
            # Be less demanding if they provided any name-like input
            return "Wie soll Ihr StreamWorks-Stream heißen? Dieser Name identifiziert Ihren Stream eindeutig."

        # Fallback
        return "Können Sie weitere Details zu Ihrem Stream angeben?"

    def _generate_suggestions(self, session: StreamWorksSession, extraction_result: ExtractionResult) -> List[str]:
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

    async def generate_xml(self, session_id: str) -> str:
        """Generate StreamWorks XML from extracted parameters"""

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Use existing XML generation logic
        from services.xml_template_engine import XMLTemplateEngine
        xml_engine = XMLTemplateEngine()

        # Combine all parameters
        all_parameters = {
            **session.stream_parameters,
            **session.job_parameters,
            "JobType": session.job_type
        }

        xml_content = await xml_engine.generate_xml(
            job_type=session.job_type,
            parameters=all_parameters
        )

        return xml_content

    async def _get_session_async(self, session_id: str) -> Optional[StreamWorksSession]:
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

    async def _save_session_async(self, session: StreamWorksSession) -> bool:
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


class StreamWorksSchemaLoader:
    """Load StreamWorks schemas for LangExtract"""

    def __init__(self):
        self.schema_path = Path(__file__).parent.parent.parent.parent / "templates" / "unified_stream_schemas.json"

    def load_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load all StreamWorks schemas"""

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data.get('job_type_schemas', {})

        except Exception as e:
            logger.error(f"Failed to load schemas: {e}")
            return {}


# Factory function
_unified_service_instance: Optional[UnifiedLangExtractService] = None

def get_unified_langextract_service() -> UnifiedLangExtractService:
    """Get singleton instance of UnifiedLangExtractService"""
    global _unified_service_instance

    if _unified_service_instance is None:
        _unified_service_instance = UnifiedLangExtractService()

    return _unified_service_instance