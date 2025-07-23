"""
🧠 ENTERPRISE INTELLIGENT CHUNKER - WORLD-CLASS RAG SYSTEM
Advanced document chunking with semantic awareness and overlap optimization
Built for maximum retrieval performance and enterprise-grade quality

Author: Senior AI Engineer
Version: 1.0.0 (Enterprise Production)
"""

import hashlib
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional

from langchain.schema import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
    # SpacyTextSplitter  # Optional
)

# import spacy  # Optional for advanced NLP

logger = logging.getLogger(__name__)

class ChunkStrategy(Enum):
    """Advanced chunking strategies for different content types"""
    SEMANTIC_OVERLAP = "semantic_overlap"      # Best for Q&A content
    MARKDOWN_HEADERS = "markdown_headers"      # Best for structured docs
    RECURSIVE_SPLIT = "recursive_split"        # Best for technical docs
    QUESTION_ANSWER = "question_answer"        # Best for FAQ content
    HYBRID_INTELLIGENT = "hybrid_intelligent"  # Best overall performance

class ChunkQuality(Enum):
    """Quality assessment for chunks"""
    EXCELLENT = "excellent"    # Perfect semantic unit
    GOOD = "good"             # Good semantic coherence
    ACCEPTABLE = "acceptable"  # Usable but not optimal
    POOR = "poor"             # Fragmented or low quality

@dataclass
class EnterpriseChunk:
    """Enterprise-grade chunk with comprehensive metadata"""
    id: str
    content: str
    content_hash: str
    chunk_index: int
    start_char: int
    end_char: int
    
    # Quality metrics
    quality_score: float      # 0.0-1.0
    semantic_density: float   # Information density
    readability_score: float  # How readable is this chunk
    
    # Context information
    previous_context: str     # Overlap with previous chunk
    next_context: str        # Overlap with next chunk
    
    # Content analysis
    key_concepts: List[str]   # Main concepts in this chunk
    entities: List[str]       # Named entities
    chunk_type: str          # question, answer, definition, etc.
    
    # Metadata
    strategy_used: ChunkStrategy
    quality_assessment: ChunkQuality
    embedding_ready: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "content": self.content,
            "content_hash": self.content_hash,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "quality_score": self.quality_score,
            "semantic_density": self.semantic_density,
            "readability_score": self.readability_score,
            "previous_context": self.previous_context,
            "next_context": self.next_context,
            "key_concepts": self.key_concepts,
            "entities": self.entities,
            "chunk_type": self.chunk_type,
            "strategy_used": self.strategy_used.value,
            "quality_assessment": self.quality_assessment.value,
            "embedding_ready": self.embedding_ready
        }

class EnterpriseIntelligentChunker:
    """🧠 World-class intelligent chunking system"""
    
    def __init__(self):
        self.nlp = None
        self.config = {
            # Chunk size configuration
            "target_chunk_size": 600,      # Optimal for embeddings
            "max_chunk_size": 1000,        # Hard limit
            "min_chunk_size": 100,         # Minimum meaningful size
            "overlap_size": 150,           # Context preservation
            
            # Quality thresholds
            "min_quality_score": 0.6,      # Minimum acceptable quality
            "excellent_threshold": 0.85,    # Excellent quality threshold
            
            # Semantic analysis
            "extract_entities": True,       # Extract named entities
            "analyze_concepts": True,       # Analyze key concepts
            "assess_readability": True,     # Readability scoring
            
            # Performance optimization
            "parallel_processing": True,    # Parallel chunk processing
            "cache_nlp_results": True,     # Cache NLP analysis
            "optimize_embeddings": True     # Optimize for embedding models
        }
        
        logger.info("🧠 Enterprise Intelligent Chunker initialized")
    
    async def initialize_nlp(self):
        """Initialize NLP pipeline for advanced analysis"""
        try:
            import spacy
            # Load German model for StreamWorks content
            self.nlp = spacy.load("de_core_news_sm")
            logger.info("✅ German NLP model loaded")
        except Exception as e:
            logger.warning(f"⚠️ NLP model not available: {e} - Using fallback analysis")
            self.nlp = None
    
    async def intelligent_chunking(
        self, 
        content: str, 
        filename: str,
        strategy: ChunkStrategy = ChunkStrategy.HYBRID_INTELLIGENT
    ) -> List[EnterpriseChunk]:
        """
        🎯 MAIN CHUNKING FUNCTION - ENTERPRISE INTELLIGENCE
        Creates semantically aware chunks with optimal overlap
        """
        logger.info(f"🧠 Intelligent chunking: {filename} with {strategy.value}")
        
        # Initialize NLP if not done
        if self.nlp is None:
            await self.initialize_nlp()
        
        # Pre-process content
        cleaned_content = self._preprocess_content(content)
        
        # Choose optimal strategy based on content analysis
        if strategy == ChunkStrategy.HYBRID_INTELLIGENT:
            strategy = self._analyze_optimal_strategy(cleaned_content)
        
        # Apply selected chunking strategy
        chunks = await self._apply_chunking_strategy(cleaned_content, strategy, filename)
        
        # Post-process chunks for quality
        optimized_chunks = await self._optimize_chunks(chunks, filename)
        
        logger.info(f"✅ Created {len(optimized_chunks)} enterprise chunks")
        return optimized_chunks
    
    def _preprocess_content(self, content: str) -> str:
        """Advanced content preprocessing for optimal chunking"""
        # Remove metadata noise
        content = re.sub(r'^#\s*Training Data.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Automatisch generiert.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Konvertiert am.*$', '', content, flags=re.MULTILINE)
        
        # Normalize whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Fix common OCR/conversion issues
        content = re.sub(r'(\w)-\s*\n(\w)', r'\1\2', content)  # Fix hyphenated words
        content = re.sub(r'([.!?])\s*\n([A-Z])', r'\1 \2', content)  # Fix sentence breaks
        
        return content.strip()
    
    def _analyze_optimal_strategy(self, content: str) -> ChunkStrategy:
        """Analyze content to determine optimal chunking strategy"""
        # Count markdown headers
        header_count = len(re.findall(r'^#+\s', content, re.MULTILINE))
        
        # Count Q&A patterns
        qa_patterns = [
            r'❓.*?\n.*?A:',
            r'Frage:.*?\n.*?Antwort:',
            r'\?\s*\n.*?[.!]',
            r'Problem:.*?\n.*?Lösung:'
        ]
        qa_count = sum(len(re.findall(pattern, content, re.MULTILINE | re.DOTALL)) for pattern in qa_patterns)
        
        # Analyze content structure
        lines = content.split('\n')
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        
        # Decision logic
        if header_count > 3 and avg_line_length > 50:
            return ChunkStrategy.MARKDOWN_HEADERS
        elif qa_count > 2:
            return ChunkStrategy.QUESTION_ANSWER
        elif len(content) > 3000:
            return ChunkStrategy.SEMANTIC_OVERLAP
        else:
            return ChunkStrategy.RECURSIVE_SPLIT
    
    async def _apply_chunking_strategy(
        self, 
        content: str, 
        strategy: ChunkStrategy, 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Apply the selected chunking strategy"""
        
        if strategy == ChunkStrategy.MARKDOWN_HEADERS:
            return await self._markdown_header_chunking(content, filename)
        elif strategy == ChunkStrategy.QUESTION_ANSWER:
            return await self._question_answer_chunking(content, filename)
        elif strategy == ChunkStrategy.SEMANTIC_OVERLAP:
            return await self._semantic_overlap_chunking(content, filename)
        else:
            return await self._recursive_split_chunking(content, filename)
    
    async def _semantic_overlap_chunking(
        self, 
        content: str, 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Advanced semantic chunking with intelligent overlap"""
        chunks = []
        
        # Use spaCy for sentence boundaries if available
        if self.nlp:
            doc = self.nlp(content)
            sentences = [sent.text.strip() for sent in doc.sents]
        else:
            # Fallback to regex-based sentence splitting
            sentences = re.split(r'[.!?]\s+', content)
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        start_char = 0
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed target size
            if current_size + len(sentence) > self.config["target_chunk_size"] and current_chunk:
                # Create chunk
                chunk_content = '. '.join(current_chunk) + '.'
                chunk = await self._create_enterprise_chunk(
                    chunk_content, chunk_index, start_char, 
                    start_char + len(chunk_content), filename,
                    ChunkStrategy.SEMANTIC_OVERLAP
                )
                chunks.append(chunk)
                
                # Prepare next chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_size = sum(len(s) for s in current_chunk)
                chunk_index += 1
                start_char += len(chunk_content) - sum(len(s) for s in overlap_sentences)
            else:
                current_chunk.append(sentence)
                current_size += len(sentence)
        
        # Handle remaining content
        if current_chunk:
            chunk_content = '. '.join(current_chunk)
            if not chunk_content.endswith('.'):
                chunk_content += '.'
            chunk = await self._create_enterprise_chunk(
                chunk_content, chunk_index, start_char, 
                start_char + len(chunk_content), filename,
                ChunkStrategy.SEMANTIC_OVERLAP
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _markdown_header_chunking(
        self, 
        content: str, 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Intelligent markdown header-based chunking"""
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )
        
        docs = splitter.split_text(content)
        chunks = []
        
        for i, doc in enumerate(docs):
            chunk = await self._create_enterprise_chunk(
                doc.page_content, i, 0, len(doc.page_content), 
                filename, ChunkStrategy.MARKDOWN_HEADERS
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _question_answer_chunking(
        self, 
        content: str, 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Specialized Q&A chunking for FAQ content"""
        chunks = []
        chunk_index = 0
        
        # Extract Q&A pairs
        qa_patterns = [
            r'❓\s*([^?]+\?)\s*A:\s*([^❓]+)',
            r'Frage:\s*([^?]+\?)\s*Antwort:\s*([^F]+)',
            r'Problem:\s*([^?]+\?)\s*Lösung:\s*([^P]+)'
        ]
        
        for pattern in qa_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                question = match.group(1).strip()
                answer = match.group(2).strip()
                
                qa_content = f"FRAGE: {question}\nANTWORT: {answer}"
                
                chunk = await self._create_enterprise_chunk(
                    qa_content, chunk_index, match.start(), 
                    match.end(), filename, ChunkStrategy.QUESTION_ANSWER
                )
                chunk.chunk_type = "qa_pair"
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
    
    async def _recursive_split_chunking(
        self, 
        content: str, 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Fallback recursive chunking with overlap"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["target_chunk_size"],
            chunk_overlap=self.config["overlap_size"],
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        docs = splitter.split_text(content)
        chunks = []
        
        for i, doc_content in enumerate(docs):
            chunk = await self._create_enterprise_chunk(
                doc_content, i, 0, len(doc_content), 
                filename, ChunkStrategy.RECURSIVE_SPLIT
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _create_enterprise_chunk(
        self, 
        content: str, 
        chunk_index: int, 
        start_char: int, 
        end_char: int, 
        filename: str,
        strategy: ChunkStrategy
    ) -> EnterpriseChunk:
        """Create enterprise-grade chunk with full analysis"""
        
        # Generate unique ID
        chunk_id = f"{filename}_{chunk_index}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Analyze content
        key_concepts = self._extract_key_concepts(content)
        entities = self._extract_entities(content)
        chunk_type = self._classify_chunk_type(content)
        
        # Calculate quality metrics
        quality_score = self._calculate_quality_score(content)
        semantic_density = self._calculate_semantic_density(content)
        readability_score = self._calculate_readability_score(content)
        
        # Quality assessment
        if quality_score >= self.config["excellent_threshold"]:
            quality = ChunkQuality.EXCELLENT
        elif quality_score >= 0.75:
            quality = ChunkQuality.GOOD
        elif quality_score >= self.config["min_quality_score"]:
            quality = ChunkQuality.ACCEPTABLE
        else:
            quality = ChunkQuality.POOR
        
        return EnterpriseChunk(
            id=chunk_id,
            content=content,
            content_hash=content_hash,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            quality_score=quality_score,
            semantic_density=semantic_density,
            readability_score=readability_score,
            previous_context="",  # Will be filled during optimization
            next_context="",      # Will be filled during optimization
            key_concepts=key_concepts,
            entities=entities,
            chunk_type=chunk_type,
            strategy_used=strategy,
            quality_assessment=quality,
            embedding_ready=True
        )
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts using advanced NLP"""
        if not self.nlp:
            # Fallback: extract important terms
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
            return list(set(words))[:10]
        
        doc = self.nlp(content)
        concepts = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3:
                concepts.append(chunk.text)
        
        # Extract important keywords
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                len(token.text) > 3 and 
                not token.is_stop):
                concepts.append(token.text)
        
        return list(set(concepts))[:10]
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities"""
        if not self.nlp:
            # Fallback: extract capitalized words
            entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
            return list(set(entities))[:10]
        
        doc = self.nlp(content)
        entities = [ent.text for ent in doc.ents]
        return list(set(entities))[:10]
    
    def _classify_chunk_type(self, content: str) -> str:
        """Classify the type of chunk"""
        content_lower = content.lower()
        
        if any(marker in content_lower for marker in ['frage:', 'antwort:', '?']):
            return 'qa_pair'
        elif any(marker in content_lower for marker in ['definition', 'ist', 'bedeutet']):
            return 'definition'
        elif any(marker in content_lower for marker in ['problem', 'fehler', 'error']):
            return 'troubleshooting'
        elif any(marker in content_lower for marker in ['schritt', 'anleitung', 'tutorial']):
            return 'instruction'
        elif any(marker in content_lower for marker in ['beispiel', 'example']):
            return 'example'
        else:
            return 'general'
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate overall quality score for chunk"""
        score = 0.0
        
        # Length appropriateness (30% of score)
        length_score = 0.3
        if self.config["min_chunk_size"] <= len(content) <= self.config["target_chunk_size"]:
            length_score = 0.3
        elif len(content) < self.config["min_chunk_size"]:
            length_score = 0.1
        else:
            length_score = 0.2
        
        # Sentence completeness (25% of score)
        sentence_score = 0.25 if content.strip().endswith(('.', '!', '?')) else 0.1
        
        # Information density (25% of score)
        word_count = len(content.split())
        info_density = min(word_count / 100, 1.0) * 0.25
        
        # Readability (20% of score)
        readability = self._calculate_readability_score(content) * 0.2
        
        return length_score + sentence_score + info_density + readability
    
    def _calculate_semantic_density(self, content: str) -> float:
        """Calculate semantic information density"""
        words = content.split()
        if not words:
            return 0.0
        
        # Count unique meaningful words
        meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
        unique_words = set(meaningful_words)
        
        return len(unique_words) / len(words) if words else 0.0
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (simplified)"""
        sentences = re.split(r'[.!?]', content)
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Normalize scores (German text considerations)
        sentence_score = min(avg_sentence_length / 20, 1.0)
        word_score = min(avg_word_length / 8, 1.0)
        
        return (sentence_score + word_score) / 2
    
    async def _optimize_chunks(
        self, 
        chunks: List[EnterpriseChunk], 
        filename: str
    ) -> List[EnterpriseChunk]:
        """Post-process chunks for optimal quality"""
        if not chunks:
            return chunks
        
        # Add context overlap information
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_chunk = chunks[i-1]
                overlap = self._find_overlap(prev_chunk.content, chunk.content)
                chunk.previous_context = overlap
            
            if i < len(chunks) - 1:
                next_chunk = chunks[i+1]
                overlap = self._find_overlap(chunk.content, next_chunk.content)
                chunk.next_context = overlap
        
        # Filter out poor quality chunks
        quality_chunks = [
            chunk for chunk in chunks 
            if chunk.quality_score >= self.config["min_quality_score"]
        ]
        
        # Re-index chunks
        for i, chunk in enumerate(quality_chunks):
            chunk.chunk_index = i
        
        return quality_chunks
    
    def _find_overlap(self, text1: str, text2: str) -> str:
        """Find overlap between two text chunks"""
        # Simple word-based overlap detection
        words1 = text1.split()
        words2 = text2.split()
        
        # Find common ending/beginning
        for i in range(min(len(words1), len(words2), 20)):
            if words1[-(i+1):] == words2[:i+1]:
                return ' '.join(words1[-(i+1):])
        
        return ""

# Global instance
enterprise_chunker = EnterpriseIntelligentChunker()