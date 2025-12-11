"""
Qdrant Vector Store Service
Enterprise-ready vector database integration with OpenAI embeddings
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import openai
from config import config


class VectorStore:
    """
    Enterprise Vector Store using Qdrant
    - OpenAI text-embedding-3-small for embeddings
    - Persistent storage via Docker
    - Batch processing for efficiency
    """
    
    COLLECTION_NAME = "streamworks_documents"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.COLLECTION_NAME}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.openai_client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        if not texts:
            return []
        
        # OpenAI allows batch embedding
        response = self.openai_client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def _generate_id(self, content: str, filename: str) -> str:
        """Generate deterministic ID from content"""
        hash_input = f"{filename}:{content[:500]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """Add a single document to the vector store"""
        if doc_id is None:
            doc_id = self._generate_id(content, metadata.get("filename", "unknown"))
        
        embedding = self._generate_embedding(content)
        
        # Convert doc_id to integer hash for Qdrant
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:16], 16)
        
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "doc_id": doc_id,
                        "content": content,
                        **metadata
                    }
                )
            ]
        )
        
        return doc_id
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents efficiently
        
        Each document should have:
        - content: str
        - metadata: Dict
        """
        if not documents:
            return []
        
        # Extract texts and generate embeddings in batch
        texts = [doc["content"] for doc in documents]
        embeddings = self._generate_embeddings_batch(texts)
        
        points = []
        doc_ids = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = self._generate_id(doc["content"], doc.get("metadata", {}).get("filename", f"doc_{i}"))
            point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:16], 16)
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "doc_id": doc_id,
                        "content": doc["content"],
                        **doc.get("metadata", {})
                    }
                )
            )
            doc_ids.append(doc_id)
        
        # Batch upsert
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )
        
        return doc_ids
    
    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents
        
        Returns list of matches with content, metadata, and score
        """
        query_embedding = self._generate_embedding(query)
        
        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "doc_id": hit.payload.get("doc_id"),
                "content": hit.payload.get("content"),
                "filename": hit.payload.get("filename"),
                "doc_type": hit.payload.get("doc_type"),
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() 
                           if k not in ["doc_id", "content"]}
            }
            for hit in results
        ]
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID"""
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:16], 16)
        
        try:
            results = self.client.retrieve(
                collection_name=self.COLLECTION_NAME,
                ids=[point_id]
            )
            if results:
                payload = results[0].payload
                return {
                    "doc_id": payload.get("doc_id"),
                    "content": payload.get("content"),
                    "metadata": {k: v for k, v in payload.items() 
                               if k not in ["doc_id", "content"]}
                }
        except Exception:
            pass
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:16], 16)
        
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=models.PointIdsList(points=[point_id])
            )
            return True
        except Exception:
            return False
    
    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all documents with pagination"""
        results = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            limit=limit,
            offset=offset,
            with_payload=True
        )
        
        documents = []
        for point in results[0]:
            payload = point.payload
            documents.append({
                "doc_id": payload.get("doc_id"),
                "filename": payload.get("filename"),
                "doc_type": payload.get("doc_type"),
                "created_at": payload.get("created_at"),
                "parent_doc_id": payload.get("parent_doc_id"),
                # Category
                "category": payload.get("category"),
                # Chunk metadata
                "chunk_index": payload.get("chunk_index"),
                "total_chunks": payload.get("total_chunks"),
                "chunk_word_count": payload.get("chunk_word_count"),
                "chunk_page_numbers": payload.get("chunk_page_numbers", []),
                "chunk_section_title": payload.get("chunk_section_title"),
                # Don't include full content in list view
                "content_preview": payload.get("content", "")[:200] + "..."
            })
        
        return documents
    
    def delete_by_parent_id(self, parent_doc_id: str) -> int:
        """
        Delete ALL chunks belonging to a parent document.
        Returns the number of deleted chunks.
        """
        deleted_count = 0
        
        try:
            # First, find all points with this parent_doc_id
            # We need to scroll through all points and filter
            scroll_result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=1000,
                with_payload=True,
                scroll_filter=models.Filter(
                    should=[
                        # Match documents where parent_doc_id equals the given ID
                        models.FieldCondition(
                            key="parent_doc_id",
                            match=models.MatchValue(value=parent_doc_id)
                        ),
                        # Also match the parent document itself (doc_id = parent_doc_id)
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=parent_doc_id)
                        )
                    ]
                )
            )
            
            points_to_delete = [point.id for point in scroll_result[0]]
            
            if points_to_delete:
                self.client.delete(
                    collection_name=self.COLLECTION_NAME,
                    points_selector=models.PointIdsList(points=points_to_delete)
                )
                deleted_count = len(points_to_delete)
                print(f"✅ Deleted {deleted_count} chunks for parent_doc_id: {parent_doc_id}")
            
        except Exception as e:
            print(f"❌ Error deleting by parent_id: {e}")
        
        return deleted_count
    
    def list_parent_doc_ids(self) -> List[str]:
        """
        Get list of unique parent document IDs.
        For documents with chunks: returns parent_doc_id
        For single-chunk documents: returns doc_id
        """
        parent_ids = set()
        
        try:
            offset = None
            while True:
                scroll_result = self.client.scroll(
                    collection_name=self.COLLECTION_NAME,
                    limit=100,
                    offset=offset,
                    with_payload=["doc_id", "parent_doc_id"]
                )
                
                points, next_offset = scroll_result
                
                for point in points:
                    # Use parent_doc_id if available, otherwise doc_id
                    parent_id = point.payload.get("parent_doc_id") or point.payload.get("doc_id")
                    if parent_id:
                        parent_ids.add(parent_id)
                
                if next_offset is None:
                    break
                offset = next_offset
                
        except Exception as e:
            print(f"❌ Error listing parent_doc_ids: {e}")
        
        return list(parent_ids)
    
    def get_all_doc_ids(self) -> set:
        """
        Get all unique doc_ids stored in Qdrant.
        Used for consistency checks with MinIO.
        """
        doc_ids = set()
        
        try:
            offset = None
            while True:
                scroll_result = self.client.scroll(
                    collection_name=self.COLLECTION_NAME,
                    limit=100,
                    offset=offset,
                    with_payload=["doc_id", "parent_doc_id"]
                )
                
                points, next_offset = scroll_result
                
                for point in points:
                    doc_id = point.payload.get("doc_id")
                    parent_id = point.payload.get("parent_doc_id")
                    if doc_id:
                        doc_ids.add(doc_id)
                    if parent_id:
                        doc_ids.add(parent_id)
                
                if next_offset is None:
                    break
                offset = next_offset
                
        except Exception as e:
            print(f"❌ Error getting all doc_ids: {e}")
        
        return doc_ids
    
    def update_metadata(self, doc_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """
        Update metadata fields for a specific document.
        
        Args:
            doc_id: The document ID to update
            metadata_updates: Dict of metadata fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the point by doc_id in payload using scroll with filter
            scroll_result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=1,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=doc_id)
                        )
                    ]
                ),
                with_payload=True
            )
            
            points, _ = scroll_result
            
            if not points:
                print(f"⚠️ Document not found: {doc_id}")
                return False
            
            # Get the point ID
            point_id = points[0].id
            
            # Update the point with new payload (merges with existing)
            self.client.set_payload(
                collection_name=self.COLLECTION_NAME,
                payload=metadata_updates,
                points=[point_id]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating metadata: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = self.client.get_collection(self.COLLECTION_NAME)
            return {
                "collection": self.COLLECTION_NAME,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value,
                "embedding_model": self.EMBEDDING_MODEL,
                "embedding_dimension": self.EMBEDDING_DIMENSION
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
vector_store = VectorStore()
