"""
Run AI Summary Migration Script
Safely adds AI summary caching fields to the documents table
"""

import asyncio
import logging
from database import AsyncSessionLocal
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Run the AI summary migration"""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting AI Summary migration...")
            
            # Check if columns already exist
            check_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'documents' 
            AND column_name IN ('ai_summary', 'summary_key_points', 'summary_generated_at');
            """
            
            result = await db.execute(text(check_sql))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if len(existing_columns) == 3:
                logger.info("✅ AI Summary columns already exist. Migration skipped.")
                return
            
            logger.info(f"Found {len(existing_columns)} existing columns: {existing_columns}")
            
            # Add missing columns
            migration_statements = []
            
            if 'ai_summary' not in existing_columns:
                migration_statements.append("ALTER TABLE documents ADD COLUMN ai_summary TEXT")
                
            if 'summary_key_points' not in existing_columns:
                migration_statements.append("ALTER TABLE documents ADD COLUMN summary_key_points JSONB")
                
            if 'summary_generated_at' not in existing_columns:
                migration_statements.append("ALTER TABLE documents ADD COLUMN summary_generated_at TIMESTAMP")
            
            # Execute migration statements
            for statement in migration_statements:
                logger.info(f"Executing: {statement}")
                await db.execute(text(statement))
            
            # Add index for performance
            try:
                index_sql = "CREATE INDEX IF NOT EXISTS idx_documents_summary_generated_at ON documents(summary_generated_at)"
                logger.info("Creating performance index...")
                await db.execute(text(index_sql))
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
            
            await db.commit()
            logger.info("✅ AI Summary migration completed successfully!")
            
            # Verify the migration
            verify_sql = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'documents' 
            AND column_name IN ('ai_summary', 'summary_key_points', 'summary_generated_at')
            ORDER BY column_name;
            """
            
            result = await db.execute(text(verify_sql))
            columns = result.fetchall()
            
            logger.info("Migration verification:")
            for col_name, col_type in columns:
                logger.info(f"  ✓ {col_name}: {col_type}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(run_migration())