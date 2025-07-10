"""
Simple Q&A Service for StreamWorks Documentation
Focused on reliability and speed without fallbacks
"""
import logging
import asyncio
from typing import Dict, Any, List
from app.services.rag_service import rag_service
from app.services.mistral_llm_service import mistral_llm_service

logger = logging.getLogger(__name__)


class SimpleQAService:
    """Simple Q&A service without complex fallback mechanisms"""
    
    def __init__(self):
        self.rag_service = rag_service
        self.mistral_service = mistral_llm_service
        self.is_initialized = False
        logger.info("🎯 Simple Q&A Service initialized")
    
    async def initialize(self):
        """Initialize services if needed"""
        try:
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            if not self.mistral_service.is_initialized:
                await self.mistral_service.initialize(skip_warmup=True)
            
            self.is_initialized = True
            logger.info("✅ Simple Q&A Service ready")
            
        except Exception as e:
            logger.error(f"❌ Q&A Service initialization failed: {e}")
            raise
    
    async def answer_question(self, question: str, max_timeout: float = 10.0) -> Dict[str, Any]:
        """
        Answer a question using RAG + Mistral
        
        Args:
            question: User question
            max_timeout: Maximum time to wait for response (default 10s)
            
        Returns:
            Dict with response and metadata
            
        Raises:
            Exception if no answer can be generated
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Search for relevant documents (max 3 seconds)
            search_task = self.rag_service.search_documents(
                query=question,
                top_k=3  # Only top 3 documents
            )
            
            documents = await asyncio.wait_for(search_task, timeout=3.0)
            
            if not documents:
                raise Exception("Keine relevanten Dokumente gefunden")
            
            # Step 2: Build simple context
            context = self._build_simple_context(documents)
            
            # Step 3: Generate response with Mistral (max 7 seconds)
            prompt = f"""Kontext aus der StreamWorks-Dokumentation:
{context}

Frage: {question}

Bitte antworte präzise und auf Deutsch basierend auf dem gegebenen Kontext."""
            
            response_task = self.mistral_service.generate_german_response(
                user_message=question,
                context=context,
                fast_mode=True,
                use_cache=True
            )
            
            response = await asyncio.wait_for(response_task, timeout=7.0)
            
            total_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "response": response,
                "documents_used": len(documents),
                "processing_time": round(total_time, 2),
                "success": True
            }
            
        except asyncio.TimeoutError:
            raise Exception(f"Zeitüberschreitung nach {max_timeout} Sekunden")
        except Exception as e:
            logger.error(f"Q&A error: {e}")
            raise
    
    def _build_simple_context(self, documents: List[Any], max_length: int = 1500) -> str:
        """Build a simple context string from documents"""
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for doc in documents[:3]:  # Maximum 3 documents
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            
            # Truncate if too long
            if current_length + len(content) > max_length:
                remaining = max_length - current_length
                if remaining > 100:  # Only add if meaningful
                    context_parts.append(content[:remaining] + "...")
                break
            
            context_parts.append(content)
            current_length += len(content)
        
        return "\n\n".join(context_parts)


# Global instance
simple_qa_service = SimpleQAService()