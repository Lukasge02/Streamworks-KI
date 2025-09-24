"""
Schema Analyzer Service - Phase 0.1
Automatisierte Extraktion von Job-Type Regeln aus bestehenden XML-Templates mittels KI-Analyse
Erweitert die bestehende xml_template_engine.py um SchemaAnalyzer-Klasse
"""

import json
import logging
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from services.llm_factory import get_llm_service
from schemas.xml_generation import JobType

logger = logging.getLogger(__name__)

@dataclass
class ParameterDefinition:
    """Definition eines einzelnen Parameters"""
    name: str
    data_type: str  # "string", "integer", "boolean", "enum", "file_path", "agent", etc.
    required: bool
    default_value: Optional[str] = None
    description: str = ""
    validation_pattern: Optional[str] = None
    enum_values: Optional[List[str]] = None
    chat_prompt: str = ""  # Wie soll nach diesem Parameter gefragt werden?
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []

@dataclass
class JobTypeSchema:
    """Schema für einen Job-Type mit allen Parametern"""
    job_type: str
    display_name: str
    description: str
    complexity: str  # "simple", "medium", "complex"
    estimated_time: str  # "2-3 Minuten"
    icon: str
    parameters: List[ParameterDefinition]
    template_examples: List[str] = None  # Beispiel XML-Dateien

    def __post_init__(self):
        if self.template_examples is None:
            self.template_examples = []

class SchemaAnalyzer:
    """KI-gestützte Analyse von XML-Templates zur Schema-Ableitung"""

    def __init__(self, export_streams_dir: str = "Export-Streams"):
        """Initialize the schema analyzer"""
        base_dir = Path(__file__).parent.parent.parent
        self.export_streams_dir = base_dir / export_streams_dir
        self.templates_dir = base_dir / "backend" / "templates"
        self.output_file = self.templates_dir / "job_type_schemas.json"

        # Ensure directories exist
        self.templates_dir.mkdir(exist_ok=True)

        logger.info(f"Schema Analyzer initialized")
        logger.info(f"Export Streams Directory: {self.export_streams_dir}")
        logger.info(f"Templates Directory: {self.templates_dir}")

    async def analyze_all_xml_templates(self) -> Dict[str, JobTypeSchema]:
        """
        Hauptmethode: Analysiert alle XML-Templates und erstellt Job-Type Schemas
        """
        logger.info("🔍 Starting comprehensive XML template analysis...")

        # 1. Sammle alle XML-Dateien
        xml_files = self._collect_xml_files()
        logger.info(f"Found {len(xml_files)} XML files to analyze")

        # 2. Kategorisiere Files nach Job-Types (intelligent guessing)
        categorized_files = self._categorize_xml_files(xml_files)

        # 3. Analysiere jeden Job-Type mit KI
        schemas = {}
        llm_service = await get_llm_service()

        for job_type, files in categorized_files.items():
            logger.info(f"🤖 Analyzing {job_type} with {len(files)} example files")
            schema = await self._analyze_job_type_with_ai(job_type, files, llm_service)
            schemas[job_type] = schema

        # 4. Speichere Schemas
        self._save_schemas(schemas)

        logger.info(f"✅ Schema analysis completed. Generated {len(schemas)} job type schemas")
        return schemas

    def _collect_xml_files(self) -> List[Path]:
        """Sammelt alle XML-Dateien aus Export-Streams"""
        xml_files = []

        if not self.export_streams_dir.exists():
            logger.warning(f"Export streams directory not found: {self.export_streams_dir}")
            return []

        # Rekursiv alle .xml Dateien finden
        for xml_file in self.export_streams_dir.rglob("*.xml"):
            if xml_file.is_file():
                xml_files.append(xml_file)

        # Priorisiere geck003 und andere wichtige Beispiele
        priority_files = []
        regular_files = []

        for xml_file in xml_files:
            filename = xml_file.name.lower()
            if any(keyword in filename for keyword in ['geck003', 'beispiel', 'example', 'demo']):
                priority_files.append(xml_file)
            else:
                regular_files.append(xml_file)

        # Prioritäts-Files zuerst, dann reguläre
        return priority_files + regular_files[:20]  # Begrenzt auf 20 zusätzliche Files

    def _categorize_xml_files(self, xml_files: List[Path]) -> Dict[str, List[Path]]:
        """Kategorisiert XML-Dateien nach vermutlichen Job-Types"""
        categorized = {
            "STANDARD": [],
            "SAP": [],
            "FILE_TRANSFER": [],
            "CUSTOM": []
        }

        for xml_file in xml_files:
            try:
                # Parse XML und analysiere Job-Types
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Finde Jobs im Stream
                jobs = root.findall(".//Job")

                file_categorized = False

                for job in jobs:
                    job_type_elem = job.find("JobType")
                    template_type_elem = job.find("TemplateType")
                    job_name = job.find("JobName")

                    if template_type_elem is not None and template_type_elem.text == "FileTransfer":
                        categorized["FILE_TRANSFER"].append(xml_file)
                        file_categorized = True
                        break

                    if job_type_elem is not None:
                        job_type = job_type_elem.text
                        if job_type in ["Windows", "Unix", "Linux"]:
                            categorized["STANDARD"].append(xml_file)
                            file_categorized = True
                            break
                        elif "SAP" in job_type or "sap" in str(job_name).lower():
                            categorized["SAP"].append(xml_file)
                            file_categorized = True
                            break

                # Fallback: Dateiname-basierte Kategorisierung
                if not file_categorized:
                    filename_lower = xml_file.name.lower()
                    if any(keyword in filename_lower for keyword in ['ft', 'filetrans', 'transfer']):
                        categorized["FILE_TRANSFER"].append(xml_file)
                    elif any(keyword in filename_lower for keyword in ['sap', 'report', 'rbdagain']):
                        categorized["SAP"].append(xml_file)
                    elif any(keyword in filename_lower for keyword in ['geck003_003', 'standard', 'windows', 'script']):
                        categorized["STANDARD"].append(xml_file)
                    else:
                        categorized["CUSTOM"].append(xml_file)

            except Exception as e:
                logger.warning(f"Could not parse {xml_file}: {str(e)}")
                categorized["CUSTOM"].append(xml_file)

        # Log Kategorisierung
        for job_type, files in categorized.items():
            logger.info(f"{job_type}: {len(files)} files")
            for file in files[:3]:  # Zeige ersten 3 Files
                logger.info(f"  - {file.name}")

        return categorized

    async def _analyze_job_type_with_ai(self, job_type: str, xml_files: List[Path], llm_service) -> JobTypeSchema:
        """Analysiert einen Job-Type mit KI und extrahiert Parameter-Schema"""

        # Sammle XML-Beispiele (max 3 für KI-Analyse)
        xml_examples = []
        for xml_file in xml_files[:3]:
            try:
                content = xml_file.read_text(encoding='utf-8')
                xml_examples.append({
                    "filename": xml_file.name,
                    "content": content[:5000]  # Begrenzt auf 5000 Zeichen
                })
            except Exception as e:
                logger.warning(f"Could not read {xml_file}: {str(e)}")

        if not xml_examples:
            # Fallback Schema ohne KI
            return self._create_fallback_schema(job_type)

        # KI-Prompt für Schema-Extraktion
        prompt = self._create_analysis_prompt(job_type, xml_examples)

        try:
            # KI-Analyse
            response = await llm_service.generate(prompt)

            # Parse AI Response zu Schema
            schema = self._parse_ai_response_to_schema(job_type, response, xml_files)
            return schema

        except Exception as e:
            logger.error(f"KI-Analysis failed for {job_type}: {str(e)}")
            return self._create_fallback_schema(job_type)

    def _create_analysis_prompt(self, job_type: str, xml_examples: List[Dict]) -> str:
        """Erstellt den KI-Prompt für die Schema-Analyse"""

        prompt = f"""Du bist ein Streamworks XML-Experte. Analysiere die folgenden XML-Beispiele für Job-Type "{job_type}" und extrahiere ein Parameter-Schema für ein Chat-Interface.

AUFGABE:
1. Identifiziere alle konfigurierbaren Parameter für {job_type} Jobs
2. Bestimme welche Parameter PFLICHT und welche OPTIONAL sind
3. Erstelle Chat-freundliche Fragen für jeden Parameter
4. Gib Datentypen und Beispielwerte an

XML-BEISPIELE für {job_type}:
"""

        for i, example in enumerate(xml_examples, 1):
            prompt += f"\n--- Beispiel {i}: {example['filename']} ---\n"
            prompt += example['content']
            prompt += "\n"

        prompt += f"""

ANTWORT-FORMAT (JSON):
{{
  "job_type": "{job_type}",
  "display_name": "Benutzerfreundlicher Name",
  "description": "Kurze Beschreibung des Job-Types",
  "complexity": "simple|medium|complex",
  "estimated_time": "X-Y Minuten",
  "icon": "passendes-icon",
  "parameters": [
    {{
      "name": "parameter_name",
      "data_type": "string|integer|boolean|enum|file_path|agent",
      "required": true|false,
      "default_value": "default wenn optional",
      "description": "Technische Beschreibung",
      "validation_pattern": "regex pattern oder null",
      "enum_values": ["wert1", "wert2"] // nur bei data_type: enum,
      "chat_prompt": "Wie sollen wir im Chat nach diesem Parameter fragen?",
      "examples": ["beispiel1", "beispiel2"]
    }}
  ]
}}

WICHTIG:
- Fokus auf Parameter, die ein Benutzer im Chat konfigurieren würde
- Ignore interne Streamworks-Metadaten (DisplayOrder, CoordinateX, etc.)
- Chat-Prompts sollen natürlich und benutzerfreundlich sein
- Beispiele sollen realistische Werte aus den XMLs verwenden

Antworte nur mit valdem JSON, keine zusätzlichen Erklärungen.
"""

        return prompt

    def _parse_ai_response_to_schema(self, job_type: str, ai_response: str, xml_files: List[Path]) -> JobTypeSchema:
        """Parsed AI Response zu JobTypeSchema"""
        try:
            # Extrahiere JSON aus AI Response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")

            json_str = ai_response[json_start:json_end]
            schema_data = json.loads(json_str)

            # Konvertiere zu ParameterDefinition Objekten
            parameters = []
            for param_data in schema_data.get('parameters', []):
                param = ParameterDefinition(
                    name=param_data['name'],
                    data_type=param_data['data_type'],
                    required=param_data['required'],
                    default_value=param_data.get('default_value'),
                    description=param_data.get('description', ''),
                    validation_pattern=param_data.get('validation_pattern'),
                    enum_values=param_data.get('enum_values'),
                    chat_prompt=param_data.get('chat_prompt', ''),
                    examples=param_data.get('examples', [])
                )
                parameters.append(param)

            # Erstelle JobTypeSchema
            schema = JobTypeSchema(
                job_type=job_type,
                display_name=schema_data.get('display_name', job_type),
                description=schema_data.get('description', f'{job_type} Job'),
                complexity=schema_data.get('complexity', 'medium'),
                estimated_time=schema_data.get('estimated_time', '3-5 Minuten'),
                icon=schema_data.get('icon', 'terminal'),
                parameters=parameters,
                template_examples=[f.name for f in xml_files]
            )

            return schema

        except Exception as e:
            logger.error(f"Failed to parse AI response for {job_type}: {str(e)}")
            logger.debug(f"AI Response was: {ai_response}")
            return self._create_fallback_schema(job_type)

    def _create_fallback_schema(self, job_type: str) -> JobTypeSchema:
        """Erstellt ein Fallback-Schema wenn KI-Analyse fehlschlägt"""

        fallback_schemas = {
            "STANDARD": JobTypeSchema(
                job_type="STANDARD",
                display_name="Standard Job",
                description="Windows oder Unix Script-Ausführung",
                complexity="simple",
                estimated_time="2-3 Minuten",
                icon="terminal",
                parameters=[
                    ParameterDefinition(
                        name="script",
                        data_type="string",
                        required=True,
                        description="Script-Code oder Befehl",
                        chat_prompt="Welchen Befehl oder Script soll der Job ausführen?",
                        examples=["echo Hello World", "dir", "ls -la"]
                    ),
                    ParameterDefinition(
                        name="job_name",
                        data_type="string",
                        required=False,
                        description="Name des Jobs",
                        chat_prompt="Wie soll der Job heißen?",
                        examples=["DataProcessing", "FileCleanup", "Report"]
                    )
                ]
            ),
            "FILE_TRANSFER": JobTypeSchema(
                job_type="FILE_TRANSFER",
                display_name="File Transfer",
                description="Dateiübertragung zwischen Systemen",
                complexity="medium",
                estimated_time="3-4 Minuten",
                icon="file-transfer",
                parameters=[
                    ParameterDefinition(
                        name="source_agent",
                        data_type="agent",
                        required=True,
                        description="Quell-Agent",
                        chat_prompt="Von welchem System sollen die Dateien übertragen werden?",
                        examples=["gtasswvv15778", "ProdServer01"]
                    ),
                    ParameterDefinition(
                        name="target_agent",
                        data_type="agent",
                        required=True,
                        description="Ziel-Agent",
                        chat_prompt="Zu welchem System sollen die Dateien übertragen werden?",
                        examples=["gtasswvw15779", "BackupServer01"]
                    ),
                    ParameterDefinition(
                        name="source_path",
                        data_type="file_path",
                        required=True,
                        description="Quell-Dateipfad",
                        chat_prompt="Welche Datei oder welches Verzeichnis soll übertragen werden?",
                        examples=["E:\\data\\export.txt", "/home/user/files/*"]
                    ),
                    ParameterDefinition(
                        name="target_path",
                        data_type="file_path",
                        required=True,
                        description="Ziel-Dateipfad",
                        chat_prompt="Wohin sollen die Dateien übertragen werden?",
                        examples=["E:\\backup\\", "/mnt/storage/incoming/"]
                    )
                ]
            ),
            "SAP": JobTypeSchema(
                job_type="SAP",
                display_name="SAP Job",
                description="SAP Report oder Programm mit Parametern",
                complexity="medium",
                estimated_time="4-6 Minuten",
                icon="database",
                parameters=[
                    ParameterDefinition(
                        name="system",
                        data_type="enum",
                        required=True,
                        description="SAP System",
                        enum_values=["PA1_100", "PA1_200", "PT1_100", "PD1_100"],
                        chat_prompt="In welchem SAP-System soll der Report ausgeführt werden?",
                        examples=["PA1_100", "PT1_100"]
                    ),
                    ParameterDefinition(
                        name="report",
                        data_type="string",
                        required=True,
                        description="SAP Report Name",
                        chat_prompt="Welchen SAP-Report möchten Sie ausführen?",
                        examples=["RBDAGAIN", "RSUSR003", "SE16"]
                    ),
                    ParameterDefinition(
                        name="variant",
                        data_type="string",
                        required=False,
                        description="Report-Variante",
                        chat_prompt="Soll eine bestimmte Variante verwendet werden? (optional)",
                        examples=["VAR01", "PROD_VARIANT"]
                    ),
                    ParameterDefinition(
                        name="batch_user",
                        data_type="string",
                        required=False,
                        default_value="Batch_PUR",
                        description="Batch-Benutzer",
                        chat_prompt="Welcher Batch-User soll verwendet werden?",
                        examples=["Batch_PUR", "SAP_BATCH"]
                    )
                ]
            )
        }

        return fallback_schemas.get(job_type, JobTypeSchema(
            job_type=job_type,
            display_name=f"Custom {job_type}",
            description=f"Benutzerdefinierter {job_type} Job",
            complexity="complex",
            estimated_time="8-12 Minuten",
            icon="settings",
            parameters=[]
        ))

    def _save_schemas(self, schemas: Dict[str, JobTypeSchema]) -> None:
        """Speichert die generierten Schemas als JSON"""
        try:
            # Konvertiere zu serialisierbarem Dict
            schemas_dict = {}
            for job_type, schema in schemas.items():
                schemas_dict[job_type] = asdict(schema)

            # Füge Metadaten hinzu
            output_data = {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Auto-generated job type schemas from XML analysis",
                "schemas": schemas_dict
            }

            # Speichere als JSON
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Schemas saved to: {self.output_file}")

        except Exception as e:
            logger.error(f"Failed to save schemas: {str(e)}")
            raise

    def load_schemas(self) -> Dict[str, JobTypeSchema]:
        """Lädt gespeicherte Schemas"""
        try:
            if not self.output_file.exists():
                logger.warning("No schemas file found, generating new schemas...")
                return {}

            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            schemas = {}
            for job_type, schema_data in data.get('schemas', {}).items():
                # Konvertiere Parameter zurück zu ParameterDefinition Objekten
                parameters = []
                for param_data in schema_data.get('parameters', []):
                    param = ParameterDefinition(**param_data)
                    parameters.append(param)

                # Erstelle JobTypeSchema
                schema_data['parameters'] = parameters
                schema = JobTypeSchema(**schema_data)
                schemas[job_type] = schema

            logger.info(f"Loaded {len(schemas)} schemas from {self.output_file}")
            return schemas

        except Exception as e:
            logger.error(f"Failed to load schemas: {str(e)}")
            return {}

# Singleton instance
_schema_analyzer = None

def get_schema_analyzer() -> SchemaAnalyzer:
    """Get schema analyzer singleton"""
    global _schema_analyzer
    if _schema_analyzer is None:
        _schema_analyzer = SchemaAnalyzer()
    return _schema_analyzer

async def analyze_schemas_if_needed() -> Dict[str, JobTypeSchema]:
    """Convenience function: Analyse schemas if not exist, otherwise load"""
    analyzer = get_schema_analyzer()

    # Prüfe ob Schemas bereits existieren
    existing_schemas = analyzer.load_schemas()

    if existing_schemas:
        logger.info("Using existing schemas")
        return existing_schemas
    else:
        logger.info("No existing schemas found, starting analysis...")
        return await analyzer.analyze_all_xml_templates()