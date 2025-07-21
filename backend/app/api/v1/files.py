"""
Simple Files API - Bulletproof Implementation
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
import logging
import os

from ...models.database import get_db
from ...services.file_manager import file_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class FileResponse(BaseModel):
    id: str
    filename: str
    category_slug: str
    category_name: str
    folder_slug: Optional[str] = None
    folder_name: Optional[str] = None
    file_size: int
    upload_date: str
    status: str

class CategoryResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    folder_count: int = 0

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all categories"""
    try:
        result = await db.execute(text("""
            SELECT 
                dc.id, dc.slug, dc.name, dc.description,
                COUNT(df.id) as folder_count
            FROM document_categories dc
            LEFT JOIN document_folders df ON dc.id = df.category_id AND df.is_active = 1
            WHERE dc.is_active = 1
            GROUP BY dc.id, dc.slug, dc.name, dc.description
            ORDER BY dc.name
        """))
        
        categories = []
        for row in result:
            categories.append(CategoryResponse(
                id=str(row.id),
                slug=row.slug,
                name=row.name,
                description=row.description,
                folder_count=row.folder_count or 0
            ))
        
        return categories
        
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(500, "Failed to retrieve categories")

@router.get("/files")
async def get_files(
    category_slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all files"""
    try:
        files = await file_manager.get_files(db, category_slug)
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to get files: {e}")
        raise HTTPException(500, "Failed to retrieve files")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category_slug: str = Form(...),
    folder_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file"""
    try:
        result = await file_manager.upload_file(file, category_slug, folder_id, db)
        return result
        
    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a file"""
    try:
        result = await file_manager.delete_file(file_id, db)
        return result
        
    except Exception as e:
        logger.error(f"❌ File deletion failed: {e}")
        raise HTTPException(500, f"Deletion failed: {str(e)}")

@router.post("/files/{file_id}/index")
async def index_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """Index a file for RAG"""
    try:
        # Get file info
        result = await db.execute(
            text("SELECT file_path, display_name, category FROM training_files WHERE id = :id"),
            {"id": file_id}
        )
        file_row = result.first()
        
        if not file_row:
            raise HTTPException(404, "File not found")
        
        # Read file content
        file_path = file_row.file_path
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(400, "File not found on disk")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple chunking (split by paragraphs)
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        
        if not chunks:
            chunks = [content]  # Use entire content if no paragraphs
        
        # Add to RAG service
        from ...services.rag_service import rag_service
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{file_id}_chunk_{i}",
                "content": chunk,
                "metadata": {
                    "source": file_row.display_name,
                    "file_id": file_id,
                    "category": file_row.category or "unknown",
                    "chunk_index": i
                }
            })
        
        # Add documents to RAG
        added_count = await rag_service.add_documents(documents)
        
        # Update file status
        await db.execute(
            text("UPDATE training_files SET status = 'indexed', chunk_count = :count WHERE id = :id"),
            {"id": file_id, "count": len(chunks)}
        )
        await db.commit()
        
        logger.info(f"✅ File indexed: {file_row.display_name} ({len(chunks)} chunks)")
        
        return {
            "message": "File indexed successfully",
            "file_id": file_id,
            "filename": file_row.display_name,
            "chunks_created": len(chunks),
            "documents_added": added_count
        }
        
    except Exception as e:
        logger.error(f"❌ File indexing failed: {e}")
        raise HTTPException(500, f"Indexing failed: {str(e)}")