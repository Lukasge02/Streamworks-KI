"""
Enterprise Test Configuration

Provides fixtures, factories, and utilities for comprehensive testing.
Supports async tests, database transactions, and mock infrastructure.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Generator
import json
import uuid
from datetime import datetime

# FastAPI app import
from main import app


# =============================================================================
# TEST MARKERS DOCUMENTATION
# =============================================================================
# @pytest.mark.unit        - Pure unit tests (no I/O)
# @pytest.mark.integration - Mocked external services
# @pytest.mark.e2e         - Requires running services
# @pytest.mark.slow        - Takes > 5 seconds
# @pytest.mark.ai          - Involves LLM calls
# =============================================================================


# =============================================================================
# BASIC FIXTURES
# =============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client with proper lifecycle."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def async_client():
    """Async HTTP client for testing async endpoints."""
    import httpx
    return httpx.AsyncClient(app=app, base_url="http://test")


# =============================================================================
# USER & AUTH FIXTURES
# =============================================================================

@pytest.fixture
def mock_user() -> Dict[str, Any]:
    """Standard test user."""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "role": "user",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_admin_user() -> Dict[str, Any]:
    """Admin test user."""
    return {
        "id": str(uuid.uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "name": "Admin User",
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_auth_headers() -> Dict[str, str]:
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token-12345"}


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture
def mock_db():
    """
    Mock database service.
    Provides common database methods with configurable return values.
    """
    mock = Mock()
    
    # Project methods
    mock.create_project.return_value = Mock(data=[{
        "id": str(uuid.uuid4()),
        "name": "Test Project",
        "description": "A test project",
        "created_at": datetime.utcnow().isoformat(),
    }])
    mock.get_project.return_value = {
        "id": "proj-123",
        "name": "Test Project",
        "description": "Test description",
    }
    mock.list_projects.return_value = Mock(data=[])
    mock.delete_project.return_value = Mock(data=[{"id": "proj-123"}])
    
    # Document methods
    mock.link_document.return_value = Mock(data=[{
        "project_id": "proj-123",
        "doc_id": "doc-123",
        "category": "context",
    }])
    mock.get_project_documents.return_value = []
    
    # Test plan methods
    mock.get_test_plans.return_value = []
    mock.create_test_plan.return_value = Mock(data=[{
        "id": str(uuid.uuid4()),
        "project_id": "proj-123",
        "content": "{}",
    }])
    mock.update_test_plan.return_value = Mock(data=[{"id": "plan-123"}])
    
    return mock


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database operations."""
    client = Mock()
    
    # Table operations
    table_mock = Mock()
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.delete.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.execute.return_value = Mock(data=[], count=0)
    
    client.table.return_value = table_mock
    return client


# =============================================================================
# VECTOR STORE / RAG FIXTURES
# =============================================================================

@pytest.fixture
def mock_vector_store():
    """Mock Qdrant vector store."""
    mock = Mock()
    
    # Search returns empty by default
    mock.search.return_value = []
    mock.get_document.return_value = None
    mock.delete_document.return_value = True
    mock.add_document.return_value = True
    
    return mock


@pytest.fixture
def mock_rag_response():
    """Sample RAG response with sources."""
    return {
        "answer": "This is a test answer based on the retrieved context.",
        "confidence": 0.85,
        "confidence_level": "high",
        "sources": [
            {
                "doc_id": "doc-001",
                "filename": "test_doc.pdf",
                "chunk_text": "Relevant context from the document...",
                "score": 0.92,
            }
        ],
        "has_context": True,
    }


@pytest.fixture
def mock_search_results():
    """Sample vector search results."""
    return [
        {
            "id": "chunk-001",
            "doc_id": "doc-001",
            "text": "This is the first chunk of text.",
            "score": 0.95,
            "metadata": {"filename": "doc1.pdf", "page": 1},
        },
        {
            "id": "chunk-002",
            "doc_id": "doc-001",
            "text": "This is the second chunk of text.",
            "score": 0.88,
            "metadata": {"filename": "doc1.pdf", "page": 2},
        },
    ]


# =============================================================================
# OPENAI / LLM FIXTURES
# =============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = Mock()
    
    # Chat completion mock
    response = Mock()
    response.choices = [Mock(message=Mock(content="Test LLM response"))]
    response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    
    client.chat.completions.create.return_value = response
    
    return client


@pytest.fixture
def mock_openai_structured_response():
    """Mock structured output from OpenAI."""
    return {
        "test_cases": [
            {
                "test_id": "TC-001",
                "title": "Test Login Success",
                "description": "Verify successful login with valid credentials",
                "steps": ["Enter valid email", "Enter valid password", "Click login"],
                "expected_result": "User is logged in successfully",
                "priority": "high",
                "category": "happy_path",
            }
        ],
        "coverage_analysis": {
            "covered_use_cases": ["UC-001"],
            "covered_business_rules": ["BR-001"],
            "coverage_gaps": [],
        },
    }


@pytest.fixture
def patch_openai():
    """Context manager to patch OpenAI calls."""
    with patch("openai.OpenAI") as mock:
        response = Mock()
        response.choices = [Mock(message=Mock(content="Mocked response"))]
        mock.return_value.chat.completions.create.return_value = response
        yield mock


# =============================================================================
# PROJECT & DOCUMENT FIXTURES
# =============================================================================

@pytest.fixture
def sample_project() -> Dict[str, Any]:
    """Sample project data."""
    return {
        "id": str(uuid.uuid4()),
        "name": "Sample Project",
        "description": "A sample project for testing",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_document() -> Dict[str, Any]:
    """Sample document data."""
    return {
        "doc_id": str(uuid.uuid4()),
        "filename": "sample_document.pdf",
        "category": "context",
        "rag_enabled": True,
        "metadata": {
            "filename": "sample_document.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "uploaded_at": datetime.utcnow().isoformat(),
        },
        "processing_status": "completed",
    }


@pytest.fixture
def sample_ddd_document() -> Dict[str, Any]:
    """Sample DDD document data."""
    return {
        "doc_id": str(uuid.uuid4()),
        "filename": "project_ddd.pdf",
        "category": "ddd",
        "rag_enabled": True,
        "metadata": {
            "filename": "project_ddd.pdf",
            "file_size": 2048000,
            "mime_type": "application/pdf",
        },
        "processing_status": "completed",
    }


# =============================================================================
# TEST PLAN FIXTURES
# =============================================================================

@pytest.fixture
def sample_test_plan() -> Dict[str, Any]:
    """Sample test plan data."""
    return {
        "id": str(uuid.uuid4()),
        "project_id": "proj-123",
        "content": json.dumps({
            "project_name": "Sample Project",
            "introduction": "Test plan for Sample Project",
            "test_cases": [
                {
                    "test_id": "TC-001",
                    "title": "Verify Login",
                    "description": "Test user login functionality",
                    "steps": ["Open login page", "Enter credentials", "Submit"],
                    "expected_result": "User logged in",
                    "priority": "high",
                    "category": "happy_path",
                }
            ],
            "coverage_analysis": {
                "covered_use_cases": ["UC-001"],
                "covered_business_rules": ["BR-001"],
                "coverage_gaps": [],
            },
        }),
        "created_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# SERVICE FIXTURES
# =============================================================================

@pytest.fixture
def mock_testing_service(mock_db, mock_vector_store, mock_openai_client):
    """
    Mock TestingService with all dependencies mocked.
    """
    from domains.testing.service import TestingService
    
    service = TestingService()
    service.db = mock_db
    service.vector_store = mock_vector_store
    service.openai_client = mock_openai_client
    
    return service


@pytest.fixture
def mock_document_service():
    """Mock document service."""
    mock = Mock()
    mock.get_upload_status.return_value = {"status": "completed"}
    mock.get_document_metadata.return_value = {
        "filename": "test.pdf",
        "file_size": 1024,
    }
    return mock


@pytest.fixture
def mock_access_service():
    """Mock access control service."""
    mock = Mock()
    mock.check_document_access.return_value = True
    mock.get_document_access.return_value = Mock(
        access_level="public",
        is_public=True,
    )
    return mock


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_mock_response(content: str, confidence: float = 0.85) -> Dict[str, Any]:
    """Helper to create mock RAG responses."""
    return {
        "answer": content,
        "confidence": confidence,
        "confidence_level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low",
        "sources": [],
        "has_context": True,
    }


def create_mock_openai_response(content: str) -> Mock:
    """Helper to create mock OpenAI API responses."""
    response = Mock()
    response.choices = [Mock(message=Mock(content=content))]
    response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    return response


# =============================================================================
# ASYNC TEST HELPERS
# =============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
