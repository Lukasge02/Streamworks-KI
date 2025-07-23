"""
🚀 BACKGROUND INDEXER - ENTERPRISE PERFORMANCE
Asynchrone Indexierung für blitzschnelle Uploads
"""
import asyncio
import logging
from typing import Dict, Any

from sqlalchemy import text

from app.models.database import get_db_session
from app.services.enterprise_chromadb_indexer import enterprise_indexer

logger = logging.getLogger(__name__)

class BackgroundIndexer:
    """
    🏎️ BACKGROUND INDEXER - ENTERPRISE PERFORMANCE
    Indexiert Dateien im Hintergrund ohne Upload zu blockieren
    """
    
    def __init__(self):
        self.indexing_queue = asyncio.Queue()
        self.is_running = False
        self.worker_task = None
    
    async def start_worker(self):
        """Start the background worker"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("🚀 Background indexer worker started")
    
    async def stop_worker(self):
        """Stop the background worker"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Background indexer worker stopped")
    
    async def queue_file_for_indexing(self, file_id: str, filename: str):
        """Queue a file for background indexing"""
        await self.indexing_queue.put({
            "file_id": file_id,
            "filename": filename
        })
        logger.info(f"📋 Queued for indexing: {filename}")
    
    async def _worker(self):
        """Background worker that processes indexing queue"""
        while self.is_running:
            try:
                # Wait for next file to index
                file_info = await asyncio.wait_for(
                    self.indexing_queue.get(), 
                    timeout=5.0
                )
                
                await self._index_file(file_info)
                
            except asyncio.TimeoutError:
                # No files to process, continue
                continue
            except Exception as e:
                logger.error(f"❌ Background worker error: {e}")
                await asyncio.sleep(1)
    
    async def _index_file(self, file_info: Dict[str, Any]):
        """Index a single file in background"""
        file_id = file_info["file_id"]
        filename = file_info["filename"]
        
        db = None
        try:
            logger.info(f"🤖 Background indexing: {filename}")
            db = await get_db_session()
            
            # Use ultra simple indexer - SCHNELL UND FUNKTIONIERT
            from app.services.document_indexer import document_indexer
            index_result = await document_indexer.index_file_ultra_simple(file_id, db)
            
            logger.info(f"✅ Background indexing complete: {filename} ({index_result['chunk_count']} chunks)")
            
        except Exception as e:
            logger.error(f"❌ Background indexing failed for {filename}: {e}")
            
            # Mark as error in database
            if db:
                try:
                    await db.execute(text("""
                        UPDATE training_files_v2 
                        SET processing_status = 'error', error_message = :error
                        WHERE id = :file_id
                    """), {"file_id": file_id, "error": str(e)})
                    await db.commit()
                except Exception as db_error:
                    logger.error(f"❌ Failed to update error status: {db_error}")
        
        finally:
            if db:
                await db.close()


# Global instance
background_indexer = BackgroundIndexer()