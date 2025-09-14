"""
Maintenance Service for StreamWorks
Simplified for LlamaIndex-only architecture
Handles cleanup operations, consistency checks, and system maintenance tasks
"""

import logging
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.core import Document, DocumentChunk
from services.llamaindex_rag_service import get_rag_service

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for system maintenance and cleanup operations (LlamaIndex-only)"""

    def __init__(self):
        # Use LlamaIndex RAG Service instead of legacy services
        logger.info("MaintenanceService initialized for LlamaIndex-only architecture")

    async def check_vector_consistency(
        self,
        db: AsyncSession,
        fix_issues: bool = False
    ) -> Dict[str, Any]:
        """
        Check consistency between database and ChromaDB (LlamaIndex-only)

        Args:
            db: Database session
            fix_issues: Whether to automatically fix found issues

        Returns:
            Dictionary with consistency report
        """
        logger.info("Starting vector consistency check (LlamaIndex)...")

        try:
            # Get LlamaIndex RAG service
            rag_service = await get_rag_service()

            # Get all document IDs from database
            db_doc_query = select(Document.id).distinct()
            db_doc_result = await db.execute(db_doc_query)
            db_document_ids = {str(doc_id) for doc_id in db_doc_result.scalars().all()}

            logger.info(f"Found {len(db_document_ids)} documents in database")

            # Initialize ChromaDB client to check vector store
            await rag_service.initialize()
            collection = rag_service.chroma_client.get_collection("rag_documents")

            # Get all chunks from ChromaDB
            try:
                vector_results = collection.get(include=['metadatas'])
                vector_chunk_ids = set(vector_results['ids']) if vector_results['ids'] else set()
                vector_doc_ids = {meta.get('doc_id', '') for meta in (vector_results.get('metadatas', []) or [])}
                vector_doc_ids.discard('')  # Remove empty strings

                logger.info(f"Found {len(vector_chunk_ids)} chunks in ChromaDB representing {len(vector_doc_ids)} documents")
            except Exception as e:
                logger.error(f"Failed to get vector chunks: {str(e)}")
                vector_chunk_ids = set()
                vector_doc_ids = set()

            # Find basic inconsistencies
            orphaned_vector_docs = vector_doc_ids - db_document_ids
            missing_vector_docs = db_document_ids - vector_doc_ids

            # Count stats (simplified for LlamaIndex-only)
            stats = {
                "check_timestamp": datetime.utcnow().isoformat(),
                "database_documents": len(db_document_ids),
                "vector_documents": len(vector_doc_ids),
                "vector_chunks": len(vector_chunk_ids),
                "orphaned_vector_documents": len(orphaned_vector_docs),
                "missing_vector_documents": len(missing_vector_docs),
                "consistency_issues": len(orphaned_vector_docs) + len(missing_vector_docs) > 0,
                "architecture": "llamaindex_only"
            }

            # Detailed issues
            issues = {
                "orphaned_vector_documents": list(orphaned_vector_docs),
                "missing_vector_documents": list(missing_vector_docs)
            }

            # Log summary
            logger.info(f"Vector consistency check completed. Issues found: {stats['consistency_issues']}")
            if stats['consistency_issues']:
                logger.warning(f"Found {len(orphaned_vector_docs)} orphaned vector docs, {len(missing_vector_docs)} missing vector docs")

            return {
                "status": "completed",
                "stats": stats,
                "issues": issues
            }

        except Exception as e:
            logger.error(f"Vector consistency check failed: {str(e)}")
            raise

    async def cleanup_orphaned_vectors(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Clean up orphaned vector entries (simplified for LlamaIndex)

        Args:
            db: Database session

        Returns:
            Cleanup report
        """
        logger.info("Starting orphaned vector cleanup...")

        try:
            # First run consistency check
            consistency_report = await self.check_vector_consistency(db)

            if not consistency_report["stats"]["consistency_issues"]:
                logger.info("No orphaned vectors found, nothing to clean up")
                return {
                    "status": "completed",
                    "cleanup_needed": False,
                    "deleted_chunks": 0
                }

            # Get RAG service and initialize
            rag_service = await get_rag_service()
            await rag_service.initialize()
            collection = rag_service.chroma_client.get_collection("rag_documents")

            # Clean up orphaned documents
            orphaned_docs = consistency_report["issues"]["orphaned_vector_documents"]
            deleted_chunks = 0

            for doc_id in orphaned_docs:
                try:
                    # Find and delete all chunks for this document
                    chunk_results = collection.get(where={"doc_id": doc_id})
                    if chunk_results['ids']:
                        collection.delete(ids=chunk_results['ids'])
                        deleted_chunks += len(chunk_results['ids'])
                        logger.info(f"Deleted {len(chunk_results['ids'])} chunks for orphaned document {doc_id}")
                except Exception as e:
                    logger.error(f"Failed to delete chunks for document {doc_id}: {str(e)}")

            logger.info(f"Cleanup completed: {deleted_chunks} chunks deleted for {len(orphaned_docs)} orphaned documents")

            return {
                "status": "completed",
                "cleanup_needed": True,
                "orphaned_documents": len(orphaned_docs),
                "deleted_chunks": deleted_chunks
            }

        except Exception as e:
            logger.error(f"Vector cleanup failed: {str(e)}")
            raise

    async def get_system_health(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get overall system health report (simplified for LlamaIndex)

        Args:
            db: Database session

        Returns:
            System health report
        """
        logger.info("Generating system health report...")

        try:
            # Run consistency check
            consistency_report = await self.check_vector_consistency(db)

            # Get basic stats
            doc_count_query = select(func.count(Document.id))
            doc_count_result = await db.execute(doc_count_query)
            total_documents = doc_count_result.scalar()

            # Calculate health score
            health_score = 100
            if consistency_report["stats"]["consistency_issues"]:
                # Reduce score based on issues
                issue_ratio = (consistency_report["stats"]["orphaned_vector_documents"] +
                             consistency_report["stats"]["missing_vector_documents"]) / max(total_documents, 1)
                health_score = max(50, 100 - int(issue_ratio * 50))

            # Determine status
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            else:
                status = "critical"

            recommendations = []
            if consistency_report["stats"]["orphaned_vector_documents"] > 0:
                recommendations.append(f"Clean up {consistency_report['stats']['orphaned_vector_documents']} orphaned vector documents")
            if consistency_report["stats"]["missing_vector_documents"] > 0:
                recommendations.append(f"Re-index {consistency_report['stats']['missing_vector_documents']} missing documents")

            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": status,
                "health_score": health_score,
                "architecture": "llamaindex_only",
                "total_documents": total_documents,
                "vector_consistency": consistency_report["stats"],
                "recommendations": recommendations
            }

            logger.info(f"System health: {status} (score: {health_score}/100)")
            return health_report

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "health_score": 0,
                "error": str(e)
            }


# Singleton service instance
_maintenance_service = None

async def get_maintenance_service() -> MaintenanceService:
    """Get the global maintenance service instance"""
    global _maintenance_service
    if _maintenance_service is None:
        _maintenance_service = MaintenanceService()
    return _maintenance_service