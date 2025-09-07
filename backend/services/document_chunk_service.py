"""
Document Chunk Service
Enterprise-grade CRUD operations for document chunks with batch processing
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete, func, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.core import DocumentChunk, Document, ChunkType
from services.docling_ingest import DoclingIngestService, DocumentChunk as DoclingChunk

logger = logging.getLogger(__name__)


class DocumentChunkService:
    """
    Service for document chunk CRUD operations
    Handles batch processing, analytics, and cleanup
    """
    
    def __init__(self):
        self.docling_service = DoclingIngestService()

    async def create_chunks_from_docling(
        self,
        db: AsyncSession,
        document_id: UUID,
        docling_chunks: List[DoclingChunk]
    ) -> List[DocumentChunk]:
        """
        Convert Docling chunks to database records
        
        Args:
            db: Database session
            document_id: Document UUID
            docling_chunks: List of Docling chunk objects
            
        Returns:
            List of created DocumentChunk records
        """
        try:
            db_chunks = []
            
            for i, docling_chunk in enumerate(docling_chunks):
                # Determine chunk type
                chunk_type = ChunkType.TEXT
                if docling_chunk.metadata.get("content_type") == "table":
                    chunk_type = ChunkType.TABLE
                elif docling_chunk.metadata.get("content_type") == "image":
                    chunk_type = ChunkType.IMAGE
                elif docling_chunk.metadata.get("content_type") == "code":
                    chunk_type = ChunkType.CODE
                
                # Calculate analytics
                word_count = len(docling_chunk.content.split()) if docling_chunk.content else 0
                char_count = len(docling_chunk.content) if docling_chunk.content else 0
                
                # Create database chunk
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    content=docling_chunk.content,
                    heading=docling_chunk.heading,
                    section_name=docling_chunk.section,
                    page_number=docling_chunk.page_number,
                    chunk_type=chunk_type,
                    chunk_metadata=docling_chunk.metadata,
                    word_count=word_count,
                    char_count=char_count
                )
                
                db_chunks.append(db_chunk)
            
            # Batch insert for performance
            db.add_all(db_chunks)
            await db.flush()
            
            # Refresh all chunks to get IDs
            for chunk in db_chunks:
                await db.refresh(chunk)
            
            logger.info(f"Created {len(db_chunks)} chunks for document {document_id}")
            return db_chunks
            
        except Exception as e:
            logger.error(f"Failed to create chunks for document {document_id}: {str(e)}")
            await db.rollback()
            raise

    async def get_document_chunks(
        self,
        db: AsyncSession,
        document_id: UUID,
        chunk_type: Optional[ChunkType] = None,
        page: int = 1,
        per_page: int = 50
    ) -> List[DocumentChunk]:
        """
        Get chunks for a document with filtering and pagination
        
        Args:
            db: Database session
            document_id: Document UUID
            chunk_type: Filter by chunk type
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            List of document chunks
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            
            if chunk_type:
                query = query.where(DocumentChunk.chunk_type == chunk_type)
            
            # Order by chunk_index for proper sequence
            query = query.order_by(asc(DocumentChunk.chunk_index))
            
            # Apply pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            result = await db.execute(query)
            chunks = result.scalars().all()
            
            return list(chunks)
            
        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {str(e)}")
            return []

    async def get_chunk_by_id(
        self,
        db: AsyncSession,
        chunk_id: UUID,
        include_document: bool = False
    ) -> Optional[DocumentChunk]:
        """
        Get chunk by ID with optional document info
        
        Args:
            db: Database session
            chunk_id: Chunk UUID
            include_document: Include document relationship
            
        Returns:
            DocumentChunk or None if not found
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            
            if include_document:
                query = query.options(selectinload(DocumentChunk.document))
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {str(e)}")
            return None

    async def update_chunk(
        self,
        db: AsyncSession,
        chunk_id: UUID,
        content: Optional[str] = None,
        heading: Optional[str] = None,
        section_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[DocumentChunk]:
        """
        Update chunk metadata
        
        Args:
            db: Database session
            chunk_id: Chunk UUID
            content: New content
            heading: New heading
            section_name: New section name
            metadata: Updated metadata
            
        Returns:
            Updated chunk or None if not found
        """
        try:
            chunk = await self.get_chunk_by_id(db, chunk_id)
            if not chunk:
                return None
            
            # Update fields
            if content is not None:
                chunk.content = content
                chunk.word_count = len(content.split())
                chunk.char_count = len(content)
            
            if heading is not None:
                chunk.heading = heading
                
            if section_name is not None:
                chunk.section_name = section_name
                
            if metadata is not None:
                # Merge metadata instead of replacing
                chunk.chunk_metadata = {**chunk.chunk_metadata, **metadata}
            
            chunk.updated_at = datetime.utcnow()
            
            await db.flush()
            await db.refresh(chunk)
            
            logger.info(f"Updated chunk: {chunk_id}")
            return chunk
            
        except Exception as e:
            logger.error(f"Failed to update chunk {chunk_id}: {str(e)}")
            await db.rollback()
            raise

    async def delete_chunks_by_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> int:
        """
        Delete all chunks for a document
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Number of deleted chunks
        """
        try:
            # Count chunks before deletion
            count_query = select(func.count(DocumentChunk.id)).where(
                DocumentChunk.document_id == document_id
            )
            count_result = await db.execute(count_query)
            chunk_count = count_result.scalar() or 0
            
            # Delete chunks
            delete_query = delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
            await db.execute(delete_query)
            await db.flush()
            
            logger.info(f"Deleted {chunk_count} chunks for document {document_id}")
            return chunk_count
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {str(e)}")
            await db.rollback()
            raise

    async def get_chunk_analytics(
        self,
        db: AsyncSession,
        document_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get chunk analytics for a document or globally
        
        Args:
            db: Database session
            document_id: Document UUID (optional, for global stats)
            
        Returns:
            Analytics dictionary
        """
        try:
            base_query = select(
                func.count(DocumentChunk.id).label('total_chunks'),
                func.sum(DocumentChunk.word_count).label('total_words'),
                func.sum(DocumentChunk.char_count).label('total_chars'),
                func.avg(DocumentChunk.word_count).label('avg_words'),
                func.avg(DocumentChunk.char_count).label('avg_chars')
            )
            
            if document_id:
                base_query = base_query.where(DocumentChunk.document_id == document_id)
            
            result = await db.execute(base_query)
            stats = result.one()
            
            # Get chunk type distribution
            type_query = select(
                DocumentChunk.chunk_type,
                func.count(DocumentChunk.id).label('count')
            )
            
            if document_id:
                type_query = type_query.where(DocumentChunk.document_id == document_id)
            
            type_query = type_query.group_by(DocumentChunk.chunk_type)
            type_result = await db.execute(type_query)
            type_distribution = {row.chunk_type.value: row.count for row in type_result}
            
            return {
                "total_chunks": stats.total_chunks or 0,
                "total_words": stats.total_words or 0,
                "total_chars": stats.total_chars or 0,
                "average_words": float(stats.avg_words or 0),
                "average_chars": float(stats.avg_chars or 0),
                "type_distribution": type_distribution,
                "document_id": str(document_id) if document_id else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get chunk analytics: {str(e)}")
            return {}

    async def search_chunks(
        self,
        db: AsyncSession,
        query: str,
        document_id: Optional[UUID] = None,
        chunk_type: Optional[ChunkType] = None,
        limit: int = 20
    ) -> List[DocumentChunk]:
        """
        Search chunks by content
        
        Args:
            db: Database session
            query: Search query
            document_id: Filter by document
            chunk_type: Filter by chunk type
            limit: Maximum results
            
        Returns:
            List of matching chunks
        """
        try:
            search_query = select(DocumentChunk).where(
                DocumentChunk.content.ilike(f"%{query}%")
            )
            
            if document_id:
                search_query = search_query.where(DocumentChunk.document_id == document_id)
                
            if chunk_type:
                search_query = search_query.where(DocumentChunk.chunk_type == chunk_type)
            
            # Order by relevance (could be enhanced with full-text search)
            search_query = search_query.order_by(desc(DocumentChunk.created_at))
            search_query = search_query.limit(limit)
            
            result = await db.execute(search_query)
            chunks = result.scalars().all()
            
            return list(chunks)
            
        except Exception as e:
            logger.error(f"Failed to search chunks: {str(e)}")
            return []

    async def cleanup_orphaned_chunks(
        self,
        db: AsyncSession
    ) -> int:
        """
        Clean up chunks without valid document references
        
        Args:
            db: Database session
            
        Returns:
            Number of cleaned chunks
        """
        try:
            # Find chunks with invalid document references
            orphan_query = select(DocumentChunk).where(
                ~DocumentChunk.document_id.in_(
                    select(Document.id)
                )
            )
            
            result = await db.execute(orphan_query)
            orphaned_chunks = result.scalars().all()
            
            if not orphaned_chunks:
                return 0
            
            # Delete orphaned chunks
            orphan_ids = [chunk.id for chunk in orphaned_chunks]
            delete_query = delete(DocumentChunk).where(
                DocumentChunk.id.in_(orphan_ids)
            )
            await db.execute(delete_query)
            await db.flush()
            
            logger.info(f"Cleaned up {len(orphaned_chunks)} orphaned chunks")
            return len(orphaned_chunks)
            
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned chunks: {str(e)}")
            await db.rollback()
            raise