"""
PostgreSQL-optimierter Batch Converter für bestehende Dateien
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import aiofiles
from datetime import datetime

from app.services.document_service import document_service
from app.core.unified_storage import storage
from app.core.database_postgres import get_db_session
from app.models.postgres_models import SystemMetric
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PostgreSQLBatchConverter:
    """Batch conversion mit PostgreSQL Analytics"""
    
    def __init__(self, source_dir: str = None):
        self.source_dir = Path(source_dir or storage.paths["documents"])
        self.results: List[Dict[str, Any]] = []
        self.stats = {
            "total_found": 0,
            "already_converted": 0,
            "newly_converted": 0,
            "conversion_errors": 0,
            "total_processing_time": 0.0
        }
    
    async def convert_all_documents(self, overwrite: bool = False) -> Dict[str, Any]:
        """Convert all PDF and TXT files with PostgreSQL deduplication"""
        
        start_time = datetime.now()
        logger.info(f"🚀 Starting batch conversion from: {self.source_dir}")
        
        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return {"error": "Source directory not found"}
        
        # Finde alle PDF und TXT Dateien
        files_to_convert = []
        for pattern in ['*.pdf', '*.txt']:
            files_to_convert.extend(self.source_dir.rglob(pattern))
        
        if not files_to_convert:
            logger.info("No PDF or TXT files found")
            return {
                "message": "No files found to convert", 
                "files_processed": 0,
                "stats": self.stats
            }
        
        self.stats["total_found"] = len(files_to_convert)
        logger.info(f"📄 Found {len(files_to_convert)} files to convert")
        
        # Check welche bereits konvertiert sind (PostgreSQL)
        if not overwrite:
            files_to_convert = await self._filter_already_converted(files_to_convert)
            logger.info(f"📋 {len(files_to_convert)} files need conversion")
        
        if not files_to_convert:
            return {
                "message": "All files already converted",
                "stats": self.stats
            }
        
        # Parallel conversion (begrenzt auf 5 gleichzeitig)
        semaphore = asyncio.Semaphore(5)
        conversion_tasks = []
        
        for file_path in files_to_convert:
            task = self._convert_single_file_with_semaphore(semaphore, file_path)
            conversion_tasks.append(task)
        
        # Execute conversions
        results = await asyncio.gather(*conversion_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Conversion failed for {files_to_convert[i]}: {result}")
                self.stats["conversion_errors"] += 1
                self.results.append({
                    "file": str(files_to_convert[i]),
                    "success": False,
                    "error": str(result)
                })
            elif result and result.get('success'):
                self.stats["newly_converted"] += 1
                self.stats["total_processing_time"] += result.get("processing_time", 0)
                self.results.append(result)
            else:
                self.stats["conversion_errors"] += 1
                if result:
                    self.results.append(result)
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Final summary
        summary = {
            "batch_processing_time": total_time,
            "stats": self.stats,
            "average_processing_time": (
                self.stats["total_processing_time"] / max(self.stats["newly_converted"], 1)
            ),
            "success_rate": (
                self.stats["newly_converted"] / max(self.stats["total_found"], 1) * 100
            ),
            "results": self.results
        }
        
        logger.info(f"✅ Batch conversion completed:")
        logger.info(f"   Total files: {self.stats['total_found']}")
        logger.info(f"   Newly converted: {self.stats['newly_converted']}")
        logger.info(f"   Already converted: {self.stats['already_converted']}")
        logger.info(f"   Errors: {self.stats['conversion_errors']}")
        logger.info(f"   Success rate: {summary['success_rate']:.1f}%")
        
        # Log batch completion to PostgreSQL
        await self._log_batch_completion(summary)
        
        return summary
    
    async def _filter_already_converted(self, files: List[Path]) -> List[Path]:
        """Filter out files that are already converted (PostgreSQL check)"""
        
        files_needing_conversion = []
        
        async with get_db_session() as session:
            for file_path in files:
                # Check if document already exists in PostgreSQL
                result = await session.execute(
                    text("SELECT id FROM documents WHERE filename = :filename"),
                    {"filename": file_path.name}
                )
                
                existing = result.first()
                if existing:
                    self.stats["already_converted"] += 1
                    logger.debug(f"⏭️ Already converted: {file_path.name}")
                else:
                    files_needing_conversion.append(file_path)
        
        return files_needing_conversion
    
    async def _convert_single_file_with_semaphore(self, semaphore: asyncio.Semaphore, 
                                                 file_path: Path) -> Dict[str, Any]:
        """Convert single file with concurrency control"""
        
        async with semaphore:
            return await self._convert_single_file(file_path)
    
    async def _convert_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Convert a single file and return detailed result"""
        
        try:
            logger.info(f"🔄 Converting: {file_path.name}")
            
            # Read file
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            # Convert using document service
            result = await document_service.convert_and_save(str(file_path), file_content)
            
            if result.success:
                return {
                    "file": str(file_path),
                    "output_file": result.output_path,
                    "document_id": result.document_id,
                    "success": True,
                    "pages_processed": result.pages_processed,
                    "processing_time": result.processing_time,
                    "file_size": result.file_size
                }
            else:
                return {
                    "file": str(file_path),
                    "success": False,
                    "error": result.error_message
                }
        
        except Exception as e:
            logger.error(f"Error converting {file_path}: {e}")
            return {
                "file": str(file_path),
                "success": False,
                "error": str(e)
            }
    
    async def _log_batch_completion(self, summary: Dict[str, Any]):
        """Log batch conversion completion to PostgreSQL"""
        
        try:
            async with get_db_session() as session:
                metric = SystemMetric(
                    metric_category="batch_processing",
                    metric_name="document_conversion_batch",
                    metric_value=summary["stats"]["newly_converted"],
                    metric_unit="files",
                    tags={
                        "total_found": summary["stats"]["total_found"],
                        "success_rate": round(summary["success_rate"], 2),
                        "processing_time": round(summary["batch_processing_time"], 2),
                        "service": "batch_converter"
                    }
                )
                
                session.add(metric)
                await session.commit()
                
                logger.info("📊 Batch completion logged to PostgreSQL")
                
        except Exception as e:
            logger.warning(f"Failed to log batch completion: {e}")

# Global batch converter
batch_converter = PostgreSQLBatchConverter()