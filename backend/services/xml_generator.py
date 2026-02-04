"""
Jinja2-based XML generation for Streamworks automation streams.

Renders the master XML template with flattened wizard session data,
applying naming conventions and custom filters.
"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_STREAM_PREFIX = "GECK003_"


def _xml_boolean(value) -> str:
    """
    Jinja2 filter that converts Python booleans to XML-friendly strings.

    Truthy values become "True", falsy values become "False".
    String values "true"/"false" (case-insensitive) are normalized.
    """
    if isinstance(value, str):
        return "True" if value.lower() in ("true", "1", "yes", "ja") else "False"
    return "True" if value else "False"


def _get_jinja_env() -> Environment:
    """
    Create and return a configured Jinja2 environment.

    The environment loads templates from the templates directory and
    registers the xml_boolean custom filter.
    """
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("xml",)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["xml_boolean"] = _xml_boolean
    return env


def _flatten_session_data(data: dict) -> dict:
    """
    Flatten nested wizard session data into a single-level dict for template rendering.

    The wizard stores data per step as:
        {
            "step_0": {"uploaded_files": [...], "description": "..."},
            "step_1": {"stream_name": "...", "job_type": "..."},
            "step_2": {"parameters": {...}},
            "step_3": {"schedule": {...}},
            "step_4": {"error_handling": {...}},
            ...
        }

    This function merges all step data into a flat namespace. For nested dicts
    within a step (e.g. step_2.parameters), the inner keys are promoted to
    top level. Lists and scalar values are kept as-is.

    Args:
        data: The wizard session data dict, typically keyed by step.

    Returns:
        A flat dict suitable for Jinja2 template rendering.
    """
    flat: dict = {}

    for key, value in data.items():
        if isinstance(value, dict):
            # This is a step dict (e.g. "step_1": {...}) or a nested section
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, dict):
                    # Promote nested dict contents (e.g. step_2.parameters.param_x)
                    for nested_key, nested_value in inner_value.items():
                        flat[nested_key] = nested_value
                else:
                    flat[inner_key] = inner_value
        else:
            flat[key] = value

    return flat


def _ensure_stream_prefix(name: str) -> str:
    """
    Ensure the stream name has the required prefix.

    Args:
        name: The raw stream name.

    Returns:
        The stream name with the prefix prepended if not already present.
    """
    if not name:
        return f"{_STREAM_PREFIX}unnamed"

    if name.startswith(_STREAM_PREFIX):
        return name

    return f"{_STREAM_PREFIX}{name}"


def generate_xml(session_data: dict) -> str:
    """
    Generate a Streamworks XML definition from wizard session data.

    Pipeline:
    1. Flatten the nested session data into template variables.
    2. Ensure the stream name carries the correct prefix.
    3. Load the master_template.xml Jinja2 template.
    4. Render and return the XML string.

    Args:
        session_data: The full wizard session data dict (with step keys).

    Returns:
        The rendered XML string.

    Raises:
        jinja2.TemplateNotFound: If master_template.xml is missing.
    """
    flat = _flatten_session_data(session_data)

    # Apply stream name prefix
    stream_name = flat.get("stream_name", "")
    flat["stream_name"] = _ensure_stream_prefix(stream_name)

    # Provide sensible defaults for common fields
    defaults = {
        "job_type": "STANDARD",
        "description": "",
        "active": True,
        "run_as_dummy": False,
        "confirm": True,
        "schedule_type": "MANUAL",
        "error_handling": "ABORT",
        "max_retries": 0,
        "retry_interval": 60,
        "priority": 0,
    }
    for key, default_value in defaults.items():
        if key not in flat:
            flat[key] = default_value

    # Map frontend field names to template variable names
    contact_name = flat.get("contact_name", "")
    if contact_name and "contact_first_name" not in flat:
        parts = contact_name.strip().split(" ", 1)
        flat["contact_first_name"] = parts[0]
        flat["contact_last_name"] = parts[1] if len(parts) > 1 else ""

    if "team" in flat and "department" not in flat:
        flat["department"] = flat["team"]

    if "email" in flat and "contact_email" not in flat:
        flat["contact_email"] = flat["email"]

    if "calendar" in flat and "calendar_id" not in flat:
        flat["calendar_id"] = flat["calendar"]

    if "documentation" in flat and "stream_documentation" not in flat:
        flat["stream_documentation"] = flat["documentation"]

    if "agent" in flat and "agent_detail" not in flat:
        flat["agent_detail"] = flat["agent"]

    if "priority" in flat and "stream_priority" not in flat:
        flat["stream_priority"] = flat["priority"]

    if "schedule_frequency" in flat and "schedule" not in flat:
        flat["schedule"] = flat["schedule_frequency"]

    if "phone" in flat and "contact_phone" not in flat:
        flat["contact_phone"] = flat["phone"]

    # Convert boolean overwrite fields to template-expected strings
    for overwrite_key in ("overwrite", "overwrite_existing"):
        if overwrite_key in flat and "overwrite_target" not in flat:
            val = flat[overwrite_key]
            if isinstance(val, bool):
                flat["overwrite_target"] = "Overwrite" if val else "Error"
            elif isinstance(val, str) and val.lower() in ("true", "1", "yes", "ja"):
                flat["overwrite_target"] = "Overwrite"
            elif isinstance(val, str):
                flat["overwrite_target"] = "Error"

    env = _get_jinja_env()
    template = env.get_template("master_template.xml")

    logger.info(
        "Generating XML for stream '%s' (job_type=%s, %d template vars)",
        flat.get("stream_name"),
        flat.get("job_type"),
        len(flat),
    )

    xml_output = template.render(**flat)
    return xml_output
