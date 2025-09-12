"""
Maintenance Service for StreamWorks
Handles cleanup operations, consistency checks, and system maintenance tasks
"""

import logging
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.core import Document, DocumentChunk
from services.vectorstore import VectorStoreService
from services.document_chunk_service import DocumentChunkService
from services.di_container import get_service

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for system maintenance and cleanup operations"""
    
    def __init__(self):
        self.chunk_service = DocumentChunkService()
    
    async def check_vector_consistency(
        self, 
        db: AsyncSession,
        fix_issues: bool = False
    ) -> Dict[str, Any]:
        """
        Check consistency between database chunks and vector store
        
        Args:
            db: Database session
            fix_issues: Whether to automatically fix found issues
            
        Returns:
            Dictionary with consistency report
        """
        logger.info("Starting vector consistency check...")
        
        try:
            # Get vector store service
            vectorstore: VectorStoreService = await get_service("vectorstore")
            
            # Get all document IDs from database
            db_doc_query = select(Document.id).distinct()
            db_doc_result = await db.execute(db_doc_query)
            db_document_ids = {str(doc_id) for doc_id in db_doc_result.scalars().all()}
            
            # Get all chunk IDs from database  
            db_chunk_query = select(DocumentChunk.id).distinct()
            db_chunk_result = await db.execute(db_chunk_query)
            db_chunk_ids = {str(chunk_id) for chunk_id in db_chunk_result.scalars().all()}
            
            # Get all documents from vector store
            vector_docs = await vectorstore.get_all_documents()
            vector_document_ids = {doc['id'] for doc in vector_docs}
            
            # Get all chunks from vector store (by querying with empty filter)
            try:
                # ChromaDB: get all chunks
                if vectorstore.collection:
                    vector_results = vectorstore.collection.get(include=['metadatas'])
                    vector_chunk_ids = set(vector_results['ids'])
                    vector_chunk_doc_ids = {meta.get('doc_id') for meta in vector_results['metadatas']}
                else:
                    vector_chunk_ids = set()
                    vector_chunk_doc_ids = set()
            except Exception as e:
                logger.error(f"Failed to get vector chunks: {str(e)}")
                vector_chunk_ids = set()
                vector_chunk_doc_ids = set()
            
            # Find inconsistencies
            orphaned_vector_docs = vector_document_ids - db_document_ids
            missing_vector_docs = db_document_ids - vector_document_ids
            orphaned_vector_chunks = vector_chunk_ids - db_chunk_ids
            
            # Find vector chunks pointing to non-existent documents
            orphaned_doc_references = vector_chunk_doc_ids - db_document_ids
            
            # Count stats
            stats = {
                "check_timestamp": datetime.utcnow().isoformat(),
                "database_documents": len(db_document_ids),
                "database_chunks": len(db_chunk_ids),
                "vector_documents": len(vector_document_ids),
                "vector_chunks": len(vector_chunk_ids),
                "orphaned_vector_documents": len(orphaned_vector_docs),
                "missing_vector_documents": len(missing_vector_docs),
                "orphaned_vector_chunks": len(orphaned_vector_chunks),
                "orphaned_document_references": len(orphaned_doc_references),
                "consistency_issues": len(orphaned_vector_docs) + len(orphaned_vector_chunks) + len(orphaned_doc_references) > 0
            }
            
            # Detailed issues
            issues = {
                "orphaned_vector_documents": list(orphaned_vector_docs),
                "missing_vector_documents": list(missing_vector_docs),
                "orphaned_vector_chunks": list(orphaned_vector_chunks),
                "orphaned_document_references": list(orphaned_doc_references)
            }
            
            logger.info(f"Consistency check complete: {stats['vector_chunks']} vector chunks, {stats['orphaned_vector_chunks']} orphaned")
            
            # Fix issues if requested
            fixed_issues = {}
            if fix_issues and stats['consistency_issues']:
                fixed_issues = await self._fix_vector_inconsistencies(
                    vectorstore, 
                    orphaned_vector_docs, 
                    orphaned_vector_chunks,
                    orphaned_doc_references
                )
            
            return {
                "stats": stats,
                "issues": issues,
                "fixes_applied": fixed_issues if fix_issues else None
            }
            
        except Exception as e:
            logger.error(f"Vector consistency check failed: {str(e)}")
            raise
    
    async def _fix_vector_inconsistencies(
        self,
        vectorstore: VectorStoreService,
        orphaned_docs: Set[str],
        orphaned_chunks: Set[str],
        orphaned_doc_refs: Set[str]
    ) -> Dict[str, Any]:
        """Fix vector store inconsistencies"""
        
        fixed = {
            "deleted_orphaned_documents": 0,
            "deleted_orphaned_chunks": 0,
            "errors": []
        }
        
        try:
            # Delete orphaned document vectors
            for doc_id in orphaned_docs:
                try:
                    await vectorstore.delete_document(doc_id)
                    fixed["deleted_orphaned_documents"] += 1
                    logger.info(f"Deleted orphaned document vectors: {doc_id}")
                except Exception as e:
                    error_msg = f"Failed to delete orphaned document {doc_id}: {str(e)}"
                    logger.error(error_msg)
                    fixed["errors"].append(error_msg)
            
            # Delete orphaned chunks by ID
            if orphaned_chunks and vectorstore.collection:
                try:
                    # Batch delete orphaned chunks
                    batch_size = 100
                    orphaned_list = list(orphaned_chunks)
                    
                    for i in range(0, len(orphaned_list), batch_size):
                        batch = orphaned_list[i:i + batch_size]
                        vectorstore.collection.delete(ids=batch)
                        fixed["deleted_orphaned_chunks"] += len(batch)
                        logger.info(f"Deleted {len(batch)} orphaned vector chunks")
                        
                except Exception as e:
                    error_msg = f"Failed to delete orphaned chunks: {str(e)}"
                    logger.error(error_msg)
                    fixed["errors"].append(error_msg)
            
            # Delete chunks with orphaned document references
            if orphaned_doc_refs and vectorstore.collection:
                try:
                    for doc_id in orphaned_doc_refs:
                        results = vectorstore.collection.get(where={"doc_id": doc_id})
                        if results['ids']:
                            vectorstore.collection.delete(ids=results['ids'])
                            fixed["deleted_orphaned_chunks"] += len(results['ids'])
                            logger.info(f"Deleted {len(results['ids'])} chunks with orphaned doc reference: {doc_id}")
                except Exception as e:
                    error_msg = f"Failed to delete chunks with orphaned doc refs: {str(e)}"
                    logger.error(error_msg)
                    fixed["errors"].append(error_msg)
            
            logger.info(f"Cleanup completed: {fixed['deleted_orphaned_documents']} docs, {fixed['deleted_orphaned_chunks']} chunks")
            return fixed
            
        except Exception as e:
            logger.error(f"Failed to fix vector inconsistencies: {str(e)}")
            fixed["errors"].append(str(e))
            return fixed
    
    async def cleanup_orphaned_database_chunks(
        self, 
        db: AsyncSession,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up document chunks without valid document references
        
        Args:
            db: Database session
            dry_run: If True, only report issues without fixing
            
        Returns:
            Cleanup report
        """
        logger.info(f"Starting database chunk cleanup (dry_run={dry_run})")
        
        try:
            if dry_run:
                # Find orphaned chunks
                orphan_query = select(DocumentChunk).where(
                    ~DocumentChunk.document_id.in_(
                        select(Document.id)
                    )
                )
                result = await db.execute(orphan_query)
                orphaned_chunks = result.scalars().all()
                
                report = {
                    "dry_run": True,
                    "orphaned_chunks_found": len(orphaned_chunks),
                    "orphaned_chunk_ids": [str(chunk.id) for chunk in orphaned_chunks],
                    "total_size_bytes": sum(chunk.char_count or 0 for chunk in orphaned_chunks)
                }
                
                logger.info(f"Found {len(orphaned_chunks)} orphaned database chunks")
                return report
            else:
                # Actually clean up
                cleaned_count = await self.chunk_service.cleanup_orphaned_chunks(db)
                
                report = {
                    "dry_run": False,
                    "cleaned_chunks": cleaned_count
                }
                
                logger.info(f"Cleaned up {cleaned_count} orphaned database chunks")
                return report
                
        except Exception as e:
            logger.error(f"Database chunk cleanup failed: {str(e)}")
            raise
    
    async def get_system_health_report(
        self, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get comprehensive system health report
        
        Returns:
            System health metrics and statistics
        """
        logger.info("Generating system health report")
        
        try:
            # Database statistics
            doc_count_query = select(func.count(Document.id))
            doc_result = await db.execute(doc_count_query)
            document_count = doc_result.scalar() or 0
            
            chunk_count_query = select(func.count(DocumentChunk.id))
            chunk_result = await db.execute(chunk_count_query)
            chunk_count = chunk_result.scalar() or 0
            
            # Vector store statistics
            vectorstore: VectorStoreService = await get_service("vectorstore")
            vector_stats = await vectorstore.get_stats()
            
            # Consistency check
            consistency_report = await self.check_vector_consistency(db, fix_issues=False)
            
            # Compile health report
            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "database": {
                    "documents": document_count,
                    "chunks": chunk_count
                },
                "vector_store": vector_stats,
                "consistency": consistency_report["stats"],
                "health_status": "healthy" if not consistency_report["stats"]["consistency_issues"] else "issues_detected",
                "recommendations": []
            }
            
            # Add recommendations based on findings
            if consistency_report["stats"]["orphaned_vector_chunks"] > 0:
                health_report["recommendations"].append(
                    f"Clean up {consistency_report['stats']['orphaned_vector_chunks']} orphaned vector chunks"
                )
            
            if consistency_report["stats"]["orphaned_vector_documents"] > 0:
                health_report["recommendations"].append(
                    f"Remove {consistency_report['stats']['orphaned_vector_documents']} orphaned vector documents"
                )
            
            logger.info(f"Health report generated: {health_report['health_status']}")
            return health_report
            
        except Exception as e:
            logger.error(f"Failed to generate health report: {str(e)}")
            raise
    
    async def full_system_cleanup(
        self, 
        db: AsyncSession,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive system cleanup
        
        Args:
            db: Database session
            dry_run: If True, only report what would be cleaned
            
        Returns:
            Comprehensive cleanup report
        """
        logger.info(f"Starting full system cleanup (dry_run={dry_run})")
        
        try:
            # Step 1: Database chunk cleanup
            db_cleanup = await self.cleanup_orphaned_database_chunks(db, dry_run)
            
            # Step 2: Vector consistency check and cleanup
            vector_cleanup = await self.check_vector_consistency(db, fix_issues=not dry_run)
            
            # Compile final report
            cleanup_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "dry_run": dry_run,
                "database_cleanup": db_cleanup,
                "vector_cleanup": vector_cleanup,
                "summary": {
                    "total_issues_found": (
                        db_cleanup.get("orphaned_chunks_found", 0) + 
                        vector_cleanup["stats"]["orphaned_vector_chunks"] +
                        vector_cleanup["stats"]["orphaned_vector_documents"]
                    ),
                    "issues_fixed": 0 if dry_run else (
                        vector_cleanup.get("fixes_applied", {}).get("deleted_orphaned_chunks", 0) +
                        vector_cleanup.get("fixes_applied", {}).get("deleted_orphaned_documents", 0) +
                        db_cleanup.get("cleaned_chunks", 0)
                    )
                }
            }
            
            logger.info(f"Full cleanup completed: {cleanup_report['summary']['total_issues_found']} issues found")
            return cleanup_report
            
        except Exception as e:
            logger.error(f"Full system cleanup failed: {str(e)}")
            raise