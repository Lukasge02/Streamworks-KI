"""
Vector Store Service für Streamworks RAG MVP
ChromaDB Integration für efficient vector storage und retrieval
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
import chromadb
import json
from datetime import datetime
import uuid

from config import settings
from .docling_ingest import DocumentChunk

class VectorStoreService:
    """Service für vector storage mit ChromaDB"""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.collection_name = "streamworks_documents"
        
    async def initialize(self):
        """Initialize ChromaDB connection und collection"""
        try:
            # Create ChromaDB client with new API
            self.chroma_client = chromadb.PersistentClient(
                path=str(settings.CHROMA_PATH)
            )
            
            # Try to get existing collection first
            try:
                self.collection = self.chroma_client.get_collection(name=self.collection_name)
                print(f"✅ Using existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create new one
                # Create collection without specifying dimensions - ChromaDB will auto-detect from first embedding
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "Streamworks document chunks with hybrid embeddings (Gamma/OpenAI)",
                        "embedding_provider": settings.EMBEDDING_PROVIDER,
                        "supports_dynamic_dimensions": True
                    }
                )
                print(f"✅ Created new collection: {self.collection_name}")
            
            print(f"✅ ChromaDB initialized - Collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ ChromaDB initialization failed: {str(e)}")
            raise Exception(f"Vector store initialization error: {str(e)}")
    
    async def store_chunks(self, chunks: List[Union[DocumentChunk, Dict[str, Any]]], doc_id: str):
        """
        Store document chunks with embeddings in ChromaDB
        
        Args:
            chunks: List of DocumentChunk objects or dictionaries with embeddings
            doc_id: Document identifier
        """
        try:
            if not self.collection:
                await self.initialize()
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                # Handle both DocumentChunk objects and dictionary format
                if isinstance(chunk, dict):
                    # Dictionary format from unified storage
                    chunk_id = chunk.get("id")
                    text = chunk.get("text", "")
                    metadata = chunk.get("metadata", {})
                    
                    # Ensure chunk has embedding
                    if 'embedding' not in metadata:
                        raise ValueError(f"Chunk {chunk_id} missing embedding")
                    
                    ids.append(chunk_id)
                    embeddings.append(metadata['embedding'])
                    documents.append(text)
                    
                    # Prepare metadata (ChromaDB doesn't support nested objects or None values)
                    chunk_metadata = {
                        'doc_id': metadata.get('doc_id', doc_id) or doc_id,
                        'doctype': metadata.get('doctype') or 'general',
                        'page_number': metadata.get('page') or 0,
                        'heading': metadata.get('heading') or "",
                        'section': metadata.get('section') or "",
                        'chunk_length': len(text),
                        'word_count': len(text.split()),
                        'created_at': metadata.get('created_at') or datetime.now().isoformat(),
                        'source_file': metadata.get('source_file') or '',
                        'content_type': metadata.get('content_type') or 'text'
                    }
                else:
                    # DocumentChunk object format
                    # Ensure chunk has embedding
                    if 'embedding' not in chunk.metadata:
                        raise ValueError(f"Chunk {chunk.chunk_id} missing embedding")
                    
                    ids.append(chunk.chunk_id)
                    embeddings.append(chunk.metadata['embedding'])
                    documents.append(chunk.content)
                    
                    # Prepare metadata (ChromaDB doesn't support nested objects or None values)
                    chunk_metadata = {
                        'doc_id': chunk.doc_id or doc_id,
                        'doctype': chunk.doctype or 'general',
                        'page_number': chunk.page_number or 0,
                        'heading': chunk.heading or "",
                        'section': chunk.section or "",
                        'chunk_length': len(chunk.content),
                        'word_count': len(chunk.content.split()),
                        'created_at': chunk.metadata.get('created_at') or datetime.now().isoformat(),
                        'source_file': chunk.metadata.get('source_file') or '',
                        'content_type': chunk.metadata.get('content_type') or 'text'
                    }
                
                metadatas.append(chunk_metadata)
            
            # Validate we have data to store
            if not ids:
                print(f"⚠️  No valid chunks to store for document {doc_id}")
                return
            
            # Store in ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"✅ Stored {len(chunks)} chunks for document {doc_id}")
            
        except Exception as e:
            print(f"❌ Failed to store chunks: {str(e)}")
            raise Exception(f"Vector store error: {str(e)}")
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            if not self.collection:
                await self.initialize()
            
            # Build where clause for filtering
            where_clause = {}
            if filters:
                if 'doctype' in filters:
                    where_clause['doctype'] = filters['doctype']
                if 'doc_id' in filters:
                    where_clause['doc_id'] = filters['doc_id']
                if 'content_type' in filters:
                    where_clause['content_type'] = filters['content_type']
            
            # Query ChromaDB
            query_params = {
                'query_embeddings': [query_embedding],
                'n_results': min(top_k, 100),  # ChromaDB limit
                'include': ['documents', 'metadatas', 'distances']
            }
            
            if where_clause:
                query_params['where'] = where_clause
            
            results = self.collection.query(**query_params)
            
            # Format results with improved similarity calculation
            similar_chunks = []
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                
                # Improved similarity calculation for ChromaDB cosine distance
                # ChromaDB returns squared cosine distance, so we need to adjust
                if distance >= 0:
                    similarity_score = max(0.0, 1.0 - distance)
                else:
                    # Handle negative distances (shouldn't happen with cosine but just in case)
                    similarity_score = 1.0
                
                chunk_data = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': similarity_score,
                    'distance': distance
                }
                
                # Only print debug for top 3 results to reduce noise
                if i < 3:
                    print(f"🔍 Chunk {i+1}: {chunk_data['id'][:30]}... (score: {similarity_score:.3f}, dist: {distance:.3f})")
                
                similar_chunks.append(chunk_data)
            
            # Improved adaptive threshold with performance optimization
            base_threshold = 0.05  # Lower threshold for better recall
            adaptive_threshold = max(base_threshold, settings.SIMILARITY_THRESHOLD * 0.7)
            
            # Smart filtering: ensure we get meaningful results
            if similar_chunks:
                # Take top results that meet threshold OR top 3 regardless of threshold
                filtered_chunks = []
                high_quality = [c for c in similar_chunks if c['similarity_score'] >= adaptive_threshold]
                
                if high_quality:
                    filtered_chunks = high_quality
                else:
                    # Take top 3 even if below threshold (for better UX)
                    filtered_chunks = similar_chunks[:3]
                    print(f"🔍 Using top {len(filtered_chunks)} chunks (below threshold but best available)")
            else:
                filtered_chunks = []
            
            print(f"✅ Returning {len(filtered_chunks)} relevant chunks (from {len(similar_chunks)} total)")
            
            return filtered_chunks[:top_k]
            
        except Exception as e:
            print(f"❌ Vector search failed: {str(e)}")
            raise Exception(f"Vector search error: {str(e)}")
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for search_similar - for use in LangGraph nodes
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar chunks with metadata
        """
        import asyncio
        try:
            # Get current event loop or create new one
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to use a different approach
                import concurrent.futures
                
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self.search_similar(query_embedding, top_k, filters)
                        )
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=30)  # 30 second timeout
            else:
                # No event loop running, we can run directly
                return loop.run_until_complete(self.search_similar(query_embedding, top_k, filters))
        except Exception as e:
            print(f"❌ Sync vector search failed: {str(e)}")
            # Fallback: return empty results
            return []
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all documents in vector store
        
        Returns:
            List of document metadata
        """
        try:
            if not self.collection:
                await self.initialize()
            
            # Get all documents
            results = self.collection.get(include=['metadatas'])
            
            # Group by document ID
            documents = {}
            for metadata in results['metadatas']:
                doc_id = metadata['doc_id']
                if doc_id not in documents:
                    documents[doc_id] = {
                        'id': doc_id,
                        'filename': metadata.get('source_file', ''),
                        'doctype': metadata['doctype'],
                        'upload_date': metadata.get('created_at', ''),
                        'size_bytes': 0,  # Will be estimated
                        'chunk_count': 0,
                        'status': 'processed'
                    }
                
                documents[doc_id]['chunk_count'] += 1
                # Estimate file size from word count (rough estimate)
                word_count = metadata.get('word_count', 0)
                documents[doc_id]['size_bytes'] += word_count * 6  # ~6 bytes per word
            
            return list(documents.values())
            
        except Exception as e:
            print(f"❌ Failed to get documents: {str(e)}")
            raise Exception(f"Document listing error: {str(e)}")
    
    async def delete_document(self, doc_id: str):
        """
        Delete all chunks for a specific document
        
        Args:
            doc_id: Document identifier to delete
        """
        try:
            if not self.collection:
                await self.initialize()
            
            # Find all chunks for this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results['ids']:
                # Delete chunks by their IDs
                self.collection.delete(ids=results['ids'])
                print(f"✅ Deleted {len(results['ids'])} chunks for document {doc_id}")
            else:
                print(f"⚠️  No chunks found for document {doc_id}")
            
        except Exception as e:
            print(f"❌ Failed to delete document {doc_id}: {str(e)}")
            raise Exception(f"Document deletion error: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Statistics about the vector store
        """
        try:
            if not self.collection:
                await self.initialize()
            
            # Get collection info
            total_chunks = self.collection.count()
            
            # Get document count
            results = self.collection.get(include=['metadatas'])
            unique_docs = set(metadata['doc_id'] for metadata in results['metadatas'])
            
            # Doctype distribution
            doctype_counts = {}
            for metadata in results['metadatas']:
                doctype = metadata.get('doctype', 'unknown')
                doctype_counts[doctype] = doctype_counts.get(doctype, 0) + 1
            
            return {
                'total_chunks': total_chunks,
                'total_documents': len(unique_docs),
                'doctype_distribution': doctype_counts,
                'collection_name': self.collection_name,
                'storage_path': str(settings.CHROMA_PATH)
            }
            
        except Exception as e:
            print(f"❌ Failed to get stats: {str(e)}")
            raise Exception(f"Stats error: {str(e)}")
    
    async def reset_collection(self):
        """Reset/clear the entire collection"""
        try:
            if self.collection:
                self.chroma_client.delete_collection(self.collection_name)
                print(f"✅ Collection {self.collection_name} deleted")
            
            # Recreate collection
            await self.initialize()
            
        except Exception as e:
            print(f"❌ Failed to reset collection: {str(e)}")
            raise Exception(f"Collection reset error: {str(e)}")