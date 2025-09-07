#!/usr/bin/env python3
"""
Run migrations directly using SQL files
"""

import asyncio
import asyncpg
import os
from pathlib import Path

async def run_migrations():
    """Run migrations directly with asyncpg"""
    print("🚀 Running Database Migrations...")
    
    # Connect to PostgreSQL
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="streamworks",
            password="streamworks2024",
            database="streamworks_ki"
        )
        print("✅ Connected to database")
        
        # Read migration file
        migration_file = Path("database/migrations/002_document_chunks.sql")
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return
        
        migration_sql = migration_file.read_text()
        print(f"📋 Executing migration: {migration_file.name}")
        
        # Execute migration
        await conn.execute(migration_sql)
        print("✅ Migration executed successfully")
        
        # Test tables
        result = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row['table_name'] for row in result]
        print(f"📋 Created tables: {tables}")
        
        await conn.close()
        print("✅ Database setup completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migrations())