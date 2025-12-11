"""
PyMuPDF Parser
Lightweight, fast PDF parsing using PyMuPDF (fitz)
"""

import io
from typing import List, Dict, Any
from .base_parser import BaseParser, ParsedDocument, DocumentType


class PyMuPdfParser(BaseParser):
    """
    Lightweight PDF parser using PyMuPDF (fitz)
    
    Advantages over Docling:
    - Much faster for simple PDFs
    - Lower memory usage
    - No heavy ML dependencies
    - Better for text-based PDFs
    
    Use Docling instead if you need:
    - Complex table extraction
    - OCR for scanned documents
    - Layout-aware parsing
    """
    
    def __init__(self):
        self._fitz = None
    
    @property
    def fitz(self):
        """Lazy load fitz (PyMuPDF)"""
        if self._fitz is None:
            try:
                import fitz
                self._fitz = fitz
            except ImportError as e:
                raise ImportError(
                    "PyMuPDF not installed. Run: pip install pymupdf"
                ) from e
        return self._fitz
    
    @property
    def supported_types(self) -> List[DocumentType]:
        return [DocumentType.PDF]
    
    @property
    def name(self) -> str:
        return "PyMuPdfParser"
    
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse PDF using PyMuPDF with proper reading order
        
        Uses block-based extraction with sorting for correct text order.
        Each block is sorted by vertical position, then horizontal.
        
        Args:
            content: Raw PDF bytes
            filename: Original filename
        """
        doc_type = self._detect_type(filename)
        
        # Open PDF from bytes
        pdf_doc = self.fitz.open(stream=content, filetype="pdf")
        
        try:
            all_page_text = []
            page_data = []  # For page-based chunking
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Extract text blocks with positions
                # blocks format: (x0, y0, x1, y1, "text", block_no, block_type)
                blocks = page.get_text("blocks")
                
                # Filter to text blocks only (block_type 0 = text)
                text_blocks = [b for b in blocks if b[6] == 0]
                
                # Sort blocks by reading order: top-to-bottom, then left-to-right
                # Sort by y0 (vertical), then x0 (horizontal) with tolerance
                sorted_blocks = sorted(
                    text_blocks,
                    key=lambda b: (
                        round(b[1] / 20) * 20,  # Group by ~20pt vertical bands
                        b[0]  # Then by horizontal position
                    )
                )
                
                # Extract text from sorted blocks
                page_text_parts = []
                for block in sorted_blocks:
                    block_text = block[4].strip()
                    if block_text:
                        page_text_parts.append(block_text)
                
                page_text = "\n".join(page_text_parts)
                
                if page_text.strip():
                    page_data.append({
                        "page": page_num + 1,
                        "text": page_text.strip()
                    })
                    all_page_text.append(f"--- Seite {page_num + 1} ---\n{page_text}")
            
            # Combine all pages
            content_text = "\n\n".join(all_page_text) if all_page_text else ""
            
            # Extract metadata
            metadata = {
                "source": filename,
                "parsing_engine": "pymupdf",
                "page_count": len(pdf_doc),
                "page_data": page_data,  # For page-based chunking
            }
            
            # Get PDF metadata if available
            pdf_metadata = pdf_doc.metadata
            if pdf_metadata:
                if pdf_metadata.get("title"):
                    metadata["pdf_title"] = pdf_metadata["title"]
                if pdf_metadata.get("author"):
                    metadata["pdf_author"] = pdf_metadata["author"]
                if pdf_metadata.get("subject"):
                    metadata["pdf_subject"] = pdf_metadata["subject"]
            
            # Count words
            word_count = len(content_text.split()) if content_text else 0
            
            # Get title
            title = pdf_metadata.get("title") if pdf_metadata else None
            if not title and page_data:
                # Use first line from first page
                first_page = page_data[0]["text"]
                first_line = first_page.split('\n')[0].strip()
                if 10 < len(first_line) < 150:
                    title = first_line
            
            return ParsedDocument(
                content=content_text,
                filename=filename,
                doc_type=doc_type,
                title=title,
                tables=[],
                metadata=metadata,
                page_count=len(pdf_doc),
                word_count=word_count,
                parsing_method="pymupdf"
            )
            
        finally:
            pdf_doc.close()
    
    def extract_images(
        self,
        content: bytes,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Extract images from PDF
        
        Returns list of image info with bytes
        """
        pdf_doc = self.fitz.open(stream=content, filetype="pdf")
        images = []
        
        try:
            for page_num, page in enumerate(pdf_doc):
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    try:
                        base_image = pdf_doc.extract_image(xref)
                        images.append({
                            "page": page_num + 1,
                            "index": img_index,
                            "width": base_image.get("width"),
                            "height": base_image.get("height"),
                            "colorspace": base_image.get("colorspace"),
                            "ext": base_image.get("ext"),
                            "image_bytes": base_image.get("image")
                        })
                    except Exception:
                        pass
                        
        finally:
            pdf_doc.close()
        
        return images
