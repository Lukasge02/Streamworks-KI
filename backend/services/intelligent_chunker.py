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
    
    # Base settings - RAG-optimierte Größen für bessere Retrieval-Performance
    min_chunk_size: int = 200      # ~50 tokens minimum für meaningful content
    max_chunk_size: int = 1000     # ~250 tokens maximum (RAG sweet spot)
    target_chunk_size: int = 600   # ~150 tokens target (optimal für RAG)
    overlap_ratio: float = 0.15    # 15% overlap für bessere context continuity
    
    # Content-type specific - RAG-optimiert für bessere Retrieval-Performance
    pdf_chunk_size: int = 700      # RAG-optimal für PDF-Inhalte
    text_chunk_size: int = 600     # RAG-optimal für Text-Retrieval
    html_chunk_size: int = 650     # RAG-optimal für HTML-Inhalte
    code_chunk_size: int = 500     # Kompakter für bessere Code-Verständlichkeit
    markdown_chunk_size: int = 600 # RAG-optimal für Markdown
    
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
        # Early return nur für komplett leeren Content
        if not content or not content.strip():
            return []
        
        # Für sehr kurze Inhalte wird Single-Chunk Fallback später angewendet
        # Hier nicht mehr früh returnen!
        
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
        
        # Phase 3.5: Single-Chunk Fallback - JEDES Dokument bekommt mindestens 1 Chunk!
        if not quality_chunks and content.strip():
            logger.warning(f"No chunks passed quality gates - applying Single-Chunk Fallback for {len(content)} chars")
            fallback_chunk = self._create_single_chunk_fallback(content, metadata or {})
            quality_chunks = [fallback_chunk]
        
        # Phase 3.7: Mini-Document Enhancement für bessere RAG-Performance
        if len(content) < 200 and quality_chunks:
            quality_chunks = self._enhance_mini_documents(quality_chunks, content)
        
        # Phase 3.6: Ultra-Fallback für extrem kurze Texte - GARANTIE für jeden Text!
        if not quality_chunks and content.strip() and len(content.strip()) >= 5:
            logger.warning(f"Ultra-Fallback: Creating chunk for very short content ({len(content.strip())} chars)")
            ultra_fallback = self._create_ultra_fallback_chunk(content, metadata or {})
            quality_chunks = [ultra_fallback]
        
        # Phase 4: Overlap optimization
        final_chunks = self._optimize_overlap(quality_chunks, target_chunk_size)
        
        # Erweiterte Logging-Statistiken
        has_fallback = any(chunk.get('metadata', {}).get('chunk_type') == 'fallback' for chunk in final_chunks)
        relaxed_count = len([c for c in final_chunks if c.get('metadata', {}).get('quality_tier') == 'small_document_relaxed'])
        
        logger.info(f"📊 Chunking Results: {len(content)} chars → {len(chunks)} raw → {len(quality_chunks)} quality → {len(final_chunks)} final chunks")
        
        if final_chunks:
            avg_chunk_size = sum(len(c['content']) for c in final_chunks) / len(final_chunks)
            quality_scores = [c.get('quality_score', 0) for c in final_chunks]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            logger.info(f"📈 Quality Metrics: avg_chunk_size={int(avg_chunk_size)}, avg_quality={avg_quality:.2f}, fallback={has_fallback}, relaxed={relaxed_count}")
            
            # Detail-Log für problematische Fälle
            if has_fallback:
                logger.warning("⚠️ Single-Chunk Fallback was used - document may have had quality issues")
            if relaxed_count > 0:
                logger.info(f"ℹ️ Used relaxed quality gates for {relaxed_count} chunks (small document)")
        else:
            logger.error("❌ No chunks created! This should never happen with fallback enabled.")
        
        # Content-Type spezifisches Logging
        if content_type:
            logger.debug(f"📄 Content-Type: {content_type}, Target Size: {target_chunk_size}")
        
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
        """Split text by paragraphs and sections - RAG-optimized with table support"""
        # Check if content contains tables
        if self._contains_tables(content):
            return self._split_table_content(content)
        
        # For small documents (< 2 * target_size), don't split by paragraphs
        # This prevents over-fragmentation of small documents
        if len(content) < 2 * self.config.target_chunk_size:
            return [(content, {'section_type': 'full_document', 'section_index': 0})]
        
        sections = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', content)
        
        # Group small paragraphs together to avoid tiny sections
        current_section = []
        current_length = 0
        min_section_size = self.config.min_chunk_size  # Don't create sections smaller than min chunk
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                para_length = len(paragraph.strip())
                
                # If adding this paragraph would exceed target or we have enough content
                if (current_length + para_length > self.config.target_chunk_size and 
                    current_section and current_length >= min_section_size):
                    # Finalize current section
                    section_content = '\n\n'.join(current_section)
                    sections.append((
                        section_content,
                        {'section_type': 'paragraph_group', 'section_index': len(sections)}
                    ))
                    
                    # Start new section
                    current_section = [paragraph.strip()]
                    current_length = para_length
                else:
                    current_section.append(paragraph.strip())
                    current_length += para_length
        
        # Add final section
        if current_section:
            section_content = '\n\n'.join(current_section)
            sections.append((
                section_content,
                {'section_type': 'paragraph_group', 'section_index': len(sections)}
            ))
        
        # If no sections created, use full document
        if not sections:
            return [(content, {'section_type': 'full_document', 'section_index': 0})]
        
        return sections
    
    def _contains_tables(self, content: str) -> bool:
        """Detect if content contains table-like structures"""
        # Look for common table indicators
        table_indicators = [
            r'-{3,}',  # Horizontal lines (---)
            r'={3,}',  # Horizontal lines (===)
            r'\|.*\|', # Pipe-separated columns
            r'\s{3,}\w+\s{3,}\w+',  # Multiple columns with spacing
        ]
        
        for indicator in table_indicators:
            if re.search(indicator, content):
                return True
        
        # Check for tabular data patterns (numbers in columns)
        lines = content.split('\n')
        numeric_columns = 0
        for line in lines:
            # Count lines with multiple numbers separated by spaces
            numbers = re.findall(r'\b\d[\d.,]*\b', line)
            if len(numbers) >= 3:  # At least 3 numbers in a line suggests tabular data
                numeric_columns += 1
        
        return numeric_columns >= 3  # At least 3 lines with numeric columns
    
    def _split_table_content(self, content: str) -> List[Tuple[str, Dict]]:
        """Split table content into logical chunks while preserving table structure"""
        sections = []
        lines = content.split('\n')
        
        # If table document is small enough, keep as single chunk
        if len(content) <= self.config.max_chunk_size:
            return [(content, {'section_type': 'table_document', 'section_index': 0})]
        
        # Find table boundaries and headers
        current_section = []
        current_length = 0
        header_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_length = len(line) + 1  # +1 for newline
            
            # Detect table headers and separators
            is_separator = bool(re.match(r'^[-=]{3,}', line))
            is_header = (i < 5 and not is_separator and 
                        (any(keyword in line.lower() for keyword in ['region', 'produkt', 'monat', 'kategorie']) or
                         re.search(r'\b\w+\s{2,}\w+', line)))  # Multiple columns
            
            # If we hit a separator or this would make chunk too large
            # But ensure minimum viable chunk size for tables (300 chars minimum)
            if (is_separator and current_section and current_length >= 300) or \
               (current_length + line_length > self.config.target_chunk_size and current_section and current_length >= 300):
                
                # Include headers in new section
                section_content = '\n'.join(header_lines + current_section)
                if section_content.strip():
                    sections.append((
                        section_content.strip(),
                        {'section_type': 'table_section', 'section_index': len(sections)}
                    ))
                
                current_section = []
                current_length = sum(len(h) + 1 for h in header_lines)
            
            # Collect headers for reuse
            if is_header or is_separator:
                if is_header:
                    header_lines.append(line)
                elif is_separator and header_lines:
                    header_lines.append(line)
            
            current_section.append(line)
            current_length += line_length
            i += 1
        
        # Add final section
        if current_section:
            section_content = '\n'.join(header_lines + current_section)
            if section_content.strip():
                sections.append((
                    section_content.strip(),
                    {'section_type': 'table_section', 'section_index': len(sections)}
                ))
        
        # If no proper sections created, treat as single table
        if not sections:
            return [(content, {'section_type': 'table_document', 'section_index': 0})]
        
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
                # Only split if current chunk is above minimum size
                if current_length >= self.config.min_chunk_size:
                    # Finalize current chunk
                    chunk_content = ' '.join(current_chunk).strip()
                    if chunk_content:
                        chunks.append((chunk_content, start_pos, start_pos + current_length))
                    
                    # Start new chunk
                    current_chunk = [sentence]
                    current_length = sentence_length
                    start_pos = start_pos + current_length
                else:
                    # Current chunk too small, keep adding to reach min size
                    current_chunk.append(sentence)
                    current_length += sentence_length
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
        """Apply quality filters to chunks with flexible gates for small documents and tables"""
        quality_chunks = []
        
        # Detect document characteristics
        total_content_length = sum(len(chunk['content']) for chunk in chunks)
        is_small_document = total_content_length < 1000  # Less than 1KB of text
        is_mini_document = total_content_length < 200    # Less than 200 chars - ultra small
        is_table_content = any(chunk.get('metadata', {}).get('section_type', '').startswith('table') for chunk in chunks)
        
        for chunk in chunks:
            quality = self._assess_chunk_quality(chunk['content'])
            
            # Standard quality check
            passes_standard = quality.is_high_quality or quality.is_acceptable
            
            # Relaxed quality check for small documents
            passes_relaxed = False
            if is_small_document and not is_mini_document:
                passes_relaxed = self._is_acceptable_for_small_document(quality)
            
            # Ultra-relaxed quality check for mini documents
            passes_mini_check = False
            if is_mini_document:
                passes_mini_check = self._is_acceptable_for_mini_document(quality, chunk['content'])
            
            # Table-specific quality check
            passes_table_check = False
            if is_table_content or self._contains_tables(chunk['content']):
                passes_table_check = self._is_acceptable_for_table_content(quality, chunk['content'])
            
            if passes_standard or passes_relaxed or passes_mini_check or passes_table_check:
                chunk['quality_score'] = self._calculate_quality_score(quality)
                chunk['quality_metrics'] = quality
                
                if passes_table_check and not passes_standard:
                    chunk['metadata'] = {**chunk.get('metadata', {}), 'quality_tier': 'table_content'}
                    logger.debug(f"Accepted table chunk: {quality.word_count} words, {len(chunk['content'])} chars")
                elif passes_mini_check and not passes_standard:
                    chunk['metadata'] = {**chunk.get('metadata', {}), 'quality_tier': 'mini_document'}
                    logger.debug(f"Accepted mini document: {quality.word_count} words, {len(chunk['content'])} chars")
                elif passes_relaxed and not passes_standard:
                    chunk['metadata'] = {**chunk.get('metadata', {}), 'quality_tier': 'small_document_relaxed'}
                    logger.debug(f"Accepted chunk with relaxed gates (small doc): {quality.word_count} words, {len(chunk['content'])} chars")
                    
                quality_chunks.append(chunk)
            else:
                logger.debug(f"Filtered low-quality chunk: {len(chunk['content'])} chars, {quality.word_count} words, tier: {quality.quality_tier}")
        
        return quality_chunks
    
    def _is_acceptable_for_small_document(self, quality: ChunkQuality) -> bool:
        """
        Relaxed quality criteria for small documents
        Ensures small docs like Kuendigung-Mietvertrag.pdf get chunked
        """
        return (
            quality.word_count >= 5 and           # Sehr niedrige Mindestanforderung (statt 25)
            quality.sentence_count >= 0 and       # Auch Fragmente erlaubt (statt 1)
            quality.alpha_ratio >= 0.2 and        # Niedrigere Textqualität OK (statt 0.5)
            quality.repetition_ratio <= 0.9       # Mehr Wiederholung erlaubt (statt 0.5)
        )
    
    def _is_acceptable_for_mini_document(self, quality: ChunkQuality, content: str) -> bool:
        """
        Ultra-relaxed criteria for very small documents (<200 chars)
        Ensures even tiny documents get processed for RAG
        """
        return (
            len(content.strip()) >= 20 and        # Mindestens 20 Zeichen
            quality.word_count >= 3 and           # Mindestens 3 Wörter
            quality.alpha_ratio >= 0.1            # Irgendwelcher Text-Content
        )
    
    def _enhance_mini_documents(self, chunks: List[Dict[str, Any]], original_content: str) -> List[Dict[str, Any]]:
        """Enhance mini documents for better RAG performance"""
        enhanced_chunks = []
        
        for chunk in chunks:
            if len(chunk['content']) < 200:
                # Add document type hints to improve RAG context
                content = chunk['content']
                enhanced_metadata = {**chunk.get('metadata', {})}
                
                # Detect document type for better RAG context
                doc_type = 'snippet'
                if any(word in content.lower() for word in ['meeting', 'termin', 'agenda']):
                    doc_type = 'meeting_note'
                elif any(word in content.lower() for word in ['kündigung', 'vertrag', 'frist']):
                    doc_type = 'contract_notice'
                elif any(word in content.lower() for word in ['betreff', 'sehr geehrte']):
                    doc_type = 'formal_letter'
                
                enhanced_metadata.update({
                    'document_type': doc_type,
                    'content_length': len(content),
                    'rag_hint': f'This is a {doc_type} with {len(content.split())} words'
                })
                
                enhanced_chunk = {**chunk, 'metadata': enhanced_metadata}
                enhanced_chunks.append(enhanced_chunk)
            else:
                enhanced_chunks.append(chunk)
        
        return enhanced_chunks
    
    def _is_acceptable_for_table_content(self, quality: ChunkQuality, content: str) -> bool:
        """Special quality criteria for table content"""
        # Tables often have different quality characteristics
        has_numbers = len(re.findall(r'\b\d[\d.,]*\b', content)) >= 5  # At least 5 numbers
        has_table_structure = bool(re.search(r'-{3,}|={3,}|\|.*\|', content))  # Table separators
        has_headers = any(keyword in content.lower() for keyword in 
                         ['region', 'produkt', 'monat', 'kategorie', 'quartal', 'umsatz', 'verkauf'])
        
        return (
            quality.word_count >= 10 and          # Mindestens 10 Wörter für Tabellen
            (has_numbers or has_table_structure or has_headers) and  # Muss tabellen-ähnlich sein
            quality.alpha_ratio >= 0.3 and        # Etwas Text erforderlich
            len(content) >= 100                    # Mindestgröße für sinnvolle Tabellen
        )
    
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
    
    def _create_single_chunk_fallback(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstelle Single-Chunk Fallback für Dokumente ohne normale Chunks
        GARANTIERT: Jedes Dokument mit Text bekommt mindestens 1 Chunk!
        """
        # Bereinige Content
        cleaned_content = content.strip()
        
        # Begrenze sehr lange Inhalte auf max_chunk_size
        if len(cleaned_content) > self.config.max_chunk_size:
            # Schneide am letzten Satz ab, wenn möglich
            truncated = cleaned_content[:self.config.max_chunk_size]
            last_sentence_end = max(
                truncated.rfind('.'),
                truncated.rfind('!'),
                truncated.rfind('?')
            )
            
            if last_sentence_end > len(truncated) * 0.7:  # Mindestens 70% des Texts behalten
                cleaned_content = truncated[:last_sentence_end + 1]
            else:
                # Fallback: Am letzten Leerzeichen abschneiden
                last_space = truncated.rfind(' ')
                if last_space > 0:
                    cleaned_content = truncated[:last_space]
                else:
                    cleaned_content = truncated
        
        # Erweiterte Metadaten für Fallback-Chunk
        fallback_metadata = {
            **metadata,
            'chunk_type': 'fallback',
            'fallback_reason': 'quality_gates_failed',
            'original_content_length': len(content),
            'truncated': len(cleaned_content) < len(content.strip()),
            'processing_timestamp': self._get_timestamp()
        }
        
        # Basis-Qualitäts-Assessment für Logging
        words = cleaned_content.split()
        sentences = self._get_sentences(cleaned_content)
        
        # Erstelle Chunk
        fallback_chunk = {
            'content': cleaned_content,
            'start_char': 0,
            'end_char': len(cleaned_content),
            'metadata': fallback_metadata,
            'quality_score': 0.3,  # Niedrigere Score für Fallback
            'quality_metrics': ChunkQuality(
                word_count=len(words),
                sentence_count=len(sentences),
                alpha_ratio=sum(1 for c in cleaned_content if c.isalpha()) / len(cleaned_content) if cleaned_content else 0,
                repetition_ratio=0.0,  # Nicht berechnet für Fallback
                semantic_completeness=0.5,  # Standard-Wert für Fallback
                content_density=1.0,  # Fallback ist immer "dicht"
                semantic_coherence=0.3,  # Niedriger für ungeprüfte Inhalte
                contextual_completeness=0.4  # Moderate Vollständigkeit
            )
        }
        
        logger.info(f"✅ Single-Chunk Fallback created: {len(words)} words, {len(sentences)} sentences, {len(cleaned_content)} chars")
        
        return fallback_chunk
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _create_ultra_fallback_chunk(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ultra-Fallback für extrem kurze Texte - ABSOLUTE GARANTIE!
        Selbst für minimale Inhalte wird ein Chunk erstellt
        """
        cleaned_content = content.strip()
        words = cleaned_content.split()
        
        # Ultra-minimale Metadaten
        ultra_metadata = {
            **metadata,
            'chunk_type': 'ultra_fallback',
            'fallback_reason': 'extremely_short_content',
            'word_count': len(words),
            'char_count': len(cleaned_content),
            'processing_timestamp': self._get_timestamp()
        }
        
        # Ultra-minimale Quality Metrics (nur für Konsistenz)
        ultra_quality = ChunkQuality(
            word_count=len(words),
            sentence_count=max(1, len(self._get_sentences(cleaned_content))),
            alpha_ratio=sum(1 for c in cleaned_content if c.isalpha()) / len(cleaned_content) if cleaned_content else 0,
            repetition_ratio=0.0,
            semantic_completeness=0.3,  # Niedrig aber akzeptabel
            content_density=1.0,
            semantic_coherence=0.2,
            contextual_completeness=0.2
        )
        
        ultra_chunk = {
            'content': cleaned_content,
            'start_char': 0,
            'end_char': len(cleaned_content),
            'metadata': ultra_metadata,
            'quality_score': 0.2,  # Niedrigste Score aber immer noch gültig
            'quality_metrics': ultra_quality
        }
        
        logger.info(f"🆘 Ultra-Fallback chunk created: '{cleaned_content[:50]}...', {len(words)} words")
        
        return ultra_chunk