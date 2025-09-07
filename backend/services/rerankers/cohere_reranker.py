"""
Cohere API Reranker
Migrates existing Cohere reranking functionality to modular architecture
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
import logging
import httpx

from .base_reranker import BaseReranker, RerankRequest, RerankResponse, RerankedResult

logger = logging.getLogger(__name__)


class CohereReranker(BaseReranker):
    """
    Cohere API-based reranker implementation
    
    Migrates existing Cohere functionality from services/reranker.py
    to the new modular architecture.
    """
    
    COHERE_API_URL = "https://api.cohere.ai/v1/rerank"
    DEFAULT_MODEL = "rerank-english-v2.0"
    ALTERNATIVE_MODELS = [
        "rerank-multilingual-v2.0",  # For multilingual content
        "rerank-english-v3.0",       # Newer model if available
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Configuration
        self.api_key = self.config.get('api_key') or self.config.get('RERANKER_API_KEY')
        self.model = self.config.get('model', self.DEFAULT_MODEL)
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout = self.config.get('timeout', 30)
        self.top_k_default = self.config.get('top_k', 5)
        
        # HTTP client
        self.client = None
        
        if not self.api_key:
            logger.warning("Cohere API key not provided - reranker will not be functional")
    
    async def initialize(self) -> None:
        """Initialize the Cohere API client"""
        if self.is_initialized:
            return
            
        try:
            if not self.api_key:
                raise ValueError("Cohere API key is required")
            
            # Initialize HTTP client with proper headers
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "Streamworks-RAG/1.0"
                },
                timeout=httpx.Timeout(self.timeout)
            )
            
            # Test API connection
            await self._test_connection()
            
            self.is_initialized = True
            logger.info(f"CohereReranker initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CohereReranker: {str(e)}")
            self.is_initialized = False
            raise
    
    async def _test_connection(self) -> None:
        """Test Cohere API connection with minimal request"""
        try:
            test_data = {
                "model": self.model,
                "query": "test query",
                "documents": ["test document"],
                "top_n": 1
            }
            
            response = await self.client.post(
                self.COHERE_API_URL,
                json=test_data,
                timeout=5  # Short timeout for connection test
            )
            
            if response.status_code == 200:
                logger.debug("Cohere API connection test successful")
            else:
                logger.warning(f"Cohere API test returned status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Cohere API connection test failed: {str(e)}")
            # Don't raise here - we'll handle it in actual reranking
    
    async def rerank(self, request: RerankRequest) -> RerankResponse:
        """
        Rerank documents using Cohere API
        
        Args:
            request: RerankRequest with query and documents
            
        Returns:
            RerankResponse with reranked results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            query = request.query
            documents = request.documents
            top_k = request.top_k or self.top_k_default
            
            if not documents:
                return RerankResponse(
                    results=[],
                    total_processed=0,
                    processing_time_ms=0.0,
                    provider=self.provider_name
                )
            
            # Extract text content for Cohere API
            doc_texts = []
            valid_docs = []
            
            for doc in documents:
                content = self._extract_content(doc)
                if content.strip():
                    doc_texts.append(content)
                    valid_docs.append(doc)
            
            if not doc_texts:
                logger.warning("No valid documents with content found for reranking")
                return RerankResponse(
                    results=[],
                    total_processed=len(documents),
                    processing_time_ms=(time.time() - start_time) * 1000,
                    provider=self.provider_name
                )
            
            # Prepare Cohere API request
            api_request = {
                "model": self.model,
                "query": query,
                "documents": doc_texts,
                "top_n": min(len(doc_texts), top_k * 2),  # Get more results to ensure quality
                "return_documents": False  # We already have the documents
            }
            
            logger.debug(f"Sending {len(doc_texts)} documents to Cohere for reranking")
            
            # Call Cohere API with retries
            cohere_response = await self._call_cohere_api(api_request)
            
            # Process Cohere response
            reranked_results = []
            
            if "results" in cohere_response:
                for i, result in enumerate(cohere_response["results"]):
                    doc_index = result.get("index", i)
                    relevance_score = result.get("relevance_score", 0.0)
                    
                    if doc_index < len(valid_docs):
                        original_doc = valid_docs[doc_index]
                        original_score = original_doc.get('similarity_score', 0.0)
                        
                        reranked_result = RerankedResult(
                            content=self._extract_content(original_doc),
                            metadata=self._extract_metadata(original_doc, request.metadata_fields),
                            original_score=float(original_score),
                            rerank_score=float(relevance_score),
                            rank_position=i + 1
                        )
                        reranked_results.append(reranked_result)
                        
                        if len(reranked_results) >= top_k:
                            break
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Cohere reranked {len(documents)} documents to top {len(reranked_results)} "
                f"in {processing_time_ms:.1f}ms"
            )
            
            return RerankResponse(
                results=reranked_results,
                total_processed=len(documents),
                processing_time_ms=processing_time_ms,
                provider=self.provider_name,
                model_info=self.model_info
            )
            
        except Exception as e:
            logger.error(f"Cohere reranking failed: {str(e)}")
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Return fallback results in original order
            fallback_results = []
            for i, doc in enumerate(documents[:top_k]):
                result = RerankedResult(
                    content=self._extract_content(doc),
                    metadata=self._extract_metadata(doc, request.metadata_fields),
                    original_score=doc.get('similarity_score', 0.0),
                    rerank_score=0.0,
                    rank_position=i + 1
                )
                fallback_results.append(result)
            
            return RerankResponse(
                results=fallback_results,
                total_processed=len(documents),
                processing_time_ms=processing_time_ms,
                provider=self.provider_name,
                model_info={"error": str(e)}
            )
    
    async def _call_cohere_api(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Cohere API with retry logic
        
        Args:
            request_data: API request payload
            
        Returns:
            API response data
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    self.COHERE_API_URL,
                    json=request_data
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_detail = ""
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("message", str(error_data))
                    except:
                        error_detail = response.text
                    
                    raise httpx.HTTPError(
                        f"Cohere API error {response.status_code}: {error_detail}"
                    )
                    
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    logger.warning(f"Cohere API attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    break
        
        raise last_exception or Exception("All Cohere API attempts failed")
    
    def is_available(self) -> bool:
        """Check if Cohere reranker is available"""
        return (
            self.is_initialized and 
            self.client is not None and 
            self.api_key is not None and
            len(self.api_key.strip()) > 0
        )
    
    @property
    def provider_name(self) -> str:
        """Get provider name"""
        return "cohere"
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": self.provider_name,
            "model_name": self.model,
            "api_endpoint": self.COHERE_API_URL,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "initialized": self.is_initialized,
            "available": self.is_available()
        }
    
    async def cleanup(self) -> None:
        """Clean up HTTP client resources"""
        if self.client is not None:
            try:
                await self.client.aclose()
            except Exception as e:
                logger.warning(f"Error closing Cohere HTTP client: {str(e)}")
            finally:
                self.client = None
                self.is_initialized = False
                logger.info("CohereReranker cleaned up successfully")