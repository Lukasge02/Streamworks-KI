"""
File Storage Service with MinIO Support
Stores original files for viewing/download
"""

import os
import io
import base64
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List

# Import config to ensure .env is loaded
from config import config  # noqa: F401


class FileStorageService:
    """
    Service for storing original document files
    
    Storage modes:
    1. Local filesystem (fallback for development)
    2. MinIO/S3 (production)
    """
    
    # Go up from storage/ -> rag/ -> services/ -> backend/
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
    
    def __init__(self):
        self._minio_client = None
        self._bucket_name = os.environ.get("MINIO_BUCKET", "documents")
        self._use_minio = self._init_minio()
        
        if not self._use_minio:
            # Ensure local upload directory exists as fallback
            os.makedirs(self.UPLOAD_DIR, exist_ok=True)
            print(f"📁 FileStorage initialized (local): {self.UPLOAD_DIR}")
    
    def _init_minio(self) -> bool:
        """Initialize MinIO client if configured"""
        endpoint = os.environ.get("MINIO_ENDPOINT")
        access_key = os.environ.get("MINIO_ACCESS_KEY")
        secret_key = os.environ.get("MINIO_SECRET_KEY")
        
        if not all([endpoint, access_key, secret_key]):
            print("⚠️ MinIO not configured, using local storage")
            return False
        
        try:
            from minio import Minio
            from minio.error import S3Error
            
            secure = os.environ.get("MINIO_SECURE", "false").lower() == "true"
            
            self._minio_client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            
            # Ensure bucket exists
            if not self._minio_client.bucket_exists(self._bucket_name):
                self._minio_client.make_bucket(self._bucket_name)
                print(f"✅ Created MinIO bucket: {self._bucket_name}")
            
            print(f"✅ FileStorage initialized (MinIO): {endpoint}/{self._bucket_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ MinIO initialization failed: {e}, falling back to local storage")
            return False
    
    def save_file(
        self,
        content: bytes,
        filename: str,
        doc_id: str
    ) -> Dict[str, Any]:
        """
        Save original file to storage
        
        Returns file info with path and URL
        """
        # Create unique filename
        ext = os.path.splitext(filename)[1].lower()
        stored_name = f"{doc_id}{ext}"
        
        if self._use_minio:
            return self._save_to_minio(content, stored_name, filename)
        else:
            return self._save_to_local(content, stored_name, filename)
    
    def _save_to_minio(self, content: bytes, stored_name: str, original_name: str) -> Dict[str, Any]:
        """Save file to MinIO"""
        try:
            data = io.BytesIO(content)
            
            # Determine content type
            ext = os.path.splitext(stored_name)[1].lower()
            content_type = self._get_content_type(ext)
            
            self._minio_client.put_object(
                self._bucket_name,
                stored_name,
                data,
                length=len(content),
                content_type=content_type,
                metadata={"original_name": original_name}
            )
            
            return {
                "stored_name": stored_name,
                "original_name": original_name,
                "storage": "minio",
                "bucket": self._bucket_name,
                "size_bytes": len(content),
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ MinIO save failed: {e}")
            raise
    
    def _save_to_local(self, content: bytes, stored_name: str, original_name: str) -> Dict[str, Any]:
        """Save file to local filesystem"""
        file_path = os.path.join(self.UPLOAD_DIR, stored_name)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "stored_name": stored_name,
            "original_name": original_name,
            "file_path": file_path,
            "storage": "local",
            "size_bytes": len(content),
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_file(self, doc_id: str, ext: str = None) -> Optional[Tuple[bytes, str]]:
        """
        Retrieve file by doc_id
        
        Tries MinIO first (if enabled), then falls back to local storage
        for backwards compatibility with files uploaded before MinIO was enabled.
        
        Returns (content, filename) or None
        """
        if self._use_minio:
            # Try MinIO first
            result = self._get_from_minio(doc_id, ext)
            if result:
                return result
            # Fall back to local storage for old files
            return self._get_from_local(doc_id, ext)
        else:
            return self._get_from_local(doc_id, ext)
    
    def _get_from_minio(self, doc_id: str, ext: str = None) -> Optional[Tuple[bytes, str]]:
        """Get file from MinIO"""
        extensions = [ext] if ext else ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']
        
        for extension in extensions:
            object_name = f"{doc_id}{extension}"
            try:
                response = self._minio_client.get_object(self._bucket_name, object_name)
                content = response.read()
                response.close()
                response.release_conn()
                return content, object_name
            except Exception:
                continue
        
        return None
    
    def _get_from_local(self, doc_id: str, ext: str = None) -> Optional[Tuple[bytes, str]]:
        """Get file from local filesystem"""
        extensions = [ext] if ext else ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']
        
        for extension in extensions:
            file_path = os.path.join(self.UPLOAD_DIR, f"{doc_id}{extension}")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                return content, f"{doc_id}{extension}"
        
        return None
    
    def get_file_base64(self, doc_id: str, ext: str = None) -> Optional[Dict[str, str]]:
        """Get file as base64 for frontend display (best for small files)"""
        result = self.get_file(doc_id, ext)
        if not result:
            return None
        
        content, filename = result
        file_ext = os.path.splitext(filename)[1].lower()
        mime = self._get_content_type(file_ext)
        b64 = base64.b64encode(content).decode('utf-8')
        
        return {
            "filename": filename,
            "mime_type": mime,
            "size_bytes": len(content),
            "data": b64,
            "data_url": f"data:{mime};base64,{b64}"
        }
    
    def get_presigned_url(
        self, 
        doc_id: str, 
        ext: str = None,
        expiry_hours: int = 1,
        inline: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate presigned URL for direct browser access
        
        This is the recommended method for large files (>2MB).
        The browser can load the file directly from MinIO without
        going through FastAPI, which avoids memory issues.
        
        Args:
            doc_id: Document ID
            ext: File extension (auto-detected if not provided)
            expiry_hours: URL expiry time in hours
            inline: If True, file displays in browser; if False, downloads
            
        Returns:
            Dict with url, filename, mime_type, expiry, size_bytes
        """
        if not self._use_minio:
            # For local storage, presigned URLs aren't possible
            # Return None so caller can fall back to base64
            return None
        
        from datetime import timedelta
        
        extensions = [ext] if ext else ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']
        
        for extension in extensions:
            object_name = f"{doc_id}{extension}"
            try:
                # Check if object exists first
                stat = self._minio_client.stat_object(self._bucket_name, object_name)
                
                mime = self._get_content_type(extension)
                
                # Set response headers for inline display or download
                response_headers = {}
                if inline:
                    response_headers["response-content-disposition"] = f"inline; filename=\"{object_name}\""
                else:
                    response_headers["response-content-disposition"] = f"attachment; filename=\"{object_name}\""
                response_headers["response-content-type"] = mime
                
                # Generate presigned URL
                url = self._minio_client.presigned_get_object(
                    self._bucket_name,
                    object_name,
                    expires=timedelta(hours=expiry_hours),
                    response_headers=response_headers
                )
                
                return {
                    "url": url,
                    "filename": object_name,
                    "mime_type": mime,
                    "size_bytes": stat.size,
                    "expiry_hours": expiry_hours,
                    "storage": "minio"
                }
            except Exception:
                continue
        
        return None
    
    def get_file_info(self, doc_id: str, ext: str = None) -> Optional[Dict[str, Any]]:
        """
        Get file metadata without downloading content
        
        Useful for determining if presigned URL should be used
        """
        if self._use_minio:
            extensions = [ext] if ext else ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']
            for extension in extensions:
                object_name = f"{doc_id}{extension}"
                try:
                    stat = self._minio_client.stat_object(self._bucket_name, object_name)
                    return {
                        "filename": object_name,
                        "size_bytes": stat.size,
                        "mime_type": self._get_content_type(extension),
                        "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                        "storage": "minio"
                    }
                except Exception:
                    continue
        else:
            # Local storage
            extensions = [ext] if ext else ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']
            for extension in extensions:
                file_path = os.path.join(self.UPLOAD_DIR, f"{doc_id}{extension}")
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    return {
                        "filename": f"{doc_id}{extension}",
                        "size_bytes": stat.st_size,
                        "mime_type": self._get_content_type(extension),
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "storage": "local"
                    }
        
        return None
    
    def _get_content_type(self, ext: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xml': 'application/xml',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.html': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def delete_file(self, doc_id: str) -> bool:
        """Delete file by doc_id"""
        if self._use_minio:
            return self._delete_from_minio(doc_id)
        else:
            return self._delete_from_local(doc_id)
    
    def _delete_from_minio(self, doc_id: str) -> bool:
        """Delete file from MinIO"""
        for ext in ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']:
            object_name = f"{doc_id}{ext}"
            try:
                self._minio_client.remove_object(self._bucket_name, object_name)
                return True
            except Exception:
                continue
        return False
    
    def _delete_from_local(self, doc_id: str) -> bool:
        """Delete file from local filesystem"""
        for ext in ['.pdf', '.docx', '.pptx', '.xml', '.txt', '.md', '.json', '.html', '.png', '.jpg']:
            file_path = os.path.join(self.UPLOAD_DIR, f"{doc_id}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        return False
    
    def list_files(self) -> List[Dict[str, Any]]:
        """List all stored files"""
        if self._use_minio:
            return self._list_minio_files()
        else:
            return self._list_local_files()
    
    def _list_minio_files(self) -> List[Dict[str, Any]]:
        """List files from MinIO"""
        files = []
        try:
            objects = self._minio_client.list_objects(self._bucket_name)
            for obj in objects:
                files.append({
                    "filename": obj.object_name,
                    "size_bytes": obj.size,
                    "modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "storage": "minio"
                })
        except Exception as e:
            print(f"❌ MinIO list failed: {e}")
        return files
    
    def _list_local_files(self) -> List[Dict[str, Any]]:
        """List files from local filesystem"""
        files = []
        if not os.path.exists(self.UPLOAD_DIR):
            return files
            
        for filename in os.listdir(self.UPLOAD_DIR):
            file_path = os.path.join(self.UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                files.append({
                    "filename": filename,
                    "size_bytes": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    "storage": "local"
                })
        return files
    
    def find_by_extension(self, ext: str) -> List[Dict[str, Any]]:
        """Find all files with a given extension"""
        files = []
        all_files = self.list_files()
        
        for f in all_files:
            filename = f["filename"]
            if filename.endswith(ext):
                doc_id = filename.replace(ext, '')
                files.append({
                    "doc_id": doc_id,
                    "filename": filename,
                    "extension": ext,
                    "size_bytes": f["size_bytes"],
                    "storage": f.get("storage", "unknown")
                })
        
        return files


# Singleton instance
file_storage = FileStorageService()
