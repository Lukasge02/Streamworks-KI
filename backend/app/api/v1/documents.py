"""
Document Management API - Enterprise Implementation
Handles document operations for the chat system
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.database import get_db
from ...services.documents.document_service import document_service

router = APIRouter()

# Pydantic Models
class DocumentResponse(BaseModel):
    """Response model for documents"""
    id: str
    filename: str
    source_path: str
    chunks: int
    total_size: int
    upload_date: str
    status: str

class DocumentsListResponse(BaseModel):
    """Response model for document lists"""
    documents: List[DocumentResponse]
    total_count: int
    total_chunks: int

class DocumentDetailsResponse(BaseModel):
    """Response model for document details"""
    id: str
    filename: str
    chunks: int
    preview: str
    metadata: Dict[str, Any]

class SearchResult(BaseModel):
    """Search result model"""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str

class SearchResponse(BaseModel):
    """Response model for search results"""
    query: str
    results_count: int
    results: List[SearchResult]

# API Endpoints
@router.get("/", response_model=DocumentsListResponse)
async def get_documents(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get all documents with pagination"""
    try:
        result = await document_service.get_documents(
            limit=limit,
            offset=offset,
            db=db
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentDetailsResponse)
async def get_document_details(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get details for a specific document"""
    try:
        result = await document_service.get_document_details(
            document_id=document_id,
            db=db
        )
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document details: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its chunks"""
    try:
        result = await document_service.delete_document(
            document_id=document_id,
            db=db
        )
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """Search through documents using vector similarity"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        results = await document_service.search_documents(
            query=query,
            top_k=top_k,
            db=db
        )
        
        return SearchResponse(
            query=query,
            results_count=len(results),
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/upload-docs")
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload multiple documents for chat context"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types
        allowed_extensions = {".txt", ".md", ".pdf", ".docx", ".json"}
        for file in files:
            if not any(file.filename.endswith(ext) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not allowed: {file.filename}"
                )
        
        result = await document_service.upload_documents(
            files=files,
            db=db
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/stats")
async def get_document_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about documents"""
    try:
        stats = await document_service.get_stats(db=db)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")