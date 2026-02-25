"""
Options router: dropdown values from the Supabase 'dropdown_options' table.

Table schema:
    id          UUID        PRIMARY KEY
    category    TEXT        NOT NULL
    label       TEXT        NOT NULL
    value       TEXT        NOT NULL
    is_active   BOOLEAN     DEFAULT TRUE
    sort_order  INTEGER     DEFAULT 0
"""

import logging

from fastapi import APIRouter, HTTPException

from services.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/categories")
def list_categories():
    """
    List all distinct option categories.

    Returns a sorted list of category name strings that have at least
    one active option.
    """
    db = get_db()

    result = (
        db.table("dropdown_options")
        .select("category")
        .eq("is_active", True)
        .execute()
    )

    rows = result.data or []

    # Extract unique category names and sort alphabetically
    categories = sorted({row["category"] for row in rows})

    return categories


@router.get("/{category}")
def get_options(category: str):
    """
    Get all active options for a given category, ordered by sort_order.

    Args:
        category: The category identifier (e.g. 'agent', 'schedule_type').

    Returns:
        A list of {label, value} dicts.
    """
    db = get_db()

    result = (
        db.table("dropdown_options")
        .select("label, value")
        .eq("category", category)
        .eq("is_active", True)
        .order("sort_order")
        .execute()
    )

    rows = result.data or []

    if not rows:
        logger.debug("No options found for category '%s'", category)

    return rows
