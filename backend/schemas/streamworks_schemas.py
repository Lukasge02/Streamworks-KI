"""
StreamWorks Parameter Schemas - Separate für jeden Stream-Typ
Definiert die erwartete Struktur für SAP, Transfer und Standard Streams
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class StreamType(Enum):
    STANDARD = "STANDARD"
    SAP = "SAP"
    FILE_TRANSFER = "FILE_TRANSFER"
    CUSTOM = "CUSTOM"

# ============================================
# BASIS SCHEMA - Gemeinsame Parameter
# ============================================

BASE_STREAM_SCHEMA = {
    "required": {
        "stream_name": {
            "type": "string",
            "description": "Eindeutiger Name des Streams",
            "prompt": "Wie soll der Stream heißen? (z.B. PROD_Daily_Report oder ZSW-T-SAP-Export)",
            "examples": ["StrJ_AC_SAP_Export", "ZSW-T-WIN-FILE-TRANSFER", "PROD_Batch_Processing"],
            "validation": r"^[A-Za-z0-9_-]+$"
        },
        "agent_detail": {
            "type": "string",
            "description": "Agent auf dem der Stream läuft",
            "prompt": "Auf welchem Agent soll der Stream laufen?",
            "examples": ["gtlnmiwvm1636", "gtasswvv15778", "prodagent001"],
            "default": "gtlnmiwvm1636"
        },
        "short_description": {
            "type": "string",
            "description": "Kurzbeschreibung des Stream-Zwecks",
            "prompt": "Beschreiben Sie kurz, was dieser Stream macht:",
            "max_length": 200
        },
        "calendar_id": {
            "type": "string",
            "description": "Kalender für Scheduling",
            "prompt": "Welcher Kalender soll verwendet werden? (Standard: UATDefaultCalendar)",
            "default": "UATDefaultCalendar",
            "examples": ["UATDefaultCalendar", "ProductionCalendar", "TestCalendar"]
        }
    },
    "optional": {
        "max_stream_runs": {
            "type": "integer",
            "description": "Maximale parallele Ausführungen",
            "prompt": "Wie viele parallele Läufe sind erlaubt? (1-1000)",
            "default": 10,
            "range": [1, 1000]
        },
        "stream_documentation": {
            "type": "string",
            "description": "Ausführliche Dokumentation",
            "prompt": "Möchten Sie eine ausführliche Dokumentation hinzufügen?",
            "multiline": True
        },
        "scheduling_required": {
            "type": "boolean",
            "description": "Ob Scheduling erforderlich ist",
            "default": True
        }
    }
}

# ============================================
# SAP STREAM SCHEMA
# ============================================

SAP_STREAM_SCHEMA = {
    **BASE_STREAM_SCHEMA,
    "sap_specific": {
        "required": {
            "sap_system": {
                "type": "string",
                "description": "SAP System ID",
                "prompt": "Welches SAP-System? (z.B. ZTV, PA1, PRD)",
                "examples": ["ZTV", "PA1", "PRD", "QAS"],
                "validation": r"^[A-Z0-9]{3}$"
            },
            "sap_mandant": {
                "type": "string",
                "description": "SAP Mandant/Client",
                "prompt": "Welcher SAP-Mandant? (z.B. 100, 300)",
                "examples": ["100", "300", "500"],
                "validation": r"^\d{3}$"
            },
            "sap_transaction": {
                "type": "string",
                "description": "SAP Transaktion oder Report",
                "prompt": "Welche SAP-Transaktion oder welcher Report? (z.B. EXE_CAL_EXPORT, SE16)",
                "examples": ["EXE_CAL_EXPORT", "SE16", "SM37", "RSBDCOS0"]
            }
        },
        "optional": {
            "jexa_parameters": {
                "type": "dict",
                "description": "jexa4S spezifische Parameter",
                "prompt": "Zusätzliche jexa4S Parameter? (optional)",
                "structure": {
                    "user": "SAP User",
                    "variant": "Report-Variante",
                    "output_file": "Ausgabedatei",
                    "output_dir": "Ausgabeverzeichnis"
                }
            },
            "sap_job_type": {
                "type": "enum",
                "description": "Art des SAP Jobs",
                "prompt": "Welche Art von SAP-Job? (Export/Import/Report)",
                "values": ["EXPORT", "IMPORT", "REPORT", "BATCH"],
                "default": "EXPORT"
            },
            "calendar_export": {
                "type": "boolean",
                "description": "Ob Fabrikkalender exportiert wird",
                "prompt": "Soll ein SAP-Fabrikkalender exportiert werden?",
                "default": False
            }
        }
    }
}

# ============================================
# FILE TRANSFER STREAM SCHEMA
# ============================================

FILE_TRANSFER_SCHEMA = {
    **BASE_STREAM_SCHEMA,
    "transfer_specific": {
        "required": {
            "source_agent": {
                "type": "string",
                "description": "Quell-Agent für Dateiübertragung",
                "prompt": "Von welchem Agent sollen die Dateien übertragen werden?",
                "examples": ["gtlnmiwvm1636", "fileserver001", "localhost"]
            },
            "target_agent": {
                "type": "string",
                "description": "Ziel-Agent für Dateiübertragung",
                "prompt": "Zu welchem Agent sollen die Dateien übertragen werden?",
                "examples": ["gtasswvv15778", "backupserver", "archivehost"]
            },
            "source_path": {
                "type": "string",
                "description": "Quellpfad der Dateien",
                "prompt": "Welcher Quellpfad? (z.B. C:\\data\\export oder /home/data/)",
                "examples": ["C:\\temp", "/var/export", "\\\\server\\share"]
            },
            "target_path": {
                "type": "string",
                "description": "Zielpfad der Dateien",
                "prompt": "Welcher Zielpfad? (z.B. C:\\archive oder /backup/)",
                "examples": ["C:\\archive", "/backup/data", "\\\\backup\\archive"]
            }
        },
        "optional": {
            "transfer_method": {
                "type": "enum",
                "description": "Übertragungsmethode",
                "prompt": "Welche Übertragungsmethode? (COPY/FTP/SFTP/RSYNC)",
                "values": ["COPY", "FTP", "SFTP", "RSYNC", "SCP"],
                "default": "COPY"
            },
            "file_pattern": {
                "type": "string",
                "description": "Dateifilter/Pattern",
                "prompt": "Welche Dateien? (z.B. *.xml, *.csv, report_*.txt)",
                "examples": ["*.xml", "*.csv", "report_*.txt", "*_EXPORT.XML"],
                "default": "*.*"
            },
            "delete_source": {
                "type": "boolean",
                "description": "Quelldateien nach Transfer löschen",
                "prompt": "Sollen die Quelldateien nach dem Transfer gelöscht werden?",
                "default": False
            },
            "archive_mode": {
                "type": "boolean",
                "description": "Archivierung aktiviert",
                "prompt": "Sollen übertragene Dateien archiviert werden?",
                "default": False
            },
            "platform": {
                "type": "enum",
                "description": "Plattform/OS für Transfer",
                "prompt": "Auf welcher Plattform? (Windows/Linux/Unix)",
                "values": ["Windows", "Linux", "Unix", "AIX", "SLES12", "SLES15"],
                "default": "Windows"
            }
        }
    }
}

# ============================================
# STANDARD STREAM SCHEMA
# ============================================

STANDARD_STREAM_SCHEMA = {
    **BASE_STREAM_SCHEMA,
    "standard_specific": {
        "required": {
            "main_script": {
                "type": "string",
                "description": "Hauptskript oder Befehl",
                "prompt": "Welches Skript oder welcher Befehl soll ausgeführt werden?",
                "examples": ["python process.py", "batch_job.bat", "./run_report.sh"],
                "multiline": True
            },
            "job_type": {
                "type": "enum",
                "description": "Betriebssystem/Plattform",
                "prompt": "Auf welchem System läuft der Job? (Windows/Linux/Unix)",
                "values": ["Windows", "Linux", "Unix", "None"],
                "default": "Windows"
            }
        },
        "optional": {
            "working_directory": {
                "type": "string",
                "description": "Arbeitsverzeichnis",
                "prompt": "In welchem Verzeichnis soll das Skript ausgeführt werden?",
                "examples": ["C:\\scripts", "/opt/batch", "/home/user/jobs"]
            },
            "parameters": {
                "type": "string",
                "description": "Skript-Parameter",
                "prompt": "Welche Parameter soll das Skript erhalten?",
                "examples": ["--input data.csv --output result.txt", "-v -f config.ini"]
            },
            "environment_variables": {
                "type": "dict",
                "description": "Umgebungsvariablen",
                "prompt": "Benötigen Sie spezielle Umgebungsvariablen?",
                "structure": {
                    "PATH": "Zusätzliche Pfade",
                    "CONFIG": "Konfigurationsdatei"
                }
            },
            "timeout": {
                "type": "integer",
                "description": "Maximale Laufzeit in Minuten",
                "prompt": "Maximale Laufzeit? (in Minuten, 0 = unbegrenzt)",
                "default": 0,
                "range": [0, 1440]
            }
        }
    }
}

# ============================================
# SCHEMA SELECTOR UND VALIDATOR
# ============================================

def get_schema_for_type(stream_type: StreamType) -> Dict[str, Any]:
    """Gibt das passende Schema für den Stream-Typ zurück"""
    schemas = {
        StreamType.SAP: SAP_STREAM_SCHEMA,
        StreamType.FILE_TRANSFER: FILE_TRANSFER_SCHEMA,
        StreamType.STANDARD: STANDARD_STREAM_SCHEMA,
        StreamType.CUSTOM: STANDARD_STREAM_SCHEMA  # Fallback zu Standard
    }
    return schemas.get(stream_type, STANDARD_STREAM_SCHEMA)

def get_required_parameters(stream_type: StreamType) -> List[str]:
    """Gibt alle erforderlichen Parameter für einen Stream-Typ zurück"""
    schema = get_schema_for_type(stream_type)
    required = []

    # Base required
    required.extend(schema.get("required", {}).keys())

    # Type-specific required
    type_key = f"{stream_type.value.lower()}_specific"
    if type_key in schema:
        required.extend(schema[type_key].get("required", {}).keys())

    return required

def get_missing_parameters(collected: Dict[str, Any], stream_type: StreamType) -> List[str]:
    """Identifiziert fehlende erforderliche Parameter"""
    required = get_required_parameters(stream_type)
    return [param for param in required if param not in collected or not collected[param]]

def generate_prompt_for_parameter(param_name: str, stream_type: StreamType) -> str:
    """Generiert intelligente Prompts für fehlende Parameter"""
    schema = get_schema_for_type(stream_type)

    # Suche in allen Schema-Bereichen
    for section in ["required", "optional", f"{stream_type.value.lower()}_specific"]:
        if section in schema:
            if section.endswith("_specific"):
                # Type-specific parameters
                for subsection in ["required", "optional"]:
                    if subsection in schema[section]:
                        if param_name in schema[section][subsection]:
                            param_def = schema[section][subsection][param_name]
                            return param_def.get("prompt", f"Bitte geben Sie {param_name} an:")
            else:
                # Base parameters
                if param_name in schema[section]:
                    param_def = schema[section][param_name]
                    return param_def.get("prompt", f"Bitte geben Sie {param_name} an:")

    return f"Bitte geben Sie einen Wert für '{param_name}' an:"

def get_parameter_examples(param_name: str, stream_type: StreamType) -> List[str]:
    """Gibt Beispielwerte für einen Parameter zurück"""
    schema = get_schema_for_type(stream_type)

    # Suche Parameter-Definition
    for section in ["required", "optional", f"{stream_type.value.lower()}_specific"]:
        if section in schema:
            if section.endswith("_specific"):
                for subsection in ["required", "optional"]:
                    if subsection in schema[section]:
                        if param_name in schema[section][subsection]:
                            param_def = schema[section][subsection][param_name]
                            return param_def.get("examples", [])
            else:
                if param_name in schema[section]:
                    param_def = schema[section][param_name]
                    return param_def.get("examples", [])

    return []