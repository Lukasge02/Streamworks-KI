"""
Migration Script - Von SQLite Chaos zu PostgreSQL
"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
import shutil
import sqlite3
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database_postgres import init_database, get_db_session
from app.models.postgres_models import Document, DocumentChunk, ChatSession
from app.core.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLMigration:
    """Complete migration to PostgreSQL"""
    
    def __init__(self):
        self.stats = {
            "files_migrated": 0,
            "documents_converted": 0,
            "chunks_created": 0,
            "errors": []
        }
    
    async def run_complete_migration(self):
        """Execute complete migration process"""
        
        logger.info("🚀 Starting complete migration to PostgreSQL...")
        
        try:
            # 1. Initialize new PostgreSQL database
            await self.init_postgres_database()
            
            # 2. Migrate existing files
            await self.migrate_existing_files()
            
            # 3. Verify migration
            await self.verify_migration()
            
            logger.info("✅ Migration completed successfully!")
            self.print_migration_stats()
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
    
    async def init_postgres_database(self):
        """Initialize PostgreSQL database"""
        logger.info("🗄️ Initializing PostgreSQL database...")
        
        await init_database()
        
        logger.info("✅ PostgreSQL database initialized")
    
    async def migrate_existing_files(self):
        """Migrate files from old chaotic structure"""
        logger.info("📁 Migrating existing files...")
        
        # Old file locations to check
        old_paths = [
            Path("./data/documents"),
            Path("./Training Data"),
            Path("./backend/data/documents")
        ]
        
        new_documents_dir = Path(settings.DATA_PATH) / "documents"
        new_documents_dir.mkdir(parents=True, exist_ok=True)
        
        for old_path in old_paths:
            if old_path.exists():
                await self._migrate_files_from_directory(old_path, new_documents_dir)
        
        logger.info(f"📄 Migrated {self.stats['files_migrated']} files")
    
    async def _migrate_files_from_directory(self, source_dir: Path, target_dir: Path):
        """Migrate files from a source directory"""
        
        for file_path in source_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                try:
                    # Create unique filename to avoid conflicts
                    target_file = target_dir / file_path.name
                    counter = 1
                    original_target = target_file
                    
                    while target_file.exists():
                        stem = original_target.stem
                        suffix = original_target.suffix
                        target_file = target_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    # Copy file
                    shutil.copy2(file_path, target_file)
                    
                    # Create database record
                    await self._create_document_record(target_file)
                    
                    self.stats['files_migrated'] += 1
                    logger.info(f"📄 Migrated: {file_path.name} -> {target_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {file_path}: {e}"
                    self.stats['errors'].append(error_msg)
                    logger.warning(error_msg)
    
    async def _create_document_record(self, file_path: Path):
        """Create database record for migrated file"""
        
        async with get_db_session() as session:
            # Create new document record
            document = Document(
                filename=file_path.name,
                original_filename=file_path.name,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                mime_type=self._get_mime_type(file_path),
                status="uploaded",
                uploaded_at=datetime.now(timezone.utc)
            )
            
            session.add(document)
            await session.commit()
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file"""
        extension_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xml': 'application/xml',
            '.json': 'application/json'
        }
        return extension_map.get(file_path.suffix.lower(), 'application/octet-stream')
    
    async def verify_migration(self):
        """Verify migration success"""
        logger.info("🔍 Verifying migration...")
        
        async with get_db_session() as session:
            from sqlalchemy import text
            
            # Count documents
            result = await session.execute(text("SELECT COUNT(*) FROM documents"))
            doc_count = result.scalar()
            
            # Check file existence
            result = await session.execute(text("SELECT file_path FROM documents"))
            paths = result.fetchall()
            
            missing_files = []
            for (file_path,) in paths:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            logger.info(f"📊 Migration Verification:")
            logger.info(f"   Total documents: {doc_count}")
            logger.info(f"   Missing files: {len(missing_files)}")
            
            if missing_files:
                logger.warning(f"⚠️ Missing files: {missing_files}")
    
    def print_migration_stats(self):
        """Print final migration statistics"""
        logger.info("📊 Migration Statistics:")
        logger.info(f"   Files migrated: {self.stats['files_migrated']}")
        logger.info(f"   Documents converted: {self.stats['documents_converted']}")
        logger.info(f"   Errors encountered: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            logger.info("❌ Errors:")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                logger.info(f"   - {error}")

async def main():
    """Main migration function"""
    migration = PostgreSQLMigration()
    await migration.run_complete_migration()

if __name__ == "__main__":
    asyncio.run(main())