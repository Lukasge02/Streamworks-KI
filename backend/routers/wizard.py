"""
Wizard router: session CRUD, AI parameter analysis, and XML generation.

All wizard session data is persisted in the Supabase 'sessions' table
(columns: id UUID, data JSONB, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ).
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models.wizard import (
    AnalyzeRequest,
    AnalyzeResponse,
    FieldChange,
    GenerateXmlRequest,
    GenerateXmlResponse,
    QuickEditApplyRequest,
    QuickEditPreview,
    QuickEditRequest,
    SaveStepRequest,
    WizardSession,
)
from services.db import get_db
from services.parameter_extractor import (
    FIELD_LABELS,
    FIELD_TO_STEP,
    extract_parameters,
    parse_edit_instruction,
)
from services.xml_generator import generate_xml

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


@router.post("/sessions", status_code=201)
def create_session():
    """Create a new empty wizard session."""
    db = get_db()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "id": session_id,
        "data": {},
        "created_at": now,
        "updated_at": now,
    }

    result = db.table("sessions").insert(row).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return {"id": session_id, "data": {}}


@router.get("/sessions")
def list_sessions():
    """List all wizard sessions, newest first."""
    db = get_db()

    result = (
        db.table("sessions")
        .select("id, data, created_at, updated_at")
        .order("created_at", desc=True)
        .execute()
    )

    return result.data or []


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    """Get a single wizard session by ID."""
    db = get_db()

    result = (
        db.table("sessions")
        .select("id, data, created_at, updated_at")
        .eq("id", session_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return result.data


@router.put("/sessions/{session_id}/steps")
def save_step(session_id: str, body: SaveStepRequest):
    """
    Save or update a single wizard step.

    Merges the step data into the session's data JSONB field under the key
    'step_{N}'. Existing keys in that step are overwritten; other steps are
    preserved.
    """
    db = get_db()

    # Fetch current session data
    existing = (
        db.table("sessions")
        .select("id, data")
        .eq("id", session_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = existing.data.get("data", {}) or {}
    step_key = f"step_{body.step}"
    session_data[step_key] = body.data

    now = datetime.now(timezone.utc).isoformat()

    result = (
        db.table("sessions")
        .update({"data": session_data, "updated_at": now})
        .eq("id", session_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save step")

    return result.data[0]


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str):
    """Delete a wizard session."""
    db = get_db()

    result = db.table("sessions").delete().eq("id", session_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return None


# ---------------------------------------------------------------------------
# AI Analyze
# ---------------------------------------------------------------------------


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_description(body: AnalyzeRequest):
    """
    Analyze a natural language description and extract Streamworks parameters.

    Uses OpenAI structured output to detect the job type and extract all
    relevant parameters from the user's description.
    """
    if not body.description.strip():
        raise HTTPException(status_code=400, detail="Description must not be empty")

    try:
        result = extract_parameters(body.description)
    except Exception as exc:
        logger.exception("Parameter extraction failed")
        raise HTTPException(
            status_code=500,
            detail=f"Parameter extraction failed: {str(exc)}",
        )

    return AnalyzeResponse(
        job_type=result.get("job_type", "STANDARD"),
        confidence=result.get("confidence", 0.0),
        parameters=result.get("parameters", {}),
        suggestions=result.get("suggestions", []),
    )


# ---------------------------------------------------------------------------
# XML Generation
# ---------------------------------------------------------------------------


@router.post("/generate-xml", response_model=GenerateXmlResponse)
def generate_xml_endpoint(body: GenerateXmlRequest):
    """
    Generate a Streamworks XML definition from a wizard session.

    Fetches the session data from Supabase, optionally overrides the stream
    name, then renders the XML using the Jinja2 master template.
    """
    db = get_db()

    result = (
        db.table("sessions")
        .select("id, data")
        .eq("id", body.session_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = result.data.get("data", {}) or {}

    # Allow stream name override from the request
    if body.stream_name:
        if "step_1" not in session_data:
            session_data["step_1"] = {}
        session_data["step_1"]["stream_name"] = body.stream_name

    warnings: list[str] = []

    # Validate that we have minimum required data
    step_1 = session_data.get("step_1", {})
    if not step_1.get("stream_name") and not body.stream_name:
        warnings.append("Kein Stream-Name angegeben. Ein Standard-Name wird generiert.")

    step_3 = session_data.get("step_3", {})
    if not step_3.get("job_type") and not step_1.get("job_type"):
        warnings.append("Kein Job-Typ erkannt. Standard-Typ STANDARD wird verwendet.")

    try:
        xml_output = generate_xml(session_data)
    except Exception as exc:
        logger.exception("XML generation failed for session %s", body.session_id)
        raise HTTPException(
            status_code=500,
            detail=f"XML generation failed: {str(exc)}",
        )

    # Derive filename from stream name
    stream_name = step_1.get("stream_name", body.stream_name or "unnamed")
    filename = f"{stream_name}.xml"

    return GenerateXmlResponse(
        xml=xml_output,
        filename=filename,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Quick Edit
# ---------------------------------------------------------------------------


def _match_session_id(
    target_name: str | None,
    session_names: dict[str, str],
) -> str | None:
    """Match an AI-detected stream name to a session ID (case-insensitive, substring fallback)."""
    if not target_name:
        # Auto-select if only one session exists
        if len(session_names) == 1:
            return next(iter(session_names))
        return None

    target_lower = target_name.lower()

    # Exact match (case-insensitive)
    for sid, name in session_names.items():
        if name.lower() == target_lower:
            return sid

    # Substring match
    for sid, name in session_names.items():
        if target_lower in name.lower() or name.lower() in target_lower:
            return sid

    return None


@router.post("/quick-edit", response_model=QuickEditPreview)
def quick_edit_preview(body: QuickEditRequest):
    """
    Parse a natural-language edit instruction and return a preview of changes.
    """
    if not body.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction must not be empty")

    if not body.session_names:
        return QuickEditPreview(
            message="Keine Streams vorhanden.",
            error="no_sessions",
        )

    # Parse instruction with AI
    try:
        result = parse_edit_instruction(
            body.instruction,
            list(body.session_names.values()),
        )
    except Exception as exc:
        logger.exception("Quick edit parsing failed")
        raise HTTPException(
            status_code=500,
            detail=f"KI-Analyse fehlgeschlagen: {str(exc)}",
        )

    changes_raw = result.get("changes", [])
    ai_message = result.get("message", "")
    target_name = result.get("target_stream_name")

    if not changes_raw:
        return QuickEditPreview(
            message=ai_message or "Keine Aenderungen erkannt.",
            error="no_changes",
        )

    # Match target stream
    session_id = _match_session_id(target_name, body.session_names)

    if not session_id:
        return QuickEditPreview(
            message=f"Stream konnte nicht zugeordnet werden: '{target_name}'. "
            f"Vorhandene Streams: {', '.join(body.session_names.values())}",
            error="ambiguous_target",
        )

    matched_name = body.session_names[session_id]

    # Load current session data for old_value
    db = get_db()
    existing = (
        db.table("sessions")
        .select("id, data")
        .eq("id", session_id)
        .single()
        .execute()
    )

    session_data = (existing.data or {}).get("data", {}) or {}

    # Build FieldChange list with old values and step numbers
    field_changes: list[FieldChange] = []
    for change in changes_raw:
        field = change.get("field", "")
        new_value = change.get("new_value", "")

        step = FIELD_TO_STEP.get(field)
        if step is None:
            continue  # Unknown field, skip

        step_key = f"step_{step}"
        step_data = session_data.get(step_key, {}) or {}
        old_value = step_data.get(field)

        field_changes.append(
            FieldChange(
                field=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value),
                step=step,
                label=FIELD_LABELS.get(field, field),
            )
        )

    if not field_changes:
        return QuickEditPreview(
            message="Keine gueltigen Felder in der Anweisung erkannt.",
            error="invalid_fields",
        )

    return QuickEditPreview(
        session_id=session_id,
        session_name=matched_name,
        changes=field_changes,
        message=ai_message,
    )


@router.post("/quick-edit/apply")
def quick_edit_apply(body: QuickEditApplyRequest):
    """
    Apply confirmed quick-edit changes to a session.

    Groups changes by step number and merges them into existing step data.
    """
    db = get_db()

    # Load session
    existing = (
        db.table("sessions")
        .select("id, data")
        .eq("id", body.session_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = existing.data.get("data", {}) or {}

    # Group changes by step
    steps_to_update: dict[int, dict[str, str]] = {}
    for change in body.changes:
        step = change.step
        if step not in steps_to_update:
            steps_to_update[step] = {}
        steps_to_update[step][change.field] = change.new_value

    # Merge into session data
    for step_num, fields in steps_to_update.items():
        step_key = f"step_{step_num}"
        step_data = session_data.get(step_key, {}) or {}
        step_data.update(fields)
        session_data[step_key] = step_data

    now = datetime.now(timezone.utc).isoformat()

    result = (
        db.table("sessions")
        .update({"data": session_data, "updated_at": now})
        .eq("id", body.session_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to apply changes")

    return result.data[0]
