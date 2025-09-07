"""
Local RAG Service - 100% lokale KI ohne Fallbacks
Pure local AI RAG implementation using only Ollama, no OpenAI dependencies
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from services.vectorstore import VectorStoreService
from services.embeddings import EmbeddingService
from services.ollama_service import OllamaService
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class LocalRAGConfig:
    """Configuration for local RAG operations"""
    # Performance settings
    top_k: int = 6
    max_sources: int = 6
    min_relevance_score: float = 0.2  # Lowered for better recall with embeddinggemma
    
    # Local LLM settings
    model_name: str = "qwen2.5:7b"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # Response settings
    include_sources: bool = True
    include_confidence: bool = True


class LocalRAGService:
    """
    Pure local RAG service using only Ollama
    No OpenAI fallbacks, no external API dependencies
    """
    
    def __init__(
        self,
        vectorstore: VectorStoreService,
        embeddings: EmbeddingService,
        ollama_service: Optional[OllamaService] = None,
        config: Optional[LocalRAGConfig] = None
    ):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.ollama = ollama_service or OllamaService()
        self.config = config or LocalRAGConfig()
        
        logger.info(f"🤖 LocalRAGService initialized with model: {self.config.model_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all local services"""
        try:
            # Check Ollama
            ollama_health = await self.ollama.health_check()
            
            # Check vector store (basic test)
            vectorstore_healthy = True
            try:
                await self.vectorstore.initialize()
            except Exception as e:
                logger.error(f"VectorStore health check failed: {str(e)}")
                vectorstore_healthy = False
            
            # Check embeddings (basic test)
            embeddings_healthy = True
            try:
                await self.embeddings.embed_query("test")
            except Exception as e:
                logger.error(f"Embeddings health check failed: {str(e)}")
                embeddings_healthy = False
            
            overall_status = "healthy" if (
                ollama_health["status"] == "healthy" and
                vectorstore_healthy and
                embeddings_healthy
            ) else "unhealthy"
            
            return {
                "status": overall_status,
                "components": {
                    "ollama": ollama_health,
                    "vectorstore": "healthy" if vectorstore_healthy else "unhealthy",
                    "embeddings": "healthy" if embeddings_healthy else "unhealthy"
                },
                "config": {
                    "model": self.config.model_name,
                    "top_k": self.config.top_k,
                    "temperature": self.config.temperature
                }
            }
            
        except Exception as e:
            logger.error(f"LocalRAG health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def query(
        self,
        query: str,
        mode: str = "accurate",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query using local RAG pipeline
        
        Args:
            query: User question
            mode: Processing mode ('fast', 'accurate', 'comprehensive')
            filters: Optional filters for document retrieval
            
        Returns:
            RAG response with answer, confidence, sources, etc.
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 LocalRAG Query: '{query[:100]}...' (mode: {mode})")
            
            # Step 1: Retrieve relevant documents
            retrieval_results = await self._retrieve_documents(query, filters)
            
            if not retrieval_results["chunks"]:
                logger.warning("No relevant documents found for query")
                return await self._generate_no_context_response(query, start_time)
            
            logger.info(f"📄 Found {len(retrieval_results['chunks'])} relevant chunks")
            
            # Step 2: Generate response based on mode
            if mode == "fast":
                generation_result = await self._fast_generate(query, retrieval_results)
            elif mode == "comprehensive":
                generation_result = await self._comprehensive_generate(query, retrieval_results)
            else:  # accurate (default)
                generation_result = await self._accurate_generate(query, retrieval_results)
            
            # Step 3: Compile final response
            processing_time = time.time() - start_time
            
            response = {
                "answer": generation_result["answer"],
                "confidence": generation_result.get("confidence", 0.5),
                "sources": retrieval_results["sources"] if self.config.include_sources else [],
                "chunks_used": len(retrieval_results["chunks"]),
                "model_used": f"{self.config.model_name} (local)",
                "processing_time": processing_time,
                "response_time": f"{processing_time:.2f}s",
                "metadata": {
                    "mode": mode,
                    "retrieved_chunks": len(retrieval_results["chunks"]),
                    "total_tokens": generation_result.get("total_tokens", 0),
                    "model_used": f"{self.config.model_name} (local)",
                    "provider": "ollama"
                }
            }
            
            logger.info(f"✅ LocalRAG completed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"LocalRAG query failed: {str(e)}")
            processing_time = time.time() - start_time
            
            return {
                "answer": f"Entschuldigung, bei der lokalen Verarbeitung ist ein Fehler aufgetreten: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "chunks_used": 0,
                "model_used": f"{self.config.model_name} (error)",
                "processing_time": processing_time,
                "response_time": f"{processing_time:.2f}s",
                "metadata": {
                    "error": str(e),
                    "provider": "ollama"
                }
            }
    
    async def _retrieve_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve relevant documents from vector store"""
        
        logger.info(f"🔍 Retrieving documents for query: '{query[:50]}...'")
        logger.info(f"📊 Using embedding provider: {self.embeddings.provider}")
        
        # Get query embedding with embeddinggemma
        query_embedding = await self.embeddings.embed_query(query)
        logger.info(f"✅ Query embedding created: {len(query_embedding)} dimensions")
        
        # Search vector store
        search_results = await self.vectorstore.search_similar(
            query_embedding=query_embedding,
            top_k=self.config.top_k,
            filters=filters
        )
        
        logger.info(f"📄 VectorStore returned {len(search_results)} results")
        
        # Extract chunks and sources
        chunks = []
        sources = set()
        
        for result in search_results:
            # Filter by relevance score
            score = result.get("similarity_score", 0.0)
            logger.info(f"📊 Document score: {score}, threshold: {self.config.min_relevance_score}")
            
            if score >= self.config.min_relevance_score:
                chunks.append({
                    "content": result.get("content", ""),
                    "score": score,
                    "metadata": result.get("metadata", {})
                })
                
                # Extract source information
                metadata = result.get("metadata", {})
                if metadata.get("source_file"):
                    sources.add(metadata["source_file"])
                    
        logger.info(f"✅ Filtered to {len(chunks)} chunks above relevance threshold")
        
        return {
            "chunks": chunks,
            "sources": list(sources)[:self.config.max_sources]
        }
    
    async def _fast_generate(self, query: str, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Fast generation - optimized for speed"""
        
        # Use only top 3 chunks for speed
        context = "\n".join([
            chunk["content"] for chunk in retrieval_results["chunks"][:3]
        ])
        
        prompt = f"""Basierend auf dem folgenden Kontext, beantworte die Frage kurz und präzise auf Deutsch:

Kontext:
{context}

Frage: {query}

Kurze Antwort:"""
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await self.ollama.chat_completion(
            messages=messages,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=500  # Shorter for fast mode
        )
        
        # Calculate confidence based on chunk relevance
        if retrieval_results["chunks"]:
            avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"][:3]) / min(3, len(retrieval_results["chunks"]))
            confidence = min(0.9, max(0.3, avg_score))
        else:
            confidence = 0.1
        
        return {
            "answer": response["choices"][0]["message"]["content"],
            "confidence": confidence,
            "total_tokens": response["usage"]["total_tokens"]
        }
    
    async def _accurate_generate(self, query: str, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Accurate generation - balanced speed and quality"""
        
        context = "\n\n".join([
            f"Quelle {i+1} (Relevanz: {chunk['score']:.2f}): {chunk['content']}"
            for i, chunk in enumerate(retrieval_results["chunks"])
        ])
        
        system_prompt = "Du bist ein hilfsreicher Assistent, der Fragen basierend auf bereitgestelltem Kontext beantwortet. Antworte immer auf Deutsch und nutze die Informationen aus dem Kontext."
        
        user_prompt = f"""Kontext:
{context}

Frage: {query}

Bitte gib eine umfassende Antwort basierend auf dem Kontext. Falls der Kontext nicht genügend Informationen enthält, sage das klar. Strukturiere deine Antwort mit Aufzählungspunkten oder Abschnitten, wenn es hilft.

Antwort:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.ollama.chat_completion(
            messages=messages,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # Calculate confidence based on chunk relevance
        if retrieval_results["chunks"]:
            avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"]) / len(retrieval_results["chunks"])
            confidence = min(0.95, max(0.3, avg_score))
        else:
            confidence = 0.1
        
        return {
            "answer": response["choices"][0]["message"]["content"],
            "confidence": confidence,
            "total_tokens": response["usage"]["total_tokens"]
        }
    
    async def _comprehensive_generate(self, query: str, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive generation - maximum quality"""
        
        # Use all available chunks
        context = "\n\n".join([
            f"Dokument {i+1} (Relevanz: {chunk['score']:.2f}):\n{chunk['content']}\n"
            f"Metadaten: {chunk['metadata']}"
            for i, chunk in enumerate(retrieval_results["chunks"])
        ])
        
        system_prompt = """Du bist ein Experte, der detaillierte Analysen basierend auf bereitgestellten Dokumenten erstellt. 
        Deine Aufgabe ist es, eine umfassende, strukturierte und gut begründete Antwort zu geben. 
        Antworte immer auf Deutsch und referenziere die verwendeten Quellen."""
        
        user_prompt = f"""Dokumentenkontext:
{context}

Frage: {query}

Bitte erstelle eine detaillierte, gut strukturierte Antwort mit folgenden Elementen:
1. Hauptantwort mit wichtigsten Punkten
2. Detaillierte Erläuterungen aus den Dokumenten
3. Relevante Zitate oder Beispiele
4. Zusammenfassung der wichtigsten Erkenntnisse

Falls bestimmte Aspekte nicht ausreichend in den Dokumenten behandelt werden, erwähne das explizit.

Umfassende Antwort:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.ollama.chat_completion(
            messages=messages,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens * 2  # More tokens for comprehensive mode
        )
        
        # Higher confidence for comprehensive mode with more context
        if retrieval_results["chunks"]:
            avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"]) / len(retrieval_results["chunks"])
            confidence = min(0.98, max(0.4, avg_score * 1.2))  # Boost confidence
        else:
            confidence = 0.1
        
        return {
            "answer": response["choices"][0]["message"]["content"],
            "confidence": confidence,
            "total_tokens": response["usage"]["total_tokens"]
        }
    
    async def _generate_no_context_response(self, query: str, start_time: float) -> Dict[str, Any]:
        """Generate response when no relevant documents are found"""
        
        messages = [{
            "role": "user", 
            "content": f"""Frage: {query}

Ich konnte keine relevanten Dokumente zu dieser Frage finden. Bitte gib eine allgemeine, hilfreiche Antwort auf Deutsch und erkläre, dass spezifische Informationen zu diesem Thema in den verfügbaren Dokumenten nicht gefunden wurden."""
        }]
        
        response = await self.ollama.chat_completion(
            messages=messages,
            model=self.config.model_name,
            temperature=0.3,  # Slightly higher for creative response
            max_tokens=500
        )
        
        processing_time = time.time() - start_time
        
        return {
            "answer": response["choices"][0]["message"]["content"],
            "confidence": 0.2,  # Low confidence without context
            "sources": [],
            "chunks_used": 0,
            "model_used": f"{self.config.model_name} (local)",
            "processing_time": processing_time,
            "response_time": f"{processing_time:.2f}s",
            "metadata": {
                "mode": "no_context",
                "retrieved_chunks": 0,
                "total_tokens": response["usage"]["total_tokens"],
                "model_used": f"{self.config.model_name} (local)",
                "provider": "ollama"
            }
        }