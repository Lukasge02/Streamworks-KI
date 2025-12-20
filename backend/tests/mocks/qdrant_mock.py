"""
Qdrant/Vector Store Mock

Provides mock implementations for vector database operations.
Simulates search, storage, and retrieval without actual Qdrant connection.
"""

from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any, Optional
import uuid


class MockSearchResult:
    """Mock vector search result."""
    
    def __init__(
        self,
        doc_id: str,
        text: str,
        score: float,
        metadata: Dict[str, Any] = None
    ):
        self.id = f"chunk-{uuid.uuid4().hex[:8]}"
        self.doc_id = doc_id
        self.text = text
        self.score = score
        self.metadata = metadata or {}
        
        # Qdrant-style payload
        self.payload = {
            "doc_id": doc_id,
            "text": text,
            **self.metadata
        }


class MockVectorStore:
    """
    Mock vector store for testing RAG operations.
    
    Usage:
        store = MockVectorStore()
        store.add_documents([...])
        results = store.search("query", top_k=5)
    """
    
    def __init__(self):
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._chunks: List[Dict[str, Any]] = []
        self._search_results: List[MockSearchResult] = []
    
    def add_document(
        self,
        doc_id: str,
        chunks: List[str],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a document with chunks to the store."""
        self._documents[doc_id] = {
            "doc_id": doc_id,
            "chunks": chunks,
            "metadata": metadata or {},
        }
        
        for i, chunk in enumerate(chunks):
            self._chunks.append({
                "id": f"{doc_id}-chunk-{i}",
                "doc_id": doc_id,
                "text": chunk,
                "metadata": {**(metadata or {}), "chunk_index": i},
            })
        
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the store."""
        if doc_id in self._documents:
            del self._documents[doc_id]
            self._chunks = [c for c in self._chunks if c["doc_id"] != doc_id]
            return True
        return False
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self._documents.get(doc_id)
    
    def set_search_results(self, results: List[MockSearchResult]):
        """Configure search results to return."""
        self._search_results = results
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        access_filter: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search the vector store.
        
        If search_results were set, returns those.
        Otherwise returns matching chunks from added documents.
        """
        if self._search_results:
            return [
                {
                    "id": r.id,
                    "doc_id": r.doc_id,
                    "text": r.text,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in self._search_results[:top_k]
            ]
        
        # Filter by access if provided
        allowed_doc_ids = None
        if access_filter and "doc_ids" in access_filter:
            allowed_doc_ids = access_filter["doc_ids"]
        
        results = []
        for chunk in self._chunks:
            if allowed_doc_ids and chunk["doc_id"] not in allowed_doc_ids:
                continue
            
            # Simple keyword matching for testing
            if query.lower() in chunk["text"].lower():
                results.append({
                    **chunk,
                    "score": 0.9,
                })
        
        return results[:top_k]
    
    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Vector similarity search (returns configured results)."""
        return self.search("", top_k, **kwargs)


def create_search_results(
    count: int = 3,
    doc_id: str = None,
    base_score: float = 0.9
) -> List[MockSearchResult]:
    """
    Create a list of mock search results.
    
    Args:
        count: Number of results to create
        doc_id: Optional doc_id for all results
        base_score: Starting score (decreases for each result)
    
    Returns:
        List of MockSearchResult objects
    """
    results = []
    for i in range(count):
        results.append(MockSearchResult(
            doc_id=doc_id or f"doc-{i+1:03d}",
            text=f"This is chunk {i+1} with relevant information about the query.",
            score=base_score - (i * 0.05),
            metadata={
                "filename": f"document_{i+1}.pdf",
                "page": i + 1,
                "chunk_index": i,
            }
        ))
    return results


def create_rag_context(search_results: List[MockSearchResult]) -> str:
    """
    Create a context string from search results (as RAG would).
    
    Args:
        search_results: List of search results
    
    Returns:
        Formatted context string
    """
    context_parts = []
    for i, result in enumerate(search_results, 1):
        context_parts.append(
            f"[Source {i}] ({result.metadata.get('filename', 'unknown')})\n"
            f"{result.text}\n"
        )
    return "\n".join(context_parts)
