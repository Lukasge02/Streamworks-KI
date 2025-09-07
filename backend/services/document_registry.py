"""
Zentrale Dokumentenverwaltung mit JSON-basierter Registry
Ersetzt viele einzelne Metadaten-Dateien durch eine zentrale documents.json
"""
import json
import threading
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import shutil
from config import settings

logger = logging.getLogger(__name__)

class DocumentRegistry:
    """Zentrale Registry für alle Dokumente - Thread-Safe JSON Storage"""
    
    def __init__(self):
        self.registry_file = settings.SYSTEM_PATH / "documents.json"
        self.lock = threading.Lock()
        self._ensure_registry_exists()
    
    def _ensure_registry_exists(self):
        """Stelle sicher dass die Registry-Datei existiert"""
        settings.SYSTEM_PATH.mkdir(parents=True, exist_ok=True)
        if not self.registry_file.exists():
            self._save_registry({"documents": [], "folders": [], "last_updated": datetime.now().isoformat()})
    
    def _load_registry(self) -> Dict[str, Any]:
        """Lade Registry aus JSON - Thread-Safe"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load registry: {e}, creating new one")
            return {"documents": [], "folders": [], "last_updated": datetime.now().isoformat()}
    
    def _save_registry(self, registry: Dict[str, Any]):
        """Speichere Registry zu JSON - Thread-Safe"""
        registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def scan_and_sync_filesystem(self) -> int:
        """Scanne Dateisystem und synchronisiere mit Registry"""
        with self.lock:
            registry = self._load_registry()
            
            # Get all existing document IDs
            existing_docs = {doc["id"]: doc for doc in registry["documents"]}
            
            # Scan filesystem (excluding .system directory)
            discovered_files = []
            try:
                for file_path in settings.DOCUMENTS_BASE_PATH.rglob("*"):
                    # Skip .system directory and its contents
                    if file_path.is_file() and not any(part.startswith('.system') for part in file_path.parts):
                        try:
                            relative_path = file_path.relative_to(settings.DOCUMENTS_BASE_PATH)
                            discovered_files.append({
                                'path': file_path,
                                'relative_path': relative_path,
                                'stats': file_path.stat()
                            })
                        except (OSError, ValueError) as e:
                            logger.warning(f"Skipped file {file_path}: {e}")
                            continue
            except Exception as e:
                logger.error(f"Filesystem scan failed: {e}")
                return 0
            
            # Add new files to registry
            added_count = 0
            for file_info in discovered_files:
                # Check if file already exists in registry
                file_exists = any(
                    doc.get("file_path") == str(file_info["relative_path"]) 
                    for doc in registry["documents"]
                )
                
                if not file_exists:
                    # Create new document entry
                    doc_metadata = self._create_document_metadata(file_info)
                    registry["documents"].append(doc_metadata)
                    added_count += 1
                    logger.info(f"🔍 Auto-discovered: {file_info['path']}")
            
            # Remove documents for deleted files
            removed_count = 0
            existing_files = {str(f["relative_path"]) for f in discovered_files}
            
            registry["documents"] = [
                doc for doc in registry["documents"] 
                if doc.get("file_path") in existing_files
            ]
            
            # Save updated registry
            self._save_registry(registry)
            
            logger.info(f"📊 Filesystem sync: +{added_count} added, -{removed_count} removed")
            return added_count
    
    def _create_document_metadata(self, file_info: Dict) -> Dict[str, Any]:
        """Erstelle Metadaten für eine neue Datei"""
        file_path = file_info['path']
        relative_path = file_info['relative_path']
        stats = file_info['stats']
        
        # Generate unique ID
        file_id = f"manual_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine file type and category
        file_extension = file_path.suffix.lower()
        if file_extension == ".md":
            doctype, category = "markdown", "documentation"
        elif file_extension == ".txt":
            doctype, category = "text", "general" 
        elif file_extension == ".pdf":
            doctype, category = "pdf", "manual"
        else:
            doctype, category = "unknown", "general"
        
        return {
            "id": file_id,
            "filename": file_path.name,
            "original_filename": file_path.name,
            "doctype": doctype,
            "category": category,
            "folder_id": str(relative_path.parent) if relative_path.parent != Path(".") else None,
            "folder_path": str(relative_path.parent) if relative_path.parent != Path(".") else None,
            "upload_date": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "size_bytes": stats.st_size,
            "chunk_count": 0,
            "status": "ready",
            "tags": [],
            "visibility": "internal",
            "language": "de",
            "created_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "file_path": str(relative_path)
        }
    
    def get_all_documents(self, category: Optional[str] = None, doctype: Optional[str] = None) -> List[Dict[str, Any]]:
        """Hole alle Dokumente mit optionaler Filterung"""
        with self.lock:
            registry = self._load_registry()
            documents = registry["documents"]
            
            # Apply filters
            if category:
                documents = [doc for doc in documents if doc.get('category') == category]
            if doctype:
                documents = [doc for doc in documents if doc.get('doctype') == doctype]
            
            # Sort by upload_date (newest first)
            documents.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
            
            return documents
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Hole ein spezifisches Dokument"""
        with self.lock:
            registry = self._load_registry()
            for doc in registry["documents"]:
                if doc["id"] == doc_id:
                    return doc
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Lösche Dokument aus Registry und Dateisystem"""
        with self.lock:
            registry = self._load_registry()
            
            # Find document
            doc = None
            for i, d in enumerate(registry["documents"]):
                if d["id"] == doc_id:
                    doc = registry["documents"].pop(i)
                    break
            
            if not doc:
                return False
            
            # Delete physical file
            try:
                if doc.get("file_path"):
                    file_path = settings.DOCUMENTS_BASE_PATH / doc["file_path"]
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"🗑️ Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete physical file: {e}")
            
            # Save updated registry
            self._save_registry(registry)
            logger.info(f"✅ Deleted document {doc_id} from registry")
            
            return True
    
    def add_document(self, file_path: Path, metadata: Dict[str, Any] = None) -> str:
        """Füge neues Dokument zur Registry hinzu"""
        with self.lock:
            registry = self._load_registry()
            
            if metadata is None:
                # Create metadata automatically
                relative_path = file_path.relative_to(settings.DOCUMENTS_BASE_PATH)
                file_info = {
                    'path': file_path,
                    'relative_path': relative_path,
                    'stats': file_path.stat()
                }
                metadata = self._create_document_metadata(file_info)
            
            registry["documents"].append(metadata)
            self._save_registry(registry)
            
            logger.info(f"➕ Added document {metadata['id']} to registry")
            return metadata["id"]
    
    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Aktualisiere Dokument-Metadaten"""
        with self.lock:
            registry = self._load_registry()
            
            for doc in registry["documents"]:
                if doc["id"] == doc_id:
                    doc.update(updates)
                    doc["updated_at"] = datetime.now().isoformat()
                    self._save_registry(registry)
                    logger.info(f"📝 Updated document {doc_id}")
                    return True
            
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Hole Registry-Statistiken"""
        with self.lock:
            registry = self._load_registry()
            documents = registry["documents"]
            
            return {
                "total_documents": len(documents),
                "by_type": {
                    doctype: len([d for d in documents if d.get("doctype") == doctype])
                    for doctype in set(d.get("doctype", "unknown") for d in documents)
                },
                "by_status": {
                    status: len([d for d in documents if d.get("status") == status])
                    for status in set(d.get("status", "unknown") for d in documents)
                },
                "last_updated": registry.get("last_updated")
            }

# Global singleton instance
document_registry = DocumentRegistry()