"""
StreamWorks RAG Service - Unified Production System
Enterprise-grade RAG implementation with Mistral 7B and E5 embeddings
"""
import logging
import asyncio
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
import aiohttp
import json

from ...core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class RAGAnswer:
    """RAG response with comprehensive metadata"""
    question: str
    answer: str
    sources: List[str]
    processing_time: float
    confidence: float
    chunks_analyzed: int
    context_length: int
    retrieval_methods: List[str]

class StreamWorksEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """E5 embedding function for StreamWorks"""
    def __init__(self, model):
        self.model = model
    
    def __call__(self, input):
        prefixed_texts = [f'passage: {text}' for text in input]
        embeddings = self.model.encode(prefixed_texts)
        return embeddings.tolist()

class RAGService:
    """Unified RAG Service for StreamWorks"""
    
    def __init__(self):
        self.embedding_model = None
        self.chromadb_client = None
        self.collection = None
        self.is_ready = False
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="RAG")
        
        # Unified configuration from settings
        self.config = {
            "embedding_model": settings.EMBEDDING_MODEL,
            "chromadb_path": settings.VECTOR_DB_PATH,
            "collection_name": "streamworks_knowledge",
            "mistral_model": settings.OLLAMA_MODEL,
            "ollama_url": "http://localhost:11434",
            "semantic_top_k": 5,
            "keyword_top_k": 3,
            "hybrid_top_k": 2,
            "max_context_length": 2000,
            "chunk_size": settings.RAG_CHUNK_SIZE,
            "chunk_overlap": settings.RAG_CHUNK_OVERLAP,
            "temperature": settings.MODEL_TEMPERATURE,
            "timeout": 30,
            "min_confidence": 0.7,
            "retry_attempts": 2,
        }
        
        # Response cache for performance
        self._response_cache = {}
        self._cache_timestamps = {}
        
        logger.info("RAG Service initialized")
    
    async def initialize(self):
        """Initialize RAG system"""
        try:
            logger.info("Initializing RAG System...")
            
            # Load embedding model
            logger.info(f"Loading embedding model: {self.config['embedding_model']}")
            self.embedding_model = SentenceTransformer(self.config["embedding_model"])
            
            # Initialize ChromaDB
            logger.info(f"Connecting to ChromaDB at: {self.config['chromadb_path']}")
            self.chromadb_client = chromadb.PersistentClient(
                path=self.config["chromadb_path"],
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.chromadb_client.get_collection(
                    self.config["collection_name"],
                    embedding_function=StreamWorksEmbeddingFunction(self.embedding_model)
                )
                logger.info(f"Connected to existing collection: {self.config['collection_name']}")
            except:
                self.collection = self.chromadb_client.create_collection(
                    self.config["collection_name"],
                    embedding_function=StreamWorksEmbeddingFunction(self.embedding_model)
                )
                logger.info(f"Created new collection: {self.config['collection_name']}")
            
            # Test Mistral connection
            await self._test_mistral_connection()
            
            self.is_ready = True
            logger.info("RAG System ready")
            
        except Exception as e:
            logger.error(f"RAG initialization failed: {e}")
            raise
    
    async def ask(self, question: str) -> RAGAnswer:
        """Main RAG query method"""
        start_time = time.time()
        
        try:
            if not self.is_ready:
                await self.initialize()
            
            # Check cache first
            if question in self._response_cache:
                cache_time = self._cache_timestamps.get(question, 0)
                if time.time() - cache_time < 3600:  # 1 hour cache
                    cached_answer = self._response_cache[question]
                    cached_answer.processing_time = time.time() - start_time
                    return cached_answer
            
            # Retrieve relevant context
            context_data = await self._retrieve_context(question)
            
            # Generate answer
            answer = await self._generate_answer(question, context_data)
            
            # Create response
            response = RAGAnswer(
                question=question,
                answer=answer,
                sources=context_data.get("sources", []),
                processing_time=time.time() - start_time,
                confidence=context_data.get("confidence", 0.8),
                chunks_analyzed=len(context_data.get("chunks", [])),
                context_length=len(context_data.get("context", "")),
                retrieval_methods=context_data.get("methods", ["semantic"])
            )
            
            # Cache response
            self._response_cache[question] = response
            self._cache_timestamps[question] = time.time()
            
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return RAGAnswer(
                question=question,
                answer="I apologize, but I'm unable to process your question right now. Please try again.",
                sources=[],
                processing_time=time.time() - start_time,
                confidence=0.0,
                chunks_analyzed=0,
                context_length=0,
                retrieval_methods=[]
            )
    
    async def _retrieve_context(self, question: str) -> Dict[str, Any]:
        """Retrieve relevant context for question"""
        try:
            # Semantic search
            semantic_results = await self._semantic_search(question)
            
            # Keyword search
            keyword_results = await self._keyword_search(question)
            
            # Combine results
            all_chunks = semantic_results + keyword_results
            
            # Deduplicate and rank
            unique_chunks = []
            seen_ids = set()
            for chunk in all_chunks:
                chunk_id = chunk.get("id", "")
                if chunk_id not in seen_ids:
                    unique_chunks.append(chunk)
                    seen_ids.add(chunk_id)
            
            # Sort by relevance score
            unique_chunks.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # Take top results
            top_chunks = unique_chunks[:self.config["hybrid_top_k"]]
            
            # Build context
            context = "\n\n".join([chunk.get("content", "") for chunk in top_chunks])
            sources = [chunk.get("source", "") for chunk in top_chunks]
            
            return {
                "context": context[:self.config["max_context_length"]],
                "sources": sources,
                "chunks": top_chunks,
                "confidence": max([chunk.get("score", 0) for chunk in top_chunks]) if top_chunks else 0.0,
                "methods": ["semantic", "keyword"]
            }
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return {
                "context": "",
                "sources": [],
                "chunks": [],
                "confidence": 0.0,
                "methods": []
            }
    
    async def _semantic_search(self, query: str) -> List[Dict]:
        """Semantic search in vector database"""
        try:
            if not self.collection:
                return []
            
            # Query vector database
            results = self.collection.query(
                query_texts=[f"query: {query}"],
                n_results=self.config["semantic_top_k"]
            )
            
            # Format results
            chunks = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    chunks.append({
                        "id": results["ids"][0][i] if results["ids"] else f"semantic_{i}",
                        "content": doc,
                        "source": results["metadatas"][0][i].get("source", "unknown") if results["metadatas"] else "unknown",
                        "score": 1.0 - results["distances"][0][i] if results["distances"] else 0.8,
                        "method": "semantic"
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(self, query: str) -> List[Dict]:
        """Keyword-based search"""
        try:
            if not self.collection:
                return []
            
            # Simple keyword matching
            # This would need to be implemented based on metadata or content filtering
            # For now, return empty as this is a basic implementation
            return []
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    async def _generate_answer(self, question: str, context_data: Dict[str, Any]) -> str:
        """Generate answer using Mistral"""
        try:
            context = context_data.get("context", "")
            
            # Build prompt
            prompt = f"""You are a helpful assistant for StreamWorks support. Answer the question based on the provided context.

Context:
{context}

Question: {question}

Answer in German, be concise and helpful. If the context doesn't contain enough information, say so clearly."""
            
            # Call Mistral
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.config["mistral_model"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config["temperature"],
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
                
                async with session.post(
                    f"{self.config['ollama_url']}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "Unable to generate answer")
                    else:
                        logger.error(f"Mistral API error: {response.status}")
                        return "Unable to generate answer due to service error"
                        
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "Unable to generate answer due to technical error"
    
    async def _test_mistral_connection(self):
        """Test Mistral connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config['ollama_url']}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        if self.config["mistral_model"] in models:
                            logger.info(f"Mistral model '{self.config['mistral_model']}' available")
                        else:
                            logger.warning(f"Mistral model '{self.config['mistral_model']}' not found")
                    else:
                        logger.warning(f"Mistral service not responding: {response.status}")
                        
        except Exception as e:
            logger.warning(f"Mistral connection test failed: {e}")
    
    async def add_documents(self, documents: List[Dict]) -> int:
        """Add documents to the knowledge base"""
        try:
            if not self.collection:
                await self.initialize()
            
            # Prepare documents for ChromaDB
            ids = []
            docs = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = doc.get("id", f"doc_{int(time.time())}_{i}")
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                ids.append(doc_id)
                docs.append(content)
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to knowledge base")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Document addition failed: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
        try:
            stats = {
                "is_ready": self.is_ready,
                "collection_count": self.collection.count() if self.collection else 0,
                "embedding_model": self.config["embedding_model"],
                "mistral_model": self.config["mistral_model"],
                "cache_size": len(self._response_cache),
                "config": self.config
            }
            return stats
            
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {"is_ready": False, "error": str(e)}

# Global RAG service instance
rag_service = RAGService()