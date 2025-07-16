#!/usr/bin/env python3
"""
Migrate existing training files to the new enterprise document system
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
import hashlib
import os
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings

def migrate_existing_files():
    """Migrate existing files from training_files to training_files_v2"""
    print("🔄 Migrating existing files to new document system...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    with engine.begin() as conn:
        # Get Q&A category ID
        result = conn.execute(text("SELECT id FROM document_categories WHERE slug = 'qa'"))
        qa_category_id = result.scalar()
        
        if not qa_category_id:
            print("❌ Q&A category not found!")
            return
        
        # Get default folder (Streamworks F1)
        result = conn.execute(text("SELECT id FROM document_folders WHERE slug = 'streamworks-f1'"))
        default_folder_id = result.scalar()
        
        # Check if old training_files table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'training_files'
            )
        """))
        
        if not result.scalar():
            print("ℹ️  No existing training_files table found. Fresh installation.")
            return
        
        # Get existing files
        result = conn.execute(text("""
            SELECT id, filename, file_hash, file_type, file_size, user_id, upload_date, status, chunk_count
            FROM training_files
            WHERE status = 'completed'
        """))
        
        existing_files = result.fetchall()
        
        if not existing_files:
            print("ℹ️  No existing files to migrate.")
            return
        
        print(f"📊 Found {len(existing_files)} files to migrate")
        
        # Migrate each file
        migrated = 0
        for file in existing_files:
            try:
                # Generate storage path
                storage_path = f"data/documents/qa/streamworks-f1/{file.filename}"
                
                # Check if already migrated
                exists = conn.execute(text(
                    "SELECT COUNT(*) FROM training_files_v2 WHERE file_hash = :hash"
                ), {"hash": file.file_hash}).scalar()
                
                if exists > 0:
                    print(f"⏭️  Skipping {file.filename} - already migrated")
                    continue
                
                # Insert into new table
                conn.execute(text("""
                    INSERT INTO training_files_v2 (
                        id, category_id, folder_id, original_filename, 
                        storage_path, file_hash, file_size, file_type,
                        processing_status, chunk_count, uploaded_by,
                        created_at, processed_at
                    ) VALUES (
                        :id, :category_id, :folder_id, :filename,
                        :storage_path, :file_hash, :file_size, :file_type,
                        :status, :chunk_count, :user_id,
                        :created_at, :processed_at
                    )
                """), {
                    "id": file.id,
                    "category_id": qa_category_id,
                    "folder_id": default_folder_id,
                    "filename": file.filename,
                    "storage_path": storage_path,
                    "file_hash": file.file_hash,
                    "file_size": file.file_size,
                    "file_type": file.file_type,
                    "status": file.status,
                    "chunk_count": file.chunk_count or 0,
                    "user_id": file.user_id,
                    "created_at": file.upload_date,
                    "processed_at": file.upload_date
                })
                
                migrated += 1
                print(f"✅ Migrated: {file.filename}")
                
            except Exception as e:
                print(f"❌ Failed to migrate {file.filename}: {e}")
        
        print(f"\n🎉 Migration complete! Migrated {migrated}/{len(existing_files)} files")
        
        # Show summary
        result = conn.execute(text("""
            SELECT 
                dc.name as category,
                df.name as folder,
                COUNT(*) as file_count
            FROM training_files_v2 tf
            JOIN document_categories dc ON tf.category_id = dc.id
            LEFT JOIN document_folders df ON tf.folder_id = df.id
            GROUP BY dc.name, df.name
            ORDER BY dc.name, df.name
        """))
        
        print("\n📈 Document Distribution:")
        for row in result:
            folder = row.folder or "No Folder"
            print(f"  {row.category} / {folder}: {row.file_count} files")

if __name__ == "__main__":
    migrate_existing_files()