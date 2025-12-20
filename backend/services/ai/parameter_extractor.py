"""
AI-Powered Parameter Extractor for Streamworks
Uses OpenAI GPT-4o-mini with structured output via instructor
Improved with real Streamworks XML examples for better extraction
"""

from typing import Dict, Any, Optional, List
from openai import OpenAI
import instructor

from config import config
from .schemas import StreamworksParams, UnifiedCommandResult


# Improved system prompt with real XML examples
SYSTEM_PROMPT = """Du bist ein Experte für Streamworks Job-Automatisierung bei Arvato Systems.
Deine Aufgabe: Extrahiere Parameter aus natürlicher Sprache für Streamworks XML-Streams.

## JOB-TYP ERKENNUNG (KRITISCH!)

1. **FILE_TRANSFER** - Wenn Dateien zwischen Servern bewegt werden:
   - Schlüsselwörter: "kopieren", "übertragen", "transferieren", "von X nach Y", "Datei", "sync"
   - Muster: "Dateien von ServerA nach ServerB"
   - Benötigt: source_agent, target_agent, source_file_pattern, target_file_path

2. **SAP** - Wenn SAP-System involviert ist:
   - Schlüsselwörter: "SAP", "Report", "Transaktion", "P01", "PA1", "ZTV", "ZREPORT"
   - Muster: "SAP Report XYZ ausführen"
   - Benötigt: sap_report oder sap_system

3. **STANDARD** - Für Scripts und Befehle:
   - Schlüsselwörter: "Script", "ausführen", "Befehl", "Python", "Shell", "Backup"
   - Muster: "Python Script auf Server ausführen"
   - Benötigt: main_script, agent_detail

## PARAMETER EXTRAKTION

Extrahiere ALLE genannten Informationen:

- **Server/Agent**: "auf LinuxServer" → agent_detail: "LinuxServer"
- **Zeitplan**: "täglich um 8 Uhr" → schedule: "täglich", start_time: "08:00"
- **Dateipfade**: "/data/*.csv" → source_file_pattern oder target_file_path
- **Quelle/Ziel**: "von Alpha nach Beta" → source_agent: "Alpha", target_agent: "Beta"

## BEISPIELE

Eingabe: "Dateien von ServerAlpha nach ServerBeta kopieren"
→ job_type: "FILE_TRANSFER", source_agent: "ServerAlpha", target_agent: "ServerBeta"

Eingabe: "Python Backup Script auf LinuxServer ausführen, täglich um 6 Uhr"  
→ job_type: "STANDARD", main_script: "python backup.py", agent_detail: "LinuxServer", schedule: "täglich", start_time: "06:00"

Eingabe: "SAP Report ZTV123 jeden Morgen um 8 starten"
→ job_type: "SAP", sap_report: "ZTV123", schedule: "täglich", start_time: "08:00"

## STREAM-NAME PRIORISIERUNG

**WICHTIG: Wenn der Benutzer einen Stream-Namen explizit nennt (z.B. "Stream NIGHTLY_BACKUP" oder "Name: XYZ"), verwende DIESEN Namen!**

Nur wenn kein Name genannt wird, generiere automatisch:
- File Transfer: "FT_[SOURCE]_[TARGET]" z.B. "FT_ALPHA_BETA"
- Standard: "[BESCHREIBUNG]_JOB" z.B. "BACKUP_DAILY"
- SAP: "SAP_[REPORT]" z.B. "SAP_ZTV123"

## RÜCKFRAGEN

Stelle eine follow_up_question für fehlende PFLICHT-Parameter:
- FILE_TRANSFER: stream_name, source_agent, target_agent, source_file_pattern
- STANDARD: stream_name, agent_detail, main_script (oder Beschreibung)
- SAP: stream_name, sap_report

Antworte auf Deutsch."""


# Unified Command System Prompt - used by both StreamCommandService and KI-Assistent
UNIFIED_COMMAND_PROMPT = """Du bist ein Experte für Streamworks Stream-Verwaltung bei Arvato Systems.

## DEINE AUFGABE
Analysiere den Benutzer-Befehl und erkenne:
1. Die gewünschte AKTION (Parameter ändern, umbenennen, öffnen, etc.)
2. Den betroffenen STREAM (falls genannt)
3. Die gewünschten PARAMETER-ÄNDERUNGEN

## AKTIONEN

### update_params (Standard für Parameter-Änderungen)
Wenn Parameter geändert werden sollen, ohne den Stream umzubenennen.
Beispiele:
- "Setze den Agent auf UC4_UNIX_01" → update_params, param_changes: {"agent_detail": "UC4_UNIX_01"}
- "Ändere die Beschreibung zu 'Mein Job'" → update_params, param_changes: {"short_description": "Mein Job"}
- "Priorität auf 5 und täglich um 8 Uhr" → update_params, param_changes: {"stream_priority": "5", "schedule": "täglich", "start_time": "08:00"}

### rename (Stream umbenennen)
- "Benenne test123 in BACKUP um" → rename, target_stream_name: "test123", new_stream_name: "BACKUP"
- "Der Stream soll jetzt XYZ heißen" → rename

### open (Stream öffnen)
- "Öffne Stream test123" → open, target_stream_name: "test123"
- "Zeige mir BACKUP" → open

### duplicate (Stream kopieren)
- "Dupliziere meinen-stream" → duplicate, target_stream_name: "meinen-stream"

### delete (Stream löschen)
- "Lösche Stream XYZ" → delete, target_stream_name: "XYZ"

## PARAMETER-KEYS (WICHTIG!)

Übersetze natürliche Sprache zu diesen exakten Keys:
- Agent/Server/Host → agent_detail
- Beschreibung/Description → short_description
- Dokumentation/Doku → stream_documentation
- Zeitplan/Schedule → schedule
- Startzeit/Zeit/Uhrzeit/"um X Uhr" → start_time
- Priorität/Priority → stream_priority
- Queue/Warteschlange → stream_queue
- Script/Befehl/Command → main_script
- Besitzer/Owner/Verantwortlicher → stream_owner
- Quell-Server/Source → source_agent
- Ziel-Server/Target → target_agent
- Quelldatei → source_file_pattern
- Zieldatei → target_file_path
- Name (bei Änderung, NICHT Umbenennung) → stream_name

## REGELN

1. Bei Umbenennung: IMMER action_type="rename" verwenden
2. Bei Parameter-Änderungen: action_type="update_params" mit param_changes Dict
3. Mehrere Parameter gleichzeitig: Alle in param_changes sammeln
4. Wenn nur Stream-Name genannt ohne Aktion → action_type="open"
5. target_stream_name nur setzen wenn ein ANDERER Stream genannt wird
6. Erklärung immer auf Deutsch

## BEISPIELE

Eingabe: "Setze den Agent auf UC4_UNIX_01 und die Priorität auf 5"
→ action_type: "update_params"
→ param_changes: {"agent_detail": "UC4_UNIX_01", "stream_priority": "5"}
→ explanation: "Agent und Priorität werden geändert."

Eingabe: "Der Stream test123 soll jetzt BACKUP_DAILY heißen"
→ action_type: "rename"
→ target_stream_name: "test123"
→ new_stream_name: "BACKUP_DAILY"
→ explanation: "Stream wird von 'test123' in 'BACKUP_DAILY' umbenannt."

Eingabe: "Täglich um 8 Uhr laufen"
→ action_type: "update_params"
→ param_changes: {"schedule": "täglich", "start_time": "08:00"}
→ explanation: "Zeitplan wird auf täglich um 08:00 Uhr gesetzt."
"""


class ParameterExtractor:
    """
    Extracts Streamworks parameters from natural language using AI
    """

    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY nicht konfiguriert!")

        self.client = instructor.from_openai(OpenAI(api_key=config.OPENAI_API_KEY))
        self.model = config.LLM_MODEL

    def analyze_command(
        self,
        message: str,
        current_params: Optional[Dict] = None,
        has_session_context: bool = False,
    ) -> "UnifiedCommandResult":
        """
        Unified command analysis for both StreamsPage and DetailPage.

        Args:
            message: The natural language command
            current_params: Current stream parameters (for context)
            has_session_context: True if command is within a stream editor

        Returns:
            UnifiedCommandResult with action type and parameter changes
        """
        from .schemas import UnifiedCommandResult

        messages = [{"role": "system", "content": UNIFIED_COMMAND_PROMPT}]

        # Add context about current parameters
        if current_params:
            params_str = ", ".join(f"{k}={v}" for k, v in current_params.items() if v)
            if params_str:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Aktueller Stream hat folgende Parameter: {params_str}",
                    }
                )

        # Add context about where the user is
        if has_session_context:
            messages.append(
                {
                    "role": "system",
                    "content": "Der Benutzer bearbeitet gerade einen Stream. Parameter-Änderungen beziehen sich auf diesen Stream.",
                }
            )

        messages.append({"role": "user", "content": message})

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=UnifiedCommandResult,
                messages=messages,
                temperature=0.1,
            )
            return result

        except Exception as e:
            print(f"Command analysis error: {e}")
            # Return fallback
            return UnifiedCommandResult(
                action_type="update_params",
                param_changes={},
                explanation=f"Fehler bei der Befehlsanalyse: {str(e)}",
                confidence=0.0,
            )

    def extract(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        existing_params: Optional[Dict] = None,
    ) -> StreamworksParams:
        """
        Extract parameters from user message
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add context of existing parameters
        if existing_params and any(v for v in existing_params.values() if v):
            params_str = ", ".join(
                f"{k}={v}"
                for k, v in existing_params.items()
                if v and k not in ["job_type", "confidence"]
            )
            context = f"Bereits bekannte Parameter: {params_str}"
            messages.append({"role": "system", "content": context})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=StreamworksParams,
                messages=messages,
                temperature=0.1,
            )

            # Auto-fill descriptions if missing
            result = self._autofill_fields(result)

            # Determine missing required fields
            result.missing_required = self._get_missing_required(result)

            # Generate follow-up question if needed
            if result.missing_required and not result.follow_up_question:
                result.follow_up_question = self._generate_follow_up(result)

            return result

        except Exception as e:
            # Log error for debugging
            print(f"Extraction error: {e}")

            return StreamworksParams(
                job_type="STANDARD",
                confidence=0.3,
                short_description=message[:50],
                follow_up_question="Es gab ein Problem bei der Verarbeitung. Bitte beschreiben Sie nochmal, was Ihr Stream machen soll.",
            )

    def _autofill_fields(self, params: StreamworksParams) -> StreamworksParams:
        """Automatically generate sensible defaults for missing fields"""

        # 1. Short Description (Max 50 chars)
        if not params.short_description:
            if params.stream_name:
                # Use stream name as base, remove spaces/underscores for compactness if needed, or just truncate
                base = f"{params.stream_name} Stream"
                params.short_description = base[:50]
            elif params.job_type == "FILE_TRANSFER":
                params.short_description = "File Transfer Stream"
            else:
                params.short_description = "Standard Stream"

        # Ensure hard limit of 50 chars
        if params.short_description and len(params.short_description) > 50:
            params.short_description = params.short_description[:47] + "..."

        # 2. Stream Documentation
        if not params.stream_documentation:
            job_readable = {
                "FILE_TRANSFER": "Dateitransfer",
                "STANDARD": "Standard-Job",
                "SAP": "SAP-Job",
            }.get(params.job_type, "Job")

            parts = [f"Automatischer {job_readable}"]
            if params.stream_name:
                parts.append(f"für {params.stream_name}")
            if params.agent_detail:
                parts.append(f"auf {params.agent_detail}")

            params.stream_documentation = " ".join(parts) + "."

        return params

    def _get_missing_required(self, params: StreamworksParams) -> List[str]:
        """Determine which required fields are missing based on job type"""
        missing = []

        # Stream name is always required
        if not params.stream_name:
            missing.append("stream_name")

        if params.job_type == "FILE_TRANSFER":
            if not params.source_agent:
                missing.append("source_agent")
            if not params.target_agent:
                missing.append("target_agent")
            if not params.source_file_pattern:
                missing.append("source_file_pattern")

        elif params.job_type == "STANDARD":
            if not params.main_script and not params.short_description:
                # If autofill is working, short_description should be present
                # But main_script is real functional requirement
                if not params.main_script:
                    missing.append("main_script")
            if not params.agent_detail:
                missing.append("agent_detail")

        elif params.job_type == "SAP":
            if not params.sap_report:
                missing.append("sap_report")

        return missing

    def _generate_follow_up(self, params: StreamworksParams) -> str:
        """Generate a follow-up question for missing parameters"""
        questions = {
            "stream_name": "Wie soll der Stream heißen?",
            "source_agent": "Von welchem Server sollen die Dateien kopiert werden?",
            "target_agent": "Auf welchen Server sollen die Dateien kopiert werden?",
            "source_file_pattern": "Welche Dateien sollen kopiert werden? (z.B. /data/*.csv)",
            "target_file_path": "In welches Verzeichnis sollen die Dateien kopiert werden?",
            "main_script": "Welches Script oder welcher Befehl soll ausgeführt werden?",
            "agent_detail": "Auf welchem Server soll das Script ausgeführt werden?",
            "sap_report": "Welcher SAP Report soll ausgeführt werden?",
        }

        if params.missing_required:
            first_missing = params.missing_required[0]
            return questions.get(
                first_missing, f"Bitte geben Sie noch {first_missing} an."
            )

        return None

    def merge_params(
        self, existing: Dict[str, Any], new_params: StreamworksParams
    ) -> Dict[str, Any]:
        """Merge new extracted params with existing ones"""
        result = existing.copy()

        # Update with new non-None values
        for field, value in new_params.model_dump().items():
            if value is not None and field not in [
                "missing_required",
                "follow_up_question",
                "confidence",
            ]:
                # Don't overwrite existing values with empty ones, UNLESS it's a refill
                # Basically, if new_params has a value (even if it's autofilled), use it
                # if the existing one is empty.

                # If new value is present
                if value:
                    result[field] = value

        return result
