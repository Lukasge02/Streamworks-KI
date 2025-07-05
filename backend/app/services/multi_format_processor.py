"""
Multi-Format Document Processor for StreamWorks-KI RAG System
Supports 20+ file formats with specialized chunking strategies
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
import csv
from io import StringIO
import xml.etree.ElementTree as ET

# Langchain Document Loaders
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, JSONLoader, 
    PyPDFLoader, UnstructuredHTMLLoader, UnstructuredXMLLoader
)
from langchain.schema import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    PythonCodeTextSplitter,
    MarkdownHeaderTextSplitter
)

logger = logging.getLogger(__name__)

class SupportedFormat(Enum):
    """Alle unterstützten Dateiformate"""
    
    # Text & Dokumentation
    TXT = "txt"
    MD = "md"
    RTF = "rtf"
    LOG = "log"
    
    # Office-Dokumente
    DOCX = "docx"
    DOC = "doc"
    PDF = "pdf"
    ODT = "odt"
    
    # Strukturierte Daten
    CSV = "csv"
    TSV = "tsv"
    XLSX = "xlsx"
    XLS = "xls"
    JSON = "json"
    JSONL = "jsonl"
    YAML = "yaml"
    YML = "yml"
    TOML = "toml"
    
    # XML-Familie
    XML = "xml"
    XSD = "xsd"
    XSL = "xsl"
    SVG = "svg"
    RSS = "rss"
    ATOM = "atom"
    
    # Code & Scripts
    PY = "py"
    JS = "js"
    TS = "ts"
    JAVA = "java"
    SQL = "sql"
    PS1 = "ps1"
    BAT = "bat"
    SH = "sh"
    BASH = "bash"
    
    # Web & Markup
    HTML = "html"
    HTM = "htm"
    
    # Konfiguration
    INI = "ini"
    CFG = "cfg"
    CONF = "conf"
    
    # E-Mail
    MSG = "msg"
    EML = "eml"

class DocumentCategory(Enum):
    """Kategorien für verschiedene Dokumenttypen"""
    HELP_DOCUMENTATION = "help_docs"
    XML_CONFIGURATION = "xml_config"
    SCHEMA_DEFINITION = "schema_def"
    QA_FAQ = "qa_faq"
    CODE_SCRIPT = "code_script"
    OFFICE_DOCUMENT = "office_doc"
    STRUCTURED_DATA = "structured_data"
    CONFIGURATION = "configuration"
    API_DOCUMENTATION = "api_docs"
    EMAIL_COMMUNICATION = "email_comm"
    WEB_CONTENT = "web_content"
    LOG_FILE = "log_file"

@dataclass
class FileProcessingResult:
    """Ergebnis der Dateiverarbeitung"""
    success: bool
    documents: List[Document]
    file_format: SupportedFormat
    category: DocumentCategory
    processing_method: str
    chunk_count: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class FormatDetector:
    """Erweiterte Dateiformaterkennung"""
    
    def __init__(self):
        self.format_signatures = {
            # Office-Dokumente
            SupportedFormat.PDF: {
                'extensions': ['.pdf'],
                'magic_bytes': [b'%PDF'],
                'content_patterns': []
            },
            SupportedFormat.DOCX: {
                'extensions': ['.docx'],
                'magic_bytes': [b'PK\x03\x04'],  # ZIP-based
                'content_patterns': []
            },
            
            # Strukturierte Daten
            SupportedFormat.JSON: {
                'extensions': ['.json'],
                'magic_bytes': [],
                'content_patterns': [r'^\s*[\{\[]', r'"\w+":\s*["\d\{\[]']
            },
            SupportedFormat.YAML: {
                'extensions': ['.yaml', '.yml'],
                'magic_bytes': [],
                'content_patterns': [r'^\w+:\s*\w+', r'---\s*\n', r'^\s*-\s+\w+']
            },
            
            # XML-Familie
            SupportedFormat.XML: {
                'extensions': ['.xml'],
                'magic_bytes': [],
                'content_patterns': [r'<\?xml', r'<\w+[^>]*>', r'xmlns=']
            },
            SupportedFormat.XSD: {
                'extensions': ['.xsd'],
                'magic_bytes': [],
                'content_patterns': [r'xs:', r'schema', r'complexType', r'simpleType']
            },
            
            # Code & Scripts
            SupportedFormat.PY: {
                'extensions': ['.py'],
                'magic_bytes': [],
                'content_patterns': [r'import\s+\w+', r'def\s+\w+', r'class\s+\w+', r'#!/usr/bin/python']
            },
            SupportedFormat.SQL: {
                'extensions': ['.sql'],
                'magic_bytes': [],
                'content_patterns': [r'SELECT\s+', r'CREATE\s+', r'INSERT\s+', r'UPDATE\s+']
            },
            SupportedFormat.PS1: {
                'extensions': ['.ps1'],
                'magic_bytes': [],
                'content_patterns': [r'param\s*\(', r'\$\w+', r'Get-\w+', r'Set-\w+']
            },
            
            # Web & Markup
            SupportedFormat.HTML: {
                'extensions': ['.html', '.htm'],
                'magic_bytes': [],
                'content_patterns': [r'<html', r'<head>', r'<body>', r'<!DOCTYPE']
            }
        }
    
    def detect_format(self, file_path: str, content_sample: bytes = None) -> SupportedFormat:
        """Erkennt Dateiformat basierend auf Extension und Inhalt"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Direkte Extension-Zuordnung
        for format_type, signature in self.format_signatures.items():
            if extension in signature['extensions']:
                return format_type
        
        # Content-basierte Erkennung falls Extension nicht eindeutig
        if content_sample:
            content_str = content_sample.decode('utf-8', errors='ignore')[:1000]
            
            for format_type, signature in self.format_signatures.items():
                # Magic Bytes Check
                for magic in signature['magic_bytes']:
                    if content_sample.startswith(magic):
                        return format_type
                
                # Content Pattern Check
                for pattern in signature['content_patterns']:
                    if re.search(pattern, content_str, re.IGNORECASE | re.MULTILINE):
                        return format_type
        
        # Fallback: TXT
        return SupportedFormat.TXT
    
    def categorize_document(self, file_format: SupportedFormat, filename: str) -> DocumentCategory:
        """Kategorisiert Dokument basierend auf Format und Dateiname"""
        filename_lower = filename.lower()
        
        # Office Dokumente
        if file_format in [SupportedFormat.PDF, SupportedFormat.DOCX, SupportedFormat.DOC]:
            return DocumentCategory.OFFICE_DOCUMENT
        
        # Code & Scripts
        if file_format in [SupportedFormat.PY, SupportedFormat.JS, SupportedFormat.SQL, 
                          SupportedFormat.PS1, SupportedFormat.BAT, SupportedFormat.SH]:
            return DocumentCategory.CODE_SCRIPT
        
        # XML Konfigurationen
        if file_format == SupportedFormat.XML:
            if any(keyword in filename_lower for keyword in ['config', 'settings', 'template']):
                return DocumentCategory.XML_CONFIGURATION
            return DocumentCategory.SCHEMA_DEFINITION
        
        # Schema Definitionen
        if file_format in [SupportedFormat.XSD, SupportedFormat.XSL]:
            return DocumentCategory.SCHEMA_DEFINITION
        
        # Hilfe-Dokumentation
        if any(keyword in filename_lower for keyword in ['help', 'doc', 'guide', 'manual', 'readme']):
            return DocumentCategory.HELP_DOCUMENTATION
        
        # FAQ/Q&A
        if any(keyword in filename_lower for keyword in ['faq', 'qa', 'question', 'answer']):
            return DocumentCategory.QA_FAQ
        
        # API Dokumentation
        if any(keyword in filename_lower for keyword in ['api', 'endpoint', 'swagger', 'openapi']):
            return DocumentCategory.API_DOCUMENTATION
        
        # Strukturierte Daten
        if file_format in [SupportedFormat.CSV, SupportedFormat.JSON, SupportedFormat.YAML, 
                          SupportedFormat.XLSX, SupportedFormat.TSV]:
            return DocumentCategory.STRUCTURED_DATA
        
        # Konfigurationsdateien
        if file_format in [SupportedFormat.INI, SupportedFormat.CFG, SupportedFormat.CONF, 
                          SupportedFormat.TOML]:
            return DocumentCategory.CONFIGURATION
        
        # Log-Dateien
        if file_format == SupportedFormat.LOG or 'log' in filename_lower:
            return DocumentCategory.LOG_FILE
        
        # Web Content
        if file_format in [SupportedFormat.HTML, SupportedFormat.HTM]:
            return DocumentCategory.WEB_CONTENT
        
        # E-Mail
        if file_format in [SupportedFormat.MSG, SupportedFormat.EML]:
            return DocumentCategory.EMAIL_COMMUNICATION
        
        # Default: Hilfe-Dokumentation
        return DocumentCategory.HELP_DOCUMENTATION

class SmartChunker:
    """Intelligente Chunking-Strategien für verschiedene Dateiformate"""
    
    def __init__(self):
        self.default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.code_splitter = PythonCodeTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )
    
    def chunk_document(self, document: Document, file_format: SupportedFormat) -> List[Document]:
        """Angepasstes Chunking basierend auf Dateiformat"""
        
        # Code-Dateien: Funktions-/Klassen-basiertes Chunking
        if file_format in [SupportedFormat.PY, SupportedFormat.JS, SupportedFormat.TS, 
                          SupportedFormat.JAVA, SupportedFormat.SQL]:
            return self._chunk_code_document(document, file_format)
        
        # Markdown: Header-basiertes Chunking
        elif file_format == SupportedFormat.MD:
            return self._chunk_markdown_document(document)
        
        # XML: Element-basiertes Chunking
        elif file_format in [SupportedFormat.XML, SupportedFormat.XSD, SupportedFormat.XSL]:
            return self._chunk_xml_document(document)
        
        # JSON: Struktur-basiertes Chunking
        elif file_format in [SupportedFormat.JSON, SupportedFormat.JSONL]:
            return self._chunk_json_document(document)
        
        # CSV: Row-basiertes Chunking
        elif file_format in [SupportedFormat.CSV, SupportedFormat.TSV]:
            return self._chunk_csv_document(document)
        
        # HTML: Tag-basiertes Chunking
        elif file_format in [SupportedFormat.HTML, SupportedFormat.HTM]:
            return self._chunk_html_document(document)
        
        # Standard Text-Chunking
        else:
            return self.default_splitter.split_documents([document])
    
    def _chunk_code_document(self, document: Document, file_format: SupportedFormat) -> List[Document]:
        """Code-spezifisches Chunking"""
        try:
            if file_format == SupportedFormat.PY:
                return self.code_splitter.split_documents([document])
            else:
                # Für andere Code-Formate: Funktions-/Klassen-Grenzen finden
                return self._chunk_by_functions(document, file_format)
        except Exception as e:
            logger.warning(f"Code chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])
    
    def _chunk_by_functions(self, document: Document, file_format: SupportedFormat) -> List[Document]:
        """Chunking basierend auf Funktions-/Klassengrenzen"""
        content = document.page_content
        
        # Verschiedene Patterns für verschiedene Sprachen
        patterns = {
            SupportedFormat.JS: [r'^function\s+\w+', r'^class\s+\w+', r'^\w+\s*=\s*function'],
            SupportedFormat.SQL: [r'^CREATE\s+', r'^SELECT\s+', r'^INSERT\s+', r'^UPDATE\s+', r'^DELETE\s+'],
            SupportedFormat.PS1: [r'^function\s+\w+', r'^\w+-\w+'],
            SupportedFormat.JAVA: [r'^(public|private|protected)?\s*(static\s+)?class\s+\w+', 
                                  r'^(public|private|protected)\s+.*\s+\w+\s*\(']
        }
        
        if file_format not in patterns:
            return self.default_splitter.split_documents([document])
        
        # Split an Funktionsgrenzen
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            current_chunk.append(line)
            
            # Check if line starts new function/class
            for pattern in patterns[file_format]:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    if len(current_chunk) > 1:  # Save previous chunk
                        chunk_content = '\n'.join(current_chunk[:-1])
                        if chunk_content.strip():
                            chunks.append(Document(
                                page_content=chunk_content,
                                metadata={**document.metadata, 'chunk_type': 'function_block'}
                            ))
                    current_chunk = [line]  # Start new chunk
                    break
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if chunk_content.strip():
                chunks.append(Document(
                    page_content=chunk_content,
                    metadata={**document.metadata, 'chunk_type': 'function_block'}
                ))
        
        return chunks if chunks else self.default_splitter.split_documents([document])
    
    def _chunk_markdown_document(self, document: Document) -> List[Document]:
        """Markdown Header-basiertes Chunking"""
        try:
            chunks = self.markdown_splitter.split_text(document.page_content)
            
            # Convert to Documents
            docs = []
            for chunk in chunks:
                docs.append(Document(
                    page_content=chunk,
                    metadata={**document.metadata, 'chunk_type': 'markdown_section'}
                ))
            
            return docs if docs else self.default_splitter.split_documents([document])
        except Exception as e:
            logger.warning(f"Markdown chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])
    
    def _chunk_xml_document(self, document: Document) -> List[Document]:
        """XML Element-basiertes Chunking"""
        try:
            content = document.page_content
            
            # Parse XML
            root = ET.fromstring(content)
            chunks = []
            
            # Chunk by top-level elements
            for element in root:
                element_str = ET.tostring(element, encoding='unicode')
                if len(element_str) > 100:  # Skip very small elements
                    chunks.append(Document(
                        page_content=element_str,
                        metadata={
                            **document.metadata, 
                            'chunk_type': 'xml_element',
                            'element_tag': element.tag
                        }
                    ))
            
            return chunks if chunks else self.default_splitter.split_documents([document])
            
        except Exception as e:
            logger.warning(f"XML chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])
    
    def _chunk_json_document(self, document: Document) -> List[Document]:
        """JSON Struktur-basiertes Chunking"""
        try:
            content = document.page_content
            data = json.loads(content)
            chunks = []
            
            # Für Arrays: Jedes Element als Chunk
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, (dict, list)) and len(str(item)) > 50:
                        chunks.append(Document(
                            page_content=json.dumps(item, indent=2),
                            metadata={
                                **document.metadata, 
                                'chunk_type': 'json_array_item',
                                'item_index': i
                            }
                        ))
            
            # Für Objekte: Top-level Schlüssel als Chunks
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)) and len(str(value)) > 50:
                        chunks.append(Document(
                            page_content=json.dumps({key: value}, indent=2),
                            metadata={
                                **document.metadata, 
                                'chunk_type': 'json_object_key',
                                'object_key': key
                            }
                        ))
            
            return chunks if chunks else self.default_splitter.split_documents([document])
            
        except Exception as e:
            logger.warning(f"JSON chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])
    
    def _chunk_csv_document(self, document: Document) -> List[Document]:
        """CSV Row-basiertes Chunking"""
        try:
            content = document.page_content
            lines = content.strip().split('\n')
            
            if len(lines) < 2:
                return self.default_splitter.split_documents([document])
            
            header = lines[0]
            chunks = []
            chunk_size = 50  # Rows per chunk
            
            for i in range(1, len(lines), chunk_size):
                chunk_lines = [header] + lines[i:i + chunk_size]
                chunk_content = '\n'.join(chunk_lines)
                
                chunks.append(Document(
                    page_content=chunk_content,
                    metadata={
                        **document.metadata, 
                        'chunk_type': 'csv_rows',
                        'start_row': i,
                        'end_row': min(i + chunk_size - 1, len(lines) - 1)
                    }
                ))
            
            return chunks if chunks else self.default_splitter.split_documents([document])
            
        except Exception as e:
            logger.warning(f"CSV chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])
    
    def _chunk_html_document(self, document: Document) -> List[Document]:
        """HTML Tag-basiertes Chunking"""
        try:
            content = document.page_content
            
            # Simple HTML chunking by sections
            sections = re.split(r'</?(?:div|section|article|main|header|footer)[^>]*>', content)
            chunks = []
            
            for section in sections:
                section = section.strip()
                if len(section) > 100:  # Skip very small sections
                    chunks.append(Document(
                        page_content=section,
                        metadata={**document.metadata, 'chunk_type': 'html_section'}
                    ))
            
            return chunks if chunks else self.default_splitter.split_documents([document])
            
        except Exception as e:
            logger.warning(f"HTML chunking failed, using default: {e}")
            return self.default_splitter.split_documents([document])

class MultiFormatProcessor:
    """Hauptklasse für Multi-Format Dokumentenverarbeitung"""
    
    def __init__(self):
        self.format_detector = FormatDetector()
        self.chunker = SmartChunker()
        
        # Statistiken
        self.processing_stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'formats_processed': {},
            'categories_processed': {}
        }
        
        logger.info("🚀 Multi-Format Processor initialisiert")
    
    async def process_file(self, file_path: str, content: bytes = None) -> FileProcessingResult:
        """Verarbeitet eine Datei und gibt strukturierte Dokumente zurück"""
        
        try:
            self.processing_stats['total_files'] += 1
            
            # Content laden falls nicht übergeben
            if content is None:
                with open(file_path, 'rb') as f:
                    content = f.read()
            
            # Format erkennen
            file_format = self.format_detector.detect_format(file_path, content[:1000])
            
            # Kategorie bestimmen
            filename = Path(file_path).name
            category = self.format_detector.categorize_document(file_format, filename)
            
            # Dokument laden mit passendem Loader
            document = await self._load_document(file_path, content, file_format)
            
            if not document:
                raise ValueError(f"Could not load document for format {file_format}")
            
            # Intelligentes Chunking
            chunks = self.chunker.chunk_document(document, file_format)
            
            # Metadaten erweitern
            for chunk in chunks:
                chunk.metadata.update({
                    'file_format': file_format.value,
                    'document_category': category.value,
                    'processing_method': 'multi_format_processor',
                    'original_filename': filename,
                    'file_size': len(content),
                    'chunk_strategy': self._get_chunk_strategy(file_format)
                })
            
            # Statistiken aktualisieren
            self.processing_stats['successful_files'] += 1
            self.processing_stats['formats_processed'][file_format.value] = \
                self.processing_stats['formats_processed'].get(file_format.value, 0) + 1
            self.processing_stats['categories_processed'][category.value] = \
                self.processing_stats['categories_processed'].get(category.value, 0) + 1
            
            logger.info(f"✅ File processed: {filename} ({file_format.value}, {len(chunks)} chunks)")
            
            return FileProcessingResult(
                success=True,
                documents=chunks,
                file_format=file_format,
                category=category,
                processing_method=self._get_chunk_strategy(file_format),
                chunk_count=len(chunks),
                metadata={
                    'original_size': len(content),
                    'chunk_sizes': [len(chunk.page_content) for chunk in chunks]
                }
            )
            
        except Exception as e:
            self.processing_stats['failed_files'] += 1
            logger.error(f"❌ Failed to process file {file_path}: {e}")
            
            return FileProcessingResult(
                success=False,
                documents=[],
                file_format=SupportedFormat.TXT,  # Default
                category=DocumentCategory.HELP_DOCUMENTATION,  # Default
                processing_method="error",
                chunk_count=0,
                error_message=str(e)
            )
    
    async def _load_document(self, file_path: str, content: bytes, file_format: SupportedFormat) -> Optional[Document]:
        """Lädt Dokument mit passendem Langchain Loader"""
        
        try:
            # Text-basierte Formate
            if file_format in [SupportedFormat.TXT, SupportedFormat.MD, SupportedFormat.LOG, 
                              SupportedFormat.RTF, SupportedFormat.INI, SupportedFormat.CFG]:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # Code-Dateien
            elif file_format in [SupportedFormat.PY, SupportedFormat.JS, SupportedFormat.TS, 
                               SupportedFormat.SQL, SupportedFormat.PS1, SupportedFormat.BAT,
                               SupportedFormat.SH, SupportedFormat.JAVA]:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # CSV
            elif file_format in [SupportedFormat.CSV, SupportedFormat.TSV]:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # JSON
            elif file_format in [SupportedFormat.JSON, SupportedFormat.JSONL]:
                content_str = content.decode('utf-8', errors='ignore')
                # Validate JSON
                json.loads(content_str)
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # YAML
            elif file_format in [SupportedFormat.YAML, SupportedFormat.YML]:
                content_str = content.decode('utf-8', errors='ignore')
                # Validate YAML
                yaml.safe_load(content_str)
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # XML
            elif file_format in [SupportedFormat.XML, SupportedFormat.XSD, SupportedFormat.XSL]:
                content_str = content.decode('utf-8', errors='ignore')
                # Validate XML
                ET.fromstring(content_str)
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # HTML
            elif file_format in [SupportedFormat.HTML, SupportedFormat.HTM]:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # PDF (würde PyPDFLoader benötigen, für jetzt Text fallback)
            elif file_format == SupportedFormat.PDF:
                # Für jetzt als Text behandeln
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            
            # Default: Als Text behandeln
            else:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
                
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            # Fallback: Als Plain Text
            try:
                content_str = content.decode('utf-8', errors='ignore')
                return Document(page_content=content_str, metadata={'source': file_path})
            except:
                return None
    
    def _get_chunk_strategy(self, file_format: SupportedFormat) -> str:
        """Gibt die verwendete Chunking-Strategie zurück"""
        strategy_map = {
            SupportedFormat.PY: "function_based",
            SupportedFormat.JS: "function_based", 
            SupportedFormat.SQL: "statement_based",
            SupportedFormat.MD: "header_based",
            SupportedFormat.XML: "element_based",
            SupportedFormat.JSON: "structure_based",
            SupportedFormat.CSV: "row_based",
            SupportedFormat.HTML: "section_based"
        }
        return strategy_map.get(file_format, "default_recursive")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Gibt Verarbeitungsstatistiken zurück"""
        success_rate = (self.processing_stats['successful_files'] / 
                       self.processing_stats['total_files'] * 100) if self.processing_stats['total_files'] > 0 else 0
        
        return {
            **self.processing_stats,
            'success_rate_percent': round(success_rate, 2)
        }
    
    def get_supported_formats(self) -> List[str]:
        """Gibt Liste aller unterstützten Formate zurück"""
        return [format_enum.value for format_enum in SupportedFormat]
    
    def get_supported_categories(self) -> List[str]:
        """Gibt Liste aller Dokumentkategorien zurück"""
        return [category.value for category in DocumentCategory]

# Global instance
multi_format_processor = MultiFormatProcessor()