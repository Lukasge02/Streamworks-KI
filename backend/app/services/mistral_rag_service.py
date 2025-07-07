"""
Mistral RAG Service - ChromaDB + Mistral 7B Integration
Optimiert für deutsche StreamWorks-Dokumentation mit Citations
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
    """RAG Service optimiert für Mistral 7B mit Citation Support"""
    
    def __init__(self):
        self.rag_service = None
        self.mistral_service = mistral_llm_service
        self.is_initialized = False
        
        logger.info("🔍 Mistral RAG Service initialisiert mit Citation Support")
    
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
        """Optimierte Dokumentensuche für Mistral's Context Window (Fallback)"""
        
        if not self.rag_service or not self.rag_service.is_initialized:
            logger.warning("RAG Service nicht verfügbar")
            return []
        
        try:
            # Normale Dokumentensuche
            docs = await self.rag_service.search_documents(query, top_k)
            
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
    
    async def generate_response(self, question: str, documents: List = None) -> Dict[str, Any]:
        """Generate response with citations for chat API"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return {
                "response": "RAG Service ist nicht verfügbar. Bitte versuchen Sie es später erneut.",
                "citations": [],
                "sources_used": 0
            }
        
        try:
            # Use provided documents or search for new ones
            if documents:
                # Use provided documents with citations
                citations = await citation_service.create_citations_from_documents(documents, question)
                context = self._build_context_from_documents(documents, citations)
                sources_used = len(set(c.filename for c in citations))
            else:
                # Search for documents with citations (OPTIMIZED - single call)
                # Performance optimization: Use concurrent search
                search_result = await asyncio.wait_for(
                    self.rag_service.search_documents_with_citations(
                        query=question,
                        top_k=3,  # Further reduced for faster response
                        include_citations=True
                    ),
                    timeout=5.0  # 5 second timeout for search
                )
                
                documents = search_result["documents"]
                citations = search_result["citations"] or []
                
                # Use pre-built context if available, otherwise build it
                if "context" in search_result:
                    context = search_result["context"]
                else:
                    context = self._build_context_from_documents(documents, citations, max_tokens=2500)  # Balanced tokens
                    
                sources_used = len(set(c.filename for c in citations))
            
            if not documents or "Keine relevanten Dokumente" in context:
                return {
                    "response": await self._generate_fallback_response(question),
                    "citations": [],
                    "sources_used": 0
                }
            
            # Generate response with Mistral (v3.0 QUALITY-OPTIMIZED PROMPT)
            mistral_rag_prompt = f"""[INST] Du bist SKI, eine hochspezialisierte deutschsprachige StreamWorks-Expertin bei Arvato Systems.

=== KRITISCHE QUALITÄTSREGELN ===
- Antworte AUSSCHLIESSLICH auf Deutsch (KEINE englischen Begriffe)
- Verwende professionelle Höflichkeitsformen (Sie/Ihnen)
- STRUKTURIERE jede Antwort EXAKT nach diesem Schema:
  ## 🔧 [Präziser Titel der Lösung]
  ### 📋 Überblick
  [Kurze Zusammenfassung in 1-2 Sätzen]
  ### 💻 Konkrete Umsetzung
  [Detaillierte Schritte mit Code/XML-Beispielen]
  ### 💡 Wichtige Hinweise
  [Besonderheiten, Fallstricke, Best Practices]
  ### 📚 Quellen
  [EXAKT: Quelle: dateiname.ext - ohne weitere Beschreibung]

=== CITATION-REGELN (KRITISCH) ===
- NIEMALS doppelte Quellen auflisten
- Format: [Quelle: dateiname.ext] - KEINE Zusatztexte
- Sammle alle Quellen am Ende unter "### 📚 Quellen"
- Verwende deutsche Dateinamen wenn verfügbar
- KEINE englischen Titel wie "A: Yes, StreamWorks supports..."

=== STREAMWORKS XML-STANDARD ===
- Nutze IMMER vollständige XML-Struktur mit <?xml version="1.0" encoding="UTF-8"?>
- Root-Element: <StreamWorksConfig>
- Hauptelemente: <BatchJob>, <DataSource>, <ProcessingSteps>, <OutputTarget>
- Verwende deutsche Attribute: beschreibung="", typ="", pfad=""

=== VERFÜGBARE DOKUMENTATION ===
{context}

=== BENUTZERANFRAGE ===
{question} [/INST]

## 🔧 StreamWorks-Lösung

"""
            
            # Performance optimization: Add timeout to LLM generation
            response = await asyncio.wait_for(
                self.mistral_service.ollama_generate(
                    prompt=mistral_rag_prompt,
                    model=settings.OLLAMA_MODEL,
                    options={
                        "temperature": 0.3,  # Optimized for consistent German responses
                        "top_p": 0.9,        # Focused for better quality
                        "top_k": 25,         # Reduced for clearer language selection
                        "repeat_penalty": 1.2,  # Increased against repetitions
                        "num_predict": 512,    # Reduced for faster response
                        "num_ctx": 4096        # Reduced context for performance
                    }
                ),
                timeout=20.0  # 20 second timeout for generation
            )
            
            if response:
                response = self.mistral_service.post_process_german(response)
                
                # Add user-friendly citations to response
                if citations:
                    citation_text = citation_service.format_citations_for_response(citations, max_citations=3)
                    response += citation_text
                
                return {
                    "response": response,
                    "citations": [c.dict() if hasattr(c, 'dict') else c.model_dump() for c in citations],
                    "sources_used": sources_used
                }
            else:
                return {
                    "response": await self._generate_fallback_response(question),
                    "citations": [],
                    "sources_used": 0
                }
                
        except Exception as e:
            logger.error(f"Fehler bei Mistral RAG Generation: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "response": "Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
                "citations": [],
                "sources_used": 0
            }
    
    def _build_context_from_documents(self, documents: List, citations: List, max_tokens: int = 3000) -> str:
        """Build context string from documents and citations"""
        if not documents:
            return "Keine relevanten Dokumente gefunden."
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(documents):
            # Estimate token length (approx. 4 chars per token)
            doc_tokens = len(doc.page_content) // 4
            
            if current_length + doc_tokens > max_tokens:
                break
            
            # Get citation info for this document
            citation = citations[i] if i < len(citations) else None
            
            if citation:
                source_info = f"{citation.source_title} ({citation.source_type.value})"
                if citation.document_type:
                    source_info += f" - {citation.document_type.value}"
                relevance_info = f"Relevanz: {citation.relevance_score:.1%}"
            else:
                # Fallback to filename cleanup
                source_filename = doc.metadata.get('source', 'Unbekannte Quelle')
                source_info = citation_service._extract_source_title(source_filename, doc.page_content[:200])
                relevance_info = f"Relevanz: {doc.metadata.get('score', 0.0):.2f}"
            
            # Balanced context formatting
            content_snippet = doc.page_content[:800]  # Reasonable content per doc
            context_part = f"""
=== {source_info} ===
{content_snippet}
"""
            context_parts.append(context_part)
            current_length += doc_tokens
        
        return "\n".join(context_parts) if context_parts else "Keine passenden Dokumente gefunden."
    
    async def generate_mistral_context(self, query: str, max_tokens: int = 3000) -> str:
        """Generiere optimalen Kontext für Mistral's 8k Context Window mit Citations"""
        
        try:
            # Hole Dokumente mit Citation Support
            search_result = await self.rag_service.search_documents_with_citations(
                query=query,
                top_k=7,
                include_citations=True
            )
            
            documents = search_result["documents"]
            citations = search_result["citations"] or []
            
            return self._build_context_from_documents(documents, citations, max_tokens)
            
        except Exception as e:
            logger.error(f"Fehler bei Citation-basierter Kontextgenerierung: {e}")
            # Fallback auf alte Methode
            docs = await self.search_for_mistral(query, top_k=7)
            
            if not docs:
                return "Keine relevanten Dokumente gefunden."
            
            context_parts = []
            current_length = 0
            
            for doc in docs:
                doc_tokens = len(doc['content']) // 4
                if current_length + doc_tokens > max_tokens:
                    break
                
                # Verbesserte Quellenangabe auch im Fallback
                source_title = citation_service._extract_source_title(doc['source'], doc['content'][:200])
                
                context_part = f"""
=== STREAMWORKS DOKUMENTATION ===
Quelle: {source_title}
Relevanz: {doc['relevance']:.2f}

{doc['content']}
"""
                context_parts.append(context_part)
                current_length += doc_tokens
            
            return "\n".join(context_parts) if context_parts else "Keine passenden Dokumente gefunden."
    
    async def answer_with_mistral_rag(self, question: str) -> str:
        """RAG-Antwort mit Mistral 7B und Citations"""
        
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return "RAG Service ist nicht verfügbar. Bitte versuchen Sie es später erneut."
        
        try:
            # 1. Kontext aus ChromaDB holen mit Citations
            context = await self.generate_mistral_context(question)
            
            # 2. Spezielle Behandlung wenn kein Kontext gefunden
            if "Keine relevanten Dokumente" in context or "Keine passenden Dokumente" in context:
                # Fallback auf allgemeine Antwort
                return await self._generate_fallback_response(question)
            
            # 3. Mistral-optimierter Prompt für RAG
            mistral_rag_prompt = f"""[INST] Du bist SKI, ein deutschsprachiger StreamWorks-Experte bei Arvato Systems.

Beantworte die Frage basierend auf der verfügbaren StreamWorks-Dokumentation.

WICHTIG: 
- Antworte nur auf Deutsch
- Verwende Emojis für bessere Lesbarkeit  
- Strukturiere die Antwort mit Markdown
- Sei präzise und hilfreich

VERFÜGBARE DOKUMENTATION:
{context}

FRAGE: {question} [/INST]

## 🎯 StreamWorks-Antwort

"""
            
            # 4. Mistral-Generation
            # Performance optimization: Add timeout to LLM generation
            response = await asyncio.wait_for(
                self.mistral_service.ollama_generate(
                    prompt=mistral_rag_prompt,
                    model=settings.OLLAMA_MODEL,
                    options={
                        "temperature": 0.3,  # Optimized for consistent German responses
                        "top_p": 0.9,        # Focused for better quality
                        "top_k": 25,         # Reduced for clearer language selection
                        "repeat_penalty": 1.2,  # Increased against repetitions
                        "num_predict": 512,    # Reduced for faster response
                        "num_ctx": 4096        # Reduced context for performance
                    }
                ),
                timeout=20.0  # 20 second timeout for generation
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
        
        fallback_prompt = f"""[INST] Du bist SKI, ein freundlicher StreamWorks-Experte bei Arvato Systems.

Die Frage konnte nicht in der spezifischen Dokumentation gefunden werden.
Gib eine hilfreiche allgemeine Antwort basierend auf StreamWorks-Grundlagen:

THEMEN:
- XML-Stream-Konfiguration
- Batch-Job-Automatisierung
- Datenverarbeitung und -transformation
- StreamWorks-Best Practices

WICHTIG:
- Antworte nur auf Deutsch
- Sei hilfreich und konkret
- Verweise auf weitere Ressourcen wenn sinnvoll

FRAGE: {question} [/INST]

"""
        
        try:
            response = await self.mistral_service.ollama_generate(
                prompt=fallback_prompt,
                model=settings.OLLAMA_MODEL,
                options={
                    "temperature": 0.1,  # Lower for consistent fallback responses
                    "top_p": 0.9,
                    "top_k": 20,
                    "repeat_penalty": 1.1,
                    "num_predict": 256,  # Even shorter for fallbacks
                    "num_ctx": 2048  # Smaller context for fallbacks
                }
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
            "optimization": "german_streamworks_with_citations"
        }

# Global instance
mistral_rag_service = MistralRAGService()