"""
Docling Document Ingestion Service
Layout-aware parsing von PDF, DOCX, HTML mit strukturierten Metadaten
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
# Note: ImageFormatOption and OcrOptions might need adjustment based on Docling version

# Intelligent chunking system
from .intelligent_chunker import IntelligentChunker, ContentType, ChunkingConfig

from config import settings
import tempfile
from PIL import Image
import io

class DocumentChunk:
    """Represents a document chunk with metadata"""
    
    def __init__(
        self,
        content: str,
        doc_id: str,
        chunk_id: str,
        page_number: Optional[int] = None,
        heading: Optional[str] = None,
        section: Optional[str] = None,
        doctype: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.page_number = page_number
        self.heading = heading
        self.section = section
        self.doctype = doctype
        self.metadata = metadata or {}
        
        # Add computed metadata
        self.metadata.update({
            "chunk_length": len(content),
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat()
        })

class DoclingIngestService:
    """Service für document processing mit Docling"""
    
    def __init__(self):
        self.converter = None
        self.chunker = None  # New intelligent chunker
        self._initialized = False
        self._initialization_error = None
        
    def _initialize(self):
        """Lazy initialization of Docling service"""
        if self._initialized:
            return True
            
        if self._initialization_error:
            raise self._initialization_error
            
        try:
            # Configure Docling with PDF pipeline options - Optimized for better text extraction
            self.pipeline_options = PdfPipelineOptions(
                do_ocr=True,  # Enable OCR for scanned PDFs
                do_table_structure=True,  # Enable table structure - may contain useful content
                generate_page_images=False,  # Disable images for better performance
                generate_table_images=False  # Disable table images but keep table structure
            )
            
            # Initialize document converter - Docling handles images automatically
            self.converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)
                }
            )
            
            # Initialize intelligent chunker with optimized settings
            chunking_config = ChunkingConfig(
                min_chunk_size=settings.MIN_CHUNK_SIZE,
                max_chunk_size=settings.MAX_CHUNK_SIZE,
                pdf_chunk_size=settings.PDF_CHUNK_SIZE,
                text_chunk_size=settings.TEXT_CHUNK_SIZE,
                min_word_count=settings.MIN_WORD_COUNT,
                overlap_ratio=settings.CHUNK_OVERLAP / settings.TEXT_CHUNK_SIZE  # Convert to ratio
            )
            
            self.chunker = IntelligentChunker(config=chunking_config)
            
            self._initialized = True
            return True
            
        except Exception as e:
            self._initialization_error = e
            raise e
            
    def _detect_content_type(self, file_path: str, file_type: str = None) -> ContentType:
        """
        Detect the appropriate content type for intelligent chunking
        
        Args:
            file_path: Path to the file being processed
            file_type: Optional file type override
            
        Returns:
            ContentType for specialized chunking
        """
        if file_type:
            # Map string types to ContentType enum
            type_mapping = {
                'pdf': ContentType.PDF,
                'text': ContentType.TEXT,
                'html': ContentType.HTML,
                'markdown': ContentType.MARKDOWN,
                'code': ContentType.CODE,
                'table': ContentType.TABLE
            }
            if file_type in type_mapping:
                return type_mapping[file_type]
        
        # Detect from file extension
        if file_path:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return ContentType.PDF
            elif file_extension in ['.md', '.markdown']:
                return ContentType.MARKDOWN
            elif file_extension in ['.html', '.htm']:
                return ContentType.HTML
            elif file_extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.xml', '.json']:
                return ContentType.CODE
            elif file_extension in ['.txt', '.docx']:
                return ContentType.TEXT
        
        # Default to text
        return ContentType.TEXT
    
    async def process_document(
        self, 
        file_path: str, 
        doctype: str = "general"
    ) -> List[DocumentChunk]:
        """
        Process document mit Docling und erstelle strukturierte chunks
        
        Args:
            file_path: Pfad zur Datei
            doctype: Dokumenttyp (general, xml, etc.)
            
        Returns:
            List von DocumentChunk Objekten
        """
        try:
            # Initialize service if not already done (lazy loading)
            self._initialize()
            
            doc_path = Path(file_path)
            
            # Validate file exists and is readable
            if not doc_path.exists():
                raise FileNotFoundError(f"Document file not found: {file_path}")
            
            if not doc_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            if doc_path.stat().st_size == 0:
                raise ValueError(f"File is empty: {file_path}")
            
            if doc_path.stat().st_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {doc_path.stat().st_size} bytes (max: {settings.MAX_FILE_SIZE})")
            
            doc_id = doc_path.stem
            
            # Handle text files directly
            if doc_path.suffix.lower() in ['.txt', '.md']:
                return await self._process_text_file(doc_path, doc_id, doctype)
            
            # Handle image files with OCR
            image_formats = ['.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp']
            if doc_path.suffix.lower() in image_formats:
                return await self._process_image_file(doc_path, doc_id, doctype)
            
            # Validate supported file formats
            supported_formats = ['.pdf', '.docx', '.html', '.htm', '.txt', '.md'] + image_formats
            if doc_path.suffix.lower() not in supported_formats:
                raise ValueError(f"Unsupported file format: {doc_path.suffix}. Supported: {supported_formats}")
            
            # Convert document with Docling for PDF/DOCX/HTML
            result = self.converter.convert(doc_path)
            if not result or not hasattr(result, 'document'):
                raise ValueError("Document conversion failed - no result returned")
            
            document = result.document
            if not document:
                raise ValueError("Document conversion failed - empty document")
            
            chunks = []
            chunk_counter = 0
            
            # Validate document has text content
            if not hasattr(document, 'texts') or not document.texts:
                logger.warning(f"Document has no extractable text content: {file_path}")
                logger.info(f"Document structure: {dir(document)}")
                raise ValueError(f"Document has no extractable text content: {file_path}")
            
            logger.info(f"Processing {len(document.texts)} text items from {file_path}")
            
            # FIXED: Extract text with improved fragmentation handling
            logger.info(f"Extracting text from {len(document.texts)} document items")
            
            # Strategy: Combine small consecutive text items to handle fragmented PDFs
            combined_text_items = []
            current_combined = ""
            current_page = None
            current_heading = None
            current_section = None
            
            for item_ix, item in enumerate(document.texts):
                try:
                    # Validate item has text content
                    if not hasattr(item, 'text') or not item.text:
                        continue
                    
                    text = item.text.strip()
                    if not text:
                        continue
                    
                    # Get page number
                    page_num = None
                    if hasattr(item, 'prov') and item.prov:
                        try:
                            page_num = getattr(item.prov[0], 'page', None)
                        except (IndexError, AttributeError):
                            pass
                    
                    # If this is a very small text item (likely fragmented), combine it
                    if len(text) < 50 and len(text.split()) < 5:
                        # Add space if not punctuation
                        if current_combined and not text.startswith((':', ';', ',', '.', '!', '?')):
                            current_combined += " "
                        current_combined += text
                        
                        # Update page/section info if this is the first item
                        if current_page is None:
                            current_page = page_num
                            current_heading = self._extract_heading(document, item_ix)
                            current_section = self._extract_section(document, item_ix)
                    else:
                        # This is a substantial text item - flush any combined text first
                        if current_combined:
                            combined_text_items.append({
                                'text': current_combined,
                                'page': current_page,
                                'heading': current_heading,
                                'section': current_section,
                                'item_index': item_ix - 1
                            })
                            current_combined = ""
                        
                        # Add this substantial item
                        combined_text_items.append({
                            'text': text,
                            'page': page_num,
                            'heading': self._extract_heading(document, item_ix),
                            'section': self._extract_section(document, item_ix),
                            'item_index': item_ix
                        })
                        
                        current_page = None
                        current_heading = None
                        current_section = None
                        
                except Exception as e:
                    logger.debug(f"Error processing item {item_ix}: {str(e)}")
                    continue
            
            # Don't forget the last combined text if any
            if current_combined:
                combined_text_items.append({
                    'text': current_combined,
                    'page': current_page,
                    'heading': current_heading,
                    'section': current_section,
                    'item_index': len(document.texts) - 1
                })
            
            logger.info(f"Combined {len(document.texts)} items into {len(combined_text_items)} text blocks")
            
            # Now process the combined text items
            for text_item in combined_text_items:
                try:
                    text = text_item['text']
                    
                    # Use intelligent chunker with semantic boundaries
                    content_type = self._detect_content_type(file_path, 'pdf')
                    
                    base_metadata = {
                        "source_file": doc_path.name,
                        "item_index": text_item['item_index'],
                        "page_number": text_item['page'],
                        "heading": text_item['heading'],
                        "section": text_item['section'],
                        "is_combined": True
                    }
                    
                    # Apply intelligent chunking with quality gates
                    intelligent_chunks = self.chunker.chunk_content(
                        content=text,
                        content_type=content_type,
                        metadata=base_metadata
                    )
                    
                    # Convert intelligent chunks to DocumentChunk objects
                    for i, chunk_data in enumerate(intelligent_chunks):
                        chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                        
                        # Combine base metadata with chunk-specific metadata
                        combined_metadata = {**base_metadata, **chunk_data['metadata']}
                        combined_metadata.update({
                            "chunk_index": i,
                            "total_chunks": len(intelligent_chunks),
                            "quality_score": chunk_data.get('quality_score', 0.0),
                            "has_overlap": chunk_data.get('has_overlap', False)
                        })
                        
                        chunk = DocumentChunk(
                            content=chunk_data['content'].strip(),
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            page_number=text_item['page'],
                            heading=text_item['heading'],
                            section=text_item['section'],
                            doctype=doctype,
                            metadata=combined_metadata
                        )
                        
                        chunks.append(chunk)
                        chunk_counter += 1
                        
                        if chunk_counter <= 5:  # Log first 5 chunks for debugging
                            logger.debug(f"Created chunk {chunk_counter}: {len(content)} chars, page {text_item['page']}")
                        
                except Exception as item_error:
                    logger.warning(f"Error processing combined text item: {str(item_error)}")
                    continue
            
            # Extract and process tables separately
            table_chunks = await self._process_tables(document, doc_id, doctype)
            chunks.extend(table_chunks)
            
            logger.info(f"✅ Processed {doc_path.name}: {len(chunks)} chunks created")
            if len(chunks) == 0:
                logger.warning(f"⚠️  No chunks created for {doc_path.name} - check content quality filters")
            print(f"✅ Processed {doc_path.name}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {str(e)}", exc_info=True)
            print(f"❌ Error processing {file_path}: {str(e)}")
            raise Exception(f"Document processing failed: {str(e)}")
    
    async def _process_text_file(
        self,
        doc_path: Path,
        doc_id: str,
        doctype: str
    ) -> List[DocumentChunk]:
        """Process plain text files (TXT, MD)"""
        try:
            # Read file content
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections by headers (for Markdown)
            sections = []
            if doc_path.suffix.lower() == '.md':
                sections = self._parse_markdown_sections(content)
            else:
                sections = [{"heading": None, "content": content}]
            
            chunks = []
            chunk_counter = 0
            
            for section in sections:
                # Use intelligent chunker with content-type detection
                content_type = self._detect_content_type(str(doc_path))
                
                base_metadata = {
                    "source_file": doc_path.name,
                    "section_heading": section["heading"],
                    "is_text_file": True
                }
                
                # Apply intelligent chunking
                intelligent_chunks = self.chunker.chunk_content(
                    content=section["content"],
                    content_type=content_type,
                    metadata=base_metadata
                )
                
                for i, chunk_data in enumerate(intelligent_chunks):
                    chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                    
                    # Combine metadata
                    combined_metadata = {**base_metadata, **chunk_data['metadata']}
                    combined_metadata.update({
                        "chunk_index": i,
                        "total_chunks": len(intelligent_chunks),
                        "quality_score": chunk_data.get('quality_score', 0.0)
                    })
                    
                    chunk = DocumentChunk(
                        content=chunk_data['content'].strip(),
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        heading=section["heading"],
                        doctype=doctype,
                        metadata=combined_metadata
                    )
                    
                    chunks.append(chunk)
                    chunk_counter += 1
            
            print(f"✅ Processed text file {doc_path.name}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            print(f"❌ Error processing text file {doc_path}: {str(e)}")
            raise
    
    async def _process_image_file(
        self,
        doc_path: Path,
        doc_id: str,
        doctype: str
    ) -> List[DocumentChunk]:
        """Process image files with OCR using Docling"""
        try:
            print(f"🔍 Processing image file with OCR: {doc_path.name}")
            
            # Convert image with Docling
            result = self.converter.convert(doc_path)
            if not result or not hasattr(result, 'document'):
                raise ValueError("Image OCR failed - no result returned")
            
            document = result.document
            if not document:
                raise ValueError("Image OCR failed - empty document")
            
            # Extract text from OCR result
            chunks = []
            chunk_counter = 0
            
            if hasattr(document, 'texts') and document.texts:
                full_text = ""
                for item in document.texts:
                    if hasattr(item, 'text') and item.text:
                        full_text += item.text + "\n"
                
                if full_text.strip():
                    # Use intelligent chunker for OCR text processing
                    content_type = ContentType.TEXT  # OCR text treated as plain text
                    
                    base_metadata = {
                        "source_file": doc_path.name,
                        "is_ocr_text": True,
                        "extraction_method": "OCR"
                    }
                    
                    # Apply intelligent chunking with quality gates
                    intelligent_chunks = self.chunker.chunk_content(
                        content=full_text,
                        content_type=content_type,
                        metadata=base_metadata
                    )
                    
                    for i, chunk_data in enumerate(intelligent_chunks):
                        chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                        
                        # Combine metadata
                        combined_metadata = {**base_metadata, **chunk_data['metadata']}
                        combined_metadata.update({
                            "chunk_index": i,
                            "total_chunks": len(intelligent_chunks),
                            "quality_score": chunk_data.get('quality_score', 0.0),
                            "ocr_confidence": 0.8  # Default OCR confidence
                        })
                        
                        chunk = DocumentChunk(
                            content=chunk_data['content'].strip(),
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            doctype=doctype,
                            metadata=combined_metadata
                        )
                        chunks.append(chunk)
                        chunk_counter += 1
            
            if not chunks:
                raise ValueError(f"No text extracted from image: {doc_path.name}")
            
            print(f"✅ Processed image {doc_path.name}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            print(f"❌ Error processing image {doc_path}: {str(e)}")
            raise Exception(f"Image processing failed: {str(e)}")
    
    async def _process_tables(
        self, 
        document, 
        doc_id: str, 
        doctype: str
    ) -> List[DocumentChunk]:
        """Process tables as separate structured chunks"""
        table_chunks = []
        
        try:
            if hasattr(document, 'tables') and document.tables:
                for i, table in enumerate(document.tables):
                    # Convert table to text representation
                    table_text = self._table_to_text(table)
                    
                    if len(table_text.strip()) > 50:
                        chunk_id = f"{doc_id}_table_{i}"
                        chunk = DocumentChunk(
                            content=table_text,
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            doctype=doctype,
                            metadata={
                                "content_type": "table",
                                "table_index": i,
                                "table_rows": getattr(table, 'num_rows', 0),
                                "table_cols": getattr(table, 'num_cols', 0)
                            }
                        )
                        table_chunks.append(chunk)
        except Exception as e:
            print(f"Warning: Table processing failed: {str(e)}")
        
        return table_chunks
    
    def _table_to_text(self, table) -> str:
        """Convert table object to readable text - Enhanced for Docling tables"""
        try:
            # Handle Docling table format
            if hasattr(table, 'table_cells') and table.table_cells:
                # Docling tables have table_cells list with TableCell objects
                num_rows = getattr(table, 'num_rows', 0)
                num_cols = getattr(table, 'num_cols', 0)
                
                if num_rows == 0 or num_cols == 0:
                    # Fallback to string representation
                    return str(table)
                
                # Create 2D array to organize cells
                grid = [['' for _ in range(num_cols)] for _ in range(num_rows)]
                
                # Fill grid with cell text
                for cell in table.table_cells:
                    try:
                        # Extract cell position and text
                        row_idx = getattr(cell, 'start_row_offset_idx', None)
                        col_idx = getattr(cell, 'start_col_offset_idx', None)
                        cell_text = getattr(cell, 'text', '')
                        
                        if row_idx is not None and col_idx is not None:
                            if 0 <= row_idx < num_rows and 0 <= col_idx < num_cols:
                                grid[row_idx][col_idx] = str(cell_text).strip()
                    except Exception as e:
                        logger.debug(f"Error processing table cell: {str(e)}")
                        continue
                
                # Convert grid to readable text format
                table_lines = []
                
                # Add each row
                for row_idx, row in enumerate(grid):
                    # Clean up empty cells
                    cleaned_row = [cell if cell else '-' for cell in row]
                    row_text = " | ".join(cleaned_row)
                    table_lines.append(row_text)
                    
                    # Add separator after header row (first row)
                    if row_idx == 0 and len(table_lines) > 0:
                        separator = "-+-".join(['-' * max(10, len(cell)) for cell in cleaned_row])
                        table_lines.append(separator)
                
                # Join all lines
                result = "\n".join(table_lines)
                
                # Validate result is reasonable size
                if len(result) > 5000:
                    # Too large - create summary instead
                    logger.warning(f"Table too large ({len(result)} chars), creating summary")
                    summary_lines = []
                    summary_lines.append(f"[Large Table: {num_rows} rows x {num_cols} columns]")
                    
                    # Include first 3 rows as preview
                    for i in range(min(3, len(grid))):
                        row_text = " | ".join([str(cell)[:20] + ('...' if len(str(cell)) > 20 else '') for cell in grid[i]])
                        summary_lines.append(row_text)
                    
                    if num_rows > 3:
                        summary_lines.append(f"... and {num_rows - 3} more rows")
                    
                    return "\n".join(summary_lines)
                
                return result
            
            # Handle traditional table.data format (fallback)
            elif hasattr(table, 'data') and table.data:
                rows = []
                for row in table.data:
                    row_text = " | ".join(str(cell) for cell in row)
                    rows.append(row_text)
                return "\n".join(rows)
            
            else:
                # Last resort - string representation
                table_str = str(table)
                # But limit size
                if len(table_str) > 5000:
                    return table_str[:5000] + "\n[Table truncated...]"
                return table_str
                
        except Exception as e:
            logger.warning(f"Error converting table to text: {str(e)}")
            # Return truncated string representation
            table_str = str(table)
            if len(table_str) > 2000:
                return table_str[:2000] + "\n[Table data truncated due to conversion error]"
            return table_str
    
    def _parse_markdown_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse markdown content into sections by headers"""
        lines = content.split('\n')
        sections = []
        current_section = {"heading": None, "content": ""}
        
        for line in lines:
            if line.strip().startswith('#'):
                # Save previous section
                if current_section["content"].strip():
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    "heading": line.strip().lstrip('#').strip(),
                    "content": ""
                }
            else:
                current_section["content"] += line + '\n'
        
        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections if sections else [{"heading": None, "content": content}]
    
    def _extract_heading(self, document, item_index: int) -> Optional[str]:
        """Extract heading context for better chunk understanding"""
        try:
            # Look for heading-level items before current item
            for i in range(max(0, item_index - 5), item_index):
                if i < len(document.texts):
                    text_item = document.texts[i]
                    # Check if item looks like a heading (short, capitalized, etc.)
                    if (len(text_item.text) < 100 and 
                        text_item.text.isupper() or text_item.text.istitle()):
                        return text_item.text.strip()
            return None
        except:
            return None
    
    def _extract_section(self, document, item_index: int) -> Optional[str]:
        """Extract section context from document structure"""
        try:
            # Simple section extraction - could be enhanced with document structure analysis
            if hasattr(document, 'structure') and document.structure:
                # Use document structure if available
                pass
            return None
        except:
            return None
    
    def _is_low_quality_chunk(self, content: str, word_count: int, sentence_count: int) -> bool:
        """
        Assess if a chunk is of low quality and should be filtered out
        
        Args:
            content: The chunk content
            word_count: Number of words in the chunk
            sentence_count: Number of sentences in the chunk
            
        Returns:
            True if the chunk should be filtered out
        """
        try:
            # Basic quality checks
            if not content or not content.strip():
                return True
            
            # Check for mostly punctuation or numbers
            alpha_chars = sum(1 for c in content if c.isalpha())
            total_chars = len(content.replace(' ', ''))
            alpha_ratio = alpha_chars / max(total_chars, 1)
            
            if alpha_ratio < 0.5:  # Less than 50% alphabetic characters
                return True
            
            # Check for repetitive content (headers/footers)
            words = content.lower().split()
            unique_words = set(words)
            uniqueness_ratio = len(unique_words) / max(word_count, 1)
            
            if uniqueness_ratio < 0.3 and word_count > 10:  # Too repetitive
                return True
            
            # Check for common non-content patterns
            low_value_patterns = [
                'page', 'seite', 'datum', 'date', 'chapter', 'kapitel',
                'inhaltsverzeichnis', 'table of contents', 'www.', 'http',
                'copyright', '©', '®', 'all rights reserved'
            ]
            
            content_lower = content.lower()
            if any(pattern in content_lower for pattern in low_value_patterns) and word_count < 15:
                return True
            
            # Check sentence quality
            if sentence_count == 0 and word_count > 5:  # No sentences but many words (likely fragmented)
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error in quality assessment: {str(e)}")
            return False  # If assessment fails, don't filter
    
    async def reindex_all_documents(self) -> int:
        """Reprocess all documents in storage directory"""
        doc_count = 0
        
        try:
            for file_path in settings.DOC_STORE_PATH.glob("*"):
                if file_path.suffix.lower() in ['.pdf', '.docx', '.html']:
                    await self.process_document(str(file_path))
                    doc_count += 1
            
            print(f"✅ Reindexed {doc_count} documents")
            return doc_count
            
        except Exception as e:
            print(f"❌ Reindex failed: {str(e)}")
            raise Exception(f"Reindex operation failed: {str(e)}")