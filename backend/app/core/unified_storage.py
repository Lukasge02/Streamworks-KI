"""
Unified Storage System - Single Source of Truth
Ersetzt alle chaotischen Storage-Konfigurationen
"""
from pathlib import Path
import logging
from app.core.postgres_config import settings

logger = logging.getLogger(__name__)

class UnifiedStorage:
    """Clean, unified storage system für alle Dateien"""
    
    def __init__(self):
        self.base_path = Path(settings.DATA_PATH)
        self.setup_clean_structure()
    
    def setup_clean_structure(self):
        """Erstellt saubere, einheitliche Ordnerstruktur"""
        
        self.paths = {
            # Hauptordner
            "documents": self.base_path / "documents",      # Alle hochgeladenen Dateien
            "converted": self.base_path / "converted",      # Alle MD-Konvertierungen
            "vector_db": self.base_path / "vector_db",      # ChromaDB Storage
            "logs": self.base_path / "logs",                # Log-Dateien
            "temp": self.base_path / "temp",                # Temporäre Dateien
            "exports": self.base_path / "exports",          # Analytics Exports
        }
        
        # Erstelle alle Ordner
        for name, path in self.paths.items():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Ensured directory: {path}")
    
    # === DOCUMENT STORAGE ===
    
    def get_document_path(self, filename: str) -> Path:
        """Pfad für hochgeladenes Dokument"""
        return self.paths["documents"] / filename
    
    def get_converted_path(self, filename: str) -> Path:
        """Pfad für konvertiertes Markdown"""
        md_name = Path(filename).with_suffix('.md').name
        return self.paths["converted"] / md_name
    
    def get_temp_path(self, filename: str) -> Path:
        """Pfad für temporäre Datei"""
        return self.paths["temp"] / filename
    
    # === VECTOR DATABASE ===
    
    def get_vector_db_path(self) -> Path:
        """ChromaDB Speicherpfad"""
        return self.paths["vector_db"]
    
    # === ANALYTICS & EXPORTS ===
    
    def get_export_path(self, filename: str) -> Path:
        """Pfad für Analytics-Exports"""
        return self.paths["exports"] / filename
    
    def get_log_path(self, filename: str) -> Path:
        """Pfad für Log-Dateien"""
        return self.paths["logs"] / filename
    
    # === UTILITIES ===
    
    def cleanup_temp_files(self) -> int:
        """Bereinigt temporäre Dateien"""
        temp_files = list(self.paths["temp"].glob("*"))
        for temp_file in temp_files:
            if temp_file.is_file():
                temp_file.unlink()
        
        logger.info(f"🧹 Cleaned {len(temp_files)} temporary files")
        return len(temp_files)
    
    def get_storage_stats(self) -> dict:
        """Storage-Statistiken für Monitoring"""
        stats = {}
        
        for name, path in self.paths.items():
            if path.exists():
                files = list(path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                stats[name] = {
                    "file_count": file_count,
                    "total_size_mb": round(total_size / 1024 / 1024, 2),
                    "path": str(path)
                }
        
        return stats
    
    def validate_storage(self) -> bool:
        """Validiert Storage-Integrität"""
        try:
            for name, path in self.paths.items():
                if not path.exists():
                    logger.warning(f"⚠️ Missing storage path: {name} -> {path}")
                    return False
                
                # Test write access
                test_file = path / ".storage_test"
                test_file.touch()
                test_file.unlink()
            
            logger.info("✅ Storage validation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Storage validation failed: {e}")
            return False

# Global storage instance
storage = UnifiedStorage()