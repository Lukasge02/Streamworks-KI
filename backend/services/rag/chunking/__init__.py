"""
Enterprise Chunking Service
Advanced text chunking for RAG with multiple strategies
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ChunkingStrategy(Enum):
    """Available chunking strategies"""
    SEMANTIC = "semantic"           # Sentence/paragraph aware
    FIXED = "fixed"                 # Fixed character size
    PAGE_BASED = "page_based"       # Respect page boundaries
    HYBRID = "hybrid"               # Combination of semantic + size limits


@dataclass
class ChunkMetadata:
    """Metadata for a single chunk"""
    chunk_index: int
    total_chunks: int
    start_char: int
    end_char: int
    page_numbers: List[int] = field(default_factory=list)
    section_title: Optional[str] = None
    word_count: int = 0
    sentence_count: int = 0


@dataclass
class Chunk:
    """A single chunk with content and metadata"""
    content: str
    metadata: ChunkMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "chunk_index": self.metadata.chunk_index,
            "total_chunks": self.metadata.total_chunks,
            "start_char": self.metadata.start_char,
            "end_char": self.metadata.end_char,
            "page_numbers": self.metadata.page_numbers,
            "section_title": self.metadata.section_title,
            "word_count": self.metadata.word_count,
            "sentence_count": self.metadata.sentence_count,
        }


class EnterpriseChunker:
    """
    Enterprise-grade text chunking service
    
    Features:
    - Multiple chunking strategies
    - Sentence and paragraph awareness
    - Page number tracking (for PDFs)
    - Section detection
    - Configurable overlap
    - Rich chunk metadata
    """
    
    # Regex patterns for text splitting
    SENTENCE_PATTERN = re.compile(r'(?<=[.!?])\s+(?=[A-ZÄÖÜ])')
    PARAGRAPH_PATTERN = re.compile(r'\n\s*\n')
    PAGE_MARKER_PATTERN = re.compile(r'--- Seite (\d+) ---')
    SECTION_PATTERN = re.compile(r'^(?:#{1,6}\s+|(?:\d+\.)+\s+|\*\*[^*]+\*\*\s*$)', re.MULTILINE)
    
    def __init__(
        self,
        max_chunk_size: int = 1500,
        min_chunk_size: int = 100,
        overlap_size: int = 150,
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_size = overlap_size
        self.strategy = strategy
    
    def chunk(
        self,
        text: str,
        strategy: Optional[ChunkingStrategy] = None,
        page_info: Optional[List[Dict[str, Any]]] = None
    ) -> List[Chunk]:
        """
        Chunk text using specified or default strategy
        
        Args:
            text: Text to chunk
            strategy: Override default strategy
            page_info: Optional page information from PDF parser
            
        Returns:
            List of Chunk objects with metadata
        """
        if not text or not text.strip():
            return []
        
        strategy = strategy or self.strategy
        
        if strategy == ChunkingStrategy.PAGE_BASED and page_info:
            return self._chunk_by_pages(text, page_info)
        elif strategy == ChunkingStrategy.SEMANTIC:
            return self._chunk_semantic(text)
        elif strategy == ChunkingStrategy.HYBRID:
            return self._chunk_hybrid(text)
        else:
            return self._chunk_fixed(text)
    
    def _chunk_semantic(self, text: str) -> List[Chunk]:
        """
        Semantic chunking - respects sentences and paragraphs
        """
        # Split into paragraphs first
        paragraphs = self.PARAGRAPH_PATTERN.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_start = 0
        char_position = 0
        
        for para in paragraphs:
            # Check if adding this paragraph exceeds max size
            if len(current_chunk) + len(para) + 2 > self.max_chunk_size:
                # If current chunk is big enough, save it
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(
                        current_chunk.strip(),
                        len(chunks),
                        current_start,
                        char_position
                    ))
                    # Start new chunk with overlap
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = overlap_text + para + "\n\n"
                    current_start = char_position - len(overlap_text)
                else:
                    # Current chunk too small, need to split paragraph
                    sentences = self._split_into_sentences(para)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > self.max_chunk_size:
                            if len(current_chunk) >= self.min_chunk_size:
                                chunks.append(self._create_chunk(
                                    current_chunk.strip(),
                                    len(chunks),
                                    current_start,
                                    char_position
                                ))
                                overlap_text = self._get_overlap(current_chunk)
                                current_chunk = overlap_text + sentence + " "
                                current_start = char_position - len(overlap_text)
                            else:
                                current_chunk += sentence + " "
                        else:
                            current_chunk += sentence + " "
                    current_chunk += "\n\n"
            else:
                current_chunk += para + "\n\n"
            
            char_position += len(para) + 2  # +2 for paragraph separator
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(
                current_chunk.strip(),
                len(chunks),
                current_start,
                char_position
            ))
        
        # Update total_chunks in all chunk metadata
        total = len(chunks)
        for chunk in chunks:
            chunk.metadata.total_chunks = total
        
        return chunks
    
    def _chunk_hybrid(self, text: str) -> List[Chunk]:
        """
        Hybrid chunking - semantic with strict size limits
        Falls back to sentence/word splitting for very long paragraphs
        """
        # First try semantic chunking
        semantic_chunks = self._chunk_semantic(text)
        
        # Post-process: ensure no chunk exceeds max size
        final_chunks = []
        for chunk in semantic_chunks:
            if len(chunk.content) <= self.max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split oversized chunks by sentences
                sub_chunks = self._split_oversized(chunk.content, chunk.metadata.start_char)
                final_chunks.extend(sub_chunks)
        
        # Renumber chunks
        total = len(final_chunks)
        for i, chunk in enumerate(final_chunks):
            chunk.metadata.chunk_index = i
            chunk.metadata.total_chunks = total
        
        return final_chunks
    
    def _chunk_by_pages(self, text: str, page_info: List[Dict[str, Any]]) -> List[Chunk]:
        """
        Page-based chunking - each page becomes a chunk (or multiple if too large)
        """
        chunks = []
        char_position = 0
        
        for page_data in page_info:
            page_num = page_data.get("page", 0)
            page_text = page_data.get("text", "")
            
            if not page_text.strip():
                continue
            
            # If page is small enough, make it one chunk
            if len(page_text) <= self.max_chunk_size:
                chunk = self._create_chunk(
                    page_text.strip(),
                    len(chunks),
                    char_position,
                    char_position + len(page_text),
                    page_numbers=[page_num]
                )
                chunks.append(chunk)
            else:
                # Split large page using semantic chunking
                page_chunks = self._chunk_semantic(page_text)
                for pc in page_chunks:
                    pc.metadata.page_numbers = [page_num]
                    pc.metadata.start_char += char_position
                    pc.metadata.end_char += char_position
                    pc.metadata.chunk_index = len(chunks)
                    chunks.append(pc)
            
            char_position += len(page_text)
        
        # Update total_chunks
        total = len(chunks)
        for chunk in chunks:
            chunk.metadata.total_chunks = total
        
        return chunks
    
    def _chunk_fixed(self, text: str) -> List[Chunk]:
        """
        Simple fixed-size chunking with overlap
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            if end >= len(text):
                chunk_text = text[start:].strip()
                if chunk_text:
                    chunks.append(self._create_chunk(chunk_text, len(chunks), start, len(text)))
                break
            
            # Find a good break point
            break_point = self._find_break_point(text, start, end)
            chunk_text = text[start:break_point].strip()
            
            if chunk_text:
                chunks.append(self._create_chunk(chunk_text, len(chunks), start, break_point))
            
            start = max(0, break_point - self.overlap_size)
        
        # Update total
        total = len(chunks)
        for chunk in chunks:
            chunk.metadata.total_chunks = total
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = self.SENTENCE_PATTERN.split(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, text: str) -> str:
        """Get overlap text from end of chunk"""
        if len(text) <= self.overlap_size:
            return text
        
        overlap = text[-self.overlap_size:]
        # Try to start at a word boundary
        space_pos = overlap.find(' ')
        if space_pos > 0:
            return overlap[space_pos + 1:]
        return overlap
    
    def _split_oversized(self, text: str, start_offset: int) -> List[Chunk]:
        """Split an oversized chunk into smaller pieces"""
        sentences = self._split_into_sentences(text)
        chunks = []
        current = ""
        current_start = start_offset
        
        for sentence in sentences:
            if len(current) + len(sentence) + 1 > self.max_chunk_size:
                if current:
                    chunks.append(self._create_chunk(
                        current.strip(),
                        0,  # Will be renumbered
                        current_start,
                        current_start + len(current)
                    ))
                    current_start += len(current)
                
                # Handle very long sentences
                if len(sentence) > self.max_chunk_size:
                    words = sentence.split()
                    word_chunk = ""
                    for word in words:
                        if len(word_chunk) + len(word) + 1 > self.max_chunk_size:
                            if word_chunk:
                                chunks.append(self._create_chunk(
                                    word_chunk.strip(),
                                    0,
                                    current_start,
                                    current_start + len(word_chunk)
                                ))
                                current_start += len(word_chunk)
                            word_chunk = word + " "
                        else:
                            word_chunk += word + " "
                    current = word_chunk
                else:
                    current = sentence + " "
            else:
                current += sentence + " "
        
        if current.strip():
            chunks.append(self._create_chunk(
                current.strip(),
                0,
                current_start,
                current_start + len(current)
            ))
        
        return chunks
    
    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """Find a natural break point"""
        search_start = start + (end - start) // 2
        
        for delimiter in ['\n\n', '\n', '. ', '! ', '? ', '; ', ', ', ' ']:
            pos = text.rfind(delimiter, search_start, end)
            if pos != -1:
                return pos + len(delimiter)
        
        return end
    
    def _create_chunk(
        self,
        content: str,
        index: int,
        start: int,
        end: int,
        page_numbers: Optional[List[int]] = None
    ) -> Chunk:
        """Create a chunk with metadata"""
        # Detect section title if present
        section_title = None
        lines = content.split('\n')
        if lines:
            first_line = lines[0].strip()
            if self.SECTION_PATTERN.match(first_line) or (
                len(first_line) < 100 and first_line.isupper()
            ):
                section_title = first_line[:100]
        
        # Extract page numbers from content if not provided
        if page_numbers is None:
            page_numbers = []
            for match in self.PAGE_MARKER_PATTERN.finditer(content):
                page_numbers.append(int(match.group(1)))
        
        metadata = ChunkMetadata(
            chunk_index=index,
            total_chunks=0,  # Will be updated later
            start_char=start,
            end_char=end,
            page_numbers=page_numbers or [],
            section_title=section_title,
            word_count=len(content.split()),
            sentence_count=len(self.SENTENCE_PATTERN.split(content))
        )
        
        return Chunk(content=content, metadata=metadata)


# Default chunker instance
enterprise_chunker = EnterpriseChunker(
    max_chunk_size=1500,
    min_chunk_size=100,
    overlap_size=150,
    strategy=ChunkingStrategy.SEMANTIC
)
