"""
ChromaDB Client - Enterprise Vector Database Implementation
Handles all vector storage and similarity search operations
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import hashlib
from datetime import datetime

from ...core.config import settings

logger = logging.getLogger(__name__)

class ChromaDBClient:
    """
    Enterprise ChromaDB Client with proper collection management
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "streamworks_documents"
        self._initialized = False
        
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"✅ Connected to existing collection: {self.collection_name}")
            except:
                # Create collection with metadata
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "StreamWorks document embeddings",
                        "created_at": datetime.now().isoformat(),
                        "embedding_model": settings.EMBEDDING_MODEL
                    }
                )
                logger.info(f"✅ Created new collection: {self.collection_name}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> int:
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents with 'id', 'content', and 'metadata'
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            Number of documents added
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            if not documents:
                return 0
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                # Generate ID if not provided
                doc_id = doc.get("id")
                if not doc_id:
                    content_hash = hashlib.md5(
                        doc["content"].encode()
                    ).hexdigest()[:16]
                    doc_id = f"doc_{content_hash}"
                
                ids.append(doc_id)
                texts.append(doc["content"])
                
                # Prepare metadata
                metadata = doc.get("metadata", {})
                metadata["added_at"] = datetime.now().isoformat()
                metadatas.append(metadata)
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            else:
                # Let ChromaDB handle embedding generation
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            
            logger.info(f"✅ Added {len(documents)} documents to ChromaDB")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata if filter_metadata else None
            )
            
            # Format results
            formatted_results = []
            
            if results and results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
                distances = results["distances"][0] if results["distances"] else [0] * len(documents)
                ids = results["ids"][0] if results["ids"] else [""] * len(documents)
                
                for i, doc in enumerate(documents):
                    formatted_results.append({
                        "id": ids[i],
                        "content": doc,
                        "metadata": metadatas[i],
                        "score": 1 - distances[i],  # Convert distance to similarity score
                        "source": metadatas[i].get("source", "Unknown")
                    })
            
            logger.info(f"✅ Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Delete documents from the vector store
        
        Args:
            ids: List of document IDs to delete
            filter_metadata: Delete documents matching metadata
            
        Returns:
            Number of documents deleted (estimated)
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            if ids:
                self.collection.delete(ids=ids)
                logger.info(f"✅ Deleted {len(ids)} documents by ID")
                return len(ids)
            elif filter_metadata:
                # Get matching documents first to count them
                results = self.collection.get(where=filter_metadata)
                count = len(results["ids"]) if results["ids"] else 0
                
                if count > 0:
                    self.collection.delete(where=filter_metadata)
                    logger.info(f"✅ Deleted {count} documents by metadata filter")
                
                return count
            else:
                logger.warning("No deletion criteria provided")
                return 0
                
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Get collection info
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_model": settings.EMBEDDING_MODEL,
                "vector_db_path": settings.VECTOR_DB_PATH,
                "metadata": self.collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise
    
    async def reset_collection(self):
        """Reset the entire collection (use with caution!)"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "StreamWorks document embeddings",
                    "created_at": datetime.now().isoformat(),
                    "embedding_model": settings.EMBEDDING_MODEL
                }
            )
            
            logger.warning(f"⚠️ Collection {self.collection_name} has been reset!")
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise