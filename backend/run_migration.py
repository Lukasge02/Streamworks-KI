#!/usr/bin/env python3
"""
Run Enterprise Document System Migration
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings

def run_migration():
    """Execute the migration"""
    print("🚀 Starting Enterprise Document System Migration...")
    
    # Create sync engine for migration
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    try:
        with engine.begin() as conn:
            # Read migration file
            migration_path = Path(__file__).parent / "database" / "migrations" / "001_enterprise_document_system.sql"
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            
            # Execute migration
            conn.execute(text(migration_sql))
            
            print("✅ Migration completed successfully!")
            
            # Verify categories
            result = conn.execute(text("SELECT name, slug FROM document_categories ORDER BY sort_order"))
            categories = result.fetchall()
            
            print("\n📁 Created Categories:")
            for cat in categories:
                print(f"  - {cat.name} ({cat.slug})")
            
            # Verify folders
            result = conn.execute(text("""
                SELECT df.name, df.slug, dc.name as category 
                FROM document_folders df 
                JOIN document_categories dc ON df.category_id = dc.id 
                ORDER BY dc.sort_order, df.sort_order
            """))
            folders = result.fetchall()
            
            print("\n📂 Created Folders:")
            for folder in folders:
                print(f"  - {folder.category}/{folder.name} ({folder.slug})")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()