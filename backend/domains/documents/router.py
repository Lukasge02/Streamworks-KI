"""
Documents API Router v3
REST endpoints with original file download support
"""

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Query,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse, Response, StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
import traceback


router = APIRouter(prefix="/api/documents", tags=["Documents"])


# Request/Response Models

# Request/Response Models
from .models import (
    SearchRequest,
    ChatRequest,
    ChatResponseModel,
    SearchResult,
    CreateCategoryRequest,
    RenameCategoryRequest,
    CreateSessionRequest,
    MoveToCategoryRequest,
    CategoryAccessRequest,
    DocumentAccessRequest,
    UpdateSessionRequest,
)


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
            "message": "RAG system operational",
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "RAG system unavailable",
            },
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
                "image": "Images (PNG, JPG) with OCR via Docling",
            },
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
            parts = filename.rsplit(".", 1)
            if len(parts) == 2:
                originals.append(
                    {
                        "doc_id": parts[0],
                        "extension": parts[1],
                        "filename": filename,
                        "size_bytes": f["size_bytes"],
                    }
                )

        return {"originals": originals, "count": len(originals)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    """
    Async upload (v4):
    - Returns 202 Accepted immediately with task_id
    - Processes file in background (parsing, chunking, embedding)
    - Frontend polls /api/documents/{task_id}/status for progress
    - Optional category parameter to assign document to specific category
    """
    try:
        doc_service = get_document_service()

        if not doc_service.can_process(file.filename):
            supported = doc_service.get_supported_types()
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported)}",
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
                save_original=True,
                explicit_category=category,  # Pass category to processing
            )

        return {
            "task_id": doc_id,
            "status": "queued",
            "message": "Upload accepted for background processing",
            "category": category,
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
                errors.append(
                    {"filename": file.filename, "error": "Unsupported file type"}
                )
                continue

            content = await file.read()

            # Run blocking processing in thread pool
            result = await run_in_threadpool(
                doc_service.process_file,
                file_content=content,
                filename=file.filename,
                save_original=True,
            )
            results.append(result)

        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    return {
        "uploaded": len(results),
        "failed": len(errors),
        "documents": results,
        "errors": errors,
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

    Lookup strategy:
    1. Try direct doc_id lookup in MinIO (for Testing docs, doc_id IS the parent)
    2. Try document metadata lookup for parent_doc_id
    3. Search by parent_doc_id filter
    """
    try:
        doc_service = get_document_service()
        vector_store = get_vector_store()

        # Strategy 1: Try direct lookup (doc_id might be the parent_doc_id for Testing docs)
        presigned = doc_service._file_storage.get_presigned_url(
            doc_id, expiry_hours=expiry_hours, inline=True
        )

        if presigned:
            return presigned

        # Strategy 2: Try document metadata lookup
        document = doc_service.get_document(doc_id)
        if document:
            parent_id = document.get("metadata", {}).get("parent_doc_id")
            if parent_id and parent_id != doc_id:
                presigned = doc_service._file_storage.get_presigned_url(
                    parent_id, expiry_hours=expiry_hours, inline=True
                )
                if presigned:
                    return presigned

        # Strategy 3: Search by parent_doc_id filter
        chunks = vector_store.search(
            query="", limit=1, score_threshold=0.0, filters={"parent_doc_id": doc_id}
        )

        if chunks:
            # doc_id is the parent - it should work for file lookup
            presigned = doc_service._file_storage.get_presigned_url(
                doc_id, expiry_hours=expiry_hours, inline=True
            )
            if presigned:
                return presigned

        # Fallback: Return file info if presigned not available
        file_info = doc_service._file_storage.get_file_info(doc_id)
        if file_info:
            return {
                "filename": file_info["filename"],
                "mime_type": file_info["mime_type"],
                "size_bytes": file_info["size_bytes"],
                "storage": file_info["storage"],
                "presigned_available": False,
                "message": "Presigned URL not available, use /original endpoint",
            }

        raise HTTPException(status_code=404, detail="File not found")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to get presigned URL: {str(e)}"
        )


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
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        content_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "xml": "application/xml",
            "txt": "text/plain",
            "md": "text/markdown",
            "json": "application/json",
            "html": "text/html",
            "png": "image/png",
            "jpg": "image/jpeg",
        }

        return Response(
            content=content,
            media_type=content_types.get(ext, "application/octet-stream"),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

        filters = None
        if request.doc_id:
            # Filter by parent_doc_id since chunks store parent_doc_id
            filters = {"parent_doc_id": request.doc_id}

        results = doc_service.search(
            query=request.query,
            limit=request.limit,
            doc_type=request.doc_type,
            filters=filters,
        )

        return [
            SearchResult(
                doc_id=r.get("doc_id", ""),
                content=r.get("content", "")[:500] + "..."
                if len(r.get("content", "")) > 500
                else r.get("content", ""),
                filename=r.get("filename", ""),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {}),
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
    doc_type: Optional[str] = None,
    category: Optional[str] = None,
    deduplicate: bool = Query(
        True, description="Deduplicate by parent_doc_id to show unique documents"
    ),
):
    """
    List all documents with pagination.

    Args:
        limit: Max documents to return
        offset: Pagination offset
        doc_type: Filter by document type (pdf, docx, etc.)
        category: Filter by category name
        deduplicate: If True (default), return unique documents; if False, return all chunks
    """
    try:
        doc_service = get_document_service()
        documents = doc_service.list_documents(
            limit=limit * 3
            if deduplicate
            else limit,  # Fetch more to account for deduplication
            offset=offset,
            doc_type=doc_type,
        )

        # Apply category filter if specified
        if category:
            default_cat = "Allgemein"
            if category == default_cat:
                # Include documents with null, empty, or "Allgemein" category
                documents = [
                    d
                    for d in documents
                    if not d.get("category") or d.get("category") == default_cat
                ]
            else:
                documents = [d for d in documents if d.get("category") == category]

        # Deduplicate by parent_doc_id if requested
        if deduplicate:
            seen_parents = set()
            unique_docs = []
            for doc in documents:
                parent_id = doc.get("parent_doc_id") or doc.get("doc_id")
                if parent_id not in seen_parents:
                    seen_parents.add(parent_id)
                    unique_docs.append(doc)
                    if len(unique_docs) >= limit:
                        break
            documents = unique_docs

        # Enrich with access levels
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        for doc in documents:
            # Use parent_doc_id for logical document identification
            # This ensures access levels and ID references are consistent with the File entity
            parent_id = doc.get("parent_doc_id") or doc.get("doc_id")

            if parent_id:
                # Check access using the logical File ID
                access = access_service.get_document_access(parent_id)
                doc["access_level"] = (
                    access.access_level.value if access else "internal"
                )

                # If deduplicating, we are returning "Files", so doc_id should be the File ID
                if deduplicate:
                    doc["doc_id"] = parent_id

        # Get accurate total count
        from services.rag.category_service import get_category_service

        cat_service = get_category_service()
        total_unique = cat_service.get_total_document_count()

        stats = doc_service.get_stats()

        return {
            "documents": documents,
            "total": total_unique,  # Total unique documents
            "total_chunks": stats.get("points_count", 0),  # Total chunks for reference
            "limit": limit,
            "offset": offset,
            "supported_types": stats.get("supported_types", []),
            "stored_files": stats.get("stored_files", 0),
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")


@router.get("/chunks/{parent_doc_id}")
async def get_document_chunks(parent_doc_id: str):
    """
    Get all chunks for a specific document, sorted by chunk_index.

    This endpoint is used by the document viewer to display all chunks
    in the correct order for a given parent document.
    """
    try:
        vector_store = get_vector_store()
        from qdrant_client.http import models

        # Get all chunks with this parent_doc_id
        chunks = []
        offset = None

        while True:
            scroll_result = vector_store.client.scroll(
                collection_name=vector_store.COLLECTION_NAME,
                limit=500,
                offset=offset,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="parent_doc_id",
                            match=models.MatchValue(value=parent_doc_id),
                        ),
                        models.FieldCondition(
                            key="doc_id", match=models.MatchValue(value=parent_doc_id)
                        ),
                    ]
                ),
                with_payload=True,
            )

            points, next_offset = scroll_result

            for point in points:
                payload = point.payload
                chunks.append(
                    {
                        "doc_id": payload.get("doc_id"),
                        "chunk_index": payload.get("chunk_index", 0),
                        "total_chunks": payload.get("total_chunks", 1),
                        "content_preview": (payload.get("content", "")[:200] + "...")
                        if payload.get("content")
                        else "",
                        "chunk_page_numbers": payload.get("chunk_page_numbers", []),
                        "chunk_section_title": payload.get("chunk_section_title"),
                        "chunk_word_count": payload.get("chunk_word_count", 0),
                    }
                )

            if next_offset is None:
                break
            offset = next_offset

        # Sort by chunk_index
        chunks.sort(key=lambda x: x.get("chunk_index", 0))

        return {"parent_doc_id": parent_doc_id, "chunks": chunks, "total": len(chunks)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


# =====================================================
# Category Management Endpoints
# IMPORTANT: These must be defined BEFORE /{doc_id}
# to avoid the catch-all route matching first!
# =====================================================


@router.get("/categories/counts")
async def get_category_counts():
    """
    Get all categories with accurate document counts (deduplicated by parent_doc_id).

    This is the primary endpoint for the frontend sidebar.
    Returns:
    - total_documents: Total unique documents across all categories
    - categories: List of categories with their document counts
    """
    try:
        from services.rag.category_service import get_category_service

        cat_service = get_category_service()
        result = cat_service.get_category_counts()

        return {
            "total_documents": result["total_documents"],
            "categories": [c.to_dict() for c in result["categories"]],
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to get category counts: {str(e)}"
        )


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
            "total": len(categories),
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to list categories: {str(e)}"
        )


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

        category = cat_service.create_category(name=request.name, parent=request.parent)

        return {"success": True, "category": category.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to create category: {str(e)}"
        )


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
            "count": len(documents),
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to get documents: {str(e)}"
        )


@router.delete("/categories/{category_path:path}")
async def delete_category(
    category_path: str,
    cascade: bool = Query(
        False, description="If true, permanently delete all documents in the folder"
    ),
    move_to: Optional[str] = None,
):
    """
    Delete a category (folder).

    - cascade=false (default): Move documents to 'move_to' or 'Allgemein'
    - cascade=true: Permanently delete all documents in the folder

    This behaves like folder deletion in Google Drive or Dropbox.
    """
    try:
        from services.rag.category_service import get_category_service

        cat_service = get_category_service()

        result = cat_service.delete_category(category_path, move_to, cascade)

        if not result.get("success"):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Delete failed")
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete category: {str(e)}"
        )


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
                "new_name": request.new_name,
            }
        else:
            raise HTTPException(status_code=404, detail="Category not found or empty")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to rename category: {str(e)}"
        )


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
            return {"success": True, "doc_id": doc_id, "new_category": request.category}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to move document: {str(e)}"
        )


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
            raise HTTPException(
                status_code=404, detail="Document not found or delete failed"
            )

        return {
            "status": "deleted",
            "doc_id": doc_id,
            "parent_doc_id": result.get("parent_doc_id"),
            "chunks_deleted": result.get("chunks_deleted", 0),
            "file_deleted": result.get("file_deleted", False),
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
        raise HTTPException(
            status_code=500, detail=f"Consistency check failed: {str(e)}"
        )


@router.get("/stats/summary")
async def get_stats():
    """Get document collection statistics"""
    try:
        doc_service = get_document_service()
        return doc_service.get_stats()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


# --- RAG Chat Endpoint (LlamaIndex) ---


def get_rag_chat_service():
    """Get LlamaIndex ChatService (replaces old EnhancedRAGChatService)"""
    from services.rag.engine.chat_service import get_chat_service

    return get_chat_service()


def get_chat_session_service():
    from services.chat_session_service import chat_session_service

    return chat_session_service


# =====================================================
# Chat Session Endpoints
# IMPORTANT: These must be defined BEFORE /chat to avoid route conflicts
# =====================================================


@router.delete("/chat/sessions")
async def delete_all_chat_sessions():
    """
    Delete all chat sessions
    """
    try:
        session_service = get_chat_session_service()
        success = session_service.delete_all_sessions()

        if success:
            return {"status": "deleted", "message": "All sessions deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete sessions")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/chat/sessions")
async def create_chat_session(request: CreateSessionRequest = None):
    """
    Create a new chat session

    Returns the new session with its ID for subsequent messages
    """
    try:
        session_service = get_chat_session_service()
        title = request.title if request and request.title else "Neuer Chat"
        session = session_service.create_session(title=title)

        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")

        return {"session": session, "message": "Session created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@router.get("/chat/sessions")
async def list_chat_sessions(limit: int = Query(50, ge=1, le=100)):
    """
    List all chat sessions ordered by most recent

    Returns sessions with message counts for sidebar display
    """
    try:
        session_service = get_chat_session_service()
        sessions = session_service.list_sessions(limit=limit)

        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """
    Get a chat session with all its messages

    Returns full session data including message history and sources
    """
    try:
        session_service = get_chat_session_service()
        session = session_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return session
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@router.patch("/chat/sessions/{session_id}")
async def update_chat_session(session_id: str, request: UpdateSessionRequest):
    """
    Update a chat session's title
    """
    try:
        session_service = get_chat_session_service()
        session = session_service.update_session(session_id, {"title": request.title})

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"session": session, "message": "Session updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to update session: {str(e)}"
        )


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session and all its messages
    """
    try:
        session_service = get_chat_session_service()
        success = session_service.delete_session(session_id)

        if not success:
            raise HTTPException(
                status_code=404, detail="Session not found or delete failed"
            )

        return {"success": True, "message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete session: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponseModel)
async def chat_with_documents(request: ChatRequest):
    """
    Chat mit den hochgeladenen Dokumenten (RAG)

    - Sucht relevante Chunks in Qdrant
    - Sendet Kontext + Frage an OpenAI GPT
    - Gibt Antwort mit Quellenangaben zurück
    - Optional: Speichert Nachrichten in Session (wenn session_id angegeben)
    """
    try:
        rag_service = get_rag_chat_service()
        session_service = get_chat_session_service()
        session_id = request.session_id

        # Auto-create session if not provided
        if not session_id:
            session = session_service.create_session(
                title=session_service.generate_session_title(request.query)
            )
            if session:
                session_id = session["id"]

        # Save user message
        if session_id:
            session_service.add_message(
                session_id=session_id, role="user", content=request.query
            )

        # Get RAG response (using enhanced service)
        result = rag_service.chat_simple(
            query=request.query,
            conversation_history=request.conversation_history,
            num_chunks=request.num_chunks,
        )

        # Save assistant response with sources
        if session_id:
            session_service.add_message(
                session_id=session_id,
                role="assistant",
                content=result["answer"],
                sources=result["sources"],
            )

        return ChatResponseModel(
            answer=result["answer"],
            sources=result["sources"],
            has_context=result["has_context"],
            chunks_found=result["chunks_found"],
            session_id=session_id,
            # Enhanced fields
            confidence=result.get("confidence"),
            confidence_level=result.get("confidence_level"),
            query_type=result.get("query_type"),
            warnings=result.get("warnings"),
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


class StreamChatRequest(BaseModel):
    """Request model for streaming chat"""

    query: str
    num_chunks: int = 5
    session_id: Optional[str] = None


@router.post("/chat/stream")
async def chat_with_documents_stream(request: StreamChatRequest):
    """
    Streaming Chat mit Dokumenten (RAG)

    Verwendet Server-Sent Events (SSE) für Echtzeit-Token-Streaming.

    Event-Typen:
    - status: Statusinformationen (Suche, Ranking, etc.)
    - source: Quelldokumente mit Relevanz-Scores
    - token: Einzelne Tokens der Antwort
    - done: Abschluss mit Metadaten (confidence, query_type)
    - error: Fehlermeldungen
    """
    from services.rag.engine.streaming_service import get_streaming_service

    streaming_service = get_streaming_service()
    session_service = get_chat_session_service()
    session_id = request.session_id

    # Auto-create session if not provided
    if not session_id:
        session = session_service.create_session(
            title=session_service.generate_session_title(request.query)
        )
        if session:
            session_id = session["id"]

    # Save user message
    if session_id:
        session_service.add_message(
            session_id=session_id, role="user", content=request.query
        )

    async def event_stream():
        """Generate SSE events"""
        full_response = ""
        sources = []

        async for event in streaming_service.stream_query(
            query_text=request.query,
            top_k=request.num_chunks,
            session_id=session_id,
        ):
            # Collect full response for session storage
            if '"type": "token"' in event or "event: token" in event:
                try:
                    import json

                    # Parse the SSE event to get content
                    for line in event.split("\n"):
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if "content" in data:
                                full_response += data["content"]
                except Exception:
                    pass

            # Collect sources for session storage
            if "event: source" in event:
                try:
                    import json

                    for line in event.split("\n"):
                        if line.startswith("data: "):
                            sources.append(json.loads(line[6:]))
                except Exception:
                    pass

            # Add session_id to done event
            if "event: done" in event:
                try:
                    import json

                    lines = event.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            data["session_id"] = session_id
                            lines[i] = f"data: {json.dumps(data, ensure_ascii=False)}"
                            event = "\n".join(lines)
                            break
                except Exception:
                    pass

                # Save assistant response
                if session_id and full_response:
                    session_service.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                        sources=sources,
                    )

            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/chat/health")
async def chat_health():
    """Health check for RAG chat service"""
    try:
        rag_service = get_rag_chat_service()
        stats = rag_service.get_stats()
        return {
            "status": "healthy" if stats["ready"] else "degraded",
            "openai_configured": stats["ready"],
            "model": stats["model"],
            "vector_store": stats.get("vector_store", {}),
            "enhancements": stats.get("enhancements", {}),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/chat/stats")
async def get_rag_stats():
    """
    Get detailed RAG system statistics

    Returns comprehensive metrics about:
    - Cache performance (hit rates)
    - Enhancement status
    - Component statistics
    """
    try:
        rag_service = get_rag_chat_service()
        stats = rag_service.get_stats()

        # Add cache stats
        from services.rag.cache import rag_cache

        cache_stats = rag_cache.get_stats()

        return {
            "rag_service": {
                "model": stats.get("model"),
                "ready": stats.get("ready"),
                "enhancements": stats.get("enhancements", {}),
            },
            "cache": cache_stats,
            "components": {
                "hybrid_search": stats.get("hybrid_search", {}),
                "query_processor": stats.get("query_processor", {}),
                "reranker": stats.get("reranker", {}),
                "context_processor": stats.get("context_processor", {}),
                "response_enhancer": stats.get("response_enhancer", {}),
            },
            "vector_store": stats.get("vector_store", {}),
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}


# =====================================================
# Access Control Endpoints
# Enterprise-grade document access management
# =====================================================


@router.get("/access/{doc_id}")
async def get_document_access(doc_id: str):
    """
    Get access control settings for a document.

    Access levels:
    - public: Accessible by all users
    - internal: Authenticated users only (default)
    - restricted: Specific roles/users only
    - project: Only within linked project context
    """
    try:
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        access = access_service.get_document_access(doc_id)

        if not access:
            return {
                "doc_id": doc_id,
                "access_level": "internal",
                "allowed_roles": [],
                "allowed_users": [],
                "is_public": False,
            }

        return access.to_dict()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get access: {str(e)}")


@router.put("/access/{doc_id}")
async def set_document_access(doc_id: str, request: DocumentAccessRequest):
    """
    Set access control settings for a document.

    Updates the access level and allowed roles/users.
    This affects RAG retrieval - restricted documents will only
    be returned to users with appropriate permissions.
    """
    try:
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        success = access_service.set_document_access(
            doc_id=doc_id,
            access_level=request.access_level,
            allowed_roles=request.allowed_roles,
            allowed_users=request.allowed_users,
        )

        if success:
            return {
                "success": True,
                "doc_id": doc_id,
                "access_level": request.access_level,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set access")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to set access: {str(e)}")


@router.get("/categories/{category_path:path}/access")
async def get_category_access(category_path: str):
    """
    Get access control settings for a category.

    If inheritable=True, all documents in the category
    inherit these access settings.
    """
    try:
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        access = access_service.get_category_access(category_path)

        if not access:
            return {
                "category_path": category_path,
                "access_level": "internal",
                "allowed_roles": [],
                "inheritable": True,
            }

        return access.to_dict()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to get category access: {str(e)}"
        )


@router.put("/categories/{category_path:path}/access")
async def set_category_access(category_path: str, request: CategoryAccessRequest):
    """
    Set access control settings for a category.

    If inheritable=True, all documents in the category
    will inherit these access settings.
    """
    try:
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        success = access_service.set_category_access(
            category_path=category_path,
            access_level=request.access_level,
            allowed_roles=request.allowed_roles,
            inheritable=request.inheritable,
        )

        if success:
            return {
                "success": True,
                "category_path": category_path,
                "access_level": request.access_level,
                "inheritable": request.inheritable,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set category access")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to set category access: {str(e)}"
        )


@router.get("/accessible")
async def list_accessible_documents(
    user_id: Optional[str] = None,
    roles: Optional[str] = None,  # Comma-separated list
    categories: Optional[str] = None,  # Comma-separated list
):
    """
    List all documents accessible to a user.

    This endpoint is useful for:
    - Testing access configurations
    - Building document selection UIs
    - Compliance auditing
    """
    try:
        from services.rag.access_service import get_access_service

        access_service = get_access_service()

        category_list = categories.split(",") if categories else None
        role_list = roles.split(",") if roles else None

        # Get ALL documents from VectorStore directly
        doc_service = get_document_service()
        all_docs = doc_service.list_documents(limit=500)

        documents = []
        seen_parents = set()

        for doc in all_docs:
            # Use parent_doc_id for logical document identification
            # Fallback to doc_id if parent_doc_id is missing (e.g. unchunked files)
            parent_id = doc.get("parent_doc_id") or doc.get("doc_id")
            doc_id = doc.get("doc_id")  # Keep original ID for reference if needed

            # Deduplication: Only process each logical document once
            if parent_id in seen_parents:
                continue
            seen_parents.add(parent_id)

            # Check if user has access using the logical File ID
            if not access_service.check_document_access(
                doc_id=parent_id, user_id=user_id, user_roles=role_list
            ):
                continue

            # Get access info for display (cached)
            access = access_service.get_document_access(parent_id)
            access_level = access.access_level.value if access else "internal"

            # Filter by Category (if requested)
            category = doc.get("category", "Allgemein")
            if category_list and category not in category_list:
                continue

            filename = doc.get("filename", "Unbenannt")

            # Return the logical ID (parent_id) as the doc_id for the frontend
            # This ensures the frontend operates on the file, not a random chunk
            documents.append(
                {
                    "doc_id": parent_id,
                    "filename": filename,
                    "category": category,
                    "access_level": access_level,
                    "chunk_count": doc.get("chunk_count", 0),
                    "original_chunk_id": doc_id,  # Keep track of a physical chunk ID if needed
                }
            )

        return {"total": len(documents), "documents": documents}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to list accessible documents: {str(e)}"
        )


# =====================================================
# Catch-all Endpoint
# MUST be defined LAST to avoid shadowing other routes
# =====================================================


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """
    Get a specific document by ID (text content).

    Lookup strategy:
    1. Direct doc_id lookup in Qdrant
    2. Search for chunks with this parent_doc_id
    """
    try:
        doc_service = get_document_service()
        vector_store = get_vector_store()

        # Strategy 1: Direct lookup
        document = doc_service.get_document(doc_id)

        # Strategy 2: Search by parent_doc_id (for Testing documents) - get ALL chunks
        if not document:
            # Get ALL chunks with this parent_doc_id
            chunks = vector_store.search(
                query="",
                limit=100,  # Get all chunks
                score_threshold=0.0,
                filters={"parent_doc_id": doc_id},
            )

            if chunks and len(chunks) > 0:
                # Sort chunks by chunk_index to reconstruct proper order
                chunks.sort(key=lambda x: x.get("metadata", {}).get("chunk_index", 0))

                # Combine all chunk contents
                full_content = "\n\n".join([c.get("content", "") for c in chunks])

                # Use metadata from first chunk
                first_meta = chunks[0].get("metadata", {})
                document = {
                    "doc_id": doc_id,
                    "content": full_content,
                    "metadata": {
                        "filename": first_meta.get("filename", "Dokument"),
                        "doc_type": first_meta.get("doc_type", "unknown"),
                        "category": first_meta.get("category", "Allgemein"),
                        "created_at": first_meta.get("created_at"),
                        "word_count": first_meta.get("word_count", 0),
                        "page_count": first_meta.get("page_count", 0),
                        "parent_doc_id": doc_id,
                        "total_chunks": len(chunks),
                    },
                }

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
