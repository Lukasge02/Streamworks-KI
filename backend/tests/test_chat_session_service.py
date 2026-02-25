"""Tests for chat session service."""

import services.db as db_mod
from services.db import _MemStore
from services import chat_session_service


def _with_fresh_db(fn):
    """Run fn with a fresh in-memory DB."""
    original = db_mod._mem_store
    db_mod._mem_store = _MemStore()
    db_mod._supabase_available = False
    try:
        return fn()
    finally:
        db_mod._mem_store = original


class TestChatSessionCRUD:
    def test_create_session(self):
        def run():
            session = chat_session_service.create_session("Test Chat")
            assert session["title"] == "Test Chat"
            assert "id" in session
            return session
        _with_fresh_db(run)

    def test_list_sessions(self):
        def run():
            chat_session_service.create_session("Chat 1")
            chat_session_service.create_session("Chat 2")
            sessions = chat_session_service.list_sessions()
            assert len(sessions) == 2
        _with_fresh_db(run)

    def test_get_session(self):
        def run():
            created = chat_session_service.create_session("Get Me")
            fetched = chat_session_service.get_session(created["id"])
            assert fetched is not None
            assert fetched["title"] == "Get Me"
        _with_fresh_db(run)

    def test_get_missing_session(self):
        def run():
            result = chat_session_service.get_session("nonexistent")
            assert result is None
        _with_fresh_db(run)

    def test_delete_session(self):
        def run():
            created = chat_session_service.create_session("Delete Me")
            chat_session_service.delete_session(created["id"])
            assert chat_session_service.get_session(created["id"]) is None
        _with_fresh_db(run)

    def test_update_session_title(self):
        def run():
            created = chat_session_service.create_session("Old Title")
            updated = chat_session_service.update_session_title(created["id"], "New Title")
            assert updated is not None
            assert updated["title"] == "New Title"
        _with_fresh_db(run)

    def test_update_session_title_missing_returns_none(self):
        def run():
            result = chat_session_service.update_session_title("nonexistent", "Title")
            assert result is None
        _with_fresh_db(run)


class TestChatMessages:
    def test_add_and_get_messages(self):
        def run():
            session = chat_session_service.create_session()
            chat_session_service.add_message(session["id"], "user", "Hello")
            chat_session_service.add_message(session["id"], "assistant", "Hi there")

            messages = chat_session_service.get_messages(session["id"])
            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert messages[1]["role"] == "assistant"
        _with_fresh_db(run)

    def test_chat_history_limit(self):
        def run():
            session = chat_session_service.create_session()
            for i in range(20):
                chat_session_service.add_message(session["id"], "user", f"msg {i}")

            history = chat_session_service.get_chat_history(session["id"], limit=5)
            assert len(history) == 5
        _with_fresh_db(run)

    def test_chat_history_format(self):
        def run():
            session = chat_session_service.create_session()
            chat_session_service.add_message(session["id"], "user", "Question")
            chat_session_service.add_message(session["id"], "assistant", "Answer")

            history = chat_session_service.get_chat_history(session["id"])
            assert history[0] == {"role": "user", "content": "Question"}
            assert history[1] == {"role": "assistant", "content": "Answer"}
        _with_fresh_db(run)
