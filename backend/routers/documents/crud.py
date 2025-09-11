"""
Document CRUD Operations Router
Basic document lifecycle operations: upload, get, update, delete, download
"""

import logging
import time
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from schemas.core import (
    DocumentUpdate, DocumentResponse, DocumentWithFolder,
    DocumentFilter, DocumentSort, UploadResponse
)
from services.document_service import DocumentService
from routers.websockets import connection_manager

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

logger = logging.getLogger(__name__)

# Create sub-router for CRUD operations
router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    folder_id: UUID = Query(..., description="Target folder ID"),
    job_id: Optional[str] = Query(None, description="Job ID for progress tracking"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    description: Optional[str] = Query(None, description="Document description"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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


# Add OPTIONS and HEAD handlers for CORS and availability checks
@router.options("/{document_id}/pdf")
async def pdf_options(document_id: UUID):
    """Handle CORS preflight requests for PDF endpoint"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )

@router.head("/{document_id}/pdf")
async def pdf_head(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """Handle HEAD requests for PDF availability checks"""
    try:
        file_info = await doc_service.get_document_file(db, document_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path, filename, mime_type = file_info
        
        # Only serve PDFs through this endpoint
        if not mime_type or not mime_type.lower() == 'application/pdf':
            raise HTTPException(status_code=400, detail="Document is not a PDF")
        
        # Return headers without body for HEAD request
        return Response(
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f"inline; filename=\"{filename}\"",
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "ALLOWALL"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check PDF {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check PDF: {str(e)}")

@router.get("/{document_id}/pdf")
async def serve_pdf(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Dedicated PDF serving endpoint with proper PDF headers
    
    - **document_id**: Document UUID
    - Returns PDF with optimized headers for modern PDF viewers and iframe embedding
    """
    try:
        file_info = await doc_service.get_document_file(db, document_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path, filename, mime_type = file_info
        
        # Only serve PDFs through this endpoint
        if not mime_type or not mime_type.lower() == 'application/pdf':
            raise HTTPException(status_code=400, detail="Document is not a PDF")
        
        # Create optimized PDF response for iframe embedding
        response = FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            headers={
                # Essential for iframe embedding
                "Content-Disposition": "inline; filename=\"" + filename + "\"",
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                
                # CORS headers for cross-origin iframe requests
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Expose-Headers": "Content-Length, Content-Range",
                
                # Security headers that allow iframe embedding from localhost
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "ALLOWALL",
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve PDF {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve PDF: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    inline: bool = Query(False, description="Display inline instead of download"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
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
        
        # Simple file download - no complex logic
        if inline:
            # For inline display
            response = FileResponse(
                path=str(file_path),
                media_type=mime_type,
            )
        else:
            # For download
            response = FileResponse(
                path=str(file_path),
                filename=filename,
                media_type=mime_type
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")