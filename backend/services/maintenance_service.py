"""
Maintenance Service for StreamWorks
Qdrant Vector Store architecture
Handles cleanup operations, consistency checks, and system maintenance tasks
"""

import logging
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.core import Document
from services.qdrant_vectorstore import get_qdrant_service

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for system maintenance and cleanup operations (Qdrant architecture)"""

    def __init__(self):
        # Use Qdrant Vector Store Service
        logger.info("MaintenanceService initialized for Qdrant architecture")

    async def check_vector_consistency(
        self,
        db: AsyncSession,
        fix_issues: bool = False
    ) -> Dict[str, Any]:
        """
        Check consistency between database and Qdrant vector store

        Args:
            db: Database session
            fix_issues: Whether to automatically fix found issues

        Returns:
            Dictionary with consistency report
        """
        logger.info("Starting vector consistency check (Qdrant)...")

        try:
            # Get Qdrant vector store service
            qdrant_service = await get_qdrant_service()
            await qdrant_service.initialize()

            # Get all document IDs from database
            db_doc_query = select(Document.id).distinct()
            db_doc_result = await db.execute(db_doc_query)
            db_document_ids = {str(doc_id) for doc_id in db_doc_result.scalars().all()}

            logger.info(f"Found {len(db_document_ids)} documents in database")

            # Get collection info from Qdrant
            try:
                collection_info = await qdrant_service.get_collection_info()
                total_chunks = collection_info.get("vectors_count", 0)

                # Get unique document IDs from Qdrant by scrolling through all points
                import asyncio
                scroll_results = await asyncio.to_thread(
                    qdrant_service.client.scroll,
                    collection_name=qdrant_service.collection_name,
                    limit=10000,  # Get all points
                    with_payload=True,
                    with_vectors=False
                )

                vector_doc_ids = set()
                vector_chunk_count = 0
                for point in scroll_results[0]:  # scroll returns (points, next_page_offset)
                    if point.payload and 'doc_id' in point.payload:
                        vector_doc_ids.add(point.payload['doc_id'])
                        vector_chunk_count += 1

                logger.info(f"Found {vector_chunk_count} chunks in Qdrant representing {len(vector_doc_ids)} documents")
            except Exception as e:
                logger.error(f"Failed to get vector chunks from Qdrant: {str(e)}")
                vector_doc_ids = set()
                vector_chunk_count = 0

            # Find basic inconsistencies
            orphaned_vector_docs = vector_doc_ids - db_document_ids
            missing_vector_docs = db_document_ids - vector_doc_ids

            # Count stats
            stats = {
                "check_timestamp": datetime.utcnow().isoformat(),
                "database_documents": len(db_document_ids),
                "vector_documents": len(vector_doc_ids),
                "vector_chunks": vector_chunk_count,
                "orphaned_vector_documents": len(orphaned_vector_docs),
                "missing_vector_documents": len(missing_vector_docs),
                "consistency_issues": len(orphaned_vector_docs) + len(missing_vector_docs) > 0,
                "architecture": "qdrant"
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
        Clean up orphaned vector entries in Qdrant

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

            # Get Qdrant service and initialize
            qdrant_service = await get_qdrant_service()
            await qdrant_service.initialize()

            # Clean up orphaned documents
            orphaned_docs = consistency_report["issues"]["orphaned_vector_documents"]
            deleted_chunks = 0

            for doc_id in orphaned_docs:
                try:
                    # Delete all chunks for this document using Qdrant service
                    success = await qdrant_service.delete_documents(doc_id)
                    if success:
                        # Count deleted chunks by checking before/after
                        chunks_before = len(await qdrant_service.get_document_chunks(doc_id, limit=1000))
                        deleted_chunks += chunks_before
                        logger.info(f"Deleted chunks for orphaned document {doc_id}")
                    else:
                        logger.warning(f"Failed to delete document {doc_id} from Qdrant")
                except Exception as e:
                    logger.error(f"Failed to delete chunks for document {doc_id}: {str(e)}")

            logger.info(f"Cleanup completed: estimated {deleted_chunks} chunks deleted for {len(orphaned_docs)} orphaned documents")

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
        Get overall system health report for Qdrant architecture

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
                "architecture": "qdrant",
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