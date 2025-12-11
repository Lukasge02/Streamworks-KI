"""
Parser Registry
Central registry for document parsers - enables modular parser management
"""

from typing import Dict, Type, Optional, List
from .base_parser import BaseParser, ParsedDocument, DocumentType
from .text_parser import TextParser


class ParserRegistry:
    """
    Central registry for document parsers
    
    Manages parser selection based on document type
    Allows adding custom parsers at runtime
    
    Parser Priority:
    1. PyMuPDF for PDFs (fast, lightweight)
    2. Docling for DOCX, PPTX, HTML, Images (OCR, tables)
    3. TextParser for TXT, MD, JSON, XML
    """
    
    def __init__(self):
        self._parsers: Dict[DocumentType, BaseParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register built-in parsers"""
        # 1. Text parser for simple formats
        text_parser = TextParser()
        for doc_type in text_parser.supported_types:
            self._parsers[doc_type] = text_parser
        
        # 2. PyMuPDF parser for PDFs (fast, lightweight)
        try:
            from .pymupdf_parser import PyMuPdfParser
            pymupdf_parser = PyMuPdfParser()
            self._parsers[DocumentType.PDF] = pymupdf_parser
            print("✅ PyMuPDF parser registered for PDFs")
        except ImportError:
            print("⚠️ PyMuPDF not available")
        
        # 3. Docling parser for complex formats (DOCX, PPTX, HTML, Images)
        # Note: Docling will NOT override PDF if PyMuPDF is available
        try:
            from .docling_parser import DoclingParser
            docling_parser = DoclingParser()
            for doc_type in docling_parser.supported_types:
                # Only register if not already handled by PyMuPDF
                if doc_type not in self._parsers:
                    self._parsers[doc_type] = docling_parser
            print("✅ Docling parser registered for DOCX, PPTX, HTML, Images")
        except ImportError:
            print("⚠️ Docling not available - some formats may not be supported")
    
    def register(self, parser: BaseParser, override: bool = False):
        """
        Register a custom parser
        
        Args:
            parser: Parser instance
            override: If True, override existing parsers for same types
        """
        for doc_type in parser.supported_types:
            if override or doc_type not in self._parsers:
                self._parsers[doc_type] = parser
    
    def get_parser(self, filename: str) -> Optional[BaseParser]:
        """Get appropriate parser for file"""
        doc_type = self._detect_type(filename)
        return self._parsers.get(doc_type)
    
    def can_parse(self, filename: str) -> bool:
        """Check if any parser can handle this file"""
        return self.get_parser(filename) is not None
    
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse document using appropriate parser
        
        Raises:
            ValueError: If no parser available for file type
        """
        parser = self.get_parser(filename)
        if parser is None:
            raise ValueError(f"No parser available for: {filename}")
        
        return parser.parse(content, filename, **kwargs)
    
    def list_supported_types(self) -> List[str]:
        """Get list of supported file extensions"""
        return [dt.value for dt in self._parsers.keys()]
    
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


# Global registry instance
parser_registry = ParserRegistry()
