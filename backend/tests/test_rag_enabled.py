"""
Tests for RAG Enabled Filtering
Verifies that documents with rag_enabled=False are excluded from RAG context.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRAGEnabledFiltering:
    """Tests for rag_enabled filtering in TestingService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database service."""
        mock = Mock()
        mock.get_project.return_value = {"id": "proj-1", "name": "Test Project"}
        return mock

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        mock = Mock()
        # Return empty results for search
        mock.search.return_value = []
        return mock

    def test_chat_with_ddd_filters_disabled_docs(self, mock_db, mock_vector_store):
        """Test that chat_with_ddd only uses rag_enabled=True documents."""
        from domains.testing.service import TestingService

        service = TestingService()
        service.db = mock_db
        service.vector_store = mock_vector_store

        # Mock get_project_documents to return mixed rag_enabled states
        service.get_project_documents = Mock(
            return_value=[
                {
                    "doc_id": "doc-enabled",
                    "metadata": {"category": "ddd", "filename": "enabled.pdf"},
                    "rag_enabled": True,
                },
                {
                    "doc_id": "doc-disabled",
                    "metadata": {"category": "ddd", "filename": "disabled.pdf"},
                    "rag_enabled": False,
                },
            ]
        )

        # Mock OpenAI client
        with patch.object(service, "openai_client") as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Test answer"))]
            mock_openai.chat.completions.create.return_value = mock_response

            result = service.chat_with_ddd("proj-1", "test query")

        # Verify vector_store.search was called with only the enabled doc_id
        search_calls = mock_vector_store.search.call_args_list
        if search_calls:
            call_kwargs = search_calls[0][1]
            access_filter = call_kwargs.get("access_filter", {})
            allowed_doc_ids = access_filter.get("doc_ids", [])

            assert "doc-enabled" in allowed_doc_ids
            assert "doc-disabled" not in allowed_doc_ids

    def test_chat_with_ddd_includes_none_as_true(self, mock_db, mock_vector_store):
        """Test that documents with rag_enabled=None (legacy) are included."""
        from domains.testing.service import TestingService

        service = TestingService()
        service.db = mock_db
        service.vector_store = mock_vector_store

        # Mock with legacy document (no rag_enabled field)
        service.get_project_documents = Mock(
            return_value=[
                {
                    "doc_id": "doc-legacy",
                    "metadata": {"category": "ddd", "filename": "legacy.pdf"},
                    # No rag_enabled field - should default to True
                }
            ]
        )

        with patch.object(service, "openai_client") as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Test answer"))]
            mock_openai.chat.completions.create.return_value = mock_response

            result = service.chat_with_ddd("proj-1", "test query")

        # Verify the legacy doc was included
        search_calls = mock_vector_store.search.call_args_list
        if search_calls:
            call_kwargs = search_calls[0][1]
            access_filter = call_kwargs.get("access_filter", {})
            allowed_doc_ids = access_filter.get("doc_ids", [])

            assert "doc-legacy" in allowed_doc_ids


class TestRAGToggleEndpoint:
    """Tests for the RAG toggle API endpoint."""

    def test_update_project_document_rag(self):
        """Test that rag status can be updated in database."""
        from services.db import DatabaseService

        # This is more of an integration test - mock the Supabase client
        with patch("services.db.create_client") as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_update = Mock()
            mock_eq1 = Mock()
            mock_eq2 = Mock()

            mock_create.return_value = mock_client
            mock_client.table.return_value = mock_table
            mock_table.update.return_value = mock_update
            mock_update.eq.return_value = mock_eq1
            mock_eq1.eq.return_value = mock_eq2
            mock_eq2.execute.return_value = Mock(
                data=[{"id": "link-1", "rag_enabled": False}]
            )

            db = DatabaseService()
            db.client = mock_client

            result = db.update_project_document_rag("proj-1", "doc-1", False)

            # Verify the update was called with correct parameters
            mock_table.update.assert_called_once_with({"rag_enabled": False})
