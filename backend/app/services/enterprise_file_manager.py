"""
🏢 ENTERPRISE FILE MANAGER - PRODUCTION READY
Consolidierte, fehlerfreie Dateiverwaltung für training_files_v2
ZERO TOLERANCE für Code-Chaos - Nur das Wichtigste!
"""
import hashlib
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.enterprise_chromadb_indexer import enterprise_indexer
from app.services.multi_format_processor import multi_format_processor

logger = logging.getLogger(__name__)

class EnterpriseFileManager:
    """
    🏆 ENTERPRISE FILE MANAGER - PRODUCTION READY
    Konsolidierte, fehlerfreie Verwaltung aller Dateien
    """
    
    def __init__(self):
        self.allowed_extensions = [
            ".txt", ".md", ".rtf", ".log", ".pdf", ".docx", ".doc", ".odt",
            ".csv", ".tsv", ".xlsx", ".xls", ".json", ".jsonl", ".yaml", ".yml",
            ".xml", ".html", ".htm", ".py", ".js", ".ts", ".sql"
        ]
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
    async def upload_file(
        self, 
        file: UploadFile, 
        category_slug: str, 
        folder_slug: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        ✅ ENTERPRISE FILE UPLOAD - BULLETPROOF
        Handles everything: validation, storage, database, indexing
        """
        try:
            # 1. VALIDATE FILE
            if not file.filename:
                raise HTTPException(400, "No filename provided")
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in self.allowed_extensions:
                raise HTTPException(400, f"File type not allowed: {file_extension}")
            
            # 2. READ AND VALIDATE CONTENT
            file_content = await file.read()
            if len(file_content) > self.max_file_size:
                raise HTTPException(400, f"File too large (max {self.max_file_size//1024//1024}MB)")
            
            # 3. GET CATEGORY
            category_result = await db.execute(
                text("SELECT id, name FROM document_categories WHERE slug = :slug AND is_active = true"),
                {"slug": category_slug}
            )
            category_row = category_result.first()
            if not category_row:
                raise HTTPException(400, f"Category not found: {category_slug}")
            
            category_id = category_row.id
            category_name = category_row.name
            
            # 4. GET FOLDER (if specified)
            folder_id = None
            folder_name = None
            if folder_slug:
                folder_result = await db.execute(
                    text("SELECT id, name FROM document_folders WHERE slug = :slug AND category_id = :cat_id AND is_active = true"),
                    {"slug": folder_slug, "cat_id": category_id}
                )
                folder_row = folder_result.first()
                if not folder_row:
                    raise HTTPException(400, f"Folder not found: {folder_slug}")
                folder_id = folder_row.id
                folder_name = folder_row.name
            
            # 5. CREATE UNIQUE STORAGE PATH
            timestamp = int(time.time())
            file_name, file_ext = os.path.splitext(file.filename)
            unique_filename = f"{file_name}_{timestamp}{file_ext}"
            
            storage_path = f"data/documents/{category_slug}"
            if folder_slug:
                storage_path += f"/{folder_slug}"
            storage_path += f"/{unique_filename}"
            
            # 6. SAVE FILE TO DISK
            storage_file_path = Path(storage_path)
            storage_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(storage_file_path, 'wb') as f:
                f.write(file_content)
            
            # ENTERPRISE PDF zu Markdown Konvertierung für beste Datenqualität
            md_path = None
            if file_extension.lower() == '.pdf':
                try:
                    from app.services.production_document_processor import production_document_processor
                    
                    # PRODUCTION-GRADE PDF zu Markdown Konvertierung
                    conversion_result = await production_document_processor.process_document(
                        str(storage_file_path), 
                        file_content, 
                        file.filename
                    )
                    
                    if conversion_result.success and conversion_result.documents:
                        # Extrahiere bereinigten Text und kombiniere zu Markdown
                        md_filename = f"{file_name}_{timestamp}.md"
                        md_path = storage_file_path.parent / md_filename
                        
                        # Kombiniere alle Chunks zu sauberem Markdown
                        clean_content_parts = []
                        for chunk in conversion_result.documents:
                            # Nutze die aggressive Reinigung vom Production Processor
                            clean_text = production_document_processor._clean_document_text_aggressive(chunk.page_content)
                            if clean_text.strip():
                                clean_content_parts.append(clean_text.strip())
                        
                        # Erstelle finales Markdown mit Titel
                        final_markdown = f"# {file_name}\\n\\n" + "\\n\\n".join(clean_content_parts)
                        
                        with open(md_path, 'w', encoding='utf-8') as md_file:
                            md_file.write(final_markdown)
                        
                        logger.info(f"📄 PRODUCTION PDF zu MD konvertiert: {md_filename}")
                except Exception as e:
                    logger.warning(f"⚠️ Enterprise PDF-Konvertierung fehlgeschlagen, Fallback: {e}")
                    try:
                        # Fallback zu einfacher Konvertierung
                        from app.services.multi_format_processor import multi_format_processor
                        simple_result = await multi_format_processor.process_file(str(storage_file_path), file_content)
                        
                        if simple_result.success and simple_result.documents:
                            md_filename = f"{file_name}_{timestamp}.md"
                            md_path = storage_file_path.parent / md_filename
                            markdown_content = "\\n\\n".join([doc.page_content for doc in simple_result.documents])
                            
                            with open(md_path, 'w', encoding='utf-8') as md_file:
                                md_file.write(markdown_content)
                            
                            logger.info(f"📄 Fallback PDF zu MD konvertiert: {md_filename}")
                    except Exception as fallback_error:
                        logger.error(f"❌ Alle PDF-Konvertierungen fehlgeschlagen: {fallback_error}")
                        md_path = None
            
            # 7. INSERT INTO DATABASE
            file_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO training_files_v2 (
                    id, category_id, folder_id, original_filename, storage_path,
                    file_hash, file_size, file_type, processing_status,
                    created_at, updated_at, is_active
                ) VALUES (
                    :id, :category_id, :folder_id, :filename, :storage_path,
                    :file_hash, :file_size, :file_type, 'uploaded',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, true
                )
            """), {
                "id": file_id,
                "category_id": category_id,
                "folder_id": folder_id,
                "filename": file.filename,
                "storage_path": str(storage_file_path),
                "file_hash": hashlib.sha256(file_content).hexdigest(),
                "file_size": len(file_content),
                "file_type": file_extension
            })
            
            await db.commit()
            logger.info(f"✅ File uploaded: {file.filename}")
            
            # 8. BACKGROUND INDEXING - QUEUE FOR PROCESSING
            final_status = "ready_for_indexing"
            
            # Queue for background indexing - NON-BLOCKING
            from app.services.background_indexer import background_indexer
            try:
                # Use asyncio.create_task to make it truly non-blocking
                import asyncio
                asyncio.create_task(background_indexer.queue_file_for_indexing(file_id, file.filename))
            except Exception as e:
                logger.warning(f"⚠️ Background indexing queue failed: {e}")
            
            logger.info(f"⚡ Upload complete and queued for indexing: {file.filename}")
            
            return {
                "id": file_id,
                "filename": file.filename,
                "category_slug": category_slug,
                "category_name": category_name,
                "folder_slug": folder_slug,
                "folder_name": folder_name,
                "file_size": len(file_content),
                "upload_date": datetime.now(timezone.utc),
                "status": final_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Upload failed: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")
    
    async def get_files(
        self, 
        db: AsyncSession,
        category_slug: Optional[str] = None,
        folder_slug: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all files with optional filtering"""
        try:
            query = """
            SELECT 
                tf.id, tf.original_filename, tf.file_size, tf.created_at,
                tf.processing_status, tf.folder_id,
                dc.slug as category_slug, dc.name as category_name,
                df.slug as folder_slug, df.name as folder_name
            FROM training_files_v2 tf
            JOIN document_categories dc ON tf.category_id = dc.id
            LEFT JOIN document_folders df ON tf.folder_id = df.id
            WHERE tf.is_active = true AND tf.deleted_at IS NULL
            """
            
            params = {}
            if category_slug:
                query += " AND dc.slug = :category_slug"
                params["category_slug"] = category_slug
            if folder_slug:
                query += " AND df.slug = :folder_slug"
                params["folder_slug"] = folder_slug
            
            query += " ORDER BY tf.created_at DESC"
            
            result = await db.execute(text(query), params)
            
            files = []
            for row in result:
                files.append({
                    "id": str(row.id),
                    "filename": row.original_filename,
                    "category_slug": row.category_slug,
                    "category_name": row.category_name,
                    "folder_id": str(row.folder_id) if row.folder_id else None,
                    "folder_slug": row.folder_slug,
                    "folder_name": row.folder_name,
                    "file_size": row.file_size,
                    "upload_date": row.created_at,
                    "status": row.processing_status
                })
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Failed to get files: {e}")
            raise HTTPException(500, "Failed to retrieve files")
    
    async def delete_file(self, file_id: str, db: AsyncSession) -> Dict[str, str]:
        """Delete a file completely"""
        try:
            # Get file info
            result = await db.execute(
                text("SELECT original_filename, storage_path FROM training_files_v2 WHERE id = :id AND is_active = true"),
                {"id": file_id}
            )
            file_row = result.first()
            if not file_row:
                raise HTTPException(404, "File not found")
            
            # Remove from ChromaDB
            try:
                await enterprise_indexer.remove_file_from_index(file_id, db)
            except Exception as e:
                logger.warning(f"⚠️ ChromaDB removal failed: {e}")
            
            # Soft delete in database
            await db.execute(
                text("UPDATE training_files_v2 SET is_active = false, deleted_at = CURRENT_TIMESTAMP WHERE id = :id"),
                {"id": file_id}
            )
            
            # Delete physical file AND associated markdown
            try:
                if os.path.exists(file_row.storage_path):
                    os.remove(file_row.storage_path)
                    logger.info(f"✅ Physical file deleted: {file_row.storage_path}")
                    
                    # Delete associated markdown file if PDF
                    file_path = Path(file_row.storage_path)
                    if file_path.suffix.lower() == '.pdf':
                        # Look for corresponding markdown file
                        md_pattern = file_path.parent / f"{file_path.stem}.md"
                        if md_pattern.exists():
                            os.remove(md_pattern)
                            logger.info(f"✅ Associated markdown deleted: {md_pattern}")
                        
                        # Also check for timestamped pattern (file_timestamp.md)
                        for md_file in file_path.parent.glob(f"{file_path.stem.split('_')[0]}_*.md"):
                            try:
                                os.remove(md_file)
                                logger.info(f"✅ Timestamped markdown deleted: {md_file}")
                            except Exception as md_error:
                                logger.warning(f"⚠️ Failed to delete {md_file}: {md_error}")
            except Exception as e:
                logger.warning(f"⚠️ Physical file deletion failed: {e}")
            
            await db.commit()
            logger.info(f"✅ File deleted: {file_row.original_filename}")
            
            return {"message": "File deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Delete failed: {e}")
            raise HTTPException(500, f"Delete failed: {str(e)}")
    
    async def cleanup_error_files(self, db: AsyncSession) -> Dict[str, Any]:
        """Clean up files with errors"""
        try:
            # Get error files
            result = await db.execute(text("""
                SELECT id, original_filename, error_message 
                FROM training_files_v2 
                WHERE processing_status = 'error' AND is_active = true
            """))
            error_files = result.fetchall()
            
            stats = {
                "total_error_files": len(error_files),
                "cleaned_files": 0,
                "details": []
            }
            
            for file_row in error_files:
                try:
                    # Try to re-index
                    index_result = await enterprise_indexer.index_file(str(file_row.id), db)
                    stats["cleaned_files"] += 1
                    stats["details"].append({
                        "file": file_row.original_filename,
                        "status": "fixed",
                        "chunks": index_result.get("chunk_count", 0)
                    })
                except Exception as e:
                    stats["details"].append({
                        "file": file_row.original_filename,
                        "status": "still_error",
                        "error": str(e)
                    })
            
            logger.info(f"✅ Cleanup complete: {stats['cleaned_files']}/{stats['total_error_files']} files fixed")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            raise HTTPException(500, f"Cleanup failed: {str(e)}")


# Global instance
enterprise_file_manager = EnterpriseFileManager()