"""
Unified Storage System für StreamWorks-KI
Zentrale Verwaltung aller Dateipfade und Speicherstrukturen
"""
from pathlib import Path
from typing import Optional
from app.core.settings import settings

class UnifiedStorage:
    """Zentrale Storage-Verwaltung für alle Dateitypen"""
    
    def __init__(self):
        self.base_path = Path(settings.TRAINING_DATA_PATH)
        self.paths = {
            "documents": self.base_path / "documents",
            "converted": self.base_path / "converted", 
            "vector_db": self.base_path / "vector_db",
            "uploads": self.base_path / "uploads",
            "xml_templates": self.base_path / "xml_templates"
        }
        
        # Ensure all directories exist
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def get_converted_path(self, filename: str) -> str:
        """Get path for converted markdown files"""
        stem = Path(filename).stem
        return str(self.paths["converted"] / f"{stem}.md")
    
    def get_document_path(self, filename: str, category: Optional[str] = None) -> str:
        """Get path for storing original documents"""
        if category:
            category_path = self.paths["documents"] / category
            category_path.mkdir(parents=True, exist_ok=True)
            return str(category_path / filename)
        else:
            return str(self.paths["documents"] / filename)
    
    def get_upload_path(self, filename: str) -> str:
        """Get path for temporary uploads"""
        return str(self.paths["uploads"] / filename)
    
    def get_xml_template_path(self, filename: str) -> str:
        """Get path for XML templates"""
        return str(self.paths["xml_templates"] / filename)
    
    def get_vector_db_path(self) -> str:
        """Get vector database path"""
        return str(self.paths["vector_db"])
    
    def ensure_directory(self, path: str) -> None:
        """Ensure directory exists"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)

# Global storage instance
storage = UnifiedStorage()