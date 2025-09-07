"""
Reranker Service für Streamworks RAG MVP
Optional reranking mit Cohere oder Jina für bessere Relevanz
"""

import asyncio
from typing import List, Dict, Any, Optional
import httpx
import json

from config import settings

class RerankerService:
    """Service für reranking retrieved chunks"""
    
    def __init__(self):
        self.provider = settings.RERANKER_PROVIDER
        self.api_key = settings.RERANKER_API_KEY
        
        if self.provider == "none" or not self.api_key:
            self.enabled = False
        else:
            self.enabled = True
            
        self.client = httpx.AsyncClient()
    
    async def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks based on query relevance
        
        Args:
            query: Search query
            chunks: Retrieved chunks from vector search
            top_k: Number of top results to return
            
        Returns:
            Reranked chunks with relevance scores
        """
        if len(chunks) <= top_k:
            return chunks[:top_k]
        
        try:
            # Always use local reranking first (fast and free)
            reranked = await self._rerank_local(query, chunks, top_k)
            
            # If external reranker is enabled, use it as well
            if self.enabled and self.provider in ["cohere", "jina"]:
                if self.provider == "cohere":
                    return await self._rerank_cohere(query, reranked, top_k)
                elif self.provider == "jina":
                    return await self._rerank_jina(query, reranked, top_k)
            
            return reranked
                
        except Exception as e:
            print(f"❌ Reranking failed: {str(e)}, falling back to original ranking")
            return chunks[:top_k]
    
    async def _rerank_local(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Local lexical reranking using keyword matching and TF-IDF-like scoring
        """
        try:
            import re
            from collections import Counter
            
            # Normalize query
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            
            # Calculate relevance scores for each chunk
            scored_chunks = []
            for chunk in chunks:
                content = chunk['content'].lower()
                content_words = re.findall(r'\b\w+\b', content)
                content_word_count = Counter(content_words)
                
                # Calculate different relevance signals
                exact_matches = sum(content_word_count[word] for word in query_words if word in content_word_count)
                word_coverage = len(query_words.intersection(content_word_count.keys())) / max(len(query_words), 1)
                
                # Check for phrase matches
                phrase_bonus = 0
                if len(query.split()) > 1:
                    if query.lower() in content:
                        phrase_bonus = 2.0
                
                # Position bonus (earlier matches score higher)
                position_bonus = 0
                for word in query_words:
                    pos = content.find(word)
                    if pos >= 0:
                        position_bonus += max(0, 1.0 - (pos / len(content)))
                
                # Combine scores with weights
                local_score = (
                    exact_matches * 1.0 +           # Raw keyword frequency
                    word_coverage * 2.0 +           # Query coverage
                    phrase_bonus +                  # Exact phrase bonus
                    position_bonus * 0.5 +          # Position bonus
                    chunk.get('similarity_score', 0) * 3.0  # Vector similarity (strongest signal)
                )
                
                chunk_copy = chunk.copy()
                chunk_copy['local_rerank_score'] = local_score
                chunk_copy['keyword_matches'] = exact_matches
                chunk_copy['word_coverage'] = word_coverage
                scored_chunks.append(chunk_copy)
            
            # Sort by combined score
            scored_chunks.sort(key=lambda x: x['local_rerank_score'], reverse=True)
            
            print(f"✅ Local reranking completed: {len(scored_chunks)} chunks scored")
            return scored_chunks[:top_k]
            
        except Exception as e:
            print(f"❌ Local reranking failed: {str(e)}")
            return chunks[:top_k]
    
    async def _rerank_cohere(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Rerank using Cohere rerank API"""
        try:
            # Prepare documents for Cohere
            documents = [chunk['content'] for chunk in chunks]
            
            payload = {
                "model": "rerank-english-v3.0",
                "query": query,
                "documents": documents,
                "top_n": min(top_k, len(documents)),
                "return_documents": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                "https://api.cohere.ai/v1/rerank",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Reorder chunks based on Cohere ranking
            reranked_chunks = []
            for ranking in result["results"]:
                original_index = ranking["index"]
                relevance_score = ranking["relevance_score"]
                
                chunk = chunks[original_index].copy()
                chunk["rerank_score"] = relevance_score
                chunk["original_rank"] = original_index
                reranked_chunks.append(chunk)
            
            print(f"✅ Cohere reranking completed: {len(reranked_chunks)} chunks")
            return reranked_chunks
            
        except Exception as e:
            print(f"❌ Cohere reranking failed: {str(e)}")
            raise
    
    async def _rerank_jina(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Rerank using Jina rerank API"""
        try:
            # Prepare documents for Jina
            documents = [
                {
                    "text": chunk['content'],
                    "id": i
                }
                for i, chunk in enumerate(chunks)
            ]
            
            payload = {
                "model": "jina-reranker-v1-base-en",
                "query": query,
                "documents": documents,
                "top_n": min(top_k, len(documents))
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                "https://api.jina.ai/v1/rerank",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Reorder chunks based on Jina ranking
            reranked_chunks = []
            for ranking in result["results"]:
                original_index = ranking["document"]["id"]
                relevance_score = ranking["relevance_score"]
                
                chunk = chunks[original_index].copy()
                chunk["rerank_score"] = relevance_score
                chunk["original_rank"] = original_index
                reranked_chunks.append(chunk)
            
            print(f"✅ Jina reranking completed: {len(reranked_chunks)} chunks")
            return reranked_chunks
            
        except Exception as e:
            print(f"❌ Jina reranking failed: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            asyncio.create_task(self.close())
        except:
            pass