"""
Document Service v3
With original file storage and image OCR support
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from .parsers.registry import parser_registry
from .parsers.base_parser import ParsedDocument
from .storage.file_storage import file_storage


class DocumentService:
    """
    Enterprise Document Management Service v3
    
    Features:
    - Modular parser architecture (PDF, Word, PowerPoint, XML, Images, etc.)
    - Original file storage for viewing/download
    - Image OCR support via Docling
    - Intelligent chunking with overlap
    - Vector store integration
    """
    
    MAX_CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 200
    
    def __init__(self, vector_store=None):
        self._vector_store = vector_store
        self._parser_registry = parser_registry
        self._file_storage = file_storage
        self._upload_status: Dict[str, Dict[str, Any]] = {}
    
    @property
    def vector_store(self):
        if self._vector_store is None:
            from .vector_store import vector_store
            self._vector_store = vector_store
        return self._vector_store
    
    def get_upload_status(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an async upload task"""
        return self._upload_status.get(doc_id)
        
    def _update_status(self, doc_id: str, status: str, progress: int, error: str = None, result: Dict = None):
        """Update internal status dictionary"""
        self._upload_status[doc_id] = {
            "status": status,
            "progress": progress,
            "error": error,
            "result": result,
            "updated_at": datetime.utcnow().isoformat()
        }

    def get_supported_types(self) -> List[str]:
        """Get list of supported file extensions"""
        return self._parser_registry.list_supported_types()
    
    def can_process(self, filename: str) -> bool:
        """Check if file type is supported"""
        return self._parser_registry.can_parse(filename)
    
    def process_file(
        self,
        file_content: bytes,
        filename: str,
        chunk_size: int = None,
        save_original: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a file using appropriate parser and add to vector store
        
        Uses enterprise chunking with:
        - Semantic splitting (respects sentences/paragraphs)
        - Rich metadata (page numbers, positions, word counts)
        - Configurable overlap for context preservation
        
        Args:
            file_content: Raw file bytes
            filename: Original filename with extension
            chunk_size: Optional custom chunk size
            save_original: Whether to save original file (default: True)
            **kwargs: Additional parser options
            
        Returns:
            Document info with doc_id, chunks count, metadata
        """
        from .chunking import enterprise_chunker, ChunkingStrategy
        
        if not self.can_process(filename):
            supported = self.get_supported_types()
            raise ValueError(
                f"Unsupported file type: {filename}. "
                f"Supported: {', '.join(supported)}"
            )
        
        # Generate document ID first
        doc_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # Save original file
        file_info = None
        if save_original:
            file_info = self._file_storage.save_file(file_content, filename, doc_id)
        
        # Parse document using appropriate parser
        parsed_doc = self._parser_registry.parse(file_content, filename, **kwargs)
        
        # Use enterprise chunker
        if chunk_size:
            enterprise_chunker.max_chunk_size = chunk_size
        
        # For PDFs: Use page-based chunking if page_data is available
        # This ensures chunk order matches document order
        page_data = parsed_doc.metadata.get("page_data")
        if page_data and parsed_doc.doc_type.value == "pdf":
            chunks = enterprise_chunker.chunk(
                parsed_doc.content,
                strategy=ChunkingStrategy.PAGE_BASED,
                page_info=page_data
            )
        else:
            # For other documents: semantic chunking
            chunks = enterprise_chunker.chunk(
                parsed_doc.content,
                strategy=ChunkingStrategy.SEMANTIC
            )
        
        # Prepare base metadata (exclude page_data - too large for storage)
        filtered_metadata = {k: v for k, v in parsed_doc.metadata.items() 
                            if k not in ['page_data', 'source', 'parsing_engine']}
        base_metadata = {
            "filename": filename,
            "doc_type": parsed_doc.doc_type.value,
            "created_at": created_at,
            "title": parsed_doc.title,
            "page_count": parsed_doc.page_count,
            "word_count": parsed_doc.word_count,
            "parsing_method": parsed_doc.parsing_method,
            "has_original": save_original,
            "parent_doc_id": doc_id,
            **filtered_metadata
        }
        
        # Store in vector database with rich chunk metadata
        if len(chunks) == 1:
            self.vector_store.add_document(
                content=chunks[0].content,
                metadata={
                    **base_metadata,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "chunk_word_count": chunks[0].metadata.word_count,
                    "chunk_start_char": chunks[0].metadata.start_char,
                    "chunk_end_char": chunks[0].metadata.end_char,
                },
                doc_id=doc_id
            )
        else:
            documents = []
            for chunk in chunks:
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": chunk.metadata.chunk_index,
                    "total_chunks": chunk.metadata.total_chunks,
                    "chunk_word_count": chunk.metadata.word_count,
                    "chunk_sentence_count": chunk.metadata.sentence_count,
                    "chunk_start_char": chunk.metadata.start_char,
                    "chunk_end_char": chunk.metadata.end_char,
                    "chunk_page_numbers": chunk.metadata.page_numbers,
                    "chunk_section_title": chunk.metadata.section_title,
                }
                documents.append({
                    "content": chunk.content,
                    "metadata": chunk_metadata
                })
            self.vector_store.add_documents_batch(documents)
        
        return {
            "doc_id": doc_id,
            "filename": filename,
            "doc_type": parsed_doc.doc_type.value,
            "chunks": len(chunks),
            "created_at": created_at,
            "has_original": save_original,
            "metadata": {
                "title": parsed_doc.title,
                "page_count": parsed_doc.page_count,
                "word_count": parsed_doc.word_count,
                "tables": len(parsed_doc.tables),
                "parsing_method": parsed_doc.parsing_method,
                "chunking_strategy": "semantic",
                **{k: v for k, v in parsed_doc.metadata.items() 
                   if k not in ['source', 'parsing_engine']}
            }
        }

    def process_file_background(
        self,
        doc_id: str,
        file_content: bytes,
        filename: str,
        save_original: bool = True
    ):
        """Background task for processing files with status updates (enterprise chunking)"""
        from .chunking import enterprise_chunker, ChunkingStrategy
        
        try:
            self._update_status(doc_id, "starting", 0)
            
            # 1. Save Original
            self._update_status(doc_id, "saving", 10)
            if save_original:
                self._file_storage.save_file(file_content, filename, doc_id)
            
            # 2. Parse
            self._update_status(doc_id, "parsing", 30)
            parsed_doc = self._parser_registry.parse(file_content, filename)
            
            # 3. Chunk with enterprise chunker
            self._update_status(doc_id, "chunking", 60)
            
            # For PDFs: Use page-based chunking if page_data is available
            page_data = parsed_doc.metadata.get("page_data")
            if page_data and parsed_doc.doc_type.value == "pdf":
                chunks = enterprise_chunker.chunk(
                    parsed_doc.content,
                    strategy=ChunkingStrategy.PAGE_BASED,
                    page_info=page_data
                )
            else:
                chunks = enterprise_chunker.chunk(
                    parsed_doc.content,
                    strategy=ChunkingStrategy.SEMANTIC
                )
            
            # Prepare base metadata (exclude page_data - too large for storage)
            created_at = datetime.utcnow().isoformat()
            filtered_metadata = {k: v for k, v in parsed_doc.metadata.items() 
                                if k not in ['page_data', 'source', 'parsing_engine']}
            base_metadata = {
                "filename": filename,
                "doc_type": parsed_doc.doc_type.value,
                "created_at": created_at,
                "title": parsed_doc.title,
                "page_count": parsed_doc.page_count,
                "word_count": parsed_doc.word_count,
                "parsing_method": parsed_doc.parsing_method,
                "has_original": save_original,
                "parent_doc_id": doc_id,
                **filtered_metadata
            }
            
            # 4. Embed / Store with rich chunk metadata
            self._update_status(doc_id, "embedding", 80)
            if len(chunks) == 1:
                self.vector_store.add_document(
                    content=chunks[0].content,
                    metadata={
                        **base_metadata,
                        "chunk_index": 0,
                        "total_chunks": 1,
                        "chunk_word_count": chunks[0].metadata.word_count,
                        "chunk_start_char": chunks[0].metadata.start_char,
                        "chunk_end_char": chunks[0].metadata.end_char,
                    },
                    doc_id=doc_id
                )
            else:
                documents = []
                for chunk in chunks:
                    chunk_metadata = {
                        **base_metadata,
                        "chunk_index": chunk.metadata.chunk_index,
                        "total_chunks": chunk.metadata.total_chunks,
                        "chunk_word_count": chunk.metadata.word_count,
                        "chunk_sentence_count": chunk.metadata.sentence_count,
                        "chunk_start_char": chunk.metadata.start_char,
                        "chunk_end_char": chunk.metadata.end_char,
                        "chunk_page_numbers": chunk.metadata.page_numbers,
                        "chunk_section_title": chunk.metadata.section_title,
                    }
                    documents.append({
                        "content": chunk.content,
                        "metadata": chunk_metadata
                    })
                self.vector_store.add_documents_batch(documents)
            
            # Complete
            result_data = {
                "doc_id": doc_id,
                "filename": filename,
                "doc_type": parsed_doc.doc_type.value,
                "chunks": len(chunks),
                "created_at": created_at,
                "chunking_strategy": "semantic"
            }
            self._update_status(doc_id, "completed", 100, result=result_data)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._update_status(doc_id, "failed", 0, error=str(e))
    
    def process_text(
        self,
        text_content: str,
        filename: str,
        doc_type: str = "txt"
    ) -> Dict[str, Any]:
        """Process plain text content (legacy compatibility)"""
        return self.process_file(
            text_content.encode('utf-8'),
            filename if filename.endswith(f'.{doc_type}') else f"{filename}.{doc_type}",
            save_original=False
        )
    
    def _chunk_content(self, content: str, chunk_size: int) -> List[str]:
        """Split content into overlapping chunks"""
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            if end >= len(content):
                chunks.append(content[start:])
                break
            
            break_point = self._find_break_point(content, start, end)
            chunks.append(content[start:break_point])
            start = max(0, break_point - self.CHUNK_OVERLAP)
        
        return chunks
    
    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """Find natural break point"""
        search_start = start + (end - start) // 2
        
        for delimiter in ['\n\n', '\n', '. ', '! ', '? ', ' ']:
            pos = text.rfind(delimiter, search_start, end)
            if pos != -1:
                return pos + len(delimiter)
        
        return end
    
    # --- Original File Methods ---
    
    def get_original_file(self, doc_id: str) -> Optional[Dict[str, str]]:
        """Get original file as base64 for viewing"""
        return self._file_storage.get_file_base64(doc_id)
    
    def download_file(self, doc_id: str) -> Optional[tuple]:
        """Get original file bytes for download"""
        return self._file_storage.get_file(doc_id)
    
    # --- Query Methods ---
    
    def search(
        self,
        query: str,
        limit: int = 5,
        doc_type: Optional[str] = None,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Semantic search across documents"""
        results = self.vector_store.search(
            query, 
            limit=limit * 2,
            score_threshold=score_threshold
        )
        
        if doc_type:
            results = [r for r in results 
                      if r.get("metadata", {}).get("doc_type") == doc_type]
        
        return results[:limit]
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        return self.vector_store.get_document(doc_id)
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Enterprise cascade delete:
        1. Find the parent_doc_id (for chunks) or use doc_id (for single docs)
        2. Delete ALL chunks from Qdrant with matching parent_doc_id
        3. Delete original file from MinIO
        
        Returns deletion report with counts.
        """
        result = {
            "doc_id": doc_id,
            "chunks_deleted": 0,
            "file_deleted": False,
            "success": False
        }
        
        try:
            # First, get the document to find parent_doc_id
            document = self.vector_store.get_document(doc_id)
            
            # Determine the parent ID (where the file is stored)
            parent_id = doc_id
            if document:
                parent_id = document.get("metadata", {}).get("parent_doc_id") or doc_id
            
            # Delete all chunks from Qdrant (uses parent_doc_id matching)
            chunks_deleted = self.vector_store.delete_by_parent_id(parent_id)
            result["chunks_deleted"] = chunks_deleted
            
            # Delete original file from MinIO
            file_deleted = self._file_storage.delete_file(parent_id)
            result["file_deleted"] = file_deleted
            
            result["success"] = chunks_deleted > 0 or file_deleted
            result["parent_doc_id"] = parent_id
            
            print(f"✅ Cascade delete: {chunks_deleted} chunks, file={'deleted' if file_deleted else 'not found'}")
            
        except Exception as e:
            print(f"❌ Delete error: {e}")
            result["error"] = str(e)
        
        return result
    
    def sync_storage(self) -> Dict[str, Any]:
        """
        Synchronize MinIO and Qdrant storage:
        
        1. Get all doc_ids from MinIO files
        2. Get all parent_doc_ids from Qdrant
        3. Delete Qdrant entries without corresponding MinIO files
        4. Delete MinIO files without corresponding Qdrant entries
        
        Returns sync report.
        """
        report = {
            "orphaned_qdrant_entries": [],
            "orphaned_minio_files": [],
            "qdrant_cleaned": 0,
            "minio_cleaned": 0,
            "errors": []
        }
        
        try:
            # Get MinIO doc_ids (from filenames like "uuid.pdf")
            minio_files = self._file_storage.list_files()
            minio_doc_ids = set()
            for f in minio_files:
                filename = f["filename"]
                # Extract doc_id from filename (format: uuid.ext)
                doc_id = filename.rsplit('.', 1)[0] if '.' in filename else filename
                minio_doc_ids.add(doc_id)
            
            # Get Qdrant parent_doc_ids
            qdrant_parent_ids = set(self.vector_store.list_parent_doc_ids())
            
            # Find orphaned Qdrant entries (in Qdrant but not in MinIO)
            orphaned_qdrant = qdrant_parent_ids - minio_doc_ids
            report["orphaned_qdrant_entries"] = list(orphaned_qdrant)
            
            # Clean orphaned Qdrant entries
            for parent_id in orphaned_qdrant:
                try:
                    deleted = self.vector_store.delete_by_parent_id(parent_id)
                    report["qdrant_cleaned"] += deleted
                except Exception as e:
                    report["errors"].append(f"Failed to delete Qdrant entry {parent_id}: {e}")
            
            # Find orphaned MinIO files (in MinIO but not in Qdrant)
            orphaned_minio = minio_doc_ids - qdrant_parent_ids
            report["orphaned_minio_files"] = list(orphaned_minio)
            
            # Clean orphaned MinIO files
            for doc_id in orphaned_minio:
                try:
                    if self._file_storage.delete_file(doc_id):
                        report["minio_cleaned"] += 1
                except Exception as e:
                    report["errors"].append(f"Failed to delete MinIO file {doc_id}: {e}")
            
            report["minio_total"] = len(minio_doc_ids)
            report["qdrant_total"] = len(qdrant_parent_ids)
            # After cleanup, check if we're now in sync:
            # - No errors during cleanup
            # - All orphaned entries were cleaned (or there were none)
            cleanup_successful = len(report["errors"]) == 0
            all_cleaned = (report["qdrant_cleaned"] == len(orphaned_qdrant) and 
                          report["minio_cleaned"] == len(orphaned_minio))
            report["in_sync"] = cleanup_successful and all_cleaned
            
            print(f"✅ Sync complete: {report['qdrant_cleaned']} Qdrant entries, {report['minio_cleaned']} MinIO files cleaned")
            
        except Exception as e:
            report["errors"].append(str(e))
            print(f"❌ Sync error: {e}")
        
        return report
    
    def get_consistency_report(self) -> Dict[str, Any]:
        """
        Check consistency between MinIO and Qdrant WITHOUT making changes.
        
        Returns a report of any inconsistencies found.
        """
        report = {
            "minio_files": 0,
            "qdrant_documents": 0,
            "orphaned_qdrant_entries": [],
            "orphaned_minio_files": [],
            "all_consistent": True
        }
        
        try:
            # Get MinIO doc_ids
            minio_files = self._file_storage.list_files()
            minio_doc_ids = set()
            for f in minio_files:
                filename = f["filename"]
                doc_id = filename.rsplit('.', 1)[0] if '.' in filename else filename
                minio_doc_ids.add(doc_id)
            
            # Get Qdrant parent_doc_ids  
            qdrant_parent_ids = set(self.vector_store.list_parent_doc_ids())
            
            # Calculate orphans
            orphaned_qdrant = qdrant_parent_ids - minio_doc_ids
            orphaned_minio = minio_doc_ids - qdrant_parent_ids
            
            report["minio_files"] = len(minio_doc_ids)
            report["qdrant_documents"] = len(qdrant_parent_ids)
            report["orphaned_qdrant_entries"] = list(orphaned_qdrant)
            report["orphaned_minio_files"] = list(orphaned_minio)
            report["all_consistent"] = len(orphaned_qdrant) == 0 and len(orphaned_minio) == 0
            
        except Exception as e:
            report["error"] = str(e)
            report["all_consistent"] = False
        
        return report
    
    def list_documents(
        self,
        limit: int = 50,
        offset: int = 0,
        doc_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all documents with pagination"""
        docs = self.vector_store.list_documents(limit=limit, offset=offset)
        
        if doc_type:
            docs = [d for d in docs if d.get("doc_type") == doc_type]
        
        return docs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = self.vector_store.get_stats()
        stats["supported_types"] = self.get_supported_types()
        stats["stored_files"] = len(self._file_storage.list_files())
        return stats


# Singleton instance
document_service = DocumentService()
