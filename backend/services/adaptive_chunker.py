"""
Adaptive Chunker - Structure-Aware Document Segmentation
Intelligently segments documents based on semantic boundaries and structure
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import math

from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain.text_splitter import MarkdownTextSplitter

from config import settings

logger = logging.getLogger(__name__)

class ChunkingStrategy(Enum):
    """Different chunking strategies"""
    FIXED_SIZE = "fixed_size"              # Traditional fixed-size chunks
    SEMANTIC_BOUNDARY = "semantic_boundary" # Respect paragraph/section breaks
    HIERARCHICAL = "hierarchical"          # Multi-level nested chunks
    SLIDING_WINDOW = "sliding_window"      # Overlapping windows with smart overlap
    ADAPTIVE_SIZE = "adaptive_size"        # Variable size based on content density

@dataclass
class DocumentStructure:
    """Represents detected document structure"""
    title: Optional[str] = None
    sections: List[Dict[str, Any]] = None
    paragraphs: List[Dict[str, Any]] = None
    lists: List[Dict[str, Any]] = None
    tables: List[Dict[str, Any]] = None
    headers: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = []
        if self.paragraphs is None:
            self.paragraphs = []
        if self.lists is None:
            self.lists = []
        if self.tables is None:
            self.tables = []
        if self.headers is None:
            self.headers = []

@dataclass
class AdaptiveChunk:
    """Enhanced chunk with structural metadata"""
    content: str
    chunk_id: str
    doc_id: str
    
    # Position and structure
    start_position: int
    end_position: int
    chunk_index: int
    
    # Structural information
    structural_type: str  # paragraph, section, list_item, table_row, etc.
    heading: Optional[str] = None
    section_path: Optional[List[str]] = None  # ["Chapter 1", "Section 1.1", "Subsection 1.1.1"]
    hierarchy_level: int = 0
    
    # Content characteristics
    word_count: int = 0
    char_count: int = 0
    sentence_count: int = 0
    complexity_score: float = 0.0
    
    # Chunking metadata
    chunking_strategy: str = "adaptive"
    boundary_quality: float = 0.0  # How clean are the boundaries?
    context_preservation: float = 0.0  # How well is context preserved?
    
    # Additional metadata
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Calculate basic metrics
        if not self.word_count:
            self.word_count = len(self.content.split())
        if not self.char_count:
            self.char_count = len(self.content)
        if not self.sentence_count:
            self.sentence_count = len(re.findall(r'[.!?]+', self.content))

class AdaptiveChunker:
    """
    Advanced Structure-Aware Document Chunker
    
    Features:
    - Multi-strategy chunking based on document type and structure
    - Semantic boundary detection using linguistic patterns
    - Hierarchical chunking with context preservation  
    - Adaptive sizing based on content complexity
    - Table and list aware segmentation
    - Optimized overlap for sliding window approach
    """
    
    def __init__(self,
                 base_chunk_size: int = 1500,
                 max_chunk_size: int = 3000,
                 min_chunk_size: int = 200,
                 overlap_ratio: float = 0.15):
        """
        Initialize Adaptive Chunker
        
        Args:
            base_chunk_size: Target chunk size for most content
            max_chunk_size: Maximum allowed chunk size
            min_chunk_size: Minimum allowed chunk size
            overlap_ratio: Overlap ratio for sliding window
        """
        self.base_chunk_size = base_chunk_size
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_ratio = overlap_ratio
        
        # Structure detection patterns
        self.structure_patterns = self._compile_structure_patterns()
        
        # Initialize various text splitters
        self.splitters = self._initialize_splitters()
        
        # Performance tracking
        self.chunking_stats = {
            'documents_processed': 0,
            'total_chunks_created': 0,
            'avg_chunk_size': 0.0,
            'boundary_quality_avg': 0.0
        }
        
        logger.info(f"🧩 AdaptiveChunker initialized - base: {base_chunk_size}, max: {max_chunk_size}")
    
    def _compile_structure_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for structure detection"""
        patterns = {
            # Headers (Markdown-style and numbered)
            'header_md': re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE),
            'header_numbered': re.compile(r'^\d+(?:\.\d+)*\.?\s+(.+)$', re.MULTILINE),
            'header_caps': re.compile(r'^[A-ZÄÖÜ][A-ZÄÖÜ\s]{3,}$', re.MULTILINE),
            
            # Paragraphs and sections
            'paragraph_break': re.compile(r'\n\s*\n'),
            'section_break': re.compile(r'\n\s*\n\s*(?=[A-ZÄÖÜ]|\d+\.|#{1,6})'),
            
            # Lists
            'bullet_list': re.compile(r'^\s*[-*•]\s+(.+)$', re.MULTILINE),
            'numbered_list': re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE),
            'letter_list': re.compile(r'^\s*[a-zA-Z]\.\s+(.+)$', re.MULTILINE),
            
            # Tables (simple detection)
            'table_row': re.compile(r'^\s*\|(.+\|)+\s*$', re.MULTILINE),
            'table_separator': re.compile(r'^\s*\|?\s*:?-+:?\s*\|.*$', re.MULTILINE),
            
            # Code blocks
            'code_block': re.compile(r'```[\s\S]*?```'),
            'inline_code': re.compile(r'`[^`]+`'),
            
            # Quotes
            'blockquote': re.compile(r'^\s*>\s+(.+)$', re.MULTILINE),
            
            # Special markers
            'page_break': re.compile(r'\f|\n\s*---+\s*\n'),
            'horizontal_rule': re.compile(r'^\s*[-=*]{3,}\s*$', re.MULTILINE)
        }
        
        return patterns
    
    def _initialize_splitters(self) -> Dict[str, TextSplitter]:
        """Initialize various text splitters for different strategies"""
        splitters = {
            'recursive': RecursiveCharacterTextSplitter(
                chunk_size=self.base_chunk_size,
                chunk_overlap=int(self.base_chunk_size * self.overlap_ratio),
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
            ),
            'markdown': MarkdownTextSplitter(
                chunk_size=self.base_chunk_size,
                chunk_overlap=int(self.base_chunk_size * self.overlap_ratio)
            ),
            'sentence': RecursiveCharacterTextSplitter(
                chunk_size=self.base_chunk_size,
                chunk_overlap=int(self.base_chunk_size * 0.05),  # Minimal overlap for sentences
                length_function=len,
                separators=[".", "!", "?", "\n\n", "\n", " "]
            )
        }
        
        return splitters
    
    async def chunk_document(
        self,
        content: str,
        doc_id: str,
        strategy: ChunkingStrategy = ChunkingStrategy.ADAPTIVE_SIZE,
        document_type: Optional[str] = None,
        preserve_structure: bool = True
    ) -> List[AdaptiveChunk]:
        """
        Chunk document using adaptive strategy
        
        Args:
            content: Document content to chunk
            doc_id: Document identifier
            strategy: Chunking strategy to use
            document_type: Type hint for document (pdf, markdown, etc.)
            preserve_structure: Whether to preserve document structure
            
        Returns:
            List of AdaptiveChunk objects
        """
        try:
            if not content or not content.strip():
                return []
            
            # Detect document structure
            structure = await self._detect_document_structure(content, document_type)
            
            # Choose optimal chunking strategy
            if strategy == ChunkingStrategy.ADAPTIVE_SIZE:
                strategy = self._choose_optimal_strategy(content, structure, document_type)
            
            logger.info(f"Chunking {doc_id} using {strategy.value} strategy")
            
            # Apply chosen strategy
            if strategy == ChunkingStrategy.SEMANTIC_BOUNDARY:
                chunks = await self._semantic_boundary_chunking(content, doc_id, structure)
            elif strategy == ChunkingStrategy.HIERARCHICAL:
                chunks = await self._hierarchical_chunking(content, doc_id, structure)
            elif strategy == ChunkingStrategy.SLIDING_WINDOW:
                chunks = await self._sliding_window_chunking(content, doc_id, structure)
            else:  # FIXED_SIZE or fallback
                chunks = await self._fixed_size_chunking(content, doc_id, structure)
            
            # Post-process chunks
            chunks = self._post_process_chunks(chunks, preserve_structure)
            
            # Update statistics
            self._update_chunking_stats(chunks)
            
            logger.info(f"Created {len(chunks)} chunks for {doc_id} (avg size: {sum(c.char_count for c in chunks) / len(chunks):.0f} chars)")
            return chunks
            
        except Exception as e:
            logger.error(f"Document chunking failed for {doc_id}: {str(e)}")
            # Fallback to simple chunking
            return await self._fallback_chunking(content, doc_id)
    
    async def _detect_document_structure(self, content: str, doc_type: Optional[str]) -> DocumentStructure:
        """
        Detect document structure using pattern matching
        """
        structure = DocumentStructure()
        
        try:
            # Detect title (first significant header or capitalized line)
            title_match = self.structure_patterns['header_md'].search(content)
            if not title_match:
                title_match = self.structure_patterns['header_caps'].search(content)
            if title_match:
                structure.title = title_match.group(1).strip()
            
            # Detect headers and build section hierarchy
            headers = []
            for match in self.structure_patterns['header_md'].finditer(content):
                level = len(match.group().split()[0])  # Count # symbols
                headers.append({
                    'text': match.group(1).strip(),
                    'level': level,
                    'start': match.start(),
                    'end': match.end()
                })
            
            # Add numbered headers
            for match in self.structure_patterns['header_numbered'].finditer(content):
                level = len(match.group().split('.')[0].split('.'))
                headers.append({
                    'text': match.group(1).strip(),
                    'level': level,
                    'start': match.start(),
                    'end': match.end()
                })
            
            structure.headers = sorted(headers, key=lambda x: x['start'])
            
            # Build section structure from headers
            current_section = None
            for i, header in enumerate(structure.headers):
                section_end = structure.headers[i + 1]['start'] if i + 1 < len(structure.headers) else len(content)
                section_content = content[header['end']:section_end].strip()
                
                section = {
                    'title': header['text'],
                    'level': header['level'],
                    'content': section_content,
                    'start': header['start'],
                    'end': section_end,
                    'word_count': len(section_content.split())
                }
                structure.sections.append(section)
            
            # Detect paragraphs
            paragraph_breaks = list(self.structure_patterns['paragraph_break'].finditer(content))
            if paragraph_breaks:
                start = 0
                for match in paragraph_breaks:
                    if start < match.start():
                        para_content = content[start:match.start()].strip()
                        if para_content and len(para_content.split()) > 3:
                            structure.paragraphs.append({
                                'content': para_content,
                                'start': start,
                                'end': match.start(),
                                'word_count': len(para_content.split())
                            })
                    start = match.end()
                
                # Last paragraph
                if start < len(content):
                    para_content = content[start:].strip()
                    if para_content and len(para_content.split()) > 3:
                        structure.paragraphs.append({
                            'content': para_content,
                            'start': start,
                            'end': len(content),
                            'word_count': len(para_content.split())
                        })
            
            # Detect lists
            for list_type, pattern in [('bullet', 'bullet_list'), ('numbered', 'numbered_list')]:
                for match in self.structure_patterns[pattern].finditer(content):
                    structure.lists.append({
                        'type': list_type,
                        'content': match.group(1).strip(),
                        'start': match.start(),
                        'end': match.end()
                    })
            
            # Detect tables
            table_rows = list(self.structure_patterns['table_row'].finditer(content))
            if table_rows:
                current_table = []
                for match in table_rows:
                    current_table.append({
                        'content': match.group().strip(),
                        'start': match.start(),
                        'end': match.end()
                    })
                
                if current_table:
                    structure.tables.append({
                        'rows': current_table,
                        'start': current_table[0]['start'],
                        'end': current_table[-1]['end']
                    })
            
            logger.debug(f"Detected structure: {len(structure.sections)} sections, {len(structure.paragraphs)} paragraphs, {len(structure.headers)} headers")
            
        except Exception as e:
            logger.warning(f"Structure detection partially failed: {str(e)}")
        
        return structure
    
    def _choose_optimal_strategy(
        self,
        content: str,
        structure: DocumentStructure,
        doc_type: Optional[str]
    ) -> ChunkingStrategy:
        """
        Choose optimal chunking strategy based on content analysis
        """
        content_length = len(content)
        word_count = len(content.split())
        
        # Document type hints
        if doc_type == 'markdown' or '# ' in content or '## ' in content:
            return ChunkingStrategy.HIERARCHICAL
        
        # Structure-based decisions
        if len(structure.headers) > 3 and len(structure.sections) > 2:
            return ChunkingStrategy.HIERARCHICAL
        
        if len(structure.paragraphs) > 5:
            return ChunkingStrategy.SEMANTIC_BOUNDARY
        
        # Content length based decisions
        if word_count < 500:
            return ChunkingStrategy.FIXED_SIZE
        elif word_count > 5000:
            return ChunkingStrategy.SLIDING_WINDOW
        else:
            return ChunkingStrategy.SEMANTIC_BOUNDARY
    
    async def _semantic_boundary_chunking(
        self,
        content: str,
        doc_id: str,
        structure: DocumentStructure
    ) -> List[AdaptiveChunk]:
        """
        Chunk respecting semantic boundaries (paragraphs, sections)
        """
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        # Use paragraphs as primary boundaries
        boundaries = structure.paragraphs if structure.paragraphs else [{'content': content, 'start': 0, 'end': len(content)}]
        
        for para in boundaries:
            para_content = para['content']
            potential_chunk = current_chunk + ("\n\n" if current_chunk else "") + para_content
            
            # Check if adding this paragraph exceeds max size
            if len(potential_chunk) > self.max_chunk_size and current_chunk:
                # Create chunk with current content
                if current_chunk.strip():
                    chunk = self._create_adaptive_chunk(
                        content=current_chunk.strip(),
                        chunk_id=f"{doc_id}_chunk_{chunk_index}",
                        doc_id=doc_id,
                        start_position=current_start,
                        end_position=current_start + len(current_chunk),
                        chunk_index=chunk_index,
                        structural_type="paragraph_group",
                        chunking_strategy="semantic_boundary"
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk with current paragraph
                current_chunk = para_content
                current_start = para['start']
            else:
                # Add paragraph to current chunk
                if not current_chunk:
                    current_start = para['start']
                current_chunk = potential_chunk
            
            # Handle oversized single paragraphs
            if len(current_chunk) > self.max_chunk_size:
                # Split the oversized paragraph
                para_chunks = await self._split_oversized_content(current_chunk, doc_id, chunk_index)
                chunks.extend(para_chunks)
                chunk_index += len(para_chunks)
                current_chunk = ""
        
        # Add remaining content
        if current_chunk.strip():
            chunk = self._create_adaptive_chunk(
                content=current_chunk.strip(),
                chunk_id=f"{doc_id}_chunk_{chunk_index}",
                doc_id=doc_id,
                start_position=current_start,
                end_position=current_start + len(current_chunk),
                chunk_index=chunk_index,
                structural_type="paragraph_group",
                chunking_strategy="semantic_boundary"
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _hierarchical_chunking(
        self,
        content: str,
        doc_id: str,
        structure: DocumentStructure
    ) -> List[AdaptiveChunk]:
        """
        Create hierarchical chunks preserving document structure
        """
        chunks = []
        chunk_index = 0
        
        if not structure.sections:
            # Fallback to semantic boundary chunking
            return await self._semantic_boundary_chunking(content, doc_id, structure)
        
        # Build section hierarchy path
        section_stack = []
        
        for section in structure.sections:
            # Update section stack based on hierarchy level
            while section_stack and section_stack[-1]['level'] >= section['level']:
                section_stack.pop()
            
            section_stack.append(section)
            section_path = [s['title'] for s in section_stack]
            
            # Determine if section needs to be split
            section_content = section['content']
            if len(section_content) <= self.max_chunk_size:
                # Create single chunk for section
                chunk = self._create_adaptive_chunk(
                    content=section_content,
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    doc_id=doc_id,
                    start_position=section['start'],
                    end_position=section['end'],
                    chunk_index=chunk_index,
                    structural_type="section",
                    heading=section['title'],
                    section_path=section_path,
                    hierarchy_level=section['level'],
                    chunking_strategy="hierarchical"
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Split section into multiple chunks
                section_chunks = await self._split_section_content(
                    section_content, doc_id, chunk_index, section['title'], section_path, section['level']
                )
                chunks.extend(section_chunks)
                chunk_index += len(section_chunks)
        
        return chunks
    
    async def _sliding_window_chunking(
        self,
        content: str,
        doc_id: str,
        structure: DocumentStructure
    ) -> List[AdaptiveChunk]:
        """
        Create overlapping chunks with intelligent overlap optimization
        """
        chunks = []
        chunk_index = 0
        
        # Calculate adaptive overlap based on content structure
        base_overlap = int(self.base_chunk_size * self.overlap_ratio)
        
        # Use sentence boundaries for smarter overlap
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        current_chunk = ""
        start_pos = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            potential_chunk = current_chunk + (" " if current_chunk else "") + sentence
            
            if len(potential_chunk) >= self.base_chunk_size or i == len(sentences) - 1:
                # Create chunk
                if current_chunk:
                    chunk = self._create_adaptive_chunk(
                        content=current_chunk.strip(),
                        chunk_id=f"{doc_id}_chunk_{chunk_index}",
                        doc_id=doc_id,
                        start_position=start_pos,
                        end_position=start_pos + len(current_chunk),
                        chunk_index=chunk_index,
                        structural_type="sliding_window",
                        chunking_strategy="sliding_window"
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Calculate smart overlap for next chunk
                if i < len(sentences) - 1:
                    # Find good overlap point (sentence boundary within overlap region)
                    overlap_chars = 0
                    overlap_sentences = []
                    
                    # Work backwards from current position
                    j = i
                    while j >= 0 and overlap_chars < base_overlap:
                        overlap_chars += len(sentences[j]) + 1
                        overlap_sentences.insert(0, sentences[j])
                        j -= 1
                    
                    # Start next chunk with overlap
                    current_chunk = " ".join(overlap_sentences)
                    if potential_chunk.strip():
                        current_chunk += " " + sentence
                    
                    # Adjust start position
                    start_pos = start_pos + len(chunks[-1].content) - len(current_chunk) if chunks else 0
                else:
                    current_chunk = sentence
            else:
                current_chunk = potential_chunk
            
            i += 1
        
        return chunks
    
    async def _fixed_size_chunking(
        self,
        content: str,
        doc_id: str,
        structure: DocumentStructure
    ) -> List[AdaptiveChunk]:
        """
        Traditional fixed-size chunking with improved boundary detection
        """
        # Use the recursive character splitter with custom separators
        text_chunks = self.splitters['recursive'].split_text(content)
        
        chunks = []
        position = 0
        
        for i, chunk_text in enumerate(text_chunks):
            # Find actual position in original content
            chunk_start = content.find(chunk_text, position)
            if chunk_start == -1:
                chunk_start = position
            
            chunk = self._create_adaptive_chunk(
                content=chunk_text,
                chunk_id=f"{doc_id}_chunk_{i}",
                doc_id=doc_id,
                start_position=chunk_start,
                end_position=chunk_start + len(chunk_text),
                chunk_index=i,
                structural_type="fixed_size",
                chunking_strategy="fixed_size"
            )
            chunks.append(chunk)
            position = chunk_start + len(chunk_text)
        
        return chunks
    
    async def _split_oversized_content(
        self,
        content: str,
        doc_id: str,
        start_chunk_index: int
    ) -> List[AdaptiveChunk]:
        """
        Split oversized content into manageable chunks
        """
        # Use sentence-based splitter for better boundaries
        text_chunks = self.splitters['sentence'].split_text(content)
        
        chunks = []
        position = 0
        
        for i, chunk_text in enumerate(text_chunks):
            chunk = self._create_adaptive_chunk(
                content=chunk_text,
                chunk_id=f"{doc_id}_chunk_{start_chunk_index + i}",
                doc_id=doc_id,
                start_position=position,
                end_position=position + len(chunk_text),
                chunk_index=start_chunk_index + i,
                structural_type="split_oversized",
                chunking_strategy="oversized_split"
            )
            chunks.append(chunk)
            position += len(chunk_text)
        
        return chunks
    
    async def _split_section_content(
        self,
        content: str,
        doc_id: str,
        start_chunk_index: int,
        section_title: str,
        section_path: List[str],
        hierarchy_level: int
    ) -> List[AdaptiveChunk]:
        """
        Split section content while preserving hierarchy information
        """
        text_chunks = self.splitters['recursive'].split_text(content)
        
        chunks = []
        position = 0
        
        for i, chunk_text in enumerate(text_chunks):
            chunk = self._create_adaptive_chunk(
                content=chunk_text,
                chunk_id=f"{doc_id}_chunk_{start_chunk_index + i}",
                doc_id=doc_id,
                start_position=position,
                end_position=position + len(chunk_text),
                chunk_index=start_chunk_index + i,
                structural_type="section_split",
                heading=section_title,
                section_path=section_path,
                hierarchy_level=hierarchy_level,
                chunking_strategy="hierarchical_split"
            )
            chunks.append(chunk)
            position += len(chunk_text)
        
        return chunks
    
    def _create_adaptive_chunk(
        self,
        content: str,
        chunk_id: str,
        doc_id: str,
        start_position: int,
        end_position: int,
        chunk_index: int,
        structural_type: str,
        chunking_strategy: str,
        heading: Optional[str] = None,
        section_path: Optional[List[str]] = None,
        hierarchy_level: int = 0
    ) -> AdaptiveChunk:
        """
        Create an AdaptiveChunk with computed metrics
        """
        # Calculate content complexity
        complexity_score = self._calculate_complexity_score(content)
        
        # Calculate boundary quality
        boundary_quality = self._calculate_boundary_quality(content, structural_type)
        
        # Calculate context preservation score
        context_preservation = self._calculate_context_preservation(content, section_path)
        
        chunk = AdaptiveChunk(
            content=content,
            chunk_id=chunk_id,
            doc_id=doc_id,
            start_position=start_position,
            end_position=end_position,
            chunk_index=chunk_index,
            structural_type=structural_type,
            heading=heading,
            section_path=section_path,
            hierarchy_level=hierarchy_level,
            complexity_score=complexity_score,
            chunking_strategy=chunking_strategy,
            boundary_quality=boundary_quality,
            context_preservation=context_preservation,
            metadata={
                'created_by': 'adaptive_chunker',
                'chunking_strategy': chunking_strategy,
                'structural_type': structural_type
            }
        )
        
        return chunk
    
    def _calculate_complexity_score(self, content: str) -> float:
        """
        Calculate content complexity score (0.0 - 1.0)
        
        Factors:
        - Vocabulary diversity
        - Sentence length variation
        - Technical term density
        - Punctuation complexity
        """
        try:
            words = content.split()
            if len(words) < 5:
                return 0.3
            
            # Vocabulary diversity (unique words / total words)
            unique_words = len(set(word.lower() for word in words))
            vocab_diversity = unique_words / len(words)
            
            # Sentence length variation
            sentences = re.split(r'[.!?]+', content)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                avg_length = sum(sentence_lengths) / len(sentence_lengths)
                length_variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
                length_complexity = min(length_variance / 100, 1.0)
            else:
                length_complexity = 0.5
            
            # Technical term density
            technical_patterns = [r'\b[A-Z]{2,}\b', r'\b\w*[0-9]+\w*\b', r'\b\w+_\w+\b']
            technical_matches = sum(len(re.findall(pattern, content)) for pattern in technical_patterns)
            technical_density = min(technical_matches / len(words), 1.0)
            
            # Combine factors
            complexity = (
                vocab_diversity * 0.4 +
                length_complexity * 0.3 +
                technical_density * 0.3
            )
            
            return min(max(complexity, 0.0), 1.0)
            
        except:
            return 0.5  # Default complexity
    
    def _calculate_boundary_quality(self, content: str, structural_type: str) -> float:
        """
        Calculate how clean the chunk boundaries are (0.0 - 1.0)
        """
        # Base quality by structural type
        quality_by_type = {
            'section': 1.0,
            'paragraph_group': 0.9,
            'paragraph': 0.8,
            'sentence_group': 0.7,
            'sliding_window': 0.6,
            'fixed_size': 0.5,
            'split_oversized': 0.4
        }
        
        base_quality = quality_by_type.get(structural_type, 0.5)
        
        # Adjust based on content characteristics
        content_stripped = content.strip()
        
        # Penalty for mid-sentence cuts
        if content_stripped and not content_stripped[-1] in '.!?':
            base_quality *= 0.8
        
        # Bonus for complete sentences
        if content_stripped.endswith('.') or content_stripped.endswith('!') or content_stripped.endswith('?'):
            base_quality = min(base_quality * 1.1, 1.0)
        
        return base_quality
    
    def _calculate_context_preservation(self, content: str, section_path: Optional[List[str]]) -> float:
        """
        Calculate how well the chunk preserves context (0.0 - 1.0)
        """
        base_score = 0.5
        
        # Bonus for hierarchical context
        if section_path:
            base_score += 0.3
        
        # Bonus for self-contained content
        content_lower = content.lower()
        if any(word in content_lower for word in ['however', 'therefore', 'furthermore', 'in conclusion']):
            base_score += 0.1
        
        # Penalty for obvious continuation text
        if content.strip().startswith(('and', 'but', 'however', 'also')):
            base_score -= 0.2
        
        return min(max(base_score, 0.0), 1.0)
    
    def _post_process_chunks(self, chunks: List[AdaptiveChunk], preserve_structure: bool) -> List[AdaptiveChunk]:
        """
        Post-process chunks for quality improvements
        """
        if not chunks:
            return chunks
        
        processed_chunks = []
        
        for chunk in chunks:
            # Skip very small chunks (merge with adjacent if possible)
            if chunk.char_count < self.min_chunk_size and len(chunks) > 1:
                # Try to merge with next chunk
                if processed_chunks:
                    last_chunk = processed_chunks[-1]
                    if last_chunk.char_count + chunk.char_count < self.max_chunk_size:
                        # Merge with previous chunk
                        merged_content = last_chunk.content + "\n\n" + chunk.content
                        last_chunk.content = merged_content
                        last_chunk.end_position = chunk.end_position
                        last_chunk.char_count = len(merged_content)
                        last_chunk.word_count = len(merged_content.split())
                        last_chunk.sentence_count = len(re.findall(r'[.!?]+', merged_content))
                        continue
            
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    async def _fallback_chunking(self, content: str, doc_id: str) -> List[AdaptiveChunk]:
        """
        Fallback to simple chunking when advanced methods fail
        """
        try:
            text_chunks = self.splitters['recursive'].split_text(content)
            
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk = AdaptiveChunk(
                    content=chunk_text,
                    chunk_id=f"{doc_id}_fallback_{i}",
                    doc_id=doc_id,
                    start_position=i * self.base_chunk_size,
                    end_position=(i + 1) * self.base_chunk_size,
                    chunk_index=i,
                    structural_type="fallback",
                    chunking_strategy="fallback",
                    word_count=len(chunk_text.split()),
                    char_count=len(chunk_text)
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Fallback chunking also failed: {str(e)}")
            return []
    
    def _update_chunking_stats(self, chunks: List[AdaptiveChunk]):
        """
        Update performance statistics
        """
        if not chunks:
            return
        
        self.chunking_stats['documents_processed'] += 1
        self.chunking_stats['total_chunks_created'] += len(chunks)
        
        # Update average chunk size
        total_chars = sum(c.char_count for c in chunks)
        old_avg = self.chunking_stats['avg_chunk_size']
        total_chunks = self.chunking_stats['total_chunks_created']
        
        self.chunking_stats['avg_chunk_size'] = (
            (old_avg * (total_chunks - len(chunks)) + total_chars) / total_chunks
        )
        
        # Update average boundary quality
        avg_quality = sum(c.boundary_quality for c in chunks) / len(chunks)
        old_boundary_avg = self.chunking_stats['boundary_quality_avg']
        
        self.chunking_stats['boundary_quality_avg'] = (
            (old_boundary_avg * (total_chunks - len(chunks)) + avg_quality * len(chunks)) / total_chunks
        )
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking performance statistics"""
        return {
            **self.chunking_stats,
            'parameters': {
                'base_chunk_size': self.base_chunk_size,
                'max_chunk_size': self.max_chunk_size,
                'min_chunk_size': self.min_chunk_size,
                'overlap_ratio': self.overlap_ratio
            }
        }
    
    def adjust_parameters(
        self,
        base_chunk_size: Optional[int] = None,
        max_chunk_size: Optional[int] = None,
        min_chunk_size: Optional[int] = None,
        overlap_ratio: Optional[float] = None
    ):
        """Dynamically adjust chunking parameters"""
        if base_chunk_size is not None:
            self.base_chunk_size = base_chunk_size
        if max_chunk_size is not None:
            self.max_chunk_size = max_chunk_size
        if min_chunk_size is not None:
            self.min_chunk_size = min_chunk_size
        if overlap_ratio is not None:
            self.overlap_ratio = overlap_ratio
        
        # Reinitialize splitters with new parameters
        self.splitters = self._initialize_splitters()
        
        logger.info(
            f"Chunking parameters updated: base={self.base_chunk_size}, "
            f"max={self.max_chunk_size}, min={self.min_chunk_size}, overlap={self.overlap_ratio}"
        )