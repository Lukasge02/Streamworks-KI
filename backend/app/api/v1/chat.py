"""
Chat API with Mistral 7B + RAG Integration
Optimiert für deutsche StreamWorks-Dokumentation mit robust input validation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Form
from pydantic import BaseModel, ValidationError as PydanticValidationError, Field
from typing import Optional, List
from enum import Enum
import logging
import time
import uuid
import asyncio
from datetime import datetime

from app.services.rag_service import rag_service
from app.services.mistral_rag_service import mistral_rag_service
from app.services.mistral_llm_service import mistral_llm_service
from app.services.xml_generator import xml_generator
from app.services.error_handler import error_handler
from app.services.citation_service import citation_service
from app.models.validation import ChatRequestValidator, ValidationErrorResponse, validate_request_size
from app.models.schemas import ChatResponseWithCitations, Citation, CitationSummary, ManualSourceCategory
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ChatMode enum removed - using dedicated endpoints instead

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

# DualMode models removed - using dedicated endpoints instead

class ChatResponse(BaseModel):
    response: str
    mode: str  # "mistral_rag", "mistral_llm", "fallback"
    conversation_id: Optional[str] = None
    sources_used: int = 0
    llm_model: Optional[str] = None
    processing_time: float = 0.0

# DualModeChatResponse removed - using dedicated endpoints instead

class DocumentUploadRequest(BaseModel):
    source_category: ManualSourceCategory = Field(..., description="Manual source category")
    description: Optional[str] = Field(None, description="Optional description for the documents")

class DocumentUploadResponse(BaseModel):
    message: str
    documents_added: int
    chunks_created: int
    source_category: str = Field(..., description="Applied source category")

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
async def chat_with_mistral(request: ChatRequestValidator, raw_request: Request):
    """Robust Chat Endpoint mit vollständiger Input-Validierung und Error Handling"""
    
    start_time = time.time()
    
    try:
        # Request size validation
        content_length = raw_request.headers.get("content-length")
        if content_length and not validate_request_size(int(content_length)):
            raise HTTPException(
                status_code=413,
                detail="Request too large. Maximum size is 10MB."
            )
        
        logger.info(f"📨 Validated Chat Request: {request.message[:50]}...")
        
        # Input validation already handled by Pydantic model
        # Additional safety checks
        if len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty after validation"
            )
        
        # Rate limiting check (simple per-request)
        if len(request.message) > 3500:  # Conservative limit
            logger.warning(f"⚠️ Large message received: {len(request.message)} chars")
        
        # Conversation ID generieren oder verwenden
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Conversation Memory importieren und Kontext laden
        try:
            from app.services.conversation_memory import conversation_memory
            conversation_context = conversation_memory.get_context(conversation_id)
            
            # Erweitere Nachricht um Konversations-Kontext
            enhanced_message = request.message
            if conversation_context:
                enhanced_message = f"{conversation_context}\n\nAktuelle Frage: {request.message}"
                logger.info(f"💬 Konversations-Kontext geladen ({len(conversation_context)} Zeichen)")
            
        except Exception as e:
            logger.warning(f"⚠️ Conversation Memory nicht verfügbar: {e}")
            enhanced_message = request.message
            conversation_context = ""
        
        # RAG-Antwort mit Mistral + Citations (mit Kontext)
        try:
            import asyncio
            # Add timeout to prevent hanging requests
            rag_result = await asyncio.wait_for(
                mistral_rag_service.generate_response(enhanced_message),
                timeout=settings.CHAT_TIMEOUT_SECONDS if hasattr(settings, 'CHAT_TIMEOUT_SECONDS') else 30.0
            )
            response = rag_result.get("response")
            if not response:
                raise Exception("Keine Antwort vom System erhalten")
            sources_used = rag_result.get("sources_used", 0)
        except asyncio.TimeoutError:
            logger.error(f"❌ Chat request timed out after {settings.CHAT_TIMEOUT_SECONDS if hasattr(settings, 'CHAT_TIMEOUT_SECONDS') else 30}s")
            raise HTTPException(
                status_code=504,
                detail="Die Anfrage hat zu lange gedauert. Das System konnte keine Antwort generieren."
            )
        
        # Speichere Konversation in Memory
        try:
            from app.services.conversation_memory import conversation_memory
            conversation_memory.add_message(
                session_id=conversation_id,
                question=request.message,  # Original-Frage ohne Kontext
                answer=response,
                metadata={
                    "llm_model": "mistral:7b-instruct",
                    "mode": "mistral_rag_with_citations",
                    "sources_used": sources_used,
                    "context_used": bool(conversation_context),
                    "processing_time": time.time() - start_time
                }
            )
            logger.info(f"💾 Konversation gespeichert: {conversation_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Konversation konnte nicht gespeichert werden: {e}")
        
        # Performance-Logging
        process_time = time.time() - start_time
        logger.info(f"🚀 Mistral response generated in {process_time:.2f}s")
        
        return ChatResponse(
            response=response,
            mode="mistral_rag_with_citations",
            conversation_id=conversation_id,
            sources_used=sources_used,
            llm_model="mistral:7b-instruct",
            processing_time=process_time
        )
        
    except PydanticValidationError as ve:
        logger.warning(f"📝 Validation error: {ve}")
        # Return specific validation error
        raise HTTPException(
            status_code=422,
            detail=f"Input validation failed: {str(ve)}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (they're already handled)
        raise
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        
        # Don't use fallback - just raise error
        raise HTTPException(
            status_code=500,
            detail=f"Systemfehler: {str(e)}"
        )

@router.post("/dual-mode")
async def dual_mode_redirect(request: dict):
    """Temporary redirect for frontend compatibility - redirects to smart Q&A"""
    from fastapi import HTTPException
    
    # Extract message from request
    message = request.get("message", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Redirect to smart Q&A endpoint
    from app.services.intelligent_qa_service import intelligent_qa_service
    
    try:
        result = await intelligent_qa_service.answer_question(message)
        
        # Format response to match expected dual-mode format
        return {
            "response": result["response"],
            "mode_used": "smart_qa",
            "processing_time": result["processing_time"],
            "metadata": {
                "intent": result.get("intent", "unknown"),
                "documents_used": result["documents_used"],
                "redirected_from": "dual_mode"
            },
            "sources": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Q&A service error: {str(e)}"
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
async def upload_documents(
    files: List[UploadFile] = File(...),
    source_category: ManualSourceCategory = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload documents to RAG vector database with manual source categorization"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        logger.info(f"📁 Uploading {len(files)} documents to RAG with category: {source_category.value}")
        
        from langchain.docstore.document import Document
        
        documents = []
        
        # Map manual categories to SourceType
        category_mapping = {
            ManualSourceCategory.TESTDATEN: "Documentation",
            ManualSourceCategory.STREAMWORKS_HILFE: "StreamWorks", 
            ManualSourceCategory.SHAREPOINT: "SharePoint"
        }
        
        mapped_source_type = category_mapping[source_category]
        
        for file in files:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Create document with manual source categorization
            doc = Document(
                page_content=text_content,
                metadata={
                    "filename": file.filename,
                    "type": "uploaded_document",
                    "size": len(content),
                    "manual_source_category": source_category.value,
                    "source_type": mapped_source_type,
                    "description": description or f"Uploaded from {source_category.value}",
                    "upload_timestamp": datetime.now().isoformat()
                }
            )
            documents.append(doc)
        
        # Add to RAG
        chunks_created = await rag_service.add_documents(documents)
        
        logger.info(f"✅ Successfully uploaded {len(documents)} documents from {source_category.value}")
        
        return DocumentUploadResponse(
            message=f"Successfully uploaded {len(documents)} documents from {source_category.value}",
            documents_added=len(documents),
            chunks_created=chunks_created,
            source_category=source_category.value
        )
        
    except Exception as e:
        logger.error(f"❌ Document Upload Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )

@router.post("/upload-docs-form", response_model=DocumentUploadResponse)
async def upload_documents_form(
    files: List[UploadFile] = File(...),
    source_category: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload documents with form-based source categorization (easier for frontend)"""
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(status_code=503, detail="RAG Service is disabled")
        
        # Validate and convert source_category
        try:
            category = ManualSourceCategory(source_category)
        except ValueError:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid source_category. Must be one of: {[c.value for c in ManualSourceCategory]}"
            )
        
        logger.info(f"📁 Form upload: {len(files)} documents as {category.value}")
        
        from langchain.docstore.document import Document
        
        documents = []
        
        # Map manual categories to SourceType
        category_mapping = {
            ManualSourceCategory.TESTDATEN: "Documentation",
            ManualSourceCategory.STREAMWORKS_HILFE: "StreamWorks", 
            ManualSourceCategory.SHAREPOINT: "SharePoint"
        }
        
        mapped_source_type = category_mapping[category]
        
        for file in files:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Create document with manual source categorization
            doc = Document(
                page_content=text_content,
                metadata={
                    "filename": file.filename,
                    "type": "uploaded_document",
                    "size": len(content),
                    "manual_source_category": category.value,
                    "source_type": mapped_source_type,
                    "description": description or f"Uploaded from {category.value}",
                    "upload_timestamp": datetime.now().isoformat()
                }
            )
            documents.append(doc)
        
        # Add to RAG
        chunks_created = await rag_service.add_documents(documents)
        
        logger.info(f"✅ Form upload successful: {len(documents)} documents from {category.value}")
        
        return DocumentUploadResponse(
            message=f"Successfully uploaded {len(documents)} documents from {category.value}",
            documents_added=len(documents),
            chunks_created=chunks_created,
            source_category=category.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Form Upload Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )

@router.get("/source-categories")
async def get_source_categories():
    """Get available source categories for manual upload"""
    return {
        "categories": [
            {
                "value": category.value,
                "description": f"Dokumente aus {category.value}",
                "example": f"Beispiel: Interne {category.value} Dokumentation"
            }
            for category in ManualSourceCategory
        ],
        "usage": {
            "form_endpoint": "/api/v1/chat/upload-docs-form",
            "json_endpoint": "/api/v1/chat/upload-docs",
            "example_curl": """curl -X POST "http://localhost:8000/api/v1/chat/upload-docs-form" \\
  -H "accept: application/json" \\
  -F "files=@document.txt" \\
  -F "source_category=StreamWorks Hilfe" \\
  -F "description=Optionale Beschreibung\""""
        }
    }

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
        
        # Convert dict objects to DocumentInfo objects
        document_infos = [
            DocumentInfo(
                id=doc.get("id", ""),
                filename=doc.get("filename", ""),
                source_path=doc.get("source_path", ""),
                chunks=doc.get("chunks", 0),
                total_size=doc.get("total_size", 0),
                upload_date=doc.get("upload_date"),
                status=doc.get("status", "indexed")
            )
            for doc in documents
        ]
        
        return DocumentsResponse(
            documents=document_infos,
            total_count=len(document_infos),
            total_chunks=sum(doc.chunks for doc in document_infos)
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

@router.post("/chat-with-citations", response_model=ChatResponseWithCitations)
async def chat_with_citations(request: ChatRequestValidator, raw_request: Request):
    """Enhanced Chat with Multi-Source Citations"""
    
    start_time = time.time()
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        # Request size validation
        content_length = raw_request.headers.get("content-length")
        if content_length and not validate_request_size(int(content_length)):
            raise HTTPException(
                status_code=413,
                detail="Request too large. Maximum size is 10MB."
            )
        
        logger.info(f"🔗 Citation Chat Request: {request.message[:100]}...")
        
        # Get documents with citations
        search_result = await rag_service.search_documents_with_citations(
            query=request.message,
            top_k=settings.RAG_TOP_K,
            include_citations=True
        )
        
        documents = search_result["documents"]
        citations = search_result["citations"] or []
        citation_summary = search_result["citation_summary"]
        
        if not documents:
            # No relevant documents found
            response_text = "Entschuldigung, ich konnte keine relevanten Informationen zu Ihrer Frage finden. Könnten Sie die Frage anders formulieren?"
            citations = []
            citation_summary = CitationSummary(
                total_citations=0,
                source_breakdown={},
                highest_relevance=0.0,
                coverage_score=0.0
            )
        else:
            # PERFORMANCE OPTIMIZED: Generate response using Mistral with RAG
            try:
                rag_result = await asyncio.wait_for(
                    mistral_rag_service.generate_response(
                        question=request.message,
                        documents=documents,
                        fast_mode=True  # Enable fast mode for better performance
                    ),
                    timeout=settings.CHAT_TIMEOUT_SECONDS if hasattr(settings, 'CHAT_TIMEOUT_SECONDS') else 20.0
                )
                
                response_text = rag_result.get("response", "Keine Antwort generiert.")
            except asyncio.TimeoutError:
                logger.error("Chat response timeout - using fallback")
                response_text = "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es mit einer einfacheren Frage erneut."
            
            # Add citation information to response
            if citations:
                citation_text = citation_service.format_citations_for_response(citations)
                response_text += citation_text
        
        processing_time = time.time() - start_time
        
        # Save to conversation memory if available
        try:
            from app.services.conversation_memory import conversation_memory
            conversation_memory.add_message(
                session_id=conversation_id,
                question=request.message,
                answer=response_text,
                metadata={
                    "citations_count": len(citations),
                    "coverage_score": citation_summary.coverage_score if citation_summary else 0.0,
                    "processing_time": processing_time,
                    "sources_used": len(set(c.filename for c in citations))
                }
            )
        except Exception as save_error:
            logger.warning(f"Could not save to conversation memory: {save_error}")
        
        return ChatResponseWithCitations(
            response=response_text,
            citations=citations,
            citation_summary=citation_summary or CitationSummary(
                total_citations=0,
                source_breakdown={},
                highest_relevance=0.0,
                coverage_score=0.0
            ),
            conversation_id=conversation_id,
            timestamp=datetime.fromtimestamp(time.time()),
            response_quality=citation_summary.coverage_score if citation_summary else 0.0
        )
        
    except Exception as e:
        logger.error(f"❌ Citation Chat Error: {str(e)}")
        
        # Fallback without citations
        try:
            fallback_response = await error_handler.handle_rag_error(e, {
                "query": request.message,
                "context": "citation_chat"
            })
            
            processing_time = time.time() - start_time
            
            return ChatResponseWithCitations(
                response=fallback_response.message,
                citations=[],
                citation_summary=CitationSummary(
                    total_citations=0,
                    source_breakdown={},
                    highest_relevance=0.0,
                    coverage_score=0.0
                ),
                conversation_id=conversation_id,
                timestamp=datetime.fromtimestamp(time.time()),
                response_quality=0.0
            )
            
        except Exception as fallback_error:
            logger.error(f"❌ Citation fallback failed: {fallback_error}")
            raise HTTPException(
                status_code=500,
                detail="Chat service temporarily unavailable"
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