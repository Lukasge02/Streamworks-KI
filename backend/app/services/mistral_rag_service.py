"""
Mistral RAG Service - ChromaDB + Mistral 7B Integration
Optimiert für deutsche StreamWorks-Dokumentation
"""
import logging
from typing import List, Dict, Any
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.mistral_llm_service import mistral_llm_service

logger = logging.getLogger(__name__)

class MistralRAGService:
    """RAG Service optimiert für Mistral 7B"""
    
    def __init__(self):
        self.rag_service = None
        self.mistral_service = mistral_llm_service
        self.is_initialized = False
        
        logger.info("🔍 Mistral RAG Service initialisiert")
    
    async def initialize(self):
        """Initialisiere RAG + Mistral Services"""
        try:
            # RAG Service initialisieren
            from app.services.rag_service import rag_service
            self.rag_service = rag_service
            
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            # Mistral Service initialisieren
            if not self.mistral_service.is_initialized:
                await self.mistral_service.initialize()
            
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
            # Nutze bestehende RAG-Suche
            documents = await self.rag_service.search_documents(query, top_k)
            
            # Für Mistral optimierte Aufbereitung
            context_docs = []
            for i, doc in enumerate(documents):
                # Relevanz basierend auf Position (erste Ergebnisse sind relevanter)
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
    
    async def generate_mistral_context(self, query: str, max_tokens: int = 3000) -> str:
        """Generiere optimalen Kontext für Mistral's 8k Context Window"""
        
        # Suche relevante Dokumente
        docs = await self.search_for_mistral(query, top_k=7)
        
        if not docs:
            return "Keine relevanten Dokumente gefunden."
        
        # Baue Kontext für Mistral auf
        context_parts = []
        current_length = 0
        
        for doc in docs:
            # Schätze Token-Länge (ca. 4 Zeichen pro Token)
            doc_tokens = len(doc['content']) // 4
            
            if current_length + doc_tokens > max_tokens:
                break
            
            # Mistral-optimierte Kontext-Formatierung
            context_part = f"""
=== STREAMWORKS DOKUMENTATION ===
Quelle: {doc['source']}
Relevanz: {doc['relevance']:.2f}

{doc['content']}
"""
            context_parts.append(context_part)
            current_length += doc_tokens
        
        if not context_parts:
            return "Keine passenden Dokumente im verfügbaren Token-Limit gefunden."
        
        return "\n".join(context_parts)
    
    async def answer_with_mistral_rag(self, question: str) -> str:
        """RAG-Antwort mit Mistral 7B"""
        
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return "RAG Service ist nicht verfügbar. Bitte versuchen Sie es später erneut."
        
        try:
            # 1. Kontext aus ChromaDB holen
            context = await self.generate_mistral_context(question)
            
            # 2. Spezielle Behandlung wenn kein Kontext gefunden
            if "Keine relevanten Dokumente" in context or "Keine passenden Dokumente" in context:
                # Fallback auf allgemeine Antwort
                return await self._generate_fallback_response(question)
            
            # 3. Mistral-optimierter Prompt für RAG
            mistral_rag_prompt = f"""[INST] Du bist SKI, ein deutschsprachiger StreamWorks-Experte bei Arvato Systems.

=== AUFGABE ===
Beantworte die Frage präzise basierend auf der bereitgestellten StreamWorks-Dokumentation.

=== ANTWORT-REGELN ===
- Antworte AUSSCHLIESSLICH auf Deutsch
- Nutze die Dokumentation als Hauptquelle
- Strukturiere die Antwort mit Markdown und passenden Emojis
- Zitiere Quellen mit [Quelle: dateiname]
- Sei konkret und hilfreich
- Verwende professionelle Höflichkeitsformen (Sie/Ihnen)

=== STREAMWORKS DOKUMENTATION ===
{context}

=== BENUTZERANFRAGE ===
{question} [/INST]

## 🔧 StreamWorks-Antwort

"""
            
            # 4. Mistral-Generation
            response = await self.mistral_service.ollama_generate(
                prompt=mistral_rag_prompt,
                model=settings.OLLAMA_MODEL,
                options={
                    "temperature": settings.MODEL_TEMPERATURE,
                    "top_p": settings.MODEL_TOP_P,
                    "top_k": settings.MODEL_TOP_K,
                    "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
                    "num_predict": settings.MODEL_MAX_TOKENS
                }
            )
            
            # 5. Deutsche Nachbearbeitung
            if response:
                response = self.mistral_service.post_process_german(response)
                return response
            else:
                return await self._generate_fallback_response(question)
            
        except Exception as e:
            logger.error(f"Fehler bei Mistral RAG: {e}")
            return "Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut."
    
    async def _generate_fallback_response(self, question: str) -> str:
        """Fallback-Antwort ohne RAG-Kontext"""
        
        fallback_prompt = f"""[INST] Du bist SKI, ein deutschsprachiger StreamWorks-Experte.

Die Frage konnte nicht in der Dokumentation gefunden werden.
Gib eine hilfreiche allgemeine Antwort basierend auf deinem Wissen über:
- XML-Stream-Erstellung
- Batch-Job-Automatisierung  
- Workload-Management
- StreamWorks-Konzepte

Frage: {question} [/INST]

## 🤔 Allgemeine StreamWorks-Hilfe

"""
        
        try:
            response = await self.mistral_service.ollama_generate(
                prompt=fallback_prompt,
                model=settings.OLLAMA_MODEL
            )
            
            if response:
                # Kennzeichne als allgemeine Antwort
                response = f"💡 **Allgemeine Hilfe** (keine spezifische Dokumentation gefunden):\n\n{response}"
                return self.mistral_service.post_process_german(response)
            
        except Exception as e:
            logger.error(f"Fallback response error: {e}")
        
        return """## ❓ Entschuldigung

Ich konnte keine spezifischen Informationen zu Ihrer Frage in der StreamWorks-Dokumentation finden.

### 💡 Vorschläge:
- Überprüfen Sie die Schreibweise Ihrer Frage
- Versuchen Sie allgemeinere Begriffe
- Nutzen Sie den Training Data Tab um weitere Dokumentation hochzuladen

### 🚀 Typische StreamWorks-Themen:
- XML-Stream-Konfiguration
- Batch-Job-Erstellung
- Zeitplanung und Scheduling
- Datenverarbeitung
"""
    
    async def get_stats(self) -> Dict[str, Any]:
        """Mistral RAG Service Statistiken"""
        
        rag_stats = {}
        if self.rag_service:
            rag_stats = await self.rag_service.get_stats()
        
        mistral_stats = await self.mistral_service.get_stats()
        
        return {
            "service": "mistral_rag",
            "is_initialized": self.is_initialized,
            "rag_service": rag_stats,
            "mistral_service": mistral_stats,
            "optimization": "german_streamworks"
        }

# Global instance
mistral_rag_service = MistralRAGService()