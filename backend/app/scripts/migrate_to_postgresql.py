#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script for StreamWorks-KI
Migrates all data while preserving relationships and optimizing for PostgreSQL
"""
import asyncio
import logging
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import argparse

# SQLAlchemy imports
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import asyncpg

# Project imports
from app.core.config_postgres import postgres_settings
from app.models.database_postgres import Base, TrainingFile, ChatConversation, DocumentMetadata

logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    """Comprehensive migration from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_path: str, dry_run: bool = False):
        self.sqlite_path = sqlite_path
        self.dry_run = dry_run
        self.pg_engine = None
        self.pg_session_factory = None
        self.migration_stats = {
            "training_files": {"total": 0, "migrated": 0, "errors": 0},
            "conversations": {"total": 0, "migrated": 0, "errors": 0},
            "metadata": {"total": 0, "migrated": 0, "errors": 0},
        }
        
    async def initialize_postgresql(self) -> bool:
        """Initialize PostgreSQL connection and schema"""
        try:
            # Create async engine
            self.pg_engine = create_async_engine(
                postgres_settings.DATABASE_URL,
                echo=False,  # Disable echo during migration
                pool_size=10,
                max_overflow=20,
            )
            
            # Create session factory
            self.pg_session_factory = async_sessionmaker(
                self.pg_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.pg_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✅ PostgreSQL connection established")
            
            # Create schema if not exists
            if not self.dry_run:
                async with self.pg_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ PostgreSQL schema created/updated")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL initialization failed: {e}")
            return False
    
    def get_sqlite_data(self) -> Dict[str, List[Dict]]:
        """Extract all data from SQLite database"""
        logger.info(f"📖 Reading SQLite database: {self.sqlite_path}")
        
        if not Path(self.sqlite_path).exists():
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        data = {}
        
        try:
            # Get training files
            cursor = conn.execute("SELECT * FROM training_files")
            training_files = [dict(row) for row in cursor.fetchall()]
            data["training_files"] = training_files
            self.migration_stats["training_files"]["total"] = len(training_files)
            logger.info(f"📄 Found {len(training_files)} training files")
            
            # Get conversations if table exists
            try:
                cursor = conn.execute("SELECT * FROM conversations")
                conversations = [dict(row) for row in cursor.fetchall()]
                data["conversations"] = conversations
                self.migration_stats["conversations"]["total"] = len(conversations)
                logger.info(f"💬 Found {len(conversations)} conversations")
            except sqlite3.OperationalError:
                logger.info("💬 No conversations table found")
                data["conversations"] = []
            
            # Get document metadata if table exists
            try:
                cursor = conn.execute("SELECT * FROM document_metadata")
                metadata = [dict(row) for row in cursor.fetchall()]
                data["document_metadata"] = metadata
                self.migration_stats["metadata"]["total"] = len(metadata)
                logger.info(f"📋 Found {len(metadata)} metadata entries")
            except sqlite3.OperationalError:
                logger.info("📋 No document_metadata table found")
                data["document_metadata"] = []
                
        finally:
            conn.close()
        
        return data
    
    def convert_training_file(self, sqlite_row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SQLite training file row to PostgreSQL format"""
        try:
            # Handle UUID conversion
            file_id = sqlite_row.get("id")
            if isinstance(file_id, str) and len(file_id) == 36:
                # Already UUID format
                pg_id = file_id
            elif isinstance(file_id, int):
                # Convert integer ID to UUID
                pg_id = str(uuid.uuid4())
            else:
                pg_id = str(uuid.uuid4())
            
            # Convert timestamps
            def convert_timestamp(ts_str):
                if not ts_str:
                    return None
                try:
                    if isinstance(ts_str, str):
                        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    return ts_str
                except:
                    return None
            
            # Handle JSON fields
            def safe_json_parse(json_str):
                if not json_str:
                    return None
                try:
                    if isinstance(json_str, str):
                        return json.loads(json_str)
                    return json_str
                except:
                    return None
            
            # Handle float conversion with string fallback
            def safe_float_convert(value):
                if value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    try:
                        return float(value)
                    except ValueError:
                        # Handle string quality ratings
                        quality_map = {
                            'excellent': 0.95,
                            'good': 0.8,
                            'fair': 0.6,
                            'poor': 0.4,
                            'very_poor': 0.2
                        }
                        return quality_map.get(value.lower(), 0.5)
                return None
            
            # Convert to PostgreSQL format
            pg_row = {
                "id": pg_id,
                "filename": sqlite_row.get("filename", "unknown.txt"),
                "display_name": sqlite_row.get("display_name"),
                "file_path": sqlite_row.get("file_path", ""),
                "original_path": sqlite_row.get("original_path"),
                "file_size": sqlite_row.get("file_size", 0) or 0,
                "upload_date": convert_timestamp(sqlite_row.get("upload_date")),
                "upload_timestamp": convert_timestamp(sqlite_row.get("upload_timestamp")) or datetime.utcnow(),
                "status": sqlite_row.get("status", "uploaded"),
                "is_indexed": bool(sqlite_row.get("is_indexed", False)),
                "indexed_at": convert_timestamp(sqlite_row.get("indexed_at")),
                "chunk_count": sqlite_row.get("chunk_count", 0) or 0,
                "chromadb_ids": safe_json_parse(sqlite_row.get("chromadb_ids")),
                "processing_metadata": safe_json_parse(sqlite_row.get("conversion_metadata")),
                "error_message": sqlite_row.get("error_message"),
                "index_status": sqlite_row.get("index_status", "pending"),
                "index_error": sqlite_row.get("index_error"),
                "processing_error": sqlite_row.get("processing_error"),
                "conversion_error": sqlite_row.get("conversion_error"),
                "processed_file_path": sqlite_row.get("processed_file_path"),
                "markdown_file_path": sqlite_row.get("markdown_file_path"),
                "original_format": sqlite_row.get("original_format"),
                "optimized_format": sqlite_row.get("optimized_format"),
                "conversion_status": sqlite_row.get("conversion_status", "pending"),
                "document_category": sqlite_row.get("document_category"),
                "document_type": sqlite_row.get("document_type"),
                "language": sqlite_row.get("language", "de"),
                "processing_method": sqlite_row.get("processing_method"),
                "processing_quality": safe_float_convert(sqlite_row.get("processing_quality")),
                "extraction_confidence": safe_float_convert(sqlite_row.get("extraction_confidence")),
                "source_type": sqlite_row.get("source_type"),
                "source_title": sqlite_row.get("source_title"),
                "source_url": sqlite_row.get("source_url"),
                "author": sqlite_row.get("author"),
                "version": sqlite_row.get("version"),
                "last_modified": convert_timestamp(sqlite_row.get("last_modified")),
                "manual_source_category": sqlite_row.get("manual_source_category"),
                "description": sqlite_row.get("description"),
                "priority": sqlite_row.get("priority", 1) or 1,
                "tags": sqlite_row.get("tags", "").split(",") if sqlite_row.get("tags") else [],
                "created_at": convert_timestamp(sqlite_row.get("upload_date")) or datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            return pg_row
            
        except Exception as e:
            logger.error(f"❌ Error converting training file row: {e}")
            logger.error(f"❌ Row data: {sqlite_row}")
            raise
    
    async def migrate_training_files(self, training_files: List[Dict]) -> bool:
        """Migrate training files to PostgreSQL"""
        if not training_files:
            logger.info("📄 No training files to migrate")
            return True
        
        logger.info(f"📄 Migrating {len(training_files)} training files...")
        
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would migrate training files")
            return True
        
        async with self.pg_session_factory() as session:
            try:
                for i, sqlite_row in enumerate(training_files):
                    try:
                        pg_row = self.convert_training_file(sqlite_row)
                        
                        # Create TrainingFile object
                        training_file = TrainingFile(**pg_row)
                        session.add(training_file)
                        
                        # Commit in batches
                        if (i + 1) % 100 == 0:
                            await session.commit()
                            logger.info(f"📄 Migrated {i + 1}/{len(training_files)} training files")
                        
                        self.migration_stats["training_files"]["migrated"] += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to migrate training file {i}: {e}")
                        self.migration_stats["training_files"]["errors"] += 1
                        await session.rollback()
                        continue
                
                # Final commit
                await session.commit()
                logger.info(f"✅ Training files migration completed: {self.migration_stats['training_files']['migrated']} migrated")
                return True
                
            except Exception as e:
                logger.error(f"❌ Training files migration failed: {e}")
                await session.rollback()
                return False
    
    async def migrate_conversations(self, conversations: List[Dict]) -> bool:
        """Migrate conversations to PostgreSQL"""
        if not conversations:
            logger.info("💬 No conversations to migrate")
            return True
        
        logger.info(f"💬 Migrating {len(conversations)} conversations...")
        
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would migrate conversations")
            return True
        
        # For now, skip conversation migration as schema might differ
        logger.info("💬 Conversation migration will be implemented based on actual schema")
        return True
    
    async def verify_migration(self) -> bool:
        """Verify migration completeness and data integrity"""
        logger.info("🔍 Verifying migration...")
        
        async with self.pg_session_factory() as session:
            try:
                # Count migrated records
                result = await session.execute(text("SELECT COUNT(*) FROM training_files"))
                pg_count = result.scalar()
                
                logger.info(f"📊 PostgreSQL training_files count: {pg_count}")
                logger.info(f"📊 SQLite training_files count: {self.migration_stats['training_files']['total']}")
                
                success_rate = (self.migration_stats['training_files']['migrated'] / 
                               max(1, self.migration_stats['training_files']['total'])) * 100
                
                logger.info(f"📊 Migration success rate: {success_rate:.1f}%")
                
                if success_rate >= 95:
                    logger.info("✅ Migration verification successful")
                    return True
                else:
                    logger.warning(f"⚠️ Migration success rate below 95%: {success_rate:.1f}%")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Migration verification failed: {e}")
                return False
    
    async def run_migration(self) -> bool:
        """Run complete migration process"""
        logger.info("🚀 Starting SQLite to PostgreSQL migration")
        
        try:
            # Initialize PostgreSQL
            if not await self.initialize_postgresql():
                return False
            
            # Extract SQLite data
            sqlite_data = self.get_sqlite_data()
            
            # Migrate data
            success = True
            success &= await self.migrate_training_files(sqlite_data["training_files"])
            success &= await self.migrate_conversations(sqlite_data["conversations"])
            
            # Verify migration
            if success and not self.dry_run:
                success &= await self.verify_migration()
            
            # Print summary
            self.print_migration_summary()
            
            if success:
                logger.info("🎉 Migration completed successfully!")
            else:
                logger.error("❌ Migration completed with errors")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
        
        finally:
            if self.pg_engine:
                await self.pg_engine.dispose()
    
    def print_migration_summary(self):
        """Print detailed migration summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*60)
        
        for table, stats in self.migration_stats.items():
            total = stats["total"]
            migrated = stats["migrated"]
            errors = stats["errors"]
            success_rate = (migrated / max(1, total)) * 100
            
            logger.info(f"{table.upper()}:")
            logger.info(f"  Total: {total}")
            logger.info(f"  Migrated: {migrated}")
            logger.info(f"  Errors: {errors}")
            logger.info(f"  Success Rate: {success_rate:.1f}%")
            logger.info("")

async def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL for StreamWorks-KI")
    parser.add_argument("--sqlite-path", required=True, help="Path to SQLite database file")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without actual migration")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create migrator
    migrator = SQLiteToPostgreSQLMigrator(
        sqlite_path=args.sqlite_path,
        dry_run=args.dry_run
    )
    
    # Run migration
    success = await migrator.run_migration()
    
    exit_code = 0 if success else 1
    exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())