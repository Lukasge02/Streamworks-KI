"""
Database abstraction layer.

Tries Supabase first. If unavailable, falls back to in-memory storage
so the app works in local dev without a running Supabase instance.
"""

import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from config import get_settings

logger = logging.getLogger(__name__)

_supabase_client = None
_supabase_available = None


def _try_supabase():
    global _supabase_client, _supabase_available
    if _supabase_available is not None:
        return _supabase_available

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key:
        logger.warning("Supabase not configured, using in-memory storage")
        _supabase_available = False
        return False

    try:
        from supabase import create_client
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
        # Quick connectivity test
        _supabase_client.table("sessions").select("id").limit(1).execute()
        _supabase_available = True
        logger.info("Connected to Supabase")
        return True
    except Exception as e:
        logger.warning(f"Supabase unavailable ({e}), using in-memory storage")
        _supabase_available = False
        return False


def get_supabase():
    if _try_supabase():
        return _supabase_client
    return None


# ── In-Memory Fallback Store ──────────────────────────────────────

class _MemStore:
    """Simple dict-based store that mimics Supabase table operations."""

    def __init__(self):
        self.tables: dict[str, list[dict]] = {
            "sessions": [],
            "streams": [],
            "dropdown_options": [],
            "chat_sessions": [],
            "chat_messages": [],
            "documents": [],
        }
        self._seed_options()

    def _seed_options(self):
        options = [
            ("agents", "UC4_UNIX_01", "UC4_UNIX_01", 1),
            ("agents", "UC4_UNIX_02", "UC4_UNIX_02", 2),
            ("agents", "UC4_WIN_01", "UC4_WIN_01", 3),
            ("agents", "UC4_WIN_02", "UC4_WIN_02", 4),
            ("agents", "UC4_SAP_01", "UC4_SAP_01", 5),
            ("transfer_mode", "Binary", "binary", 1),
            ("transfer_mode", "Text", "text", 2),
            ("transfer_mode", "Auto", "auto", 3),
            ("schedule", "Taeglich", "taeglich", 1),
            ("schedule", "Woechentlich", "woechentlich", 2),
            ("schedule", "Monatlich", "monatlich", 3),
            ("schedule", "Stuendlich", "stuendlich", 4),
            ("schedule", "Einmalig", "einmalig", 5),
            ("job_type", "Standard Job", "STANDARD", 1),
            ("job_type", "Dateitransfer", "FILE_TRANSFER", 2),
            ("job_type", "SAP Job", "SAP", 3),
            ("sap_system", "PA1", "PA1", 1),
            ("sap_system", "P01", "P01", 2),
            ("sap_system", "QA1", "QA1", 3),
            ("sap_system", "DEV", "DEV", 4),
            ("calendar", "Werktage DE", "WERKTAGE_DE", 1),
            ("calendar", "Alle Tage", "ALLE_TAGE", 2),
            ("calendar", "Monatsende", "MONATSENDE", 3),
        ]
        for cat, label, value, sort in options:
            self.tables["dropdown_options"].append({
                "id": str(uuid.uuid4()),
                "category": cat,
                "label": label,
                "value": value,
                "is_active": True,
                "sort_order": sort,
            })

    def table(self, name: str):
        if name not in self.tables:
            self.tables[name] = []
        return _MemTable(self.tables[name])


class _MemResult:
    def __init__(self, data: list[dict]):
        self.data = data


class _MemTable:
    def __init__(self, rows: list[dict]):
        self._rows = rows
        self._filters: list[tuple[str, str]] = []
        self._order_key = None
        self._order_desc = False
        self._selected = "*"

    def select(self, cols="*"):
        t = _MemTable(self._rows)
        t._selected = cols
        t._filters = list(self._filters)
        return t

    def insert(self, data: dict):
        t = _MemTable(self._rows)
        t._filters = list(self._filters)
        t._insert_data = data
        return t

    def update(self, data: dict):
        t = _MemTable(self._rows)
        t._filters = list(self._filters)
        t._update_data = data
        return t

    def delete(self):
        t = _MemTable(self._rows)
        t._filters = list(self._filters)
        t._is_delete = True
        return t

    def eq(self, key: str, value):
        self._filters.append((key, value))
        return self

    def order(self, key: str, desc: bool = False):
        self._order_key = key
        self._order_desc = desc
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def single(self):
        self._single = True
        return self

    def execute(self):
        # Handle insert
        if hasattr(self, '_insert_data'):
            now = datetime.now(timezone.utc).isoformat()
            row = {**self._insert_data}
            if "id" not in row:
                row["id"] = str(uuid.uuid4())
            if "created_at" not in row:
                row["created_at"] = now
            if "updated_at" not in row:
                row["updated_at"] = now
            self._rows.append(row)
            return _MemResult([row])

        # Handle delete
        if hasattr(self, '_is_delete'):
            deleted = [r for r in self._rows if self._matches(r)]
            remaining = [r for r in self._rows if not self._matches(r)]
            self._rows.clear()
            self._rows.extend(remaining)
            return _MemResult(deleted)

        # Handle update
        if hasattr(self, '_update_data'):
            updated = []
            for r in self._rows:
                if self._matches(r):
                    now = datetime.now(timezone.utc).isoformat()
                    for k, v in self._update_data.items():
                        if v == "now()":
                            r[k] = now
                        else:
                            r[k] = v
                    updated.append(r)
            return _MemResult(updated)

        # Handle select
        results = [r for r in self._rows if self._matches(r)]
        if self._order_key:
            results.sort(
                key=lambda r: r.get(self._order_key, ""),
                reverse=self._order_desc,
            )
        if hasattr(self, '_limit'):
            results = results[:self._limit]
        if hasattr(self, '_single') and self._single:
            return _MemResult(results[0] if results else None)
        return _MemResult(results)

    def _matches(self, row: dict) -> bool:
        for key, value in self._filters:
            if row.get(key) != value:
                return False
        return True


_mem_store = _MemStore()


def get_db():
    """Returns Supabase client or in-memory fallback."""
    sb = get_supabase()
    if sb is not None:
        return sb
    return _mem_store
