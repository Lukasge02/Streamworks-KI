"""
Central Parameter Schema for Streamworks
Single source of truth for all stream/job parameters with aliases, types, and descriptions.
Used by both StreamCommandService and ParameterExtractor.
"""

from typing import Dict, List, Literal, Optional
from dataclasses import dataclass


@dataclass
class ParamDefinition:
    """Definition of a stream/job parameter"""

    key: str
    label: str
    aliases: List[str]
    description: str
    param_type: Literal["string", "number", "boolean", "select", "textarea"]
    category: Literal[
        "stream",
        "job",
        "schedule",
        "contact",
        "file_transfer",
        "sap",
        "advanced",
        "system",
    ]
    options: Optional[List[str]] = None
    max_length: Optional[int] = None
    required_for: Optional[List[str]] = None  # Job types where this is required


# =============================================================================
# CENTRAL PARAMETER DEFINITIONS
# =============================================================================

PARAM_DEFINITIONS: Dict[str, ParamDefinition] = {
    # ============ STREAM LEVEL ============
    "stream_name": ParamDefinition(
        key="stream_name",
        label="Stream-Name",
        aliases=["name", "streamname", "stream"],
        description="Name des Streams",
        param_type="string",
        category="stream",
        required_for=["STANDARD", "FILE_TRANSFER", "SAP"],
    ),
    "short_description": ParamDefinition(
        key="short_description",
        label="Kurzbeschreibung",
        aliases=["beschreibung", "description", "desc", "kurzbeschreibung"],
        description="Kurze Beschreibung des Streams (max 50 Zeichen)",
        param_type="string",
        category="stream",
        max_length=50,
    ),
    "stream_documentation": ParamDefinition(
        key="stream_documentation",
        label="Dokumentation",
        aliases=["dokumentation", "doku", "documentation", "doc"],
        description="Ausführliche Dokumentation des Streams",
        param_type="textarea",
        category="stream",
    ),
    "stream_owner": ParamDefinition(
        key="stream_owner",
        label="Verantwortlicher",
        aliases=["owner", "besitzer", "verantwortlicher", "zuständig"],
        description="Verantwortliche Person oder Team",
        param_type="string",
        category="stream",
    ),
    "stream_path": ParamDefinition(
        key="stream_path",
        label="Stream-Pfad",
        aliases=["pfad", "path", "ordner", "folder"],
        description="Pfad/Ordner für den Stream, z.B. /Abteilung/Team",
        param_type="string",
        category="system",
    ),
    "stream_priority": ParamDefinition(
        key="stream_priority",
        label="Priorität",
        aliases=["priorität", "priority", "prio"],
        description="Priorität des Streams (0-10)",
        param_type="number",
        category="stream",
    ),
    "stream_queue": ParamDefinition(
        key="stream_queue",
        label="Queue",
        aliases=["queue", "warteschlange"],
        description="Queue Name für den Stream",
        param_type="string",
        category="stream",
    ),
    "max_stream_runs": ParamDefinition(
        key="max_stream_runs",
        label="Max. parallele Läufe",
        aliases=["max runs", "parallel", "max_runs"],
        description="Maximale Anzahl gleichzeitiger Stream-Runs",
        param_type="number",
        category="advanced",
    ),
    # ============ AGENT/SERVER ============
    "agent_detail": ParamDefinition(
        key="agent_detail",
        label="Agent/Server",
        aliases=["agent", "server", "host", "maschine", "rechner"],
        description="Standard-Agent/Server auf dem der Stream läuft",
        param_type="string",
        category="job",
        required_for=["STANDARD"],
    ),
    # ============ JOB LEVEL ============
    "job_name": ParamDefinition(
        key="job_name",
        label="Job-Name",
        aliases=["jobname", "job name", "job"],
        description="Name des Haupt-Jobs",
        param_type="string",
        category="job",
    ),
    "main_script": ParamDefinition(
        key="main_script",
        label="Script/Befehl",
        aliases=["script", "befehl", "command", "cmd", "skript"],
        description="Auszuführendes Script oder Befehl",
        param_type="textarea",
        category="job",
        required_for=["STANDARD"],
    ),
    "run_as_user": ParamDefinition(
        key="run_as_user",
        label="Ausführender User",
        aliases=["user", "benutzer", "run as", "runas"],
        description="OS User unter dem der Job läuft",
        param_type="string",
        category="job",
    ),
    "job_timeout": ParamDefinition(
        key="job_timeout",
        label="Timeout (Minuten)",
        aliases=["timeout", "zeitlimit", "max zeit"],
        description="Timeout in Minuten",
        param_type="number",
        category="job",
    ),
    # ============ SCHEDULE ============
    "schedule": ParamDefinition(
        key="schedule",
        label="Zeitplan",
        aliases=["zeitplan", "schedule", "frequenz", "häufigkeit"],
        description="Zeitplan: täglich, wöchentlich, monatlich, stündlich",
        param_type="select",
        category="schedule",
        options=["täglich", "wöchentlich", "monatlich", "stündlich", "manuell"],
    ),
    "start_time": ParamDefinition(
        key="start_time",
        label="Startzeit",
        aliases=["startzeit", "zeit", "uhrzeit", "time", "um"],
        description="Startzeit im Format HH:MM",
        param_type="string",
        category="schedule",
    ),
    "calendar_id": ParamDefinition(
        key="calendar_id",
        label="Kalender",
        aliases=["kalender", "calendar"],
        description="Kalender-ID für Scheduling",
        param_type="string",
        category="schedule",
    ),
    # ============ FILE TRANSFER ============
    "source_agent": ParamDefinition(
        key="source_agent",
        label="Quell-Server",
        aliases=["quelle", "source", "von", "quellserver", "quell-agent"],
        description="Server VON dem Dateien kopiert werden",
        param_type="string",
        category="file_transfer",
        required_for=["FILE_TRANSFER"],
    ),
    "target_agent": ParamDefinition(
        key="target_agent",
        label="Ziel-Server",
        aliases=["ziel", "target", "nach", "zielserver", "ziel-agent"],
        description="Server AUF den Dateien kopiert werden",
        param_type="string",
        category="file_transfer",
        required_for=["FILE_TRANSFER"],
    ),
    "source_file_pattern": ParamDefinition(
        key="source_file_pattern",
        label="Quelldatei/Pattern",
        aliases=["quelldatei", "source file", "datei", "file pattern", "source_path"],
        description="Quell-Dateipfad oder Pattern, z.B. /data/*.csv",
        param_type="string",
        category="file_transfer",
        required_for=["FILE_TRANSFER"],
    ),
    "target_file_path": ParamDefinition(
        key="target_file_path",
        label="Zielverzeichnis",
        aliases=["zieldatei", "target file", "zielordner", "target_path"],
        description="Ziel-Verzeichnis für die Dateien",
        param_type="string",
        category="file_transfer",
    ),
    # ============ SAP ============
    "sap_report": ParamDefinition(
        key="sap_report",
        label="SAP Report",
        aliases=["report", "sap report", "programm"],
        description="SAP Report/Programm Name",
        param_type="string",
        category="sap",
        required_for=["SAP"],
    ),
    "sap_system": ParamDefinition(
        key="sap_system",
        label="SAP System",
        aliases=["sap system", "system", "sid"],
        description="SAP System-ID, z.B. P01, D01",
        param_type="string",
        category="sap",
    ),
    "sap_variant": ParamDefinition(
        key="sap_variant",
        label="SAP Variante",
        aliases=["variante", "variant"],
        description="SAP Variante für den Report",
        param_type="string",
        category="sap",
    ),
    # ============ CONTACT ============
    "contact_name": ParamDefinition(
        key="contact_name",
        label="Kontakt Name",
        aliases=["kontakt", "contact", "ansprechpartner"],
        description="Name der Kontaktperson",
        param_type="string",
        category="contact",
    ),
    "contact_email": ParamDefinition(
        key="contact_email",
        label="E-Mail",
        aliases=["email", "mail", "e-mail"],
        description="E-Mail Adresse",
        param_type="string",
        category="contact",
    ),
    # ============ FLAGS ============
    "status_flag": ParamDefinition(
        key="status_flag",
        label="Aktiv",
        aliases=["aktiv", "active", "enabled", "status"],
        description="Stream ist aktiv/inaktiv",
        param_type="boolean",
        category="advanced",
    ),
    "deploy_as_active": ParamDefinition(
        key="deploy_as_active",
        label="Aktiv deployen",
        aliases=["deploy aktiv", "deploy active"],
        description="Direkt als aktiv deployen",
        param_type="boolean",
        category="advanced",
    ),
}


def get_param_by_alias(alias: str) -> Optional[str]:
    """
    Find the canonical parameter key by an alias.
    Returns the key if found, None otherwise.
    """
    alias_lower = alias.lower().strip()

    # Check exact key match first
    if alias_lower in PARAM_DEFINITIONS:
        return alias_lower

    # Check aliases
    for key, definition in PARAM_DEFINITIONS.items():
        if alias_lower in [a.lower() for a in definition.aliases]:
            return key

    return None


def get_all_param_keys() -> List[str]:
    """Get all parameter keys"""
    return list(PARAM_DEFINITIONS.keys())


def get_required_params(job_type: str) -> List[str]:
    """Get required parameters for a job type"""
    return [
        key
        for key, definition in PARAM_DEFINITIONS.items()
        if definition.required_for and job_type in definition.required_for
    ]


def build_alias_prompt() -> str:
    """
    Build a prompt section listing all parameters and their aliases
    for the AI to understand.
    """
    lines = ["## PARAMETER MAPPING", ""]
    lines.append("Übersetze natürliche Sprache zu Parameter-Keys:")

    for key, definition in PARAM_DEFINITIONS.items():
        aliases_str = ", ".join([f'"{a}"' for a in definition.aliases[:3]])
        lines.append(f"- {aliases_str} → {key}")

    return "\n".join(lines)
