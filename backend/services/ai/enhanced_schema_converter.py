"""
Enhanced Schema Converter für LangExtract Integration
Konvertiert Streamworks Schemas in optimierte Few-Shot Examples für LangExtract
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class EnhancedSchemaConverter:
    """
    Konvertiert Streamworks unified_stream_schemas.json in LangExtract-optimierte Examples

    Features:
    - Generiert realistische Few-Shot Examples
    - Optimiert für deutsche Sprache und Streamworks Domäne
    - Integriert Source Grounding Information
    - Erstellt Job-Type spezifische Prompts
    """

    def __init__(self, schema_path: Optional[str] = None):
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            self.schema_path = Path(__file__).parent.parent.parent / "templates" / "unified_stream_schemas.json"

        self.converted_schemas = {}
        self.few_shot_examples = {}

    def load_and_convert_schemas(self) -> Dict[str, Any]:
        """Load und konvertiere alle Schemas"""

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                original_schemas = json.load(f)

            logger.info("🔄 Converting Streamworks schemas to LangExtract format...")

            # Extract base data
            common_stream_params = original_schemas.get('common_stream_parameters', [])
            job_type_schemas = original_schemas.get('job_type_schemas', {})

            # Convert each job type
            for job_type, schema_data in job_type_schemas.items():
                converted = self._convert_job_type_schema(
                    job_type,
                    schema_data,
                    common_stream_params
                )
                self.converted_schemas[job_type] = converted

            # Generate comprehensive few-shot examples
            self._generate_comprehensive_examples()

            logger.info(f"✅ Converted {len(self.converted_schemas)} job type schemas")
            return self.converted_schemas

        except Exception as e:
            logger.error(f"❌ Schema conversion failed: {e}")
            return {}

    def _convert_job_type_schema(
        self,
        job_type: str,
        schema_data: Dict[str, Any],
        common_stream_params: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Konvertiert ein einzelnes Job-Type Schema"""

        logger.info(f"🔧 Converting {job_type} schema...")

        # Base schema information
        converted = {
            "job_type": job_type,
            "display_name": schema_data.get('display_name', job_type),
            "description": schema_data.get('description', ''),
            "complexity": schema_data.get('complexity', 'medium'),

            # LangExtract specific
            "extraction_prompt": self._build_extraction_prompt(job_type, schema_data, common_stream_params),
            "few_shot_examples": self._generate_few_shot_examples(job_type, schema_data, common_stream_params),

            # Parameter definitions
            "stream_parameters": common_stream_params,
            "job_parameters": schema_data.get('job_parameters', []),

            # Detection configuration
            "detection_config": schema_data.get('detection_config', {}),

            # Validation
            "required_parameters": self._extract_required_parameters(
                common_stream_params,
                schema_data.get('job_parameters', [])
            ),

            # Metadata
            "converted_at": datetime.now().isoformat(),
            "original_schema": schema_data
        }

        return converted

    def _build_extraction_prompt(
        self,
        job_type: str,
        schema_data: Dict[str, Any],
        common_stream_params: List[Dict[str, Any]]
    ) -> str:
        """Erstellt optimierten Extraction Prompt für LangExtract"""

        # Job-type spezifische Prompts
        job_specific_prompts = {
            "FILE_TRANSFER": """
Extract file transfer parameters from the German user message.

Focus on identifying:
- Source and target systems/agents (server names, agent IDs)
- File patterns, paths, and directories
- Transfer settings and configurations
- Stream metadata (name, description, schedule)

Look for keywords like: datentransfer, übertragung, server, agent, dateien, von, nach, zu
            """.strip(),

            "SAP": """
Extract SAP system parameters from the German user message.

Focus on identifying:
- SAP system names and mandants (PA1, PT1, GT123, etc.)
- Report names, transactions, variants
- Export/import formats and settings
- Fabrikkalender, table names, system connections
- Stream metadata (name, description, schedule)

Look for keywords like: sap, export, import, system, kalender, tabelle, mandant
            """.strip(),

            "STANDARD": """
Extract standard process parameters from the German user message.

Focus on identifying:
- Process types and workflow settings
- Input/output formats and configurations
- Scheduling and automation settings
- General stream parameters
- Stream metadata (name, description, schedule)

Look for keywords like: prozess, verarbeitung, standard, workflow, automatisch
            """.strip()
        }

        base_prompt = job_specific_prompts.get(job_type, f"Extract {job_type} stream parameters from user message.")

        # Add parameter details
        stream_params_info = self._format_parameters_for_prompt(common_stream_params, "Stream")
        job_params_info = self._format_parameters_for_prompt(schema_data.get('job_parameters', []), "Job-specific")

        full_prompt = f"""
{base_prompt}

STREAM PARAMETERS (required for all streams):
{stream_params_info}

{job_type} SPECIFIC PARAMETERS:
{job_params_info}

Return extracted parameters with source grounding information.
        """.strip()

        return full_prompt

    def _format_parameters_for_prompt(self, parameters: List[Dict[str, Any]], category: str) -> str:
        """Formatiert Parameter für Prompt"""

        formatted = []
        for param in parameters:
            name = param.get('name', '')
            data_type = param.get('data_type', 'string')
            description = param.get('description', '')
            required = "REQUIRED" if param.get('required', False) else "optional"
            examples = param.get('examples', [])

            example_str = f"Examples: {', '.join(str(ex) for ex in examples[:3])}" if examples else ""

            formatted.append(f"- {name} ({data_type}, {required}): {description} {example_str}")

        return "\n".join(formatted)

    def _generate_few_shot_examples(
        self,
        job_type: str,
        schema_data: Dict[str, Any],
        common_stream_params: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generiert realistische Few-Shot Examples für LangExtract"""

        logger.info(f"📝 Generating few-shot examples for {job_type}...")

        examples = []

        if job_type == "FILE_TRANSFER":
            examples = [
                {
                    "input": "Ich brauche einen Datentransfer von GT123_Server nach BASF_Agent für alle CSV Dateien aus dem Export-Verzeichnis",
                    "output": {
                        "StreamName": "GT123_BASF_Transfer",
                        "ShortDescription": "CSV Transfer GT123 zu BASF",
                        "source_agent": "GT123_Server",
                        "target_agent": "BASF_Agent",
                        "source_path": "/export/*.csv",
                        "JobCategory": "FILE_TRANSFER"
                    },
                    "source_grounding": {
                        "source_agent": {"text": "GT123_Server", "start": 43, "end": 54},
                        "target_agent": {"text": "BASF_Agent", "start": 60, "end": 70},
                        "source_path": {"text": "CSV Dateien aus dem Export-Verzeichnis", "start": 80, "end": 119}
                    }
                },
                {
                    "input": "Transfer von LocalAgent_001 zu TargetServer_002: alle PDF Dokumente synchronisieren täglich um 6 Uhr",
                    "output": {
                        "StreamName": "Daily_PDF_Sync",
                        "ShortDescription": "Tägliche PDF Synchronisation",
                        "source_agent": "LocalAgent_001",
                        "target_agent": "TargetServer_002",
                        "source_path": "*.pdf",
                        "SchedulingRequiredFlag": True,
                        "JobCategory": "FILE_TRANSFER"
                    },
                    "source_grounding": {
                        "source_agent": {"text": "LocalAgent_001", "start": 13, "end": 27},
                        "target_agent": {"text": "TargetServer_002", "start": 31, "end": 47},
                        "source_path": {"text": "PDF Dokumente", "start": 54, "end": 67},
                        "SchedulingRequiredFlag": {"text": "täglich um 6 Uhr", "start": 84, "end": 101}
                    }
                },
                {
                    "input": "Dateiübertragung zwischen Server001 und Server002 für Backup-Zwecke mit maximalen 10 Ausführungen",
                    "output": {
                        "StreamName": "Backup_Transfer_Stream",
                        "ShortDescription": "Backup Transfer Server001->002",
                        "source_agent": "Server001",
                        "target_agent": "Server002",
                        "MaxStreamRuns": 10,
                        "JobCategory": "FILE_TRANSFER"
                    },
                    "source_grounding": {
                        "source_agent": {"text": "Server001", "start": 25, "end": 34},
                        "target_agent": {"text": "Server002", "start": 40, "end": 49},
                        "MaxStreamRuns": {"text": "maximalen 10 Ausführungen", "start": 73, "end": 99}
                    }
                }
            ]

        elif job_type == "SAP":
            examples = [
                {
                    "input": "SAP Kalender Export von System PA1_100 Tabelle ZTV_CALENDAR als Excel Format täglich",
                    "output": {
                        "StreamName": "SAP_Calendar_Export",
                        "ShortDescription": "PA1 Kalender Export zu Excel",
                        "system": "PA1_100",
                        "report": "ZTV_CALENDAR",
                        "variant": "EXCEL_DAILY",
                        "SchedulingRequiredFlag": True,
                        "JobCategory": "SAP"
                    },
                    "source_grounding": {
                        "system": {"text": "PA1_100", "start": 32, "end": 39},
                        "report": {"text": "ZTV_CALENDAR", "start": 48, "end": 60},
                        "variant": {"text": "Excel Format", "start": 65, "end": 77},
                        "SchedulingRequiredFlag": {"text": "täglich", "start": 78, "end": 85}
                    }
                },
                {
                    "input": "Export aus SAP GT123_PRD mit Report RSUSR003 Variante WEEKLY für Benutzerdaten",
                    "output": {
                        "StreamName": "GT123_User_Export",
                        "ShortDescription": "GT123 Benutzer Export wöchentlich",
                        "system": "GT123_PRD",
                        "report": "RSUSR003",
                        "variant": "WEEKLY",
                        "JobCategory": "SAP"
                    },
                    "source_grounding": {
                        "system": {"text": "GT123_PRD", "start": 16, "end": 25},
                        "report": {"text": "RSUSR003", "start": 37, "end": 45},
                        "variant": {"text": "WEEKLY", "start": 55, "end": 61}
                    }
                },
                {
                    "input": "SAP-System PT1_100 Fabrikkalender Daten exportieren mit Standard-Variant",
                    "output": {
                        "StreamName": "PT1_Factory_Calendar",
                        "ShortDescription": "PT1 Fabrikkalender Export",
                        "system": "PT1_100",
                        "report": "FACTORY_CALENDAR",
                        "variant": "STANDARD",
                        "JobCategory": "SAP"
                    },
                    "source_grounding": {
                        "system": {"text": "PT1_100", "start": 11, "end": 18},
                        "report": {"text": "Fabrikkalender", "start": 19, "end": 33},
                        "variant": {"text": "Standard-Variant", "start": 55, "end": 71}
                    }
                }
            ]

        elif job_type == "STANDARD":
            examples = [
                {
                    "input": "Standard Prozess für Datenverarbeitung automatisch alle 4 Stunden mit Fehlerbehandlung",
                    "output": {
                        "StreamName": "Auto_Data_Processing",
                        "ShortDescription": "4h Datenverarbeitung automatisch",
                        "process_type": "DataProcessing",
                        "schedule_interval": "4hours",
                        "error_handling": True,
                        "SchedulingRequiredFlag": True,
                        "JobCategory": "STANDARD"
                    },
                    "source_grounding": {
                        "process_type": {"text": "Datenverarbeitung", "start": 20, "end": 37},
                        "schedule_interval": {"text": "alle 4 Stunden", "start": 51, "end": 66},
                        "error_handling": {"text": "Fehlerbehandlung", "start": 71, "end": 87}
                    }
                },
                {
                    "input": "Workflow für Batch-Verarbeitung mit Input-Format CSV und Output als JSON, maximal 20 Läufe",
                    "output": {
                        "StreamName": "CSV_to_JSON_Batch",
                        "ShortDescription": "CSV zu JSON Batch-Verarbeitung",
                        "process_type": "BatchProcessing",
                        "input_format": "CSV",
                        "output_format": "JSON",
                        "MaxStreamRuns": 20,
                        "JobCategory": "STANDARD"
                    },
                    "source_grounding": {
                        "process_type": {"text": "Batch-Verarbeitung", "start": 13, "end": 31},
                        "input_format": {"text": "CSV", "start": 53, "end": 56},
                        "output_format": {"text": "JSON", "start": 72, "end": 76},
                        "MaxStreamRuns": {"text": "maximal 20 Läufe", "start": 78, "end": 95}
                    }
                }
            ]

        # Add metadata to examples
        for example in examples:
            example["job_type"] = job_type
            example["generated_at"] = datetime.now().isoformat()
            example["language"] = "de"

        return examples

    def _extract_required_parameters(
        self,
        stream_params: List[Dict[str, Any]],
        job_params: List[Dict[str, Any]]
    ) -> List[str]:
        """Extrahiert erforderliche Parameter"""

        required = []

        for param in stream_params:
            if param.get('required', False):
                required.append(param['name'])

        for param in job_params:
            if param.get('required', False):
                required.append(param['name'])

        return required

    def _generate_comprehensive_examples(self):
        """Generiert umfassende Example-Datenbank"""

        logger.info("📚 Generating comprehensive example database...")

        # Job-Type Detection Examples
        self.few_shot_examples["job_type_detection"] = [
            {
                "input": "Datentransfer zwischen Servern konfigurieren",
                "output": "FILE_TRANSFER",
                "confidence": 0.9,
                "reasoning": "Keywords: datentransfer, servern"
            },
            {
                "input": "SAP Export aus GT123 System einrichten",
                "output": "SAP",
                "confidence": 0.95,
                "reasoning": "Keywords: sap, export, system"
            },
            {
                "input": "Standard Workflow für Datenverarbeitung",
                "output": "STANDARD",
                "confidence": 0.8,
                "reasoning": "Keywords: standard, workflow"
            }
        ]

        # Parameter Extraction Examples (cross job-type)
        self.few_shot_examples["parameter_extraction"] = {
            "stream_names": [
                {"input": "für den DataExport_v2 Stream", "output": "DataExport_v2"},
                {"input": "neuer Transfer namens BASF_Daily", "output": "BASF_Daily"},
                {"input": "Stream heißt SAP_Weekly_Export", "output": "SAP_Weekly_Export"}
            ],
            "descriptions": [
                {"input": "täglicher Export zwischen Systemen", "output": "Täglicher Export zwischen Systemen"},
                {"input": "automatische Synchronisation", "output": "Automatische Synchronisation"},
                {"input": "backup prozess für daten", "output": "Backup Prozess für Daten"}
            ],
            "scheduling": [
                {"input": "täglich um 6 Uhr", "output": True, "schedule": "daily_6am"},
                {"input": "alle 4 Stunden", "output": True, "schedule": "every_4h"},
                {"input": "manuell ausführen", "output": False, "schedule": "manual"}
            ]
        }

        # Edge Cases und Error Handling
        self.few_shot_examples["edge_cases"] = [
            {
                "input": "irgendwas mit daten machen",
                "output": "UNCLEAR",
                "reasoning": "Zu vage, keine spezifischen Keywords"
            },
            {
                "input": "SAP Transfer zwischen Server001 und Agent002",
                "output": "MIXED_KEYWORDS",
                "reasoning": "SAP + Transfer Keywords gemischt"
            }
        ]

    def export_langextract_schemas(self, output_path: Optional[str] = None) -> str:
        """Exportiert konvertierte Schemas für LangExtract"""

        if not self.converted_schemas:
            self.load_and_convert_schemas()

        if output_path is None:
            output_path = self.schema_path.parent / "langextract_schemas.json"
        else:
            output_path = Path(output_path)

        # Create comprehensive LangExtract format
        langextract_format = {
            "version": "langextract_v1.0",
            "generated_at": datetime.now().isoformat(),
            "source_schema": str(self.schema_path),
            "description": "Streamworks schemas converted for LangExtract integration",

            # Job Type Detection
            "job_type_detection": {
                "prompt": "Identify the Streamworks job type from German user input",
                "examples": self.few_shot_examples.get("job_type_detection", []),
                "available_types": list(self.converted_schemas.keys())
            },

            # Parameter Extraction per Job Type
            "parameter_extraction": self.converted_schemas,

            # Cross-cutting Examples
            "common_examples": self.few_shot_examples.get("parameter_extraction", {}),

            # Edge Cases
            "edge_cases": self.few_shot_examples.get("edge_cases", []),

            # Metadata
            "language": "de",
            "domain": "streamworks_configuration",
            "extraction_method": "source_grounded"
        }

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(langextract_format, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ LangExtract schemas exported to: {output_path}")
        return str(output_path)

    def validate_examples(self) -> Dict[str, Any]:
        """Validiert generierte Examples"""

        logger.info("🔍 Validating generated examples...")

        validation_results = {
            "total_examples": 0,
            "valid_examples": 0,
            "validation_errors": [],
            "coverage_report": {}
        }

        for job_type, schema in self.converted_schemas.items():
            examples = schema.get("few_shot_examples", [])
            validation_results["total_examples"] += len(examples)

            # Validate each example
            for i, example in enumerate(examples):
                try:
                    # Check required fields
                    required_fields = ["input", "output", "source_grounding"]
                    for field in required_fields:
                        if field not in example:
                            raise ValueError(f"Missing required field: {field}")

                    # Validate source grounding
                    source_grounding = example.get("source_grounding", {})
                    input_text = example.get("input", "")

                    for param_name, grounding in source_grounding.items():
                        start = grounding.get("start", 0)
                        end = grounding.get("end", 0)
                        text = grounding.get("text", "")

                        # Check if grounding text matches input
                        if input_text[start:end] != text:
                            raise ValueError(f"Source grounding mismatch for {param_name}")

                    validation_results["valid_examples"] += 1

                except Exception as e:
                    validation_results["validation_errors"].append({
                        "job_type": job_type,
                        "example_index": i,
                        "error": str(e)
                    })

            # Coverage report
            required_params = schema.get("required_parameters", [])
            covered_params = set()

            for example in examples:
                covered_params.update(example.get("output", {}).keys())

            validation_results["coverage_report"][job_type] = {
                "required_parameters": len(required_params),
                "covered_parameters": len(covered_params & set(required_params)),
                "coverage_percentage": len(covered_params & set(required_params)) / max(len(required_params), 1) * 100
            }

        validation_results["success_rate"] = validation_results["valid_examples"] / max(validation_results["total_examples"], 1) * 100

        logger.info(f"📊 Validation complete: {validation_results['success_rate']:.1f}% success rate")
        return validation_results


# Factory Function

def convert_streamworks_schemas_for_langextract(
    schema_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Factory function für Schema-Konvertierung"""

    converter = EnhancedSchemaConverter(schema_path)
    schemas = converter.load_and_convert_schemas()

    # Export for LangExtract
    exported_path = converter.export_langextract_schemas(output_path)

    # Validate
    validation = converter.validate_examples()

    return {
        "converted_schemas": schemas,
        "exported_path": exported_path,
        "validation_results": validation,
        "converter_instance": converter
    }


# Quick Test Function

def test_schema_conversion():
    """Quick test der Schema-Konvertierung"""

    logger.info("🧪 Testing schema conversion...")

    result = convert_streamworks_schemas_for_langextract()

    print(f"✅ Conversion complete!")
    print(f"📁 Exported to: {result['exported_path']}")
    print(f"📊 Validation: {result['validation_results']['success_rate']:.1f}% success")
    print(f"📈 Coverage: {len(result['converted_schemas'])} job types converted")

    return result


if __name__ == "__main__":
    test_schema_conversion()