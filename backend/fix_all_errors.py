"""
🚨 NOTFALL: ALLE FEHLER SOFORT BEHEBEN
"""
import asyncio
import sys
import os
sys.path.append('.')

from sqlalchemy import text
from app.models.database import get_db_session
from app.services.simple_indexer import simple_indexer

async def fix_all_error_files():
    print('🚨 NOTFALL: Alle Error-Files sofort reparieren!')
    
    db = await get_db_session()
    try:
        # Get all error files
        result = await db.execute(text('''
            SELECT id, original_filename, error_message
            FROM training_files_v2 
            WHERE processing_status = 'error' AND is_active = true
        '''))
        
        error_files = result.fetchall()
        print(f'📄 Found {len(error_files)} error files')
        
        success_count = 0
        for file_row in error_files:
            try:
                print(f'🔧 Fixing: {file_row.original_filename}')
                
                # Try to re-index with simple indexer
                result = await simple_indexer.index_file_simple(str(file_row.id), db)
                
                if result['status'] == 'indexed':
                    success_count += 1
                    print(f'✅ Fixed: {file_row.original_filename} ({result["chunk_count"]} chunks)')
                else:
                    print(f'⚠️ Still has issues: {file_row.original_filename}')
                
            except Exception as e:
                print(f'❌ Failed to fix {file_row.original_filename}: {e}')
        
        print(f'🎯 RESULT: {success_count}/{len(error_files)} files fixed!')
        
    except Exception as e:
        print(f'❌ Critical error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(fix_all_error_files())