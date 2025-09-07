"""
Local Cross-Encoder Reranker
Uses sentence-transformers for local reranking without API dependencies
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .base_reranker import BaseReranker, RerankRequest, RerankResponse, RerankedResult

logger = logging.getLogger(__name__)


class LocalReranker(BaseReranker):
    """
    Local cross-encoder reranker using sentence-transformers
    
    Provides high-quality reranking without external API dependencies.
    Optimized for MacBook Air M1 with MPS acceleration.
    """
    
    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    ALTERNATIVE_MODELS = [
        "cross-encoder/ms-marco-MiniLM-L-6-v2",    # Faster, slightly lower quality
        "cross-encoder/ms-marco-TinyBERT-L-2-v2",  # Fastest, good for development
        "cross-encoder/ms-marco-electra-base",      # Higher quality, slower
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Configuration
        self.model_name = self.config.get('model', self.DEFAULT_MODEL)
        self.device = self._detect_device()
        self.max_length = self.config.get('max_length', 512)
        self.batch_size = self.config.get('batch_size', 32)
        self.top_k_default = self.config.get('top_k', 5)
        
        # Runtime objects (initialized in initialize())
        self.model = None
        self._model_cache_dir = Path(self.config.get('cache_dir', './models/rerankers'))
        
        logger.info(f"LocalReranker configured with model: {self.model_name}")
    
    def _detect_device(self) -> str:
        """Detect optimal device for model inference"""
        device = self.config.get('device', 'auto')
        
        if device == 'auto':
            try:
                import torch
                if torch.backends.mps.is_available():
                    return 'mps'  # Apple Silicon optimized
                elif torch.cuda.is_available():
                    return 'cuda'
                else:
                    return 'cpu'
            except ImportError:
                logger.warning("PyTorch not available, falling back to CPU")
                return 'cpu'
        
        return device
    
    async def initialize(self) -> None:
        """Initialize the cross-encoder model"""
        if self.is_initialized:
            return
            
        try:
            logger.info(f"Initializing LocalReranker with model: {self.model_name}")
            
            # Import sentence-transformers (lazy import for optional dependency)
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required for LocalReranker. "
                    "Install with: pip install sentence-transformers"
                ) from e
            
            # Create cache directory
            self._model_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load model with error handling for different models
            model_loaded = False
            models_to_try = [self.model_name] + [
                m for m in self.ALTERNATIVE_MODELS if m != self.model_name
            ]
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Attempting to load model: {model_name}")
                    
                    self.model = CrossEncoder(
                        model_name,
                        max_length=self.max_length,
                        device=self.device,
                        trust_remote_code=False  # Security best practice
                    )
                    
                    self.model_name = model_name  # Update to actually loaded model
                    model_loaded = True
                    logger.info(f"Successfully loaded model: {model_name} on device: {self.device}")
                    break
                    
                except Exception as e:
                    logger.warning(f"Failed to load model {model_name}: {str(e)}")
                    continue
            
            if not model_loaded:
                raise RuntimeError("Failed to load any cross-encoder model")
                
            self.is_initialized = True
            
            # Performance test
            await self._performance_test()
            
        except Exception as e:
            logger.error(f"Failed to initialize LocalReranker: {str(e)}")
            self.is_initialized = False
            raise
    
    async def _performance_test(self) -> None:
        """Run a quick performance test"""
        try:
            start_time = time.time()
            
            # Test with sample data
            test_pairs = [
                ("What is machine learning?", "Machine learning is a subset of AI"),
                ("What is machine learning?", "The weather is nice today")
            ]
            
            scores = self.model.predict(test_pairs)
            test_time = (time.time() - start_time) * 1000
            
            logger.info(f"Performance test completed in {test_time:.1f}ms")
            logger.debug(f"Test scores: {scores}")
            
        except Exception as e:
            logger.warning(f"Performance test failed: {str(e)}")
    
    async def rerank(self, request: RerankRequest) -> RerankResponse:
        """
        Rerank documents using cross-encoder
        
        Args:
            request: RerankRequest with query and documents
            
        Returns:
            RerankResponse with reranked results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Extract content from documents
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
            
            # Prepare query-document pairs for cross-encoder
            pairs = []
            valid_docs = []
            
            for doc in documents:
                content = self._extract_content(doc)
                if content.strip():  # Only process non-empty content
                    pairs.append((query, content))
                    valid_docs.append(doc)
            
            if not pairs:
                logger.warning("No valid documents with content found for reranking")
                return RerankResponse(
                    results=[],
                    total_processed=len(documents),
                    processing_time_ms=(time.time() - start_time) * 1000,
                    provider=self.provider_name
                )
            
            # Predict relevance scores
            logger.debug(f"Reranking {len(pairs)} documents with query: '{query[:50]}...'")
            
            # Run prediction (this is the CPU/GPU intensive part)
            relevance_scores = await asyncio.get_event_loop().run_in_executor(
                None, self.model.predict, pairs
            )
            
            # Create reranked results
            reranked_results = []
            for i, (doc, score) in enumerate(zip(valid_docs, relevance_scores)):
                original_score = doc.get('similarity_score', 0.0)
                
                result = RerankedResult(
                    content=self._extract_content(doc),
                    metadata=self._extract_metadata(doc, request.metadata_fields),
                    original_score=float(original_score),
                    rerank_score=float(score),
                    rank_position=i + 1
                )
                reranked_results.append(result)
            
            # Sort by rerank score (descending)
            reranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
            
            # Update rank positions and limit to top_k
            final_results = []
            for i, result in enumerate(reranked_results[:top_k]):
                result.rank_position = i + 1
                final_results.append(result)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Reranked {len(documents)} documents to top {len(final_results)} "
                f"in {processing_time_ms:.1f}ms"
            )
            
            return RerankResponse(
                results=final_results,
                total_processed=len(documents),
                processing_time_ms=processing_time_ms,
                provider=self.provider_name,
                model_info=self.model_info
            )
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Return original order as fallback
            fallback_results = []
            for i, doc in enumerate(documents[:top_k]):
                result = RerankedResult(
                    content=self._extract_content(doc),
                    metadata=self._extract_metadata(doc, request.metadata_fields),
                    original_score=doc.get('similarity_score', 0.0),
                    rerank_score=0.0,  # No reranking score available
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
    
    def is_available(self) -> bool:
        """Check if the reranker is available and functional"""
        try:
            # Check if model is loaded
            if not self.is_initialized or self.model is None:
                return False
            
            # Basic functionality test
            test_scores = self.model.predict([("test", "test")])
            return len(test_scores) > 0 and not any(
                score != score for score in test_scores  # NaN check
            )
            
        except Exception as e:
            logger.debug(f"Availability check failed: {str(e)}")
            return False
    
    @property
    def provider_name(self) -> str:
        """Get provider name"""
        return "local"
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = {
            "provider": self.provider_name,
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "batch_size": self.batch_size,
            "initialized": self.is_initialized
        }
        
        if self.model is not None:
            try:
                # Add model-specific info if available
                info["model_type"] = "CrossEncoder"
                info["framework"] = "sentence-transformers"
                
                # Try to get model parameters count (if available)
                try:
                    if hasattr(self.model.model, 'num_parameters'):
                        info["parameters"] = self.model.model.num_parameters()
                except:
                    pass  # Not critical
                    
            except Exception:
                pass  # Model info is optional
        
        return info
    
    async def cleanup(self) -> None:
        """Clean up model resources"""
        if self.model is not None:
            try:
                # Move model to CPU to free GPU/MPS memory
                if hasattr(self.model, 'model'):
                    self.model.model.cpu()
                    
                # Clear CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    elif torch.backends.mps.is_available():
                        torch.mps.empty_cache()
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Cleanup warning: {str(e)}")
            
            self.model = None
            self.is_initialized = False
            logger.info("LocalReranker cleaned up successfully")