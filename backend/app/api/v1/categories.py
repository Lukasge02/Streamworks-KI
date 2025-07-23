import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")

class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    file_count: int = 0
    is_active: bool = True

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Folder name")
    description: Optional[str] = Field(None, max_length=500, description="Folder description")

class FolderResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    category_id: str
    category_name: str
    created_at: datetime
    updated_at: datetime
    file_count: int = 0
    is_active: bool = True

def create_slug(name: str) -> str:
    """Create URL-friendly slug from name"""
    import re
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

# Category Management
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all categories with file counts"""
    try:
        # Get categories with file counts
        query = """
        SELECT 
            dc.id, dc.name, dc.slug, dc.description, 
            dc.created_at, dc.updated_at, dc.is_active,
            COUNT(tf.id) as file_count
        FROM document_categories dc
        LEFT JOIN training_files_v2 tf ON dc.id = tf.category_id 
            AND tf.is_active = true AND tf.deleted_at IS NULL
        WHERE dc.is_active = true OR :include_inactive
        GROUP BY dc.id, dc.name, dc.slug, dc.description, dc.created_at, dc.updated_at, dc.is_active
        ORDER BY dc.name
        """
        
        result = await db.execute(text(query), {"include_inactive": include_inactive})
        categories = []
        
        for row in result:
            categories.append(CategoryResponse(
                id=str(row.id),
                name=row.name,
                slug=row.slug,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
                file_count=row.file_count,
                is_active=row.is_active
            ))
        
        logger.info(f"✅ Retrieved {len(categories)} categories")
        return categories
        
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    try:
        # Create slug
        slug = create_slug(category.name)
        
        # Check if slug already exists
        existing = await db.execute(
            text("SELECT id FROM document_categories WHERE slug = :slug"),
            {"slug": slug}
        )
        if existing.scalar():
            raise HTTPException(
                status_code=409,
                detail=f"Category with slug '{slug}' already exists"
            )
        
        # Create category
        category_id = str(uuid.uuid4())
        await db.execute(
            text("""
            INSERT INTO document_categories (id, name, slug, description, created_at, updated_at, is_active)
            VALUES (:id, :name, :slug, :description, NOW(), NOW(), true)
            """),
            {
                "id": category_id,
                "name": category.name,
                "slug": slug,
                "description": category.description
            }
        )
        
        await db.commit()
        
        # Return created category
        result = await db.execute(
            text("SELECT * FROM document_categories WHERE id = :id"),
            {"id": category_id}
        )
        row = result.first()
        
        response = CategoryResponse(
            id=str(row.id),
            name=row.name,
            slug=row.slug,
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
            file_count=0,
            is_active=row.is_active
        )
        
        logger.info(f"✅ Created category: {category.name} ({slug})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create category: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing category"""
    try:
        # Check if category exists
        existing = await db.execute(
            text("SELECT * FROM document_categories WHERE id = :id"),
            {"id": category_id}
        )
        existing_row = existing.first()
        if not existing_row:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Prepare update data
        update_data = {"id": category_id}
        update_fields = []
        
        if category.name is not None:
            slug = create_slug(category.name)
            # Check if new slug conflicts with other categories
            slug_check = await db.execute(
                text("SELECT id FROM document_categories WHERE slug = :slug AND id != :id"),
                {"slug": slug, "id": category_id}
            )
            if slug_check.scalar():
                raise HTTPException(
                    status_code=409,
                    detail=f"Category with slug '{slug}' already exists"
                )
            update_data["name"] = category.name
            update_data["slug"] = slug
            update_fields.extend(["name = :name", "slug = :slug"])
        
        if category.description is not None:
            update_data["description"] = category.description
            update_fields.append("description = :description")
        
        if update_fields:
            update_fields.append("updated_at = NOW()")
            query = f"UPDATE document_categories SET {', '.join(update_fields)} WHERE id = :id"
            await db.execute(text(query), update_data)
            await db.commit()
        
        # Return updated category
        result = await db.execute(
            text("""
            SELECT dc.*, COUNT(tf.id) as file_count
            FROM document_categories dc
            LEFT JOIN training_files_v2 tf ON dc.id = tf.category_id 
                AND tf.is_active = true AND tf.deleted_at IS NULL
            WHERE dc.id = :id
            GROUP BY dc.id, dc.name, dc.slug, dc.description, dc.created_at, dc.updated_at, dc.is_active
            """),
            {"id": category_id}
        )
        row = result.first()
        
        response = CategoryResponse(
            id=str(row.id),
            name=row.name,
            slug=row.slug,
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
            file_count=row.file_count,
            is_active=row.is_active
        )
        
        logger.info(f"✅ Updated category: {category_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to update category: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update category: {str(e)}")

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category (soft delete unless force=True)"""
    try:
        # Check if category exists
        existing = await db.execute(
            text("SELECT * FROM document_categories WHERE id = :id"),
            {"id": category_id}
        )
        if not existing.first():
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if category has files
        file_count = await db.execute(
            text("SELECT COUNT(*) FROM training_files_v2 WHERE category_id = :id AND is_active = true"),
            {"id": category_id}
        )
        file_count = file_count.scalar()
        
        if file_count > 0 and not force:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete category with {file_count} files. Use force=True to delete anyway."
            )
        
        if force:
            # Hard delete: Remove files and category
            await db.execute(
                text("DELETE FROM training_files_v2 WHERE category_id = :id"),
                {"id": category_id}
            )
            await db.execute(
                text("DELETE FROM document_folders WHERE category_id = :id"),
                {"id": category_id}
            )
            await db.execute(
                text("DELETE FROM document_categories WHERE id = :id"),
                {"id": category_id}
            )
        else:
            # Soft delete: Mark as inactive
            await db.execute(
                text("UPDATE document_categories SET is_active = false, updated_at = NOW() WHERE id = :id"),
                {"id": category_id}
            )
        
        await db.commit()
        
        logger.info(f"✅ {'Hard' if force else 'Soft'} deleted category: {category_id}")
        return {"message": f"Category {'permanently deleted' if force else 'deactivated'} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete category: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")

# Folder Management
@router.get("/categories/{category_id}/folders", response_model=List[FolderResponse])
async def get_folders(
    category_id: str,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all folders for a category"""
    try:
        query = """
        SELECT 
            df.id, df.name, df.slug, df.description, 
            df.category_id, dc.name as category_name,
            df.created_at, df.updated_at, df.is_active,
            COUNT(tf.id) as file_count
        FROM document_folders df
        JOIN document_categories dc ON df.category_id = dc.id
        LEFT JOIN training_files_v2 tf ON df.id = tf.folder_id 
            AND tf.is_active = true AND tf.deleted_at IS NULL
        WHERE df.category_id = :category_id 
            AND (df.is_active = true OR :include_inactive)
        GROUP BY df.id, df.name, df.slug, df.description, df.category_id, 
                 dc.name, df.created_at, df.updated_at, df.is_active
        ORDER BY df.name
        """
        
        result = await db.execute(text(query), {
            "category_id": category_id,
            "include_inactive": include_inactive
        })
        folders = []
        
        for row in result:
            folders.append(FolderResponse(
                id=str(row.id),
                name=row.name,
                slug=row.slug,
                description=row.description,
                category_id=str(row.category_id),
                category_name=row.category_name,
                created_at=row.created_at,
                updated_at=row.updated_at,
                file_count=row.file_count,
                is_active=row.is_active
            ))
        
        logger.info(f"✅ Retrieved {len(folders)} folders for category {category_id}")
        return folders
        
    except Exception as e:
        logger.error(f"❌ Failed to get folders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve folders: {str(e)}")

@router.post("/categories/{category_id}/folders", response_model=FolderResponse)
async def create_folder(
    category_id: str,
    folder: FolderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder in a category"""
    try:
        # Check if category exists
        category_check = await db.execute(
            text("SELECT name FROM document_categories WHERE id = :id"),
            {"id": category_id}
        )
        category_row = category_check.first()
        if not category_row:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Create slug
        slug = create_slug(folder.name)
        
        # Check if slug already exists in this category
        existing = await db.execute(
            text("SELECT id FROM document_folders WHERE slug = :slug AND category_id = :category_id"),
            {"slug": slug, "category_id": category_id}
        )
        if existing.scalar():
            raise HTTPException(
                status_code=409,
                detail=f"Folder with slug '{slug}' already exists in this category"
            )
        
        # Create folder
        folder_id = str(uuid.uuid4())
        await db.execute(
            text("""
            INSERT INTO document_folders (id, name, slug, description, category_id, created_at, updated_at, is_active)
            VALUES (:id, :name, :slug, :description, :category_id, NOW(), NOW(), true)
            """),
            {
                "id": folder_id,
                "name": folder.name,
                "slug": slug,
                "description": folder.description,
                "category_id": category_id
            }
        )
        
        await db.commit()
        
        # Return created folder
        response = FolderResponse(
            id=folder_id,
            name=folder.name,
            slug=slug,
            description=folder.description,
            category_id=category_id,
            category_name=category_row.name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            file_count=0,
            is_active=True
        )
        
        logger.info(f"✅ Created folder: {folder.name} ({slug}) in category {category_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create folder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")