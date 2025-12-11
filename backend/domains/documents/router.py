"""
Documents API Router v3
REST endpoints with original file download support
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from typing import List, Optional
from pydantic import BaseModel
import traceback


router = APIRouter(prefix="/api/documents", tags=["Documents"])


# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    doc_type: Optional[str] = None


class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None
    num_chunks: int = 5


class ChatResponseModel(BaseModel):
    answer: str
    sources: List[dict]
    has_context: bool
    chunks_found: int


class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    doc_type: str
    chunks: int
    created_at: str
    has_original: bool = True
    metadata: dict


class SearchResult(BaseModel):
    doc_id: str
    content: str
    filename: str
    score: float
    metadata: dict


# Lazy imports
def get_document_service():
    from services.rag.document_service import document_service
    return document_service


def get_vector_store():
    from services.rag.vector_store import vector_store
    return vector_store


@router.get("/health")
async def health_check():
    """Check RAG system health and supported types"""
    try:
        doc_service = get_document_service()
        stats = doc_service.get_stats()
        return {
            "status": "healthy",
            "qdrant": stats,
            "supported_types": doc_service.get_supported_types(),
            "stored_files": stats.get("stored_files", 0),
            "message": "RAG system operational"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "RAG system unavailable"
            }
        )


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported file types"""
    try:
        doc_service = get_document_service()
        return {
            "types": doc_service.get_supported_types(),
            "description": {
                "pdf": "PDF documents (via PyMuPDF - fast text extraction)",
                "docx": "Microsoft Word documents (via Docling AI)",
                "pptx": "Microsoft PowerPoint (via Docling AI)",
                "xml": "XML files with Streamworks metadata extraction",
                "txt": "Plain text files",
                "md": "Markdown files",
                "json": "JSON documents",
                "html": "HTML pages (via Docling AI)",
                "image": "Images (PNG, JPG) with OCR via Docling"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/originals/list")
async def list_original_files():
    """
    List all stored original files with their doc_ids
    """
    try:
        from services.rag.storage.file_storage import file_storage
        files = file_storage.list_files()
        
        # Parse doc_ids from filenames
        originals = []
        for f in files:
            filename = f["filename"]
            # Format is: {doc_id}.{ext}
            parts = filename.rsplit('.', 1)
            if len(parts) == 2:
                originals.append({
                    "doc_id": parts[0],
                    "extension": parts[1],
                    "filename": filename,
                    "size_bytes": f["size_bytes"]
                })
        
        return {"originals": originals, "count": len(originals)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Async upload (v4):
    - Returns 202 Accepted immediately with task_id
    - Processes file in background (parsing, chunking, embedding)
    - Frontend polls /api/documents/{task_id}/status for progress
    """
    try:
        from fastapi import BackgroundTasks
        doc_service = get_document_service()
        
        if not doc_service.can_process(file.filename):
            supported = doc_service.get_supported_types()
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported)}"
            )
        
        # Read file immediately (since UploadFile is bound to request scope)
        content = await file.read()
        
        # Generate ID and start background task
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Initialize status
        doc_service._update_status(doc_id, "queued", 0)
        
        # Add to background tasks
        if background_tasks:
            background_tasks.add_task(
                doc_service.process_file_background,
                doc_id=doc_id,
                file_content=content,
                filename=file.filename,
                save_original=True
            )
        
        return {
            "task_id": doc_id,
            "status": "queued",
            "message": "Upload accepted for background processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{task_id}/status")
async def get_upload_status(task_id: str):
    """Get status of background upload task"""
    doc_service = get_document_service()
    status = doc_service.get_upload_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return status


@router.post("/upload-batch")
async def upload_documents_batch(files: List[UploadFile] = File(...)):
    """Upload multiple documents at once"""
    from fastapi.concurrency import run_in_threadpool
    results = []
    errors = []
    
    doc_service = get_document_service()
    
    for file in files:
        try:
            if not doc_service.can_process(file.filename):
                errors.append({
                    "filename": file.filename,
                    "error": "Unsupported file type"
                })
                continue
            
            content = await file.read()
            
            # Run blocking processing in thread pool
            result = await run_in_threadpool(
                doc_service.process_file,
                file_content=content,
                filename=file.filename,
                save_original=True
            )
            results.append(result)
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "uploaded": len(results),
        "failed": len(errors),
        "documents": results,
        "errors": errors
    }


@router.get("/{doc_id}/original")
async def get_original_file(doc_id: str):
    """
    Get original file as base64 for viewing in browser.
    
    Lookup strategy:
    1. Try direct doc_id lookup in MinIO
    2. Get document metadata from Qdrant, extract parent_doc_id
    3. Try parent_doc_id lookup in MinIO
    4. If still not found, search for any document with matching filename
    """
    try:
        doc_service = get_document_service()
        
        # Strategy 1: Direct lookup
        file_data = doc_service.get_original_file(doc_id)
        if file_data:
            print(f"✅ Original found directly with doc_id: {doc_id}")
            return file_data
        
        # Strategy 2: Get parent_doc_id from document metadata
        document = doc_service.get_document(doc_id)
        if document:
            parent_id = document.get("metadata", {}).get("parent_doc_id")
            if parent_id and parent_id != doc_id:
                file_data = doc_service.get_original_file(parent_id)
                if file_data:
                    print(f"✅ Original found via parent_doc_id: {parent_id}")
                    return file_data
            
            # Strategy 3: Maybe the doc_id in metadata differs from URL param
            meta_doc_id = document.get("doc_id")
            if meta_doc_id and meta_doc_id != doc_id:
                file_data = doc_service.get_original_file(meta_doc_id)
                if file_data:
                    print(f"✅ Original found via metadata doc_id: {meta_doc_id}")
                    return file_data
        
        print(f"❌ Original file not found for doc_id: {doc_id}")
        raise HTTPException(status_code=404, detail="Original file not found")
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get file: {str(e)}")


@router.get("/{doc_id}/presigned")
async def get_presigned_url(doc_id: str, expiry_hours: int = 1):
    """
    Get presigned URL for direct browser access to file.
    
    This is the recommended method for large files (>2MB).
    The browser can load the file directly from MinIO storage,
    which avoids memory issues with base64 encoding.
    
    Returns:
        - url: Direct presigned URL (valid for expiry_hours)
        - filename: Original filename
        - mime_type: MIME type for content-type header
        - size_bytes: File size
        - expiry_hours: How long the URL is valid
    """
    try:
        doc_service = get_document_service()
        
        # Get the actual file ID (might need parent_doc_id lookup)
        actual_id = doc_id
        document = doc_service.get_document(doc_id)
        if document:
            parent_id = document.get("metadata", {}).get("parent_doc_id")
            if parent_id:
                actual_id = parent_id
        
        # Try to get presigned URL
        presigned = doc_service._file_storage.get_presigned_url(
            actual_id, 
            expiry_hours=expiry_hours,
            inline=True
        )
        
        if presigned:
            return presigned
        
        # Fallback: If MinIO not available, return file info with indicator to use base64
        file_info = doc_service._file_storage.get_file_info(actual_id)
        if file_info:
            return {
                "filename": file_info["filename"],
                "mime_type": file_info["mime_type"],
                "size_bytes": file_info["size_bytes"],
                "storage": file_info["storage"],
                "presigned_available": False,
                "message": "Presigned URL not available, use /original endpoint for base64"
            }
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get presigned URL: {str(e)}")


@router.get("/{doc_id}/download")
async def download_file(doc_id: str):
    """
    Download original file.
    Uses same multi-strategy lookup as /original endpoint.
    """
    try:
        doc_service = get_document_service()
        
        # Strategy 1: Direct lookup
        result = doc_service.download_file(doc_id)
        
        # Strategy 2: Try parent_doc_id
        if not result:
            document = doc_service.get_document(doc_id)
            if document:
                parent_id = document.get("metadata", {}).get("parent_doc_id")
                if parent_id and parent_id != doc_id:
                    result = doc_service.download_file(parent_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Original file not found")
        
        content, filename = result
        
        # Determine content type
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'xml': 'application/xml',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'json': 'application/json',
            'html': 'text/html',
            'png': 'image/png',
            'jpg': 'image/jpeg',
        }
        
        return Response(
            content=content,
            media_type=content_types.get(ext, 'application/octet-stream'),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """Semantic search across all documents"""
    try:
        doc_service = get_document_service()
        results = doc_service.search(
            query=request.query,
            limit=request.limit,
            doc_type=request.doc_type
        )
        
        return [
            SearchResult(
                doc_id=r.get("doc_id", ""),
                content=r.get("content", "")[:500] + "..." if len(r.get("content", "")) > 500 else r.get("content", ""),
                filename=r.get("filename", ""),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {})
            )
            for r in results
        ]
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/list")
async def list_documents(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    doc_type: Optional[str] = None
):
    """List all documents with pagination"""
    try:
        doc_service = get_document_service()
        documents = doc_service.list_documents(
            limit=limit,
            offset=offset,
            doc_type=doc_type
        )
        
        stats = doc_service.get_stats()
        
        return {
            "documents": documents,
            "total": stats.get("points_count", 0),
            "limit": limit,
            "offset": offset,
            "supported_types": stats.get("supported_types", []),
            "stored_files": stats.get("stored_files", 0)
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")


# =====================================================
# Category Management Endpoints
# IMPORTANT: These must be defined BEFORE /{doc_id} 
# to avoid the catch-all route matching first!
# =====================================================

class CreateCategoryRequest(BaseModel):
    name: str
    parent: Optional[str] = None


class MoveToCategoryRequest(BaseModel):
    category: str


@router.get("/categories")
async def list_categories():
    """
    List all document categories
    
    Returns hierarchical category structure with document counts
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        categories = cat_service.list_categories()
        
        return {
            "categories": [c.to_dict() for c in categories],
            "total": len(categories)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to list categories: {str(e)}")


@router.post("/categories")
async def create_category(request: CreateCategoryRequest):
    """
    Create a new category
    
    Categories are virtual folders for organizing documents.
    They become active when documents are assigned to them.
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        
        category = cat_service.create_category(
            name=request.name,
            parent=request.parent
        )
        
        return {
            "success": True,
            "category": category.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")


@router.get("/categories/{category_path:path}/documents")
async def get_documents_by_category(category_path: str, limit: int = 100):
    """
    Get all documents in a specific category
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        
        documents = cat_service.get_documents_by_category(category_path, limit)
        
        return {
            "category": category_path,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")


@router.delete("/categories/{category_path:path}")
async def delete_category(category_path: str, move_to: Optional[str] = None):
    """
    Delete a category and move its documents
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        
        success = cat_service.delete_category(category_path, move_to)
        
        return {
            "success": success,
            "deleted_category": category_path,
            "documents_moved_to": move_to or "Allgemein"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")


class RenameCategoryRequest(BaseModel):
    new_name: str


@router.put("/categories/{category_path:path}/rename")
async def rename_category(category_path: str, request: RenameCategoryRequest):
    """
    Rename a category
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        
        success = cat_service.rename_category(category_path, request.new_name)
        
        if success:
            return {
                "success": True,
                "old_name": category_path,
                "new_name": request.new_name
            }
        else:
            raise HTTPException(status_code=404, detail="Category not found or empty")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to rename category: {str(e)}")


@router.put("/{doc_id}/category")
async def move_document_to_category(doc_id: str, request: MoveToCategoryRequest):
    """
    Move a document to a different category
    
    Updates the category metadata for the document and all its chunks.
    """
    try:
        from services.rag.category_service import get_category_service
        cat_service = get_category_service()
        
        success = cat_service.move_document(doc_id, request.category)
        
        if success:
            return {
                "success": True,
                "doc_id": doc_id,
                "new_category": request.category
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to move document: {str(e)}")


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID (text content)"""
    try:
        doc_service = get_document_service()
        document = doc_service.get_document(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if original file exists (with fallback to parent_doc_id)
        has_original = doc_service.get_original_file(doc_id) is not None
        if not has_original:
            parent_id = document.get("metadata", {}).get("parent_doc_id")
            if parent_id and parent_id != doc_id:
                has_original = doc_service.get_original_file(parent_id) is not None
        
        document["has_original"] = has_original
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Get failed: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """
    Enterprise cascade delete:
    - Deletes ALL chunks from Qdrant (using parent_doc_id)
    - Deletes original file from MinIO
    """
    try:
        doc_service = get_document_service()
        result = doc_service.delete_document(doc_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Document not found or delete failed")
        
        return {
            "status": "deleted",
            "doc_id": doc_id,
            "parent_doc_id": result.get("parent_doc_id"),
            "chunks_deleted": result.get("chunks_deleted", 0),
            "file_deleted": result.get("file_deleted", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/sync")
async def sync_storage():
    """
    Synchronize MinIO and Qdrant:
    - Removes orphaned Qdrant entries (no corresponding MinIO file)
    - Removes orphaned MinIO files (no corresponding Qdrant entry)
    """
    try:
        doc_service = get_document_service()
        result = doc_service.sync_storage()
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/health/consistency")
async def check_consistency():
    """
    Check consistency between MinIO and Qdrant WITHOUT making changes.
    Returns a report of any orphaned entries found.
    """
    try:
        doc_service = get_document_service()
        report = doc_service.get_consistency_report()
        return report
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Consistency check failed: {str(e)}")


@router.get("/stats/summary")
async def get_stats():
    """Get document collection statistics"""
    try:
        doc_service = get_document_service()
        return doc_service.get_stats()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


# --- RAG Chat Endpoint ---

def get_rag_chat_service():
    from services.rag.rag_chat_service import rag_chat_service
    return rag_chat_service


@router.post("/chat", response_model=ChatResponseModel)
async def chat_with_documents(request: ChatRequest):
    """
    Chat mit den hochgeladenen Dokumenten (RAG)
    
    - Sucht relevante Chunks in Qdrant
    - Sendet Kontext + Frage an OpenAI GPT
    - Gibt Antwort mit Quellenangaben zurück
    """
    try:
        rag_service = get_rag_chat_service()
        
        result = rag_service.chat(
            query=request.query,
            conversation_history=request.conversation_history,
            num_chunks=request.num_chunks
        )
        
        return ChatResponseModel(
            answer=result["answer"],
            sources=result["sources"],
            has_context=result["has_context"],
            chunks_found=result["chunks_found"]
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")



@router.get("/chat/health")
async def chat_health():
    """Health check for RAG chat service"""
    try:
        from config import config
        rag_service = get_rag_chat_service()
        stats = rag_service.get_stats()
        return {
            "status": "healthy" if stats["ready"] else "degraded",
            "openai_configured": stats["ready"],
            "model": stats["model"],
            "vector_store": stats["vector_store"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
