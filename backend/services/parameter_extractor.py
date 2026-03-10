"""
AI-powered parameter extraction from natural language descriptions.

Uses OpenAI structured output to extract Streamworks automation parameters
from free-text descriptions, with job type detection and confidence scoring.
"""

import json
import logging
from pathlib import Path

import yaml
from openai import OpenAI

from config import get_settings

logger = logging.getLogger(__name__)

_PARAMETERS_PATH = Path(__file__).resolve().parent.parent / "config" / "parameters.yaml"


def _load_parameter_schema() -> dict:
    """
    Load the parameter definitions from parameters.yaml.

    Returns:
        The parsed YAML contents as a dict.
    """
    with open(_PARAMETERS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_schema_description(schema: dict) -> str:
    """
    Build a human-readable description of the parameter schema for the system prompt.

    Args:
        schema: The parsed parameters.yaml dict.

    Returns:
        A formatted string describing all parameter groups and their fields.
    """
    parts: list[str] = []

    raw_job_types = schema.get("job_types", [])
    job_types = list(raw_job_types.keys()) if isinstance(raw_job_types, dict) else list(raw_job_types)
    if job_types:
        parts.append(f"Unterstuetzte Job-Typen: {', '.join(job_types)}")
        parts.append("")

    for group in schema.get("parameter_groups", []):
        group_name = group.get("name", "Unbekannt")
        group_label = group.get("label", group_name)
        parts.append(f"## Parametergruppe: {group_label}")

        for param in group.get("parameters", []):
            key = param.get("key", "")
            label = param.get("label", key)
            param_type = param.get("type", "string")
            required = param.get("required", False)
            description = param.get("description", "")
            options = param.get("options", [])

            line = f"  - {key} ({label}): Typ={param_type}"
            if required:
                line += ", PFLICHTFELD"
            if description:
                line += f" - {description}"
            if options:
                line += f" [Optionen: {', '.join(str(o) for o in options)}]"
            parts.append(line)

        parts.append("")

    return "\n".join(parts)


def _build_json_schema(schema: dict) -> dict:
    """
    Build a JSON Schema for OpenAI structured output based on the parameter definitions.

    The schema defines:
    - job_type: The detected automation job type.
    - confidence: How confident the extraction is (0.0 to 1.0).
    - parameters: A flat dict of extracted parameter key-value pairs.
    - suggestions: A list of suggestions or clarification requests.

    Args:
        schema: The parsed parameters.yaml dict.

    Returns:
        A JSON Schema dict suitable for OpenAI response_format.
    """
    param_properties = {}
    for group in schema.get("parameter_groups", []):
        for param in group.get("parameters", []):
            key = param.get("key", "")
            param_type = param.get("type", "string")

            if param_type == "boolean":
                param_properties[key] = {"type": ["boolean", "null"]}
            elif param_type == "number" or param_type == "integer":
                param_properties[key] = {"type": ["number", "null"]}
            else:
                param_properties[key] = {"type": ["string", "null"]}

    raw_job_types = schema.get("job_types", ["STANDARD", "FILE_TRANSFER", "SAP"])
    job_types = list(raw_job_types.keys()) if isinstance(raw_job_types, dict) else list(raw_job_types)

    return {
        "type": "json_schema",
        "json_schema": {
            "name": "parameter_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "job_type": {
                        "type": "string",
                        "enum": job_types,
                    },
                    "confidence": {
                        "type": "number",
                    },
                    "parameters": {
                        "type": "object",
                        "properties": param_properties,
                        "required": list(param_properties.keys()),
                        "additionalProperties": False,
                    },
                    "suggestions": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["job_type", "confidence", "parameters", "suggestions"],
                "additionalProperties": False,
            },
        },
    }


SYSTEM_PROMPT = """\
Du bist ein Experte fuer Streamworks-Automatisierung und Parameter-Extraktion.

Deine Aufgabe ist es, aus einer natuerlichsprachlichen Beschreibung eines Automatisierungs-Jobs \
die relevanten Parameter zu extrahieren.

Hier ist das vollstaendige Parameter-Schema:

{schema_description}

Regeln:
1. Erkenne zuerst den Job-Typ (z.B. STANDARD, FILE_TRANSFER, SAP) anhand der Beschreibung.
2. Extrahiere alle Parameter, die in der Beschreibung erwaehnt oder impliziert werden.
3. Setze Parameter auf null, wenn sie nicht aus der Beschreibung ableitbar sind.
4. Vergib einen Confidence-Wert zwischen 0.0 und 1.0 basierend darauf, wie eindeutig die Beschreibung ist.
5. Gib hilfreiche Vorschlaege (suggestions) fuer fehlende Pflichtfelder oder Unklarheiten.
6. Achte besonders auf: Stream-Name, Ausfuehrungsplan (Schedule), Quell-/Zielpfade, Agent-Namen, \
Fehlerbehandlung und SAP-spezifische Parameter.
7. Bei Datumsangaben verwende das Format YYYY-MM-DD, bei Zeiten HH:MM.
8. Bei Schedules/Cron-Ausdruecken versuche den gewuenschten Ausfuehrungsplan zu erkennen.

Antworte ausschliesslich im vorgegebenen JSON-Format.
"""


def extract_parameters(description: str) -> dict:
    """
    Extract Streamworks automation parameters from a natural language description.

    Pipeline:
    1. Load the parameter schema from parameters.yaml.
    2. Build a system prompt with the full schema description.
    3. Call OpenAI with structured output (JSON Schema) for reliable extraction.
    4. Return the parsed result with job_type, confidence, parameters, and suggestions.

    Args:
        description: A free-text description of the desired automation job.

    Returns:
        A dict with keys:
        - job_type (str): Detected job type.
        - confidence (float): Extraction confidence 0.0-1.0.
        - parameters (dict): Extracted parameter key-value pairs.
        - suggestions (list[str]): Recommendations for the user.
    """
    settings = get_settings()
    schema = _load_parameter_schema()

    schema_description = _build_schema_description(schema)
    json_schema = _build_json_schema(schema)

    system_message = SYSTEM_PROMPT.format(schema_description=schema_description)

    client = OpenAI(api_key=settings.openai_api_key)

    logger.info(
        "Extracting parameters from description (%d chars)", len(description)
    )

    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": description},
        ],
        response_format=json_schema,
        temperature=0.1,
        max_tokens=4096,
    )

    raw_content = completion.choices[0].message.content or "{}"
    result = json.loads(raw_content)

    # Strip null values from parameters for a cleaner response
    if "parameters" in result:
        result["parameters"] = {
            k: v for k, v in result["parameters"].items() if v is not None
        }

    logger.info(
        "Extracted %d parameters (job_type=%s, confidence=%.2f)",
        len(result.get("parameters", {})),
        result.get("job_type", "UNKNOWN"),
        result.get("confidence", 0.0),
    )

    return result


# ---------------------------------------------------------------------------
# Quick Edit: parse natural-language edit instructions
# ---------------------------------------------------------------------------

FIELD_TO_STEP: dict[str, int] = {
    "stream_name": 1, "short_description": 1, "documentation": 1, "priority": 1,
    "contact_name": 2, "email": 2, "phone": 2, "team": 2,
    "job_type": 3,
    "agent": 4, "main_script": 4, "script_parameters": 4,
    "source_agent": 4, "target_agent": 4, "source_file_pattern": 4, "target_file_path": 4,
    "transfer_mode": 4, "overwrite": 4,
    "sap_system": 4, "sap_client": 4, "sap_report": 4, "sap_variant": 4,
    "schedule_frequency": 5, "start_time": 5, "calendar": 5,
}

FIELD_ALIASES: dict[str, str] = {
    "name": "stream_name",
    "stream-name": "stream_name",
    "streamname": "stream_name",
    "beschreibung": "short_description",
    "description": "short_description",
    "kurzbeschreibung": "short_description",
    "doku": "documentation",
    "dokumentation": "documentation",
    "prioritaet": "priority",
    "kontakt": "contact_name",
    "kontaktperson": "contact_name",
    "ansprechpartner": "contact_name",
    "e-mail": "email",
    "mail": "email",
    "telefon": "phone",
    "telefonnummer": "phone",
    "abteilung": "team",
    "jobtyp": "job_type",
    "job-typ": "job_type",
    "skript": "main_script",
    "script": "main_script",
    "parameter": "script_parameters",
    "quellagent": "source_agent",
    "zielagent": "target_agent",
    "quelldatei": "source_file_pattern",
    "zieldatei": "target_file_path",
    "zielpfad": "target_file_path",
    "ueberschreiben": "overwrite",
    "frequenz": "schedule_frequency",
    "zeitplan": "schedule_frequency",
    "startzeit": "start_time",
    "kalender": "calendar",
    "sap-system": "sap_system",
    "sap-mandant": "sap_client",
    "mandant": "sap_client",
    "report": "sap_report",
    "variante": "sap_variant",
}

FIELD_LABELS: dict[str, str] = {
    "stream_name": "Stream-Name",
    "short_description": "Kurzbeschreibung",
    "documentation": "Dokumentation",
    "priority": "Prioritaet",
    "contact_name": "Kontaktperson",
    "email": "E-Mail",
    "phone": "Telefon",
    "team": "Team/Abteilung",
    "job_type": "Job-Typ",
    "agent": "Agent",
    "main_script": "Skript",
    "script_parameters": "Skript-Parameter",
    "source_agent": "Quell-Agent",
    "target_agent": "Ziel-Agent",
    "source_file_pattern": "Quell-Datei",
    "target_file_path": "Ziel-Pfad",
    "transfer_mode": "Transfer-Modus",
    "overwrite": "Ueberschreiben",
    "sap_system": "SAP-System",
    "sap_client": "SAP-Mandant",
    "sap_report": "SAP-Report",
    "sap_variant": "SAP-Variante",
    "schedule_frequency": "Frequenz",
    "start_time": "Startzeit",
    "calendar": "Kalender",
}

EDIT_SYSTEM_PROMPT = """\
Du bist ein Assistent, der natuerlichsprachliche Bearbeitungsanweisungen fuer Streamworks-Streams parst.

Du bekommst:
1. Eine Bearbeitungsanweisung vom Benutzer
2. Eine Liste vorhandener Stream-Namen

Deine Aufgabe:
- Erkenne welcher Stream gemeint ist (target_stream_name)
- Erkenne welche Felder geaendert werden sollen
- Gib die Aenderungen als strukturiertes JSON zurueck

Verfuegbare Felder und ihre Aliase:
- stream_name (Name, Stream-Name)
- short_description (Beschreibung, Kurzbeschreibung)
- documentation (Dokumentation, Doku)
- priority (Prioritaet)
- contact_name (Kontakt, Kontaktperson, Ansprechpartner)
- email (E-Mail, Mail)
- phone (Telefon, Telefonnummer)
- team (Team, Abteilung)
- job_type (Job-Typ, Jobtyp)
- agent (Agent)
- main_script (Skript, Script)
- script_parameters (Parameter)
- source_agent (Quell-Agent)
- target_agent (Ziel-Agent)
- source_file_pattern (Quelldatei)
- target_file_path (Zieldatei, Zielpfad)
- transfer_mode (Transfer-Modus)
- overwrite (Ueberschreiben)
- sap_system (SAP-System)
- sap_client (SAP-Mandant, Mandant)
- sap_report (SAP-Report, Report)
- sap_variant (SAP-Variante, Variante)
- schedule_frequency (Frequenz, Zeitplan)
- start_time (Startzeit)
- calendar (Kalender)

Antworte IMMER mit genau diesem JSON-Format:
{
  "target_stream_name": "Name des Streams oder null",
  "changes": [
    {"field": "feldname", "new_value": "neuer Wert"}
  ],
  "message": "Kurze Erklaerung was geaendert wird"
}

Regeln:
- Verwende immer die technischen Feldnamen (z.B. "stream_name", nicht "Name")
- Wenn kein Stream-Name erkennbar ist, setze target_stream_name auf null
- Wenn die Anweisung unklar ist, setze changes auf [] und erklaere in message warum
- Gib nur Felder zurueck die tatsaechlich geaendert werden sollen
"""


def parse_edit_instruction(instruction: str, stream_names: list[str]) -> dict:
    """
    Parse a natural-language edit instruction using OpenAI.

    Args:
        instruction: The user's edit command in natural language.
        stream_names: List of existing stream names for matching.

    Returns:
        Dict with target_stream_name, changes, and message.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    names_text = ", ".join(stream_names) if stream_names else "(keine Streams vorhanden)"

    logger.info("Parsing edit instruction: %s", instruction[:100])

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EDIT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Vorhandene Streams: {names_text}\n\nAnweisung: {instruction}",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=1024,
    )

    raw = completion.choices[0].message.content or "{}"
    result = json.loads(raw)

    # Normalize field names through alias map
    for change in result.get("changes", []):
        field = change.get("field", "")
        if field in FIELD_ALIASES:
            change["field"] = FIELD_ALIASES[field]

    logger.info(
        "Parsed edit: target=%s, %d changes",
        result.get("target_stream_name"),
        len(result.get("changes", [])),
    )

    return result
