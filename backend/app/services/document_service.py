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

from app.core.settings import settings
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