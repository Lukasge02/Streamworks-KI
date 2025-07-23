"""
🏢 ENTERPRISE FILES API - PRODUCTION READY
Clean, consolidated API replacing the chaotic files.py
ZERO TOLERANCE für Code-Chaos!
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.enterprise_chromadb_indexer import enterprise_indexer
from app.services.enterprise_file_manager import enterprise_file_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class FileResponse(BaseModel):
    id: str
    filename: str
    category_slug: str
    category_name: str
    folder_id: Optional[str] = None
    folder_slug: Optional[str] = None
    folder_name: Optional[str] = None
    file_size: int
    upload_date: str
    status: str

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

@router.get("/categories", response_model=List[CategoryOption])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all active categories"""
    try:
        result = await db.execute(text("""
            SELECT 
                dc.id, dc.slug, dc.name, dc.description,
                COUNT(df.id) as folder_count
            FROM document_categories dc
            LEFT JOIN document_folders df ON dc.id = df.category_id AND df.is_active = true
            WHERE dc.is_active = true
            GROUP BY dc.id, dc.slug, dc.name, dc.description
            ORDER BY dc.name
        """))
        
        categories = []
        for row in result:
            categories.append(CategoryOption(
                id=str(row.id),
                slug=row.slug,
                name=row.name,
                description=row.description,
                folder_count=row.folder_count
            ))
        
        return categories
        
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(500, "Failed to retrieve categories")

@router.get("/categories/{category_slug}/folders", response_model=List[FolderOption])
async def get_folders(category_slug: str, db: AsyncSession = Depends(get_db)):
    """Get all folders for a category"""
    try:
        result = await db.execute(text("""
            SELECT df.id, df.slug, df.name, df.description
            FROM document_folders df
            JOIN document_categories dc ON df.category_id = dc.id
            WHERE dc.slug = :slug AND dc.is_active = true AND df.is_active = true
            ORDER BY df.name
        """), {"slug": category_slug})
        
        folders = []
        for row in result:
            folders.append(FolderOption(
                id=str(row.id),
                slug=row.slug,
                name=row.name,
                description=row.description
            ))
        
        return folders
        
    except Exception as e:
        logger.error(f"❌ Failed to get folders: {e}")
        raise HTTPException(500, "Failed to retrieve folders")

@router.post("/categories/{category_slug}/folders", response_model=FolderOption)
async def create_folder(
    category_slug: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder"""
    try:
        # Get category
        category_result = await db.execute(
            text("SELECT id FROM document_categories WHERE slug = :slug AND is_active = true"),
            {"slug": category_slug}
        )
        category_row = category_result.first()
        if not category_row:
            raise HTTPException(400, f"Category not found: {category_slug}")
        
        # Create unique slug with timestamp
        import re, time
        base_slug = re.sub(r'[^\w\s-]', '', name.lower())
        base_slug = re.sub(r'[-\s]+', '-', base_slug).strip('-')
        slug = f"{base_slug}-{int(time.time())}"
        
        # Double-check for uniqueness
        existing_result = await db.execute(text("""
            SELECT id FROM document_folders 
            WHERE slug = :slug AND category_id = :cat_id AND is_active = true
        """), {"slug": slug, "cat_id": category_row.id})
        
        if existing_result.scalar():
            # Add random number if still exists
            import random
            slug = f"{base_slug}-{int(time.time())}-{random.randint(100, 999)}"
        
        # Create folder
        import uuid
        folder_id = str(uuid.uuid4())
        await db.execute(text("""
            INSERT INTO document_folders (id, name, slug, description, category_id, created_at, updated_at, is_active)
            VALUES (:id, :name, :slug, :description, :cat_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, true)
        """), {
            "id": folder_id,
            "name": name,
            "slug": slug,
            "description": description,
            "cat_id": category_row.id
        })
        
        await db.commit()
        logger.info(f"✅ Created folder: {name}")
        
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
        raise HTTPException(500, "Failed to create folder")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category_slug: str = Form(...),
    folder_slug: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """✅ ENTERPRISE FILE UPLOAD - BULLETPROOF"""
    return await enterprise_file_manager.upload_file(file, category_slug, folder_slug, db)

@router.get("/files")
async def get_files(
    category_slug: Optional[str] = None,
    folder_slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all files with optional filtering"""
    return await enterprise_file_manager.get_files(db, category_slug, folder_slug)

@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a file"""
    return await enterprise_file_manager.delete_file(file_id, db)

@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a folder"""
    try:
        # Check if folder has files
        result = await db.execute(text("""
            SELECT COUNT(*) FROM training_files_v2 
            WHERE folder_id = :id AND is_active = true
        """), {"id": folder_id})
        
        if result.scalar() > 0:
            raise HTTPException(409, "Cannot delete folder with files")
        
        # Soft delete folder
        await db.execute(text("""
            UPDATE document_folders 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """), {"id": folder_id})
        
        await db.commit()
        logger.info(f"✅ Deleted folder: {folder_id}")
        
        return {"message": "Folder deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete folder: {e}")
        raise HTTPException(500, "Failed to delete folder")

@router.post("/files/{file_id}/index")
async def index_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """Manually index a file to ChromaDB"""
    try:
        result = await enterprise_indexer.index_file(file_id, db)
        return result
    except Exception as e:
        logger.error(f"❌ Manual indexing failed: {e}")
        raise HTTPException(500, f"Indexing failed: {str(e)}")

@router.delete("/files/{file_id}/index")
async def remove_file_from_index(file_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a file from ChromaDB index"""
    try:
        success = await enterprise_indexer.remove_file_from_index(file_id, db)
        return {"success": success, "message": "File removed from index"}
    except Exception as e:
        logger.error(f"❌ Failed to remove from index: {e}")
        raise HTTPException(500, f"Remove from index failed: {str(e)}")

@router.post("/admin/cleanup")
async def cleanup_error_files(db: AsyncSession = Depends(get_db)):
    """Admin: Clean up files with errors"""
    return await enterprise_file_manager.cleanup_error_files(db)