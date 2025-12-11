"""
Image Parser
OCR-based parsing for image files using Docling
"""

import io
import tempfile
import os
from typing import List
from .base_parser import BaseParser, ParsedDocument, DocumentType


class ImageParser(BaseParser):
    """
    Parser for image files with OCR
    
    Uses Docling for optical character recognition
    Supports: PNG, JPG, JPEG
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
        return [DocumentType.IMAGE]
    
    @property
    def name(self) -> str:
        return "ImageParser"
    
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse image using OCR via Docling
        """
        doc_type = DocumentType.IMAGE
        
        # Write to temp file
        ext = filename.split('.')[-1].lower() if '.' in filename else 'png'
        with tempfile.NamedTemporaryFile(
            suffix=f".{ext}",
            delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Convert using Docling
            result = self.converter.convert(tmp_path)
            doc = result.document
            
            # Extract text content
            text_content = doc.export_to_markdown()
            
            # Clean up empty image placeholders
            if "<!-- image -->" in text_content and len(text_content.strip()) < 50:
                text_content = f"[Bild: {filename}]\n\n" + text_content
            
            metadata = {
                "source": filename,
                "parsing_engine": "docling_ocr",
                "image_format": ext,
                "ocr_applied": True
            }
            
            return ParsedDocument(
                content=text_content,
                filename=filename,
                doc_type=doc_type,
                metadata=metadata,
                parsing_method="docling_ocr"
            )
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
