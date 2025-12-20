import pytest
from unittest.mock import Mock
from services.rag.access_service import AccessControlService


@pytest.fixture
def access_service():
    service = AccessControlService()
    # Mock dependencies if necessary, but AccessControlService
    # primarily uses MinIO/VectorStore which we might need to mock
    # or it uses its own logic for check_access which is pure logic + DB lookup.
    # For unit testing check_access logic, we can mock the document metadata retrieval.
    service.get_document_access = Mock()
    return service


def test_public_access(access_service):
    # Setup
    doc_id = "doc_123"
    access_service.get_document_access.return_value = Mock(access_level="public")

    # Test
    assert (
        access_service.check_document_access(doc_id, user_id="anon", user_roles=[])
    )


def test_internal_access_denied_anon(access_service):
    # Setup
    doc_id = "doc_internal"
    access_service.get_document_access.return_value = Mock(
        access_level="internal", is_public=False
    )

    # Test
    assert (
        not access_service.check_document_access(doc_id, user_id=None, user_roles=[])
    )


def test_internal_access_allowed_auth(access_service):
    # Setup
    doc_id = "doc_internal"
    access_service.get_document_access.return_value = Mock(
        access_level="internal", is_public=False
    )

    # Test
    assert (
        access_service.check_document_access(doc_id, user_id="user_1", user_roles=[])
    )


def test_restricted_access_denied(access_service):
    # Setup
    doc_id = "doc_restricted"
    access_service.get_document_access.return_value = Mock(
        access_level="restricted",
        allowed_roles=["admin"],
        allowed_users=[],
        is_public=False,
    )

    # Test
    assert (
        not access_service.check_document_access(
            doc_id, user_id="user_1", user_roles=["user"]
        )
    )


def test_restricted_access_allowed(access_service):
    # Setup
    doc_id = "doc_restricted"
    access_service.get_document_access.return_value = Mock(
        access_level="restricted",
        allowed_roles=["admin"],
        allowed_users=[],
        is_public=False,
    )

    # Test
    assert (
        access_service.check_document_access(
            doc_id, user_id="admin_user", user_roles=["admin"]
        )
    )
