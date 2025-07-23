"""
Training Service - Consolidated Version
Manages training data files with clean architecture and all legacy compatibility
Unified from training_service.py (v1) and training_service_v2.py (v2)
"""
import os
import uuid
import aiofiles
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
import logging
from pathlib import Path

from app.core.base_service import BaseService, ServiceOperationError, ServiceConfigurationError
from app.core.async_manager import task_manager, managed_task
from app.core.security import SecurityError
from app.models.database import TrainingFile
from app.models.schemas import TrainingFileResponse, CategoryStats
from app.core.settings import settings
from app.services.rag_service import rag_service
from app.services.multi_format_processor import multi_format_processor
from app.services.production_document_processor import production_document_processor
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
            indexed_query = select(TrainingFile).where(TrainingFile.is_indexed.is_(True))
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
                upload_date=datetime.now(timezone.utc),
                upload_timestamp=datetime.now(timezone.utc),
                status="uploaded",
                original_format=file_extension.lstrip('.'),
                manual_source_category=manual_category,
                priority=1
            )
            
            self.db.add(training_file)
            await self.db.commit()
            await self.db.refresh(training_file)
            
            # Process file asynchronously with managed task system
            task_id = await task_manager.submit_task(
                self._process_file_async_safe(str(training_file.id)),
                name=f"process_file_{training_file.filename}",
                timeout=600.0,  # 10 minutes timeout
                max_retries=0,  # Disable retries to prevent coroutine reuse
                metadata={
                    "file_id": str(training_file.id),
                    "filename": training_file.filename,
                    "file_size": len(file_content)
                }
            )
            
            logger.info(f"📋 File processing task submitted: {task_id}")
            
            return TrainingFileResponse.model_validate(training_file)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"File upload failed: {e}")
            raise ServiceOperationError(f"Failed to upload file: {e}")
    
    async def save_training_file(self, filename: str, file_content: bytes, 
                                category: str) -> TrainingFileResponse:
        """Save training file to filesystem and database (legacy method for compatibility)"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Generate unique ID and paths
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{filename}"
            
            # Separate paths for originals and optimized files
            category_path = self.base_path / "originals" / category
            category_path.mkdir(parents=True, exist_ok=True)
            original_path = category_path / safe_filename
            
            # Save original file
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"💾 Original file saved to: {original_path}")
            
            # Create database entry
            training_file = TrainingFile(
                id=file_id,
                filename=filename,
                display_name=filename,
                category=category,
                file_path=str(original_path),
                file_size=len(file_content),
                upload_date=datetime.now(timezone.utc),
                upload_timestamp=datetime.now(timezone.utc),
                status="ready",
                is_indexed=False,
                chunk_count=0,
                original_format=Path(filename).suffix.lower().lstrip('.')
            )
            
            self.db.add(training_file)
            await self.db.commit()
            await self.db.refresh(training_file)
            
            logger.info(f"📝 Database record created: {file_id}")
            
            # Process file asynchronously with managed task system
            task_id = await task_manager.submit_task(
                self._process_file_async_safe(str(training_file.id)),
                name=f"process_file_{training_file.filename}",
                timeout=600.0,  # 10 minutes timeout
                max_retries=0,  # Disable retries to prevent coroutine reuse
                metadata={
                    "file_id": str(training_file.id),
                    "filename": training_file.filename,
                    "category": category
                }
            )
            
            logger.info(f"📋 File processing task submitted: {task_id}")
            
            return TrainingFileResponse.model_validate(training_file)
            
        except Exception as e:
            # Clean up file if database operation fails
            if 'original_path' in locals() and original_path.exists():
                original_path.unlink()
            await self.db.rollback()
            logger.error(f"Save training file failed: {e}")
            raise ServiceOperationError(f"Failed to save training file: {e}")
    
    async def upload_file_with_validation(self, file_content: bytes, filename: str, 
                                         manual_category: Optional[str] = None) -> TrainingFileResponse:
        """Upload file with comprehensive security validation"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Basic security validation
            if not filename:
                raise SecurityError("Filename cannot be empty")
            
            if not file_content:
                raise SecurityError("File content cannot be empty")
            
            # Check file size (max 100MB)
            file_size = len(file_content)
            if file_size > 100 * 1024 * 1024:
                raise SecurityError(f"File too large: {file_size} bytes (max 100MB)")
            
            # Check file extension
            file_extension = Path(filename).suffix.lower()
            if file_extension not in ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.json', '.xml', '.csv', '.html']:
                raise SecurityError(f"Unsupported file type: {file_extension}")
            
            logger.info(f"📄 Validated file upload: {filename} ({file_size} bytes)")
            
            # Use regular upload after validation
            return await self.upload_file(file_content, filename, manual_category)
            
        except SecurityError as e:
            logger.error(f"🚨 Security validation failed for {filename}: {e}")
            raise ServiceOperationError(f"File upload blocked by security validation: {e}")
        except Exception as e:
            logger.error(f"❌ File upload validation failed: {e}")
            raise ServiceOperationError(f"File upload failed: {e}")
    
    @managed_task(timeout=600.0, max_retries=2)
    async def _process_file_async_safe(self, file_id: str) -> None:
        """Process uploaded file with separate DB session and managed task execution"""
        from app.models.database import AsyncSessionLocal
        
        # Create new database session for async processing
        new_db = None
        try:
            new_db = AsyncSessionLocal()
            
            # Get file record with new session
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await new_db.execute(query)
            training_file = result.scalar_one_or_none()
            
            if not training_file:
                logger.error(f"Training file not found for async processing: {file_id}")
                return
            
            # Update status to processing
            training_file.status = "processing"
            await new_db.commit()
            
            logger.info(f"🔄 Starting file processing: {training_file.filename}")
            
            # Choose processor based on file type with timeout
            try:
                processor_result = await asyncio.wait_for(
                    self._choose_and_run_processor_safe(
                        training_file.file_path, 
                        training_file.filename,
                        training_file.category,
                        file_id
                    ),
                    timeout=300.0  # 5 minute timeout for individual processing
                )
            except asyncio.TimeoutError:
                raise ServiceOperationError(f"File processing timed out for {training_file.filename}")
            
            logger.info(f"🔍 Processing result for {training_file.filename}: success={processor_result.success}")
            
            if processor_result.success:
                # Update file with processing results
                training_file.status = "ready"
                training_file.processed_file_path = processor_result.output_path
                training_file.markdown_file_path = processor_result.markdown_path
                training_file.processing_method = processor_result.processor_used
                training_file.processing_quality = str(processor_result.quality_score) if processor_result.quality_score is not None else None
                training_file.conversion_status = "completed"
                
                # Index in RAG if available with timeout
                if self.rag_service and processor_result.markdown_path:
                    try:
                        await asyncio.wait_for(
                            self._index_in_rag_safe(training_file, processor_result.markdown_path),
                            timeout=120.0  # 2 minute timeout for RAG indexing
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"⏰ RAG indexing timed out for {training_file.filename}")
                        training_file.index_status = "timeout"
            else:
                training_file.status = "error"
                training_file.processing_error = processor_result.error_message
                training_file.error_message = processor_result.error_message
                training_file.conversion_status = "failed"
            
            await new_db.commit()
            logger.info(f"✅ File processing completed: {file_id}")
            
        except Exception as e:
            logger.error(f"❌ Async file processing failed for {file_id}: {e}")
            
            # Try to mark file as error with proper error handling
            if new_db:
                try:
                    query = select(TrainingFile).where(TrainingFile.id == file_id)
                    result = await new_db.execute(query)
                    training_file = result.scalar_one_or_none()
                    
                    if training_file:
                        training_file.status = "error"
                        training_file.processing_error = str(e)[:1000]  # Limit error message length
                        training_file.error_message = str(e)[:1000]
                        training_file.conversion_status = "failed"
                        await new_db.commit()
                        
                except Exception as cleanup_error:
                    logger.error(f"❌ Failed to mark file as error: {cleanup_error}")
            
            # Re-raise the original exception
            raise
            
        finally:
            # Ensure database session is always closed
            if new_db:
                try:
                    await new_db.close()
                except Exception as e:
                    logger.error(f"❌ Error closing database session: {e}")
    
    async def _index_in_rag_safe(self, training_file: TrainingFile, markdown_path: str) -> None:
        """Index processed file in RAG system with error handling"""
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
            
            # Add to RAG and get chunk count
            chunk_count = await self.rag_service.add_documents([document])
            
            # Update indexing status
            training_file.is_indexed = True
            training_file.indexed_at = datetime.now(timezone.utc)
            training_file.index_status = "indexed"
            training_file.chunk_count = chunk_count  # Store chunk count
            
            logger.info(f"✅ File indexed in RAG: {training_file.filename} ({chunk_count} chunks)")
            
        except Exception as e:
            logger.error(f"❌ RAG indexing failed for {training_file.filename}: {e}")
            training_file.index_status = "failed"
            training_file.index_error = str(e)
    
    
    async def _choose_and_run_processor_safe(self, file_path: str, filename: str, category: str = "help_data", file_id: Optional[str] = None) -> 'ProcessingResult':
        """Choose appropriate processor and run it (safe version for async processing)"""
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower().lstrip('.')
        
        try:
            # Specialized processor for TXT files (high quality conversion)
            if file_extension == 'txt' and 'txt_to_md' in self._file_processors:
                logger.info(f"🔄 Processing TXT file with specialized converter: {filename}")
                result = await txt_to_md_converter.convert_file(file_path)
                if result:
                    return ProcessingResult(
                        success=True,
                        output_path=result,
                        markdown_path=result,
                        processor_used='txt_to_md',
                        quality_score=0.9
                    )
            
            # Try production document processor for other formats
            if 'production_doc' in self._file_processors:
                logger.info(f"🔄 Processing file with production document processor: {filename}")
                with open(file_path, 'rb') as f:
                    content = f.read()
                result = await production_document_processor.process_document(file_path, content)
                if result.success:
                    # Convert production result to expected format
                    # Create optimized output path based on category
                    if category == "help_data":
                        optimized_dir = Path(settings.HELP_DATA_PATH)
                    elif category == "stream_templates":
                        optimized_dir = Path(settings.XML_TEMPLATE_PATH)
                    else:
                        optimized_dir = Path(settings.TRAINING_DATA_PATH) / "optimized" / category
                    
                    optimized_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Use the same UUID as the original file
                    if file_id:
                        # Use provided file_id
                        unique_id = file_id
                    else:
                        # Extract UUID from original filename (format: UUID_filename)
                        original_filename = file_path_obj.name
                        if '_' in original_filename and len(original_filename.split('_')[0]) == 36:
                            unique_id = original_filename.split('_')[0]
                        else:
                            # Fallback to new UUID if not found
                            unique_id = str(uuid.uuid4())
                    
                    optimized_filename = f"{unique_id}_{file_path_obj.stem}.md"
                    output_path = str(optimized_dir / optimized_filename)
                    
                    # Save documents to markdown file
                    markdown_content = []
                    for doc in result.documents:
                        markdown_content.append(doc.page_content)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(markdown_content))
                    
                    return ProcessingResult(
                        success=True,
                        output_path=output_path,
                        markdown_path=output_path,
                        processor_used=result.processing_method,
                        quality_score=result.extraction_confidence,
                        error_message=result.error_message or "Unknown error"
                    )
            
            # Fallback to multi-format processor
            if 'multi_format' in self._file_processors:
                logger.info(f"🔄 Processing file with multi-format processor: {filename}")
                result = await multi_format_processor.process_file(file_path)
                if result.success:
                    # Convert multi-format result to expected format
                    # Create optimized output path based on category
                    if category == "help_data":
                        optimized_dir = Path(settings.HELP_DATA_PATH)
                    elif category == "stream_templates":
                        optimized_dir = Path(settings.XML_TEMPLATE_PATH)
                    else:
                        optimized_dir = Path(settings.TRAINING_DATA_PATH) / "optimized" / category
                    
                    optimized_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Use the same UUID as the original file
                    if file_id:
                        # Use provided file_id
                        unique_id = file_id
                    else:
                        # Extract UUID from original filename (format: UUID_filename)
                        original_filename = file_path_obj.name
                        if '_' in original_filename and len(original_filename.split('_')[0]) == 36:
                            unique_id = original_filename.split('_')[0]
                        else:
                            # Fallback to new UUID if not found
                            unique_id = str(uuid.uuid4())
                    
                    optimized_filename = f"{unique_id}_{file_path_obj.stem}.md"
                    output_path = str(optimized_dir / optimized_filename)
                    
                    # Save documents to markdown file
                    markdown_content = []
                    for doc in result.documents:
                        markdown_content.append(doc.page_content)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(markdown_content))
                    
                    return ProcessingResult(
                        success=True,
                        output_path=output_path,
                        markdown_path=output_path,
                        processor_used=result.processing_method,
                        quality_score=0.8,  # Default quality score
                        error_message=result.error_message or "Unknown error"
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
    
    async def _choose_and_run_processor(self, training_file: TrainingFile) -> 'ProcessingResult':
        """Choose appropriate processor and run it"""
        file_path = Path(training_file.file_path)
        file_extension = file_path.suffix.lower().lstrip('.')
        
        try:
            # Specialized processor for TXT files (high quality conversion)
            if file_extension == 'txt' and 'txt_to_md' in self._file_processors:
                logger.info(f"🔄 Processing TXT file with specialized converter: {training_file.filename}")
                result = await txt_to_md_converter.convert_file(str(file_path))
                if result:
                    return ProcessingResult(
                        success=True,
                        output_path=result,
                        markdown_path=result,
                        processor_used='txt_to_md',
                        quality_score=0.9
                    )
            
            # Try production document processor for other formats
            if 'production_doc' in self._file_processors:
                logger.info(f"🔄 Processing file with production document processor: {training_file.filename}")
                with open(str(file_path), 'rb') as f:
                    content = f.read()
                result = await production_document_processor.process_document(str(file_path), content)
                if result.success:
                    # Convert production result to expected format
                    # Create optimized output path based on category
                    category = getattr(training_file, 'category', 'help_data')
                    if category == "help_data":
                        optimized_dir = Path(settings.HELP_DATA_PATH)
                    elif category == "stream_templates":
                        optimized_dir = Path(settings.XML_TEMPLATE_PATH)
                    else:
                        optimized_dir = Path(settings.TRAINING_DATA_PATH) / "optimized" / category
                    
                    optimized_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Use the same UUID as the original file
                    unique_id = getattr(training_file, 'id', str(uuid.uuid4()))
                    optimized_filename = f"{unique_id}_{file_path.stem}.md"
                    output_path = str(optimized_dir / optimized_filename)
                    
                    # Save documents to markdown file
                    markdown_content = []
                    for doc in result.documents:
                        markdown_content.append(doc.page_content)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(markdown_content))
                    
                    return ProcessingResult(
                        success=True,
                        output_path=output_path,
                        markdown_path=output_path,
                        processor_used=result.processing_method,
                        quality_score=result.extraction_confidence,
                        error_message=result.error_message or "Unknown error"
                    )
            
            # Fallback to multi-format processor
            if 'multi_format' in self._file_processors:
                logger.info(f"🔄 Processing file with multi-format processor: {training_file.filename}")
                result = await multi_format_processor.process_file(str(file_path))
                if result.success:
                    # Convert multi-format result to expected format
                    # Create optimized output path based on category
                    category = getattr(training_file, 'category', 'help_data')
                    if category == "help_data":
                        optimized_dir = Path(settings.HELP_DATA_PATH)
                    elif category == "stream_templates":
                        optimized_dir = Path(settings.XML_TEMPLATE_PATH)
                    else:
                        optimized_dir = Path(settings.TRAINING_DATA_PATH) / "optimized" / category
                    
                    optimized_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Use the same UUID as the original file
                    unique_id = getattr(training_file, 'id', str(uuid.uuid4()))
                    optimized_filename = f"{unique_id}_{file_path.stem}.md"
                    output_path = str(optimized_dir / optimized_filename)
                    
                    # Save documents to markdown file
                    markdown_content = []
                    for doc in result.documents:
                        markdown_content.append(doc.page_content)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(markdown_content))
                    
                    return ProcessingResult(
                        success=True,
                        output_path=output_path,
                        markdown_path=output_path,
                        processor_used=result.processing_method,
                        quality_score=0.8,  # Default quality score
                        error_message=result.error_message or "Unknown error"
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
            training_file.indexed_at = datetime.now(timezone.utc)
            training_file.index_status = "indexed"
            
        except Exception as e:
            logger.error(f"RAG indexing failed: {e}")
            training_file.index_status = "failed"
            training_file.index_error = str(e)
    
    async def get_all_files(self, skip: int = 0, limit: int = 100) -> List[TrainingFileResponse]:
        """Get all training files with pagination"""
        try:
            query = select(TrainingFile).offset(skip).limit(limit).order_by(desc(TrainingFile.upload_date))
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
                
            query = query.offset(skip).limit(limit).order_by(desc(TrainingFile.upload_date))
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
                    # TODO: Implement remove_documents_by_source method in RAG service
                    # await self.rag_service.remove_documents_by_source(training_file.filename)
                    logger.warning("RAG document removal not implemented yet")
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
    
    async def get_training_status(self) -> CategoryStats:
        """Get training status (alias for get_stats)"""
        return await self.get_stats()
    
    async def get_stats(self) -> CategoryStats:
        """Get training data statistics"""
        try:
            # Count files by status
            total_query = select(TrainingFile)
            total_result = await self.db.execute(total_query)
            total_files = len(total_result.scalars().all())
            
            indexed_query = select(TrainingFile).where(TrainingFile.is_indexed.is_(True))
            indexed_result = await self.db.execute(indexed_query)
            indexed_files = len(indexed_result.scalars().all())
            
            return CategoryStats(
                total=total_files,
                ready=total_files,  # Simplified
                processing=0,
                error=0
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise ServiceOperationError(f"Failed to get statistics: {e}")
    
    async def get_chromadb_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics"""
        try:
            # Get files with chunk counts
            query = select(TrainingFile).where(TrainingFile.is_indexed.is_(True))
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
    
    async def delete_training_file(self, file_id: str) -> bool:
        """Delete training file from filesystem and database"""
        try:
            # Get file record
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                logger.warning(f"File not found for deletion: {file_id}")
                return False
            
            files_deleted = []
            
            # Delete original file from filesystem
            file_path = getattr(file_record, 'file_path', None)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                files_deleted.append(f"Original: {file_path}")
                logger.info(f"🗑️ Original file deleted: {file_path}")
            
            # Delete processed files if they exist
            processed_file_path = getattr(file_record, 'processed_file_path', None)
            if processed_file_path and os.path.exists(processed_file_path):
                os.remove(processed_file_path)
                files_deleted.append(f"Processed: {processed_file_path}")
                logger.info(f"🗑️ Processed file deleted: {processed_file_path}")
            
            # Delete markdown file if it exists
            if hasattr(file_record, 'markdown_file_path') and file_record.markdown_file_path:
                if os.path.exists(file_record.markdown_file_path):
                    os.remove(file_record.markdown_file_path)
                    files_deleted.append(f"Markdown: {file_record.markdown_file_path}")
                    logger.info(f"🗑️ Markdown file deleted: {file_record.markdown_file_path}")
            
            # Also check for optimized MD files in standard location (for TXT files)
            filename = getattr(file_record, 'filename', '')
            if filename.lower().endswith('.txt'):
                from pathlib import Path
                # Extract original filename from file path (remove UUID prefix)
                record_file_path = getattr(file_record, 'file_path', '')
                original_filename = Path(record_file_path).name
                # Create expected optimized MD filename
                optimized_filename = original_filename.replace('.txt', '_optimized.md')
                optimized_path = Path("data/training_data/optimized/help_data") / optimized_filename
                
                if optimized_path.exists():
                    optimized_path.unlink()
                    files_deleted.append(f"Optimized MD: {optimized_path}")
                    logger.info(f"🗑️ Optimized MD file deleted: {optimized_path}")
            
            # Remove from ChromaDB if indexed
            if getattr(file_record, 'is_indexed', False):
                try:
                    await self.remove_from_chromadb(file_id)
                    logger.info(f"🗑️ Removed from ChromaDB: {file_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove from ChromaDB: {e}")
            
            # Delete database record
            await self.db.delete(file_record)
            await self.db.commit()
            
            logger.info(f"✅ Complete deletion for {file_id}. Files removed: {', '.join(files_deleted) if files_deleted else 'None'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_id}: {e}")
            await self.db.rollback()
            raise ServiceOperationError(f"Failed to delete file: {e}")
    
    async def remove_from_chromadb(self, file_id: str) -> bool:
        """Remove file from ChromaDB index"""
        try:
            if not self.rag_service:
                logger.warning("RAG service not available")
                return False
            
            # Get documents with matching file_id metadata
            # ChromaDB doesn't support direct deletion by metadata, so we need to find and delete
            logger.info(f"🗑️ Attempting to remove file {file_id} from ChromaDB")
            
            # Mark file as not indexed in database
            update_query = update(TrainingFile).where(
                TrainingFile.id == file_id
            ).values(
                is_indexed=False,
                index_status="removed",
                chunk_count=0
            )
            await self.db.execute(update_query)
            await self.db.commit()
            
            logger.info(f"✅ File {file_id} marked as removed from index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove from ChromaDB: {e}")
            return False
    
    async def process_training_file(self, file_id: str) -> bool:
        """Process/reprocess a training file manually"""
        try:
            # Get file record
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            training_file = result.scalar_one_or_none()
            
            if not training_file:
                logger.error(f"Training file not found: {file_id}")
                return False
            
            logger.info(f"🔄 Manually processing file: {training_file.filename}")
            
            # Trigger async processing with managed task
            task_id = await task_manager.submit_task(
                self._process_file_async_safe(file_id),
                name=f"reprocess_file_{training_file.filename}",
                timeout=600.0,
                max_retries=0,  # Disable retries to prevent coroutine reuse
                metadata={"file_id": file_id, "type": "reprocessing"}
            )
            
            logger.info(f"📋 File reprocessing task submitted: {task_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process training file {file_id}: {e}")
            return False
    
    async def index_file_to_chromadb(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Index a single file to ChromaDB"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get file record
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            training_file = result.scalar_one_or_none()
            
            if not training_file:
                logger.error(f"File not found for indexing: {file_id}")
                return None
            
            # Check if already indexed
            if getattr(training_file, 'is_indexed', False):
                logger.info(f"File already indexed: {training_file.filename}")
                return {
                    "file_id": file_id,
                    "filename": training_file.filename,
                    "status": "already_indexed",
                    "chunk_count": training_file.chunk_count or 0
                }
            
            # Find processed/optimized file
            markdown_path = None
            
            # Check for optimized MD file (for TXT files)
            if training_file.filename.lower().endswith('.txt'):
                from pathlib import Path
                original_filename = Path(training_file.file_path).name
                optimized_filename = original_filename.replace('.txt', '_optimized.md')
                optimized_path = Path("data/training_data/optimized/help_data") / optimized_filename
                if optimized_path.exists():
                    markdown_path = str(optimized_path)
            
            # Fall back to processed file path
            processed_file_path = getattr(training_file, 'processed_file_path', None)
            if not markdown_path and processed_file_path and os.path.exists(processed_file_path):
                markdown_path = processed_file_path
            
            # Fall back to original file
            original_file_path = getattr(training_file, 'file_path', None)
            if not markdown_path and original_file_path and os.path.exists(original_file_path):
                markdown_path = original_file_path
            
            if not markdown_path:
                logger.error(f"No processable file found for {training_file.filename}")
                return None
            
            # Index in RAG
            await self._index_in_rag_safe(training_file, markdown_path)
            await self.db.commit()
            
            logger.info(f"✅ File indexed to ChromaDB: {training_file.filename}")
            return {
                "file_id": file_id,
                "filename": training_file.filename,
                "status": "indexed",
                "chunk_count": training_file.chunk_count or 0,
                "indexed_at": training_file.indexed_at.isoformat() if training_file.indexed_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to index file {file_id}: {e}")
            await self.db.rollback()
            return None
    
    async def batch_index_to_chromadb(self, file_ids: List[str]) -> Dict[str, Any]:
        """Batch index multiple files to ChromaDB"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            results = {
                "total_files": len(file_ids),
                "successful": 0,
                "failed": 0,
                "results": []
            }
            
            for file_id in file_ids:
                try:
                    result = await self.index_file_to_chromadb(file_id)
                    if result:
                        results["successful"] += 1
                        results["results"].append(result)
                    else:
                        results["failed"] += 1
                        results["results"].append({
                            "file_id": file_id,
                            "status": "failed",
                            "error": "Indexing failed"
                        })
                except Exception as e:
                    results["failed"] += 1
                    results["results"].append({
                        "file_id": file_id,
                        "status": "failed", 
                        "error": str(e)
                    })
                    logger.error(f"Failed to index file {file_id} in batch: {e}")
            
            logger.info(f"✅ Batch indexing completed: {results['successful']}/{results['total_files']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Batch indexing failed: {e}")
            return {
                "total_files": len(file_ids),
                "successful": 0,
                "failed": len(file_ids),
                "error": str(e),
                "results": []
            }

    async def get_training_status(self) -> Dict[str, Any]:
        """Get training status for both categories"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get all files
            files = await self.get_training_files()
            
            # Initialize stats
            help_data_stats = CategoryStats(total=0, ready=0, processing=0, error=0)
            stream_template_stats = CategoryStats(total=0, ready=0, processing=0, error=0)
            
            # Count files by category and status
            for file in files:
                category = getattr(file, 'category', 'help_data')
                status = getattr(file, 'status', 'error')
                
                if category == 'help_data':
                    help_data_stats.total += 1
                    if status == 'ready':
                        help_data_stats.ready += 1
                    elif status == 'processing':
                        help_data_stats.processing += 1
                    elif status == 'error':
                        help_data_stats.error += 1
                else:
                    stream_template_stats.total += 1
                    if status == 'ready':
                        stream_template_stats.ready += 1
                    elif status == 'processing':
                        stream_template_stats.processing += 1
                    elif status == 'error':
                        stream_template_stats.error += 1
            
            from app.models.schemas import TrainingStatusResponse
            return TrainingStatusResponse(
                help_data_stats=help_data_stats,
                stream_template_stats=stream_template_stats,
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to get training status: {e}")
            raise ServiceOperationError(f"Failed to get training status: {e}")

# Utility class for legacy compatibility
class ProcessingResult:
    """Result of file processing operation"""
    def __init__(self, success: bool, output_path: Optional[str] = None, markdown_path: Optional[str] = None, 
                 processor_used: Optional[str] = None, quality_score: float = 0.0, error_message: Optional[str] = None):
        self.success = success
        self.output_path = output_path
        self.markdown_path = markdown_path
        self.processor_used = processor_used
        self.quality_score = quality_score
        self.error_message = error_message