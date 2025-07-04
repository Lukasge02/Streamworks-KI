"""
Chat API with Mistral 7B + RAG Integration
Optimiert für deutsche StreamWorks-Dokumentation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import logging
import time

from app.services.rag_service import rag_service
from app.services.mistral_rag_service import mistral_rag_service
from app.services.mistral_llm_service import mistral_llm_service
from app.services.xml_generator import xml_generator
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMode(str, Enum):
    QA = "qa"
    XML_GENERATOR = "xml_generator"

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class DualModeChatRequest(BaseModel):
    message: str
    mode: ChatMode = ChatMode.QA
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mode: str  # "mistral_rag", "mistral_llm", "fallback"
    conversation_id: Optional[str] = None
    sources_used: int = 0
    model_used: Optional[str] = None
    processing_time: float = 0.0

class DualModeChatResponse(BaseModel):
    response: str
    mode_used: str
    processing_time: float
    metadata: dict
    sources: Optional[List[str]] = None

class DocumentUploadResponse(BaseModel):
    message: str
    documents_added: int
    chunks_created: int

class DocumentInfo(BaseModel):
    id: str
    filename: str
    source_path: str
    chunks: int
    total_size: int
    upload_date: Optional[str] = None
    status: str = "indexed"

class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int
    total_chunks: int

class DocumentDetailsResponse(BaseModel):
    id: str
    filename: str
    chunks: int
    preview: str
    metadata: dict

class SearchDocumentsResponse(BaseModel):
    query: str
    results_count: int
    results: List[dict]

class DeleteDocumentResponse(BaseModel):
    success: bool
    message: str

@router.post("/", response_model=ChatResponse)
async def chat_with_mistral(request: ChatRequest):
    """Optimierter Chat für Mistral 7B + RAG"""
    
    start_time = time.time()
    
    try:
        logger.info(f"📨 Mistral Chat Request: {request.message[:50]}...")
        
        # RAG-Antwort mit Mistral
        response = await mistral_rag_service.answer_with_mistral_rag(request.message)
        
        # Performance-Logging
        process_time = time.time() - start_time
        logger.info(f"🚀 Mistral response generated in {process_time:.2f}s")
        
        return ChatResponse(
            response=response,
            mode="mistral_rag",
            conversation_id=request.conversation_id,
            sources_used=0,  # TODO: Track sources from RAG
            model_used="mistral:7b-instruct",
            processing_time=process_time
        )
        
    except Exception as e:
        logger.error(f"❌ Mistral chat error: {e}")
        process_time = time.time() - start_time
        
        return ChatResponse(
            response="Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
            mode="error_fallback",
            conversation_id=request.conversation_id,
            sources_used=0,
            model_used="mistral:7b-instruct",
            processing_time=process_time
        )

@router.post("/dual-mode", response_model=DualModeChatResponse)
async def dual_mode_chat(request: DualModeChatRequest):
    """Dual-Mode Chat mit Mode-Selection für Q&A und XML Generation"""
    
    start_time = time.time()
    
    try:
        logger.info(f"🤖 Dual-Mode Chat Request: {request.mode.value} - {request.message[:50]}...")
        
        if request.mode == ChatMode.QA:
            # Nutze optimierten RAG Service für Q&A
            result = await rag_service.query(request.message)
            
            response = DualModeChatResponse(
                response=result["answer"],
                mode_used="qa",
                processing_time=time.time() - start_time,
                metadata={"confidence": result.get("confidence", 0.9), "model": "rag_service"},
                sources=result.get("sources", [])
            )
            
        elif request.mode == ChatMode.XML_GENERATOR:
            # Extrahiere XML-Anforderungen aus User-Message
            xml_requirements = extract_xml_requirements(request.message)
            
            # Nutze bestehenden XML Generator Service
            xml_content = await xml_generator.generate_xml_stream(xml_requirements)
            
            response = DualModeChatResponse(
                response=f"```xml\n{xml_content}\n```",
                mode_used="xml_generator",
                processing_time=time.time() - start_time,
                metadata={"xml_valid": True, "requirements": xml_requirements},
                sources=None
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported mode: {request.mode}")
            
        logger.info(f"✅ Dual-Mode response generated in {response.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"❌ Dual-Mode chat error: {e}")
        process_time = time.time() - start_time
        
        return DualModeChatResponse(
            response="Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
            mode_used="error_fallback",
            processing_time=process_time,
            metadata={"error": str(e)},
            sources=None
        )

def extract_xml_requirements(message: str) -> dict:
    """Extrahiere XML-Anforderungen aus User-Message"""
    # Einfache Keyword-Extraktion (später durch LLM erweitern)
    requirements = {
        "name": "DataProcessing",
        "description": message,
        "schedule": "daily",
        "source": "/data/input",
        "target": "/data/output"
    }
    
    # Keyword-basierte Extraktion
    message_lower = message.lower()
    
    # Schedule extraction
    if "stündlich" in message_lower or "hourly" in message_lower or "jede stunde" in message_lower:
        requirements["schedule"] = "hourly"
    elif "wöchentlich" in message_lower or "weekly" in message_lower or "jede woche" in message_lower:
        requirements["schedule"] = "weekly"
    elif "täglich" in message_lower or "daily" in message_lower or "jeden tag" in message_lower:
        requirements["schedule"] = "daily"
    
    # Simple name extraction
    if "import" in message_lower:
        requirements["name"] = "DataImport"
    elif "export" in message_lower:
        requirements["name"] = "DataExport"
    elif "transformation" in message_lower or "transform" in message_lower:
        requirements["name"] = "DataTransformation"
    elif "backup" in message_lower:
        requirements["name"] = "DataBackup"
    
    # Source/Target hints
    if "csv" in message_lower:
        requirements["source"] = "/data/csv"
        requirements["target"] = "/processed/csv"
    elif "database" in message_lower or "db" in message_lower:
        requirements["source"] = "/data/database"
        requirements["target"] = "/processed/database"
    
    return requirements

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

async def _is_knowledge_question(message: str) -> bool:
    """Determine if message is a knowledge-based question suitable for RAG"""
    knowledge_keywords = [
        "was", "wie", "wo", "wann", "warum", "welche",
        "what", "how", "where", "when", "why", "which",
        "xml", "stream", "api", "config", "schedule",
        "dokumentation", "hilfe", "help", "erklär", "zeig"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in knowledge_keywords)

def _build_context_from_docs(documents: List) -> str:
    """Build context string from relevant documents"""
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get('filename', 'Unbekannt')
        content = doc.page_content.strip()
        
        # Limit content length per document
        if len(content) > 500:
            content = content[:500] + "..."
        
        context_parts.append(f"[Quelle {i}: {source}]\n{content}")
    
    return "\n\n".join(context_parts)

def _generate_fallback_response(message: str) -> str:
    """Generate fallback response when all systems fail"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hallo", "hi", "hey", "guten tag"]):
        return "👋 Hallo! Ich bin SKI, deine StreamWorks-KI. Wie kann ich dir heute helfen?"
    
    elif any(word in message_lower for word in ["xml", "stream"]):
        return "🔧 Für XML-Stream-Erstellung verwende den **Stream Generator** Tab. Dort kannst du interaktiv Streams konfigurieren!"
    
    elif any(word in message_lower for word in ["hilfe", "help"]):
        return "💡 Ich helfe gerne! Du kannst mich fragen zu:\n\n• StreamWorks Dokumentation\n• XML-Stream Erstellung\n• API Verwendung\n• Konfiguration\n\nWas interessiert dich?"
    
    else:
        return f"🤔 Entschuldigung, ich konnte '{message}' nicht verstehen. Versuche eine spezifischere Frage oder nutze die anderen Tabs für weitere Features."

@router.get("/mistral-status")
async def get_mistral_status():
    """Mistral-spezifischer Status"""
    
    try:
        # Teste Mistral-Verfügbarkeit
        test_response = await mistral_llm_service.generate_german_response(
            user_message="Test",
            context=""
        )
        
        # Get service stats
        mistral_stats = await mistral_llm_service.get_stats()
        rag_stats = await mistral_rag_service.get_stats()
        
        return {
            "model": "mistral:7b-instruct",
            "status": "ready",
            "test_response_length": len(test_response),
            "german_optimization": True,
            "mistral_service": mistral_stats,
            "rag_service": rag_stats,
            "performance": {
                "temperature": settings.MODEL_TEMPERATURE,
                "top_p": settings.MODEL_TOP_P,
                "top_k": settings.MODEL_TOP_K,
                "max_tokens": settings.MODEL_MAX_TOKENS,
                "context_window": settings.MODEL_CONTEXT_WINDOW
            }
        }
        
    except Exception as e:
        return {
            "model": "mistral:7b-instruct", 
            "status": "error",
            "error": str(e),
            "german_optimization": False
        }

@router.get("/llm-health")
async def llm_health():
    """Health check for LLM Service (Legacy)"""
    try:
        mistral_stats = await mistral_llm_service.get_stats()
        
        return {
            "status": "healthy",
            "service": "mistral_llm", 
            "llm_enabled": settings.LLM_ENABLED,
            "llm_stats": mistral_stats
        }
        
    except Exception as e:
        logger.error(f"❌ LLM Health Check Error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/documents", response_model=DocumentsResponse)
async def list_documents():
    """List all indexed documents in the vector database"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        documents = await rag_service.get_all_documents()
        
        return DocumentsResponse(
            documents=documents,
            total_count=len(documents),
            total_chunks=sum(doc.chunks for doc in documents)
        )
        
    except Exception as e:
        logger.error(f"❌ List Documents Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )

@router.get("/documents/{doc_id}", response_model=DocumentDetailsResponse)
async def get_document_details(doc_id: str):
    """Get detailed information about a specific document"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        details = await rag_service.get_document_details(doc_id)
        
        return DocumentDetailsResponse(
            id=details["id"],
            filename=details["filename"],
            chunks=details["chunks"],
            preview=details["preview"],
            metadata=details["metadata"]
        )
        
    except Exception as e:
        logger.error(f"❌ Get Document Details Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get document details: {str(e)}"
        )

@router.delete("/documents/{doc_id}", response_model=DeleteDocumentResponse)
async def delete_document(doc_id: str):
    """Delete a document from the vector database"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        success = await rag_service.delete_document(doc_id)
        
        if success:
            return DeleteDocumentResponse(
                success=True,
                message=f"Document {doc_id} deleted successfully"
            )
        else:
            return DeleteDocumentResponse(
                success=False,
                message=f"Document {doc_id} not found or could not be deleted"
            )
        
    except Exception as e:
        logger.error(f"❌ Delete Document Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.get("/documents/search", response_model=SearchDocumentsResponse)
async def search_documents_endpoint(query: str, top_k: int = 5):
    """Search for documents based on query (enhanced version of /search)"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        documents = await rag_service.search_documents(query, top_k)
        
        results = []
        for doc in documents:
            results.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, 'score', None),
                "source": doc.metadata.get('source', 'unknown')
            })
        
        return SearchDocumentsResponse(
            query=query,
            results_count=len(results),
            results=results
        )
        
    except Exception as e:
        logger.error(f"❌ Search Documents Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document search failed: {str(e)}"
        )

@router.post("/test")
async def test_simple():
    """Simple test endpoint"""
    return {
        "message": "StreamWorks-KI Hybrid Chat Service is working!",
        "rag_enabled": settings.RAG_ENABLED,
        "llm_enabled": settings.LLM_ENABLED,
        "timestamp": "2025-07-04T02:00:00Z"
    }