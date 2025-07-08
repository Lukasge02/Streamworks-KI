#!/usr/bin/env python3
"""
ChromaDB Sync Script for StreamWorks-KI
Command-line tool for managing ChromaDB sync operations
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.chromadb_sync_service import ChromaDBSyncService
from app.models.database import AsyncSessionLocal
from app.core.config import settings


async def analyze_orphaned_chunks():
    """Analyze ChromaDB for orphaned chunks"""
    print("🔍 Analyzing ChromaDB for orphaned chunks...")
    
    async with AsyncSessionLocal() as db:
        sync_service = ChromaDBSyncService(db)
        
        try:
            analysis = await sync_service.analyze_orphaned_chunks()
            
            print(f"\n📊 ChromaDB Analysis Results:")
            print(f"{'='*50}")
            print(f"Total chunks in ChromaDB: {analysis['total_chunks_in_chromadb']:,}")
            print(f"Unique source files: {analysis['total_unique_sources']:,}")
            print(f"Orphaned chunks: {analysis['orphaned_chunk_count']:,}")
            print(f"Orphaned files: {len(analysis['orphaned_files'])}")
            
            if analysis['orphaned_files']:
                print(f"\n🚨 Orphaned Files Found:")
                print(f"{'='*50}")
                for i, orphaned_file in enumerate(analysis['orphaned_files'][:10], 1):
                    print(f"{i:2d}. {orphaned_file['filename']} ({orphaned_file['chunks']} chunks)")
                    print(f"    Source: {orphaned_file['source']}")
                    print(f"    File ID: {orphaned_file['file_id']}")
                    print()
                
                if len(analysis['orphaned_files']) > 10:
                    print(f"... and {len(analysis['orphaned_files']) - 10} more files")
            
            print(f"\n💡 Recommendations:")
            print(f"{'='*50}")
            for rec in analysis['recommendations']:
                print(f"   {rec}")
            
            # Save detailed analysis to file
            output_file = f"chromadb_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"\n💾 Detailed analysis saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)


async def cleanup_orphaned_chunks(dry_run: bool = True):
    """Clean up orphaned chunks from ChromaDB"""
    action_type = "🔬 Simulating" if dry_run else "🗑️ Performing"
    print(f"{action_type} ChromaDB orphaned chunks cleanup...")
    
    async with AsyncSessionLocal() as db:
        sync_service = ChromaDBSyncService(db)
        
        try:
            result = await sync_service.cleanup_orphaned_chunks(dry_run=dry_run)
            
            print(f"\n📊 Cleanup Results:")
            print(f"{'='*50}")
            print(f"Action: {result['action']}")
            print(f"Dry run: {result['dry_run']}")
            print(f"Files cleaned: {result['cleaned_files']}")
            print(f"Chunks cleaned: {result['cleaned_chunks']}")
            
            if result['errors']:
                print(f"\n⚠️ Errors encountered:")
                for error in result['errors']:
                    print(f"   - {error['source']}: {error['error']}")
            
            print(f"\n✅ {result['message']}")
            
            if dry_run:
                print(f"\n💡 To perform actual cleanup, run:")
                print(f"   python scripts/sync_chromadb.py --cleanup --force")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            sys.exit(1)


async def sync_database(dry_run: bool = True):
    """Sync database with filesystem"""
    action_type = "🔬 Simulating" if dry_run else "🔄 Performing"
    print(f"{action_type} database sync with filesystem...")
    
    async with AsyncSessionLocal() as db:
        sync_service = ChromaDBSyncService(db)
        
        try:
            result = await sync_service.sync_database_with_chromadb(dry_run=dry_run)
            
            print(f"\n📊 Database Sync Results:")
            print(f"{'='*50}")
            print(f"Action: {result['action']}")
            print(f"Dry run: {result['dry_run']}")
            print(f"Files checked: {result['files_checked']}")
            print(f"Files to remove: {result['files_to_remove']}")
            print(f"Files removed: {result['files_removed']}")
            
            if result['orphaned_files']:
                print(f"\n🚨 Orphaned Database Entries:")
                for orphaned in result['orphaned_files'][:5]:
                    print(f"   - {orphaned['filename']} (ID: {orphaned['id']})")
                    print(f"     Path: {orphaned['file_path']}")
                
                if len(result['orphaned_files']) > 5:
                    print(f"   ... and {len(result['orphaned_files']) - 5} more files")
            
            if result['errors']:
                print(f"\n⚠️ Errors encountered:")
                for error in result['errors']:
                    print(f"   - {error['filename']}: {error['error']}")
            
            print(f"\n✅ {result['message']}")
            
            if dry_run:
                print(f"\n💡 To perform actual sync, run:")
                print(f"   python scripts/sync_chromadb.py --sync-db --force")
            
        except Exception as e:
            print(f"❌ Database sync failed: {e}")
            sys.exit(1)


async def full_sync_check():
    """Perform comprehensive sync check"""
    print("🔍 Performing comprehensive sync check...")
    
    async with AsyncSessionLocal() as db:
        sync_service = ChromaDBSyncService(db)
        
        try:
            analysis = await sync_service.full_sync_check()
            
            print(f"\n📊 Full Sync Analysis:")
            print(f"{'='*50}")
            print(f"Timestamp: {analysis['timestamp']}")
            
            print(f"\n📁 Filesystem:")
            print(f"   Total files: {analysis['filesystem']['total_files']}")
            print(f"   Files by type: {analysis['filesystem']['files_by_type']}")
            
            print(f"\n🗄️ Database:")
            print(f"   Total entries: {analysis['database']['total_entries']}")
            print(f"   Indexed entries: {analysis['database']['indexed_entries']}")
            print(f"   Entries by category: {analysis['database']['entries_by_category']}")
            
            print(f"\n🔮 ChromaDB:")
            print(f"   Total chunks: {analysis['chromadb']['total_chunks']}")
            print(f"   Unique sources: {analysis['chromadb']['unique_sources']}")
            print(f"   Orphaned chunks: {analysis['chromadb']['orphaned_chunks']}")
            print(f"   Orphaned files: {analysis['chromadb']['orphaned_files']}")
            
            print(f"\n🚨 Sync Issues:")
            print(f"   ChromaDB orphaned chunks: {analysis['sync_issues']['chromadb_orphaned_chunks']}")
            print(f"   Database orphaned entries: {analysis['sync_issues']['database_orphaned_entries']}")
            print(f"   Unindexed files: {analysis['sync_issues']['unindexed_files']}")
            
            print(f"\n💡 Recommendations:")
            print(f"{'='*50}")
            for rec in analysis['recommendations']:
                print(f"   {rec}")
            
            # Save detailed analysis to file
            output_file = f"full_sync_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"\n💾 Detailed analysis saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Full sync check failed: {e}")
            sys.exit(1)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ChromaDB Sync Management Tool")
    parser.add_argument("--analyze", action="store_true", help="Analyze orphaned chunks")
    parser.add_argument("--cleanup", action="store_true", help="Clean up orphaned chunks")
    parser.add_argument("--sync-db", action="store_true", help="Sync database with filesystem")
    parser.add_argument("--full-check", action="store_true", help="Perform comprehensive sync check")
    parser.add_argument("--force", action="store_true", help="Actually perform changes (disable dry-run)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Default to analysis if no specific action is provided
    if not any([args.analyze, args.cleanup, args.sync_db, args.full_check]):
        args.analyze = True
    
    dry_run = not args.force
    
    print("🚀 ChromaDB Sync Management Tool")
    print("================================")
    print(f"Settings: {settings.PROJECT_NAME} - {settings.ENV}")
    print(f"Vector DB Path: {settings.VECTOR_DB_PATH}")
    
    try:
        if args.analyze:
            await analyze_orphaned_chunks()
        
        if args.cleanup:
            await cleanup_orphaned_chunks(dry_run=dry_run)
        
        if args.sync_db:
            await sync_database(dry_run=dry_run)
        
        if args.full_check:
            await full_sync_check()
        
        print("\n✅ All operations completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())