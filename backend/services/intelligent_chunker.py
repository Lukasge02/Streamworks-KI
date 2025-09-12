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
    """Konfiguration für intelligentes Chunking - 2024 RAG Best Practices"""
    
    # Base settings - 2024 optimierte Größen (~250 tokens ≈ 1000 chars)
    min_chunk_size: int = 150      # ~37 tokens minimum für meaningful content
    max_chunk_size: int = 1200     # ~300 tokens maximum (2024 sweet spot)
    target_chunk_size: int = 1000  # ~250 tokens target (2024 recommendation)
    overlap_ratio: float = 0.15    # 15% overlap für context continuity
    
    # Content-type specific - 2024 standards für bessere semantic coherence
    pdf_chunk_size: int = 1000     # Standard target für PDF (bessere balance)
    text_chunk_size: int = 1000    # Unified target für consistency
    html_chunk_size: int = 1000    # Unified target
    code_chunk_size: int = 800     # Etwas kleiner für code readability
    markdown_chunk_size: int = 1000 # Standard target für markdown
    
    # Quality gates - 2024 optimiert für semantic coherence
    min_word_count: int = 25       # ~6-7 tokens minimum
    min_sentence_count: int = 1    # Ein vollständiger Satz minimum
    max_repetition_ratio: float = 0.3  # Weniger Redundanz
    min_alpha_ratio: float = 0.6   # Realistischer threshold für diverse content
    
    # 2024 RAG-spezifische Quality Gates
    target_word_count: int = 200   # ~50 tokens target (sweet spot für retrieval)
    max_word_count: int = 300      # ~75 tokens maximum
    max_sentence_length: int = 150 # Lesbarkeit threshold
    
    # Semantic coherence thresholds (2024 advanced)
    min_semantic_coherence: float = 0.4  # Minimum für acceptability
    target_semantic_coherence: float = 0.7 # Target für high quality
    
    # Context bridging settings (2024 advanced overlap)
    context_bridge_sentences: int = 1  # Sentences to bridge between chunks
    semantic_overlap_threshold: float = 0.3  # Similarity threshold für bridging
    
    # German language specific
    sentence_endings: List[str] = field(default_factory=lambda: ['.', '!', '?', '...'])
    paragraph_markers: List[str] = field(default_factory=lambda: ['\n\n', '\r\n\r\n'])
    section_markers: List[str] = field(default_factory=lambda: ['#', '##', '###'])
    
    # 2024 Advanced features flags
    enable_hierarchical_chunking: bool = True
    enable_contextual_overlap: bool = True
    enable_semantic_boundary_detection: bool = True
    

@dataclass
class ChunkQuality:
    """2024 Chunk-Quality-Metriken mit erweiterten semantic features"""
    word_count: int
    sentence_count: int
    alpha_ratio: float
    repetition_ratio: float
    semantic_completeness: float
    content_density: float
    
    # 2024 erweiterte Metriken
    token_estimate: int = 0  # Estimated token count (~4 chars per token)
    semantic_coherence: float = 0.0  # Semantic coherence score
    contextual_completeness: float = 0.0  # Context completeness
    
    def __post_init__(self):
        """Calculate derived metrics"""
        # Estimate tokens (rough approximation)
        self.token_estimate = max(1, self.word_count // 4 * 3)  # ~3 tokens per 4 words
    
    @property
    def is_high_quality(self) -> bool:
        """2024 RAG High Quality Kriterien - optimiert für semantic retrieval"""
        return (
            50 <= self.word_count <= 300 and  # 2024 sweet spot range
            self.sentence_count >= 1 and      # Mindestens ein vollständiger Satz
            self.alpha_ratio >= 0.6 and       # Realistischer threshold
            self.repetition_ratio <= 0.3 and  # Weniger Redundanz
            self.semantic_completeness >= 0.7 # Hohe semantische Vollständigkeit
        )
    
    @property
    def is_acceptable(self) -> bool:
        """2024 RAG Akzeptanz-Kriterien - praktikable balance"""
        return (
            25 <= self.word_count <= 400 and  # Erweiterte range für flexibility
            self.sentence_count >= 1 and      # Mindestens ein Satz
            self.alpha_ratio >= 0.5 and       # Niedrigere threshold für diverse content
            self.repetition_ratio <= 0.5 and  # Moderate Redundanz
            self.semantic_completeness >= 0.4 # Grundlegende Kohärenz
        )
    
    @property
    def is_rag_optimized(self) -> bool:
        """2024 RAG-Optimierung: Chunks im 250-token sweet spot"""
        return (
            150 <= self.word_count <= 250 and  # ~37-62 tokens (2024 optimal range)
            self.is_high_quality
        )
    
    @property
    def is_context_complete(self) -> bool:
        """2024 Context completeness check"""
        return (
            self.semantic_completeness >= 0.6 and
            self.contextual_completeness >= 0.5
        )
    
    @property
    def quality_tier(self) -> str:
        """2024 Quality tier classification"""
        if self.is_rag_optimized:
            return "optimal"
        elif self.is_high_quality:
            return "high"
        elif self.is_acceptable:
            return "acceptable"
        else:
            return "poor"
    
    @property
    def retrieval_score(self) -> float:
        """2024 Composite score für retrieval quality (0-1)"""
        # Weight factors based on 2024 research
        word_score = min(1.0, max(0.0, (self.word_count - 25) / 225))  # 25-250 word range
        semantic_score = self.semantic_completeness
        coherence_score = self.semantic_coherence if hasattr(self, 'semantic_coherence') else 0.5
        repetition_penalty = max(0.0, 1.0 - (self.repetition_ratio * 2))
        
        # Weighted composite score
        composite = (
            word_score * 0.25 +
            semantic_score * 0.35 +
            coherence_score * 0.25 +
            repetition_penalty * 0.15
        )
        
        return min(1.0, max(0.0, composite))


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
        """Get optimal chunk size for content type - 2024 optimized"""
        size_map = {
            ContentType.PDF: self.config.pdf_chunk_size,
            ContentType.TEXT: self.config.text_chunk_size,
            ContentType.HTML: self.config.html_chunk_size,
            ContentType.CODE: self.config.code_chunk_size,
            ContentType.MARKDOWN: self.config.markdown_chunk_size,
            ContentType.TABLE: self.config.text_chunk_size
        }
        return size_map.get(content_type, self.config.target_chunk_size)
    
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
        """Assess quality metrics of a chunk - 2024 enhanced"""
        words = content.split()
        word_count = len(words)
        
        # Count sentences
        sentences = self._get_sentences(content)
        sentence_count = len(sentences)
        
        # Calculate alpha ratio
        alpha_chars = sum(1 for c in content if c.isalpha())
        alpha_ratio = alpha_chars / len(content) if content else 0
        
        # Calculate repetition ratio
        repetition_ratio = self._calculate_repetition_ratio(words)
        
        # Estimate semantic completeness (simplified)
        semantic_completeness = self._estimate_semantic_completeness(content)
        
        # Calculate content density
        content_density = len(content.strip()) / len(content) if content else 0
        
        # 2024: Enhanced semantic coherence estimation
        semantic_coherence = self._estimate_semantic_coherence(content, sentences)
        
        # 2024: Contextual completeness
        contextual_completeness = self._estimate_contextual_completeness(content, sentences)
        
        return ChunkQuality(
            word_count=word_count,
            sentence_count=sentence_count,
            alpha_ratio=alpha_ratio,
            repetition_ratio=repetition_ratio,
            semantic_completeness=semantic_completeness,
            content_density=content_density,
            semantic_coherence=semantic_coherence,
            contextual_completeness=contextual_completeness
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
        """Calculate overall quality score - 2024 enhanced with semantic metrics"""
        # Use the new retrieval_score from ChunkQuality
        return quality.retrieval_score
    
    def _estimate_semantic_coherence(self, content: str, sentences: List[str]) -> float:
        """
        2024: Estimate semantic coherence of chunk content
        Simplified heuristic-based approach - could be enhanced with embeddings
        """
        if not sentences or len(sentences) < 1:
            return 0.0
        
        # Basic coherence indicators
        coherence_score = 0.5  # Base score
        
        # Sentence length consistency (coherent chunks have similar sentence lengths)
        if len(sentences) > 1:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            consistency_score = max(0.0, 1.0 - (variance / (avg_length ** 2 + 1)))
            coherence_score = (coherence_score + consistency_score) / 2
        
        # Transition word presence (indicates good flow)
        transition_words = {
            'jedoch', 'aber', 'dennoch', 'außerdem', 'darüber hinaus', 'folglich',
            'daher', 'deshalb', 'somit', 'allerdings', 'hingegen', 'dagegen',
            'also', 'zunächst', 'schließlich', 'dabei', 'furthermore', 'however',
            'therefore', 'moreover', 'consequently', 'nevertheless'
        }
        
        content_lower = content.lower()
        transition_count = sum(1 for word in transition_words if word in content_lower)
        transition_score = min(1.0, transition_count / max(1, len(sentences)))
        
        coherence_score = (coherence_score * 0.7) + (transition_score * 0.3)
        
        return min(1.0, max(0.0, coherence_score))
    
    def _estimate_contextual_completeness(self, content: str, sentences: List[str]) -> float:
        """
        2024: Estimate how contextually complete the chunk is
        """
        if not content or not sentences:
            return 0.0
        
        completeness_score = 0.5  # Base score
        
        # Check for complete sentences (end with proper punctuation)
        complete_sentences = sum(1 for s in sentences if any(s.strip().endswith(end) for end in ['.', '!', '?']))
        if sentences:
            complete_ratio = complete_sentences / len(sentences)
            completeness_score = (completeness_score + complete_ratio) / 2
        
        # Check for balanced parentheses, quotes, etc.
        balance_score = 0.5
        open_chars = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        for open_char, close_char in open_chars.items():
            if open_char == close_char:  # Quotes
                count = content.count(open_char)
                if count % 2 == 0:  # Even number means balanced
                    balance_score += 0.1
            else:  # Brackets
                open_count = content.count(open_char)
                close_count = content.count(close_char)
                if open_count == close_count:
                    balance_score += 0.1
        
        balance_score = min(1.0, balance_score)
        completeness_score = (completeness_score * 0.7) + (balance_score * 0.3)
        
        return min(1.0, max(0.0, completeness_score))
    
    def _optimize_overlap(self, chunks: List[Dict[str, Any]], target_size: int) -> List[Dict[str, Any]]:
        """2024: Enhanced overlap optimization mit semantic awareness"""
        if len(chunks) <= 1:
            return chunks
        
        # Use 2024 configuration settings
        overlap_ratio = self.config.overlap_ratio
        enable_contextual = self.config.enable_contextual_overlap
        enable_semantic = self.config.enable_semantic_boundary_detection
        
        optimized_chunks = [chunks[0]]  # Keep first chunk as-is
        
        for i in range(1, len(chunks)):
            prev_chunk = optimized_chunks[-1]
            current_chunk = chunks[i]
            
            # 2024: Smart overlap based on content analysis
            if enable_contextual:
                overlap_content = self._create_contextual_overlap(
                    prev_chunk['content'], 
                    current_chunk['content'],
                    target_size,
                    overlap_ratio
                )
            else:
                # Fallback to simple overlap
                overlap_content = self._create_simple_overlap(
                    prev_chunk['content'],
                    target_size,
                    overlap_ratio
                )
            
            # Apply overlap if beneficial
            if overlap_content and overlap_content.strip():
                current_chunk['content'] = f"{overlap_content} {current_chunk['content']}".strip()
                current_chunk['has_overlap'] = True
                current_chunk['overlap_size'] = len(overlap_content)
                current_chunk['overlap_type'] = 'contextual' if enable_contextual else 'simple'
            
            optimized_chunks.append(current_chunk)
        
        return optimized_chunks
    
    def _create_contextual_overlap(
        self, 
        prev_content: str, 
        current_content: str, 
        target_size: int, 
        overlap_ratio: float
    ) -> str:
        """2024: Create semantically aware overlap between chunks"""
        
        max_overlap_size = int(target_size * overlap_ratio)
        
        # Get sentences from previous chunk
        prev_sentences = self._get_sentences(prev_content)
        if not prev_sentences:
            return ""
        
        # Strategy 1: Take last N sentences that fit in overlap size
        overlap_sentences = []
        current_size = 0
        
        for sentence in reversed(prev_sentences):
            sentence_size = len(sentence)
            if current_size + sentence_size <= max_overlap_size:
                overlap_sentences.insert(0, sentence)  # Maintain order
                current_size += sentence_size
            else:
                break
        
        if not overlap_sentences:
            # Fallback: take part of last sentence
            last_sentence = prev_sentences[-1]
            if len(last_sentence) > max_overlap_size:
                # Try to break at word boundary
                words = last_sentence.split()
                overlap_words = []
                current_size = 0
                
                for word in reversed(words):
                    if current_size + len(word) + 1 <= max_overlap_size:
                        overlap_words.insert(0, word)
                        current_size += len(word) + 1
                    else:
                        break
                
                return " ".join(overlap_words).strip()
            else:
                return last_sentence.strip()
        
        overlap_content = " ".join(overlap_sentences).strip()
        
        # 2024: Semantic bridge enhancement
        if self.config.context_bridge_sentences > 0:
            # Add context bridge from current chunk beginning
            current_sentences = self._get_sentences(current_content)
            if current_sentences and len(current_sentences) > 0:
                bridge_sentences = current_sentences[:self.config.context_bridge_sentences]
                # Check if adding bridge provides semantic continuity
                if self._should_add_semantic_bridge(overlap_content, bridge_sentences[0]):
                    bridge_text = " ".join(bridge_sentences).strip()
                    if len(overlap_content) + len(bridge_text) + 10 <= max_overlap_size * 1.2:  # Allow slight overflow for bridge
                        overlap_content = f"{overlap_content} [BRIDGE: {bridge_text[:50]}...]"
        
        return overlap_content
    
    def _create_simple_overlap(self, prev_content: str, target_size: int, overlap_ratio: float) -> str:
        """Simple character-based overlap (fallback)"""
        overlap_size = int(target_size * overlap_ratio)
        
        if len(prev_content) <= overlap_size:
            return prev_content
        
        overlap_start = len(prev_content) - overlap_size
        overlap_content = prev_content[overlap_start:]
        
        # Try to start at sentence boundary
        for ending in self.config.sentence_endings:
            if ending in overlap_content:
                first_end = overlap_content.find(ending)
                if first_end > len(overlap_content) * 0.3:  # Not too early
                    overlap_content = overlap_content[first_end + len(ending):].strip()
                    break
        
        return overlap_content
    
    def _should_add_semantic_bridge(self, overlap_content: str, next_sentence: str) -> bool:
        """2024: Determine if semantic bridge would improve coherence"""
        if not overlap_content or not next_sentence:
            return False
        
        # Simple heuristic: add bridge if there are connecting words or concepts
        overlap_words = set(overlap_content.lower().split())
        next_words = set(next_sentence.lower().split())
        
        # Remove common stop words for better analysis
        stop_words = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'mit', 'von', 'zu', 'ist', 'sind', 'the', 'and', 'or', 'but', 'in', 'on', 'with', 'from', 'to', 'is', 'are'}
        overlap_content_words = overlap_words - stop_words
        next_content_words = next_words - stop_words
        
        if not overlap_content_words or not next_content_words:
            return False
        
        # Calculate semantic overlap
        common_words = overlap_content_words & next_content_words
        total_words = overlap_content_words | next_content_words
        
        if len(total_words) == 0:
            return False
        
        semantic_similarity = len(common_words) / len(total_words)
        
        return semantic_similarity >= self.config.semantic_overlap_threshold
    
    def _chunk_with_enhanced_semantic_overlap(
        self,
        content: str,
        target_size: int,
        content_type: ContentType
    ) -> List[Dict[str, Any]]:
        """
        RAG-optimierte Chunking mit verbessertem semantic overlap für bessere Kontextkontinuität
        """
        # Basis-Chunks erstellen
        base_chunks = self._chunk_with_semantic_boundaries(content, target_size, content_type)
        
        if len(base_chunks) <= 1:
            return [{'content': chunk[0], 'start': chunk[1], 'end': chunk[2], 'has_overlap': False} for chunk in base_chunks]
        
        enhanced_chunks = []
        
        for i, (chunk_content, start, end) in enumerate(base_chunks):
            chunk_data = {
                'content': chunk_content,
                'start': start,
                'end': end,
                'has_overlap': False,
                'overlap_type': 'none'
            }
            
            # Erweiterte Overlap-Strategien für RAG
            if i > 0:  # Nicht der erste Chunk
                prev_chunk = base_chunks[i-1][0]
                
                # Strategie 1: Sentence-aware overlap (30% des vorherigen Chunks)
                overlap_text = self._get_semantic_overlap(prev_chunk, chunk_content)
                
                if overlap_text:
                    chunk_data['content'] = f"{overlap_text} {chunk_content}".strip()
                    chunk_data['has_overlap'] = True
                    chunk_data['overlap_type'] = 'sentence_aware'
                    chunk_data['overlap_length'] = len(overlap_text)
            
            # Strategie 2: Context bridging für thematische Kontinuität
            if i > 0 and i < len(base_chunks) - 1:
                # Bridge zwischen vorherigem und nächstem Chunk
                next_chunk = base_chunks[i+1][0]
                if self._should_add_context_bridge(chunk_content, next_chunk):
                    bridge_text = self._extract_context_bridge(chunk_content, next_chunk)
                    if bridge_text:
                        chunk_data['content'] = f"{chunk_data['content']} {bridge_text}".strip()
                        chunk_data['overlap_type'] = 'context_bridge'
            
            enhanced_chunks.append(chunk_data)
        
        return enhanced_chunks
    
    def _get_semantic_overlap(self, prev_chunk: str, current_chunk: str) -> str:
        """Extrahiere semantisch sinnvollen Overlap zwischen Chunks"""
        if not prev_chunk or not current_chunk:
            return ""
        
        # Hol die letzten 2-3 Sätze vom vorherigen Chunk
        prev_sentences = self._get_sentences(prev_chunk)
        if len(prev_sentences) < 2:
            return ""
        
        # Nimm die letzten 2 Sätze als Overlap (max 30% des target size)
        overlap_sentences = prev_sentences[-2:]
        overlap_text = " ".join(overlap_sentences).strip()
        
        # Begrenze Overlap-Größe
        max_overlap_size = int(self.config.max_chunk_size * self.config.overlap_ratio)
        if len(overlap_text) > max_overlap_size:
            # Nimm nur den letzten Satz
            overlap_text = prev_sentences[-1].strip()
        
        return overlap_text
    
    def _should_add_context_bridge(self, current_chunk: str, next_chunk: str) -> bool:
        """Prüfe ob Context-Bridge zwischen Chunks sinnvoll ist"""
        # Einfache Heuristik: Wenn Chunks sehr kurz sind oder thematisch verwandt
        return (
            len(current_chunk) < self.config.target_word_count * 4 or  # Kurze Chunks
            self._chunks_are_thematically_related(current_chunk, next_chunk)
        )
    
    def _chunks_are_thematically_related(self, chunk1: str, chunk2: str) -> bool:
        """Einfache thematische Verwandtschaftsprüfung"""
        # Basis-Implementierung: Gemeinsame Keywords prüfen
        words1 = set(chunk1.lower().split())
        words2 = set(chunk2.lower().split())
        
        # Filtere Stoppwörter (vereinfacht)
        stopwords = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'mit', 'von', 'zu', 'ist', 'sind', 'ein', 'eine'}
        words1 = {w for w in words1 if len(w) > 3 and w not in stopwords}
        words2 = {w for w in words2 if len(w) > 3 and w not in stopwords}
        
        if not words1 or not words2:
            return False
        
        # Jaccard-Ähnlichkeit > 0.2
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return union > 0 and (intersection / union) > 0.2
    
    def _extract_context_bridge(self, current_chunk: str, next_chunk: str) -> str:
        """Extrahiere Context-Bridge Text zwischen verwandten Chunks"""
        # Nimm ersten Satz vom nächsten Chunk als Bridge
        next_sentences = self._get_sentences(next_chunk)
        if next_sentences:
            bridge = next_sentences[0].strip()
            # Begrenze Bridge-Länge
            if len(bridge) > 150:  # Max 150 Zeichen für Bridge
                bridge = bridge[:150] + "..."
            return bridge
        return ""