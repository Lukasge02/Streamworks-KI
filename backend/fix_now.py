"""
🚨 SOFORT ALLE FEHLER BEHEBEN - ULTRA SIMPLE
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from app.models.database import get_db_session
from app.services.ultra_simple_indexer import ultra_simple_indexer

async def fix_now():
    print('🚨 SOFORT FIX - ULTRA SIMPLE')
    
    db = await get_db_session()
    try:
        # Get one error file
        result = await db.execute(text('''
            SELECT id, original_filename
            FROM training_files_v2 
            WHERE processing_status = 'error' AND is_active = true
            LIMIT 1
        '''))
        
        error_file = result.first()
        if error_file:
            print(f'🔧 Testing: {error_file.original_filename}')
            
            result = await ultra_simple_indexer.index_file_ultra_simple(str(error_file.id), db)
            print(f'✅ ERFOLG: {result}')
        else:
            print('❌ No error files found')
        
    except Exception as e:
        print(f'❌ FEHLER: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(fix_now())