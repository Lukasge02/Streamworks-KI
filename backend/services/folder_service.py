"""
Folder Service for Hierarchical Document Organization
Enterprise-grade folder management with path optimization
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.core import Folder, Document
from schemas.core import FolderCreate, FolderUpdate, FolderResponse, FolderTree

logger = logging.getLogger(__name__)


class FolderService:
    """
    Service for folder CRUD operations with hierarchical support
    Handles folder trees, path management, and document counting
    """

    @staticmethod
    async def create_folder(
        db: AsyncSession, 
        folder_data: FolderCreate
    ) -> Folder:
        """
        Create a new folder with automatic path generation
        
        Args:
            db: Database session
            folder_data: Folder creation data
            
        Returns:
            Created folder with generated path
        """
        try:
            # Generate path based on parent
            path = []
            if folder_data.parent_id:
                parent = await FolderService.get_folder_by_id(db, folder_data.parent_id)
                if not parent:
                    raise ValueError(f"Parent folder {folder_data.parent_id} not found")
                path = parent.path + [folder_data.name]
            else:
                path = [folder_data.name]

            # Create folder
            folder = Folder(
                name=folder_data.name,
                description=folder_data.description,
                parent_id=folder_data.parent_id,
                path=path
            )
            
            db.add(folder)
            await db.flush()
            await db.refresh(folder)
            
            logger.info(f"Created folder: {folder.name} (path: {'/'.join(path)})")
            return folder
            
        except Exception as e:
            logger.error(f"Failed to create folder: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def get_folder_by_id(
        db: AsyncSession, 
        folder_id: UUID,
        include_documents: bool = False,
        include_children: bool = False
    ) -> Optional[Folder]:
        """
        Get folder by ID with optional relationships
        
        Args:
            db: Database session
            folder_id: Folder UUID
            include_documents: Include folder documents
            include_children: Include child folders
            
        Returns:
            Folder or None if not found
        """
        try:
            query = select(Folder).where(Folder.id == folder_id)
            
            if include_documents or include_children:
                options = []
                if include_documents:
                    options.append(selectinload(Folder.documents))
                if include_children:
                    options.append(selectinload(Folder.children))
                query = query.options(*options)
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get folder {folder_id}: {str(e)}")
            return None

    @staticmethod
    async def get_folders_list(
        db: AsyncSession,
        parent_id: Optional[UUID] = None,
        include_document_count: bool = True
    ) -> List[FolderResponse]:
        """
        Get list of folders with optional parent filtering
        
        Args:
            db: Database session
            parent_id: Filter by parent folder (None for root folders)
            include_document_count: Include document counts
            
        Returns:
            List of folder responses with metadata
        """
        try:
            # Base query
            query = select(Folder)
            if parent_id is not None:
                query = query.where(Folder.parent_id == parent_id)
            else:
                query = query.where(Folder.parent_id.is_(None))
            
            query = query.order_by(Folder.name)
            
            result = await db.execute(query)
            folders = result.scalars().all()
            
            # Build response with counts
            folder_responses = []
            for folder in folders:
                # Get document count if requested
                document_count = 0
                children_count = 0
                
                if include_document_count:
                    # Count documents in this folder
                    doc_query = select(func.count(Document.id)).where(
                        Document.folder_id == folder.id
                    )
                    doc_result = await db.execute(doc_query)
                    document_count = doc_result.scalar() or 0
                    
                    # Count child folders
                    child_query = select(func.count(Folder.id)).where(
                        Folder.parent_id == folder.id
                    )
                    child_result = await db.execute(child_query)
                    children_count = child_result.scalar() or 0
                
                folder_response = FolderResponse(
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
                folder_responses.append(folder_response)
            
            return folder_responses
            
        except Exception as e:
            logger.error(f"Failed to get folders list: {str(e)}")
            return []

    @staticmethod
    async def get_folder_tree(
        db: AsyncSession,
        root_id: Optional[UUID] = None,
        max_depth: int = 10
    ) -> List[FolderTree]:
        """
        Get hierarchical folder tree structure
        
        Args:
            db: Database session
            root_id: Root folder ID (None for all root folders)
            max_depth: Maximum depth to traverse
            
        Returns:
            Nested folder tree structure
        """
        try:
            async def build_tree(parent_id: Optional[UUID], depth: int = 0) -> List[FolderTree]:
                if depth >= max_depth:
                    return []
                
                # Get folders at current level
                folders = await FolderService.get_folders_list(
                    db, parent_id=parent_id, include_document_count=True
                )
                
                tree = []
                for folder in folders:
                    # Get children recursively
                    children = await build_tree(folder.id, depth + 1)
                    
                    folder_tree = FolderTree(
                        **folder.dict(),
                        children=children,
                        documents=[]  # Documents loaded separately if needed
                    )
                    tree.append(folder_tree)
                
                return tree
            
            return await build_tree(root_id)
            
        except Exception as e:
            logger.error(f"Failed to build folder tree: {str(e)}")
            return []

    @staticmethod
    async def update_folder(
        db: AsyncSession, 
        folder_id: UUID, 
        folder_data: FolderUpdate
    ) -> Optional[Folder]:
        """
        Update folder with path regeneration if parent changed
        
        Args:
            db: Database session
            folder_id: Folder ID to update
            folder_data: Update data
            
        Returns:
            Updated folder or None if not found
        """
        try:
            folder = await FolderService.get_folder_by_id(db, folder_id)
            if not folder:
                return None
            
            # Update fields
            if folder_data.name is not None:
                folder.name = folder_data.name
            if folder_data.description is not None:
                folder.description = folder_data.description
            
            # Handle parent change
            if folder_data.parent_id is not None:
                # Validate new parent exists and isn't a descendant
                if folder_data.parent_id != folder.parent_id:
                    if folder_data.parent_id:
                        parent = await FolderService.get_folder_by_id(db, folder_data.parent_id)
                        if not parent:
                            raise ValueError(f"Parent folder {folder_data.parent_id} not found")
                        
                        # Check for circular reference
                        if str(folder.id) in [str(p) for p in parent.path if isinstance(p, (str, UUID))]:
                            raise ValueError("Cannot move folder to its own descendant")
                    
                    folder.parent_id = folder_data.parent_id
                    
                    # Regenerate path
                    if folder.parent_id:
                        parent = await FolderService.get_folder_by_id(db, folder.parent_id)
                        folder.path = parent.path + [folder.name]
                    else:
                        folder.path = [folder.name]
                    
                    # Update all descendant paths
                    await FolderService._update_descendant_paths(db, folder)
            
            await db.flush()
            await db.refresh(folder)
            
            logger.info(f"Updated folder: {folder.name}")
            return folder
            
        except Exception as e:
            logger.error(f"Failed to update folder {folder_id}: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_folder(
        db: AsyncSession, 
        folder_id: UUID,
        force: bool = False
    ) -> bool:
        """
        Delete folder with optional cascade
        
        Args:
            db: Database session
            folder_id: Folder ID to delete
            force: Delete even if folder contains documents/subfolders
            
        Returns:
            True if deleted successfully
        """
        try:
            folder = await FolderService.get_folder_by_id(
                db, folder_id, include_documents=True, include_children=True
            )
            if not folder:
                return False
            
            # Check for documents/children if not forcing
            if not force:
                if folder.documents:
                    raise ValueError(f"Folder contains {len(folder.documents)} documents")
                if folder.children:
                    raise ValueError(f"Folder contains {len(folder.children)} subfolders")
            
            # Delete folder (cascade will handle children and documents)
            await db.delete(folder)
            await db.flush()
            
            logger.info(f"Deleted folder: {folder.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete folder {folder_id}: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def search_folders(
        db: AsyncSession,
        query: str,
        limit: int = 50
    ) -> List[FolderResponse]:
        """
        Search folders by name and description
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching folders
        """
        try:
            search_pattern = f"%{query}%"
            db_query = select(Folder).where(
                or_(
                    Folder.name.ilike(search_pattern),
                    Folder.description.ilike(search_pattern)
                )
            ).limit(limit).order_by(Folder.name)
            
            result = await db.execute(db_query)
            folders = result.scalars().all()
            
            # Convert to response format
            responses = []
            for folder in folders:
                # Get document count
                doc_query = select(func.count(Document.id)).where(
                    Document.folder_id == folder.id
                )
                doc_result = await db.execute(doc_query)
                document_count = doc_result.scalar() or 0
                
                response = FolderResponse(
                    id=folder.id,
                    name=folder.name,
                    description=folder.description,
                    parent_id=folder.parent_id,
                    path=folder.path,
                    created_at=folder.created_at,
                    updated_at=folder.updated_at,
                    document_count=document_count,
                    children_count=0  # Skip for search results
                )
                responses.append(response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to search folders: {str(e)}")
            return []

    @staticmethod
    async def _update_descendant_paths(db: AsyncSession, folder: Folder):
        """Update paths for all descendant folders"""
        try:
            children_query = select(Folder).where(Folder.parent_id == folder.id)
            result = await db.execute(children_query)
            children = result.scalars().all()
            
            for child in children:
                child.path = folder.path + [child.name]
                await FolderService._update_descendant_paths(db, child)
                
        except Exception as e:
            logger.error(f"Failed to update descendant paths: {str(e)}")
            raise