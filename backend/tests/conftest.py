"""Shared test fixtures."""

import os
import pytest

# Force in-memory storage by clearing Supabase env vars before any import
os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_KEY", None)
os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"

from config import get_settings, Settings
from services.db import _MemStore


@pytest.fixture()
def fresh_memstore():
    """Return a fresh in-memory store with seed data, isolated per test."""
    store = _MemStore()
    return store


@pytest.fixture()
def client():
    """FastAPI TestClient with a fresh in-memory DB per test."""
    import services.db as db_mod

    original_store = db_mod._mem_store
    db_mod._mem_store = _MemStore()
    # Force in-memory path
    db_mod._supabase_available = False

    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as c:
        yield c

    # Restore
    db_mod._mem_store = original_store


@pytest.fixture()
def mock_openai(monkeypatch):
    """Patch OpenAI client to avoid real API calls."""

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChoice:
        def __init__(self, content):
            self.message = FakeMessage(content)

    class FakeCompletion:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, **kwargs):
            return FakeCompletion('{"job_type":"STANDARD","confidence":0.8,"parameters":{},"suggestions":[]}')

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)
    return FakeOpenAI
