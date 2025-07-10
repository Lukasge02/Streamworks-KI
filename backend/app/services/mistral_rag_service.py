"""
Mistral RAG Service - ChromaDB + Mistral 7B Integration
Optimiert für deutsche StreamWorks-Dokumentation mit Citations
PERFORMANCE OPTIMIZED VERSION
"""
import logging
import asyncio
from typing import List, Dict, Any
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.mistral_llm_service import mistral_llm_service
from app.services.citation_service import citation_service

logger = logging.getLogger(__name__)

class MistralRAGService:
    """RAG Service optimiert für Mistral 7B mit Citation Support - PERFORMANCE EDITION"""
    
    def __init__(self):
        self.rag_service = None
        self.mistral_service = mistral_llm_service
        self.is_initialized = False
        
        logger.info("🔍 Mistral RAG Service (OPTIMIZED) initialisiert")
    
    async def initialize(self):
        """Initialisiere RAG + Mistral Services mit Performance-Optimierung"""
        try:
            # RAG Service initialisieren
            from app.services.rag_service import rag_service
            self.rag_service = rag_service
            
            if not self.rag_service.is_initialized:
                await asyncio.wait_for(self.rag_service.initialize(), timeout=15.0)
            
            # Mistral Service mit schneller Initialisierung
            if not self.mistral_service.is_initialized:
                await self.mistral_service.initialize(skip_warmup=True)  # Fast startup
            
            self.is_initialized = True
            logger.info("✅ Mistral RAG Service erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Mistral RAG Service Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
    
    async def search_for_mistral(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Optimierte Dokumentensuche für Mistral's Context Window"""
        
        if not self.rag_service or not self.rag_service.is_initialized:
            logger.warning("RAG Service nicht verfügbar")
            return []
        
        try:
            # Normale Dokumentensuche mit Timeout
            docs = await asyncio.wait_for(
                self.rag_service.search_documents(query, top_k),
                timeout=8.0
            )
            
            if not docs:
                logger.info(f"Keine Dokumente für Query gefunden: {query}")
                return []
            
            # Konvertiere zu Mistral-Format
            context_docs = []
            for i, doc in enumerate(docs):
                # Nutze distance als relevance score
                relevance = 1.0 - (i * 0.1)  # 1.0, 0.9, 0.8, etc.
                
                context_docs.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', doc.metadata.get('filename', 'unknown')),
                    'relevance': max(0.1, relevance)  # Minimum 0.1
                })
            
            return context_docs
            
        except Exception as e:
            logger.error(f"Fehler bei Dokumentensuche: {e}")
            return []
    
    async def generate_response(self, question: str, documents: List = None, fast_mode: bool = True) -> Dict[str, Any]:
        """Generate response with citations - PERFORMANCE OPTIMIZED"""
        
        # Quick initialization check
        if not self.is_initialized:
            try:
                await asyncio.wait_for(self.initialize(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.error("RAG service initialization timeout")
                raise Exception("Service nicht verfügbar")
        
        if not self.is_initialized:
            raise Exception("RAG Service ist nicht initialisiert. Das System kann keine Antworten generieren.")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # OPTIMIZED: Concurrent document processing with reduced scope
            if documents:
                citations = await citation_service.create_citations_from_documents(documents, question)
                context = self._build_context_from_documents(documents, citations)
                sources_used = len(set(c.filename for c in citations))
            else:
                # Fast document search with timeout
                search_task = asyncio.create_task(
                    self.rag_service.search_documents_with_citations(
                        query=question,
                        top_k=3  # Reduced for speed
                    )
                )
                
                try:
                    search_result = await asyncio.wait_for(search_task, timeout=3.0)  # Faster timeout
                    documents = search_result.get("documents", [])
                    citations = search_result.get("citations", [])
                    context = search_result.get("context", "")
                    sources_used = len(set(c.filename for c in citations)) if citations else 0
                    
                    if not documents:
                        raise Exception("Keine relevanten Dokumente gefunden")
                        
                except asyncio.TimeoutError:
                    logger.error("Document search timeout")
                    raise Exception("Dokumentensuche zu langsam")
            
            # PERFORMANCE CRITICAL: Fast Mistral response generation (optimized)
            try:
                mistral_response = await asyncio.wait_for(
                    self.mistral_service.generate_german_response(
                        user_message=question,
                        context=context,
                        fast_mode=True,  # Always use fast mode
                        use_cache=True   # Enable caching for better performance
                    ),
                    timeout=10.0  # Much more aggressive timeout
                )
            except asyncio.TimeoutError:
                logger.error("Mistral response timeout")
                raise asyncio.TimeoutError("Die Anfrage hat zu lange gedauert. Das System konnte keine Antwort generieren.")
            
            # Performance tracking
            total_time = asyncio.get_event_loop().time() - start_time
            
            if total_time > 8.0:
                logger.warning(f"Slow RAG response: {total_time:.2f}s")
            
            return {
                "response": mistral_response,
                "citations": citations if citations else [],
                "sources_used": sources_used,
                "performance_mode": "optimized",
                "response_time": round(total_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            raise Exception(f"Fehler beim Generieren der Antwort: {str(e)}")
    
    
    def _build_context_from_documents(self, documents: List, citations: List, max_tokens: int = 2000) -> str:
        """Build optimized context string - reduced for performance"""
        if not documents:
            raise Exception("Keine relevanten Dokumente gefunden. Das System kann keine Antwort generieren.")
        
        context_parts = []
        current_length = 0
        
        # Limit to first 2 documents for performance
        for i, doc in enumerate(documents[:2]):
            doc_tokens = len(doc.page_content) // 4
            
            if current_length + doc_tokens > max_tokens:
                break
            
            # Simplified context formatting for speed
            content_snippet = doc.page_content[:600]  # Reduced content
            context_part = f"=== QUELLE {i+1} ===\n{content_snippet}\n"
            context_parts.append(context_part)
            current_length += doc_tokens
        
        if not context_parts:
            raise Exception("Keine passenden Dokumente gefunden. Das System kann keine Antwort generieren.")
        return "\n".join(context_parts)
    
    async def answer_with_mistral_rag(self, question: str) -> str:
        """RAG-Antwort mit Mistral 7B - LEGACY COMPATIBILITY"""
        result = await self.generate_response(question, fast_mode=True)
        return result.get("response", "Keine Antwort verfügbar.")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Service Statistiken"""
        rag_stats = {}
        if self.rag_service:
            try:
                rag_stats = await self.rag_service.get_stats()
            except:
                rag_stats = {"status": "error"}
        
        mistral_stats = await self.mistral_service.get_stats()
        
        return {
            "service": "mistral_rag_optimized",
            "is_initialized": self.is_initialized,
            "rag_service": rag_stats,
            "mistral_service": mistral_stats,
            "performance_mode": "high_speed",
            "optimization_level": "maximum"
        }

# Global instance
mistral_rag_service = MistralRAGService()