"""
Chat API with RAG-based Q&A System
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.services.rag_service import rag_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mode: str  # "rag", "fallback"
    conversation_id: Optional[str] = None
    sources_used: int = 0

class DocumentUploadResponse(BaseModel):
    message: str
    documents_added: int
    chunks_created: int

@router.post("/", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """Chat using RAG-based Q&A System"""
    try:
        logger.info(f"📨 RAG Chat Request: {request.message[:50]}...")
        
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        # Generate response using RAG
        response = await rag_service.answer_question(request.message)
        
        # Determine mode based on response
        mode = "rag" if "Basierend auf" in response else "fallback"
        
        logger.info(f"✅ RAG Response generated (mode: {mode})")
        
        return ChatResponse(
            response=response,
            mode=mode,
            conversation_id=request.conversation_id,
            sources_used=settings.RAG_TOP_K if mode == "rag" else 0
        )
        
    except Exception as e:
        logger.error(f"❌ RAG Chat Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Chat service error: {str(e)}"
        )

@router.post("/upload-docs", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to RAG vector database"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        logger.info(f"📁 Uploading {len(files)} documents to RAG")
        
        from langchain.docstore.document import Document
        
        documents = []
        
        for file in files:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Create document
            doc = Document(
                page_content=text_content,
                metadata={
                    "filename": file.filename,
                    "type": "uploaded_document",
                    "size": len(content)
                }
            )
            documents.append(doc)
        
        # Add to RAG
        chunks_created = await rag_service.add_documents(documents)
        
        logger.info(f"✅ Successfully uploaded {len(documents)} documents")
        
        return DocumentUploadResponse(
            message=f"Successfully uploaded {len(documents)} documents",
            documents_added=len(documents),
            chunks_created=chunks_created
        )
        
    except Exception as e:
        logger.error(f"❌ Document Upload Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )

@router.get("/health")
async def chat_health():
    """Health check for RAG Chat Service"""
    try:
        rag_stats = await rag_service.get_stats()
        
        return {
            "status": "healthy",
            "service": "rag_chat",
            "rag_enabled": settings.RAG_ENABLED,
            "rag_stats": rag_stats,
            "embedding_model": settings.EMBEDDING_MODEL,
            "vector_db_path": settings.VECTOR_DB_PATH
        }
        
    except Exception as e:
        logger.error(f"❌ Health Check Error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/search")
async def search_documents(query: str, top_k: int = 5):
    """Search documents in vector database (dev endpoint)"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        documents = await rag_service.search_documents(query, top_k)
        
        results = []
        for doc in documents:
            results.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, 'score', None)
            })
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Search Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.post("/initialize-rag")
async def initialize_rag():
    """Initialize RAG service (dev endpoint)"""
    try:
        await rag_service.initialize()
        stats = await rag_service.get_stats()
        
        return {
            "message": "RAG Service initialized successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ RAG Initialization Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG initialization failed: {str(e)}"
        )

@router.post("/test")
async def test_simple():
    """Simple test endpoint"""
    return {
        "message": "StreamWorks-KI RAG Chat Service is working!",
        "rag_enabled": settings.RAG_ENABLED,
        "timestamp": "2025-07-04T01:30:00Z"
    }