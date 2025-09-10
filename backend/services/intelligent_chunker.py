"""
Intelligent Chunking Service für StreamWorks RAG
Semantic-aware chunking mit deutschen Sprachstrukturen und Quality-Gates
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Optional spaCy import with fallback
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types für spezifisches Chunking"""
    PDF = "pdf"
    TEXT = "text"
    HTML = "html" 
    MARKDOWN = "markdown"
    CODE = "code"
    TABLE = "table"


@dataclass
class ChunkingConfig:
    """Konfiguration für intelligentes Chunking"""
    
    # Base settings
    min_chunk_size: int = 200
    max_chunk_size: int = 2000
    overlap_ratio: float = 0.25  # 25% overlap
    
    # Content-type specific
    pdf_chunk_size: int = 2500
    text_chunk_size: int = 1800
    html_chunk_size: int = 1500
    code_chunk_size: int = 1200
    
    # Quality gates
    min_word_count: int = 30
    min_sentence_count: int = 2
    max_repetition_ratio: float = 0.4  # Max 40% repeated content
    min_alpha_ratio: float = 0.7  # Min 70% alphabetic characters
    
    # German language specific
    sentence_endings: List[str] = field(default_factory=lambda: ['.', '!', '?', '...'])
    paragraph_markers: List[str] = field(default_factory=lambda: ['\n\n', '\r\n\r\n'])
    section_markers: List[str] = field(default_factory=lambda: ['#', '##', '###'])
    

@dataclass
class ChunkQuality:
    """Chunk-Quality-Metriken"""
    word_count: int
    sentence_count: int
    alpha_ratio: float
    repetition_ratio: float
    semantic_completeness: float
    content_density: float
    
    @property
    def is_high_quality(self) -> bool:
        return (
            self.word_count >= 30 and
            self.sentence_count >= 2 and
            self.alpha_ratio >= 0.7 and
            self.repetition_ratio <= 0.4 and
            self.semantic_completeness >= 0.6
        )
    
    @property
    def is_acceptable(self) -> bool:
        return (
            self.word_count >= 20 and
            self.sentence_count >= 1 and
            self.alpha_ratio >= 0.5 and
            self.repetition_ratio <= 0.6
        )


class IntelligentChunker:
    """Intelligent chunking mit semantic boundaries und quality gates"""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()
        self.nlp = None
        self._initialize_nlp()
        
    def _initialize_nlp(self):
        """Initialize German NLP model für sentence boundary detection"""
        if not SPACY_AVAILABLE:
            self.nlp = None
            logger.warning("⚠️ spaCy not available - using pattern-based sentence detection")
            return
            
        try:
            # Versuche deutsches Modell zu laden
            self.nlp = spacy.load("de_core_news_sm")
            logger.info("✅ German spaCy model loaded")
        except OSError:
            try:
                # Fallback auf englisches Modell
                self.nlp = spacy.load("en_core_web_sm")
                logger.warning("⚠️ Using English spaCy model - install de_core_news_sm for better German support")
            except OSError:
                # Fallback auf pattern-based sentence detection
                self.nlp = None
                logger.warning("⚠️ No spaCy model available - using pattern-based sentence detection")
    
    def chunk_content(
        self, 
        content: str, 
        content_type: ContentType = ContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Intelligent chunking mit semantic boundaries
        
        Args:
            content: Text content
            content_type: Type of content for specialized chunking
            metadata: Additional metadata
            
        Returns:
            List of high-quality chunks with metadata
        """
        if not content or len(content.strip()) < self.config.min_chunk_size:
            return []
        
        # Get content-specific chunk size
        target_chunk_size = self._get_target_chunk_size(content_type)
        
        # Phase 1: Structure-aware pre-splitting
        sections = self._split_by_structure(content, content_type)
        
        # Phase 2: Semantic boundary chunking
        chunks = []
        for section_content, section_meta in sections:
            section_chunks = self._chunk_with_semantic_boundaries(
                section_content, 
                target_chunk_size,
                content_type
            )
            
            # Add section metadata to chunks
            for chunk_content, chunk_start, chunk_end in section_chunks:
                combined_meta = {**(metadata or {}), **(section_meta or {})}
                chunk_with_meta = {
                    'content': chunk_content,
                    'start_char': chunk_start,
                    'end_char': chunk_end,
                    'metadata': combined_meta
                }
                chunks.append(chunk_with_meta)
        
        # Phase 3: Quality filtering
        quality_chunks = self._apply_quality_gates(chunks)
        
        # Phase 4: Overlap optimization
        final_chunks = self._optimize_overlap(quality_chunks, target_chunk_size)
        
        logger.info(f"Chunking: {len(content)} chars → {len(chunks)} raw → {len(quality_chunks)} quality → {len(final_chunks)} final chunks")
        
        return final_chunks
    
    def _get_target_chunk_size(self, content_type: ContentType) -> int:
        """Get optimal chunk size for content type"""
        size_map = {
            ContentType.PDF: self.config.pdf_chunk_size,
            ContentType.TEXT: self.config.text_chunk_size,
            ContentType.HTML: self.config.html_chunk_size,
            ContentType.CODE: self.config.code_chunk_size,
            ContentType.MARKDOWN: self.config.text_chunk_size,
            ContentType.TABLE: self.config.text_chunk_size
        }
        return size_map.get(content_type, self.config.text_chunk_size)
    
    def _split_by_structure(self, content: str, content_type: ContentType) -> List[Tuple[str, Dict]]:
        """Structure-aware pre-splitting basierend auf document type"""
        
        if content_type == ContentType.HTML:
            return self._split_html_structure(content)
        elif content_type == ContentType.MARKDOWN:
            return self._split_markdown_structure(content)
        elif content_type == ContentType.CODE:
            return self._split_code_structure(content)
        else:
            return self._split_text_structure(content)
    
    def _split_text_structure(self, content: str) -> List[Tuple[str, Dict]]:
        """Split text by paragraphs and sections"""
        sections = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                sections.append((
                    paragraph.strip(),
                    {'section_type': 'paragraph', 'section_index': i}
                ))
        
        return sections
    
    def _split_html_structure(self, content: str) -> List[Tuple[str, Dict]]:
        """Split HTML by semantic elements"""
        sections = []
        
        # Extract headers, paragraphs, lists etc.
        header_pattern = r'<h[1-6][^>]*>(.*?)</h[1-6]>'
        paragraph_pattern = r'<p[^>]*>(.*?)</p>'
        
        # Find headers
        for match in re.finditer(header_pattern, content, re.DOTALL | re.IGNORECASE):
            sections.append((
                match.group(1).strip(),
                {'section_type': 'header', 'tag': match.group(0)[:3]}
            ))
        
        # Find paragraphs
        for match in re.finditer(paragraph_pattern, content, re.DOTALL | re.IGNORECASE):
            sections.append((
                match.group(1).strip(),
                {'section_type': 'paragraph'}
            ))
        
        # If no HTML structure found, fall back to text splitting
        if not sections:
            return self._split_text_structure(content)
        
        return sections
    
    def _split_markdown_structure(self, content: str) -> List[Tuple[str, Dict]]:
        """Split Markdown by headers and sections"""
        sections = []
        
        lines = content.split('\n')
        current_section = []
        current_header = None
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section
                if current_section:
                    sections.append((
                        '\n'.join(current_section).strip(),
                        {'section_type': 'content', 'header': current_header}
                    ))
                    current_section = []
                
                # New header
                current_header = line.strip()
                sections.append((
                    current_header,
                    {'section_type': 'header', 'level': len(line.split()[0])}
                ))
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append((
                '\n'.join(current_section).strip(),
                {'section_type': 'content', 'header': current_header}
            ))
        
        return sections
    
    def _split_code_structure(self, content: str) -> List[Tuple[str, Dict]]:
        """Split code by functions, classes, etc."""
        sections = []
        
        # Detect functions, classes, methods
        function_pattern = r'(def\s+\w+.*?:\n(?:.*?\n)*?(?=\ndef|\nclass|\Z))'
        class_pattern = r'(class\s+\w+.*?:\n(?:.*?\n)*?(?=\nclass|\ndef|\Z))'
        
        # Find classes
        for match in re.finditer(class_pattern, content, re.MULTILINE | re.DOTALL):
            sections.append((
                match.group(1).strip(),
                {'section_type': 'class', 'language': 'python'}
            ))
        
        # Find functions
        for match in re.finditer(function_pattern, content, re.MULTILINE | re.DOTALL):
            sections.append((
                match.group(1).strip(),
                {'section_type': 'function', 'language': 'python'}
            ))
        
        # If no code structure found, use text splitting
        if not sections:
            return self._split_text_structure(content)
        
        return sections
    
    def _chunk_with_semantic_boundaries(
        self, 
        content: str, 
        target_size: int,
        content_type: ContentType
    ) -> List[Tuple[str, int, int]]:
        """Chunk content respecting semantic boundaries"""
        
        if len(content) <= target_size:
            return [(content, 0, len(content))]
        
        # Get sentence boundaries
        sentences = self._get_sentences(content)
        if not sentences:
            # Fallback to character-based chunking
            return self._fallback_chunking(content, target_size)
        
        chunks = []
        current_chunk = []
        current_length = 0
        start_pos = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed target size
            if current_length + sentence_length > target_size and current_chunk:
                # Finalize current chunk
                chunk_content = ' '.join(current_chunk).strip()
                if chunk_content:
                    chunks.append((chunk_content, start_pos, start_pos + current_length))
                
                # Start new chunk
                current_chunk = [sentence]
                current_length = sentence_length
                start_pos = start_pos + current_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk).strip()
            if chunk_content:
                chunks.append((chunk_content, start_pos, start_pos + current_length))
        
        return chunks
    
    def _get_sentences(self, content: str) -> List[str]:
        """Extract sentences using NLP or pattern-based detection"""
        
        if self.nlp:
            # Use spaCy for accurate sentence segmentation
            doc = self.nlp(content)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback: pattern-based sentence detection
            # This is simplified for German - handles common cases
            sentence_endings = r'[.!?](?:\s|$)'
            sentences = re.split(sentence_endings, content)
            return [s.strip() for s in sentences if s.strip()]
    
    def _fallback_chunking(self, content: str, target_size: int) -> List[Tuple[str, int, int]]:
        """Simple character-based chunking as fallback"""
        chunks = []
        start = 0
        
        while start < len(content):
            end = min(start + target_size, len(content))
            
            # Try to break at word boundary
            if end < len(content):
                # Look backwards for space
                while end > start and content[end] != ' ':
                    end -= 1
                if end == start:  # No space found, force break
                    end = min(start + target_size, len(content))
            
            chunk_content = content[start:end].strip()
            if chunk_content:
                chunks.append((chunk_content, start, end))
            
            start = end
        
        return chunks
    
    def _apply_quality_gates(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply quality filters to chunks"""
        quality_chunks = []
        
        for chunk in chunks:
            quality = self._assess_chunk_quality(chunk['content'])
            
            if quality.is_high_quality or quality.is_acceptable:
                chunk['quality_score'] = self._calculate_quality_score(quality)
                chunk['quality_metrics'] = quality
                quality_chunks.append(chunk)
            else:
                logger.debug(f"Filtered low-quality chunk: {len(chunk['content'])} chars, {quality.word_count} words")
        
        return quality_chunks
    
    def _assess_chunk_quality(self, content: str) -> ChunkQuality:
        """Assess quality metrics of a chunk"""
        words = content.split()
        word_count = len(words)
        
        # Count sentences
        sentence_count = len(self._get_sentences(content))
        
        # Calculate alpha ratio
        alpha_chars = sum(1 for c in content if c.isalpha())
        alpha_ratio = alpha_chars / len(content) if content else 0
        
        # Calculate repetition ratio
        repetition_ratio = self._calculate_repetition_ratio(words)
        
        # Estimate semantic completeness (simplified)
        semantic_completeness = self._estimate_semantic_completeness(content)
        
        # Calculate content density
        content_density = len(content.strip()) / len(content) if content else 0
        
        return ChunkQuality(
            word_count=word_count,
            sentence_count=sentence_count,
            alpha_ratio=alpha_ratio,
            repetition_ratio=repetition_ratio,
            semantic_completeness=semantic_completeness,
            content_density=content_density
        )
    
    def _calculate_repetition_ratio(self, words: List[str]) -> float:
        """Calculate how much content is repetitive"""
        if len(words) < 3:
            return 0.0
        
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        repeated_words = sum(count - 1 for count in word_freq.values() if count > 1)
        return repeated_words / len(words) if words else 0
    
    def _estimate_semantic_completeness(self, content: str) -> float:
        """Estimate if chunk contains complete thoughts"""
        # Simplified heuristic - real implementation would use NLP
        
        # Check for sentence endings
        has_sentence_endings = any(ending in content for ending in self.config.sentence_endings)
        
        # Check for complete sentence structure (very basic)
        sentences = self._get_sentences(content)
        complete_sentences = sum(1 for s in sentences if len(s.split()) >= 3 and any(end in s for end in self.config.sentence_endings))
        
        if not sentences:
            return 0.3
        
        completeness = (complete_sentences / len(sentences)) * 0.7
        if has_sentence_endings:
            completeness += 0.3
        
        return min(1.0, completeness)
    
    def _calculate_quality_score(self, quality: ChunkQuality) -> float:
        """Calculate overall quality score"""
        score = 0.0
        
        # Word count component (0-0.3)
        word_score = min(0.3, quality.word_count / 100)
        score += word_score
        
        # Sentence count component (0-0.2)  
        sentence_score = min(0.2, quality.sentence_count / 5)
        score += sentence_score
        
        # Alpha ratio component (0-0.2)
        score += quality.alpha_ratio * 0.2
        
        # Repetition penalty (0-0.1)
        repetition_penalty = quality.repetition_ratio * 0.1
        score -= repetition_penalty
        
        # Semantic completeness (0-0.3)
        score += quality.semantic_completeness * 0.3
        
        return max(0.0, min(1.0, score))
    
    def _optimize_overlap(self, chunks: List[Dict[str, Any]], target_size: int) -> List[Dict[str, Any]]:
        """Optimize overlap between chunks for better context continuity"""
        if len(chunks) <= 1:
            return chunks
        
        overlap_size = int(target_size * self.config.overlap_ratio)
        optimized_chunks = [chunks[0]]  # Keep first chunk as-is
        
        for i in range(1, len(chunks)):
            prev_chunk = optimized_chunks[-1]
            current_chunk = chunks[i]
            
            # Extract overlap from previous chunk
            prev_content = prev_chunk['content']
            current_content = current_chunk['content']
            
            if len(prev_content) > overlap_size:
                # Take last part of previous chunk as context
                overlap_start = len(prev_content) - overlap_size
                # Find sentence boundary for clean overlap
                overlap_content = prev_content[overlap_start:]
                
                # Find first sentence end in overlap for clean break
                for ending in self.config.sentence_endings:
                    if ending in overlap_content:
                        first_end = overlap_content.find(ending)
                        if first_end > len(overlap_content) * 0.3:  # Not too early
                            overlap_content = overlap_content[first_end + len(ending):].strip()
                            break
                
                # Combine overlap with current chunk
                if overlap_content and overlap_content != current_content:
                    current_chunk['content'] = f"{overlap_content} {current_content}".strip()
                    current_chunk['has_overlap'] = True
                    current_chunk['overlap_size'] = len(overlap_content)
            
            optimized_chunks.append(current_chunk)
        
        return optimized_chunks