"""
LlamaIndex Ingestion Service

Document processing pipeline using LlamaIndex:
- File parsing with SimpleDirectoryReader
- Semantic chunking with SentenceSplitter
- Metadata extraction and enhancement
- Integration with MinIO file storage
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import tempfile
import re

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode, Document

from .index_service import get_index_service
from .settings import LlamaIndexSettings


class IngestionService:
    """
    Document Ingestion Service using LlamaIndex
    
    Features:
    - Multi-format parsing (PDF, DOCX, TXT, etc.)
    - Semantic chunking with sentence boundaries
    - Rich metadata extraction
    - MinIO file storage integration
    """
    
    def __init__(self):
        self._index_service = None
        self._file_storage = None
        self._node_parser = SentenceSplitter(
            chunk_size=LlamaIndexSettings.CHUNK_SIZE,
            chunk_overlap=LlamaIndexSettings.CHUNK_OVERLAP,
        )
    
    @property
    def index_service(self):
        """Lazy-loaded index service"""
        if self._index_service is None:
            self._index_service = get_index_service()
        return self._index_service
    
    @property
    def file_storage(self):
        """Lazy-loaded MinIO file storage (existing implementation)"""
        if self._file_storage is None:
            from services.rag.storage.file_storage import file_storage
            self._file_storage = file_storage
        return self._file_storage
    
    def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        save_original: bool = True,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a file into the vector store
        
        Args:
            file_content: Raw file bytes
            filename: Original filename with extension
            save_original: Whether to save to MinIO
            category: Document category for filtering
            metadata: Additional metadata to store
            
        Returns:
            Ingestion result with doc_id, chunks count, metadata
        """
        doc_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # Determine file type
        file_ext = Path(filename).suffix.lower()
        doc_type = self._get_doc_type(file_ext)
        
        # Save original file to MinIO
        if save_original:
            self.file_storage.save_file(file_content, filename, doc_id)
        
        # Parse document using LlamaIndex
        documents = self._parse_file(file_content, filename, file_ext)
        
        if not documents:
            raise ValueError(f"Failed to parse file: {filename}")
        
        # Extract intelligent metadata from filename
        version = self._extract_version(filename, documents[0].text if documents else "")
        year = self._extract_year(filename)
        auto_category = self._extract_category(filename)
        final_category = category or auto_category or "Allgemein"
        
        # Build base metadata
        base_metadata = {
            "doc_id": doc_id,
            "parent_doc_id": doc_id,
            "filename": filename,
            "doc_type": doc_type,
            "created_at": created_at,
            "has_original": save_original,
            "category": final_category,
            "version": version,
            "year": year,
            **(metadata or {}),
        }
        
        # Chunk documents into nodes
        nodes = self._create_nodes(documents, base_metadata)
        
        # Add nodes to index
        node_ids = self.index_service.add_nodes(nodes)
        
        return {
            "doc_id": doc_id,
            "filename": filename,
            "doc_type": doc_type,
            "chunks": len(nodes),
            "created_at": created_at,
            "has_original": save_original,
            "category": final_category,
            "metadata": {
                "version": version,
                "year": year,
                "word_count": sum(len(n.text.split()) for n in nodes),
            },
        }
    
    def ingest_text(
        self,
        text: str,
        title: str,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest plain text content
        
        Args:
            text: Text content to ingest
            title: Document title
            category: Document category
            metadata: Additional metadata
            
        Returns:
            Ingestion result
        """
        doc_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        base_metadata = {
            "doc_id": doc_id,
            "parent_doc_id": doc_id,
            "filename": title,
            "doc_type": "txt",
            "created_at": created_at,
            "has_original": False,
            "category": category or "Allgemein",
            "title": title,
            **(metadata or {}),
        }
        
        # Create document and parse
        document = Document(text=text, metadata=base_metadata)
        nodes = self._node_parser.get_nodes_from_documents([document])
        
        # Enhance node metadata
        for i, node in enumerate(nodes):
            node.metadata.update({
                "chunk_index": i,
                "total_chunks": len(nodes),
                "chunk_word_count": len(node.text.split()),
            })
        
        # Add to index
        self.index_service.add_nodes(nodes)
        
        return {
            "doc_id": doc_id,
            "filename": title,
            "doc_type": "txt",
            "chunks": len(nodes),
            "created_at": created_at,
        }
    
    def _parse_file(
        self,
        file_content: bytes,
        filename: str,
        file_ext: str,
    ) -> List[Document]:
        """Parse file content using LlamaIndex readers"""
        
        # Write to temp file for LlamaIndex to read
        with tempfile.NamedTemporaryFile(
            suffix=file_ext,
            delete=False,
        ) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Use SimpleDirectoryReader for robust parsing
            reader = SimpleDirectoryReader(
                input_files=[str(tmp_path)],
            )
            documents = reader.load_data()
            
            return documents
            
        except Exception as e:
            print(f"⚠️ LlamaIndex parsing failed for {filename}: {e}")
            # Fallback: try as plain text
            try:
                text = file_content.decode('utf-8', errors='ignore')
                return [Document(text=text, metadata={"filename": filename})]
            except Exception:
                return []
        finally:
            # Clean up temp file
            try:
                tmp_path.unlink()
            except Exception:
                pass
    
    def _create_nodes(
        self,
        documents: List[Document],
        base_metadata: Dict[str, Any],
    ) -> List[TextNode]:
        """Create TextNodes from documents with enhanced metadata"""
        
        # Parse documents into nodes
        nodes = self._node_parser.get_nodes_from_documents(documents)
        
        # Enhance each node with metadata
        for i, node in enumerate(nodes):
            node.metadata.update({
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(nodes),
                "chunk_word_count": len(node.text.split()),
            })
            
            # Preserve any extracted metadata from parser
            if hasattr(node, 'relationships'):
                # Keep source document reference
                pass
        
        return nodes
    
    def _get_doc_type(self, file_ext: str) -> str:
        """Map file extension to document type"""
        type_map = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".doc": "docx",
            ".txt": "txt",
            ".md": "markdown",
            ".xlsx": "excel",
            ".xls": "excel",
            ".csv": "csv",
            ".pptx": "powerpoint",
            ".ppt": "powerpoint",
            ".xml": "xml",
            ".json": "json",
            ".html": "html",
            ".htm": "html",
        }
        return type_map.get(file_ext, "unknown")
    
    def _extract_version(self, filename: str, content: str = "") -> str:
        """Extract version from filename or content"""
        # Try filename first
        version_match = re.search(
            r"(?:v|version)[_\-\s]?(\d+(?:[\.-]\d+)*)",
            filename,
            re.IGNORECASE,
        )
        if version_match:
            return version_match.group(1)
        
        # Fallback to content
        if content:
            content_match = re.search(
                r"Version[:\s]*(\d+(?:\.\d+)+)",
                content[:500],
                re.IGNORECASE,
            )
            if content_match:
                return content_match.group(1)
        
        return "unknown"
    
    def _extract_year(self, filename: str) -> Optional[int]:
        """Extract year from filename"""
        year_match = re.search(r"(202[0-9])", filename)
        return int(year_match.group(1)) if year_match else None
    
    def _extract_category(self, filename: str) -> Optional[str]:
        """Extract category from filename prefix (IT_, HR_, etc)"""
        category_match = re.match(r"^([A-Z]+)_", filename)
        return category_match.group(1) if category_match else None
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported file types"""
        return [
            "pdf", "docx", "doc", "txt", "md",
            "xlsx", "xls", "csv",
            "pptx", "ppt",
            "xml", "json", "html",
        ]


# Singleton instance
_ingestion_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    """Get singleton IngestionService instance"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
