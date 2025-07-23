# WIR GEHEN 8 PROMPTS DURCH, MACHE IMMER NUR DAS, WAS ICH DIR GESAGT HABE!

# 📄 PostgreSQL-optimiertes Simple Document Service

## Ziel
Integration des einfachen, effizienten Document Services in das neue PostgreSQL-System. Fokussiert auf schnelle PDF/TXT → MD Konvertierung mit PostgreSQL Analytics.

## Was implementiert wird:
- **Clean Document Service**: Optimiert für PostgreSQL
- **Batch Converter**: Für bestehende Dateien
- **Analytics Integration**: Performance-Tracking für Bachelor-Arbeit  
- **Unified Storage**: Integration in das neue Storage-System

---

## Phase 1: PostgreSQL-optimiertes Document Service

### 1.1 Erstelle `backend/app/services/document_service.py`
```python
"""
Clean Document Service - PostgreSQL-optimiert
Schnelle PDF/TXT zu Markdown Konvertierung mit Analytics-Integration
"""
import logging
import asyncio
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone
import aiofiles
import pypdf
from io import BytesIO

from app.core.postgres_config import settings
from app.core.unified_storage import storage
from app.core.database_postgres import get_db_session
from app.models.postgres_models import Document, SystemMetric

logger = logging.getLogger(__name__)

@dataclass
class ConversionResult:
    """Result of document conversion with PostgreSQL integration"""
    success: bool
    markdown_content: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: int = 0
    processing_time: float = 0.0
    pages_processed: int = 0
    document_id: Optional[str] = None

@dataclass
class ConversionStats:
    """Conversion statistics for PostgreSQL analytics"""
    total_files: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    total_size_mb: float = 0.0

class DocumentService:
    """PostgreSQL-optimized document conversion service"""
    
    def __init__(self):
        self.storage = storage
        self.stats = ConversionStats()
        
    async def convert_pdf_to_markdown(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Convert PDF to clean Markdown with PostgreSQL logging"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # PDF in Memory laden
            pdf_stream = BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_stream)
            
            if not reader.pages:
                await self._log_conversion_error("PDF contains no pages", file_path)
                return ConversionResult(
                    success=False,
                    error_message="PDF contains no pages"
                )
            
            # Text von allen Seiten extrahieren
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    # RAG-optimierte Bereinigung
                    cleaned = self._clean_text_for_rag(text)
                    if cleaned:
                        text_parts.append(f"## Seite {page_num}\n\n{cleaned}")
            
            if not text_parts:
                await self._log_conversion_error("No extractable text found", file_path)
                return ConversionResult(
                    success=False,
                    error_message="No extractable text found in PDF"
                )
            
            # Markdown erstellen
            filename = Path(file_path).stem
            markdown_content = f"# {filename}\n\n" + "\n\n".join(text_parts)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # PostgreSQL Performance Logging
            await self._log_conversion_performance(
                "pdf_conversion", processing_time, len(text_parts), file_path
            )
            
            return ConversionResult(
                success=True,
                markdown_content=markdown_content,
                file_size=len(markdown_content),
                processing_time=processing_time,
                pages_processed=len(text_parts)
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"PDF conversion failed: {e}")
            await self._log_conversion_error(str(e), file_path)
            
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def convert_txt_to_markdown(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Convert TXT to structured Markdown with PostgreSQL logging"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Text dekodieren mit verschiedenen Encodings
            text = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                await self._log_conversion_error("Could not decode text file", file_path)
                return ConversionResult(
                    success=False,
                    error_message="Could not decode text file"
                )
            
            text = text.strip()
            if not text:
                await self._log_conversion_error("File is empty", file_path)
                return ConversionResult(
                    success=False,
                    error_message="File is empty"
                )
            
            # Markdown strukturieren für RAG-Optimierung
            filename = Path(file_path).stem
            
            if text.startswith('#'):
                markdown_content = text
            else:
                # RAG-optimierte Struktur hinzufügen
                cleaned_text = self._clean_text_for_rag(text)
                markdown_content = f"# {filename}\n\n{cleaned_text}"
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # PostgreSQL Performance Logging
            await self._log_conversion_performance(
                "txt_conversion", processing_time, 1, file_path
            )
            
            return ConversionResult(
                success=True,
                markdown_content=markdown_content,
                file_size=len(markdown_content),
                processing_time=processing_time,
                pages_processed=1
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"TXT conversion failed: {e}")
            await self._log_conversion_error(str(e), file_path)
            
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _clean_text_for_rag(self, text: str) -> str:
        """RAG-optimierte Text-Bereinigung für besseres Chunking"""
        
        # Mehrfache Leerzeilen reduzieren
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        text = '\n\n'.join(para.strip() for para in text.split('\n\n') if para.strip())
        
        # Extrem lange Zeilen umbrechen (optimal für RAG-Chunking)
        lines = []
        for line in text.split('\n'):
            if len(line) > 200:
                # Lange Zeilen an Satzenden umbrechen
                import re
                sentences = re.split(r'(?<=[.!?])\s+', line)
                lines.extend(sentences)
            else:
                lines.append(line)
        
        # Doppelte Leerzeichen entfernen
        text = '\n'.join(lines)
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n ', '\n')
        
        return text
    
    async def save_markdown(self, markdown_content: str, filename: str) -> str:
        """Save markdown using unified storage system"""
        try:
            output_path = self.storage.get_converted_path(filename)
            
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
            
            logger.info(f"✅ Markdown saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save markdown: {e}")
            raise
    
    async def convert_and_save(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Universal converter with PostgreSQL database integration"""
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name
        
        # Konvertieren
        if file_ext == '.pdf':
            result = await self.convert_pdf_to_markdown(file_path, file_content)
        elif file_ext in ['.txt', '.md']:
            result = await self.convert_txt_to_markdown(file_path, file_content)
        else:
            logger.warning(f"⚠️ Unsupported format: {file_ext}")
            return ConversionResult(
                success=False,
                error_message=f"Unsupported file format: {file_ext}"
            )
        
        if result.success:
            # Speichern
            try:
                output_path = await self.save_markdown(result.markdown_content, filename)
                result.output_path = output_path
                
                # PostgreSQL Database Record erstellen
                document_id = await self._create_document_record(
                    filename, file_path, output_path, result
                )
                result.document_id = document_id
                
                logger.info(f"✅ Document processed: {filename} → {document_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save/record document: {e}")
                result.success = False
                result.error_message = f"Save failed: {e}"
        
        # Statistiken aktualisieren
        await self._update_stats(result, len(file_content))
        
        return result
    
    async def _create_document_record(self, filename: str, file_path: str, 
                                    output_path: str, result: ConversionResult) -> str:
        """Create PostgreSQL document record with analytics data"""
        
        async with get_db_session() as session:
            # Create document record
            document = Document(
                filename=filename,
                original_filename=filename,
                file_path=file_path,
                converted_path=output_path,
                file_size=result.file_size,
                mime_type=self._get_mime_type(Path(filename)),
                status="converted",
                conversion_time_seconds=result.processing_time,
                uploaded_at=datetime.now(timezone.utc),
                converted_at=datetime.now(timezone.utc),
                processing_metadata={
                    "pages_processed": result.pages_processed,
                    "conversion_method": "simple_document_service",
                    "rag_optimized": True
                }
            )
            
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            logger.info(f"📝 Document record created: {document.id}")
            return str(document.id)
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file"""
        extension_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown'
        }
        return extension_map.get(file_path.suffix.lower(), 'application/octet-stream')
    
    async def _log_conversion_performance(self, conversion_type: str, processing_time: float,
                                        pages: int, file_path: str):
        """Log conversion performance to PostgreSQL for analytics"""
        
        try:
            async with get_db_session() as session:
                metric = SystemMetric(
                    metric_category="performance",
                    metric_name=f"{conversion_type}_time",
                    metric_value=processing_time,
                    metric_unit="seconds",
                    tags={
                        "file_type": Path(file_path).suffix.lower(),
                        "pages_processed": pages,
                        "service": "document_service"
                    }
                )
                
                session.add(metric)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log performance metric: {e}")
    
    async def _log_conversion_error(self, error_message: str, file_path: str):
        """Log conversion errors to PostgreSQL"""
        
        try:
            async with get_db_session() as session:
                metric = SystemMetric(
                    metric_category="error",
                    metric_name="conversion_error",
                    metric_value=1,
                    metric_unit="count",
                    tags={
                        "error_message": error_message[:200],  # Truncate long errors
                        "file_type": Path(file_path).suffix.lower(),
                        "service": "document_service"
                    }
                )
                
                session.add(metric)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log error metric: {e}")
    
    async def _update_stats(self, result: ConversionResult, file_size_bytes: int):
        """Update internal statistics"""
        self.stats.total_files += 1
        self.stats.total_size_mb += file_size_bytes / 1024 / 1024
        
        if result.success:
            self.stats.successful_conversions += 1
        else:
            self.stats.failed_conversions += 1
        
        self.stats.total_processing_time += result.processing_time
        self.stats.average_processing_time = (
            self.stats.total_processing_time / self.stats.total_files
        )
    
    def get_stats(self) -> ConversionStats:
        """Get current conversion statistics"""
        return self.stats

# Global service instance
document_service = DocumentService()
```

---

## Phase 2: Batch Converter für PostgreSQL

### 2.1 Erstelle `backend/app/utils/batch_converter.py`
```python
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
                from app.models.postgres_models import SystemMetric
                
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
```

---

## Phase 3: API Integration

### 3.1 Update `backend/app/api/v1/documents.py`
```python
"""
Document API - PostgreSQL-optimiert
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.services.document_service import document_service
from app.utils.batch_converter import batch_converter
from app.core.database_postgres import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_and_convert(
    file: UploadFile = File(...),
    category: str = "general",
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Upload and convert document to markdown"""
    
    try:
        # Validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_extensions = {'.pdf', '.txt', '.md'}
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Convert and save
        result = await document_service.convert_and_save(file.filename, file_content)
        
        if not result.success:
            raise HTTPException(
                status_code=422, 
                detail=f"Conversion failed: {result.error_message}"
            )
        
        return JSONResponse({
            "success": True,
            "message": "Document converted successfully",
            "document_id": result.document_id,
            "original_filename": file.filename,
            "output_path": result.output_path,
            "processing_time": result.processing_time,
            "pages_processed": result.pages_processed,
            "file_size": result.file_size
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch-convert")
async def batch_convert_existing(
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Batch convert all existing PDF and TXT files"""
    
    try:
        # Start conversion in background
        background_tasks.add_task(
            batch_converter.convert_all_documents, 
            overwrite=overwrite
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Batch conversion started (overwrite={overwrite})",
            "note": "Check logs for progress updates"
        })
        
    except Exception as e:
        logger.error(f"Batch conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversion-stats")
async def get_conversion_stats(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Get document conversion statistics"""
    
    try:
        stats = document_service.get_stats()
        
        return JSONResponse({
            "service_stats": {
                "total_files": stats.total_files,
                "successful_conversions": stats.successful_conversions,
                "failed_conversions": stats.failed_conversions,
                "success_rate": f"{(stats.successful_conversions/max(stats.total_files,1)*100):.1f}%",
                "total_processing_time": f"{stats.total_processing_time:.2f}s",
                "average_processing_time": f"{stats.average_processing_time:.2f}s",
                "total_size_mb": f"{stats.total_size_mb:.2f} MB"
            }
        })
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def document_service_health() -> JSONResponse:
    """Health check for document service"""
    
    return JSONResponse({
        "service": "document_service",
        "status": "healthy",
        "database": "postgresql",
        "storage": "unified_storage",
        "supported_formats": [".pdf", ".txt", ".md"],
        "features": ["conversion", "batch_processing", "analytics_logging"]
    })
```

---

## Phase 4: CLI Tool für Testing

### 4.1 Erstelle `backend/scripts/convert_documents.py`
```python
#!/usr/bin/env python3
"""
Document Conversion CLI Tool - PostgreSQL-optimiert
"""
import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.document_service import document_service
from app.utils.batch_converter import batch_converter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def convert_single_file(file_path: str):
    """Convert a single file"""
    
    logger.info(f"🔄 Converting single file: {file_path}")
    
    file_obj = Path(file_path)
    if not file_obj.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    with open(file_obj, 'rb') as f:
        content = f.read()
    
    result = await document_service.convert_and_save(file_path, content)
    
    if result.success:
        logger.info(f"✅ Successfully converted:")
        logger.info(f"   Document ID: {result.document_id}")
        logger.info(f"   Output: {result.output_path}")
        logger.info(f"   Processing time: {result.processing_time:.2f}s")
        logger.info(f"   Pages: {result.pages_processed}")
    else:
        logger.error(f"❌ Conversion failed: {result.error_message}")

async def convert_batch(source_dir: str, overwrite: bool = False):
    """Convert all files in a directory"""
    
    logger.info(f"🚀 Starting batch conversion from: {source_dir}")
    
    converter = batch_converter if not source_dir else PostgreSQLBatchConverter(source_dir)
    result = await converter.convert_all_documents(overwrite=overwrite)
    
    if "error" in result:
        logger.error(f"❌ Batch conversion failed: {result['error']}")
    else:
        logger.info("📊 Batch conversion completed!")
        stats = result.get("stats", {})
        logger.info(f"   Success rate: {result.get('success_rate', 0):.1f}%")
        logger.info(f"   Total time: {result.get('batch_processing_time', 0):.2f}s")

async def show_stats():
    """Show current conversion statistics"""
    
    stats = document_service.get_stats()
    
    print("\n📊 Document Service Statistics:")
    print(f"   Total files processed: {stats.total_files}")
    print(f"   Successful conversions: {stats.successful_conversions}")
    print(f"   Failed conversions: {stats.failed_conversions}")
    print(f"   Success rate: {(stats.successful_conversions/max(stats.total_files,1)*100):.1f}%")
    print(f"   Average processing time: {stats.average_processing_time:.2f}s")
    print(f"   Total data processed: {stats.total_size_mb:.2f} MB")

def main():
    parser = argparse.ArgumentParser(description="PostgreSQL Document Conversion Tool")
    parser.add_argument("--file", help="Convert single file")
    parser.add_argument("--batch", help="Batch convert directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing conversions")
    parser.add_argument("--stats", action="store_true", help="Show conversion statistics")
    
    args = parser.parse_args()
    
    if args.stats:
        asyncio.run(show_stats())
    elif args.file:
        asyncio.run(convert_single_file(args.file))
    elif args.batch:
        asyncio.run(convert_batch(args.batch, args.overwrite))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

## 🚀 Deployment Commands

```bash
# 1. Document Service implementieren
# → Gib dieses Markdown an Claude Code

# 2. Batch-Konvertierung testen
python backend/scripts/convert_documents.py --batch ./data/documents --overwrite

# 3. API testen
curl -X POST "http://localhost:8000/api/v1/documents/batch-convert"

# 4. Statistiken anzeigen
python backend/scripts/convert_documents.py --stats

# 5. Health Check
curl "http://localhost:8000/api/v1/documents/health"
```

## 🎯 Erwartete Ergebnisse

**✅ Nach der Implementation:**
- Alle PDF/TXT Dateien werden zu sauberem Markdown konvertiert
- PostgreSQL Analytics tracken Performance-Daten  
- Unified Storage System organisiert alle Dateien
- API Endpoints für Upload und Batch-Processing
- CLI Tool für Development und Testing

**📊 Bachelor-Arbeit Benefits:**
- Performance-Daten in PostgreSQL für wissenschaftliche Auswertung
- Batch-Processing Statistiken
- RAG-optimierte Markdown-Ausgabe
- Enterprise-Standard Code-Qualität

**Das Document Service ist perfekt auf Ihr neues PostgreSQL-System abgestimmt! 🎯**