"""
Contextual Embedder Service

Enhanced embedding service that generates document-aware chunk embeddings by incorporating
document context, hierarchical structure, and domain-specific knowledge into the embedding process.

Key Features:
- Document context injection for better semantic understanding
- Hierarchical position encoding for structural awareness
- Domain-specific embedding enhancements
- Multi-granularity embedding generation
- Embedding cache management and persistence

Author: AI Assistant
Date: 2025-01-XX
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from functools import lru_cache
import hashlib

import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)


class EmbeddingStrategy(Enum):
    BASIC = "basic"
    CONTEXTUAL = "contextual" 
    HIERARCHICAL = "hierarchical"
    DOMAIN_ADAPTIVE = "domain_adaptive"
    MULTI_GRANULAR = "multi_granular"


class DocumentType(Enum):
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    LEGAL = "legal"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    GENERAL = "general"


@dataclass
class ChunkContext:
    """Context information for a document chunk"""
    document_id: str
    document_title: Optional[str] = None
    document_type: DocumentType = DocumentType.GENERAL
    chunk_index: int = 0
    total_chunks: int = 1
    section_title: Optional[str] = None
    hierarchical_level: int = 0
    preceding_context: Optional[str] = None
    following_context: Optional[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    embedding: np.ndarray
    context_embedding: Optional[np.ndarray] = None
    hierarchical_features: Optional[np.ndarray] = None
    domain_features: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EmbeddingPerformanceMetrics:
    """Performance metrics for embedding generation"""
    total_embeddings: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_embedding_time: float = 0.0
    total_processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        if self.total_embeddings == 0:
            return 0.0
        return self.cache_hits / self.total_embeddings


class ContextualEmbedder:
    """Advanced embedding service with document context awareness"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        contextual_model_name: str = "distilbert-base-multilingual-cased",
        cache_dir: Optional[str] = None,
        max_context_length: int = 512,
        embedding_dimension: int = 384,
        enable_gpu: bool = True
    ):
        self.model_name = model_name
        self.contextual_model_name = contextual_model_name
        self.max_context_length = max_context_length
        self.embedding_dimension = embedding_dimension
        self.enable_gpu = enable_gpu
        
        # Initialize cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache/embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
        # Performance tracking
        self.metrics = EmbeddingPerformanceMetrics()
        self._embedding_cache: Dict[str, EmbeddingResult] = {}
        self._domain_keywords: Dict[DocumentType, List[str]] = self._load_domain_keywords()
        
        logger.info(f"ContextualEmbedder initialized with model: {model_name}")
    
    def _initialize_models(self):
        """Initialize embedding models"""
        try:
            # Primary embedding model
            self.embedding_model = SentenceTransformer(self.model_name)
            if self.enable_gpu and torch.cuda.is_available():
                self.embedding_model = self.embedding_model.to('cuda')
                logger.info("Using GPU for embedding generation")
            
            # Contextual model for enhanced embeddings
            self.contextual_tokenizer = AutoTokenizer.from_pretrained(self.contextual_model_name)
            self.contextual_model = AutoModel.from_pretrained(self.contextual_model_name)
            
            if self.enable_gpu and torch.cuda.is_available():
                self.contextual_model = self.contextual_model.to('cuda')
            
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _load_domain_keywords(self) -> Dict[DocumentType, List[str]]:
        """Load domain-specific keywords for enhanced embeddings"""
        return {
            DocumentType.TECHNICAL: [
                "implementation", "algorithm", "specification", "architecture",
                "system", "performance", "optimization", "configuration"
            ],
            DocumentType.ACADEMIC: [
                "research", "methodology", "analysis", "hypothesis", "conclusion",
                "literature", "study", "experimental", "theoretical"
            ],
            DocumentType.LEGAL: [
                "regulation", "compliance", "contract", "liability", "jurisdiction",
                "statute", "precedent", "obligation", "rights"
            ],
            DocumentType.MEDICAL: [
                "diagnosis", "treatment", "symptoms", "patient", "clinical",
                "therapeutic", "medical", "healthcare", "procedure"
            ],
            DocumentType.FINANCIAL: [
                "investment", "portfolio", "risk", "return", "capital", "market",
                "financial", "economic", "asset", "liability"
            ],
            DocumentType.GENERAL: [
                "information", "process", "method", "approach", "concept",
                "principle", "example", "description", "explanation"
            ]
        }
    
    @lru_cache(maxsize=1000)
    def _generate_cache_key(self, content: str, context_str: str, strategy: str) -> str:
        """Generate cache key for embedding"""
        combined = f"{content}|{context_str}|{strategy}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def embed_chunk(
        self,
        content: str,
        context: ChunkContext,
        strategy: EmbeddingStrategy = EmbeddingStrategy.CONTEXTUAL
    ) -> EmbeddingResult:
        """Generate contextual embedding for a document chunk"""
        start_time = time.time()
        
        try:
            # Create cache key
            context_str = json.dumps(asdict(context), sort_keys=True, default=str)
            cache_key = self._generate_cache_key(content, context_str, strategy.value)
            
            # Check cache
            if cache_key in self._embedding_cache:
                self.metrics.cache_hits += 1
                self.metrics.total_embeddings += 1
                return self._embedding_cache[cache_key]
            
            # Generate embedding based on strategy
            if strategy == EmbeddingStrategy.BASIC:
                result = await self._basic_embedding(content)
            elif strategy == EmbeddingStrategy.CONTEXTUAL:
                result = await self._contextual_embedding(content, context)
            elif strategy == EmbeddingStrategy.HIERARCHICAL:
                result = await self._hierarchical_embedding(content, context)
            elif strategy == EmbeddingStrategy.DOMAIN_ADAPTIVE:
                result = await self._domain_adaptive_embedding(content, context)
            elif strategy == EmbeddingStrategy.MULTI_GRANULAR:
                result = await self._multi_granular_embedding(content, context)
            else:
                result = await self._contextual_embedding(content, context)
            
            # Cache result
            self._embedding_cache[cache_key] = result
            self.metrics.cache_misses += 1
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback to basic embedding
            result = await self._basic_embedding(content)
        
        # Update metrics
        processing_time = time.time() - start_time
        self.metrics.total_embeddings += 1
        self.metrics.total_processing_time += processing_time
        self.metrics.avg_embedding_time = (
            self.metrics.total_processing_time / self.metrics.total_embeddings
        )
        
        return result
    
    async def _basic_embedding(self, content: str) -> EmbeddingResult:
        """Generate basic embedding without context"""
        embedding = self.embedding_model.encode(
            content,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return EmbeddingResult(
            embedding=embedding,
            metadata={"strategy": "basic", "model": self.model_name}
        )
    
    async def _contextual_embedding(self, content: str, context: ChunkContext) -> EmbeddingResult:
        """Generate context-aware embedding"""
        # Prepare contextual input
        contextual_text = self._prepare_contextual_input(content, context)
        
        # Generate primary embedding
        primary_embedding = self.embedding_model.encode(
            contextual_text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Generate context-specific features
        context_features = await self._extract_contextual_features(content, context)
        
        return EmbeddingResult(
            embedding=primary_embedding,
            context_embedding=context_features,
            metadata={
                "strategy": "contextual",
                "document_type": context.document_type.value,
                "chunk_position": f"{context.chunk_index}/{context.total_chunks}"
            }
        )
    
    async def _hierarchical_embedding(self, content: str, context: ChunkContext) -> EmbeddingResult:
        """Generate embedding with hierarchical structure awareness"""
        # Generate base contextual embedding
        contextual_result = await self._contextual_embedding(content, context)
        
        # Add hierarchical position encoding
        hierarchical_features = self._generate_hierarchical_features(context)
        
        # Combine embeddings with hierarchical information
        enhanced_embedding = self._combine_embeddings(
            contextual_result.embedding,
            hierarchical_features,
            weights=[0.8, 0.2]
        )
        
        return EmbeddingResult(
            embedding=enhanced_embedding,
            context_embedding=contextual_result.context_embedding,
            hierarchical_features=hierarchical_features,
            metadata={
                "strategy": "hierarchical",
                "hierarchical_level": context.hierarchical_level,
                "section_title": context.section_title
            }
        )
    
    async def _domain_adaptive_embedding(self, content: str, context: ChunkContext) -> EmbeddingResult:
        """Generate domain-adaptive embedding"""
        # Generate hierarchical embedding as base
        hierarchical_result = await self._hierarchical_embedding(content, context)
        
        # Extract domain-specific features
        domain_features = self._extract_domain_features(content, context.document_type)
        
        # Adaptive weighting based on domain characteristics
        domain_weight = self._calculate_domain_weight(content, context.document_type)
        
        # Combine embeddings
        enhanced_embedding = self._combine_embeddings(
            hierarchical_result.embedding,
            domain_features,
            weights=[1.0 - domain_weight, domain_weight]
        )
        
        return EmbeddingResult(
            embedding=enhanced_embedding,
            context_embedding=hierarchical_result.context_embedding,
            hierarchical_features=hierarchical_result.hierarchical_features,
            domain_features=domain_features,
            metadata={
                "strategy": "domain_adaptive",
                "domain_weight": domain_weight,
                "document_type": context.document_type.value
            }
        )
    
    async def _multi_granular_embedding(self, content: str, context: ChunkContext) -> EmbeddingResult:
        """Generate multi-granular embeddings at different levels"""
        # Generate sentence-level embeddings
        sentences = self._split_into_sentences(content)
        sentence_embeddings = []
        
        for sentence in sentences[:5]:  # Limit to first 5 sentences
            if sentence.strip():
                emb = self.embedding_model.encode(
                    sentence,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                sentence_embeddings.append(emb)
        
        # Generate paragraph-level embedding (full content)
        paragraph_embedding = await self._domain_adaptive_embedding(content, context)
        
        # Aggregate sentence embeddings
        if sentence_embeddings:
            sentence_agg = np.mean(sentence_embeddings, axis=0)
            # Combine with paragraph embedding
            final_embedding = self._combine_embeddings(
                paragraph_embedding.embedding,
                sentence_agg,
                weights=[0.7, 0.3]
            )
        else:
            final_embedding = paragraph_embedding.embedding
        
        return EmbeddingResult(
            embedding=final_embedding,
            context_embedding=paragraph_embedding.context_embedding,
            hierarchical_features=paragraph_embedding.hierarchical_features,
            domain_features=paragraph_embedding.domain_features,
            metadata={
                "strategy": "multi_granular",
                "sentence_count": len(sentence_embeddings),
                "total_sentences": len(sentences)
            }
        )
    
    def _prepare_contextual_input(self, content: str, context: ChunkContext) -> str:
        """Prepare input text with context information"""
        contextual_parts = []
        
        # Add document title if available
        if context.document_title:
            contextual_parts.append(f"Document: {context.document_title}")
        
        # Add section title if available
        if context.section_title:
            contextual_parts.append(f"Section: {context.section_title}")
        
        # Add preceding context (truncated)
        if context.preceding_context:
            preceding = context.preceding_context[-100:]  # Last 100 chars
            contextual_parts.append(f"Previous: {preceding}")
        
        # Add main content
        contextual_parts.append(content)
        
        # Add following context (truncated)
        if context.following_context:
            following = context.following_context[:100]  # First 100 chars
            contextual_parts.append(f"Next: {following}")
        
        return " | ".join(contextual_parts)
    
    async def _extract_contextual_features(self, content: str, context: ChunkContext) -> np.ndarray:
        """Extract context-specific features using contextual model"""
        try:
            # Prepare input for contextual model
            context_input = f"{context.document_title or ''} {context.section_title or ''} {content}"
            
            # Tokenize and encode
            inputs = self.contextual_tokenizer(
                context_input,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_context_length,
                padding=True
            )
            
            if self.enable_gpu and torch.cuda.is_available():
                inputs = {k: v.to('cuda') for k, v in inputs.items()}
            
            # Generate contextual features
            with torch.no_grad():
                outputs = self.contextual_model(**inputs)
                # Use CLS token embedding as context features
                context_features = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
            
            return context_features
            
        except Exception as e:
            logger.warning(f"Error extracting contextual features: {e}")
            # Return zero vector as fallback
            return np.zeros(768)  # Default BERT-like dimension
    
    def _generate_hierarchical_features(self, context: ChunkContext) -> np.ndarray:
        """Generate features encoding hierarchical position"""
        features = np.zeros(32)  # 32-dimensional hierarchical encoding
        
        # Position in document
        if context.total_chunks > 1:
            features[0] = context.chunk_index / context.total_chunks
        
        # Hierarchical level encoding
        if context.hierarchical_level < 16:
            features[1 + context.hierarchical_level] = 1.0
        
        # Section presence
        features[17] = 1.0 if context.section_title else 0.0
        
        # Document type encoding
        doc_type_idx = list(DocumentType).index(context.document_type)
        if doc_type_idx < 10:
            features[20 + doc_type_idx] = 1.0
        
        return features
    
    def _extract_domain_features(self, content: str, document_type: DocumentType) -> np.ndarray:
        """Extract domain-specific features"""
        domain_keywords = self._domain_keywords.get(document_type, [])
        
        features = np.zeros(64)  # 64-dimensional domain features
        
        # Keyword presence features
        content_lower = content.lower()
        for i, keyword in enumerate(domain_keywords[:32]):  # First 32 features for keywords
            if keyword in content_lower:
                features[i] = 1.0
        
        # Length-based features
        features[32] = min(len(content) / 1000, 1.0)  # Normalized length
        features[33] = len(content.split()) / 100  # Word count (normalized)
        
        # Complexity features
        avg_word_length = np.mean([len(word) for word in content.split()]) if content.split() else 0
        features[34] = min(avg_word_length / 10, 1.0)
        
        return features
    
    def _calculate_domain_weight(self, content: str, document_type: DocumentType) -> float:
        """Calculate adaptive weight for domain features"""
        domain_keywords = self._domain_keywords.get(document_type, [])
        content_lower = content.lower()
        
        keyword_matches = sum(1 for keyword in domain_keywords if keyword in content_lower)
        keyword_score = keyword_matches / len(domain_keywords) if domain_keywords else 0
        
        # Base weight based on document type
        base_weights = {
            DocumentType.TECHNICAL: 0.3,
            DocumentType.ACADEMIC: 0.25,
            DocumentType.LEGAL: 0.35,
            DocumentType.MEDICAL: 0.4,
            DocumentType.FINANCIAL: 0.3,
            DocumentType.GENERAL: 0.1
        }
        
        base_weight = base_weights.get(document_type, 0.1)
        
        # Adaptive weight based on keyword presence
        adaptive_weight = base_weight + (keyword_score * 0.2)
        
        return min(adaptive_weight, 0.5)  # Cap at 50%
    
    def _combine_embeddings(self, emb1: np.ndarray, emb2: np.ndarray, weights: List[float]) -> np.ndarray:
        """Combine two embeddings with given weights"""
        # Ensure same dimensions
        if len(emb1) != len(emb2):
            min_dim = min(len(emb1), len(emb2))
            emb1 = emb1[:min_dim]
            emb2 = emb2[:min_dim]
        
        # Weighted combination
        combined = weights[0] * emb1 + weights[1] * emb2
        
        # Normalize
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm
        
        return combined
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def embed_batch(
        self,
        chunks: List[Tuple[str, ChunkContext]],
        strategy: EmbeddingStrategy = EmbeddingStrategy.CONTEXTUAL,
        batch_size: int = 32
    ) -> List[EmbeddingResult]:
        """Embed multiple chunks efficiently"""
        results = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_tasks = [
                self.embed_chunk(content, context, strategy)
                for content, context in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch embedding error: {result}")
                    # Add empty result for failed embedding
                    results.append(EmbeddingResult(
                        embedding=np.zeros(self.embedding_dimension),
                        metadata={"error": str(result)}
                    ))
                else:
                    results.append(result)
        
        return results
    
    def get_performance_metrics(self) -> EmbeddingPerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics
    
    def clear_cache(self):
        """Clear embedding cache"""
        self._embedding_cache.clear()
        self.metrics.cache_hits = 0
        self.metrics.cache_misses = 0
        logger.info("Embedding cache cleared")
    
    async def save_cache_to_disk(self, filepath: Optional[str] = None):
        """Save embedding cache to disk"""
        if filepath is None:
            filepath = self.cache_dir / f"embedding_cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            cache_data = {
                key: {
                    "embedding": result.embedding.tolist(),
                    "metadata": result.metadata
                }
                for key, result in self._embedding_cache.items()
            }
            
            with open(filepath, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Embedding cache saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")