"""
Base Parser Interface
Abstract base class for all document parsers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class DocumentType(Enum):
    """Supported document types"""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XML = "xml"
    TXT = "txt"
    MD = "md"
    JSON = "json"
    HTML = "html"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class ParsedDocument:
    """
    Standardized output from any parser
    All parsers must return this format
    """
    content: str
    filename: str
    doc_type: DocumentType
    
    # Metadata extracted from document
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    
    # Content structure
    chunks: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    
    # Document-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing info
    page_count: int = 0
    word_count: int = 0
    char_count: int = 0
    parsing_method: str = "unknown"
    
    def __post_init__(self):
        """Calculate stats if not provided"""
        if not self.char_count:
            self.char_count = len(self.content)
        if not self.word_count:
            self.word_count = len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "content": self.content,
            "filename": self.filename,
            "doc_type": self.doc_type.value,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at,
            "chunks": self.chunks,
            "tables": self.tables,
            "metadata": self.metadata,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "parsing_method": self.parsing_method
        }


class BaseParser(ABC):
    """
    Abstract base class for document parsers
    
    All parsers must implement:
    - parse(): Parse document and return ParsedDocument
    - supported_types: List of supported DocumentTypes
    """
    
    @property
    @abstractmethod
    def supported_types(self) -> List[DocumentType]:
        """Return list of document types this parser handles"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Parser name for logging"""
        pass
    
    @abstractmethod
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse document content
        
        Args:
            content: Raw file bytes
            filename: Original filename
            **kwargs: Parser-specific options
            
        Returns:
            ParsedDocument with extracted content and metadata
        """
        pass
    
    def can_parse(self, filename: str) -> bool:
        """Check if this parser can handle the file"""
        doc_type = self._detect_type(filename)
        return doc_type in self.supported_types
    
    def _detect_type(self, filename: str) -> DocumentType:
        """Detect document type from filename"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        type_map = {
            'pdf': DocumentType.PDF,
            'docx': DocumentType.DOCX,
            'doc': DocumentType.DOCX,
            'pptx': DocumentType.PPTX,
            'ppt': DocumentType.PPTX,
            'xml': DocumentType.XML,
            'txt': DocumentType.TXT,
            'md': DocumentType.MD,
            'markdown': DocumentType.MD,
            'json': DocumentType.JSON,
            'html': DocumentType.HTML,
            'htm': DocumentType.HTML,
            'png': DocumentType.IMAGE,
            'jpg': DocumentType.IMAGE,
            'jpeg': DocumentType.IMAGE,
        }
        
        return type_map.get(ext, DocumentType.UNKNOWN)
