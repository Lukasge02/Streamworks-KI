"""
Folder Management API Router
Enterprise-grade REST API for folder operations
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from database import get_async_session
from schemas.core import (
    FolderCreate, FolderUpdate, FolderResponse, FolderTree,
    FolderList, FolderStats
)
from services.folder_service import FolderService

router = APIRouter(prefix="/api/v1/folders", tags=["folders"])


@router.post("/", response_model=FolderResponse, status_code=201)
async def create_folder(
    folder_data: FolderCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new folder
    
    - **name**: Folder name (required)
    - **description**: Optional description
    - **parent_id**: Optional parent folder ID for hierarchy
    """
    try:
        folder = await FolderService.create_folder(db, folder_data)
        
        return FolderResponse(
            id=folder.id,
            name=folder.name,
            description=folder.description,
            parent_id=folder.parent_id,
            path=folder.path,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            document_count=0,
            children_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")


@router.get("/")
async def get_folders(
    parent_id: Optional[UUID] = Query(None, description="Filter by parent folder ID"),
    include_counts: bool = Query(True, description="Include document and children counts"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get list of folders

    - **parent_id**: Filter by parent folder (null for root folders)
    - **include_counts**: Include document and children counts
    """
    try:
        folders = await FolderService.get_folders_list(
            db,
            parent_id=parent_id,
            include_document_count=include_counts
        )

        # Serialize response completely before sending
        response_data = []
        for folder in folders:
            response_data.append({
                "id": str(folder.id),
                "name": folder.name,
                "description": folder.description,
                "parent_id": str(folder.parent_id) if folder.parent_id else None,
                "path": folder.path,
                "created_at": folder.created_at.isoformat(),
                "updated_at": folder.updated_at.isoformat(),
                "document_count": folder.document_count if hasattr(folder, 'document_count') else 0,
                "children_count": folder.children_count if hasattr(folder, 'children_count') else 0
            })

        # Return as explicit JSONResponse with proper headers
        response_json = json.dumps(response_data, ensure_ascii=False)
        return JSONResponse(
            content=json.loads(response_json),
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(response_json.encode('utf-8')))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folders: {str(e)}")


@router.get("/tree")
async def get_folder_tree(
    root_id: Optional[UUID] = Query(None, description="Root folder ID (null for all roots)"),
    max_depth: int = Query(10, ge=1, le=20, description="Maximum tree depth"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get hierarchical folder tree

    - **root_id**: Root folder ID (null for all root folders)
    - **max_depth**: Maximum depth to traverse (1-20)
    """
    try:
        tree = await FolderService.get_folder_tree(db, root_id, max_depth)

        # Convert tree to serializable format
        def serialize_folder_tree(folder_node):
            return {
                "id": str(folder_node.id),
                "name": folder_node.name,
                "description": folder_node.description,
                "parent_id": str(folder_node.parent_id) if folder_node.parent_id else None,
                "path": folder_node.path,
                "created_at": folder_node.created_at.isoformat(),
                "updated_at": folder_node.updated_at.isoformat(),
                "document_count": folder_node.document_count if hasattr(folder_node, 'document_count') else 0,
                "children_count": folder_node.children_count if hasattr(folder_node, 'children_count') else 0,
                "children": [serialize_folder_tree(child) for child in (folder_node.children or [])]
            }

        # Serialize complete tree
        response_data = []
        for root_folder in tree:
            response_data.append(serialize_folder_tree(root_folder))

        # Return as explicit JSONResponse with proper headers
        response_json = json.dumps(response_data, ensure_ascii=False)
        return JSONResponse(
            content=json.loads(response_json),
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(response_json.encode('utf-8')))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folder tree: {str(e)}")


@router.get("/search", response_model=List[FolderResponse])
async def search_folders(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Search folders by name and description
    
    - **q**: Search query (minimum 1 character)
    - **limit**: Maximum number of results (1-100)
    """
    try:
        folders = await FolderService.search_folders(db, q, limit)
        return folders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get folder by ID
    
    - **folder_id**: Folder UUID
    """
    try:
        folder = await FolderService.get_folder_by_id(db, folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Get counts
        from services.document import DocumentService
        from sqlalchemy import select, func
        from models.core import Document, Folder as FolderModel
        
        # Document count
        doc_query = select(func.count(Document.id)).where(Document.folder_id == folder_id)
        doc_result = await db.execute(doc_query)
        document_count = doc_result.scalar() or 0
        
        # Children count
        child_query = select(func.count(FolderModel.id)).where(FolderModel.parent_id == folder_id)
        child_result = await db.execute(child_query)
        children_count = child_result.scalar() or 0
        
        return FolderResponse(
            id=folder.id,
            name=folder.name,
            description=folder.description,
            parent_id=folder.parent_id,
            path=folder.path,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            document_count=document_count,
            children_count=children_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folder: {str(e)}")


@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: UUID,
    folder_data: FolderUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update folder
    
    - **folder_id**: Folder UUID
    - **name**: New folder name (optional)
    - **description**: New description (optional)
    - **parent_id**: New parent folder ID (optional)
    """
    try:
        folder = await FolderService.update_folder(db, folder_id, folder_data)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        return FolderResponse(
            id=folder.id,
            name=folder.name,
            description=folder.description,
            parent_id=folder.parent_id,
            path=folder.path,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            document_count=0,  # Skip count for update response
            children_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update folder: {str(e)}")


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: UUID,
    force: bool = Query(False, description="Force delete even if folder contains items"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete folder
    
    - **folder_id**: Folder UUID
    - **force**: Force delete even if folder contains documents or subfolders
    """
    try:
        success = await FolderService.delete_folder(db, folder_id, force=force)
        if not success:
            raise HTTPException(status_code=404, detail="Folder not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete folder: {str(e)}")


@router.get("/{folder_id}/stats", response_model=dict)
async def get_folder_stats(
    folder_id: UUID,
    recursive: bool = Query(False, description="Include statistics from all subfolders"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get folder statistics
    
    - **folder_id**: Folder UUID
    - **recursive**: Include statistics from all subfolders
    """
    try:
        folder = await FolderService.get_folder_by_id(db, folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Basic stats implementation
        from sqlalchemy import select, func
        from models.core import Document, Folder as FolderModel
        
        # Document stats
        doc_query = select(
            func.count(Document.id).label('count'),
            func.sum(Document.file_size).label('total_size')
        ).where(Document.folder_id == folder_id)
        
        doc_result = await db.execute(doc_query)
        doc_stats = doc_result.one()
        
        # Subfolder count
        child_query = select(func.count(FolderModel.id)).where(FolderModel.parent_id == folder_id)
        child_result = await db.execute(child_query)
        subfolder_count = child_result.scalar() or 0
        
        return {
            "folder_id": folder_id,
            "folder_name": folder.name,
            "document_count": doc_stats.count or 0,
            "total_size_bytes": doc_stats.total_size or 0,
            "subfolder_count": subfolder_count,
            "recursive": recursive
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folder stats: {str(e)}")