#!/usr/bin/env python3
"""
🧹 COMPLETE DATA CLEANUP SCRIPT
Removes ALL data from database and ChromaDB to fix inconsistencies
"""

import sqlite3
import chromadb
from chromadb.config import Settings
import shutil
import os
from pathlib import Path

def cleanup_database():
    """Clean up all database tables"""
    print("🗄️ Cleaning up database...")
    
    conn = sqlite3.connect('streamworks_ki.db')
    cursor = conn.cursor()
    
    # Delete all from training_files
    cursor.execute("DELETE FROM training_files")
    deleted_v1 = cursor.rowcount
    
    # Delete all from training_files_v2
    cursor.execute("DELETE FROM training_files_v2")
    deleted_v2 = cursor.rowcount
    
    # Reset auto-increment (if table exists)
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('training_files', 'training_files_v2')")
    except sqlite3.OperationalError:
        pass  # Table doesn't exist, that's fine
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ Deleted {deleted_v1} rows from training_files")
    print(f"   ✅ Deleted {deleted_v2} rows from training_files_v2")

def cleanup_chromadb():
    """Clean up ChromaDB completely"""
    print("🔍 Cleaning up ChromaDB...")
    
    try:
        client = chromadb.PersistentClient(
            path='./data/vector_db_production',
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get current collection
        try:
            collection = client.get_collection('streamworks_production')
            all_chunks = collection.get(include=['metadatas'])
            chunk_count = len(all_chunks['metadatas'] or [])
            
            # Delete collection
            client.delete_collection('streamworks_production')
            print(f"   ✅ Deleted ChromaDB collection with {chunk_count} chunks")
            
            # Recreate empty collection
            client.create_collection('streamworks_production')
            print(f"   ✅ Created new empty ChromaDB collection")
            
        except Exception as e:
            print(f"   ⚠️ Collection not found or already empty: {e}")
            
    except Exception as e:
        print(f"   ❌ ChromaDB cleanup failed: {e}")

def cleanup_uploaded_files():
    """Clean up uploaded files"""
    print("📁 Cleaning up uploaded files...")
    
    upload_dirs = [
        './data/documents',
        './data/uploads',
        './uploads'
    ]
    
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            try:
                shutil.rmtree(upload_dir)
                print(f"   ✅ Deleted {upload_dir}")
            except Exception as e:
                print(f"   ⚠️ Could not delete {upload_dir}: {e}")

def verify_cleanup():
    """Verify that cleanup was successful"""
    print("🔍 Verifying cleanup...")
    
    # Check database
    conn = sqlite3.connect('streamworks_ki.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM training_files")
    v1_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_files_v2")
    v2_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   📊 training_files: {v1_count} rows")
    print(f"   📊 training_files_v2: {v2_count} rows")
    
    # Check ChromaDB
    try:
        client = chromadb.PersistentClient(
            path='./data/vector_db_production',
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection('streamworks_production')
        all_chunks = collection.get(include=['metadatas'])
        chunk_count = len(all_chunks['metadatas'] or [])
        
        print(f"   📊 ChromaDB chunks: {chunk_count}")
        
    except Exception as e:
        print(f"   ❌ ChromaDB verification failed: {e}")
        
    # Final status
    if v1_count == 0 and v2_count == 0 and chunk_count == 0:
        print("   ✅ ALL DATA SUCCESSFULLY CLEANED!")
        return True
    else:
        print("   ❌ CLEANUP INCOMPLETE - some data remains")
        return False

if __name__ == "__main__":
    print("🧹 STARTING COMPLETE DATA CLEANUP")
    print("=" * 50)
    
    cleanup_database()
    cleanup_chromadb()
    cleanup_uploaded_files()
    
    print("\n" + "=" * 50)
    success = verify_cleanup()
    
    if success:
        print("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        print("   You can now upload files with a clean state.")
    else:
        print("⚠️ CLEANUP HAD ISSUES - manual intervention may be needed")