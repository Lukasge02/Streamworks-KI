"""
Document Management API Router
Enterprise-grade REST API for document operations
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from schemas.core import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentWithFolder,
    DocumentFilter, DocumentSort, BulkDeleteRequest, BulkDeleteResponse,
    BulkMoveRequest, BulkMoveResponse, BulkReprocessRequest, UploadResponse
)
from services.document_service import DocumentService
from services.document_chunk_service import DocumentChunkService
from routers.websockets import connection_manager

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
doc_service = DocumentService()
chunk_service = DocumentChunkService()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    folder_id: UUID = Query(..., description="Target folder ID"),
    job_id: Optional[str] = Query(None, description="Job ID for progress tracking"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    description: Optional[str] = Query(None, description="Document description"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Upload a document to a folder with optional progress tracking
    
    - **file**: Document file to upload
    - **folder_id**: Target folder UUID
    - **job_id**: Optional job ID for WebSocket progress tracking
    - **tags**: Optional comma-separated tags
    - **description**: Optional document description
    """
    try:
        import time
        start_time = time.time()
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Upload document with optional progress tracking
        document = await doc_service.upload_document(
            db=db,
            file=file,
            folder_id=folder_id,
            job_id=job_id,
            tags=tag_list,
            description=description
        )
        
        # Send completion notification via WebSocket if job_id provided
        if job_id and document:
            try:
                # Handle both Enum and string status values
                status_value = document.status.value if hasattr(document.status, 'value') else document.status
                success = status_value in ['ready', 'skipped']
                await connection_manager.send_job_completion(
                    job_id=job_id,
                    success=success,
                    document_id=str(document.id),
                    error=document.error_message
                )
            except Exception as ws_error:
                # Don't fail upload if WebSocket notification fails
                logger.warning(f"Failed to send WebSocket completion for job {job_id}: {str(ws_error)}")
        
        upload_time = time.time() - start_time
        
        response = UploadResponse(
            document=DocumentResponse(
                id=document.id,
                filename=document.filename,
                original_filename=document.original_filename,
                folder_id=document.folder_id,
                file_hash=document.file_hash,
                file_size=document.file_size,
                mime_type=document.mime_type,
                status=document.status,
                error_message=document.error_message,
                created_at=document.created_at,
                updated_at=document.updated_at,
                processed_at=document.processed_at,
                tags=document.tags,
                description=document.description
            ),
            message=f"Document uploaded successfully. Processing status: {document.status.value if hasattr(document.status, 'value') else document.status}",
            upload_time=round(upload_time, 2),
            processing_info={
                "chunk_count": document.chunk_count,
                "status": document.status.value if hasattr(document.status, 'value') else document.status,
                "processing_metadata": document.processing_metadata,
                "job_id": job_id  # Include job_id in response for client reference
            }
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[DocumentWithFolder])
async def get_documents(
    folder_id: Optional[UUID] = Query(None, description="Filter by folder ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in filename and description"),
    tags: Optional[str] = Query(None, description="Filter by comma-separated tags"),
    sort: DocumentSort = Query(DocumentSort.CREATED_DESC, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get list of documents with filtering and sorting
    
    - **folder_id**: Filter by folder UUID
    - **status**: Filter by document status
    - **search**: Search query for filename and description
    - **tags**: Comma-separated tags to filter by
    - **sort**: Sort order (created_desc, created_asc, name_asc, name_desc, size_asc, size_desc)
    - **page**: Page number (1-based)
    - **per_page**: Items per page (1-200)
    """
    try:
        # Build filters
        filters = DocumentFilter()
        if folder_id:
            filters.folder_id = folder_id
        if status:
            filters.status = status
        if search:
            filters.search_query = search
        if tags:
            filters.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        documents = await doc_service.get_documents_list(
            db=db,
            folder_id=folder_id,
            filters=filters,
            sort=sort,
            page=page,
            per_page=per_page
        )
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")


@router.get("/folder/{folder_id}", response_model=List[DocumentWithFolder])
async def get_documents_by_folder(
    folder_id: UUID,
    sort: DocumentSort = Query(DocumentSort.CREATED_DESC, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all documents in a specific folder
    
    - **folder_id**: Folder UUID
    - **sort**: Sort order
    - **page**: Page number
    - **per_page**: Items per page
    """
    try:
        documents = await doc_service.get_documents_list(
            db=db,
            folder_id=folder_id,
            sort=sort,
            page=page,
            per_page=per_page
        )
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentWithFolder)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get document by ID
    
    - **document_id**: Document UUID
    """
    try:
        document = await doc_service.get_document_by_id(db, document_id, include_folder=True)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        folder_info = None
        if document.folder:
            folder_info = {
                "id": document.folder.id,
                "name": document.folder.name,
                "path": document.folder.path,
                "created_at": document.folder.created_at,
                "updated_at": document.folder.updated_at
            }
        
        return DocumentWithFolder(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            folder_id=document.folder_id,
            file_hash=document.file_hash,
            file_size=document.file_size,
            mime_type=document.mime_type,
            status=document.status,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
            processed_at=document.processed_at,
            tags=document.tags,
            description=document.description,
            folder=folder_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update document metadata
    
    - **document_id**: Document UUID
    - **filename**: New filename (optional)
    - **folder_id**: New folder ID (optional)
    - **tags**: New tags list (optional)
    - **description**: New description (optional)
    """
    try:
        document = await doc_service.update_document(db, document_id, update_data)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            folder_id=document.folder_id,
            file_hash=document.file_hash,
            file_size=document.file_size,
            mime_type=document.mime_type,
            status=document.status,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
            processed_at=document.processed_at,
            tags=document.tags,
            description=document.description
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete document
    
    - **document_id**: Document UUID
    """
    try:
        success = await doc_service.delete_document(db, document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    inline: bool = Query(False, description="Display inline instead of download"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Download or view document file
    
    - **document_id**: Document UUID
    - **inline**: If true, display inline (for PDF viewer), if false, force download
    """
    try:
        file_info = await doc_service.get_document_file(db, document_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="Document or file not found")
        
        file_path, filename, mime_type = file_info
        
        if inline:
            # For inline display (PDF viewer) - don't force download
            return FileResponse(
                path=str(file_path),
                media_type=mime_type,
                # No filename parameter = Content-Disposition: inline
            )
        else:
            # For download - force download with filename
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type=mime_type
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_documents(
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete multiple documents in batch
    
    - **document_ids**: List of document UUIDs to delete
    """
    try:
        result = await doc_service.bulk_delete_documents(db, request.document_ids)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")


@router.post("/bulk-move", response_model=BulkMoveResponse)
async def bulk_move_documents(
    request: BulkMoveRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Move multiple documents to a target folder
    
    - **document_ids**: List of document UUIDs to move
    - **target_folder_id**: Target folder UUID
    """
    try:
        result = await doc_service.bulk_move_documents(
            db, request.document_ids, request.target_folder_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk move failed: {str(e)}")


@router.post("/bulk-reprocess")
async def bulk_reprocess_documents(
    request: BulkReprocessRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Reprocess multiple documents with Docling/OCR
    
    - **document_ids**: List of document UUIDs to reprocess
    """
    try:
        reprocessed = []
        failed = []
        
        for document_id in request.document_ids:
            try:
                document = await doc_service.reprocess_document(db, document_id)
                if document:
                    reprocessed.append(str(document_id))
                else:
                    failed.append({
                        "id": str(document_id),
                        "error": "Document not found"
                    })
            except Exception as e:
                failed.append({
                    "id": str(document_id),
                    "error": str(e)
                })
        
        return {
            "reprocessed": reprocessed,
            "failed": failed,
            "total_requested": len(request.document_ids),
            "total_reprocessed": len(reprocessed),
            "total_failed": len(failed)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk reprocess failed: {str(e)}")


@router.get("/stats/overview")
async def get_document_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get overall document statistics
    """
    try:
        from sqlalchemy import select, func
        from models.core import Document
        
        # Basic document stats
        stats_query = select(
            func.count(Document.id).label('total_documents'),
            func.sum(Document.file_size).label('total_size_bytes'),
            func.avg(Document.file_size).label('average_size_bytes')
        )
        
        stats_result = await db.execute(stats_query)
        stats = stats_result.one()
        
        return {
            "total_documents": stats.total_documents or 0,
            "total_size_bytes": stats.total_size_bytes or 0,
            "average_size_bytes": float(stats.average_size_bytes or 0),
            "timestamp": "2025-09-05T21:28:00Z"  # Current timestamp would be dynamic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# Chunk Management Endpoints

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    chunk_type: Optional[str] = Query(None, description="Filter by chunk type (text, table, image, code)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get chunks for a specific document
    
    - **document_id**: Document UUID
    - **chunk_type**: Filter by chunk type
    - **page**: Page number (1-based)
    - **per_page**: Items per page (1-200)
    """
    try:
        from models.core import ChunkType
        
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Validate chunk_type if provided
        chunk_type_enum = None
        if chunk_type:
            try:
                chunk_type_enum = ChunkType(chunk_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid chunk_type. Must be one of: {[t.value for t in ChunkType]}"
                )
        
        chunks = await chunk_service.get_document_chunks(
            db=db,
            document_id=document_id,
            chunk_type=chunk_type_enum,
            page=page,
            per_page=per_page
        )
        
        # Convert to response format
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "content_preview": chunk.content_preview,
                "heading": chunk.heading,
                "section_name": chunk.section_name,
                "page_number": chunk.page_number,
                "chunk_type": chunk.chunk_type.value,
                "metadata": chunk.chunk_metadata,
                "word_count": chunk.word_count,
                "char_count": chunk.char_count,
                "created_at": chunk.created_at,
                "updated_at": chunk.updated_at
            })
        
        return {
            "chunks": chunk_responses,
            "total_chunks": len(chunk_responses),
            "page": page,
            "per_page": per_page,
            "document_id": str(document_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


@router.get("/{document_id}/processing-status")
async def get_document_processing_status(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get document processing status and metadata
    
    - **document_id**: Document UUID
    """
    try:
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status.value if hasattr(document.status, 'value') else document.status,
            "chunk_count": document.chunk_count,
            "processing_metadata": document.processing_metadata,
            "processed_at": document.processed_at,
            "error_message": document.error_message,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}")


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Reprocess document with Docling (useful for fixing failed processing)
    
    - **document_id**: Document UUID
    """
    try:
        document = await doc_service.reprocess_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": f"Document reprocessing initiated",
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status.value if hasattr(document.status, 'value') else document.status,
            "chunk_count": document.chunk_count,
            "processing_metadata": document.processing_metadata
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reprocess document: {str(e)}")


@router.get("/{document_id}/chunks/{chunk_id}")
async def get_document_chunk(
    document_id: UUID,
    chunk_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get specific chunk by ID
    
    - **document_id**: Document UUID
    - **chunk_id**: Chunk UUID
    """
    try:
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        chunk = await chunk_service.get_chunk_by_id(db, chunk_id, include_document=True)
        if not chunk or chunk.document_id != document_id:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "heading": chunk.heading,
            "section_name": chunk.section_name,
            "page_number": chunk.page_number,
            "chunk_type": chunk.chunk_type.value,
            "metadata": chunk.chunk_metadata,
            "word_count": chunk.word_count,
            "char_count": chunk.char_count,
            "created_at": chunk.created_at,
            "updated_at": chunk.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunk: {str(e)}")


@router.get("/{document_id}/chunks/analytics")
async def get_document_chunk_analytics(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get chunk analytics for a document
    
    - **document_id**: Document UUID
    """
    try:
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analytics = await chunk_service.get_chunk_analytics(db, document_id)
        
        return {
            "document_id": str(document_id),
            "filename": document.filename,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunk analytics: {str(e)}")


@router.get("/chunks/search")
async def search_chunks(
    query: str = Query(..., description="Search query"),
    document_id: Optional[UUID] = Query(None, description="Filter by document"),
    chunk_type: Optional[str] = Query(None, description="Filter by chunk type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Search chunks by content
    
    - **query**: Search query
    - **document_id**: Filter by document (optional)
    - **chunk_type**: Filter by chunk type (optional)
    - **limit**: Maximum results (1-100)
    """
    try:
        from models.core import ChunkType
        
        # Validate chunk_type if provided
        chunk_type_enum = None
        if chunk_type:
            try:
                chunk_type_enum = ChunkType(chunk_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid chunk_type. Must be one of: {[t.value for t in ChunkType]}"
                )
        
        chunks = await chunk_service.search_chunks(
            db=db,
            query=query,
            document_id=document_id,
            chunk_type=chunk_type_enum,
            limit=limit
        )
        
        # Convert to response format
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content_preview": chunk.content_preview,
                "heading": chunk.heading,
                "section_name": chunk.section_name,
                "page_number": chunk.page_number,
                "chunk_type": chunk.chunk_type.value,
                "word_count": chunk.word_count,
                "char_count": chunk.char_count,
                "created_at": chunk.created_at
            })
        
        return {
            "query": query,
            "results": chunk_responses,
            "total_results": len(chunk_responses),
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search chunks: {str(e)}")