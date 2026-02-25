"""Tests for RAG chat endpoints."""

from unittest.mock import patch, MagicMock


class TestChatEndpoint:
    def test_chat_creates_session(self, client):
        with patch("routers.rag.rag_service") as mock_rag:
            mock_rag.query.return_value = {
                "answer": "Test answer",
                "sources": [
                    {"document_name": "doc.pdf", "text": "chunk", "score": 0.9, "page": 1}
                ],
                "confidence": 0.85,
            }

            resp = client.post("/api/rag/chat", json={"message": "What is Streamworks?"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["answer"] == "Test answer"
            assert "session_id" in data
            assert len(data["sources"]) == 1

    def test_chat_with_existing_session(self, client):
        with patch("routers.rag.rag_service") as mock_rag, \
             patch("routers.rag.chat_session_service") as mock_css:
            mock_css.get_session.return_value = {"id": "existing-id", "title": "Test"}
            mock_css.add_message.return_value = {"id": "msg1"}
            mock_css.get_chat_history.return_value = []
            mock_css.update_session_title.return_value = None
            mock_rag.query.return_value = {
                "answer": "Response",
                "sources": [],
                "confidence": 0.5,
            }

            resp = client.post(
                "/api/rag/chat",
                json={"message": "Follow up", "session_id": "existing-id"},
            )
            assert resp.status_code == 200

    def test_chat_with_invalid_session_404(self, client):
        with patch("routers.rag.chat_session_service") as mock_css:
            mock_css.get_session.return_value = None

            resp = client.post(
                "/api/rag/chat",
                json={"message": "Hello", "session_id": "bad-id"},
            )
            assert resp.status_code == 404


class TestChatSessionEndpoints:
    def test_list_sessions(self, client):
        resp = client.get("/api/rag/sessions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_delete_session(self, client):
        with patch("routers.rag.chat_session_service") as mock_css:
            mock_css.delete_session.return_value = None

            resp = client.delete("/api/rag/sessions/some-id")
            assert resp.status_code == 200
            assert resp.json()["message"] == "Session deleted"
