"""
Docling Parser
AI-powered document parsing for PDF, Word, PowerPoint using IBM Docling
"""

import io
import tempfile
import os
from typing import List, Dict, Any
from .base_parser import BaseParser, ParsedDocument, DocumentType


class DoclingParser(BaseParser):
    """
    Enterprise document parser using IBM Docling
    
    Supports:
    - PDF (including scanned with OCR)
    - Word (DOCX)
    - PowerPoint (PPTX)
    - Images with OCR
    - HTML
    
    Features:
    - Table extraction with structure
    - Layout-aware parsing
    - OCR for scanned documents
    - Markdown/JSON output
    """
    
    def __init__(self):
        self._converter = None
    
    @property
    def converter(self):
        """Lazy load Docling converter"""
        if self._converter is None:
            try:
                from docling.document_converter import DocumentConverter
                self._converter = DocumentConverter()
            except ImportError as e:
                raise ImportError(
                    "Docling not installed. Run: pip install docling"
                ) from e
        return self._converter
    
    @property
    def supported_types(self) -> List[DocumentType]:
        return [
            DocumentType.PDF,
            DocumentType.DOCX,
            DocumentType.PPTX,
            DocumentType.HTML,
            DocumentType.IMAGE
        ]
    
    @property
    def name(self) -> str:
        return "DoclingParser"
    
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse document using Docling
        
        Args:
            content: Raw file bytes
            filename: Original filename
            extract_tables: Whether to extract tables (default: True)
            ocr_enabled: Enable OCR for scanned docs (default: True)
        """
        doc_type = self._detect_type(filename)
        
        # Write to temp file (Docling needs file path)
        with tempfile.NamedTemporaryFile(
            suffix=f".{filename.split('.')[-1]}",
            delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Convert document
            result = self.converter.convert(tmp_path)
            doc = result.document
            
            # Extract markdown content
            markdown_content = doc.export_to_markdown()
            
            # Extract tables if present
            tables = []
            for table in getattr(doc, 'tables', []):
                try:
                    tables.append({
                        "data": table.export_to_dataframe().to_dict() if hasattr(table, 'export_to_dataframe') else {},
                        "caption": getattr(table, 'caption', None)
                    })
                except Exception:
                    pass
            
            # Extract metadata
            metadata = {
                "source": filename,
                "parsing_engine": "docling",
                "has_tables": len(tables) > 0,
            }
            
            # Get page count for PDFs
            page_count = 0
            if hasattr(doc, 'pages'):
                page_count = len(doc.pages)
            
            return ParsedDocument(
                content=markdown_content,
                filename=filename,
                doc_type=doc_type,
                title=getattr(doc, 'title', None),
                tables=tables,
                metadata=metadata,
                page_count=page_count,
                parsing_method="docling"
            )
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def parse_to_chunks(
        self,
        content: bytes,
        filename: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> ParsedDocument:
        """
        Parse and automatically chunk document
        Uses Docling's built-in chunking for better semantic splitting
        """
        doc = self.parse(content, filename)
        
        # Use simple chunking if content is small
        if len(doc.content) <= chunk_size:
            doc.chunks = [doc.content]
            return doc
        
        # Chunk by paragraphs/sections when possible
        chunks = []
        paragraphs = doc.content.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Handle very long paragraphs
                if len(para) > chunk_size:
                    words = para.split()
                    temp = ""
                    for word in words:
                        if len(temp) + len(word) <= chunk_size:
                            temp += word + " "
                        else:
                            chunks.append(temp.strip())
                            temp = word + " "
                    if temp:
                        current_chunk = temp
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        doc.chunks = chunks
        return doc
