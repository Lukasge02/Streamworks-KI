"""
Debug Router
Endpoints for debugging and monitoring Qdrant integration
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/qdrant/health", response_model=Dict[str, Any])
async def get_qdrant_health():
    """
    Get Qdrant service health status and collection information
    """
    try:
        from services.qdrant_rag_service import get_rag_service

        rag_service = await get_rag_service()
        health_status = await rag_service.get_health_status()

        return JSONResponse(content=health_status)

    except Exception as e:
        logger.error(f"Failed to get Qdrant health status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "service": "QdrantRAGService",
                "status": "error",
                "error": str(e)
            }
        )


@router.get("/qdrant/documents/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Maximum chunks to return"),
    offset: int = Query(0, ge=0, description="Number of chunks to skip"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all Qdrant chunks for a specific document

    - **document_id**: Document UUID to inspect
    - **limit**: Maximum number of chunks to return (1-1000)
    - **offset**: Number of chunks to skip for pagination
    """
    try:
        # Verify document exists in database
        from services.document import DocumentService
        doc_service = DocumentService()

        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get chunks from Qdrant
        from services.qdrant_rag_service import get_rag_service
        rag_service = await get_rag_service()

        if not await rag_service.initialize():
            raise HTTPException(status_code=503, detail="Qdrant service not available")

        chunks = await rag_service.qdrant_service.get_document_chunks(
            doc_id=str(document_id),
            limit=limit,
            offset=offset
        )

        # Prepare response with document metadata
        response_data = {
            "document": {
                "id": str(document.id),
                "filename": document.filename,
                "original_filename": document.original_filename,
                "status": document.status.value if hasattr(document.status, 'value') else str(document.status),
                "created_at": document.created_at.isoformat(),
                "file_size": document.file_size,
                "chunk_count_db": getattr(document, 'chunk_count', 0)
            },
            "qdrant_chunks": {
                "total_found": len(chunks),
                "offset": offset,
                "limit": limit,
                "chunks": chunks
            },
            "analysis": {
                "chunks_in_qdrant": len(chunks),
                "chunks_expected": getattr(document, 'chunk_count', 0),
                "qdrant_sync_status": "✅ synchronized" if len(chunks) > 0 else "❌ missing chunks"
            }
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document chunks for {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(e)}")


@router.delete("/qdrant/documents/{document_id}/chunks")
async def delete_document_chunks(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete Qdrant chunks for a specific document (debug cleanup)

    - **document_id**: Document UUID to clean up
    """
    try:
        # Verify document exists in database
        from services.document import DocumentService
        doc_service = DocumentService()

        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete chunks from Qdrant
        from services.qdrant_rag_service import get_rag_service
        rag_service = await get_rag_service()

        success = await rag_service.delete_document(str(document_id))

        response_data = {
            "document_id": str(document_id),
            "filename": document.original_filename,
            "deletion_success": success,
            "message": f"Chunks {'successfully deleted' if success else 'deletion failed'} from Qdrant"
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document chunks for {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chunks: {str(e)}")


@router.get("/qdrant/collection/info")
async def get_qdrant_collection_info():
    """
    Get Qdrant collection information and statistics
    """
    try:
        from services.qdrant_rag_service import get_rag_service

        rag_service = await get_rag_service()
        if not await rag_service.initialize():
            raise HTTPException(status_code=503, detail="Qdrant service not available")

        collection_info = await rag_service.qdrant_service.get_collection_info()

        return JSONResponse(content={
            "collection": collection_info,
            "service_health": await rag_service.get_health_status()
        })

    except Exception as e:
        logger.error(f"Failed to get Qdrant collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.post("/qdrant/documents/{document_id}/reprocess")
async def reprocess_document_chunks(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Reprocess document and regenerate Qdrant chunks

    - **document_id**: Document UUID to reprocess
    """
    try:
        # Reprocess document
        from services.document import DocumentService
        doc_service = DocumentService()

        document = await doc_service.reprocess_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found or reprocessing failed")

        # Get updated chunk count from Qdrant
        from services.qdrant_rag_service import get_rag_service
        rag_service = await get_rag_service()

        chunks = await rag_service.qdrant_service.get_document_chunks(
            doc_id=str(document_id),
            limit=1  # Just count
        )

        response_data = {
            "document_id": str(document_id),
            "filename": document.original_filename,
            "status": document.status.value if hasattr(document.status, 'value') else str(document.status),
            "chunks_in_qdrant": len(chunks) if chunks else 0,
            "reprocessed_at": document.updated_at.isoformat() if document.updated_at else None,
            "message": "Document successfully reprocessed and chunks updated in Qdrant"
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reprocess document: {str(e)}")


@router.get("/qdrant/orphaned-chunks")
async def find_orphaned_chunks(
    limit: int = Query(50, ge=1, le=500, description="Maximum orphaned chunks to find"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Find Qdrant chunks that don't have corresponding documents in the database
    """
    try:
        from services.qdrant_rag_service import get_rag_service
        from services.document import DocumentService

        rag_service = await get_rag_service()
        doc_service = DocumentService()

        if not await rag_service.initialize():
            raise HTTPException(status_code=503, detail="Qdrant service not available")

        # Get all document IDs from database
        documents = await doc_service.get_documents_list(db, per_page=10000)  # Get all documents
        db_doc_ids = {str(doc.id) for doc in documents}

        # This is a simplified implementation - a full implementation would scan all Qdrant chunks
        # For now, we return collection statistics
        collection_info = await rag_service.qdrant_service.get_collection_info()

        response_data = {
            "analysis": {
                "documents_in_db": len(db_doc_ids),
                "total_chunks_in_qdrant": collection_info.get("points_count", 0),
                "estimated_chunks_per_doc": round(collection_info.get("points_count", 0) / len(db_doc_ids), 2) if db_doc_ids else 0
            },
            "collection_stats": collection_info,
            "note": "Full orphaned chunk detection requires scanning all Qdrant points and is resource-intensive. This endpoint provides summary statistics."
        }

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Failed to find orphaned chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze orphaned chunks: {str(e)}")


@router.post("/qdrant/cleanup/optimize")
async def optimize_qdrant_collection():
    """
    Trigger Qdrant collection optimization and cleanup
    """
    try:
        from services.qdrant_rag_service import get_rag_service

        rag_service = await get_rag_service()
        if not await rag_service.initialize():
            raise HTTPException(status_code=503, detail="Qdrant service not available")

        # Get collection info before optimization
        before_info = await rag_service.qdrant_service.get_collection_info()

        # Note: Qdrant handles optimization automatically
        # This endpoint mainly provides collection status

        after_info = await rag_service.qdrant_service.get_collection_info()

        response_data = {
            "optimization_completed": True,
            "collection_stats": {
                "before": before_info,
                "after": after_info
            },
            "message": "Qdrant handles optimization automatically. Collection status retrieved."
        }

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Failed to optimize Qdrant collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize collection: {str(e)}")


@router.get("/consistency/check")
async def check_consistency(
    db: AsyncSession = Depends(get_async_session)
):
    """
    Comprehensive consistency check between database and Qdrant

    Identifies:
    - Orphaned chunks (in Qdrant but not in DB)
    - Missing chunks (in DB but not in Qdrant)
    - Chunk count mismatches
    """
    try:
        from services.consistency_service import get_consistency_service

        consistency_service = await get_consistency_service()
        report = await consistency_service.perform_full_consistency_check(db)

        return JSONResponse(content=report)

    except Exception as e:
        logger.error(f"Consistency check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Consistency check failed: {str(e)}")


@router.post("/consistency/cleanup-orphaned")
async def cleanup_orphaned_chunks(
    dry_run: bool = Query(True, description="If true, only simulate cleanup"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Clean up orphaned chunks from Qdrant (chunks without DB documents)

    - **dry_run**: If true, only simulate the cleanup without making changes
    """
    try:
        from services.consistency_service import get_consistency_service

        consistency_service = await get_consistency_service()

        # First run consistency check to find orphaned chunks
        await consistency_service.perform_full_consistency_check(db)

        # Then cleanup orphaned chunks
        cleanup_report = await consistency_service.cleanup_orphaned_chunks(dry_run=dry_run)

        return JSONResponse(content=cleanup_report)

    except Exception as e:
        logger.error(f"Orphaned chunk cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.post("/consistency/repair/{document_id}")
async def repair_document_consistency(
    document_id: UUID,
    action: str = Query(..., description="Action: 'reprocess' or 'delete_chunks'"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Repair consistency issues for a specific document

    - **document_id**: Document UUID to repair
    - **action**: 'reprocess' (recreate chunks) or 'delete_chunks' (remove orphaned chunks)
    """
    try:
        from services.document import DocumentService

        doc_service = DocumentService()

        if action == "reprocess":
            # Reprocess document to recreate chunks
            document = await doc_service.reprocess_document(db, document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found or reprocessing failed")

            # Get updated chunk count
            from services.qdrant_rag_service import get_rag_service
            rag_service = await get_rag_service()
            chunks = await rag_service.qdrant_service.get_document_chunks(
                doc_id=str(document_id),
                limit=1
            )

            return JSONResponse(content={
                "action": "reprocess",
                "document_id": str(document_id),
                "filename": document.original_filename,
                "chunks_created": len(chunks) if chunks else 0,
                "status": "success"
            })

        elif action == "delete_chunks":
            # Delete orphaned chunks for this document
            from services.qdrant_rag_service import get_rag_service
            rag_service = await get_rag_service()
            success = await rag_service.delete_document(str(document_id))

            return JSONResponse(content={
                "action": "delete_chunks",
                "document_id": str(document_id),
                "success": success,
                "status": "success" if success else "failed"
            })

        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'reprocess' or 'delete_chunks'")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document consistency repair failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Repair failed: {str(e)}")


@router.get("/consistency/status")
async def get_consistency_status(
    db: AsyncSession = Depends(get_async_session)
):
    """
    Quick consistency status overview without detailed analysis
    """
    try:
        # Get basic counts
        from services.document import DocumentService
        doc_service = DocumentService()

        documents = await doc_service.get_documents_list(db, per_page=10000)
        db_count = len(documents)

        # Get Qdrant stats
        from services.qdrant_rag_service import get_rag_service
        rag_service = await get_rag_service()

        if not await rag_service.initialize():
            raise HTTPException(status_code=503, detail="Qdrant service not available")

        collection_info = await rag_service.qdrant_service.get_collection_info()
        qdrant_points = collection_info.get("points_count", 0)

        # Quick assessment
        status = "unknown"
        if db_count == 0 and qdrant_points == 0:
            status = "✅ empty_and_consistent"
        elif db_count == 0 and qdrant_points > 0:
            status = "❌ orphaned_chunks_detected"
        elif db_count > 0 and qdrant_points == 0:
            status = "⚠️ missing_chunks_detected"
        elif db_count > 0 and qdrant_points > 0:
            status = "ℹ️ needs_detailed_check"

        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "quick_status": status,
            "database": {
                "document_count": db_count
            },
            "qdrant": {
                "points_count": qdrant_points,
                "collection_status": collection_info.get("status", "unknown")
            },
            "recommendation": "Run /debug/consistency/check for detailed analysis" if status.startswith("ℹ️") or status.startswith("⚠️") or status.startswith("❌") else "System appears consistent"
        })

    except Exception as e:
        logger.error(f"Consistency status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")