"""
Enterprise Storage Configuration
Handles file organization with original names and folder structure
"""
import os
from pathlib import Path
from typing import Optional
import hashlib
from datetime import datetime

class StorageConfig:
    """Enterprise-grade storage configuration"""
    
    def __init__(self, base_path: str = "./data/documents"):
        self.base_path = Path(base_path)
        self.ensure_structure()
    
    def ensure_structure(self):
        """Create folder structure if not exists"""
        categories = ["qa", "stream-xml", "streamworks-api"]
        for category in categories:
            (self.base_path / category).mkdir(parents=True, exist_ok=True)
    
    def get_file_path(
        self, 
        category: str, 
        folder: Optional[str], 
        filename: str,
        preserve_original: bool = True
    ) -> Path:
        """
        Generate file path preserving original filename
        
        Structure:
        /data/documents/
        ├── qa/
        │   ├── streamworks-f1/
        │   │   ├── Installation_Guide.pdf
        │   │   └── FAQ_Common_Issues.pdf
        │   ├── sharepoint/
        │   │   └── SharePoint_Integration.docx
        │   └── confluence/
        │       └── API_Documentation.md
        ├── stream-xml/
        │   ├── Template_Basic.xml
        │   └── Template_Advanced.xml
        └── streamworks-api/
            └── API_Spec_v2.0.json
        """
        # Build path
        path_parts = [self.base_path, category]
        if folder:
            path_parts.append(folder)
        
        base_dir = Path(*path_parts)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        if preserve_original:
            # Keep original filename, handle duplicates
            file_path = base_dir / filename
            if file_path.exists():
                # Add timestamp to handle duplicates
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}{ext}"
                file_path = base_dir / filename
        else:
            # Legacy mode with hash prefix
            file_hash = hashlib.sha256(filename.encode()).hexdigest()[:8]
            file_path = base_dir / f"{file_hash}_{filename}"
        
        return file_path
    
    def get_display_source(self, category: str, folder: Optional[str], filename: str) -> str:
        """Generate display source for RAG responses"""
        if category == "qa" and folder:
            # Clean folder name for display
            folder_display = folder.replace("-", " ").title()
            return f"{folder_display} - {filename}"
        elif category == "stream-xml":
            return f"Stream XML - {filename}"
        elif category == "streamworks-api":
            return f"API Docs - {filename}"
        else:
            return filename
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        
        return f"{name}{ext}".strip()