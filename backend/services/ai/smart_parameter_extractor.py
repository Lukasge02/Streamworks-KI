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

        keyword_mapping = {
            "FILE_TRANSFER": [
                "file transfer", "file", "datei", "dateien", "transfer", "kopier", "kopieren",
                "verschieben", "sftp", "ftp", "rsync", "kopie", "copy"
            ],
            "SAP": [
                "sap", "jexa", "mandant", "report", "transaction", "transaktion", "fabrik",
                "calendar", "kalender", "variant", "sap-system"
            ],
            "STANDARD": [
                "script", "skript", "batch", "job", "prozess", "process", "command",
                "befehl", "shell", "python", "exe"
            ],
        }

        for job_type, keywords in keyword_mapping.items():
            if any(keyword in message_lower for keyword in keywords):
                return job_type

        job_types_info = []
        for job_type, schema in self.schemas.items():
            job_types_info.append(f"""
{job_type}: {schema['display_name']} - {schema['description']}
Typische Parameter: {[p['name'] for p in schema['parameters'][:3]]}
""")

        prompt = ChatPromptTemplate.from_template("""
Du bist ein Experte für die Klassifizierung von Job-Anfragen.

Verfügbare Job-Types:
{job_types}

Analysiere diese User-Nachricht und bestimme den wahrscheinlichsten Job-Type:
"{user_message}"

Regeln:
- Wenn SAP, Report, System erwähnt wird → SAP
- Wenn Datei, Transfer, Copy erwähnt wird → FILE_TRANSFER
- Wenn Resource, Custom, spezifisch erwähnt wird → CUSTOM
- Standard Streams, einfache Jobs → STANDARD
- Bei Unsicherheit → STANDARD

Antworte NUR mit einem der Job-Type Namen: STANDARD, SAP, FILE_TRANSFER, CUSTOM
""")

        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "job_types": "\n".join(job_types_info),
                "user_message": user_message
            })

            detected_type = response.content.strip().upper()

            if detected_type in self.schemas:
                logger.info(f"Job-Type erkannt: {detected_type}")
                return detected_type
            else:
                logger.warning(f"Unbekannter Job-Type erkannt: {detected_type}, verwende STANDARD")
                return "STANDARD"

        except Exception as e:
            logger.error(f"Fehler bei Job-Type Detection: {e}")
            return "STANDARD"

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
