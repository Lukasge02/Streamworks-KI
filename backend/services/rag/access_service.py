"""
Document Access Control Service
Enterprise-grade access management for RAG documents

Access Levels:
- public: Accessible by all users
- internal: Authenticated users only (default)
- restricted: Specific roles/users only
- project: Only within linked project context
"""

from typing import List, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging


class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PROJECT = "project"


@dataclass
class DocumentAccess:
    """Access control record for a document"""

    doc_id: str
    access_level: AccessLevel = AccessLevel.INTERNAL
    allowed_roles: List[str] = None
    allowed_users: List[str] = None
    is_public: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.allowed_roles is None:
            self.allowed_roles = []
        if self.allowed_users is None:
            self.allowed_users = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "doc_id": self.doc_id,
            "access_level": self.access_level.value
            if isinstance(self.access_level, AccessLevel)
            else self.access_level,
            "allowed_roles": self.allowed_roles,
            "allowed_users": self.allowed_users,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class CategoryAccess:
    """Access control record for a category (folder)"""

    category_path: str
    access_level: AccessLevel = AccessLevel.INTERNAL
    allowed_roles: List[str] = None
    inheritable: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.allowed_roles is None:
            self.allowed_roles = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "category_path": self.category_path,
            "access_level": self.access_level.value
            if isinstance(self.access_level, AccessLevel)
            else self.access_level,
            "allowed_roles": self.allowed_roles,
            "inheritable": self.inheritable,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AccessControlService:
    """
    Enterprise Document Access Control Service

    Features:
    - Document-level and category-level access control
    - Role-based permissions
    - Access inheritance from categories
    - Caching for performance
    """

    def __init__(self, db=None, vector_store=None):
        self._db = db
        self._vector_store = vector_store
        self.logger = logging.getLogger(__name__)

        # In-memory cache for access rules (MVP approach)
        # In production, use Supabase tables
        self._document_access_cache: Dict[str, DocumentAccess] = {}
        self._category_access_cache: Dict[str, CategoryAccess] = {}

    @property
    def db(self):
        if self._db is None:
            from services.db import db

            self._db = db
        return self._db

    @property
    def vector_store(self):
        if self._vector_store is None:
            from services.rag.vector_store import vector_store

            self._vector_store = vector_store
        return self._vector_store

    # =========================================================================
    # Document Access Management
    # =========================================================================

    def get_document_access(self, doc_id: str) -> Optional[DocumentAccess]:
        """
        Get access rules for a specific document.
        Falls back to category access if no document-specific rules exist.
        """
        # Try to get from Cache first
        if doc_id in self._document_access_cache:
            return self._document_access_cache[doc_id]

        # Try to get from Supabase DB (Enterprise Source of Truth)
        # This overrides Qdrant metadata if present in DB
        if self.db and self.db.client:
            try:
                # Check for explicit permissions override
                resp = (
                    self.db.client.table("document_permissions")
                    .select("*")
                    .eq("doc_id", doc_id)
                    .execute()
                )
                if resp.data:
                    # If we have entries, it implies Restricted access
                    # Collect allowed roles/users
                    allowed_roles = []
                    allowed_users = []
                    for perm in resp.data:
                        if perm.get("role"):
                            allowed_roles.append(perm.get("role"))
                        if perm.get("user_id"):
                            allowed_users.append(perm.get("user_id"))

                    return DocumentAccess(
                        doc_id=doc_id,
                        access_level=AccessLevel.RESTRICTED,
                        allowed_roles=list(set(allowed_roles)),
                        allowed_users=list(set(allowed_users)),
                    )
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch permissions from DB for {doc_id}: {e}"
                )

        # Fallback to Qdrant Metadata (Fast Path)
        doc = self.vector_store.get_document(doc_id)
        if doc:
            metadata = doc.get("metadata", {})
            access_level = metadata.get("access_level", AccessLevel.INTERNAL.value)
            category = metadata.get("category", "Allgemein")

            # If no document-specific access, check category
            cat_access = self.get_category_access(category)
            if cat_access and cat_access.inheritable:
                return DocumentAccess(
                    doc_id=doc_id,
                    access_level=AccessLevel(cat_access.access_level)
                    if isinstance(cat_access.access_level, str)
                    else cat_access.access_level,
                    allowed_roles=cat_access.allowed_roles,
                )

            return DocumentAccess(
                doc_id=doc_id,
                access_level=AccessLevel(access_level)
                if isinstance(access_level, str)
                else access_level,
            )

        # Default: internal access
        return DocumentAccess(doc_id=doc_id, access_level=AccessLevel.INTERNAL)

    def set_document_access(
        self,
        doc_id: str,
        access_level: str = "internal",
        allowed_roles: List[str] = None,
        allowed_users: List[str] = None,
    ) -> bool:
        """
        Set access rules for a specific document.
        Updates both cache and Qdrant metadata.
        """
        try:
            access = DocumentAccess(
                doc_id=doc_id,
                access_level=AccessLevel(access_level),
                allowed_roles=allowed_roles or [],
                allowed_users=allowed_users or [],
                is_public=(access_level == "public"),
            )

            # Update cache
            self._document_access_cache[doc_id] = access

            # Update Qdrant metadata
            self.vector_store.update_metadata(
                doc_id,
                {
                    "access_level": access_level,
                    "allowed_roles": allowed_roles or [],
                    "allowed_users": allowed_users or [],
                },
            )

            self.logger.info(f"Set access for {doc_id}: {access_level}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting document access: {e}")
            return False

    def check_document_access(
        self, doc_id: str, user_id: Optional[str] = None, user_roles: List[str] = None
    ) -> bool:
        """
        Check if a user has access to a specific document.

        Args:
            doc_id: The document ID to check
            user_id: Optional user ID
            user_roles: List of user's roles

        Returns:
            True if access is granted, False otherwise
        """
        user_roles = user_roles or []
        access = self.get_document_access(doc_id)

        if not access:
            return True  # Default allow if no rules

        # Public documents are always accessible
        if access.is_public or access.access_level == AccessLevel.PUBLIC:
            return True

        # Internal: requires authentication
        if (
            access.access_level == AccessLevel.INTERNAL
            or access.access_level == "internal"
        ):
            return user_id is not None

        # Restricted: check roles and users
        if (
            access.access_level == AccessLevel.RESTRICTED
            or access.access_level == "restricted"
        ):
            # Check if user is in allowed users
            if user_id and user_id in (access.allowed_users or []):
                return True

            # Check if user has allowed role
            if user_roles and access.allowed_roles:
                if any(role in access.allowed_roles for role in user_roles):
                    return True

            return False

        # Project: handled separately via project document links
        if (
            access.access_level == AccessLevel.PROJECT
            or access.access_level == "project"
        ):
            return True  # Access checked at project level

        return True

    # =========================================================================
    # Category Access Management
    # =========================================================================

    def get_category_access(self, category_path: str) -> Optional[CategoryAccess]:
        """Get access rules for a category."""
        if category_path in self._category_access_cache:
            return self._category_access_cache[category_path]

        # Default: internal access for all categories
        return CategoryAccess(
            category_path=category_path,
            access_level=AccessLevel.INTERNAL,
            inheritable=True,
        )

    def set_category_access(
        self,
        category_path: str,
        access_level: str = "internal",
        allowed_roles: List[str] = None,
        inheritable: bool = True,
    ) -> bool:
        """
        Set access rules for a category.
        All documents in the category will inherit these rules if inheritable=True.
        """
        try:
            access = CategoryAccess(
                category_path=category_path,
                access_level=AccessLevel(access_level),
                allowed_roles=allowed_roles or [],
                inheritable=inheritable,
            )

            self._category_access_cache[category_path] = access
            self.logger.info(f"Set category access for {category_path}: {access_level}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting category access: {e}")
            return False

    def list_category_access_rules(self) -> List[Dict]:
        """List all category access rules."""
        return [access.to_dict() for access in self._category_access_cache.values()]

    # =========================================================================
    # Bulk Access Operations
    # =========================================================================

    def get_accessible_doc_ids(
        self,
        user_id: Optional[str] = None,
        user_roles: List[str] = None,
        categories: List[str] = None,
    ) -> Set[str]:
        """
        Get all document IDs accessible by a user.

        Args:
            user_id: Optional user ID
            user_roles: User's roles
            categories: Optional filter by categories

        Returns:
            Set of accessible document IDs
        """
        user_roles = user_roles or []
        accessible_ids = set()

        try:
            # Get all documents from vector store
            all_parent_ids = self.vector_store.list_parent_doc_ids()

            for doc_id in all_parent_ids:
                # Check access
                if self.check_document_access(doc_id, user_id, user_roles):
                    # If category filter, check category
                    if categories:
                        doc = self.vector_store.get_document(doc_id)
                        if doc:
                            doc_category = doc.get("metadata", {}).get(
                                "category", "Allgemein"
                            )
                            if doc_category in categories:
                                accessible_ids.add(doc_id)
                    else:
                        accessible_ids.add(doc_id)

            return accessible_ids

        except Exception as e:
            self.logger.error(f"Error getting accessible doc IDs: {e}")
            return set()

    def filter_accessible_chunks(
        self,
        chunks: List[Dict],
        user_id: Optional[str] = None,
        user_roles: List[str] = None,
    ) -> List[Dict]:
        """
        Filter a list of search result chunks based on access control.

        Args:
            chunks: Search results from vector store
            user_id: Optional user ID
            user_roles: User's roles

        Returns:
            Filtered list of accessible chunks
        """
        user_roles = user_roles or []
        accessible_chunks = []

        for chunk in chunks:
            doc_id = chunk.get("doc_id") or chunk.get("metadata", {}).get(
                "parent_doc_id"
            )
            if doc_id and self.check_document_access(doc_id, user_id, user_roles):
                accessible_chunks.append(chunk)

        return accessible_chunks

    # =========================================================================
    # Project Document Selection (for Testing Page)
    # =========================================================================

    def get_project_selected_docs(self, project_id: str) -> List[str]:
        """
        Get list of document IDs selected for RAG in a project.
        """
        try:
            # Get from project_documents table via db service
            links = self.db.get_project_documents(project_id)
            return [link.get("doc_id") for link in links if link.get("doc_id")]
        except Exception as e:
            self.logger.error(f"Error getting project documents: {e}")
            return []

    def set_project_selected_docs(
        self, project_id: str, doc_ids: List[str], rag_enabled: bool = True
    ) -> bool:
        """
        Set which documents are selected for RAG in a project.
        This is used for explicit document selection in Testing page.
        """
        # This would update project_documents table
        # For MVP, we use the existing link_project_document / unlink_project_document
        return True


# Singleton instance
_access_service_instance = None


def get_access_service() -> AccessControlService:
    global _access_service_instance
    if _access_service_instance is None:
        _access_service_instance = AccessControlService()
    return _access_service_instance
