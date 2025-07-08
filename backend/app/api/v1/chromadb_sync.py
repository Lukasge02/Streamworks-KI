"""
ChromaDB Sync API endpoints for StreamWorks-KI
Provides REST API for ChromaDB synchronization operations
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.database import get_db
from app.services.chromadb_sync_service import ChromaDBSyncService
from app.core.responses import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chromadb-sync", tags=["ChromaDB Sync"])


@router.get("/analyze", response_model=ApiResponse)
async def analyze_orphaned_chunks(
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Analyze ChromaDB for orphaned chunks (chunks pointing to non-existent files)
    
    Returns:
        Analysis results showing orphaned chunks and files
    """
    try:
        sync_service = ChromaDBSyncService(db)
        analysis = await sync_service.analyze_orphaned_chunks()
        
        return ApiResponse(
            success=True,
            message=f"Found {analysis['orphaned_chunk_count']} orphaned chunks in {len(analysis['orphaned_files'])} files",
            data=analysis
        )
        
    except Exception as e:
        logger.error(f"❌ ChromaDB analysis failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"ChromaDB analysis failed: {str(e)}"
        )


@router.post("/cleanup", response_model=ApiResponse)
async def cleanup_orphaned_chunks(
    dry_run: bool = Query(True, description="Perform dry run (simulation) instead of actual cleanup"),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Clean up orphaned chunks from ChromaDB
    
    Args:
        dry_run: If True, only simulate cleanup without making changes
        
    Returns:
        Cleanup results
    """
    try:
        sync_service = ChromaDBSyncService(db)
        result = await sync_service.cleanup_orphaned_chunks(dry_run=dry_run)
        
        action_type = "Simulated" if dry_run else "Performed"
        
        return ApiResponse(
            success=True,
            message=f"{action_type} cleanup of {result['cleaned_chunks']} orphaned chunks from {result['cleaned_files']} files",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ ChromaDB cleanup failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"ChromaDB cleanup failed: {str(e)}"
        )


@router.post("/sync-database", response_model=ApiResponse)
async def sync_database_with_filesystem(
    dry_run: bool = Query(True, description="Perform dry run (simulation) instead of actual sync"),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Synchronize database training files with filesystem
    Removes database entries for files that no longer exist
    
    Args:
        dry_run: If True, only simulate sync without making changes
        
    Returns:
        Sync results
    """
    try:
        sync_service = ChromaDBSyncService(db)
        result = await sync_service.sync_database_with_chromadb(dry_run=dry_run)
        
        action_type = "Simulated" if dry_run else "Performed"
        
        return ApiResponse(
            success=True,
            message=f"{action_type} database sync: {result['files_removed']} orphaned entries removed from {result['files_checked']} checked",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ Database sync failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database sync failed: {str(e)}"
        )


@router.get("/full-check", response_model=ApiResponse)
async def full_sync_check(
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Perform comprehensive sync check of filesystem, database, and ChromaDB
    
    Returns:
        Comprehensive sync analysis
    """
    try:
        sync_service = ChromaDBSyncService(db)
        analysis = await sync_service.full_sync_check()
        
        # Count total issues
        total_issues = (
            analysis['sync_issues']['chromadb_orphaned_chunks'] +
            analysis['sync_issues']['database_orphaned_entries'] +
            analysis['sync_issues']['unindexed_files']
        )
        
        return ApiResponse(
            success=True,
            message=f"Full sync check completed - {total_issues} issues found across all systems",
            data=analysis
        )
        
    except Exception as e:
        logger.error(f"❌ Full sync check failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Full sync check failed: {str(e)}"
        )


@router.get("/stats", response_model=ApiResponse)
async def get_sync_stats(
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Get quick sync statistics
    
    Returns:
        Basic sync statistics
    """
    try:
        sync_service = ChromaDBSyncService(db)
        
        # Get quick analysis
        analysis = await sync_service.analyze_orphaned_chunks()
        
        stats = {
            'chromadb_total_chunks': analysis['total_chunks_in_chromadb'],
            'chromadb_unique_sources': analysis['total_unique_sources'],
            'orphaned_chunks': analysis['orphaned_chunk_count'],
            'orphaned_files': len(analysis['orphaned_files']),
            'database_files': analysis['database_files_count'],
            'health_status': 'healthy' if analysis['orphaned_chunk_count'] == 0 else 'needs_attention',
            'last_check': analysis['timestamp']
        }
        
        return ApiResponse(
            success=True,
            message="Sync statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"❌ Sync stats retrieval failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Sync stats retrieval failed: {str(e)}"
        )


@router.post("/repair", response_model=ApiResponse)
async def repair_sync_issues(
    repair_chromadb: bool = Query(True, description="Repair ChromaDB orphaned chunks"),
    repair_database: bool = Query(True, description="Repair database orphaned entries"),
    dry_run: bool = Query(True, description="Perform dry run (simulation) instead of actual repair"),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    Repair all sync issues in one operation
    
    Args:
        repair_chromadb: Whether to clean up ChromaDB orphaned chunks
        repair_database: Whether to remove orphaned database entries
        dry_run: If True, only simulate repair without making changes
        
    Returns:
        Comprehensive repair results
    """
    try:
        sync_service = ChromaDBSyncService(db)
        
        repair_results = {
            'chromadb_cleanup': None,
            'database_sync': None,
            'total_issues_fixed': 0
        }
        
        # Repair ChromaDB if requested
        if repair_chromadb:
            chromadb_result = await sync_service.cleanup_orphaned_chunks(dry_run=dry_run)
            repair_results['chromadb_cleanup'] = chromadb_result
            repair_results['total_issues_fixed'] += chromadb_result['cleaned_chunks']
        
        # Repair database if requested
        if repair_database:
            database_result = await sync_service.sync_database_with_chromadb(dry_run=dry_run)
            repair_results['database_sync'] = database_result
            repair_results['total_issues_fixed'] += database_result['files_removed']
        
        action_type = "Simulated" if dry_run else "Performed"
        
        return ApiResponse(
            success=True,
            message=f"{action_type} comprehensive repair: {repair_results['total_issues_fixed']} issues fixed",
            data=repair_results
        )
        
    except Exception as e:
        logger.error(f"❌ Sync repair failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Sync repair failed: {str(e)}"
        )