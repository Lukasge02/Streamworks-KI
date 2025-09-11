"""
Document Storage Handler
Handles file storage operations, path generation, and file system management
"""

import os
import hashlib
import shutil
from pathlib import Path
from typing import Tuple, BinaryIO
import logging

logger = logging.getLogger(__name__)


class DocumentStorageHandler:
    """
    Handles file storage operations for documents
    """
    
    def __init__(self, storage_root: str = "storage/documents"):
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def generate_storage_path(self, filename: str, file_hash: str) -> str:
        """Generate storage path for file"""
        # Use first 2 chars of hash for directory structure
        dir1 = file_hash[:2]
        dir2 = file_hash[2:4]
        
        # Clean filename
        clean_name = self.sanitize_filename(filename)
        
        # Add hash prefix to avoid conflicts
        storage_name = f"{file_hash[:8]}_{clean_name}"
        
        return f"{dir1}/{dir2}/{storage_name}"

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove potentially dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        clean_name = ''.join(c for c in filename if c not in dangerous_chars)
        
        # Limit length
        if len(clean_name) > 200:
            name, ext = os.path.splitext(clean_name)
            clean_name = name[:200-len(ext)] + ext
        
        return clean_name or "unnamed_file"

    def detect_mime_type(self, filename: str, content: bytes) -> str:
        """Detect MIME type from filename and content"""
        # Simple MIME type detection based on file extension
        ext = Path(filename).suffix.lower()
        
        mime_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
    
    def save_file(self, content: bytes, storage_path: str) -> Path:
        """
        Save file content to storage path
        
        Args:
            content: File content as bytes
            storage_path: Relative storage path (e.g., "aa/bb/aaabbbcc_filename.pdf")
            
        Returns:
            Full path to saved file
        """
        full_path = self.storage_root / storage_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File saved to {full_path}")
        return full_path
    
    def get_file_path(self, storage_path: str) -> Path:
        """Get full path for stored file"""
        return self.storage_root / storage_path
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in storage"""
        return (self.storage_root / storage_path).exists()
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            storage_path: Relative storage path
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        try:
            full_path = self.storage_root / storage_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                
                # Clean up empty directories
                try:
                    # Remove parent directories if they're empty
                    parent = full_path.parent
                    while parent != self.storage_root and not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent
                except OSError:
                    pass  # Directory not empty, which is fine
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {str(e)}")
            return False
    
    def get_file_info(self, storage_path: str) -> Tuple[bool, int]:
        """
        Get file information
        
        Args:
            storage_path: Relative storage path
            
        Returns:
            Tuple of (exists, size_in_bytes)
        """
        try:
            full_path = self.storage_root / storage_path
            if full_path.exists():
                return True, full_path.stat().st_size
            return False, 0
        except Exception as e:
            logger.error(f"Failed to get file info for {storage_path}: {str(e)}")
            return False, 0