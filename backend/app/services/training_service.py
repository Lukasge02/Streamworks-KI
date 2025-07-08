"""
Training Service - Consolidated Version
Manages training data files with clean architecture and all legacy compatibility
Unified from training_service.py (v1) and training_service_v2.py (v2)
"""
import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import logging
from pathlib import Path

from app.core.base_service import BaseService, ServiceOperationError, ServiceConfigurationError
from app.models.database import TrainingFile
from app.models.schemas import TrainingFileResponse, TrainingFileCreate, TrainingStatusResponse, CategoryStats
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.txt_to_md_converter import txt_to_md_converter
from app.services.multi_format_processor import multi_format_processor, FileProcessingResult
from app.services.enterprise_markdown_converter import enterprise_markdown_converter
from app.services.production_document_processor import production_document_processor, ProcessingResult
from langchain.schema import Document

logger = logging.getLogger(__name__)

class TrainingService(BaseService):
    """
    Unified Training Service - Production-ready with clean architecture
    
    Features:
    - Clean Architecture with BaseService
    - Legacy compatibility for existing code
    - Comprehensive error handling
    - Performance monitoring
    - Multi-format document processing
    """
    
    def __init__(self, db_session: AsyncSession):
        super().__init__("TrainingService")
        self.db = db_session
        self.base_path = Path(settings.TRAINING_DATA_PATH)
        self.rag_service = None
        self._file_processors = {}
        self._supported_formats = {
            'pdf', 'docx', 'txt', 'md', 'html', 'xml', 'json',
            'xlsx', 'csv', 'pptx', 'rtf', 'odt', 'epub'
        }
        
    async def _initialize_impl(self) -> None:
        """Initialize service dependencies"""
        try:
            # Ensure base paths exist
            os.makedirs(self.base_path, exist_ok=True)
            os.makedirs(self.base_path / "originals", exist_ok=True)
            os.makedirs(self.base_path / "optimized", exist_ok=True)
            
            # Initialize processors
            self._initialize_processors()
            
            # Initialize RAG service connection
            try:
                from app.services.rag_service import rag_service
                self.rag_service = rag_service
            except ImportError:
                logger.warning("RAG service not available during initialization")
            
            logger.info(f"Training service initialized with {len(self._supported_formats)} supported formats")
            
        except Exception as e:
            raise ServiceConfigurationError(f"Failed to initialize training service: {e}")
    
    def _initialize_processors(self) -> None:
        """Initialize file processors"""
        try:
            self._file_processors = {
                'multi_format': multi_format_processor,
                'enterprise_md': enterprise_markdown_converter,
                'production_doc': production_document_processor,
                'txt_to_md': txt_to_md_converter
            }
        except Exception as e:
            logger.warning(f"Some processors failed to initialize: {e}")
    
    async def _cleanup_impl(self) -> None:
        """Cleanup service resources"""
        self._file_processors.clear()
        self.rag_service = None
    
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Service-specific health check"""
        try:
            # Count files in database
            query = select(TrainingFile)
            result = await self.db.execute(query)
            total_files = len(result.scalars().all())
            
            # Count indexed files
            indexed_query = select(TrainingFile).where(TrainingFile.is_indexed == True)
            indexed_result = await self.db.execute(indexed_query)
            indexed_files = len(indexed_result.scalars().all())
            
            return {
                "is_healthy": True,
                "total_files": total_files,
                "indexed_files": indexed_files,
                "processors_available": len(self._file_processors),
                "supported_formats": len(self._supported_formats),
                "rag_service_connected": self.rag_service is not None,
                "base_path_exists": self.base_path.exists()
            }
            
        except Exception as e:
            return {
                "is_healthy": False,
                "error": str(e)
            }
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self.is_ready
    
    async def upload_file(self, file_content: bytes, filename: str, 
                         manual_category: Optional[str] = None) -> TrainingFileResponse:
        """Upload and process a training file"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Generate unique ID and paths
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix.lower()
            
            # Create file paths
            original_path = self.base_path / "originals" / f"{file_id}_{filename}"
            
            # Save original file
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            # Create database entry
            training_file = TrainingFile(
                id=file_id,
                filename=filename,
                display_name=filename,
                file_path=str(original_path),
                file_size=len(file_content),
                upload_date=datetime.utcnow(),
                upload_timestamp=datetime.utcnow(),
                status="uploaded",
                original_format=file_extension.lstrip('.'),
                manual_source_category=manual_category,
                priority=1
            )
            
            self.db.add(training_file)
            await self.db.commit()
            await self.db.refresh(training_file)
            
            # Process file asynchronously
            await self._process_file_async(training_file)
            
            return TrainingFileResponse.model_validate(training_file)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"File upload failed: {e}")
            raise ServiceOperationError(f"Failed to upload file: {e}")
    
    async def _process_file_async(self, training_file: TrainingFile) -> None:
        """Process uploaded file"""
        try:
            # Update status to processing
            training_file.status = "processing"
            await self.db.commit()
            
            # Choose processor based on file type
            processor_result = await self._choose_and_run_processor(training_file)
            
            if processor_result.success:
                # Update file with processing results
                training_file.status = "ready"
                training_file.processed_file_path = processor_result.output_path
                training_file.markdown_file_path = processor_result.markdown_path
                training_file.processing_method = processor_result.processor_used
                training_file.processing_quality = processor_result.quality_score
                training_file.conversion_status = "completed"
                
                # Index in RAG if available
                if self.rag_service and processor_result.markdown_path:
                    await self._index_in_rag(training_file, processor_result.markdown_path)
            else:
                training_file.status = "error"
                training_file.processing_error = processor_result.error_message
                training_file.conversion_status = "failed"
            
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            training_file.status = "error"
            training_file.processing_error = str(e)
            await self.db.commit()
    
    async def _choose_and_run_processor(self, training_file: TrainingFile) -> 'ProcessingResult':
        """Choose appropriate processor and run it"""
        file_path = Path(training_file.file_path)
        file_extension = file_path.suffix.lower().lstrip('.')
        
        try:
            # Try production document processor first (best quality)
            if 'production_doc' in self._file_processors:
                result = await production_document_processor.process_file(str(file_path))
                if result.success:
                    return result
            
            # Fallback to multi-format processor
            if 'multi_format' in self._file_processors:
                result = await multi_format_processor.process_file(
                    str(file_path), 
                    target_format='markdown'
                )
                if result.success:
                    return result
            
            # Last resort: text extraction
            if file_extension == 'txt' and 'txt_to_md' in self._file_processors:
                result = await txt_to_md_converter.convert_file(str(file_path))
                if result:
                    return ProcessingResult(
                        success=True,
                        output_path=result,
                        markdown_path=result,
                        processor_used='txt_to_md',
                        quality_score=0.8
                    )
            
            # If all processors fail
            return ProcessingResult(
                success=False,
                error_message=f"No suitable processor found for {file_extension} files"
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=f"Processing failed: {e}"
            )
    
    async def _index_in_rag(self, training_file: TrainingFile, markdown_path: str) -> None:
        """Index processed file in RAG system"""
        try:
            if not self.rag_service:
                logger.warning("RAG service not available for indexing")
                return
            
            # Load document content
            async with aiofiles.open(markdown_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Create document for RAG
            document = Document(
                page_content=content,
                metadata={
                    'source': training_file.filename,
                    'file_id': training_file.id,
                    'source_type': training_file.original_format,
                    'category': training_file.manual_source_category or 'general'
                }
            )
            
            # Add to RAG
            await self.rag_service.add_documents([document])
            
            # Update indexing status
            training_file.is_indexed = True
            training_file.indexed_at = datetime.utcnow()
            training_file.index_status = "indexed"
            
        except Exception as e:
            logger.error(f"RAG indexing failed: {e}")
            training_file.index_status = "failed"
            training_file.index_error = str(e)
    
    async def get_all_files(self, skip: int = 0, limit: int = 100) -> List[TrainingFileResponse]:
        """Get all training files with pagination"""
        try:
            query = select(TrainingFile).offset(skip).limit(limit).order_by(TrainingFile.upload_timestamp.desc())
            result = await self.db.execute(query)
            files = result.scalars().all()
            return [TrainingFileResponse.model_validate(file) for file in files]
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            raise ServiceOperationError(f"Failed to retrieve files: {e}")
    
    async def get_training_files(self, category: Optional[str] = None, status: Optional[str] = None, 
                               skip: int = 0, limit: int = 100) -> List[TrainingFileResponse]:
        """Get training files with optional filtering"""
        try:
            query = select(TrainingFile)
            
            # Apply filters if provided
            if category:
                query = query.where(TrainingFile.manual_source_category == category)
            if status:
                query = query.where(TrainingFile.status == status)
                
            query = query.offset(skip).limit(limit).order_by(TrainingFile.upload_timestamp.desc())
            result = await self.db.execute(query)
            files = result.scalars().all()
            return [TrainingFileResponse.model_validate(file) for file in files]
        except Exception as e:
            logger.error(f"Failed to get training files: {e}")
            raise ServiceOperationError(f"Failed to retrieve files: {e}")
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a training file"""
        try:
            # Get file record
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            training_file = result.scalar_one_or_none()
            
            if not training_file:
                return False
            
            # Delete physical files
            await self._delete_physical_files(training_file)
            
            # Remove from RAG if indexed
            if training_file.is_indexed and self.rag_service:
                try:
                    await self.rag_service.remove_documents_by_source(training_file.filename)
                except Exception as e:
                    logger.warning(f"Failed to remove from RAG: {e}")
            
            # Delete database record
            await self.db.delete(training_file)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete file: {e}")
            raise ServiceOperationError(f"Failed to delete file: {e}")
    
    async def _delete_physical_files(self, training_file: TrainingFile) -> None:
        """Delete physical files associated with training file"""
        files_to_delete = [
            training_file.file_path,
            training_file.processed_file_path,
            training_file.markdown_file_path
        ]
        
        for file_path in files_to_delete:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
    
    async def get_stats(self) -> CategoryStats:
        """Get training data statistics"""
        try:
            # Count files by status
            total_query = select(TrainingFile)
            total_result = await self.db.execute(total_query)
            total_files = len(total_result.scalars().all())
            
            indexed_query = select(TrainingFile).where(TrainingFile.is_indexed == True)
            indexed_result = await self.db.execute(indexed_query)
            indexed_files = len(indexed_result.scalars().all())
            
            return CategoryStats(
                total_files=total_files,
                indexed_files=indexed_files,
                ready_files=total_files,  # Simplified
                processing_files=0,
                categories={}
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise ServiceOperationError(f"Failed to get statistics: {e}")
    
    async def get_chromadb_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics"""
        try:
            # Get files with chunk counts
            query = select(TrainingFile).where(TrainingFile.is_indexed == True)
            result = await self.db.execute(query)
            indexed_files = result.scalars().all()
            
            total_chunks = sum(file.chunk_count or 0 for file in indexed_files)
            
            stats = {
                "total_indexed_files": len(indexed_files),
                "total_chunks": total_chunks,
                "avg_chunks_per_file": total_chunks / len(indexed_files) if indexed_files else 0,
                "indexed_files_by_status": {},
                "files": []
            }
            
            # Add individual file stats
            for file in indexed_files:
                stats["files"].append({
                    "filename": file.filename,
                    "chunk_count": file.chunk_count or 0,
                    "indexed_at": file.indexed_at.isoformat() if file.indexed_at else None,
                    "index_status": file.index_status
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get ChromaDB stats: {e}")
            raise ServiceOperationError(f"Failed to get ChromaDB statistics: {e}")

# Utility class for legacy compatibility
class ProcessingResult:
    """Result of file processing operation"""
    def __init__(self, success: bool, output_path: str = None, markdown_path: str = None, 
                 processor_used: str = None, quality_score: float = 0.0, error_message: str = None):
        self.success = success
        self.output_path = output_path
        self.markdown_path = markdown_path
        self.processor_used = processor_used
        self.quality_score = quality_score
        self.error_message = error_message