from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

from ...models.database import get_db
from ...services.enterprise_chromadb_indexer import enterprise_indexer

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class FileResponse(BaseModel):
    id: str
    filename: str
    category_slug: str
    category_name: str
    folder_slug: Optional[str] = None
    folder_name: Optional[str] = None
    file_size: int
    upload_date: datetime
    status: str
    chunk_count: Optional[int] = None
    indexed_at: Optional[datetime] = None

class CategoryOption(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    folder_count: int = 0

class FolderOption(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None

# Allowed file extensions
ALLOWED_EXTENSIONS = [
    ".txt", ".md", ".rtf", ".log", ".pdf", ".docx", ".doc", ".odt",
    ".csv", ".tsv", ".xlsx", ".xls", ".json", ".jsonl", ".yaml", ".yml",
    ".xml", ".html", ".htm", ".py", ".js", ".ts", ".sql"
]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.get("/categories", response_model=List[CategoryOption])
async def get_categories_for_upload(db: AsyncSession = Depends(get_db)):
    """Get all active categories for upload selection"""
    try:
        query = """
        SELECT 
            dc.id, dc.slug, dc.name, dc.description,
            COUNT(df.id) as folder_count
        FROM document_categories dc
        LEFT JOIN document_folders df ON dc.id = df.category_id AND df.is_active = true
        WHERE dc.is_active = true
        GROUP BY dc.id, dc.slug, dc.name, dc.description
        ORDER BY dc.name
        """
        
        result = await db.execute(text(query))
        categories = []
        
        for row in result:
            categories.append(CategoryOption(
                id=str(row.id),
                slug=row.slug,
                name=row.name,
                description=row.description,
                folder_count=row.folder_count
            ))
        
        logger.info(f"✅ Retrieved {len(categories)} categories for upload")
        return categories
        
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

@router.get("/categories/{category_slug}/folders", response_model=List[FolderOption])
async def get_folders_for_category(
    category_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all folders for a specific category"""
    try:
        query = """
        SELECT df.id, df.slug, df.name, df.description
        FROM document_folders df
        JOIN document_categories dc ON df.category_id = dc.id
        WHERE dc.slug = :category_slug AND dc.is_active = true AND df.is_active = true
        ORDER BY df.name
        """
        
        result = await db.execute(text(query), {"category_slug": category_slug})
        folders = []
        
        for row in result:
            folders.append(FolderOption(
                id=str(row.id),
                slug=row.slug,
                name=row.name,
                description=row.description
            ))
        
        logger.info(f"✅ Retrieved {len(folders)} folders for category {category_slug}")
        return folders
        
    except Exception as e:
        logger.error(f"❌ Failed to get folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve folders")

@router.post("/categories/{category_slug}/folders", response_model=FolderOption)
async def create_folder(
    category_slug: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder in a category"""
    try:
        # Get category
        category_query = """
        SELECT id, name FROM document_categories 
        WHERE slug = :slug AND is_active = true
        """
        category_result = await db.execute(text(category_query), {"slug": category_slug})
        category_row = category_result.first()
        
        if not category_row:
            raise HTTPException(status_code=400, detail=f"Category '{category_slug}' not found")
        
        # Create slug
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # Check if slug already exists in this category
        existing_query = """
        SELECT id FROM document_folders 
        WHERE slug = :slug AND category_id = :category_id AND is_active = true
        """
        existing_result = await db.execute(text(existing_query), {
            "slug": slug,
            "category_id": category_row.id
        })
        
        if existing_result.scalar():
            raise HTTPException(status_code=409, detail=f"Folder '{name}' already exists in category")
        
        # Create folder
        folder_id = str(uuid.uuid4())
        insert_query = """
        INSERT INTO document_folders (id, name, slug, description, category_id, created_at, updated_at, is_active)
        VALUES (:id, :name, :slug, :description, :category_id, NOW(), NOW(), true)
        """
        await db.execute(text(insert_query), {
            "id": folder_id,
            "name": name,
            "slug": slug,
            "description": description,
            "category_id": category_row.id
        })
        
        await db.commit()
        
        logger.info(f"✅ Created folder: {name} in category {category_slug}")
        return FolderOption(
            id=folder_id,
            slug=slug,
            name=name,
            description=description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to create folder")

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a folder"""
    try:
        # Check if folder exists
        folder_query = """
        SELECT name FROM document_folders 
        WHERE id = :id AND is_active = true
        """
        folder_result = await db.execute(text(folder_query), {"id": folder_id})
        folder_row = folder_result.first()
        
        if not folder_row:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Check if folder has files
        files_query = """
        SELECT COUNT(*) FROM training_files_v2 
        WHERE folder_id = :folder_id AND is_active = true
        """
        files_result = await db.execute(text(files_query), {"folder_id": folder_id})
        file_count = files_result.scalar()
        
        if file_count > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete folder with {file_count} files. Please move or delete files first."
            )
        
        # Soft delete folder
        delete_query = """
        UPDATE document_folders 
        SET is_active = false, updated_at = NOW()
        WHERE id = :id
        """
        await db.execute(text(delete_query), {"id": folder_id})
        await db.commit()
        
        logger.info(f"✅ Deleted folder: {folder_row.name}")
        return {"message": "Folder deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete folder")

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    category_slug: str = Form(..., description="Category slug"),
    folder_slug: Optional[str] = Form(None, description="Optional folder slug"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to a specific category and optional folder"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Get category
        category_query = """
        SELECT id, name FROM document_categories 
        WHERE slug = :slug AND is_active = true
        """
        category_result = await db.execute(text(category_query), {"slug": category_slug})
        category_row = category_result.first()
        
        if not category_row:
            raise HTTPException(status_code=400, detail=f"Category '{category_slug}' not found")
        
        category_id = category_row.id
        category_name = category_row.name
        
        # Get folder (optional)
        folder_id = None
        folder_name = None
        if folder_slug:
            folder_query = """
            SELECT id, name FROM document_folders 
            WHERE slug = :slug AND category_id = :category_id AND is_active = true
            """
            folder_result = await db.execute(text(folder_query), {
                "slug": folder_slug,
                "category_id": category_id
            })
            folder_row = folder_result.first()
            
            if not folder_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Folder '{folder_slug}' not found in category '{category_slug}'"
                )
            
            folder_id = folder_row.id
            folder_name = folder_row.name
        
        # Create unique storage path to avoid conflicts
        import time
        timestamp = int(time.time())
        storage_path = f"data/documents/{category_slug}"
        if folder_slug:
            storage_path += f"/{folder_slug}"
        
        # Add timestamp to filename to ensure uniqueness
        file_name, file_ext = os.path.splitext(file.filename)
        unique_filename = f"{file_name}_{timestamp}{file_ext}"
        storage_path += f"/{unique_filename}"
        
        # Create directory if it doesn't exist
        storage_file_path = Path(storage_path)
        storage_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file to disk
        with open(storage_file_path, 'wb') as f:
            f.write(file_content)
        
        # Always insert new file (no duplicate check - timestamp ensures uniqueness)
        file_id = str(uuid.uuid4())
        insert_query = """
        INSERT INTO training_files_v2 (
            id, category_id, folder_id, original_filename, storage_path,
            file_hash, file_size, file_type, processing_status,
            created_at, updated_at, is_active
        ) VALUES (
            :id, :category_id, :folder_id, :filename, :storage_path,
            :file_hash, :file_size, :file_type, 'completed',
            NOW(), NOW(), true
        )
        """
        await db.execute(text(insert_query), {
            "id": file_id,
            "category_id": category_id,
            "folder_id": folder_id,
            "filename": file.filename,
            "storage_path": str(storage_file_path),
            "file_hash": hashlib.sha256(file_content).hexdigest(),
            "file_size": len(file_content),
            "file_type": file_extension
        })
        
        logger.info(f"✅ Inserted new file: {file.filename}")
        
        await db.commit()
        
        # Use the file_id from insert (always exists now)
        actual_file_id = file_id
        
        # Queue for background indexing - INSTANT UPLOAD
        from ...services.background_indexer import background_indexer
        try:
            await background_indexer.queue_file_for_indexing(actual_file_id, file.filename)
            index_status = "uploaded"  # Will be "indexed" after background processing
        except Exception as e:
            logger.warning(f"⚠️ Failed to queue for indexing: {e}")
            index_status = "uploaded"
        
        return FileResponse(
            id=actual_file_id,
            filename=file.filename,
            category_slug=category_slug,
            category_name=category_name,
            folder_slug=folder_slug,
            folder_name=folder_name,
            file_size=len(file_content),
            upload_date=datetime.now(timezone.utc),
            status=index_status,
            chunk_count=0,  # Will be updated after indexing
            indexed_at=None  # Will be updated after indexing
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files", response_model=List[FileResponse])
async def get_files(
    category_slug: Optional[str] = None,
    folder_slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all files, optionally filtered by category and/or folder"""
    try:
        query = """
        SELECT 
            tf.id, tf.original_filename, tf.file_size, tf.created_at,
            tf.processing_status,
            dc.slug as category_slug, dc.name as category_name,
            df.slug as folder_slug, df.name as folder_name,
            COALESCE(
                (SELECT old_tf.chunk_count FROM training_files old_tf 
                 WHERE old_tf.filename = tf.original_filename AND old_tf.status = 'ready'
                 ORDER BY old_tf.indexed_at DESC LIMIT 1),
                (SELECT old_tf.chunk_count FROM training_files old_tf 
                 WHERE old_tf.filename LIKE '%' || REPLACE(tf.original_filename, '.pdf', '') || '%' AND old_tf.status = 'ready'
                 ORDER BY old_tf.indexed_at DESC LIMIT 1),
                0
            ) as chunk_count,
            COALESCE(
                (SELECT old_tf.indexed_at FROM training_files old_tf 
                 WHERE old_tf.filename = tf.original_filename AND old_tf.status = 'ready'
                 ORDER BY old_tf.indexed_at DESC LIMIT 1),
                (SELECT old_tf.indexed_at FROM training_files old_tf 
                 WHERE old_tf.filename LIKE '%' || REPLACE(tf.original_filename, '.pdf', '') || '%' AND old_tf.status = 'ready'
                 ORDER BY old_tf.indexed_at DESC LIMIT 1),
                NULL
            ) as indexed_at
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
            # Determine actual status based on chunk count and processing status
            actual_status = row.processing_status
            if row.chunk_count > 0:
                actual_status = "ready"  # File is indexed
            elif row.processing_status == "completed":
                actual_status = "uploaded"  # File uploaded but not indexed yet
            
            # Debug: Check if data is there
            print(f"DEBUG: {row.original_filename} -> chunks: {row.chunk_count}, indexed: {row.indexed_at}")
            
            files.append(FileResponse(
                id=str(row.id),
                filename=row.original_filename,
                category_slug=row.category_slug,
                category_name=row.category_name,
                folder_slug=row.folder_slug,
                folder_name=row.folder_name,
                file_size=row.file_size,
                upload_date=row.created_at,
                status=actual_status,
                chunk_count=row.chunk_count,
                indexed_at=row.indexed_at
            ))
        
        logger.info(f"✅ Retrieved {len(files)} files")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to get files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@router.post("/files/{file_id}/index")
async def index_file_to_chromadb(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Manually index a file to ChromaDB"""
    try:
        result = await enterprise_indexer.index_file(file_id, db)
        return result
    except Exception as e:
        logger.error(f"❌ Manual indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.delete("/files/{file_id}/index")
async def remove_file_from_index(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a file from ChromaDB index"""
    try:
        success = await enterprise_indexer.remove_file_from_index(file_id, db)
        if success:
            return {"message": "File removed from index successfully"}
        else:
            return {"message": "No chunks found for this file"}
    except Exception as e:
        logger.error(f"❌ Failed to remove from index: {e}")
        raise HTTPException(status_code=500, detail=f"Remove from index failed: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    try:
        # Check if file exists
        check_query = """
        SELECT original_filename, storage_path FROM training_files_v2 
        WHERE id = :file_id AND is_active = true
        """
        check_result = await db.execute(text(check_query), {"file_id": file_id})
        file_row = check_result.first()
        
        if not file_row:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Soft delete in database
        delete_query = """
        UPDATE training_files_v2 
        SET is_active = false, deleted_at = NOW()
        WHERE id = :file_id
        """
        await db.execute(text(delete_query), {"file_id": file_id})
        
        # Delete physical file
        try:
            if os.path.exists(file_row.storage_path):
                os.remove(file_row.storage_path)
        except Exception as e:
            logger.warning(f"⚠️ Could not delete physical file: {e}")
        
        # Remove from ChromaDB index
        try:
            await enterprise_indexer.remove_file_from_index(file_id, db)
            logger.info(f"🗑️ Removed file from ChromaDB index")
        except Exception as e:
            logger.warning(f"⚠️ Could not remove from ChromaDB: {e}")
        
        await db.commit()
        
        logger.info(f"✅ Deleted file: {file_row.original_filename}")
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")