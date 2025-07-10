"""
Fast Q&A Service - Document Search Only
No LLM processing, just intelligent document retrieval and formatting
"""
import logging
import asyncio
from typing import Dict, Any, List
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class FastQAService:
    """Ultra-fast Q&A service using only document search without LLM processing"""
    
    def __init__(self):
        self.rag_service = rag_service
        self.is_initialized = False
        logger.info("⚡ Fast Q&A Service initialized")
    
    async def initialize(self):
        """Initialize RAG service if needed"""
        try:
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            self.is_initialized = True
            logger.info("✅ Fast Q&A Service ready")
            
        except Exception as e:
            logger.error(f"❌ Fast Q&A Service initialization failed: {e}")
            raise
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using only document search and smart formatting
        
        Args:
            question: User question
            
        Returns:
            Dict with response and metadata
            
        Raises:
            Exception if no answer can be generated
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Search for relevant documents (should be very fast)
            documents = await asyncio.wait_for(
                self.rag_service.search_documents(query=question, top_k=3),
                timeout=2.0  # Very short timeout for document search
            )
            
            if not documents:
                raise Exception("Keine relevanten Dokumente zu Ihrer Frage gefunden")
            
            # Format documents into a structured response
            response = self._format_document_response(question, documents)
            
            total_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "response": response,
                "documents_used": len(documents),
                "processing_time": round(total_time, 2),
                "success": True,
                "method": "document_search_only"
            }
            
        except asyncio.TimeoutError:
            raise Exception("Dokumentensuche zu langsam")
        except Exception as e:
            logger.error(f"Fast Q&A error: {e}")
            raise
    
    def _format_document_response(self, question: str, documents: List[Any]) -> str:
        """Format documents into a structured response without LLM"""
        
        if not documents:
            return "Keine relevanten Informationen gefunden."
        
        # Extract key information from documents
        response_parts = ["## StreamWorks Information\n"]
        
        # Add question context
        question_lower = question.lower()
        
        for i, doc in enumerate(documents[:3], 1):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            
            # Get source info
            source = "Unbekannte Quelle"
            if hasattr(doc, 'metadata') and doc.metadata:
                source = doc.metadata.get('source', doc.metadata.get('filename', 'Unbekannte Quelle'))
            
            # Extract relevant excerpt (first 300 chars of content)
            excerpt = content[:300].strip()
            if len(content) > 300:
                excerpt += "..."
            
            response_parts.append(f"### Quelle {i}: {source}")
            response_parts.append(excerpt)
            response_parts.append("")  # Empty line
        
        # Add footer
        response_parts.append("---")
        response_parts.append("*Basierend auf StreamWorks-Dokumentation*")
        
        return "\n".join(response_parts)


# Global instance
fast_qa_service = FastQAService()