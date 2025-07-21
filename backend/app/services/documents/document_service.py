"""
Document Service - Enterprise Implementation
Central service for document management in the chat system
"""
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import UploadFile

from ...infrastructure.vectordb.chromadb_client import ChromaDBClient
from ..file_manager import file_manager

logger = logging.getLogger(__name__)

class DocumentService:
    """
    Enterprise Document Service for chat context management
    """
    
    def __init__(self):
        self.chromadb_client = ChromaDBClient()
        self.upload_dir = Path("./data/chat_documents")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_documents(
        self,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get all documents with pagination"""
        try:
            # Get documents from training_files table
            result = await db.execute(
                text("""
                    SELECT 
                        id, filename, file_path, file_size, 
                        upload_date, chunk_count, status
                    FROM training_files
                    WHERE status IN ('indexed', 'ready')
                    ORDER BY upload_date DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"limit": limit, "offset": offset}
            )
            
            documents = []
            total_chunks = 0
            
            for row in result:
                documents.append({
                    "id": str(row.id),
                    "filename": row.filename,
                    "source_path": row.file_path,
                    "chunks": row.chunk_count or 0,
                    "total_size": row.file_size or 0,
                    "upload_date": str(row.upload_date) if row.upload_date else "",
                    "status": row.status
                })
                total_chunks += row.chunk_count or 0
            
            # Get total count
            count_result = await db.execute(
                text("SELECT COUNT(*) as count FROM training_files WHERE status IN ('indexed', 'ready')")
            )
            total_count = count_result.scalar() or 0
            
            return {
                "documents": documents,
                "total_count": total_count,
                "total_chunks": total_chunks
            }
            
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            raise
    
    async def get_document_details(
        self,
        document_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a document"""
        try:
            result = await db.execute(
                text("""
                    SELECT 
                        id, filename, file_path, file_size,
                        chunk_count, status, upload_date
                    FROM training_files
                    WHERE id = :id
                """),
                {"id": document_id}
            )
            
            row = result.first()
            if not row:
                return None
            
            # Read file preview
            preview = ""
            if row.file_path and os.path.exists(row.file_path):
                try:
                    with open(row.file_path, 'r', encoding='utf-8') as f:
                        preview = f.read(500)  # First 500 chars
                except Exception as e:
                    logger.warning(f"Could not read file preview: {e}")
            
            return {
                "id": str(row.id),
                "filename": row.filename,
                "chunks": row.chunk_count or 0,
                "preview": preview,
                "metadata": {
                    "file_size": row.file_size,
                    "upload_date": str(row.upload_date) if row.upload_date else "",
                    "status": row.status,
                    "file_path": row.file_path
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get document details: {e}")
            raise
    
    async def delete_document(
        self,
        document_id: str,
        db: AsyncSession
    ) -> bool:
        """Delete a document and its chunks from ChromaDB"""
        try:
            # Get document info
            result = await db.execute(
                text("SELECT file_path FROM training_files WHERE id = :id"),
                {"id": document_id}
            )
            row = result.first()
            
            if not row:
                return False
            
            # Delete from ChromaDB
            await self.chromadb_client.delete_documents(
                filter_metadata={"file_id": document_id}
            )
            
            # Delete from database
            await db.execute(
                text("DELETE FROM training_files WHERE id = :id"),
                {"id": document_id}
            )
            
            # Delete physical file
            if row.file_path and os.path.exists(row.file_path):
                try:
                    os.remove(row.file_path)
                except Exception as e:
                    logger.warning(f"Could not delete file: {e}")
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete document: {e}")
            raise
    
    async def search_documents(
        self,
        query: str,
        top_k: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Search documents using vector similarity"""
        try:
            results = await self.chromadb_client.search(
                query=query,
                top_k=top_k
            )
            return results
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            raise
    
    async def upload_documents(
        self,
        files: List[UploadFile],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Upload multiple documents for chat context"""
        try:
            uploaded_count = 0
            chunks_created = 0
            
            for file in files:
                # Use existing file manager for consistency
                result = await file_manager.upload_file(
                    file=file,
                    category_slug="qa_docs",  # Default category for chat docs
                    folder_id=None,
                    db=db
                )
                
                if result:
                    uploaded_count += 1
                    # The file will be indexed by background indexer
            
            return {
                "message": f"Successfully uploaded {uploaded_count} documents",
                "documents_added": uploaded_count,
                "chunks_created": chunks_created  # Will be updated after indexing
            }
            
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            raise
    
    async def get_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get document statistics"""
        try:
            # Get ChromaDB stats
            chromadb_stats = await self.chromadb_client.get_collection_stats()
            
            # Get database stats
            result = await db.execute(
                text("""
                    SELECT 
                        COUNT(*) as total_files,
                        SUM(chunk_count) as total_chunks,
                        SUM(file_size) as total_size
                    FROM training_files
                    WHERE status = 'indexed'
                """)
            )
            db_stats = result.first()
            
            return {
                "database": {
                    "total_files": db_stats.total_files or 0,
                    "total_chunks": db_stats.total_chunks or 0,
                    "total_size_mb": round((db_stats.total_size or 0) / 1024 / 1024, 2)
                },
                "vector_store": chromadb_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise

# Singleton instance
document_service = DocumentService()