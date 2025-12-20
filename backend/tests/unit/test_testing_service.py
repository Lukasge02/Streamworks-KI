"""
Unit Tests for TestingService

Tests core functionality with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import uuid

from tests.factories import (
    ProjectFactory,
    DocumentFactory,
    TestPlanFactory,
    TestCaseFactory,
    create_test_project_with_documents,
)
from tests.mocks.openai_mock import MockOpenAI, create_structured_output_mock
from tests.mocks.qdrant_mock import MockVectorStore, create_search_results
from tests.mocks.supabase_mock import MockSupabaseClient


@pytest.mark.unit
class TestTestingServiceProjects:
    """Tests for project CRUD operations."""

    def test_create_project(self, mock_db):
        """Test project creation."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        result = service.create_project("Test Project", "Description")
        
        assert result is not None
        assert "id" in result
        assert result["name"] == "Test Project"
        mock_db.create_project.assert_called_once()

    def test_create_project_without_description(self, mock_db):
        """Test project creation without description."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        result = service.create_project("Test Project")
        
        assert result is not None
        mock_db.create_project.assert_called_once_with("Test Project", None)

    def test_list_projects(self, mock_db):
        """Test listing all projects."""
        from domains.testing.service import TestingService
        
        mock_db.list_projects.return_value = Mock(data=[
            ProjectFactory(),
            ProjectFactory(),
        ])
        
        service = TestingService()
        service.db = mock_db
        
        result = service.list_projects()
        
        assert isinstance(result, Mock)
        mock_db.list_projects.assert_called_once()

    def test_get_project(self, mock_db, sample_project):
        """Test getting a specific project."""
        from domains.testing.service import TestingService
        
        mock_db.get_project.return_value = sample_project
        
        service = TestingService()
        service.db = mock_db
        
        result = service.get_project(sample_project["id"])
        
        assert result == sample_project
        mock_db.get_project.assert_called_once_with(sample_project["id"])

    def test_delete_project(self, mock_db):
        """Test project deletion."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        result = service.delete_project("proj-123")
        
        mock_db.delete_project.assert_called_once_with("proj-123")


@pytest.mark.unit
class TestTestingServiceDocuments:
    """Tests for document linking operations."""

    def test_link_document(self, mock_db, mock_user):
        """Test linking a document to a project."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        # User with proper role (not customer)
        mock_user["role"] = "user"
        result = service.link_document(
            project_id="proj-123",
            doc_id="doc-456",
            category="context",
            filename="test.pdf",
            user=mock_user
        )
        
        mock_db.link_project_document.assert_called_once()

    def test_link_document_denied_for_customer(self, mock_db):
        """Test that customers cannot link documents."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        customer_user = {"id": "user-123", "role": "customer"}
        
        with pytest.raises(PermissionError):
            service.link_document(
                project_id="proj-123",
                doc_id="doc-456",
                category="ddd",
                user=customer_user
            )

    def test_unlink_document(self, mock_db):
        """Test unlinking a document from a project."""
        from domains.testing.service import TestingService
        
        mock_db.unlink_project_document.return_value = True
        
        service = TestingService()
        service.db = mock_db
        service.doc_service = Mock()
        service.doc_service.delete_document.return_value = {
            "success": True,
            "chunks_deleted": 5,
            "file_deleted": True
        }
        
        result = service.unlink_document("proj-123", "doc-456")
        
        mock_db.unlink_project_document.assert_called_once()
        assert result["success"] == True

    def test_get_project_documents_empty(self, mock_db, mock_vector_store):
        """Test getting documents for project with no documents."""
        from domains.testing.service import TestingService
        
        mock_db.get_project_documents.return_value = []
        
        service = TestingService()
        service.db = mock_db
        service.vector_store = mock_vector_store
        
        result = service.get_project_documents("proj-123")
        
        assert result == []


@pytest.mark.unit
class TestTestingServiceTestPlans:
    """Tests for test plan operations."""

    def test_get_test_plans_empty(self, mock_db):
        """Test getting test plans when none exist."""
        from domains.testing.service import TestingService
        
        mock_db.get_test_plans.return_value = []
        
        service = TestingService()
        service.db = mock_db
        
        result = service.get_test_plans("proj-123")
        
        assert result == []

    def test_get_test_plans(self, mock_db):
        """Test getting existing test plans."""
        from domains.testing.service import TestingService
        
        plans = [TestPlanFactory(), TestPlanFactory()]
        mock_db.get_test_plans.return_value = plans
        
        service = TestingService()
        service.db = mock_db
        
        result = service.get_test_plans("proj-123")
        
        assert len(result) == 2

    def test_update_plan(self, mock_db):
        """Test updating a test plan."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        
        new_content = json.dumps({"test_cases": []})
        result = service.update_plan("plan-123", new_content)
        
        mock_db.update_test_plan.assert_called_once()


@pytest.mark.unit
class TestTestingServiceRAGFiltering:
    """Tests for RAG filtering based on rag_enabled flag."""

    def test_rag_enabled_filtering(self, mock_db, mock_vector_store):
        """Test that only rag_enabled documents are used."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        service.vector_store = mock_vector_store
        
        # Mock get_project_documents to return mixed rag_enabled states
        service.get_project_documents = Mock(return_value=[
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
        ])
        
        # Get RAG-enabled doc IDs
        docs = service.get_project_documents("proj-1")
        enabled_docs = [d for d in docs if d.get("rag_enabled", True)]
        
        assert len(enabled_docs) == 1
        assert enabled_docs[0]["doc_id"] == "doc-enabled"

    def test_legacy_documents_included(self, mock_db, mock_vector_store):
        """Test that documents without rag_enabled field are included (default True)."""
        from domains.testing.service import TestingService
        
        service = TestingService()
        service.db = mock_db
        service.vector_store = mock_vector_store
        
        # Mock legacy document without rag_enabled field
        service.get_project_documents = Mock(return_value=[
            {
                "doc_id": "doc-legacy",
                "metadata": {"category": "ddd", "filename": "legacy.pdf"},
                # No rag_enabled field
            },
        ])
        
        docs = service.get_project_documents("proj-1")
        enabled_docs = [d for d in docs if d.get("rag_enabled", True)]
        
        assert len(enabled_docs) == 1


@pytest.mark.unit
class TestTestingServiceModels:
    """Tests for Pydantic models used in test plan generation."""

    def test_test_case_model_valid(self):
        """Test TestCaseModel with valid data."""
        from domains.testing.service import TestCaseModel
        
        test_case = TestCaseModel(
            test_id="TC-001",
            title="Test Login",
            description="Test user login",
            preconditions="User has valid credentials",
            steps="1. Enter username\n2. Enter password\n3. Click login",
            expected_result="User logged in",
            priority="high",
            category="happy_path",
        )
        
        assert test_case.test_id == "TC-001"
        assert test_case.priority == "high"

    def test_test_case_model_defaults(self):
        """Test TestCaseModel default values."""
        from domains.testing.service import TestCaseModel
        
        test_case = TestCaseModel(
            test_id="TC-001",
            title="Test",
            description="Desc",
            preconditions="None",
            steps="Step 1",
            expected_result="Result",
        )
        
        assert test_case.priority == "medium"
        assert test_case.category == "happy_path"

    def test_test_plan_model_valid(self):
        """Test TestPlanModel with valid data."""
        from domains.testing.service import TestPlanModel, TestCaseModel, CoverageAnalysis
        
        test_cases = [
            TestCaseModel(
                test_id="TC-001",
                title="Test",
                description="Desc",
                preconditions="None",
                steps="Step 1",
                expected_result="Result",
            )
        ]
        
        coverage = CoverageAnalysis(
            covered_use_cases=["UC-001"],
            covered_business_rules=["BR-001"],
        )
        
        plan = TestPlanModel(
            project_name="Project",
            introduction="Intro",
            test_cases=test_cases,
            summary="Executive summary of the test plan",
            coverage=coverage,
        )
        
        assert plan.project_name == "Project"
        assert len(plan.test_cases) == 1



@pytest.mark.unit
class TestFactories:
    """Tests for factory classes themselves."""

    def test_user_factory(self):
        """Test UserFactory creates valid users."""
        from tests.factories import UserFactory
        
        user = UserFactory()
        
        assert "id" in user
        assert "email" in user
        assert user["role"] == "user"

    def test_user_factory_admin(self):
        """Test UserFactory admin trait."""
        from tests.factories import UserFactory
        
        admin = UserFactory(admin=True)
        
        assert admin["role"] == "admin"

    def test_project_factory(self):
        """Test ProjectFactory creates valid projects."""
        from tests.factories import ProjectFactory
        
        project = ProjectFactory()
        
        assert "id" in project
        assert "name" in project
        assert "description" in project

    def test_document_factory_ddd(self):
        """Test DocumentFactory DDD trait."""
        from tests.factories import DocumentFactory
        
        doc = DocumentFactory(ddd=True)
        
        assert doc["category"] == "ddd"

    def test_test_plan_factory(self):
        """Test TestPlanFactory creates valid test plans."""
        from tests.factories import TestPlanFactory
        
        plan = TestPlanFactory()
        
        assert "id" in plan
        assert "content" in plan
        
        content = json.loads(plan["content"])
        assert "test_cases" in content

    def test_create_project_with_documents(self):
        """Test batch factory function."""
        from tests.factories import create_test_project_with_documents
        
        result = create_test_project_with_documents(
            num_context_docs=3,
            num_ddd_docs=1
        )
        
        assert "project" in result
        assert len(result["documents"]) == 4
        assert len(result["links"]) == 4
