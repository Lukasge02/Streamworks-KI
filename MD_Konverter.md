# 🚀 Claude Code Refactoring Plan - StreamWorks KI Clean Architecture

## Ziel
Refactoring des bestehenden chaotischen Systems zu einer sauberen Enterprise-Architektur mit fokussierter PDF/TXT → MD Konvertierung für optimales RAG-Chunking.

## Phase 1: Code Cleanup & Struktur bereinigen

### 1.1 Backup-Ordner und doppelte Services entfernen
```bash
# Löschen überflüssiger Backup-Ordner
rm -rf backend/.backup_rag_services/

# Löschen doppelter Service-Dateien
rm backend/app/services/training_service_v2.py
rm backend/app/services/enterprise_intelligent_chunker.py
rm backend/app/services/enterprise_chromadb_indexer.py
rm backend/app/services/production_document_processor.py
```

### 1.2 Neue saubere Ordnerstruktur erstellen
```
backend/app/
├── core/
│   ├── config.py           # Zentrale Konfiguration
│   ├── database.py         # DB Connection & Models
│   └── exceptions.py       # Custom Exceptions
├── services/
│   ├── document_service.py # Clean PDF/TXT → MD
│   ├── rag_service.py      # Sauberer RAG Service
│   └── mistral_service.py  # LLM Integration
├── api/v1/
│   ├── documents.py        # Upload/Convert API
│   ├── chat.py            # Q&A API
│   └── health.py          # System Health
└── utils/
    └── file_utils.py       # Helper Functions
```

## Phase 2: Clean Document Service Implementation

### 2.1 Erstelle `backend/app/services/document_service.py`
```python
"""
Clean Document Service - PDF/TXT to Markdown Conversion
Fokussiert auf schnelle, zuverlässige Konvertierung für RAG-Optimierung
"""
import logging
import asyncio
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import aiofiles
import pypdf
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class ConversionResult:
    """Result of document conversion"""
    success: bool
    markdown_content: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: int = 0
    processing_time: float = 0.0
    pages_processed: int = 0

@dataclass
class ConversionStats:
    """Conversion statistics"""
    total_files: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0

class DocumentService:
    """Clean, fast document conversion service"""
    
    def __init__(self, output_base_path: str = "./data/documents"):
        self.output_base_path = Path(output_base_path)
        self.stats = ConversionStats()
        
    async def convert_pdf_to_markdown(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Convert PDF to clean Markdown for RAG optimization"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # PDF in Memory laden
            pdf_stream = BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_stream)
            
            if not reader.pages:
                return ConversionResult(
                    success=False,
                    error_message="PDF contains no pages"
                )
            
            # Text von allen Seiten extrahieren
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    # Einfache aber effektive Bereinigung
                    cleaned = self._clean_text(text)
                    if cleaned:
                        text_parts.append(f"## Seite {page_num}\n\n{cleaned}")
            
            if not text_parts:
                return ConversionResult(
                    success=False,
                    error_message="No extractable text found in PDF"
                )
            
            # Markdown erstellen
            filename = Path(file_path).stem
            markdown_content = f"# {filename}\n\n" + "\n\n".join(text_parts)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
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
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def convert_txt_to_markdown(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Convert TXT to structured Markdown"""
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
                return ConversionResult(
                    success=False,
                    error_message="Could not decode text file"
                )
            
            text = text.strip()
            if not text:
                return ConversionResult(
                    success=False,
                    error_message="File is empty"
                )
            
            # Markdown strukturieren
            filename = Path(file_path).stem
            
            # Wenn bereits Markdown-Header vorhanden, beibehalten
            if text.startswith('#'):
                markdown_content = text
            else:
                # Einfache Struktur hinzufügen
                cleaned_text = self._clean_text(text)
                markdown_content = f"# {filename}\n\n{cleaned_text}"
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
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
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text for better RAG performance"""
        # Mehrfache Leerzeilen reduzieren
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        text = '\n\n'.join(para.strip() for para in text.split('\n\n') if para.strip())
        
        # Extrem lange Zeilen umbrechen (für besseres Chunking)
        lines = []
        for line in text.split('\n'):
            if len(line) > 200:
                # Lange Zeilen an Satzenden umbrechen
                import re
                sentences = re.split(r'(?<=[.!?])\s+', line)
                lines.extend(sentences)
            else:
                lines.append(line)
        
        return '\n'.join(lines)
    
    async def save_markdown(self, markdown_content: str, output_path: str) -> bool:
        """Save markdown with proper error handling"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
            
            logger.info(f"✅ Markdown saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save markdown: {e}")
            return False
    
    async def convert_file(self, file_path: str, file_content: bytes) -> ConversionResult:
        """Universal file converter - detects format automatically"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            result = await self.convert_pdf_to_markdown(file_path, file_content)
        elif file_ext in ['.txt', '.md']:
            result = await self.convert_txt_to_markdown(file_path, file_content)
        else:
            return ConversionResult(
                success=False,
                error_message=f"Unsupported file format: {file_ext}"
            )
        
        # Statistiken aktualisieren
        self.stats.total_files += 1
        if result.success:
            self.stats.successful_conversions += 1
        else:
            self.stats.failed_conversions += 1
        
        self.stats.total_processing_time += result.processing_time
        self.stats.average_processing_time = (
            self.stats.total_processing_time / self.stats.total_files
        )
        
        return result
    
    def get_stats(self) -> ConversionStats:
        """Get conversion statistics"""
        return self.stats

# Global service instance
document_service = DocumentService()
```

## Phase 3: Batch-Konvertierung für bestehende Dateien

### 3.1 Erstelle `backend/app/utils/batch_converter.py`
```python
"""
Batch Converter für bestehende Dateien in documents/qa_docs
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import aiofiles

from app.services.document_service import document_service, ConversionResult

logger = logging.getLogger(__name__)

class BatchConverter:
    """Batch conversion of existing files"""
    
    def __init__(self, source_dir: str = "./data/documents/qa_docs"):
        self.source_dir = Path(source_dir)
        self.results: List[Dict[str, Any]] = []
    
    async def convert_all_files(self) -> Dict[str, Any]:
        """Convert all PDF and TXT files in qa_docs directory"""
        
        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return {"error": "Source directory not found"}
        
        # Finde alle PDF und TXT Dateien
        files_to_convert = []
        for pattern in ['*.pdf', '*.txt']:
            files_to_convert.extend(self.source_dir.glob(pattern))
        
        if not files_to_convert:
            logger.info("No PDF or TXT files found to convert")
            return {"message": "No files to convert", "files_processed": 0}
        
        logger.info(f"Found {len(files_to_convert)} files to convert")
        
        # Konvertiere alle Dateien
        conversion_tasks = []
        for file_path in files_to_convert:
            task = self._convert_single_file(file_path)
            conversion_tasks.append(task)
        
        # Parallel processing für bessere Performance
        results = await asyncio.gather(*conversion_tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Conversion failed for {files_to_convert[i]}: {result}")
                failed += 1
            elif result and result.get('success'):
                successful += 1
            else:
                failed += 1
        
        summary = {
            "total_files": len(files_to_convert),
            "successful_conversions": successful,
            "failed_conversions": failed,
            "conversion_rate": f"{(successful/len(files_to_convert)*100):.1f}%",
            "results": [r for r in results if not isinstance(r, Exception)]
        }
        
        logger.info(f"Batch conversion completed: {successful}/{len(files_to_convert)} successful")
        return summary
    
    async def _convert_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Convert a single file and save as markdown"""
        try:
            # Datei lesen
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            # Konvertieren
            result = await document_service.convert_file(str(file_path), file_content)
            
            if not result.success:
                return {
                    "file": str(file_path),
                    "success": False,
                    "error": result.error_message
                }
            
            # Markdown speichern
            output_filename = file_path.stem + '.md'
            output_path = file_path.parent / output_filename
            
            saved = await document_service.save_markdown(
                result.markdown_content, str(output_path)
            )
            
            if not saved:
                return {
                    "file": str(file_path),
                    "success": False,
                    "error": "Failed to save markdown"
                }
            
            return {
                "file": str(file_path),
                "output_file": str(output_path),
                "success": True,
                "pages_processed": result.pages_processed,
                "processing_time": result.processing_time,
                "file_size": result.file_size
            }
            
        except Exception as e:
            logger.error(f"Error converting {file_path}: {e}")
            return {
                "file": str(file_path),
                "success": False,
                "error": str(e)
            }

# Global batch converter
batch_converter = BatchConverter()
```

## Phase 4: Clean API Endpoints

### 4.1 Aktualisiere `backend/app/api/v1/documents.py`
```python
"""
Clean Document API - Upload und Konvertierung
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from app.services.document_service import document_service, ConversionResult
from app.utils.batch_converter import batch_converter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_and_convert(
    file: UploadFile = File(...),
    category: str = "qa_docs"
) -> JSONResponse:
    """Upload file and convert to markdown"""
    
    try:
        # Validierung
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_extensions = {'.pdf', '.txt', '.md'}
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Datei lesen
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Konvertieren
        result = await document_service.convert_file(file.filename, file_content)
        
        if not result.success:
            raise HTTPException(
                status_code=422, 
                detail=f"Conversion failed: {result.error_message}"
            )
        
        # Als Markdown speichern
        from pathlib import Path
        output_dir = Path(f"./data/documents/{category}")
        output_filename = Path(file.filename).stem + '.md'
        output_path = output_dir / output_filename
        
        saved = await document_service.save_markdown(
            result.markdown_content, str(output_path)
        )
        
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to save converted file")
        
        return JSONResponse({
            "success": True,
            "message": "File converted successfully",
            "original_filename": file.filename,
            "output_filename": output_filename,
            "output_path": str(output_path),
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
async def batch_convert_existing(background_tasks: BackgroundTasks) -> JSONResponse:
    """Convert all existing PDF and TXT files to markdown"""
    
    try:
        # Starte Batch-Konvertierung im Hintergrund
        background_tasks.add_task(batch_converter.convert_all_files)
        
        return JSONResponse({
            "success": True,
            "message": "Batch conversion started in background",
            "note": "Check logs for progress updates"
        })
        
    except Exception as e:
        logger.error(f"Batch conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversion-stats")
async def get_conversion_stats() -> JSONResponse:
    """Get conversion statistics"""
    
    try:
        stats = document_service.get_stats()
        
        return JSONResponse({
            "total_files": stats.total_files,
            "successful_conversions": stats.successful_conversions,
            "failed_conversions": stats.failed_conversions,
            "success_rate": f"{(stats.successful_conversions/max(stats.total_files,1)*100):.1f}%",
            "total_processing_time": f"{stats.total_processing_time:.2f}s",
            "average_processing_time": f"{stats.average_processing_time:.2f}s"
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
        "supported_formats": [".pdf", ".txt", ".md"],
        "stats": document_service.get_stats().__dict__
    })
```

## Phase 5: Startup Script für Batch-Konvertierung

### 5.1 Erstelle `backend/scripts/convert_existing_files.py`
```python
"""
Startup Script - Konvertiert alle bestehenden Dateien
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.batch_converter import batch_converter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Convert all existing files in qa_docs"""
    
    logger.info("🚀 Starting batch conversion of existing files...")
    
    try:
        result = await batch_converter.convert_all_files()
        
        logger.info("📊 Batch Conversion Results:")
        logger.info(f"   Total files: {result.get('total_files', 0)}")
        logger.info(f"   Successful: {result.get('successful_conversions', 0)}")
        logger.info(f"   Failed: {result.get('failed_conversions', 0)}")
        logger.info(f"   Success rate: {result.get('conversion_rate', 'N/A')}")
        
        if result.get('successful_conversions', 0) > 0:
            logger.info("✅ Batch conversion completed successfully!")
        else:
            logger.warning("⚠️ No files were converted successfully")
            
    except Exception as e:
        logger.error(f"❌ Batch conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 6: Integration & Testing

### 6.1 Requirements aktualisieren
```python
# backend/requirements_clean.txt (neue, saubere Version)
# Core FastAPI
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# Document Processing (minimal)
pypdf==3.17.4
aiofiles==23.2.1

# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0

# RAG (später)
chromadb==0.4.18
sentence-transformers==2.2.2

# LLM
ollama==0.1.7

# Utils
python-dotenv==1.0.0
```

### 6.2 Startup-Kommandos
```bash
# 1. Bestehende Dateien konvertieren
cd backend
python scripts/convert_existing_files.py

# 2. Server starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. API testen
curl -X POST "http://localhost:8000/api/v1/documents/batch-convert"
curl "http://localhost:8000/api/v1/documents/conversion-stats"
```

## Erwartete Ergebnisse

### Performance Targets:
- **PDF → MD**: < 2s pro Datei
- **TXT → MD**: < 200ms pro Datei  
- **Batch Processing**: Parallel für bessere Performance
- **Memory Usage**: < 500MB für gesamtes System

### Code Quality:
- **90% weniger Code** als aktuell
- **100% Type Safety** mit Python typing
- **Klare Verantwortlichkeiten** pro Service
- **Enterprise Error Handling**
- **Comprehensive Logging**

### Funktionalität:
1. ✅ Alle PDFs und TXTs in `documents/qa_docs/` → MD konvertiert
2. ✅ Saubere API für neue Uploads
3. ✅ Monitoring und Statistiken
4. ✅ Proper Error Handling
5. ✅ RAG-optimiertes Markdown Format

Das System ist dann bereit für die RAG-Integration ohne Over-Engineering!