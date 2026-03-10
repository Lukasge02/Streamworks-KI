"""
Database abstraction layer using PostgreSQL (psycopg2).

Provides a chainable query builder that mimics the Supabase SDK interface,
so all existing router/service code continues to work unchanged.

Falls back to a file-backed in-memory store when DATABASE_URL is not set
(for local development without Docker).
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

from config import get_settings

logger = logging.getLogger(__name__)

# ── Connection Pool ──────────────────────────────────────────────────

_pool: SimpleConnectionPool | None = None


def _get_pool() -> SimpleConnectionPool | None:
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    if not settings.database_url:
        logger.warning("DATABASE_URL not set, using in-memory fallback")
        return None

    try:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.database_url,
        )
        # Quick connectivity test
        conn = _pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.commit()
        finally:
            _pool.putconn(conn)
        logger.info("Connected to PostgreSQL")
        return _pool
    except Exception as e:
        logger.warning("PostgreSQL unavailable (%s), using in-memory fallback", e)
        _pool = None
        return None


def init_db():
    """Run all migration SQL files against the database."""
    pool = _get_pool()
    if pool is None:
        return

    migrations_dir = Path(__file__).resolve().parent.parent / "migrations"
    if not migrations_dir.exists():
        return

    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            for sql_file in sorted(migrations_dir.glob("*.sql")):
                logger.info("Running migration: %s", sql_file.name)
                cur.execute(sql_file.read_text(encoding="utf-8"))
        conn.commit()
        logger.info("All migrations applied successfully")
    except Exception as e:
        conn.rollback()
        logger.error("Migration failed: %s", e)
        raise
    finally:
        pool.putconn(conn)


# ── PostgreSQL Query Builder ─────────────────────────────────────────

class _PgResult:
    def __init__(self, data):
        self.data = data


class _PgTable:
    """Chainable query builder that translates to SQL."""

    def __init__(self, table_name: str, pool: SimpleConnectionPool):
        self._table = table_name
        self._pool = pool
        self._op = "select"
        self._columns = "*"
        self._filters: list[tuple[str, object]] = []
        self._order_key: str | None = None
        self._order_desc = False
        self._limit_n: int | None = None
        self._single_mode = False
        self._insert_data: dict | None = None
        self._update_data: dict | None = None

    def select(self, cols="*"):
        self._op = "select"
        self._columns = cols
        return self

    def insert(self, data: dict):
        self._op = "insert"
        self._insert_data = data
        return self

    def update(self, data: dict):
        self._op = "update"
        self._update_data = data
        return self

    def delete(self):
        self._op = "delete"
        return self

    def eq(self, key: str, value):
        self._filters.append((key, value))
        return self

    def order(self, key: str, desc: bool = False):
        self._order_key = key
        self._order_desc = desc
        return self

    def limit(self, n: int):
        self._limit_n = n
        return self

    def single(self):
        self._single_mode = True
        self._limit_n = 1
        return self

    def _where_clause(self):
        if not self._filters:
            return "", []
        parts = []
        values = []
        for key, val in self._filters:
            if val is None:
                parts.append(f'"{key}" IS NULL')
            else:
                parts.append(f'"{key}" = %s')
                values.append(val)
        return " WHERE " + " AND ".join(parts), values

    def execute(self):
        conn = self._pool.getconn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if self._op == "insert":
                    return self._exec_insert(cur, conn)
                elif self._op == "update":
                    return self._exec_update(cur, conn)
                elif self._op == "delete":
                    return self._exec_delete(cur, conn)
                else:
                    return self._exec_select(cur)
        finally:
            self._pool.putconn(conn)

    def _exec_insert(self, cur, conn):
        data = dict(self._insert_data)

        # Auto-generate id if missing
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        # Serialize dicts/lists to JSON for JSONB columns
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                data[k] = json.dumps(v, ensure_ascii=False)

        cols = ", ".join(f'"{k}"' for k in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f'INSERT INTO "{self._table}" ({cols}) VALUES ({placeholders}) RETURNING *'

        cur.execute(sql, list(data.values()))
        conn.commit()
        row = cur.fetchone()
        return _PgResult([self._deserialize(dict(row))] if row else [])

    def _exec_update(self, cur, conn):
        data = dict(self._update_data)

        # Handle "now()" special value
        set_parts = []
        values = []
        for k, v in data.items():
            if v == "now()":
                set_parts.append(f'"{k}" = NOW()')
            else:
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False)
                set_parts.append(f'"{k}" = %s')
                values.append(v)

        where, where_vals = self._where_clause()
        values.extend(where_vals)

        sql = f'UPDATE "{self._table}" SET {", ".join(set_parts)}{where} RETURNING *'
        cur.execute(sql, values)
        conn.commit()
        rows = cur.fetchall()
        return _PgResult([self._deserialize(dict(r)) for r in rows])

    def _exec_delete(self, cur, conn):
        where, values = self._where_clause()
        sql = f'DELETE FROM "{self._table}"{where} RETURNING *'
        cur.execute(sql, values)
        conn.commit()
        rows = cur.fetchall()
        return _PgResult([self._deserialize(dict(r)) for r in rows])

    def _exec_select(self, cur):
        where, values = self._where_clause()

        order = ""
        if self._order_key:
            direction = "DESC" if self._order_desc else "ASC"
            order = f' ORDER BY "{self._order_key}" {direction}'

        limit = ""
        if self._limit_n is not None:
            limit = f" LIMIT {self._limit_n}"

        sql = f'SELECT {self._columns} FROM "{self._table}"{where}{order}{limit}'
        cur.execute(sql, values)
        rows = cur.fetchall()
        result = [self._deserialize(dict(r)) for r in rows]

        if self._single_mode:
            return _PgResult(result[0] if result else None)
        return _PgResult(result)

    def _deserialize(self, row: dict) -> dict:
        """Ensure JSONB columns come back as Python dicts/lists, and datetimes as ISO strings."""
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.isoformat()
            elif isinstance(v, str) and k in ("data", "sources", "metadata"):
                try:
                    row[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    pass
        return row


class _PgStore:
    """PostgreSQL store with the same .table() interface as Supabase client."""

    def __init__(self, pool: SimpleConnectionPool):
        self._pool = pool

    def table(self, name: str):
        return _PgTable(name, self._pool)


# ── In-Memory Fallback Store ────────────────────────────────────────

_STORAGE_FILE = Path(__file__).resolve().parent.parent / "data" / "local_db.json"


class _MemStore:
    """File-backed dict store for local dev without PostgreSQL."""

    _DEFAULT_TABLES = [
        "sessions", "streams", "dropdown_options",
        "chat_sessions", "chat_messages", "documents", "folders",
    ]

    def __init__(self, persist: bool = True):
        self._persist_enabled = persist
        self.tables: dict[str, list[dict]] = {}
        self._load()
        self._seed_options()

    def _load(self):
        if self._persist_enabled and _STORAGE_FILE.exists():
            try:
                with open(_STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t in self._DEFAULT_TABLES:
                    self.tables[t] = data.get(t, [])
                logger.info("Loaded local DB from %s", _STORAGE_FILE)
                return
            except Exception as e:
                logger.warning("Failed to load local DB (%s), starting fresh", e)
        for t in self._DEFAULT_TABLES:
            self.tables[t] = []

    def _save(self):
        if not self._persist_enabled:
            return
        try:
            _STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tables, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("Failed to save local DB: %s", e)

    def _seed_options(self):
        if self.tables.get("dropdown_options"):
            return
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
        self._save()

    def table(self, name: str):
        if name not in self.tables:
            self.tables[name] = []
        return _MemTable(self.tables[name], self._save)


class _MemResult:
    def __init__(self, data):
        self.data = data


class _MemTable:
    def __init__(self, rows: list[dict], on_mutate=None):
        self._rows = rows
        self._on_mutate = on_mutate
        self._filters: list[tuple[str, object]] = []
        self._order_key = None
        self._order_desc = False
        self._selected = "*"

    def _clone(self):
        t = _MemTable(self._rows, self._on_mutate)
        t._filters = list(self._filters)
        return t

    def select(self, cols="*"):
        t = self._clone()
        t._selected = cols
        return t

    def insert(self, data: dict):
        t = self._clone()
        t._insert_data = data
        return t

    def update(self, data: dict):
        t = self._clone()
        t._update_data = data
        return t

    def delete(self):
        t = self._clone()
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

    def _persist(self):
        if self._on_mutate:
            self._on_mutate()

    def execute(self):
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
            self._persist()
            return _MemResult([row])

        if hasattr(self, '_is_delete'):
            deleted = [r for r in self._rows if self._matches(r)]
            remaining = [r for r in self._rows if not self._matches(r)]
            self._rows.clear()
            self._rows.extend(remaining)
            self._persist()
            return _MemResult(deleted)

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
            if updated:
                self._persist()
            return _MemResult(updated)

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


# ── Public API ───────────────────────────────────────────────────────

_store = None


def get_db():
    """Returns PostgreSQL store or in-memory fallback."""
    global _store
    if _store is not None:
        return _store

    pool = _get_pool()
    if pool is not None:
        _store = _PgStore(pool)
        # Run migrations on first connect
        init_db()
    else:
        _store = _MemStore()

    return _store
