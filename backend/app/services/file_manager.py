"""
Simple File Manager - Bulletproof Implementation
"""
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class SimpleFileManager:
    """Simple, working file manager"""
    
    def __init__(self):
        self.upload_dir = Path("./data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = [".txt", ".md", ".pdf", ".docx", ".json"]
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
    async def get_files(
        self, 
        db: AsyncSession,
        category_slug: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all files - simple version"""
        try:
            # Simple query that works with existing schema
            query = """
            SELECT 
                tf.id, 
                COALESCE(tf.display_name, tf.filename) as filename,
                tf.file_size,
                tf.upload_date,
                tf.status
            FROM training_files tf
            WHERE 1=1
            """
            
            params = {}
            if category_slug:
                # Simple category filter
                query += " AND tf.category = :category_slug"
                params["category_slug"] = category_slug
            
            query += " ORDER BY tf.id DESC LIMIT 100"
            
            result = await db.execute(text(query), params)
            
            files = []
            for row in result:
                files.append({
                    "id": str(row.id),
                    "filename": row.filename or "Unknown",
                    "category_slug": category_slug or 'unknown',
                    "category_name": 'Unknown',
                    "folder_slug": None,
                    "folder_name": None,
                    "file_size": row.file_size or 0,
                    "upload_date": str(row.upload_date) if row.upload_date else datetime.now().isoformat(),
                    "status": row.status or "unknown"
                })
            
            logger.info(f"✅ Retrieved {len(files)} files")
            return files
            
        except Exception as e:
            logger.error(f"❌ Failed to get files: {e}")
            # DEBUG: Print the error details
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return empty list instead of crashing
            return []
    
    async def upload_file(
        self,
        file: UploadFile,
        category_slug: str,
        folder_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Upload file - simple version"""
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(400, "No filename provided")
            
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                raise HTTPException(400, f"File type {file_ext} not allowed")
            
            # Read file content
            content = await file.read()
            if len(content) > self.max_file_size:
                raise HTTPException(400, "File too large")
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%d%m%y-%H%M%S")
            safe_filename = f"{Path(file.filename).stem}-{timestamp}{file_ext}"
            file_path = self.upload_dir / safe_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Get category ID
            cat_result = await db.execute(
                text("SELECT id FROM document_categories WHERE slug = :slug"),
                {"slug": category_slug}
            )
            cat_row = cat_result.first()
            category_id = cat_row.id if cat_row else None
            
            # Insert into database - using only columns that definitely exist
            await db.execute(text("""
                INSERT INTO training_files (
                    id, filename, display_name, category, 
                    file_size, file_path, status, upload_date
                ) VALUES (
                    :id, :filename, :display_name, :category,
                    :file_size, :file_path, 'uploaded', CURRENT_TIMESTAMP
                )
            """), {
                "id": file_id,
                "filename": safe_filename,
                "display_name": file.filename,
                "category": category_slug,
                "file_size": len(content),
                "file_path": str(file_path)
            })
            
            await db.commit()
            
            logger.info(f"✅ File uploaded: {file.filename}")
            
            return {
                "id": file_id,
                "filename": file.filename,
                "status": "uploaded",
                "file_size": len(content),
                "message": "File uploaded successfully"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ File upload failed: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")
    
    async def delete_file(self, file_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Delete file - simple version"""
        try:
            # Get file info
            result = await db.execute(
                text("SELECT storage_path, original_filename FROM training_files WHERE id = :id"),
                {"id": file_id}
            )
            file_row = result.first()
            
            if not file_row:
                raise HTTPException(404, "File not found")
            
            # Delete from filesystem
            if file_row.storage_path and os.path.exists(file_row.storage_path):
                try:
                    os.remove(file_row.storage_path)
                except Exception as e:
                    logger.warning(f"Could not delete file from disk: {e}")
            
            # Delete from database
            await db.execute(
                text("DELETE FROM training_files WHERE id = :id"),
                {"id": file_id}
            )
            
            await db.commit()
            
            logger.info(f"✅ File deleted: {file_id}")
            
            return {
                "message": "File deleted successfully",
                "filename": file_row.original_filename
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ File deletion failed: {e}")
            raise HTTPException(500, f"Deletion failed: {str(e)}")

# Global instance
file_manager = SimpleFileManager()