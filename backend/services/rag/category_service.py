"""
Document Category Service v2
Robust document organization with proper deduplication by parent_doc_id
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import os
import json


@dataclass
class Category:
    """Represents a document category/folder"""

    name: str
    path: str  # Full path like "Bachelorarbeit/Kapitel1"
    parent: Optional[str] = None
    document_count: int = 0
    children: List["Category"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "parent": self.parent,
            "document_count": self.document_count,
            "children": [c.to_dict() for c in self.children],
        }


class CategoryService:
    """
    Service for managing document categories v2

    Key improvements:
    - Proper deduplication by parent_doc_id (counts documents, not chunks)
    - Efficient single-query approach for counting
    - Robust persistence for empty categories

    Categories are implemented using:
    1. Qdrant metadata for document-category associations
    2. JSON file for persisting empty categories (so they don't disappear)
    """

    DEFAULT_CATEGORY = "Allgemein"
    CATEGORIES_FILE = "storage/categories.json"

    def __init__(self, vector_store):
        self._vector_store = vector_store
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(self.CATEGORIES_FILE), exist_ok=True)

    # ==========================================
    # Storage Methods (for empty categories)
    # ==========================================

    def _load_stored_categories(self) -> Set[str]:
        """Load stored categories from JSON file"""
        try:
            if os.path.exists(self.CATEGORIES_FILE):
                with open(self.CATEGORIES_FILE, "r") as f:
                    data = json.load(f)
                    return set(data.get("categories", []))
        except Exception as e:
            print(f"⚠️ Failed to load categories: {e}")
        return set()

    def _save_stored_categories(self, categories: Set[str]) -> bool:
        """Save categories to JSON file"""
        try:
            with open(self.CATEGORIES_FILE, "w") as f:
                json.dump({"categories": list(categories)}, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Failed to save categories: {e}")
            return False

    def _add_stored_category(self, name: str) -> bool:
        """Add a category to storage"""
        cats = self._load_stored_categories()
        cats.add(name)
        return self._save_stored_categories(cats)

    def _remove_stored_category(self, name: str) -> bool:
        """Remove a category from storage"""
        cats = self._load_stored_categories()
        cats.discard(name)
        return self._save_stored_categories(cats)

    # ==========================================
    # Core Methods - REFACTORED for v2
    # ==========================================

    def _get_all_documents_with_categories(self) -> Tuple[Dict[str, Set[str]], int]:
        """
        Get all documents with their categories, properly deduplicated by parent_doc_id.

        Returns:
            Tuple of (category_to_doc_ids dict, total_unique_document_count)
        """
        category_doc_ids: Dict[str, Set[str]] = {}  # category -> set of parent_doc_ids
        all_doc_ids: Set[str] = set()  # All unique documents

        try:
            offset = None
            batch_count = 0

            while True:
                # Scroll through ALL documents in Qdrant
                scroll_result = self._vector_store.client.scroll(
                    collection_name=self._vector_store.COLLECTION_NAME,
                    limit=500,
                    offset=offset,
                    with_payload=["parent_doc_id", "doc_id", "category"],
                )

                points, next_offset = scroll_result
                batch_count += 1

                for point in points:
                    payload = point.payload
                    # Use parent_doc_id for deduplication, fallback to doc_id
                    parent_id = payload.get("parent_doc_id") or payload.get("doc_id")

                    if not parent_id:
                        continue

                    # Track unique documents
                    all_doc_ids.add(parent_id)

                    # Get category (default to Allgemein)
                    category = payload.get("category") or self.DEFAULT_CATEGORY

                    # Add to category bucket
                    if category not in category_doc_ids:
                        category_doc_ids[category] = set()
                    category_doc_ids[category].add(parent_id)

                if next_offset is None:
                    break
                offset = next_offset

            print(
                f"📊 Scanned {batch_count} batches, found {len(all_doc_ids)} unique documents"
            )

        except Exception as e:
            print(f"❌ Error scanning documents: {e}")
            import traceback

            traceback.print_exc()

        return category_doc_ids, len(all_doc_ids)

    def list_categories(self) -> List[Category]:
        """
        List all categories with accurate document counts.

        REFACTORED v2:
        - Counts unique DOCUMENTS (by parent_doc_id), not chunks
        - Includes stored categories (even if empty)
        - Single efficient scan of all documents
        """
        # Get stored categories (includes empty ones)
        stored_categories = self._load_stored_categories()

        # Ensure default category exists
        stored_categories.add(self.DEFAULT_CATEGORY)

        # Get document counts per category
        category_doc_ids, _ = self._get_all_documents_with_categories()

        # Combine stored + found categories
        all_category_names = set(stored_categories) | set(category_doc_ids.keys())

        # Build category list with correct counts
        categories = []
        for cat_name in sorted(all_category_names):
            doc_count = len(category_doc_ids.get(cat_name, set()))

            parts = cat_name.split("/")
            categories.append(
                Category(
                    name=parts[-1],
                    path=cat_name,
                    parent="/".join(parts[:-1]) if len(parts) > 1 else None,
                    document_count=doc_count,
                )
            )

        return categories

    def get_total_document_count(self) -> int:
        """
        Get total count of unique documents (not chunks).

        This is the count that should be displayed for "Alle Dokumente".
        """
        _, total_count = self._get_all_documents_with_categories()
        return total_count

    def get_category_counts(self) -> Dict[str, Any]:
        """
        Get all category counts in a single call.

        Returns dict with:
        - total_documents: int (count for "Alle Dokumente")
        - categories: List[Category] (each with document_count)
        """
        stored_categories = self._load_stored_categories()
        stored_categories.add(self.DEFAULT_CATEGORY)

        category_doc_ids, total_count = self._get_all_documents_with_categories()

        all_category_names = set(stored_categories) | set(category_doc_ids.keys())

        categories = []
        for cat_name in sorted(all_category_names):
            doc_count = len(category_doc_ids.get(cat_name, set()))
            parts = cat_name.split("/")
            categories.append(
                Category(
                    name=parts[-1],
                    path=cat_name,
                    parent="/".join(parts[:-1]) if len(parts) > 1 else None,
                    document_count=doc_count,
                )
            )

        return {"total_documents": total_count, "categories": categories}

    def create_category(self, name: str, parent: Optional[str] = None) -> Category:
        """
        Create a new category and persist it.

        Categories are stored in JSON file so they persist even when empty.
        """
        # Validate name
        invalid_chars = ["/", "\\", "<", ">", ":", '"', "|", "?", "*"]
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Category name cannot contain '{char}'")

        # Build full path
        path = f"{parent}/{name}" if parent else name

        # Persist the category
        self._add_stored_category(path)

        print(f"✅ Created category: {path}")

        return Category(name=name, path=path, parent=parent, document_count=0)

    def move_document(self, doc_id: str, new_category: str) -> bool:
        """
        Move a document to a different category.

        REFACTORED v2:
        - Updates ALL chunks with the same parent_doc_id
        - Works whether doc_id is a chunk ID or parent ID
        """
        try:
            from qdrant_client.http import models

            # First, determine the parent_doc_id
            # The provided doc_id could be either a chunk ID or parent ID
            parent_id = None

            # Search for documents matching this doc_id
            scroll_result = self._vector_store.client.scroll(
                collection_name=self._vector_store.COLLECTION_NAME,
                limit=1,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="doc_id", match=models.MatchValue(value=doc_id)
                        ),
                        models.FieldCondition(
                            key="parent_doc_id", match=models.MatchValue(value=doc_id)
                        ),
                    ]
                ),
                with_payload=["doc_id", "parent_doc_id"],
            )

            points, _ = scroll_result
            if not points:
                print(f"⚠️ Document not found: {doc_id}")
                return False

            # Get the parent_doc_id
            payload = points[0].payload
            parent_id = payload.get("parent_doc_id") or payload.get("doc_id")

            # Now find ALL chunks with this parent_doc_id and update them
            all_chunks_result = self._vector_store.client.scroll(
                collection_name=self._vector_store.COLLECTION_NAME,
                limit=1000,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="parent_doc_id",
                            match=models.MatchValue(value=parent_id),
                        ),
                        models.FieldCondition(
                            key="doc_id", match=models.MatchValue(value=parent_id)
                        ),
                    ]
                ),
                with_payload=False,  # We only need IDs
            )

            chunk_points, _ = all_chunks_result
            point_ids = [p.id for p in chunk_points]

            if not point_ids:
                print(f"⚠️ No chunks found for document: {parent_id}")
                return False

            # Update category for all chunks
            self._vector_store.client.set_payload(
                collection_name=self._vector_store.COLLECTION_NAME,
                payload={"category": new_category},
                points=point_ids,
            )

            # Ensure the new category is stored (so it appears even if later empty)
            self._add_stored_category(new_category)

            print(f"✅ Moved {len(point_ids)} chunk(s) to category: {new_category}")
            return True

        except Exception as e:
            print(f"❌ Failed to move document: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_documents_by_category(
        self, category: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all unique documents in a specific category.

        Returns deduplicated list (one entry per document, not per chunk).
        """
        from qdrant_client.http import models

        try:
            seen_parents: Set[str] = set()
            result: List[Dict[str, Any]] = []
            offset = None

            # Handle "Allgemein" category (includes null and empty)
            if category == self.DEFAULT_CATEGORY:
                # We need to match category IS NULL OR category = "Allgemein" OR category = ""
                # Unfortunately Qdrant doesn't have IS NULL, so we scan and filter
                while len(result) < limit:
                    scroll_result = self._vector_store.client.scroll(
                        collection_name=self._vector_store.COLLECTION_NAME,
                        limit=500,
                        offset=offset,
                        with_payload=True,
                    )

                    points, next_offset = scroll_result

                    for point in points:
                        payload = point.payload
                        doc_cat = payload.get("category") or self.DEFAULT_CATEGORY

                        if doc_cat != self.DEFAULT_CATEGORY:
                            continue

                        parent_id = payload.get("parent_doc_id") or payload.get(
                            "doc_id"
                        )

                        if parent_id not in seen_parents:
                            seen_parents.add(parent_id)
                            result.append(
                                {
                                    "doc_id": payload.get("doc_id"),
                                    "parent_doc_id": parent_id,
                                    "filename": payload.get("filename"),
                                    "doc_type": payload.get("doc_type"),
                                    "created_at": payload.get("created_at"),
                                    "category": doc_cat,
                                }
                            )

                            if len(result) >= limit:
                                break

                    if next_offset is None or len(result) >= limit:
                        break
                    offset = next_offset
            else:
                # Specific category - use filter
                while len(result) < limit:
                    scroll_result = self._vector_store.client.scroll(
                        collection_name=self._vector_store.COLLECTION_NAME,
                        limit=500,
                        offset=offset,
                        scroll_filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="category",
                                    match=models.MatchValue(value=category),
                                )
                            ]
                        ),
                        with_payload=True,
                    )

                    points, next_offset = scroll_result

                    for point in points:
                        payload = point.payload
                        parent_id = payload.get("parent_doc_id") or payload.get(
                            "doc_id"
                        )

                        if parent_id not in seen_parents:
                            seen_parents.add(parent_id)
                            result.append(
                                {
                                    "doc_id": payload.get("doc_id"),
                                    "parent_doc_id": parent_id,
                                    "filename": payload.get("filename"),
                                    "doc_type": payload.get("doc_type"),
                                    "created_at": payload.get("created_at"),
                                    "category": category,
                                }
                            )

                            if len(result) >= limit:
                                break

                    if next_offset is None or len(result) >= limit:
                        break
                    offset = next_offset

            return result

        except Exception as e:
            print(f"❌ Failed to get documents: {e}")
            import traceback

            traceback.print_exc()
            return []

    def delete_category(
        self, category: str, move_to: Optional[str] = None, cascade: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a category.

        Args:
            category: Category name to delete
            move_to: If not cascade, move documents to this category (default: Allgemein)
            cascade: If True, permanently delete all documents in the category

        Returns:
            Dict with deletion report
        """
        result = {
            "category": category,
            "cascade": cascade,
            "documents_affected": 0,
            "success": False,
        }

        try:
            docs = self.get_documents_by_category(category)
            result["documents_affected"] = len(docs)

            if cascade:
                # CASCADE DELETE: Delete all documents
                from services.rag.storage.file_storage import get_file_storage

                file_storage = get_file_storage()

                deleted_count = 0
                for doc in docs:
                    parent_id = doc.get("parent_doc_id") or doc.get("doc_id")

                    # Delete from Qdrant (all chunks)
                    chunks_deleted = self._vector_store.delete_by_parent_id(parent_id)

                    # Delete from MinIO
                    file_storage.delete_file(parent_id)

                    deleted_count += 1

                result["documents_deleted"] = deleted_count
                print(
                    f"🗑️ CASCADE DELETE: Deleted {deleted_count} documents from '{category}'"
                )

            else:
                # MOVE: Move documents to target category
                target = move_to or self.DEFAULT_CATEGORY
                for doc in docs:
                    parent_id = doc.get("parent_doc_id") or doc.get("doc_id")
                    self.move_document(parent_id, target)

                result["moved_to"] = target
                print(f"📦 Moved {len(docs)} documents from '{category}' to '{target}'")

            # Remove category from storage
            self._remove_stored_category(category)
            result["success"] = True

        except Exception as e:
            print(f"❌ Failed to delete category: {e}")
            import traceback

            traceback.print_exc()
            result["error"] = str(e)

        return result

    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        Rename a category by moving all documents and updating storage.
        """
        if not new_name or not new_name.strip():
            return False

        new_name = new_name.strip()

        try:
            # Check if category exists
            stored_cats = self._load_stored_categories()
            docs = self.get_documents_by_category(old_name)

            if not docs and old_name not in stored_cats:
                print(f"⚠️ Category does not exist: {old_name}")
                return False

            # Move all documents to the new category name
            for doc in docs:
                parent_id = doc.get("parent_doc_id") or doc.get("doc_id")
                self.move_document(parent_id, new_name)

            # Update storage: remove old, add new
            self._remove_stored_category(old_name)
            self._add_stored_category(new_name)

            print(
                f"✅ Renamed category '{old_name}' to '{new_name}' ({len(docs)} documents)"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to rename category: {e}")
            return False


# Singleton instance
_category_service = None


def get_category_service():
    """Get or create the category service singleton"""
    global _category_service

    if _category_service is None:
        from services.rag.vector_store import vector_store

        _category_service = CategoryService(vector_store=vector_store)

    return _category_service
