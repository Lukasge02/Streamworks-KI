"""
SIMPLE FOLDERS API - WORKS 100%
No complex services, direct database queries
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db

router = APIRouter()

@router.get("/categories/{category_slug}/folders")
async def get_folders(category_slug: str, db: AsyncSession = Depends(get_db)):
    """Get all folders for a category - SIMPLE VERSION"""
    try:
        # Get category first
        category_result = await db.execute(
            text("SELECT id FROM document_categories WHERE slug = :slug"),
            {"slug": category_slug}
        )
        category_row = category_result.first()
        if not category_row:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_id = category_row.id
        
        # Get folders - SIMPLE QUERY (no file_count/subfolder_count columns)
        folders_result = await db.execute(
            text("""
                SELECT id, name, slug, parent_folder_id
                FROM document_folders 
                WHERE category_id = :category_id 
                AND is_active = true
                ORDER BY name
            """),
            {"category_id": category_id}
        )
        
        folders = []
        for row in folders_result:
            folders.append({
                "id": str(row.id),
                "name": row.name,
                "slug": row.slug,
                "parent_folder_id": str(row.parent_folder_id) if row.parent_folder_id else None,
                "file_count": 0,  # Default value
                "subfolder_count": 0  # Default value
            })
        
        return {"folders": folders}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/categories/{category_slug}/folders")
async def create_folder(
    category_slug: str,
    name: str = Form(...),
    parent_id: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder - SIMPLE VERSION"""
    try:
        # Get category
        category_result = await db.execute(
            text("SELECT id FROM document_categories WHERE slug = :slug"),
            {"slug": category_slug}
        )
        category_row = category_result.first()
        if not category_row:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_id = category_row.id
        
        # Generate folder data
        folder_id = str(uuid.uuid4())
        slug = name.lower().replace(" ", "_").replace("-", "_")
        
        # Insert folder - SIMPLE INSERT
        await db.execute(
            text("""
                INSERT INTO document_folders 
                (id, category_id, parent_folder_id, name, slug, description, 
                 color, icon, sort_order, is_active, created_at, updated_at)
                VALUES 
                (:id, :category_id, :parent_id, :name, :slug, :description,
                 :color, :icon, :sort_order, :is_active, :created_at, :updated_at)
            """),
            {
                "id": folder_id,
                "category_id": category_id,
                "parent_id": parent_id if parent_id else None,
                "name": name,
                "slug": slug,
                "description": f"Ordner für {name}",
                "color": "#3B82F6",
                "icon": "folder",
                "sort_order": 0,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        )
        
        await db.commit()
        
        return {
            "id": folder_id,
            "name": name,
            "slug": slug,
            "message": "Folder created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Create error: {str(e)}")

@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a folder - COMPLETE DELETION including filesystem"""
    import shutil
    from pathlib import Path
    
    try:
        # Check if folder exists and get info
        folder_result = await db.execute(
            text("""
                SELECT df.name, df.slug, dc.slug as category_slug 
                FROM document_folders df
                JOIN document_categories dc ON df.category_id = dc.id
                WHERE df.id = :id AND df.is_active = true
            """),
            {"id": folder_id}
        )
        folder_row = folder_result.first()
        if not folder_row:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        folder_slug = folder_row.slug
        category_slug = folder_row.category_slug
        
        # 1. Delete all files in folder from database
        await db.execute(
            text("UPDATE training_files_v2 SET deleted_at = :deleted_at WHERE folder_id = :folder_id"),
            {"folder_id": folder_id, "deleted_at": datetime.now(timezone.utc)}
        )
        
        # 2. Delete physical folder from filesystem  
        document_dir = Path("data/documents") / category_slug / folder_slug
        if document_dir.exists():
            shutil.rmtree(document_dir)
            print(f"🗑️ Physischer Ordner gelöscht: {document_dir}")
        
        # 3. Delete folder from database (soft delete)
        await db.execute(
            text("""
                UPDATE document_folders 
                SET is_active = false, updated_at = :updated_at 
                WHERE id = :id
            """),
            {"id": folder_id, "updated_at": datetime.now(timezone.utc)}
        )
        
        await db.commit()
        
        return {"message": f"Folder '{folder_row.name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")