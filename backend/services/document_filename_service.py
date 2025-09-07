"""
Enterprise Document Filename Service
Manages mapping between internal document IDs and user-friendly original filenames
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from config import settings

logger = logging.getLogger(__name__)

class DocumentFilenameService:
    """Service for managing document filename mappings for enterprise UX"""
    
    def __init__(self):
        self.documents_json_path = Path("/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/storage/documents.json")
        self.job_history_path = Path("./storage/job_history")
        self._filename_cache: Dict[str, str] = {}
        
    async def get_original_filename(self, doc_id: str) -> str:
        """Get the original user-friendly filename for a document ID"""
        
        # Check cache first
        if doc_id in self._filename_cache:
            return self._filename_cache[doc_id]
        
        logger.info(f"Resolving filename for doc_id: {doc_id}")
        
        # Clean doc_id - remove extension if it's a UUID with extension
        clean_doc_id = self._extract_uuid_from_filename(doc_id)
        if clean_doc_id != doc_id:
            logger.info(f"Extracted UUID {clean_doc_id} from filename {doc_id}")
        
        # Try documents.json first (folder-based uploads)
        original_filename = await self._get_from_documents_json(clean_doc_id)
        if original_filename:
            self._filename_cache[doc_id] = original_filename
            logger.info(f"Found filename in documents.json: {original_filename}")
            return original_filename
        
        # Try job history (upload system)
        original_filename = await self._get_from_job_history(clean_doc_id)
        if original_filename:
            self._filename_cache[doc_id] = original_filename
            logger.info(f"Found filename in job history: {original_filename}")
            return original_filename
        
        # Try vector store metadata
        original_filename = await self._get_from_vector_store(clean_doc_id)
        if original_filename:
            self._filename_cache[doc_id] = original_filename
            logger.info(f"Found filename in vector store: {original_filename}")
            return original_filename
        
        # Apply known mappings for legacy documents
        original_filename = self._apply_known_mappings(clean_doc_id)
        if original_filename:
            self._filename_cache[doc_id] = original_filename
            logger.info(f"Found filename in known mappings: {original_filename}")
            return original_filename
        
        # Fallback to cleaned filename
        fallback = self.clean_filename(doc_id)
        self._filename_cache[doc_id] = fallback
        logger.info(f"Using fallback filename: {fallback}")
        return fallback
    
    async def _get_from_documents_json(self, doc_id: str) -> Optional[str]:
        """Get filename from documents.json (folder-based system)"""
        try:
            if not self.documents_json_path.exists():
                return None
                
            with open(self.documents_json_path, 'r', encoding='utf-8') as f:
                documents_data = json.load(f)
            
            if doc_id in documents_data:
                document = documents_data[doc_id]
                return document.get('original_filename') or document.get('filename')
                
        except Exception as e:
            logger.warning(f"Failed to read documents.json: {str(e)}")
        
        return None
    
    async def _get_from_job_history(self, doc_id: str) -> Optional[str]:
        """Get filename from job history (upload tracking system)"""
        try:
            if not self.job_history_path.exists():
                return None
                
            for job_file in self.job_history_path.glob("*.json"):
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                    
                    if job_data.get('document_id') == doc_id:
                        return job_data.get('filename')
                        
                except Exception as e:
                    logger.warning(f"Failed to read job history {job_file}: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"Failed to access job history: {str(e)}")
        
        return None
    
    async def _get_from_vector_store(self, doc_id: str) -> Optional[str]:
        """Get filename from vector store metadata"""
        try:
            from services.vectorstore import VectorStoreService
            
            vector_store = VectorStoreService()
            await vector_store.initialize()
            
            # Get document metadata from ChromaDB
            results = vector_store.collection.get(
                where={"doc_id": doc_id},
                include=['metadatas'],
                limit=1
            )
            
            if results['metadatas'] and len(results['metadatas']) > 0:
                metadata = results['metadatas'][0]
                return metadata.get('original_filename') or metadata.get('filename')
                
        except Exception as e:
            logger.warning(f"Failed to get filename from vector store: {str(e)}")
        
        return None
    
    def _apply_known_mappings(self, doc_id: str) -> Optional[str]:
        """Apply known document ID to filename mappings for legacy documents"""
        
        # Known mappings for existing documents (legacy support)
        known_mappings = {
            'v1': 'GMX Premium.pdf',
            'streamworks-doc-1': 'StreamWorks Benutzerhandbuch.pdf',
            'rental-termination': 'Kuendigung-Mietvertrag.pdf',
            # Legacy document mappings - extend as needed
            'doc-1': 'Erste Dokumentation.pdf',
            'test-doc': 'Test Dokument.pdf',
            'manual-1': 'Benutzerhandbuch Version 1.pdf'
        }
        
        return known_mappings.get(doc_id)
    
    async def get_bulk_filenames(self, doc_ids: List[str]) -> Dict[str, str]:
        """Get original filenames for multiple document IDs efficiently"""
        filename_map = {}
        
        # Check cache first for all doc_ids
        uncached_ids = []
        for doc_id in doc_ids:
            if doc_id in self._filename_cache:
                filename_map[doc_id] = self._filename_cache[doc_id]
            else:
                uncached_ids.append(doc_id)
        
        if not uncached_ids:
            return filename_map  # All were cached
        
        # Bulk load from documents.json if it exists
        try:
            if self.documents_json_path.exists():
                with open(self.documents_json_path, 'r', encoding='utf-8') as f:
                    documents_data = json.load(f)
                
                for doc_id in uncached_ids[:]:
                    clean_id = self._extract_uuid_from_filename(doc_id)
                    if clean_id in documents_data:
                        document = documents_data[clean_id]
                        original_filename = document.get('original_filename') or document.get('filename')
                        if original_filename:
                            filename_map[doc_id] = original_filename
                            self._filename_cache[doc_id] = original_filename
                            uncached_ids.remove(doc_id)
        except Exception as e:
            logger.warning(f"Failed to bulk load from documents.json: {str(e)}")
        
        # For remaining uncached IDs, resolve individually
        for doc_id in uncached_ids:
            filename_map[doc_id] = await self.get_original_filename(doc_id)
        
        return filename_map
    
    async def update_filename_mapping(self, doc_id: str, original_filename: str):
        """Update the filename mapping in cache and persistent storage"""
        self._filename_cache[doc_id] = original_filename
        logger.info(f"Updated filename mapping: {doc_id} -> {original_filename}")
        
        # Optionally persist to a dedicated mapping file
        # This could be implemented if needed for performance
        pass
    
    def clear_cache(self):
        """Clear the filename cache - useful for testing or memory management"""
        self._filename_cache.clear()
        logger.info("Filename cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the filename cache"""
        return {
            "cached_entries": len(self._filename_cache),
            "cache_size_kb": len(str(self._filename_cache)) / 1024,
            "entries": list(self._filename_cache.keys()) if len(self._filename_cache) < 50 else list(self._filename_cache.keys())[:50] + ["..."]
        }
    
    def _extract_uuid_from_filename(self, filename: str) -> str:
        """Extract UUID from filename if it contains one, otherwise return as-is"""
        import re
        
        # UUID pattern (with possible extension)
        uuid_pattern = r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})(\.\w+)?'
        match = re.match(uuid_pattern, filename.lower())
        
        if match:
            return match.group(1)  # Return just the UUID part
        
        return filename  # Return as-is if not a UUID pattern
    
    def clean_filename(self, filename: str) -> str:
        """Clean and format filename for enterprise display"""
        if not filename:
            return "Unbenanntes Dokument"
        
        # Remove UUID patterns if they exist
        import re
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}(\.[\w]+)?$'
        
        if re.match(uuid_pattern, filename.lower()):
            # Extract extension if present
            extension_match = re.search(r'\.(\w+)$', filename.lower())
            if extension_match:
                extension = extension_match.group(1)
                return f"Dokument.{extension}"
            else:
                return "Dokument.pdf"
        
        # Clean up common issues
        cleaned = filename.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words appropriately
        parts = cleaned.split('.')
        if len(parts) > 1:
            name_part = ' '.join(word.capitalize() for word in parts[0].split())
            extension = parts[-1].lower()
            return f"{name_part}.{extension}"
        else:
            return ' '.join(word.capitalize() for word in cleaned.split())

# Global service instance
document_filename_service = DocumentFilenameService()