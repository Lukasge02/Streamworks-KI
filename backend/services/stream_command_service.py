"""
Stream Command Service - Natural Language Command Interpreter for Streams
Ermöglicht Befehle wie "Benenne Stream X in Y um" oder "Setze Agent auf UC4_UNIX_01"
Now with AI-powered flexible command understanding!
"""

import re
from enum import Enum
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass
from difflib import SequenceMatcher
from pydantic import BaseModel, Field


from services.db import db
from config import config


class CommandType(Enum):
    """Supported command types"""

    RENAME = "rename"
    UPDATE_PARAM = "update_param"
    CHANGE_SCHEDULE = "change_schedule"
    DUPLICATE = "duplicate"
    DELETE = "delete"
    OPEN = "open"
    CREATE = "create"
    UNKNOWN = "unknown"


# Pydantic schema for AI command extraction
class AICommandResult(BaseModel):
    """Structured output for AI command analysis"""

    command_type: Literal[
        "rename", "update_param", "open", "duplicate", "delete", "create", "unknown"
    ] = Field(
        description="Art des Befehls: 'rename' zum Umbenennen, 'update_param' zum Ändern von Parametern, 'open' zum Öffnen, 'duplicate' zum Duplizieren, 'delete' zum Löschen"
    )

    # For RENAME commands
    stream_name: Optional[str] = Field(
        default=None,
        description="Name oder Teil des Namens des Streams, der gefunden werden soll",
    )
    new_stream_name: Optional[str] = Field(
        default=None, description="Neuer Name für den Stream (nur bei 'rename')"
    )

    # For UPDATE_PARAM commands - can update multiple params at once!
    param_changes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Dictionary mit Parameter-Änderungen, z.B. {'agent_detail': 'UC4_UNIX_01', 'short_description': 'Meine Beschreibung'}",
    )

    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Konfidenz der Erkennung"
    )

    explanation: Optional[str] = Field(
        default=None, description="Kurze Erklärung was erkannt wurde"
    )


# AI System Prompt for Command Analysis
COMMAND_SYSTEM_PROMPT = """Du bist ein Experte für die Interpretation von natürlicher Sprache zu Streamworks Stream-Befehlen.

## DEINE AUFGABE
Analysiere den Benutzer-Befehl und extrahiere:
1. Den Befehlstyp (rename, update_param, open, duplicate, delete)
2. Den betroffenen Stream (Name oder Teil davon)
3. Die gewünschten Änderungen

## BEFEHLSTYPEN

### RENAME (Umbenennen)
Schlüsselwörter: "umbenennen", "rename", "neuer name", "namen ändern", "heißen"
Beispiele:
- "Benenne test123 in neuername um" → rename, stream_name: "test123", new_stream_name: "neuername"
- "Der Stream BACKUP soll jetzt BACKUP_DAILY heißen" → rename
- "Stream XYZ umbenennen zu ABC" → rename

### UPDATE_PARAM (Parameter ändern)
Schlüsselwörter: "setze", "ändere", "wechsle", "auf ... ändern", Parameter-Namen
Beispiele:
- "Setze den Agent auf UC4_UNIX_01" → update_param, param_changes: {"agent_detail": "UC4_UNIX_01"}
- "Ändere die Beschreibung zu 'Mein Backup Job'" → update_param, param_changes: {"short_description": "Mein Backup Job"}
- "Der Zeitplan soll täglich um 8 Uhr sein" → update_param, param_changes: {"schedule": "täglich", "start_time": "08:00"}
- "Priorität auf 5 setzen" → update_param, param_changes: {"stream_priority": "5"}

### OPEN (Öffnen)
Schlüsselwörter: "öffne", "zeige", "bearbeite", "gehe zu"
Beispiele:
- "Öffne Stream test123" → open, stream_name: "test123"
- "Zeige mir den BACKUP Stream" → open, stream_name: "BACKUP"

### DUPLICATE (Duplizieren)
Schlüsselwörter: "dupliziere", "kopiere", "clone", "erstelle kopie"
Beispiele:
- "Dupliziere den Stream" → duplicate
- "Kopiere BACKUP als BACKUP_V2" → duplicate, stream_name: "BACKUP"

### DELETE (Löschen)
Schlüsselwörter: "lösche", "entferne", "delete"
Beispiele:
- "Lösche Stream XYZ" → delete, stream_name: "XYZ"

## PARAMETER MAPPING

Übersetze natürliche Sprache zu Parameter-Keys:
- "Agent", "Server", "Host" → agent_detail
- "Name" (beim ändern, nicht umbenennen) → stream_name  
- "Beschreibung", "Description" → short_description
- "Zeitplan", "Schedule" → schedule
- "Startzeit", "Zeit", "um X Uhr" → start_time
- "Priorität", "Priority" → stream_priority
- "Queue", "Warteschlange" → stream_queue
- "Script", "Befehl", "Command" → main_script
- "Dokumentation", "Doku" → stream_documentation
- "Besitzer", "Owner", "Verantwortlicher" → stream_owner
- "Quell-Server", "Source" → source_agent
- "Ziel-Server", "Target" → target_agent
- "Quelldatei", "Source File" → source_file_pattern
- "Zieldatei", "Target File" → target_file_path

## WICHTIG

1. Wenn der Benutzer nur einen Stream-Namen erwähnt ohne Aktion → "open"
2. Bei Mehrfach-Änderungen: Alle in param_changes sammeln!
3. Bei Umbenennung: IMMER command_type "rename" verwenden, NIEMALS update_param für stream_name nutzen!
4. Der stream_name ist der zu suchende Stream, new_stream_name ist der neue Name bei Umbenennung
5. Sei flexibel bei der Schreibweise und Formulierung!

Antworte immer auf Deutsch im Feld explanation."""


@dataclass
class ParsedCommand:
    """Result of command parsing"""

    command_type: CommandType
    stream_name: Optional[str] = None
    new_name: Optional[str] = None
    param_key: Optional[str] = None  # For single param update (regex fallback)
    param_value: Optional[str] = None  # For single param update (regex fallback)
    param_changes: Optional[Dict[str, str]] = None  # For multiple param updates (AI)
    raw_text: str = ""
    confidence: float = 0.0
    explanation: Optional[str] = None  # AI explanation


@dataclass
class CommandResult:
    """Result of command execution"""

    success: bool
    session_id: Optional[str] = None
    action: str = ""
    changes: Optional[Dict[str, Any]] = None
    original_name: Optional[str] = None
    redirect_url: Optional[str] = None
    message: str = ""
    suggestions: Optional[List[str]] = None


class StreamCommandService:
    """
    Service for parsing and executing natural language commands on streams.
    Uses AI (OpenAI) for flexible command understanding with regex fallback.

    Examples:
    - "Benenne test123 in teststream456 um"
    - "Ändere den Agent auf UC4_UNIX_01"
    - "Der Zeitplan soll täglich um 8 Uhr sein"
    - "Dupliziere Stream xyz"
    - "Öffne Stream test123"
    """

    # Parameter name mappings (German -> internal key) - for fallback
    PARAM_MAPPINGS = {
        "agent": "agent_detail",
        "server": "agent_detail",
        "script": "main_script",
        "befehl": "main_script",
        "command": "main_script",
        "name": "stream_name",
        "beschreibung": "short_description",
        "description": "short_description",
        "quelle": "source_agent",
        "source": "source_agent",
        "ziel": "target_agent",
        "target": "target_agent",
        "quelldatei": "source_file_pattern",
        "zieldatei": "target_file_path",
        "zeitplan": "schedule",
        "schedule": "schedule",
        "startzeit": "start_time",
        "timeout": "job_timeout",
        "priorität": "stream_priority",
        "priority": "stream_priority",
        "user": "run_as_user",
        "benutzer": "run_as_user",
    }

    def __init__(self):
        self._db = db
        self._extractor = None
        self._ai_available = False

        # Use unified ParameterExtractor for AI commands
        if config.OPENAI_API_KEY:
            try:
                from services.ai.parameter_extractor import ParameterExtractor

                self._extractor = ParameterExtractor()
                self._ai_available = True
                print(
                    "StreamCommandService: Using unified ParameterExtractor for AI commands"
                )
            except Exception as e:
                print(
                    f"StreamCommandService: AI init failed, using regex fallback: {e}"
                )

    def parse_command(self, text: str) -> "ParsedCommand":
        """
        Parse a natural language command using unified AI (with regex fallback).

        Args:
            text: The natural language command text

        Returns:
            ParsedCommand with type, target, and parameters
        """
        text = text.strip()

        # Try unified AI-powered analysis first
        if self._ai_available and self._extractor:
            try:
                ai_result = self._extractor.analyze_command(
                    message=text,
                    current_params=None,
                    has_session_context=False,  # From streams page, no active session
                )

                if ai_result and ai_result.action_type != "question":
                    return self._convert_unified_result(ai_result, text)
            except Exception as e:
                print(f"AI parsing failed, using regex fallback: {e}")

        # Fallback to regex-based parsing
        return self._parse_with_regex(text)

    def _convert_unified_result(self, ai_result, raw_text: str) -> "ParsedCommand":
        """Convert UnifiedCommandResult to ParsedCommand format"""
        action_type_map = {
            "rename": CommandType.RENAME,
            "update_params": CommandType.UPDATE_PARAM,
            "open": CommandType.OPEN,
            "duplicate": CommandType.DUPLICATE,
            "delete": CommandType.DELETE,
            "create": CommandType.CREATE,
            "question": CommandType.UNKNOWN,
        }

        cmd_type = action_type_map.get(ai_result.action_type, CommandType.UNKNOWN)

        return ParsedCommand(
            command_type=cmd_type,
            stream_name=ai_result.target_stream_name,
            new_name=ai_result.new_stream_name,
            param_changes=ai_result.param_changes if ai_result.param_changes else None,
            raw_text=raw_text,
            confidence=ai_result.confidence,
            explanation=ai_result.explanation,
        )

    def _parse_with_regex(self, text: str) -> "ParsedCommand":
        """Fallback regex-based parsing"""
        text_lower = text.lower()

        # RENAME patterns
        rename_patterns = [
            r"(?:benenne|rename|umbenennen)\s+(?:stream\s+)?['\"]?(.+?)['\"]?\s+(?:in|zu|nach)\s+['\"]?(.+?)['\"]?(?:\s+um)?$",
            r"(?:ändere|change)\s+(?:den\s+)?(?:stream\s+)?(?:name|namen)\s+(?:von\s+)?['\"]?(.+?)['\"]?\s+(?:in|zu|auf)\s+['\"]?(.+?)['\"]?$",
        ]

        for pattern in rename_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return ParsedCommand(
                    command_type=CommandType.RENAME,
                    stream_name=match.group(1).strip(),
                    new_name=match.group(2).strip(),
                    raw_text=text,
                    confidence=0.9,
                )

        # OPEN patterns
        open_patterns = [
            r"(?:öffne|open|zeige|show|bearbeite|edit)\s+(?:stream\s+)?['\"]?(.+?)['\"]?$",
        ]

        for pattern in open_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return ParsedCommand(
                    command_type=CommandType.OPEN,
                    stream_name=match.group(1).strip(),
                    raw_text=text,
                    confidence=0.85,
                )

        # DUPLICATE patterns
        duplicate_patterns = [
            r"(?:dupliziere|kopiere|duplicate|copy|clone)\s+(?:stream\s+)?['\"]?(.+?)['\"]?$",
        ]

        for pattern in duplicate_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return ParsedCommand(
                    command_type=CommandType.DUPLICATE,
                    stream_name=match.group(1).strip(),
                    raw_text=text,
                    confidence=0.9,
                )

        # Unknown command
        return ParsedCommand(
            command_type=CommandType.UNKNOWN, raw_text=text, confidence=0.0
        )

    def _normalize_param_key(self, param: str) -> str:
        """Convert German/common param names to internal keys"""
        param_lower = param.lower().strip()
        return self.PARAM_MAPPINGS.get(param_lower, param_lower.replace(" ", "_"))

    def find_stream_by_name(self, name: str, threshold: float = 0.6) -> List[Dict]:
        """
        Fuzzy search for streams matching the given name.

        Args:
            name: Stream name to search for
            threshold: Minimum similarity score (0-1)

        Returns:
            List of matching sessions sorted by similarity
        """
        try:
            sessions = self._db.list_sessions(limit=100)
        except Exception as e:
            print(f"Error fetching sessions: {e}")
            return []

        matches = []
        name_lower = name.lower().strip()

        for session in sessions:
            session_name = (session.get("name") or "").lower()

            # Exact match
            if session_name == name_lower:
                matches.append({**session, "_score": 1.0})
                continue

            # Partial match
            if name_lower in session_name or session_name in name_lower:
                score = len(name_lower) / max(len(session_name), len(name_lower))
                if score >= threshold:
                    matches.append({**session, "_score": score})
                continue

            # Fuzzy match using SequenceMatcher
            score = SequenceMatcher(None, name_lower, session_name).ratio()
            if score >= threshold:
                matches.append({**session, "_score": score})

        # Sort by score descending
        matches.sort(key=lambda x: x["_score"], reverse=True)
        return matches

    def execute_command(
        self, command: ParsedCommand, session_id: Optional[str] = None
    ) -> CommandResult:
        """
        Execute a parsed command.

        Args:
            command: The parsed command to execute
            session_id: Optional session ID (for context-bound commands like UPDATE_PARAM)

        Returns:
            CommandResult with execution details
        """
        if command.command_type == CommandType.UNKNOWN:
            return CommandResult(
                success=False,
                message="Befehl nicht erkannt. Versuche z.B. 'Benenne test123 in neuername um'",
                suggestions=[
                    "Benenne [name] in [neuer name] um",
                    "Öffne [stream name]",
                    "Setze [parameter] auf [wert]",
                    "Dupliziere [stream name]",
                ],
            )

        if command.command_type == CommandType.RENAME:
            return self._execute_rename(command)

        if command.command_type == CommandType.DUPLICATE:
            return self._execute_duplicate(command)

        if command.command_type == CommandType.OPEN:
            return self._execute_open(command)

        if command.command_type == CommandType.UPDATE_PARAM:
            return self._execute_update_param(command, session_id)

        if command.command_type == CommandType.CHANGE_SCHEDULE:
            return self._execute_change_schedule(command, session_id)

        if command.command_type == CommandType.DELETE:
            return self._execute_delete(command)

        return CommandResult(
            success=False,
            message=f"Befehlstyp '{command.command_type.value}' noch nicht implementiert",
        )

    def _execute_rename(self, command: ParsedCommand) -> CommandResult:
        """Execute a RENAME command"""
        matches = self.find_stream_by_name(command.stream_name)

        if not matches:
            return CommandResult(
                success=False,
                message=f"Kein Stream mit Namen '{command.stream_name}' gefunden.",
                suggestions=self._get_similar_names(command.stream_name),
            )

        # Use best match
        target = matches[0]
        session_id = target["id"]
        original_name = target.get("name", "")

        # Get full session data and update
        session_data = self._db.get_session(session_id)
        if not session_data:
            return CommandResult(
                success=False,
                message=f"Session {session_id} konnte nicht geladen werden.",
            )

        # Prepare changes (don't save yet - let user confirm in editor)
        changes = {"stream_name": command.new_name}

        return CommandResult(
            success=True,
            session_id=session_id,
            action="rename",
            changes=changes,
            original_name=original_name,
            redirect_url=f"/streams/{session_id}?apply=rename&stream_name={command.new_name}",
            message=f"Stream '{original_name}' wird in '{command.new_name}' umbenannt. Bitte speichern zum Bestätigen.",
        )

    def _execute_duplicate(self, command: ParsedCommand) -> CommandResult:
        """Execute a DUPLICATE command"""
        matches = self.find_stream_by_name(command.stream_name)

        if not matches:
            return CommandResult(
                success=False,
                message=f"Kein Stream mit Namen '{command.stream_name}' gefunden.",
                suggestions=self._get_similar_names(command.stream_name),
            )

        target = matches[0]

        return CommandResult(
            success=True,
            session_id=target["id"],
            action="duplicate",
            original_name=target.get("name", ""),
            redirect_url=f"/streams?action=duplicate&id={target['id']}",
            message=f"Stream '{target.get('name')}' wird dupliziert.",
        )

    def _execute_open(self, command: ParsedCommand) -> CommandResult:
        """Execute an OPEN command"""
        matches = self.find_stream_by_name(command.stream_name)

        if not matches:
            return CommandResult(
                success=False,
                message=f"Kein Stream mit Namen '{command.stream_name}' gefunden.",
                suggestions=self._get_similar_names(command.stream_name),
            )

        target = matches[0]

        return CommandResult(
            success=True,
            session_id=target["id"],
            action="open",
            original_name=target.get("name", ""),
            redirect_url=f"/streams/{target['id']}",
            message=f"Öffne Stream '{target.get('name')}'.",
        )

    def _execute_update_param(
        self, command: ParsedCommand, session_id: Optional[str]
    ) -> CommandResult:
        """Execute an UPDATE_PARAM command - supports both AI (param_changes) and regex (param_key/value)"""

        # Determine the target session
        target_session_id = session_id
        original_name = None

        # If a stream name is provided, find it
        if command.stream_name:
            matches = self.find_stream_by_name(command.stream_name)
            if matches:
                target = matches[0]
                target_session_id = target["id"]
                original_name = target.get("name", "")
            else:
                return CommandResult(
                    success=False,
                    message=f"Kein Stream mit Namen '{command.stream_name}' gefunden.",
                    suggestions=self._get_similar_names(command.stream_name),
                )

        if not target_session_id:
            return CommandResult(
                success=False,
                message="Kein Stream ausgewählt. Bitte erst einen Stream öffnen oder einen Stream-Namen nennen.",
            )

        # Collect all changes
        changes = {}

        # AI-based: multiple param changes
        if command.param_changes:
            changes.update(command.param_changes)

        # Legacy regex-based: single param
        if command.param_key and command.param_value:
            changes[command.param_key] = command.param_value

        if not changes:
            return CommandResult(
                success=False, message="Keine Parameter-Änderungen erkannt."
            )

        # Build redirect URL with all params
        import urllib.parse

        param_query = "&".join(
            f"{k}={urllib.parse.quote(str(v))}" for k, v in changes.items()
        )

        # Format message
        if len(changes) == 1:
            key, value = list(changes.items())[0]
            message = f"Parameter '{key}' wird auf '{value}' gesetzt."
        else:
            changes_str = ", ".join(f"{k}={v}" for k, v in changes.items())
            message = f"Parameter werden geändert: {changes_str}"

        if command.explanation:
            message = f"{command.explanation} - {message}"

        return CommandResult(
            success=True,
            session_id=target_session_id,
            action="update_param",
            changes=changes,
            original_name=original_name,
            redirect_url=f"/streams/{target_session_id}?apply=param&{param_query}",
            message=message,
        )

    def _execute_change_schedule(
        self, command: ParsedCommand, session_id: Optional[str]
    ) -> CommandResult:
        """Execute a CHANGE_SCHEDULE command"""
        if not session_id:
            return CommandResult(
                success=False,
                message="Kein Stream ausgewählt. Bitte erst einen Stream öffnen.",
            )

        # Parse schedule value
        schedule_value = command.param_value
        changes = {}

        # Try to extract time
        time_match = re.search(r"(\d{1,2}):(\d{2})", schedule_value)
        if time_match:
            changes["start_time"] = (
                f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
            )

        # Try to extract frequency
        if "täglich" in schedule_value.lower() or "daily" in schedule_value.lower():
            changes["schedule"] = "täglich"
        elif (
            "wöchentlich" in schedule_value.lower()
            or "weekly" in schedule_value.lower()
        ):
            changes["schedule"] = "wöchentlich"
        elif (
            "monatlich" in schedule_value.lower() or "monthly" in schedule_value.lower()
        ):
            changes["schedule"] = "monatlich"

        if not changes:
            changes["schedule"] = schedule_value

        return CommandResult(
            success=True,
            session_id=session_id,
            action="change_schedule",
            changes=changes,
            message=f"Zeitplan wird aktualisiert: {changes}",
        )

    def _execute_delete(self, command: ParsedCommand) -> CommandResult:
        """Execute a DELETE command (with confirmation)"""
        matches = self.find_stream_by_name(command.stream_name)

        if not matches:
            return CommandResult(
                success=False,
                message=f"Kein Stream mit Namen '{command.stream_name}' gefunden.",
                suggestions=self._get_similar_names(command.stream_name),
            )

        target = matches[0]

        # Don't actually delete - require confirmation
        return CommandResult(
            success=True,
            session_id=target["id"],
            action="delete_confirm",
            original_name=target.get("name", ""),
            redirect_url=f"/streams?action=delete&id={target['id']}",
            message=f"⚠️ Stream '{target.get('name')}' wirklich löschen? Bitte im UI bestätigen.",
        )

    def _get_similar_names(self, name: str, limit: int = 5) -> List[str]:
        """Get list of similar stream names for suggestions"""
        try:
            sessions = self._db.list_sessions(limit=100)
            names = [s.get("name", "") for s in sessions if s.get("name")]

            # Sort by similarity
            scored = [
                (n, SequenceMatcher(None, name.lower(), n.lower()).ratio())
                for n in names
            ]
            scored.sort(key=lambda x: x[1], reverse=True)

            return [n for n, _ in scored[:limit]]
        except Exception:
            return []


# Global singleton instance
stream_command_service = StreamCommandService()
