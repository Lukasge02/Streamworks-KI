"""
OpenAI-based RAG Service implementation
"""
import time
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from .models import RAGServiceInterface, RAGConfig, RAGMode
from ..di_container import ServiceLifecycle
from ..vectorstore import VectorStoreService
from ..embeddings import EmbeddingService
from ..adaptive_retrieval import AdaptiveRetrievalService
from config import settings

logger = logging.getLogger(__name__)


class OpenAIRAGService(RAGServiceInterface, ServiceLifecycle):
    """
    OpenAI-based RAG Service for document queries
    Clean, focused implementation using OpenAI for generation + ChromaDB for persistence
    """
    
    def __init__(self, 
                 vectorstore: VectorStoreService,
                 embeddings: EmbeddingService,
                 config: Optional[RAGConfig] = None):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.config = config or RAGConfig()
        self._initialized = False
        
        # Initialize OpenAI client
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY ist erforderlich für OpenAI RAG Service")
        
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize adaptive retrieval service
        self.adaptive_retrieval = AdaptiveRetrievalService()
        logger.info("✅ Adaptive Retrieval Service initialized")
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if self._initialized:
            return
            
        logger.info("Initializing OpenAI RAG Service")
        
        # Ensure dependencies are initialized
        if hasattr(self.vectorstore, 'initialize') and callable(getattr(self.vectorstore, 'initialize')):
            await self.vectorstore.initialize()
        
        if hasattr(self.embeddings, 'initialize') and callable(getattr(self.embeddings, 'initialize')):
            await self.embeddings.initialize()
        
        self._initialized = True
        logger.info("OpenAI RAG Service initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Test OpenAI connection
            openai_healthy = False
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                openai_healthy = True
            except Exception as e:
                logger.error(f"OpenAI health check failed: {str(e)}")
            
            # Test embedding service
            embedding_healthy = False
            try:
                await self.embeddings.embed_query("test")
                embedding_healthy = True
            except Exception as e:
                logger.error(f"Embedding health check failed: {str(e)}")
            
            # Test vectorstore
            vectorstore_healthy = False
            try:
                # Generate a proper test embedding using the embeddings service
                test_embedding = await self.embeddings.embed_query("health check test")
                await self.vectorstore.search_similar(
                    query_embedding=test_embedding,
                    top_k=1
                )
                vectorstore_healthy = True
            except Exception as e:
                logger.error(f"Vectorstore health check failed: {str(e)}")
                # Try with a simple embedding as fallback
                try:
                    # Try with OpenAI embedding dimension (1536 for text-embedding-3-large)
                    test_embedding = [0.1] * 1536
                    await self.vectorstore.search_similar(
                        query_embedding=test_embedding,
                        top_k=1
                    )
                    vectorstore_healthy = True
                    logger.info("Vectorstore health check passed with fallback embedding")
                except Exception as e2:
                    logger.error(f"Vectorstore health check fallback also failed: {str(e2)}")
            
            return {
                "status": "healthy" if (openai_healthy and embedding_healthy and vectorstore_healthy) else "unhealthy",
                "openai": "connected" if openai_healthy else "disconnected",
                "embeddings": "ready" if embedding_healthy else "not ready",
                "vectorstore": "ready" if vectorstore_healthy else "not ready",
                "config": {
                    "model": self.config.model_name,
                    "rag_type": self.config.rag_type.value,
                    "top_k": self.config.top_k
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("Cleaning up OpenAI RAG Service")
        self._initialized = False
    
    async def query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[RAGMode] = None,
        include_sources: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process RAG query with OpenAI generation
        
        Args:
            query: User question
            filters: Optional metadata filters
            mode: Processing mode
            include_sources: Include source citations
            
        Returns:
            Dict with answer, confidence, sources, and metadata
        """
        start_time = time.time()
        processing_mode = mode or self.config.processing_mode
        
        try:
            # Step 1: Retrieve relevant documents
            retrieval_results = await self._retrieve_documents(query, filters, processing_mode)
            
            # Step 2: Generate response with OpenAI
            generation_result = await self._generate_response(query, retrieval_results, processing_mode)
            
            # Step 3: Package result with enhanced performance tracking
            processing_time = time.time() - start_time
            result = {
                "answer": generation_result["answer"],
                "confidence": generation_result["confidence"],
                "sources": retrieval_results["sources"] if include_sources else [],
                "processing_mode": processing_mode.value,
                "response_time": processing_time,
                "metadata": {
                    "retrieved_chunks": len(retrieval_results["chunks"]),
                    "total_tokens": generation_result.get("total_tokens", 0),
                    "model_used": generation_result["model_used"],
                    "embedding_model": "EmbeddingGemma",
                    "rag_type": self.config.rag_type.value,
                    "performance": {
                        "retrieval_time": retrieval_results.get("retrieval_time", 0),
                        "adaptive_time": retrieval_results.get("adaptive_time", 0),
                        "generation_time": generation_result.get("generation_time", 0),
                        "total_time": processing_time,
                        "chunks_processed": len(retrieval_results["chunks"]),
                        "sources_found": len(retrieval_results["sources"]),
                        "adaptive_retrieval": retrieval_results.get("adaptive_retrieval", {})
                    }
                }
            }
            
            logger.info(f"✅ RAG Query erfolgreich - {result['response_time']:.2f}s")
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"❌ RAG Query failed ({error_type}): {str(e)}")
            
            processing_time = time.time() - start_time
            return {
                "answer": f"Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Anfrage: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "processing_mode": processing_mode.value,
                "response_time": processing_time,
                "error": str(e),
                "error_type": error_type,
                "metadata": {
                    "retrieved_chunks": 0,
                    "total_tokens": 0,
                    "model_used": "none",
                    "rag_type": self.config.rag_type.value,
                    "performance": {
                        "total_time": processing_time,
                        "error": True
                    }
                }
            }
    
    async def _retrieve_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        mode: RAGMode
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents from vector store
        
        Args:
            query: User query
            filters: Optional metadata filters
            mode: Processing mode for retrieval strategy
            
        Returns:
            Dict with chunks, sources, and retrieval metadata
        """
        retrieval_start = time.time()
        
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.embed_query(query)
            
            # Adaptive retrieval based on mode
            adaptive_start = time.time()
            
            if self.config.use_adaptive_retrieval and mode in [RAGMode.ACCURATE, RAGMode.COMPREHENSIVE]:
                # Use adaptive retrieval for better results
                retrieval_config = await self.adaptive_retrieval.optimize_retrieval_config(
                    query=query,
                    mode=mode,
                    base_config={
                        "top_k": self.config.top_k,
                        "similarity_threshold": self.config.similarity_threshold
                    }
                )
            else:
                # Use basic retrieval configuration
                retrieval_config = {
                    "top_k": self.config.top_k if mode != RAGMode.COMPREHENSIVE else self.config.top_k * 2,
                    "similarity_threshold": self.config.similarity_threshold
                }
            
            adaptive_time = time.time() - adaptive_start
            
            # Perform vector search
            search_results = await self.vectorstore.search_similar(
                query_embedding=query_embedding,
                top_k=retrieval_config["top_k"],
                metadata_filter=filters,
                include_distances=True
            )
            
            # Process results
            chunks = []
            sources = []
            
            for result in search_results:
                # Extract content and metadata
                chunk_data = {
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity": 1 - result.get("distance", 0),  # Convert distance to similarity
                    "document_id": result.get("metadata", {}).get("document_id", ""),
                    "chunk_id": result.get("id", "")
                }
                
                # Filter by similarity threshold
                if chunk_data["similarity"] >= retrieval_config["similarity_threshold"]:
                    chunks.append(chunk_data)
                    
                    # Create source reference
                    source = {
                        "document_id": chunk_data["document_id"],
                        "filename": chunk_data["metadata"].get("filename", "Unknown"),
                        "title": chunk_data["metadata"].get("title", ""),
                        "chunk_id": chunk_data["chunk_id"],
                        "similarity": chunk_data["similarity"],
                        "page": chunk_data["metadata"].get("page_number", None)
                    }
                    sources.append(source)
            
            retrieval_time = time.time() - retrieval_start
            
            logger.info(f"📄 Retrieved {len(chunks)} relevant chunks in {retrieval_time:.2f}s")
            
            return {
                "chunks": chunks,
                "sources": sources,
                "retrieval_time": retrieval_time,
                "adaptive_time": adaptive_time,
                "retrieval_config": retrieval_config,
                "adaptive_retrieval": {
                    "enabled": self.config.use_adaptive_retrieval,
                    "optimization_time": adaptive_time,
                    "config_used": retrieval_config
                }
            }
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            return {
                "chunks": [],
                "sources": [],
                "retrieval_time": time.time() - retrieval_start,
                "adaptive_time": 0,
                "error": str(e)
            }
    
    async def _generate_response(
        self,
        query: str,
        retrieval_results: Dict[str, Any],
        mode: RAGMode
    ) -> Dict[str, Any]:
        """
        Generate response using OpenAI with retrieved context
        
        Args:
            query: Original user query
            retrieval_results: Results from document retrieval
            mode: Processing mode
            
        Returns:
            Dict with generated answer, confidence, and generation metadata
        """
        generation_start = time.time()
        chunks = retrieval_results["chunks"]
        
        try:
            if not chunks:
                # No relevant context found
                return {
                    "answer": "Entschuldigung, ich konnte keine relevanten Informationen zu Ihrer Frage in den verfügbaren Dokumenten finden. Können Sie Ihre Frage anders formulieren oder spezifischer stellen?",
                    "confidence": 0.0,
                    "model_used": "fallback",
                    "generation_time": time.time() - generation_start,
                    "total_tokens": 0
                }
            
            # Build context from chunks
            context_parts = []
            for i, chunk in enumerate(chunks[:self.config.max_sources]):
                source_info = f"[Quelle {i+1}: {chunk['metadata'].get('filename', 'Unknown')}]"
                context_parts.append(f"{source_info}\n{chunk['text']}")
            
            context = "\n\n".join(context_parts)
            
            # Build prompt based on mode
            if mode == RAGMode.FAST:
                system_prompt = """Sie sind ein hilfreicher AI-Assistent. Beantworten Sie die Frage kurz und präzise basierend auf dem bereitgestellten Kontext. Wenn die Antwort nicht im Kontext enthalten ist, sagen Sie das deutlich."""
            elif mode == RAGMode.COMPREHENSIVE:
                system_prompt = """Sie sind ein sachkundiger AI-Assistent. Geben Sie eine umfassende, detaillierte Antwort basierend auf dem bereitgestellten Kontext. Zitieren Sie relevante Quellen und gehen Sie auf verschiedene Aspekte der Frage ein. Wenn zusätzliche Informationen hilfreich wären, erwähnen Sie das."""
            else:  # ACCURATE
                system_prompt = """Sie sind ein präziser AI-Assistent. Beantworten Sie die Frage genau und faktisch basierend auf dem bereitgestellten Kontext. Zitieren Sie die Quellen Ihrer Informationen und seien Sie ehrlich, wenn Sie unsicher sind oder Informationen fehlen."""
            
            user_prompt = f"""Kontext:
{context}

Frage: {query}

Bitte beantworten Sie die Frage basierend auf dem bereitgestellten Kontext. Geben Sie eine klare, hilfreiche Antwort."""
            
            # Generate response with OpenAI
            response = await self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            answer = response.choices[0].message.content
            total_tokens = response.usage.total_tokens if response.usage else 0
            
            # Calculate confidence based on chunk relevance and answer quality
            confidence = self._calculate_universal_confidence(chunks, answer)
            
            generation_time = time.time() - generation_start
            
            return {
                "answer": answer,
                "confidence": confidence,
                "model_used": self.config.model_name,
                "generation_time": generation_time,
                "total_tokens": total_tokens,
                "context_chunks": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {
                "answer": f"Entschuldigung, es gab ein Problem bei der Generierung der Antwort: {str(e)}",
                "confidence": 0.0,
                "model_used": "error",
                "generation_time": time.time() - generation_start,
                "total_tokens": 0,
                "error": str(e)
            }
    
    def _calculate_universal_confidence(self, chunks: List[Dict], answer: str) -> float:
        """
        Calculate confidence score based on retrieved chunks and generated answer
        
        Args:
            chunks: Retrieved document chunks
            answer: Generated answer
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not chunks or not answer:
            return 0.0
        
        try:
            # Factor 1: Average similarity of retrieved chunks
            similarities = [chunk.get("similarity", 0.0) for chunk in chunks]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            
            # Factor 2: Number of relevant chunks (more sources = higher confidence)
            chunk_factor = min(len(chunks) / self.config.max_sources, 1.0)
            
            # Factor 3: Answer length and structure (longer, structured answers typically more confident)
            answer_length_factor = min(len(answer.split()) / 100, 1.0)  # Normalize to 100 words
            
            # Factor 4: Check for uncertainty markers in answer
            uncertainty_markers = ["nicht sicher", "möglicherweise", "könnte", "vielleicht", "unklar", "schwer zu sagen"]
            uncertainty_penalty = 0.0
            answer_lower = answer.lower()
            for marker in uncertainty_markers:
                if marker in answer_lower:
                    uncertainty_penalty += 0.1
            
            # Combine factors
            base_confidence = (avg_similarity * 0.4 + chunk_factor * 0.3 + answer_length_factor * 0.3)
            final_confidence = max(0.0, min(1.0, base_confidence - uncertainty_penalty))
            
            return final_confidence
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5  # Default medium confidence