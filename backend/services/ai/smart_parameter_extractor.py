"""
Smart Parameter Extractor - MVP Implementation
Multi-Parameter-Extraktion aus Chat-Nachrichten mit LangChain
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# ================================
# PYDANTIC MODELS FOR EXTRACTION
# ================================

class ExtractedParameter(BaseModel):
    """Einzelner extrahierter Parameter"""
    name: str = Field(description="Name des Parameters")
    value: Union[str, int, bool, None] = Field(description="Extrahierter Wert")
    confidence: float = Field(description="Konfidenz-Score 0.0-1.0")
    source_text: str = Field(description="Original-Text aus dem die Info extrahiert wurde")

class ParameterExtractionResult(BaseModel):
    """Ergebnis der Parameter-Extraktion"""
    job_type: Optional[str] = Field(description="Erkannter Job-Type (STANDARD, SAP, FILE_TRANSFER, CUSTOM)")
    extracted_parameters: List[ExtractedParameter] = Field(description="Liste extrahierter Parameter")
    missing_parameters: List[str] = Field(description="Liste fehlender Parameter")
    confidence_score: float = Field(description="Gesamt-Konfidenz der Extraktion")
    needs_clarification: bool = Field(description="Ob Nachfragen nötig sind")
    suggested_questions: List[str] = Field(description="Vorgeschlagene Nachfragen")

class HierarchicalExtractionResult(BaseModel):
    """Erweiterte Parameter-Extraktion für hierarchische Streams"""
    session_type: str = Field(default="STREAM_CONFIGURATION", description="Session-Typ")
    context_detected: str = Field(description="Erkannter Kontext: stream, job, oder mixed")

    # Stream-Level Extraktion
    stream_parameters: List[ExtractedParameter] = Field(default_factory=list, description="Stream-Level Parameter")
    missing_stream_parameters: List[str] = Field(default_factory=list, description="Fehlende Stream-Parameter")

    # Job-Level Extraktion
    detected_job_types: List[str] = Field(default_factory=list, description="Erkannte Job-Types")
    job_parameters: Dict[str, List[ExtractedParameter]] = Field(default_factory=dict, description="Job-Parameter nach Job-Type")
    missing_job_parameters: Dict[str, List[str]] = Field(default_factory=dict, description="Fehlende Job-Parameter")

    # Gesamt-Status
    confidence_score: float = Field(description="Gesamt-Konfidenz der Extraktion")
    needs_clarification: bool = Field(description="Ob Nachfragen nötig sind")
    suggested_questions: List[str] = Field(description="Vorgeschlagene Nachfragen")
    next_context: Optional[str] = Field(None, description="Empfohlener nächster Kontext")

    # Metadaten
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict, description="Zusätzliche Extractions-Metadaten")

class StandardJobParameters(BaseModel):
    """STANDARD Job Type Parameter"""
    StreamName: Optional[str] = Field(description="Name des Streams")
    StreamDocumentation: Optional[str] = Field(description="Dokumentation für den Stream")
    MaxStreamRuns: Optional[int] = Field(description="Maximale Anzahl der Ausführungen")
    ShortDescription: Optional[str] = Field(description="Kurze Beschreibung des Streams")
    SchedulingRequiredFlag: Optional[bool] = Field(description="Ob eine Planung erforderlich ist")
    StreamRunDeletionType: Optional[str] = Field(description="Typ der Löschung für Stream-Ausführungen")
    JobName: Optional[str] = Field(description="Name des Jobs")
    JobCategory: Optional[str] = Field(description="Kategorie des Jobs")
    IsNotificationRequired: Optional[bool] = Field(description="Ob eine Benachrichtigung erforderlich ist")

class SAPJobParameters(BaseModel):
    """SAP Job Type Parameter"""
    system: Optional[str] = Field(description="SAP System (PA1_100, PA1_200, PT1_100, PD1_100)")
    report: Optional[str] = Field(description="SAP Report Name")
    variant: Optional[str] = Field(description="Report-Variante")
    batch_user: Optional[str] = Field(description="Batch-Benutzer")

class FileTransferParameters(BaseModel):
    """FILE_TRANSFER Job Type Parameter"""
    source_agent: Optional[str] = Field(description="Quell-Agent")
    target_agent: Optional[str] = Field(description="Ziel-Agent")
    source_path: Optional[str] = Field(description="Quell-Dateipfad")
    target_path: Optional[str] = Field(description="Ziel-Dateipfad")

class CustomJobParameters(BaseModel):
    """CUSTOM Job Type Parameter"""
    ResourceName: Optional[str] = Field(description="Name der Ressource")
    ShortDescription: Optional[str] = Field(description="Kurze Beschreibung der Ressource")
    Status: Optional[str] = Field(description="Status der Ressource (Active, Inactive)")
    MaxParallelAllocations: Optional[int] = Field(description="Maximale Anzahl paralleler Zuweisungen")
    AutoReleaseFlag: Optional[bool] = Field(description="Ob die Ressource automatisch freigegeben werden soll")
    LogicalResourceType: Optional[str] = Field(description="Typ der logischen Ressource")
    MasterLogicalResourceId: Optional[str] = Field(description="ID der Master-logischen Ressource")
    DefaultMaxParallelAllocations: Optional[int] = Field(description="Standardwert für maximale parallele Zuweisungen")

# ================================
# SMART PARAMETER EXTRACTOR
# ================================

class SmartParameterExtractor:
    """
    Intelligenter Parameter-Extraktor mit LangChain
    Extrahiert multiple Parameter aus Chat-Nachrichten
    """

    def __init__(self, openai_api_key: str, schemas_path: Optional[str] = None):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.1
        )

        # Lade Job-Type Schemas
        if schemas_path:
            self.schemas = self._load_schemas(schemas_path)
        else:
            # Default path
            default_path = Path(__file__).parent.parent.parent / "templates" / "job_type_schemas.json"
            self.schemas = self._load_schemas(str(default_path))

        # Erstelle Pydantic Model Mapping
        self.parameter_models = {
            "STANDARD": StandardJobParameters,
            "SAP": SAPJobParameters,
            "FILE_TRANSFER": FileTransferParameters,
            "CUSTOM": CustomJobParameters
        }

        logger.info(f"SmartParameterExtractor initialisiert mit {len(self.schemas)} Job-Types")

    def _load_schemas(self, path: str) -> Dict[str, Any]:
        """Lädt Job-Type Schemas aus JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('schemas', {})
        except FileNotFoundError:
            logger.error(f"Schema-Datei nicht gefunden: {path}")
            return {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Schemas: {e}")
            return {}

    async def extract_parameters(
        self,
        user_message: str,
        current_job_type: Optional[str] = None,
        existing_parameters: Optional[Dict[str, Any]] = None
    ) -> ParameterExtractionResult:
        """
        Extrahiert Parameter aus User-Nachricht

        Args:
            user_message: Die Nachricht des Users
            current_job_type: Aktueller Job-Type (falls bereits bestimmt)
            existing_parameters: Bereits gesammelte Parameter

        Returns:
            ParameterExtractionResult mit extrahierten Parametern
        """
        try:
            logger.info(f"Extrahiere Parameter aus: '{user_message[:100]}...'")

            # Schritt 1: Bestimme Job-Type falls noch nicht bekannt
            if not current_job_type:
                job_type = await self._detect_job_type(user_message)
            else:
                job_type = current_job_type

            # Schritt 2: Extrahiere Parameter für den Job-Type
            if job_type and job_type in self.schemas:
                extracted = await self._extract_job_parameters(
                    user_message, job_type, existing_parameters or {}
                )
                extracted.job_type = job_type
                return extracted
            else:
                # Fallback: Versuche generische Extraktion
                return await self._generic_parameter_extraction(user_message)

        except Exception as e:
            logger.error(f"Fehler bei Parameter-Extraktion: {e}")
            return ParameterExtractionResult(
                job_type=None,
                extracted_parameters=[],
                missing_parameters=[],
                confidence_score=0.0,
                needs_clarification=True,
                suggested_questions=["Entschuldigung, ich konnte Ihre Anfrage nicht verstehen. Könnten Sie sie anders formulieren?"]
            )

    async def _detect_job_type(self, user_message: str) -> Optional[str]:
        """Erkennt Job-Type aus User-Nachricht"""

        # Erstelle Job-Type Detection Prompt
        message_lower = user_message.lower()

        # Erweiterte deutsche Keywords für bessere Erkennung
        keyword_mapping = {
            "FILE_TRANSFER": [
                # Bestehende Keywords
                "file transfer", "file", "datei", "dateien", "transfer", "kopier", "kopieren",
                "verschieben", "sftp", "ftp", "rsync", "kopie", "copy",
                # 🆕 Deutsche Keywords für FILE_TRANSFER
                "datentransfer", "datenübertragung", "übertragung", "übertragen",
                "zwischen", "von", "nach", "agent", "server", "system",
                "sync", "synchronisation", "synchronisierung", "bewegung", "transport",
                # 🔧 Häufige Schreibfehler und Variationen
                "datentrasnfer", "datentrasfer", "datetransfer", "data transfer",
                "file-transfer", "filetransfer", "datei transfer", "dateien transfer",
                "daten übertragung", "daten-übertragung", "datenübetragung"
            ],
            "SAP": [
                # Bestehende Keywords
                "sap", "jexa", "mandant", "report", "transaction", "transaktion", "fabrik",
                "calendar", "kalender", "variant", "sap-system",
                # 🆕 Deutsche SAP Keywords
                "gt123", "pa1", "pt1", "pd1", "ztv", "prd", "dev", "tst",
                "fabrikkalender", "sap system", "systemname", "export", "import",
                "jexa4s", "batch", "abap", "rfc"
            ],
            "STANDARD": [
                # WICHTIG: Nur explizite STANDARD Keywords - kein Default mehr!
                "standard job", "standard stream", "standard", "script", "skript",
                "batch job", "prozess", "process", "command", "befehl",
                "shell", "python script", "exe", "executable", "programm"
            ],
        }

        # Pattern-basierte Erkennung mit Konfidenz-Bewertung
        confidence_scores = self._detect_patterns_and_keywords(message_lower, keyword_mapping)

        # Bestimme Job-Type basierend auf Konfidenz (NIE automatisch STANDARD!)
        result = self._determine_job_type_by_confidence(confidence_scores, user_message)

        # Fallback zu LLM-basierter Erkennung nur wenn Konfidenz < 50%
        if result is None:
            return await self._llm_based_job_type_detection(user_message)

        return result

    def _detect_patterns_and_keywords(self, message_lower: str, keyword_mapping: dict) -> dict:
        """
        Intelligente Pattern- und Keyword-Erkennung mit Konfidenz-Scores
        """
        import re

        confidence_scores = {
            "FILE_TRANSFER": 0.0,
            "SAP": 0.0,
            "STANDARD": 0.0
        }

        # 1. High-Confidence Patterns (95% Konfidenz)
        high_confidence_patterns = {
            "FILE_TRANSFER": [
                r"zwischen\s+\w+\s+und\s+\w+",  # "zwischen server1 und server2"
                r"von\s+\w+\s+nach\s+\w+",      # "von agent1 nach agent2"
                r"datentransfer\s+zwischen",     # "datentransfer zwischen"
                r"\w+\s+zu\s+\w+\s+transfer",   # "server1 zu server2 transfer"
                # 🔧 Verbesserte Pattern für häufige Begriffe
                r"daten[trs]*transfer",          # "datentransfer", "datentrasnfer", etc.
                r"(datei|file).{0,3}transfer",   # "dateien transfer", "file transfer"
                r"transfer.*zwischen",           # "transfer zwischen"
                r"übertragung.*von.*zu",         # "übertragung von A zu B"
            ],
            "SAP": [
                r"sap\s+\w+",                    # "sap gt123", "sap system"
                r"aus\s+sap",                    # "export aus sap"
                r"sap-system\s+\w+",             # "sap-system gt123"
            ]
        }

        # 2. Medium-Confidence Patterns (75% Konfidenz)
        medium_confidence_patterns = {
            "FILE_TRANSFER": [
                r"übertragung.*zwischen",        # "übertragung zwischen"
                r"agent.*agent",                 # "von agent zu agent"
                r"server.*server",               # "server zu server"
            ],
            "SAP": [
                r"export.*sap",                  # "export aus sap"
                r"fabrikkalender",              # "fabrikkalender"
            ]
        }

        # 3. Pattern-Erkennung mit Konfidenz-Scoring
        for job_type, patterns in high_confidence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    confidence_scores[job_type] = max(confidence_scores[job_type], 0.95)
                    logger.info(f"🎯 High-confidence pattern gefunden für {job_type}: {pattern}")

        for job_type, patterns in medium_confidence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    confidence_scores[job_type] = max(confidence_scores[job_type], 0.75)
                    logger.info(f"📊 Medium-confidence pattern gefunden für {job_type}: {pattern}")

        # 4. Keyword-basierte Scoring (additive Konfidenz)
        for job_type, keywords in keyword_mapping.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in message_lower)
            if keyword_matches > 0:
                # 🔧 Spezielle Behandlung für eindeutige FILE_TRANSFER Begriffe
                if job_type == "FILE_TRANSFER":
                    high_confidence_keywords = [
                        "datentransfer", "datentrasnfer", "file transfer", "übertragung",
                        "transfer", "datei transfer", "dateien transfer"
                    ]
                    # Wenn eindeutige Keywords gefunden werden, erhöhe Konfidenz
                    has_strong_keyword = any(keyword in message_lower for keyword in high_confidence_keywords)
                    if has_strong_keyword:
                        keyword_confidence = min(0.85, 0.6 + (0.2 * keyword_matches))
                    else:
                        keyword_confidence = min(0.4 + (0.2 * (keyword_matches - 1)), 0.8)
                else:
                    # Base confidence: 0.4 + (0.2 * zusätzliche keywords)
                    keyword_confidence = min(0.4 + (0.2 * (keyword_matches - 1)), 0.8)

                confidence_scores[job_type] = max(confidence_scores[job_type], keyword_confidence)
                logger.info(f"🔍 {keyword_matches} Keywords gefunden für {job_type}: confidence {keyword_confidence}")

        # 5. 🔧 Fuzzy-Matching für ähnliche Begriffe (für häufige Schreibfehler)
        confidence_scores = self._apply_fuzzy_matching(message_lower, confidence_scores)

        logger.info(f"📈 Finale Konfidenz-Scores: {confidence_scores}")
        return confidence_scores

    def _apply_fuzzy_matching(self, message_lower: str, confidence_scores: dict) -> dict:
        """
        Anwendung von Fuzzy-Matching für ähnliche Begriffe
        """
        import re

        # Fuzzy-Pattern für FILE_TRANSFER (toleriert 1-2 Buchstabenfehler)
        fuzzy_file_transfer_patterns = [
            r"dat[aei][nrt][a-z]*transfer",      # datentransfer, datentrasnfer, etc.
            r"file.{0,2}transfer",               # file transfer, file-transfer
            r"transfer.{0,3}dat[aei]",          # transfer daten, transfer data
            r"[ua]bertr[aie]g[u]?ng",           # übertragung, ubertragung
        ]

        for pattern in fuzzy_file_transfer_patterns:
            if re.search(pattern, message_lower):
                # Erhöhe FILE_TRANSFER Konfidenz bei Fuzzy-Match
                fuzzy_confidence = 0.75
                confidence_scores["FILE_TRANSFER"] = max(
                    confidence_scores["FILE_TRANSFER"],
                    fuzzy_confidence
                )
                logger.info(f"🎯 Fuzzy-Match für FILE_TRANSFER: {pattern} → confidence {fuzzy_confidence}")

        return confidence_scores

    def _determine_job_type_by_confidence(self, confidence_scores: dict, user_message: str) -> Optional[str]:
        """
        Bestimmt Job-Type basierend auf Konfidenz-Scores
        WICHTIG: NIE automatisch STANDARD wählen!
        """
        # Sortiere nach Konfidenz
        sorted_scores = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
        highest_job_type, highest_confidence = sorted_scores[0]

        logger.info(f"🏆 Höchste Konfidenz: {highest_job_type} ({highest_confidence*100:.1f}%)")

        # Konfidenz-basierte Entscheidung
        if highest_confidence >= 0.80:
            logger.info(f"✅ Hohe Konfidenz ({highest_confidence*100:.1f}%) → {highest_job_type}")
            return highest_job_type
        elif highest_confidence >= 0.50:
            logger.info(f"⚠️ Mittlere Konfidenz ({highest_confidence*100:.1f}%) → Nachfrage erforderlich")
            return "ASK_USER"  # Spezialfall für Dialog Manager
        else:
            logger.info(f"❓ Niedrige Konfidenz ({highest_confidence*100:.1f}%) → Stream-Type Selector")
            return None  # Zeigt Stream-Type Selector

    async def _llm_based_job_type_detection(self, user_message: str) -> Optional[str]:
        """
        LLM-basierte Erkennung als letzter Fallback
        OHNE automatisches STANDARD-Defaulting!
        """
        try:
            job_types_info = []
            for job_type, schema in self.schemas.items():
                job_types_info.append(f"{job_type}: {schema['display_name']} - {schema['description']}")

            prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Klassifizierung von Job-Anfragen.
WICHTIG: Wähle NUR dann einen Job-Type, wenn du dir zu 80% sicher bist!

Verfügbare Job-Types:
{job_types}

Analysiere diese User-Nachricht:
"{user_message}"

Regeln:
- FILE_TRANSFER: Dateitransfer, zwischen Systemen, Server zu Server, Agent zu Agent
- SAP: SAP-Systeme, Reports, jexa, Mandanten, GT123, PA1, etc.
- STANDARD: Explizite Standard-Jobs, Scripts, Commands
- Bei Unsicherheit: Antworte mit "UNCERTAIN"

Antworte NUR mit: FILE_TRANSFER, SAP, STANDARD oder UNCERTAIN
""")

            chain = prompt | self.llm
            response = await chain.ainvoke({
                "job_types": "\n".join(job_types_info),
                "user_message": user_message
            })

            detected_type = response.content.strip().upper()

            if detected_type == "UNCERTAIN":
                logger.info("🤖 LLM ist unsicher → Keine automatische Entscheidung")
                return None
            elif detected_type in self.schemas:
                logger.info(f"🤖 LLM-Erkennung: {detected_type}")
                return detected_type
            else:
                logger.warning(f"🤖 LLM antwortete unbekannt: {detected_type}")
                return None

        except Exception as e:
            logger.error(f"❌ Fehler bei LLM Job-Type Detection: {e}")
            return None

    async def _extract_job_parameters(
        self,
        user_message: str,
        job_type: str,
        existing_parameters: Dict[str, Any]
    ) -> ParameterExtractionResult:
        """Extrahiert Parameter für einen bestimmten Job-Type"""

        schema = self.schemas[job_type]
        parameter_model = self.parameter_models[job_type]

        # Erstelle Parameter-Info für das Prompt
        parameter_info = []
        for param in schema['parameters']:
            examples_str = ", ".join([str(ex) for ex in param['examples'][:2]])
            parameter_info.append(f"""
- {param['name']} ({param['data_type']}): {param['description']}
  Frage: "{param['chat_prompt']}"
  Beispiele: {examples_str}
  Erforderlich: {'Ja' if param['required'] else 'Nein'}
""")

        # Erstelle Extraction Parser
        parser = PydanticOutputParser(pydantic_object=ParameterExtractionResult)

        prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Extraktion von Stream-Parametern aus User-Nachrichten.

Job-Type: {job_type}
Parameter für diesen Job-Type:
{parameters}

Bereits gesammelte Parameter:
{existing_parameters}

User-Nachricht: "{user_message}"

Aufgabe:
1. Extrahiere ALLE Parameter, die in der Nachricht erwähnt werden
2. Bestimme Konfidenz-Score für jeden Parameter (0.0-1.0)
3. Identifiziere fehlende Parameter
4. Generiere hilfreiche Nachfragen für fehlende Parameter

Wichtig:
- Erkenne auch implizite Angaben (z.B. "täglich" → SchedulingRequiredFlag=true)
- Extrahiere mehrere Parameter aus einer Nachricht
- Nutze Kontext und Erfahrung für Schlussfolgerungen
- Bei Unsicherheit: niedrigere Konfidenz, aber versuche trotzdem zu extrahieren

{format_instructions}
""")

        try:
            chain = prompt | self.llm | parser
            result = await chain.ainvoke({
                "job_type": job_type,
                "parameters": "\n".join(parameter_info),
                "existing_parameters": json.dumps(existing_parameters, indent=2, ensure_ascii=False),
                "user_message": user_message,
                "format_instructions": parser.get_format_instructions()
            })

            logger.info(f"Parameter extrahiert für {job_type}: {len(result.extracted_parameters)} gefunden")
            return result

        except Exception as e:
            logger.error(f"Fehler bei Parameter-Extraktion für {job_type}: {e}")

            # Fallback: Simple keyword-basierte Extraktion
            return await self._keyword_based_extraction(user_message, job_type, schema)

    async def _keyword_based_extraction(
        self,
        user_message: str,
        job_type: str,
        schema: Dict[str, Any]
    ) -> ParameterExtractionResult:
        """Fallback: Keyword-basierte Parameter-Extraktion"""

        extracted_params = []
        message_lower = user_message.lower()

        # Simple Keyword-Matching für häufige Parameter
        keyword_mappings = {
            "name": ["name", "heißt", "genannt", "titel"],
            "stream": ["stream", "job", "task", "aufgabe"],
            "system": ["system", "pa1", "pt1", "pd1", "sap"],
            "path": ["pfad", "path", "verzeichnis", "ordner"],
            "file": ["datei", "file", ".txt", ".xml", ".csv"]
        }

        for param in schema['parameters']:
            param_name = param['name'].lower()

            # Prüfe Keywords
            for keyword_type, keywords in keyword_mappings.items():
                if keyword_type in param_name:
                    for keyword in keywords:
                        if keyword in message_lower:
                            # Versuche Wert zu extrahieren (sehr simpel)
                            words = user_message.split()
                            keyword_index = next(
                                (i for i, word in enumerate(words) if keyword.lower() in word.lower()),
                                -1
                            )

                            if keyword_index >= 0 and keyword_index < len(words) - 1:
                                potential_value = words[keyword_index + 1].strip('.,!?')

                                extracted_params.append(ExtractedParameter(
                                    name=param['name'],
                                    value=potential_value,
                                    confidence=0.6,  # Niedrige Konfidenz für Keyword-basierte Extraktion
                                    source_text=f"{words[keyword_index]} {potential_value}"
                                ))
                                break

        # Bestimme fehlende Parameter
        extracted_names = {p.name for p in extracted_params}
        required_params = [p['name'] for p in schema['parameters'] if p['required']]
        missing_params = [name for name in required_params if name not in extracted_names]

        # Generiere einfache Nachfragen
        suggested_questions = []
        for missing in missing_params[:2]:  # Maximal 2 Nachfragen
            param_info = next((p for p in schema['parameters'] if p['name'] == missing), None)
            if param_info:
                suggested_questions.append(param_info['chat_prompt'])

        return ParameterExtractionResult(
            job_type=job_type,
            extracted_parameters=extracted_params,
            missing_parameters=missing_params,
            confidence_score=0.5,  # Mittlere Konfidenz für Fallback
            needs_clarification=len(missing_params) > 0,
            suggested_questions=suggested_questions
        )

    async def _generic_parameter_extraction(self, user_message: str) -> ParameterExtractionResult:
        """Generische Parameter-Extraktion ohne Job-Type"""

        return ParameterExtractionResult(
            job_type=None,
            extracted_parameters=[],
            missing_parameters=[],
            confidence_score=0.0,
            needs_clarification=True,
            suggested_questions=[
                "Welchen Art von Job möchten Sie erstellen?",
                "Handelt es sich um einen Standard-Job, SAP-Report, Dateitransfer oder etwas anderes?"
            ]
        )

    def get_job_type_info(self, job_type: str) -> Dict[str, Any]:
        """Gibt Informationen über einen Job-Type zurück"""
        return self.schemas.get(job_type, {})

    def get_available_job_types(self) -> List[Dict[str, Any]]:
        """Gibt alle verfügbaren Job-Types zurück"""
        return [
            {
                "job_type": job_type,
                "display_name": schema["display_name"],
                "description": schema["description"],
                "complexity": schema["complexity"],
                "estimated_time": schema["estimated_time"],
                "parameter_count": len(schema["parameters"])
            }
            for job_type, schema in self.schemas.items()
        ]

    # ================================
    # HIERARCHICAL EXTRACTION METHODS
    # ================================

    async def extract_hierarchical_parameters(
        self,
        user_message: str,
        session_context: Optional[Dict[str, Any]] = None
    ) -> HierarchicalExtractionResult:
        """
        Hierarchische Parameter-Extraktion für Stream-Konfiguration

        Args:
            user_message: Die Nachricht des Users
            session_context: Aktueller Session-Kontext mit bisherigen Parametern

        Returns:
            HierarchicalExtractionResult mit Stream- und Job-Level Parametern
        """
        try:
            logger.info(f"Hierarchische Extraktion für: '{user_message[:100]}...'")

            # Schritt 1: Kontext-Analyse - Stream vs Job vs Mixed
            context_analysis = await self._analyze_context(user_message, session_context)

            # Schritt 2: Parameter nach Scope klassifizieren und extrahieren
            stream_params = []
            job_params = {}
            detected_job_types = []

            if context_analysis["has_stream_context"]:
                stream_params = await self._extract_stream_parameters(user_message)

            if context_analysis["has_job_context"]:
                for job_type in context_analysis["detected_job_types"]:
                    job_parameters = await self._extract_job_parameters_for_type(user_message, job_type)
                    if job_parameters:
                        job_params[job_type] = job_parameters
                        detected_job_types.append(job_type)

            # Schritt 3: Completion-Analyse
            missing_stream_params = await self._get_missing_stream_parameters(stream_params)
            missing_job_params = {}
            for job_type in detected_job_types:
                missing_job_params[job_type] = await self._get_missing_job_parameters(
                    job_type, job_params.get(job_type, [])
                )

            # Schritt 4: Intelligente Nachfragen generieren
            suggested_questions = await self._generate_hierarchical_questions(
                context_analysis["primary_context"],
                missing_stream_params,
                missing_job_params
            )

            # Schritt 5: Confidence und Next Context bestimmen
            confidence_score = self._calculate_hierarchical_confidence(
                stream_params, job_params, context_analysis
            )

            next_context = self._determine_next_context(
                context_analysis["primary_context"],
                missing_stream_params,
                missing_job_params
            )

            return HierarchicalExtractionResult(
                context_detected=context_analysis["primary_context"],
                stream_parameters=stream_params,
                missing_stream_parameters=missing_stream_params,
                detected_job_types=detected_job_types,
                job_parameters=job_params,
                missing_job_parameters=missing_job_params,
                confidence_score=confidence_score,
                needs_clarification=len(missing_stream_params) > 0 or len(missing_job_params) > 0,
                suggested_questions=suggested_questions,
                next_context=next_context,
                extraction_metadata={
                    "context_analysis": context_analysis,
                    "timestamp": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Fehler bei hierarchischer Parameter-Extraktion: {e}")
            return HierarchicalExtractionResult(
                context_detected="unknown",
                stream_parameters=[],
                missing_stream_parameters=[],
                detected_job_types=[],
                job_parameters={},
                missing_job_parameters={},
                confidence_score=0.0,
                needs_clarification=True,
                suggested_questions=["Entschuldigung, ich konnte Ihre Anfrage nicht verstehen. Könnten Sie sie anders formulieren?"],
                extraction_metadata={"error": str(e)}
            )

    async def _analyze_context(
        self,
        user_message: str,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analysiert den Kontext der User-Nachricht"""

        # Import hier um zirkuläre Abhängigkeiten zu vermeiden
        from models.parameter_models import classify_parameter_scope, STREAM_LEVEL_PARAMETERS, JOB_LEVEL_PARAMETERS

        message_lower = user_message.lower()

        # Keyword-basierte Kontext-Erkennung
        stream_keywords = [
            "stream", "name", "titel", "beschreibung", "dokumentation", "dokumentieren",
            "konfiguration", "grundeinstellung", "basis", "allgemein"
        ]

        job_keywords = {
            "FILE_TRANSFER": ["datei", "file", "transfer", "kopier", "verschieben", "agent", "pfad", "quelle", "ziel"],
            "SAP": ["sap", "report", "system", "pa1", "pt1", "pd1", "mandant", "transaktion"],
            "CUSTOM": ["resource", "ressource", "custom", "benutzerdefiniert"],
            "STANDARD": ["job", "task", "aufgabe", "prozess", "ausführung"]
        }

        # Stream-Kontext prüfen
        has_stream_context = any(keyword in message_lower for keyword in stream_keywords)

        # Job-Kontext prüfen
        detected_job_types = []
        for job_type, keywords in job_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_job_types.append(job_type)

        has_job_context = len(detected_job_types) > 0

        # Primärer Kontext bestimmen
        if has_stream_context and has_job_context:
            primary_context = "mixed"
        elif has_stream_context:
            primary_context = "stream"
        elif has_job_context:
            primary_context = "job"
        else:
            # Fallback: Session-Kontext analysieren
            if session_context and session_context.get("jobs"):
                primary_context = "job"
            else:
                primary_context = "stream"  # Default zu Stream-Konfiguration

        return {
            "primary_context": primary_context,
            "has_stream_context": has_stream_context,
            "has_job_context": has_job_context,
            "detected_job_types": detected_job_types,
            "confidence": 0.8 if (has_stream_context or has_job_context) else 0.3
        }

    async def _extract_stream_parameters(self, user_message: str) -> List[ExtractedParameter]:
        """
        Intelligente LLM-basierte Extraktion von Stream-Level Parametern aus natürlicher deutscher Sprache

        Erkennt Parameter aus Fließtext wie:
        - "Der Stream soll DataTransfer heißen"
        - "Ich möchte einen Stream namens TestStream"
        - "Das ist ein Datentransfer zwischen GT123 und BASF"
        """
        try:
            # Stream Parameter Extraction Prompt (Deutsch optimiert)
            extraction_prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Extraktion von Streamworks-Parametern aus natürlicher deutscher Sprache.

AUFGABE: Extrahiere Stream-Level Parameter aus der folgenden Benutzernachricht.

VERFÜGBARE STREAM-PARAMETER:
- StreamName: Der eindeutige Name des Streams (z.B. "DataTransfer", "SAPExport", "TestStream")
- ShortDescription: Prägnante Kurzbeschreibung (MAXIMAL 50 Zeichen) - PFLICHTFELD für Streams
- MaxStreamRuns: Maximale Anzahl von Stream-Ausführungen (Zahl)
- SchedulingRequiredFlag: Ob Scheduling erforderlich ist (true/false)
- StreamRunDeletionType: Typ der Löschung ("None", "OnCompletion", "Scheduled")
- JobName: Name des Jobs innerhalb des Streams
- JobCategory: Kategorie des Jobs ("DataTransfer", "SAP", "Standard", "FILE_TRANSFER")
- IsNotificationRequired: Ob Benachrichtigungen erforderlich sind (true/false)

DEUTSCHE SPRACHMUSTER FÜR SHORTDESCRIPTION (≤50 Zeichen):
✅ StreamName aus: "heißt", "soll heißen", "namens", "mit dem Namen", "Stream Name", "benannt"
✅ ShortDescription aus: "ist ein", "für", "zwischen", "Transfer", "Export", "Import", "dient zur"
✅ Job-Kategorie aus: "datentransfer", "file transfer", "SAP", "übertragung", "export", "import"

BEISPIELE:
- "Der Stream soll DataTransfer heißen" → StreamName: "DataTransfer"
- "Transfer zwischen GT123 und BASF" → ShortDescription: "Transfer GT123-BASF"
- "Das ist ein SAP Export" → ShortDescription: "SAP Export", JobCategory: "SAP"
- "Für die Datenübertragung" → ShortDescription: "Datenübertragung"
- "Stream namens TestStream für File Transfer" → StreamName: "TestStream", ShortDescription: "File Transfer"
- "Ein Export Stream mit 10 Durchläufen" → ShortDescription: "Export Stream", MaxStreamRuns: 10

WICHTIG FÜR SHORTDESCRIPTION:
- Extrahiere immer eine ShortDescription wenn möglich
- Maximal 50 Zeichen
- Fokus auf Zweck/Funktion des Streams
- Bevorzuge kurze, prägnante Formulierungen
- Bei langen Beschreibungen: kürze intelligent ab

BENUTZERNACHRICHT:
"{user_message}"

Antworte nur mit einem JSON-Array von Objekten mit dieser Struktur:
[
  {{
    "name": "ParameterName",
    "value": "ExtrahierterWert",
    "confidence": 0.9,
    "source_text": "Originaler Text aus dem die Info stammt"
  }}
]

Wenn keine Parameter gefunden werden, antworte mit einem leeren Array: []
""")

            # LLM-Aufruf für Extraktion
            chain = extraction_prompt | self.llm

            response = await chain.ainvoke({
                "user_message": user_message
            })

            # Parse JSON Response
            import json
            try:
                response_text = response.content.strip()

                # Remove potential markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                extracted_data = json.loads(response_text.strip())

                # Convert to ExtractedParameter objects
                extracted_params = []
                for item in extracted_data:
                    if isinstance(item, dict) and all(key in item for key in ["name", "value", "confidence", "source_text"]):
                        extracted_params.append(ExtractedParameter(
                            name=item["name"],
                            value=item["value"],
                            confidence=float(item["confidence"]),
                            source_text=item["source_text"]
                        ))

                logger.info(f"🎯 LLM Stream-Extraktion: {len(extracted_params)} Parameter aus '{user_message[:50]}...'")

                # Log extracted parameters for debugging
                for param in extracted_params:
                    logger.info(f"   → {param.name}: {param.value} (conf: {param.confidence})")

                # Intelligente ShortDescription-Generierung falls nicht extrahiert
                extracted_params = self._ensure_short_description(extracted_params, user_message)

                return extracted_params

            except json.JSONDecodeError as e:
                logger.warning(f"JSON Parse Error in stream extraction: {e}")
                logger.warning(f"Raw LLM response: {response.content}")
                return []

        except Exception as e:
            logger.error(f"Fehler bei LLM Stream-Parameter-Extraktion: {e}")

            # Fallback: Verbesserte Regex-Pattern für kritische Parameter
            extracted_params = []
            import re

            # StreamName - Erweiterte deutsche Pattern
            stream_name_patterns = [
                r"stream\s*(?:soll|heißt|mit\s+(?:dem\s+)?namen?)\s+([a-zA-Z0-9_\-]+)",
                r"(?:namens|genannt)\s+([a-zA-Z0-9_\-]+)",
                r"stream\s*name[:\s]+([a-zA-Z0-9_\-]+)",
                r"(?:der\s+stream\s+)?heißt\s+([a-zA-Z0-9_\-]+)",
                r"name[:\s]+([a-zA-Z0-9_\-]+)"
            ]

            for pattern in stream_name_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    extracted_params.append(ExtractedParameter(
                        name="StreamName",
                        value=match.group(1),
                        confidence=0.75,
                        source_text=match.group(0)
                    ))
                    logger.info(f"📝 Fallback-Extraktion StreamName: {match.group(1)}")
                    break

            # ShortDescription - Transfer/Zwischen Pattern
            if "transfer" in user_message.lower() or "zwischen" in user_message.lower():
                # Extrahiere Transfer-Beschreibungen
                transfer_patterns = [
                    r"(?:transfer|übertragung)\s+(?:zwischen|von|zu)\s+([^.]+)",
                    r"zwischen\s+([^.]+)",
                    r"(?:ist\s+(?:ein\s+)?)?([^.]*(?:transfer|übertragung)[^.]*)"
                ]

                for pattern in transfer_patterns:
                    match = re.search(pattern, user_message, re.IGNORECASE)
                    if match:
                        description = match.group(1).strip()
                        if len(description) > 3 and len(description) < 100:
                            extracted_params.append(ExtractedParameter(
                                name="ShortDescription",
                                value=description,
                                confidence=0.70,
                                source_text=match.group(0)
                            ))
                            logger.info(f"📝 Fallback-Extraktion ShortDescription: {description}")
                            break

            return extracted_params

    async def _extract_job_parameters_for_type(
        self,
        user_message: str,
        job_type: str
    ) -> List[ExtractedParameter]:
        """Extrahiert Job-spezifische Parameter aus der Nachricht"""

        if job_type == "FILE_TRANSFER":
            return await self._extract_file_transfer_parameters(user_message)
        elif job_type == "SAP":
            return await self._extract_sap_parameters(user_message)
        elif job_type == "CUSTOM":
            return await self._extract_custom_parameters(user_message)
        elif job_type == "STANDARD":
            return await self._extract_standard_job_parameters(user_message)

        return []

    async def _extract_file_transfer_parameters(self, user_message: str) -> List[ExtractedParameter]:
        """Extrahiert FILE_TRANSFER spezifische Parameter"""
        import re

        extracted_params = []

        # Agent-Extraktion
        agent_patterns = [
            r"(?:quell|source)[-\s]*agent[:\s]+([a-zA-Z0-9_\-]+)",
            r"(?:quelle|von)[:\s]+([a-zA-Z0-9_\-]+)",
            r"(?:ziel|target)[-\s]*agent[:\s]+([a-zA-Z0-9_\-]+)",
            r"(?:zu|nach)[:\s]+([a-zA-Z0-9_\-]+)"
        ]

        for pattern in agent_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                agent_value = match.group(1)

                # Bestimme ob Source oder Target Agent
                if any(word in pattern for word in ["quell", "source", "quelle", "von"]):
                    param_name = "source_agent"
                elif any(word in pattern for word in ["ziel", "target", "zu", "nach"]):
                    param_name = "target_agent"
                else:
                    # Fallback basierend auf Reihenfolge
                    existing_agents = [p.name for p in extracted_params if p.name in ["source_agent", "target_agent"]]
                    param_name = "source_agent" if "source_agent" not in existing_agents else "target_agent"

                extracted_params.append(ExtractedParameter(
                    name=param_name,
                    value=agent_value,
                    confidence=0.90,
                    source_text=match.group(0)
                ))

        # Pfad-Extraktion
        path_patterns = [
            r"(?:pfad|path)[:\s]+([A-Za-z]:[\\\/][^\\s]+)",
            r"(?:von|aus)[:\s]+([A-Za-z]:[\\\/][^\\s]+)",
            r"(?:zu|nach)[:\s]+([A-Za-z]:[\\\/][^\\s]+)",
            r"([A-Za-z]:[\\\/][^\\s]+)"  # Allgemeine Pfad-Erkennung
        ]

        for pattern in path_patterns:
            matches = re.finditer(pattern, user_message, re.IGNORECASE)
            for match in matches:
                path_value = match.group(1)

                # Bestimme ob Source oder Target Path
                match_text = match.group(0).lower()
                if any(word in match_text for word in ["von", "aus", "quell", "source"]) or \
                   not any(p.name == "source_path" for p in extracted_params):
                    param_name = "source_path"
                else:
                    param_name = "target_path"

                extracted_params.append(ExtractedParameter(
                    name=param_name,
                    value=path_value,
                    confidence=0.85,
                    source_text=match.group(0)
                ))

        return extracted_params

    async def _extract_sap_parameters(self, user_message: str) -> List[ExtractedParameter]:
        """Extrahiert SAP spezifische Parameter"""
        # Implementierung für SAP-Parameter
        return []

    async def _extract_custom_parameters(self, user_message: str) -> List[ExtractedParameter]:
        """Extrahiert CUSTOM spezifische Parameter"""
        # Implementierung für Custom-Parameter
        return []

    async def _extract_standard_job_parameters(self, user_message: str) -> List[ExtractedParameter]:
        """Extrahiert STANDARD Job spezifische Parameter"""
        # Implementierung für Standard Job-Parameter
        return []

    async def _get_missing_stream_parameters(
        self,
        extracted_params: List[ExtractedParameter]
    ) -> List[str]:
        """Bestimmt fehlende Stream-Parameter"""
        from models.parameter_models import STREAM_LEVEL_PARAMETERS

        extracted_names = {p.name for p in extracted_params}

        # Erforderliche Stream-Parameter (basierend auf STANDARD Schema)
        standard_schema = self.get_job_type_info("STANDARD")
        if standard_schema:
            required_params = [p["name"] for p in standard_schema["parameters"] if p["required"]]
            return [name for name in required_params if name not in extracted_names]

        return []

    async def _get_missing_job_parameters(
        self,
        job_type: str,
        extracted_params: List[ExtractedParameter]
    ) -> List[str]:
        """Bestimmt fehlende Job-Parameter für einen Job-Type"""
        extracted_names = {p.name for p in extracted_params}

        job_schema = self.get_job_type_info(job_type)
        if job_schema:
            required_params = [p["name"] for p in job_schema["parameters"] if p["required"]]
            return [name for name in required_params if name not in extracted_names]

        return []

    async def _generate_hierarchical_questions(
        self,
        primary_context: str,
        missing_stream_params: List[str],
        missing_job_params: Dict[str, List[str]]
    ) -> List[str]:
        """Generiert intelligente Nachfragen basierend auf fehlendem Kontext"""
        questions = []

        # Stream-Parameter Fragen
        if missing_stream_params and len(missing_stream_params) <= 2:
            for param in missing_stream_params[:2]:
                if param == "StreamName":
                    questions.append("Wie soll der Stream heißen?")
                elif param == "ShortDescription":
                    questions.append("Können Sie eine kurze Beschreibung für den Stream angeben?")
                elif param == "JobName":
                    questions.append("Wie soll der Job genannt werden?")

        # Job-Parameter Fragen
        for job_type, missing_params in missing_job_params.items():
            if missing_params and len(missing_params) <= 2:
                for param in missing_params[:1]:  # Nur die wichtigste Frage
                    if job_type == "FILE_TRANSFER":
                        if param == "source_agent":
                            questions.append("Von welchem System sollen die Dateien übertragen werden?")
                        elif param == "target_agent":
                            questions.append("Zu welchem System sollen die Dateien übertragen werden?")
                        elif param == "source_path":
                            questions.append("Welche Dateien oder welches Verzeichnis soll übertragen werden?")

        # Fallback-Fragen
        if not questions:
            if primary_context == "stream":
                questions.append("Möchten Sie weitere Details zur Stream-Konfiguration angeben?")
            elif primary_context == "job":
                questions.append("Welche weiteren Parameter benötigen Sie für den Job?")
            else:
                questions.append("Was möchten Sie als nächstes konfigurieren?")

        return questions[:3]  # Maximal 3 Fragen

    def _calculate_hierarchical_confidence(
        self,
        stream_params: List[ExtractedParameter],
        job_params: Dict[str, List[ExtractedParameter]],
        context_analysis: Dict[str, Any]
    ) -> float:
        """Berechnet Gesamt-Confidence für hierarchische Extraktion"""

        # Basis-Confidence von Kontext-Analyse
        base_confidence = context_analysis.get("confidence", 0.5)

        # Parameter-Confidence
        all_params = stream_params + [p for params in job_params.values() for p in params]
        if all_params:
            avg_param_confidence = sum(p.confidence for p in all_params) / len(all_params)
            return (base_confidence + avg_param_confidence) / 2

        return base_confidence

    def _determine_next_context(
        self,
        primary_context: str,
        missing_stream_params: List[str],
        missing_job_params: Dict[str, List[str]]
    ) -> Optional[str]:
        """Bestimmt den empfohlenen nächsten Kontext"""

        # Priorisierung: Fehlende erforderliche Parameter zuerst
        if missing_stream_params:
            return "stream"

        for job_type, missing_params in missing_job_params.items():
            if missing_params:
                return f"job_{job_type.lower()}"

        # Kein fehlender Kontext - Session könnte vollständig sein
        return None

    def _ensure_short_description(
        self,
        extracted_params: List[ExtractedParameter],
        user_message: str
    ) -> List[ExtractedParameter]:
        """
        Stellt sicher, dass eine ShortDescription vorhanden ist.
        Generiert sie intelligent aus verfügbaren Parametern falls nicht extrahiert.
        """
        # Prüfe ob ShortDescription bereits extrahiert wurde
        has_short_description = any(p.name == "ShortDescription" for p in extracted_params)

        if has_short_description:
            # Validiere und kürze existierende ShortDescription
            for param in extracted_params:
                if param.name == "ShortDescription":
                    param.value = self._truncate_smart(str(param.value), 50)
            return extracted_params

        # Generiere ShortDescription aus verfügbaren Informationen
        stream_name = None
        job_category = None

        for param in extracted_params:
            if param.name == "StreamName":
                stream_name = str(param.value)
            elif param.name == "JobCategory":
                job_category = str(param.value)

        # Intelligente ShortDescription-Generierung
        generated_description = self._generate_smart_description(
            user_message, stream_name, job_category
        )

        if generated_description:
            extracted_params.append(ExtractedParameter(
                name="ShortDescription",
                value=generated_description,
                confidence=0.8,  # Leicht reduzierte Konfidenz für generierte Beschreibungen
                source_text=f"Auto-generiert aus: {user_message[:30]}..."
            ))
            logger.info(f"🤖 Auto-generierte ShortDescription: {generated_description}")

        return extracted_params

    def _generate_smart_description(
        self,
        user_message: str,
        stream_name: Optional[str] = None,
        job_category: Optional[str] = None
    ) -> Optional[str]:
        """
        Generiert intelligente ShortDescription aus verfügbaren Informationen
        """
        import re

        # Strategie 1: Aus StreamName + JobCategory
        if stream_name and job_category:
            if job_category.upper() == "SAP":
                return self._truncate_smart(f"SAP {stream_name}", 50)
            elif job_category.upper() in ["DATATRANSFER", "FILE_TRANSFER"]:
                return self._truncate_smart(f"{stream_name} Transfer", 50)
            else:
                return self._truncate_smart(f"{job_category} {stream_name}", 50)

        # Strategie 2: Aus StreamName allein
        if stream_name:
            # Erkenne Type aus StreamName
            name_lower = stream_name.lower()
            if "transfer" in name_lower or "ft" in name_lower:
                return self._truncate_smart(f"{stream_name} Transfer", 50)
            elif "export" in name_lower:
                return self._truncate_smart(f"{stream_name} Export", 50)
            elif "sap" in name_lower:
                return self._truncate_smart(f"SAP {stream_name}", 50)
            else:
                return self._truncate_smart(stream_name, 50)

        # Strategie 3: Aus User-Message extrahieren
        message_lower = user_message.lower()

        # Deutsche Beschreibungspattern
        description_patterns = [
            r"(?:ist\s+ein|für\s+(?:die\s+)?|dient\s+zur)\s+([^.!?]+)",
            r"(?:transfer|übertragung)\s+(?:von|zwischen|zu)\s+([^.!?]+)",
            r"(?:export|import)\s+(?:von|zu|für)\s+([^.!?]+)",
            r"(?:sap|file)\s+([^.!?]+)"
        ]

        for pattern in description_patterns:
            match = re.search(pattern, message_lower)
            if match:
                description = match.group(1).strip()
                # Bereinige und kürze
                description = re.sub(r'\s+', ' ', description)  # Mehrfache Leerzeichen
                description = description.capitalize()
                return self._truncate_smart(description, 50)

        # Strategie 4: Fallback basierend auf Keywords
        if "transfer" in message_lower:
            return "Datentransfer"
        elif "export" in message_lower:
            return "Export"
        elif "import" in message_lower:
            return "Import"
        elif "sap" in message_lower:
            return "SAP Process"

        # Kein passender Ansatz gefunden
        return None

    def _truncate_smart(self, text: str, max_length: int) -> str:
        """
        Intelligentes Kürzen von Text mit sinnvollen Wortgrenzen
        """
        if len(text) <= max_length:
            return text

        # Kürze an Wortgrenze
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > max_length * 0.7:  # Mindestens 70% der gewünschten Länge
            return truncated[:last_space]
        else:
            # Kürze hart ab wenn Wortgrenze zu weit vorne ist
            return truncated[:max_length-3] + "..."

# ================================
# FACTORY FUNCTION
# ================================

_extractor_instance: Optional[SmartParameterExtractor] = None

def get_smart_parameter_extractor(openai_api_key: Optional[str] = None) -> SmartParameterExtractor:
    """Factory function für SmartParameterExtractor"""
    global _extractor_instance

    if _extractor_instance is None:
        if not openai_api_key:
            from config import settings
            openai_api_key = settings.OPENAI_API_KEY

        _extractor_instance = SmartParameterExtractor(openai_api_key)

    return _extractor_instance
