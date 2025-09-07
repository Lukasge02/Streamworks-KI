#!/usr/bin/env python3
"""
Run Docling chunks migration directly on Supabase
No local PostgreSQL needed!
"""

import asyncio
import asyncpg
from pathlib import Path

async def run_migration():
    """Execute migration on Supabase"""
    print("🚀 Connecting to Supabase PostgreSQL...")
    
    # Supabase connection
    try:
        conn = await asyncpg.connect(
            host="db.snzxgfmewxbeevoywula.supabase.co",
            port=5432,
            user="postgres",
            password="Specki2002!",
            database="postgres"
        )
        print("✅ Connected to Supabase")
        
        # Check existing tables
        existing_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        print(f"\n📋 Existing tables: {[t['table_name'] for t in existing_tables]}")
        
        # Check if document_chunks already exists
        chunk_table_exists = any(t['table_name'] == 'document_chunks' for t in existing_tables)
        
        if chunk_table_exists:
            print("\n⚠️  Table 'document_chunks' already exists!")
            # Check if it has the correct structure
            columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = 'document_chunks'
            """)
            column_names = [c['column_name'] for c in columns]
            
            # Check for the renamed column
            if 'metadata' in column_names and 'chunk_metadata' not in column_names:
                print("🔧 Updating table structure (renaming metadata to chunk_metadata)...")
                await conn.execute("ALTER TABLE document_chunks RENAME COLUMN metadata TO chunk_metadata")
                print("✅ Column renamed")
            elif 'chunk_metadata' in column_names:
                print("✅ Table structure is already up to date")
            
            # Still add missing columns to documents table if needed
            doc_columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = 'documents'
            """)
            doc_column_names = [c['column_name'] for c in doc_columns]
            
            if 'chunk_count' not in doc_column_names:
                print("🔧 Adding chunk_count to documents table...")
                await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunk_count INTEGER DEFAULT 0")
                print("✅ Added chunk_count")
                
            if 'processing_metadata' not in doc_column_names:
                print("🔧 Adding processing_metadata to documents table...")
                await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_metadata JSONB DEFAULT '{}'")
                print("✅ Added processing_metadata")
        
        else:
            # Table doesn't exist, run full migration
            # Read and execute migration
            migration_file = Path("backend/database/migrations/002_document_chunks.sql")
            if not migration_file.exists():
                print(f"❌ Migration file not found: {migration_file}")
                await conn.close()
                return
            
            migration_sql = migration_file.read_text()
            print(f"\n📝 Executing migration from: {migration_file.name}")
            
            # Execute migration
            await conn.execute(migration_sql)
            print("✅ Migration executed successfully!")
        
        # Verify new table
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'document_chunks'
            ORDER BY ordinal_position
        """)
        
        print("\n🔍 Document chunks table structure:")
        for col in columns[:10]:  # Show first 10 columns
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
        
        if len(columns) > 10:
            print(f"  ... and {len(columns) - 10} more columns")
        
        # Check if documents table has new columns
        doc_columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'documents' 
            AND column_name IN ('chunk_count', 'processing_metadata')
        """)
        
        if doc_columns:
            print("\n✅ Documents table updated with:")
            for col in doc_columns:
                print(f"  - {col['column_name']}")
        
        # Test cascade deletion setup
        cascade_test = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.referential_constraints
            WHERE constraint_name LIKE '%document_chunks%'
            AND delete_rule = 'CASCADE'
        """)
        
        if cascade_test > 0:
            print(f"\n✅ CASCADE deletion configured ({cascade_test} constraint)")
        
        await conn.close()
        print("\n🎉 Supabase is ready for Docling integration!")
        print("\n📋 Next steps:")
        print("1. Start backend: cd backend && uvicorn main:app --reload")
        print("2. Upload a document via API or frontend")
        print("3. Check processing status and chunks")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_migration())