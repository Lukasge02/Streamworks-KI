#!/usr/bin/env python3
"""
Cleanup Orphaned Files Script
=============================

This script cleans up orphaned database entries and associated files that occur when:
1. Files are deleted directly from filesystem (VSCode) instead of through the API
2. Markdown conversion files are left behind after manual deletions
3. ChromaDB entries become stale

Usage:
    python3 -m app.scripts.cleanup_orphaned_files [--dry-run] [--force]

Options:
    --dry-run    Show what would be cleaned up without making changes
    --force      Skip confirmation prompts
    --verbose    Show detailed logging

Author: StreamWorks-KI Team
Date: 2025-07-07
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.config import Settings
from app.models.database import TrainingFile, get_db
from app.services.training_service import TrainingService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrphanedFilesCleanup:
    """Handles cleanup of orphaned files and database entries."""
    
    def __init__(self, dry_run: bool = False, force: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        self.settings = Settings()
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Statistics
        self.stats = {
            'orphaned_db_entries': 0,
            'orphaned_markdown_files': 0,
            'orphaned_chromadb_entries': 0,
            'filesystem_files_missing': 0,
            'total_cleaned': 0
        }
    
    async def run_cleanup(self) -> Dict[str, int]:
        """Run the complete cleanup process."""
        logger.info(f"🧹 Starting orphaned files cleanup (dry_run={self.dry_run})")
        
        async for db in get_db():
            training_service = TrainingService(db)
            
            # 1. Find orphaned database entries
            orphaned_entries = await self._find_orphaned_db_entries(db)
            logger.info(f"📊 Found {len(orphaned_entries)} orphaned database entries")
            
            # 2. Find orphaned markdown files
            orphaned_markdown = await self._find_orphaned_markdown_files(db)
            logger.info(f"📊 Found {len(orphaned_markdown)} orphaned markdown files")
            
            # 3. Display summary
            await self._display_cleanup_summary(orphaned_entries, orphaned_markdown)
            
            # 4. Confirm cleanup (unless forced)
            if not self.force and not self.dry_run:
                if not self._confirm_cleanup():
                    logger.info("❌ Cleanup cancelled by user")
                    return self.stats
            
            # 5. Perform cleanup
            if not self.dry_run:
                await self._cleanup_orphaned_entries(db, training_service, orphaned_entries)
                await self._cleanup_orphaned_markdown(orphaned_markdown)
            
            # 6. Final statistics
            logger.info(f"✅ Cleanup completed. Total items processed: {self.stats['total_cleaned']}")
            return self.stats
    
    async def _find_orphaned_db_entries(self, db: AsyncSession) -> List[TrainingFile]:
        """Find database entries where the original file no longer exists."""
        logger.info("🔍 Scanning database for orphaned entries...")
        
        # Get all training files from database
        query = select(TrainingFile)
        result = await db.execute(query)
        all_files = result.scalars().all()
        
        orphaned = []
        for file_record in all_files:
            if file_record.file_path and not os.path.exists(file_record.file_path):
                orphaned.append(file_record)
                self.stats['filesystem_files_missing'] += 1
                
                if self.verbose:
                    logger.debug(f"📁 Missing file: {file_record.filename} -> {file_record.file_path}")
        
        self.stats['orphaned_db_entries'] = len(orphaned)
        return orphaned
    
    async def _find_orphaned_markdown_files(self, db: AsyncSession) -> List[str]:
        """Find markdown files that have no corresponding database entry."""
        logger.info("🔍 Scanning for orphaned markdown files...")
        
        # Get all file IDs from database
        query = select(TrainingFile.id)
        result = await db.execute(query)
        valid_file_ids = {row[0] for row in result.fetchall()}
        
        orphaned_markdown = []
        
        # Search directories for markdown files
        search_dirs = [
            os.path.join(self.settings.TRAINING_DATA_PATH, "optimized", "help_data"),
            os.path.join(self.settings.TRAINING_DATA_PATH, "optimized", "stream_templates"),
            os.path.join(self.settings.TRAINING_DATA_PATH, "optimized"),
            os.path.join(self.settings.TRAINING_DATA_PATH, "processed")
        ]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            try:
                for filename in os.listdir(search_dir):
                    if not filename.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(search_dir, filename)
                    
                    # Extract file ID from markdown filename
                    # Pattern: {file_id}_filename_optimized.md or {file_id}_filename.md
                    if '_' in filename:
                        potential_file_id = filename.split('_')[0]
                        
                        # Check if this file ID exists in database
                        if potential_file_id not in valid_file_ids:
                            orphaned_markdown.append(file_path)
                            
                            if self.verbose:
                                logger.debug(f"📄 Orphaned markdown: {filename} (ID: {potential_file_id})")
                                
            except OSError as e:
                logger.warning(f"⚠️ Could not scan directory {search_dir}: {e}")
        
        self.stats['orphaned_markdown_files'] = len(orphaned_markdown)
        return orphaned_markdown
    
    async def _display_cleanup_summary(self, orphaned_entries: List[TrainingFile], 
                                     orphaned_markdown: List[str]):
        """Display a summary of what will be cleaned up."""
        logger.info("📋 Cleanup Summary:")
        logger.info("=" * 50)
        
        # Database entries
        if orphaned_entries:
            logger.info(f"🗃️ Database Entries to Remove: {len(orphaned_entries)}")
            for entry in orphaned_entries[:5]:  # Show first 5
                logger.info(f"   - {entry.filename} (ID: {entry.id})")
            if len(orphaned_entries) > 5:
                logger.info(f"   ... and {len(orphaned_entries) - 5} more")
        
        # Markdown files
        if orphaned_markdown:
            logger.info(f"📄 Markdown Files to Remove: {len(orphaned_markdown)}")
            for md_file in orphaned_markdown[:5]:  # Show first 5
                logger.info(f"   - {os.path.basename(md_file)}")
            if len(orphaned_markdown) > 5:
                logger.info(f"   ... and {len(orphaned_markdown) - 5} more")
        
        if not orphaned_entries and not orphaned_markdown:
            logger.info("✨ No orphaned files found - system is clean!")
    
    def _confirm_cleanup(self) -> bool:
        """Ask user for confirmation before cleanup."""
        total_items = self.stats['orphaned_db_entries'] + self.stats['orphaned_markdown_files']
        
        if total_items == 0:
            return True
        
        print(f"\n⚠️  About to clean up {total_items} orphaned items.")
        print("This action cannot be undone!")
        
        while True:
            response = input("Continue? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    async def _cleanup_orphaned_entries(self, db: AsyncSession, training_service: TrainingService,
                                      orphaned_entries: List[TrainingFile]):
        """Clean up orphaned database entries and associated data."""
        logger.info(f"🗑️ Cleaning up {len(orphaned_entries)} orphaned database entries...")
        
        for entry in orphaned_entries:
            try:
                # Remove from ChromaDB if indexed
                if entry.is_indexed:
                    try:
                        await training_service.remove_from_chromadb(entry.id)
                        self.stats['orphaned_chromadb_entries'] += 1
                        logger.info(f"🗑️ Removed from ChromaDB: {entry.id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not remove from ChromaDB {entry.id}: {e}")
                
                # Clean up associated markdown files for this entry
                markdown_files_deleted = await training_service._delete_associated_markdown_files(entry)
                if markdown_files_deleted:
                    logger.info(f"🗑️ Cleaned up markdown files for {entry.id}: {len(markdown_files_deleted)} files")
                
                # Remove database record
                await db.delete(entry)
                await db.commit()
                
                self.stats['total_cleaned'] += 1
                logger.info(f"✅ Cleaned up orphaned entry: {entry.filename} (ID: {entry.id})")
                
            except Exception as e:
                logger.error(f"❌ Failed to cleanup entry {entry.id}: {e}")
                await db.rollback()
    
    async def _cleanup_orphaned_markdown(self, orphaned_markdown: List[str]):
        """Clean up orphaned markdown files."""
        logger.info(f"🗑️ Cleaning up {len(orphaned_markdown)} orphaned markdown files...")
        
        for md_file in orphaned_markdown:
            try:
                os.remove(md_file)
                self.stats['total_cleaned'] += 1
                logger.info(f"✅ Removed orphaned markdown: {os.path.basename(md_file)}")
            except OSError as e:
                logger.warning(f"⚠️ Could not remove {md_file}: {e}")


async def main():
    """Main entry point for the cleanup script."""
    parser = argparse.ArgumentParser(
        description="Cleanup orphaned files and database entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 -m app.scripts.cleanup_orphaned_files --dry-run
    python3 -m app.scripts.cleanup_orphaned_files --force
    python3 -m app.scripts.cleanup_orphaned_files --verbose
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be cleaned up without making changes'
    )
    
    parser.add_argument(
        '--force',
        action='store_true', 
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed logging'
    )
    
    args = parser.parse_args()
    
    # Run cleanup
    cleanup = OrphanedFilesCleanup(
        dry_run=args.dry_run,
        force=args.force, 
        verbose=args.verbose
    )
    
    try:
        stats = await cleanup.run_cleanup()
        
        # Print final summary
        print("\n" + "="*50)
        print("🧹 CLEANUP SUMMARY")
        print("="*50)
        print(f"Orphaned DB entries: {stats['orphaned_db_entries']}")
        print(f"Orphaned markdown files: {stats['orphaned_markdown_files']}")
        print(f"ChromaDB entries cleaned: {stats['orphaned_chromadb_entries']}")
        print(f"Total items cleaned: {stats['total_cleaned']}")
        print("="*50)
        
        if args.dry_run:
            print("🔍 DRY RUN - No changes were made")
        else:
            print("✅ Cleanup completed successfully")
            
    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())