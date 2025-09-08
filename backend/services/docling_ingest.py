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

# LangChain for intelligent chunking
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    Language
)
from langchain.text_splitter import TextSplitter

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
        self.text_splitter = None
        self.markdown_splitter = None
        self.pdf_text_splitter = None  # PDF-specific splitter
        self.code_splitter = None  # Code-specific splitter
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
            
            # Initialize LangChain text splitters for intelligent chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.TEXT_CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            # PDF-specific splitter with larger chunks for better context
            self.pdf_text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.PDF_CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            self.markdown_splitter = MarkdownTextSplitter(
                chunk_size=settings.TEXT_CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            
            # Code-specific splitter
            try:
                from langchain.text_splitter import PythonCodeTextSplitter
                self.code_splitter = PythonCodeTextSplitter(
                    chunk_size=settings.TEXT_CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )
            except ImportError:
                # Fallback to regular text splitter if code splitter not available
                self.code_splitter = self.text_splitter
            
            self._initialized = True
            return True
            
        except Exception as e:
            self._initialization_error = e
            raise e
            
    def _get_appropriate_splitter(self, file_path: str, file_type: str = None) -> TextSplitter:
        """
        Get the most appropriate text splitter based on file type
        
        Args:
            file_path: Path to the file being processed
            file_type: Optional file type override
            
        Returns:
            Appropriate TextSplitter instance
        """
        try:
            if not self._initialized:
                self._initialize()
                
            file_extension = Path(file_path).suffix.lower() if file_path else ""
            
            # PDF files get larger chunks for better context retention
            if file_extension == '.pdf' or file_type == 'pdf':
                return self.pdf_text_splitter
                
            # Markdown files get specialized splitter
            if file_extension in ['.md', '.markdown'] or file_type == 'markdown':
                return self.markdown_splitter
                
            # Code files get specialized splitter
            if file_extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.xml', '.json'] or file_type == 'code':
                return self.code_splitter
                
            # Image/OCR files get smaller chunks for better quality
            if file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'] or file_type == 'image':
                return self.text_splitter  # Use standard text splitter with smaller chunks
                
            # Default to standard text splitter
            return self.text_splitter
            
        except Exception as e:
            logger.warning(f"Failed to get appropriate splitter, using default: {str(e)}")
            return self.text_splitter if self.text_splitter else None
    
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
                    
                    # Use appropriate text splitter for intelligent chunking
                    splitter = self._get_appropriate_splitter(file_path, 'pdf')
                    if not splitter:
                        raise ValueError("Text splitter not initialized properly")
                    content_chunks = splitter.split_text(text)
                    
                    for i, content in enumerate(content_chunks):
                        # Enhanced quality check for PDF chunks
                        stripped_content = content.strip()
                        word_count = len(stripped_content.split())
                        
                        # More reasonable filtering for combined text
                        if (len(stripped_content) < 10 or  # Allow shorter chunks from combined text
                            word_count < 1):  # Just need some actual words
                            logger.debug(f"Skipping tiny chunk: {len(stripped_content)} chars, {word_count} words")
                            continue
                            
                        chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                        
                        chunk = DocumentChunk(
                        content=content.strip(),
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        page_number=text_item['page'],
                        heading=text_item['heading'],
                        section=text_item['section'],
                        doctype=doctype,
                        metadata={
                            "source_file": doc_path.name,
                            "item_index": text_item['item_index'],
                            "chunk_index": i,
                            "total_chunks": len(content_chunks),
                            "is_combined": True
                        }
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
                # Use appropriate splitter based on file type
                splitter = self._get_appropriate_splitter(str(doc_path))
                if not splitter:
                    raise ValueError("Text splitter not initialized properly")
                content_chunks = splitter.split_text(section["content"])
                
                for i, chunk_content in enumerate(content_chunks):
                    # Quality check for text file chunks
                    stripped_content = chunk_content.strip()
                    word_count = len(stripped_content.split())
                    
                    if (len(stripped_content) < settings.MIN_CHUNK_SIZE or 
                        word_count < settings.MIN_WORD_COUNT):
                        continue
                    
                    chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                    
                    chunk = DocumentChunk(
                        content=chunk_content.strip(),
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        heading=section["heading"],
                        doctype=doctype,
                        metadata={
                            "source_file": doc_path.name,
                            "chunk_index": i,
                            "total_chunks": len(content_chunks),
                            "file_type": doc_path.suffix.lower()
                        }
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
                    # Use appropriate splitter for OCR text (smaller chunks for better quality)
                    splitter = self._get_appropriate_splitter(str(doc_path), 'image')  
                    if not splitter:
                        splitter = self.text_splitter  # Fallback
                    text_chunks = splitter.split_text(full_text)
                    
                    for i, chunk_content in enumerate(text_chunks):
                        # Quality check: minimum content requirements
                        stripped_content = chunk_content.strip()
                        word_count = len(stripped_content.split())
                        
                        if (len(stripped_content) < settings.MIN_CHUNK_SIZE or 
                            word_count < settings.MIN_WORD_COUNT):
                            continue
                        
                        chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                        chunk = DocumentChunk(
                            content=chunk_content.strip(),
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            doctype=doctype,
                            metadata={
                                "source_file": doc_path.name,
                                "file_type": "image",
                                "ocr_processed": True,
                                "chunk_index": i,
                                "total_chunks": len(text_chunks)
                            }
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
        """Convert table object to readable text"""
        try:
            # Basic table to text conversion
            if hasattr(table, 'data') and table.data:
                rows = []
                for row in table.data:
                    row_text = " | ".join(str(cell) for cell in row)
                    rows.append(row_text)
                return "\n".join(rows)
            else:
                return str(table)
        except:
            return str(table)
    
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