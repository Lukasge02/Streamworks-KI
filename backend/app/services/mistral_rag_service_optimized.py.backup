"""
Mistral RAG Service - PERFORMANCE OPTIMIZED Version
ChromaDB + Mistral 7B Integration mit verbesserter Performance
"""
import logging
import asyncio
from typing import List, Dict, Any
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.mistral_llm_service import mistral_llm_service
from app.services.citation_service import citation_service

logger = logging.getLogger(__name__)

class MistralRAGServiceOptimized:
    """RAG Service optimiert für Mistral 7B mit Citations - PERFORMANCE EDITION"""
    
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
            logger.info("✅ Mistral RAG Service (OPTIMIZED) erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Mistral RAG Service Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
    
    async def generate_response(self, question: str, documents: List = None, fast_mode: bool = True) -> Dict[str, Any]:
        """Generate response with citations - PERFORMANCE OPTIMIZED"""
        
        # Quick fallback check
        if not self.is_initialized:
            try:
                await asyncio.wait_for(self.initialize(), timeout=8.0)
            except asyncio.TimeoutError:
                logger.warning("RAG service initialization timeout - using fallback")
        
        if not self.is_initialized:
            return {
                "response": self._get_quick_fallback_response(question),
                "citations": [],
                "sources_used": 0,
                "performance_mode": "fallback"
            }
        
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
                    search_result = await asyncio.wait_for(search_task, timeout=6.0)
                    documents = search_result.get("documents", [])
                    citations = search_result.get("citations", [])
                    context = search_result.get("context", "")
                    sources_used = len(set(c.filename for c in citations))
                except asyncio.TimeoutError:
                    logger.warning("Document search timeout - using fallback")
                    return {
                        "response": self._get_quick_fallback_response(question),
                        "citations": [],
                        "sources_used": 0,
                        "performance_mode": "search_timeout"
                    }
            
            # PERFORMANCE CRITICAL: Fast Mistral response generation
            try:
                mistral_response = await asyncio.wait_for(
                    self.mistral_service.generate_german_response(
                        user_message=question,
                        context=context,
                        fast_mode=True  # Always use fast mode
                    ),
                    timeout=15.0  # Aggressive timeout
                )
            except asyncio.TimeoutError:
                logger.error("Mistral response timeout - using fallback")
                mistral_response = self._get_quick_fallback_response(question)
            
            # Performance tracking
            total_time = asyncio.get_event_loop().time() - start_time
            
            if total_time > 8.0:
                logger.warning(f"Slow RAG response: {total_time:.2f}s")
            
            return {
                "response": mistral_response,
                "citations": citations,
                "sources_used": sources_used,
                "performance_mode": "optimized",
                "response_time": round(total_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "response": self._get_quick_fallback_response(question),
                "citations": [],
                "sources_used": 0,
                "performance_mode": "error_fallback",
                "error": str(e)
            }
    
    def _get_quick_fallback_response(self, question: str) -> str:
        """Schnelle Fallback-Antwort ohne LLM-Aufruf"""
        question_lower = question.lower()
        
        if "streamworks" in question_lower:
            return """## 🔧 StreamWorks-Information

### 📋 Überblick
StreamWorks ist eine Plattform für die Datenverarbeitung und Batch-Job-Automatisierung bei Arvato Systems.

### 💻 Grundfunktionen
- XML-basierte Stream-Konfiguration
- Automatisierte Batch-Jobs
- Datenverarbeitung und -transformation
- Zeitgesteuerte Ausführung

### 💡 Wichtiger Hinweis
Aufgrund technischer Probleme kann ich Ihnen momentan keine detaillierte Antwort geben. Bitte versuchen Sie es später erneut oder konsultieren Sie die StreamWorks-Dokumentation."""
        
        elif any(word in question_lower for word in ["xml", "template", "stream", "batch"]):
            return """## 🔧 StreamWorks-Konfiguration

### 📋 Überblick
Für XML-Templates und Stream-Konfigurationen stehen verschiedene Optionen zur Verfügung.

### 💻 Grundstruktur
```xml
<?xml version="1.0" encoding="UTF-8"?>
<StreamWorksConfig>
  <BatchJob beschreibung="Job-Beschreibung">
    <DataSource typ="..." pfad="..." />
    <ProcessingSteps>
      <!-- Verarbeitungsschritte -->
    </ProcessingSteps>
    <OutputTarget pfad="..." format="..." />
  </BatchJob>
</StreamWorksConfig>
```

### 💡 Wichtiger Hinweis
Für detaillierte Konfigurationen empfehle ich Ihnen, die StreamWorks-Dokumentation zu konsultieren."""
        
        else:
            return """## ❓ Entschuldigung

Das System ist momentan eingeschränkt verfügbar. 

### 💡 Vorschläge
- Versuchen Sie es in wenigen Minuten erneut
- Nutzen Sie spezifischere Begriffe zu StreamWorks
- Wenden Sie sich an den Support bei dringenden Fragen

### 📚 Verfügbare Themen
- StreamWorks-Konfiguration
- XML-Templates
- Batch-Jobs
- Datenverarbeitung"""
    
    def _build_context_from_documents(self, documents: List, citations: List, max_tokens: int = 2000) -> str:
        """Build optimized context string - reduced for performance"""
        if not documents:
            return "Keine relevanten Dokumente gefunden."
        
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
        
        return "\n".join(context_parts) if context_parts else "Keine passenden Dokumente gefunden."
    
    async def get_stats(self) -> Dict[str, Any]:
        """Service Statistiken"""
        return {
            "service": "mistral_rag_optimized",
            "is_initialized": self.is_initialized,
            "performance_mode": "high_speed",
            "optimization_level": "maximum"
        }

# Global instance
mistral_rag_service_optimized = MistralRAGServiceOptimized()