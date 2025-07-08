"""
ChromaDB Sync Service for StreamWorks-KI
Manages synchronization between filesystem and ChromaDB vector database
"""

import os
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import TrainingFile
from app.services.rag_service import rag_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChromaDBSyncService:
    """Service for syncing ChromaDB with filesystem and database"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_service = rag_service
        
    async def analyze_orphaned_chunks(self) -> Dict[str, Any]:
        """
        Analyze ChromaDB for orphaned chunks (chunks pointing to non-existent files)
        
        Returns:
            Dict containing orphaned files analysis
        """
        try:
            # Initialize RAG service if needed
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            # Get all documents from ChromaDB
            chromadb_docs = await self.rag_service.get_all_documents()
            
            orphaned_files = []
            valid_files = []
            orphaned_chunk_count = 0
            
            # Track unique source files
            source_files_in_chromadb = set()
            
            # Get direct access to ChromaDB collection for detailed analysis
            collection = self.rag_service.vector_store._collection
            all_data = collection.get()
            
            # Analyze each chunk
            for i, doc_content in enumerate(all_data['documents']):
                metadata = all_data['metadatas'][i]
                source = metadata.get('source', 'unknown')
                
                # Track source files
                source_files_in_chromadb.add(source)
                
                # Check if source file exists on filesystem
                file_exists = False
                
                # Check various possible file paths
                possible_paths = [
                    source,  # Direct path
                    os.path.join(".", source),  # Relative to current
                    os.path.join("..", source),  # Relative to parent
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        file_exists = True
                        break
                
                # If file doesn't exist, it's orphaned
                if not file_exists:
                    orphaned_chunk_count += 1
                    
                    # Check if we already tracked this orphaned file
                    if source not in [f['source'] for f in orphaned_files]:
                        orphaned_files.append({
                            'source': source,
                            'filename': metadata.get('filename', 'unknown'),
                            'file_id': metadata.get('file_id', 'unknown'),
                            'chunks': 1
                        })
                    else:
                        # Increment chunk count for existing orphaned file
                        for f in orphaned_files:
                            if f['source'] == source:
                                f['chunks'] += 1
                                break
                else:
                    valid_files.append({
                        'source': source,
                        'filename': metadata.get('filename', 'unknown'),
                        'file_id': metadata.get('file_id', 'unknown')
                    })
            
            # Get database training files for comparison
            db_files = await self._get_database_training_files()
            
            # Compare database vs ChromaDB
            db_file_paths = {f.file_path for f in db_files}
            chromadb_file_paths = source_files_in_chromadb
            
            # Find mismatches
            db_only_files = db_file_paths - chromadb_file_paths
            chromadb_only_files = chromadb_file_paths - db_file_paths
            
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'total_chunks_in_chromadb': len(all_data['documents']),
                'total_unique_sources': len(source_files_in_chromadb),
                'orphaned_files': orphaned_files,
                'orphaned_chunk_count': orphaned_chunk_count,
                'valid_files_count': len(valid_files),
                'database_files_count': len(db_files),
                'sync_issues': {
                    'files_in_db_not_in_chromadb': len(db_only_files),
                    'files_in_chromadb_not_in_db': len(chromadb_only_files),
                    'db_only_files': list(db_only_files)[:10],  # Limit for readability
                    'chromadb_only_files': list(chromadb_only_files)[:10]
                },
                'recommendations': self._generate_recommendations(orphaned_files, orphaned_chunk_count)
            }
            
            logger.info(f"🔍 ChromaDB sync analysis completed: {orphaned_chunk_count} orphaned chunks found")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ ChromaDB sync analysis failed: {e}")
            raise
    
    async def cleanup_orphaned_chunks(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up orphaned chunks from ChromaDB
        
        Args:
            dry_run: If True, only simulate cleanup (default: True)
            
        Returns:
            Dict containing cleanup results
        """
        try:
            # Get orphaned chunks analysis
            analysis = await self.analyze_orphaned_chunks()
            orphaned_files = analysis['orphaned_files']
            
            if not orphaned_files:
                return {
                    'action': 'cleanup',
                    'dry_run': dry_run,
                    'cleaned_files': 0,
                    'cleaned_chunks': 0,
                    'message': 'No orphaned chunks found'
                }
            
            cleaned_files = 0
            cleaned_chunks = 0
            cleanup_errors = []
            
            # Initialize RAG service if needed
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            # Get direct access to ChromaDB collection
            collection = self.rag_service.vector_store._collection
            
            for orphaned_file in orphaned_files:
                try:
                    source = orphaned_file['source']
                    
                    if not dry_run:
                        # Delete all chunks for this source
                        results = collection.get(where={"source": source})
                        
                        if results['ids']:
                            collection.delete(ids=results['ids'])
                            cleaned_chunks += len(results['ids'])
                            logger.info(f"🗑️ Cleaned {len(results['ids'])} chunks for source: {source}")
                        
                        # Persist changes
                        self.rag_service.vector_store.persist()
                    
                    cleaned_files += 1
                    
                except Exception as e:
                    cleanup_errors.append({
                        'source': orphaned_file['source'],
                        'error': str(e)
                    })
                    logger.error(f"❌ Failed to clean chunks for {orphaned_file['source']}: {e}")
            
            action_type = "simulation" if dry_run else "cleanup"
            
            result = {
                'action': action_type,
                'dry_run': dry_run,
                'cleaned_files': cleaned_files,
                'cleaned_chunks': cleaned_chunks,
                'errors': cleanup_errors,
                'message': f"{'Simulated' if dry_run else 'Performed'} cleanup of {cleaned_chunks} orphaned chunks from {cleaned_files} files"
            }
            
            if dry_run:
                logger.info(f"🔬 Dry run: Would clean {cleaned_chunks} orphaned chunks from {cleaned_files} files")
            else:
                logger.info(f"🗑️ Cleanup completed: Removed {cleaned_chunks} orphaned chunks from {cleaned_files} files")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ ChromaDB cleanup failed: {e}")
            raise
    
    async def sync_database_with_chromadb(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Synchronize database training files with ChromaDB
        Remove database entries for files that no longer exist on filesystem
        
        Args:
            dry_run: If True, only simulate sync (default: True)
            
        Returns:
            Dict containing sync results
        """
        try:
            # Get all database training files
            db_files = await self._get_database_training_files()
            
            files_to_remove = []
            files_checked = 0
            
            for db_file in db_files:
                files_checked += 1
                
                # Check if file exists on filesystem
                file_exists = False
                
                # Check various possible file paths
                possible_paths = [
                    db_file.file_path,  # Direct path
                    os.path.join(".", db_file.file_path),  # Relative to current
                    os.path.join("..", db_file.file_path),  # Relative to parent
                ]
                
                # Also check processed file path if it exists
                if db_file.processed_file_path:
                    possible_paths.extend([
                        db_file.processed_file_path,
                        os.path.join(".", db_file.processed_file_path),
                        os.path.join("..", db_file.processed_file_path)
                    ])
                
                for path in possible_paths:
                    if os.path.exists(path):
                        file_exists = True
                        break
                
                # If file doesn't exist, mark for removal
                if not file_exists:
                    files_to_remove.append({
                        'id': db_file.id,
                        'filename': db_file.filename,
                        'file_path': db_file.file_path,
                        'processed_file_path': db_file.processed_file_path,
                        'is_indexed': db_file.is_indexed
                    })
            
            # Perform cleanup if not dry run
            removed_files = 0
            cleanup_errors = []
            
            if not dry_run:
                for file_to_remove in files_to_remove:
                    try:
                        # Remove from ChromaDB if indexed
                        if file_to_remove['is_indexed']:
                            await self._remove_file_from_chromadb(file_to_remove['id'])
                        
                        # Remove from database
                        await self._remove_file_from_database(file_to_remove['id'])
                        
                        removed_files += 1
                        logger.info(f"🗑️ Removed orphaned database entry: {file_to_remove['filename']}")
                        
                    except Exception as e:
                        cleanup_errors.append({
                            'file_id': file_to_remove['id'],
                            'filename': file_to_remove['filename'],
                            'error': str(e)
                        })
                        logger.error(f"❌ Failed to remove file {file_to_remove['id']}: {e}")
            
            action_type = "simulation" if dry_run else "sync"
            
            result = {
                'action': action_type,
                'dry_run': dry_run,
                'files_checked': files_checked,
                'files_to_remove': len(files_to_remove),
                'files_removed': removed_files,
                'errors': cleanup_errors,
                'orphaned_files': files_to_remove,
                'message': f"{'Simulated' if dry_run else 'Performed'} database sync: {removed_files} orphaned entries removed"
            }
            
            if dry_run:
                logger.info(f"🔬 Dry run: Would remove {len(files_to_remove)} orphaned database entries")
            else:
                logger.info(f"🗑️ Database sync completed: Removed {removed_files} orphaned entries")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {e}")
            raise
    
    async def full_sync_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive sync check of filesystem, database, and ChromaDB
        
        Returns:
            Dict containing comprehensive sync analysis
        """
        try:
            # Get all three data sources
            filesystem_files = await self._get_filesystem_files()
            database_files = await self._get_database_training_files()
            chromadb_analysis = await self.analyze_orphaned_chunks()
            
            # Create comprehensive analysis
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'filesystem': {
                    'total_files': len(filesystem_files),
                    'files_by_type': self._categorize_files(filesystem_files)
                },
                'database': {
                    'total_entries': len(database_files),
                    'indexed_entries': len([f for f in database_files if f.is_indexed]),
                    'entries_by_category': self._categorize_db_files(database_files)
                },
                'chromadb': {
                    'total_chunks': chromadb_analysis['total_chunks_in_chromadb'],
                    'unique_sources': chromadb_analysis['total_unique_sources'],
                    'orphaned_chunks': chromadb_analysis['orphaned_chunk_count'],
                    'orphaned_files': len(chromadb_analysis['orphaned_files'])
                },
                'sync_issues': {
                    'chromadb_orphaned_chunks': chromadb_analysis['orphaned_chunk_count'],
                    'database_orphaned_entries': len([f for f in database_files if not self._file_exists(f.file_path)]),
                    'unindexed_files': len([f for f in filesystem_files if not self._is_file_indexed(f, database_files)])
                },
                'recommendations': self._generate_full_sync_recommendations(chromadb_analysis, database_files, filesystem_files)
            }
            
            logger.info("🔍 Full sync check completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Full sync check failed: {e}")
            raise
    
    async def _get_database_training_files(self) -> List[TrainingFile]:
        """Get all training files from database"""
        query = select(TrainingFile)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _get_filesystem_files(self) -> List[Dict[str, Any]]:
        """Get all files from filesystem training data directories"""
        filesystem_files = []
        
        # Define training data directories
        base_path = os.path.join(".", "data", "training_data")
        
        directories = [
            os.path.join(base_path, "originals", "help_data"),
            os.path.join(base_path, "originals", "stream_templates"),
            os.path.join(base_path, "optimized", "help_data"),
            os.path.join(base_path, "optimized", "stream_templates"),
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        filesystem_files.append({
                            'filename': filename,
                            'file_path': file_path,
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path),
                            'directory': directory
                        })
        
        return filesystem_files
    
    async def _remove_file_from_chromadb(self, file_id: str):
        """Remove file from ChromaDB by file_id"""
        try:
            # Initialize RAG service if needed
            if not self.rag_service.is_initialized:
                await self.rag_service.initialize()
            
            # Get direct access to ChromaDB collection
            collection = self.rag_service.vector_store._collection
            
            # Find and delete all chunks for this file_id
            results = collection.get(where={"file_id": file_id})
            
            if results['ids']:
                collection.delete(ids=results['ids'])
                self.rag_service.vector_store.persist()
                logger.info(f"🗑️ Removed {len(results['ids'])} chunks for file_id: {file_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to remove file from ChromaDB: {e}")
            raise
    
    async def _remove_file_from_database(self, file_id: str):
        """Remove file from database by file_id"""
        try:
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            file_record = result.scalar_one_or_none()
            
            if file_record:
                await self.db.delete(file_record)
                await self.db.commit()
                logger.info(f"🗑️ Removed database entry for file_id: {file_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to remove file from database: {e}")
            raise
    
    def _file_exists(self, file_path: str) -> bool:
        """Check if file exists on filesystem"""
        if not file_path:
            return False
        
        # Check various possible file paths
        possible_paths = [
            file_path,  # Direct path
            os.path.join(".", file_path),  # Relative to current
            os.path.join("..", file_path),  # Relative to parent
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _is_file_indexed(self, filesystem_file: Dict[str, Any], database_files: List[TrainingFile]) -> bool:
        """Check if filesystem file is indexed in database"""
        for db_file in database_files:
            if filesystem_file['filename'] == db_file.filename:
                return True
        return False
    
    def _categorize_files(self, filesystem_files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize filesystem files by extension"""
        categories = {}
        for file_info in filesystem_files:
            ext = os.path.splitext(file_info['filename'])[1].lower()
            categories[ext] = categories.get(ext, 0) + 1
        return categories
    
    def _categorize_db_files(self, database_files: List[TrainingFile]) -> Dict[str, int]:
        """Categorize database files by category"""
        categories = {}
        for db_file in database_files:
            category = db_file.category or 'unknown'
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _generate_recommendations(self, orphaned_files: List[Dict[str, Any]], orphaned_chunk_count: int) -> List[str]:
        """Generate recommendations based on orphaned files analysis"""
        recommendations = []
        
        if orphaned_chunk_count > 0:
            recommendations.append(f"🧹 Clean up {orphaned_chunk_count} orphaned chunks from {len(orphaned_files)} files")
            recommendations.append("🔄 Run `cleanup_orphaned_chunks(dry_run=False)` to remove orphaned chunks")
        
        if orphaned_chunk_count > 1000:
            recommendations.append("⚠️ High number of orphaned chunks detected - consider full database rebuild")
        
        if len(orphaned_files) > 10:
            recommendations.append("📋 Consider implementing automatic sync checks to prevent future orphaning")
        
        if not recommendations:
            recommendations.append("✅ ChromaDB is clean - no orphaned chunks detected")
        
        return recommendations
    
    def _generate_full_sync_recommendations(self, chromadb_analysis: Dict[str, Any], database_files: List[TrainingFile], filesystem_files: List[Dict[str, Any]]) -> List[str]:
        """Generate comprehensive recommendations for full sync"""
        recommendations = []
        
        # ChromaDB recommendations
        if chromadb_analysis['orphaned_chunk_count'] > 0:
            recommendations.append(f"🧹 Clean up {chromadb_analysis['orphaned_chunk_count']} orphaned chunks from ChromaDB")
        
        # Database recommendations
        orphaned_db_entries = len([f for f in database_files if not self._file_exists(f.file_path)])
        if orphaned_db_entries > 0:
            recommendations.append(f"🗑️ Remove {orphaned_db_entries} orphaned database entries")
        
        # Filesystem recommendations
        unindexed_files = len([f for f in filesystem_files if not self._is_file_indexed(f, database_files)])
        if unindexed_files > 0:
            recommendations.append(f"📥 Index {unindexed_files} unindexed files from filesystem")
        
        # Overall recommendations
        if len(recommendations) > 2:
            recommendations.append("🔄 Consider running a full sync operation to resolve all issues")
        
        if not recommendations:
            recommendations.append("✅ All systems are in sync - no issues detected")
        
        return recommendations

# Global instance
chromadb_sync_service = ChromaDBSyncService