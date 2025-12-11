"""
Document Category Service
Manages document organization using MinIO prefixes and Qdrant metadata
"""

from typing import List, Dict, Any, Optional, Set
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
            "children": [c.to_dict() for c in self.children]
        }


class CategoryService:
    """
    Service for managing document categories
    
    Categories are implemented using:
    1. MinIO object prefixes for file organization
    2. Qdrant metadata for document-category associations
    3. JSON file for persisting empty categories
    
    This approach provides:
    - Visual folder structure in MinIO console
    - Fast category filtering via Qdrant queries
    - Persistence for empty categories
    """
    
    DEFAULT_CATEGORY = "Allgemein"
    CATEGORIES_FILE = "storage/categories.json"
    
    def __init__(self, file_storage, vector_store):
        self._file_storage = file_storage
        self._vector_store = vector_store
        self._categories_cache = None
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(self.CATEGORIES_FILE), exist_ok=True)
    
    def _load_stored_categories(self) -> Set[str]:
        """Load stored categories from JSON file"""
        try:
            if os.path.exists(self.CATEGORIES_FILE):
                with open(self.CATEGORIES_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data.get("categories", []))
        except Exception as e:
            print(f"⚠️ Failed to load categories: {e}")
        return set()
    
    def _save_stored_categories(self, categories: Set[str]) -> bool:
        """Save categories to JSON file"""
        try:
            with open(self.CATEGORIES_FILE, 'w') as f:
                json.dump({"categories": list(categories)}, f)
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
    
    def list_categories(self) -> List[Category]:
        """
        List all categories by scanning document metadata AND stored categories
        Returns hierarchical category structure
        """
        # Start with stored categories (including empty ones)
        categories_set = self._load_stored_categories()
        seen_parents = set()
        
        try:
            # Scroll through all documents to find categories with documents
            docs = self._vector_store.list_documents(limit=1000)
            
            for doc in docs:
                # Deduplicate by parent_doc_id to count unique documents
                parent_id = doc.get("parent_doc_id") or doc.get("doc_id")
                
                if parent_id in seen_parents:
                    continue
                seen_parents.add(parent_id)
                
                # Get category (default to Allgemein)
                category = doc.get("category") or self.DEFAULT_CATEGORY
                categories_set.add(category)
                
        except Exception as e:
            print(f"⚠️ Error listing categories: {e}")
        
        # Build category tree
        categories = []
        for cat_path in sorted(categories_set):
            parts = cat_path.split("/")
            cat = Category(
                name=parts[-1],
                path=cat_path,
                parent="/".join(parts[:-1]) if len(parts) > 1 else None
            )
            categories.append(cat)
        
        # Count documents per category
        for cat in categories:
            cat.document_count = self._count_documents_in_category(cat.path)
        
        return categories
    
    def _count_documents_in_category(self, category: str) -> int:
        """Count documents in a specific category"""
        try:
            docs = self._vector_store.list_documents(limit=1000)
            count = 0
            seen_parents = set()
            
            for doc in docs:
                doc_cat = doc.get("category") or self.DEFAULT_CATEGORY
                parent_id = doc.get("parent_doc_id")
                
                # Match category and only count unique parent docs
                if doc_cat == category:
                    if parent_id and parent_id not in seen_parents:
                        seen_parents.add(parent_id)
                        count += 1
                    elif not parent_id:
                        count += 1
            
            return count
        except Exception:
            return 0
    
    def create_category(self, name: str, parent: Optional[str] = None) -> Category:
        """
        Create a new category and persist it
        
        Categories are stored in JSON file so they persist even when empty.
        """
        # Validate name
        invalid_chars = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Category name cannot contain '{char}'")
        
        # Build full path
        path = f"{parent}/{name}" if parent else name
        
        # Persist the category
        self._add_stored_category(path)
        
        return Category(
            name=name,
            path=path,
            parent=parent,
            document_count=0
        )
    
    def move_document(self, doc_id: str, new_category: str) -> bool:
        """
        Move a document to a different category
        
        Updates the category metadata in Qdrant for the document
        and all its chunks.
        
        Args:
            doc_id: Can be either a chunk doc_id OR a parent_doc_id
            new_category: Target category name
        """
        try:
            # Get all documents and find matching ones
            all_docs = self._vector_store.list_documents(limit=1000)
            
            # First, determine the parent_doc_id
            # The provided doc_id could be either a chunk ID or parent ID
            parent_id = None
            
            for d in all_docs:
                d_id = d.get("doc_id")
                d_parent = d.get("parent_doc_id")
                
                # Check if doc_id matches this chunk's doc_id
                if d_id == doc_id:
                    parent_id = d_parent or d_id
                    break
                # Check if doc_id matches this chunk's parent_doc_id
                if d_parent == doc_id:
                    parent_id = doc_id
                    break
            
            if not parent_id:
                print(f"⚠️ Document not found: {doc_id}")
                return False
            
            # Update all chunks with the same parent_doc_id
            updated = 0
            for d in all_docs:
                d_parent = d.get("parent_doc_id", d.get("doc_id"))
                if d_parent == parent_id:
                    # Update category in metadata
                    self._vector_store.update_metadata(
                        d.get("doc_id"),
                        {"category": new_category}
                    )
                    updated += 1
            
            print(f"✅ Moved {updated} chunk(s) to category: {new_category}")
            return updated > 0
            
        except Exception as e:
            print(f"❌ Failed to move document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_documents_by_category(
        self, 
        category: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all documents in a specific category"""
        try:
            all_docs = self._vector_store.list_documents(limit=1000)
            
            # Filter by category and deduplicate by parent_doc_id
            seen_parents = set()
            result = []
            
            for doc in all_docs:
                doc_cat = doc.get("category") or self.DEFAULT_CATEGORY
                parent_id = doc.get("parent_doc_id", doc.get("doc_id"))
                
                if doc_cat == category and parent_id not in seen_parents:
                    seen_parents.add(parent_id)
                    result.append(doc)
                    
                    if len(result) >= limit:
                        break
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to get documents: {e}")
            return []
    
    def delete_category(self, category: str, move_to: Optional[str] = None) -> bool:
        """
        Delete a category and remove from storage
        
        If move_to is provided, documents are moved to that category.
        Otherwise, documents are moved to the default category.
        """
        target = move_to or self.DEFAULT_CATEGORY
        
        try:
            # Move documents to target category
            docs = self.get_documents_by_category(category)
            for doc in docs:
                self.move_document(doc.get("doc_id"), target)
            
            # Remove from storage
            self._remove_stored_category(category)
            
            return True
        except Exception as e:
            print(f"❌ Failed to delete category: {e}")
            return False
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        Rename a category by moving all documents and updating storage
        """
        if not new_name or not new_name.strip():
            return False
        
        new_name = new_name.strip()
        
        try:
            # Check if category exists in storage
            stored_cats = self._load_stored_categories()
            category_exists = old_name in stored_cats
            
            docs = self.get_documents_by_category(old_name)
            
            if not docs and not category_exists:
                # Category doesn't exist anywhere
                return False
            
            # Move all documents to the new category name
            for doc in docs:
                doc_id = doc.get("parent_doc_id") or doc.get("doc_id")
                self.move_document(doc_id, new_name)
            
            # Update storage: remove old, add new
            self._remove_stored_category(old_name)
            self._add_stored_category(new_name)
            
            print(f"✅ Renamed category '{old_name}' to '{new_name}' ({len(docs)} documents)")
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
        # Import singletons directly to avoid circular imports
        from services.rag.document_service import document_service
        from services.rag.vector_store import vector_store
        
        _category_service = CategoryService(
            file_storage=document_service._file_storage,
            vector_store=vector_store
        )
    
    return _category_service
