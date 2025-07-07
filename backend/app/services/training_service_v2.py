"""
Training Service v2.0 - Clean Architecture Implementation
Manages training data files with proper service patterns
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


class TrainingServiceV2(BaseService):
    """
    Production-ready training service with clean architecture
    
    Features:
    - Proper service lifecycle management
    - Comprehensive error handling
    - Resource cleanup
    - Performance monitoring
    """
    
    def __init__(self, db_session: AsyncSession):
        super().__init__("TrainingService")
        self.db = db_session
        self.base_path = Path(settings.TRAINING_DATA_PATH)
        self._file_processors = {}
        self._supported_formats = set()
        
    async def _initialize_impl(self) -> None:
        """Initialize training service"""
        # Ensure directory structure
        await self._ensure_directories()
        
        # Register file processors
        await self._register_processors()
        
        # Validate configuration
        await self._validate_configuration()
        
        self._log_operation("Initialization complete", 
                          f"Supporting {len(self._supported_formats)} file formats")
    
    async def _cleanup_impl(self) -> None:
        """Cleanup training service resources"""
        # Close any open file handles
        for processor in self._file_processors.values():
            if hasattr(processor, 'cleanup'):
                await processor.cleanup()
        
        self._file_processors.clear()
        self._log_operation("Cleanup complete")
    
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Training service health check"""
        try:
            # Check database connection
            db_healthy = await self._check_database_health()
            
            # Check file system access
            fs_healthy = await self._check_filesystem_health()
            
            # Get statistics
            stats = await self._get_service_stats()
            
            return {
                "database_healthy": db_healthy,
                "filesystem_healthy": fs_healthy,
                "supported_formats": list(self._supported_formats),
                "processor_count": len(self._file_processors),
                **stats
            }
            
        except Exception as e:
            return {"health_check_error": str(e), "is_healthy": False}
    
    async def _ensure_directories(self) -> None:
        """Ensure training data directory structure exists"""
        directories = [
            self.base_path,
            self.base_path / "originals" / "help_data",
            self.base_path / "originals" / "stream_templates", 
            self.base_path / "optimized" / "help_data",
            self.base_path / "optimized" / "stream_templates",
            self.base_path / "processed",
            self.base_path / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self._logger.debug(f"📁 Directory ensured: {directory}")
    
    async def _register_processors(self) -> None:
        """Register file processors for different formats"""
        try:
            # Import processors dynamically to avoid circular dependencies
            from app.services.txt_to_md_converter import txt_to_md_converter
            from app.services.enterprise_markdown_converter import enterprise_markdown_converter
            from app.services.production_document_processor import production_document_processor
            
            self._file_processors = {
                'txt': txt_to_md_converter,
                'md': enterprise_markdown_converter,
                'pdf': production_document_processor,
                'docx': production_document_processor,
                'doc': production_document_processor
            }
            
            # Collect supported formats
            for processor_name, processor in self._file_processors.items():
                if hasattr(processor, 'supported_formats'):
                    self._supported_formats.update(processor.supported_formats)
                else:
                    self._supported_formats.add(processor_name)
                    
            self._logger.info(f"📄 Registered {len(self._file_processors)} file processors")
            
        except ImportError as e:
            raise ServiceConfigurationError(f"Failed to import file processors: {e}")
    
    async def _validate_configuration(self) -> None:
        """Validate service configuration"""
        if not self.base_path.exists():
            raise ServiceConfigurationError(f"Training data path does not exist: {self.base_path}")
        
        if not os.access(self.base_path, os.W_OK):
            raise ServiceConfigurationError(f"No write access to training data path: {self.base_path}")
        
        if not self.db:
            raise ServiceConfigurationError("Database session not provided")
    
    async def _check_database_health(self) -> bool:
        """Check database connection health"""
        try:
            # Simple query to check connection
            result = await self.db.execute(select(TrainingFile).limit(1))
            return True
        except Exception as e:
            self._logger.error(f"Database health check failed: {e}")
            return False
    
    async def _check_filesystem_health(self) -> bool:
        """Check filesystem access health"""
        try:
            test_file = self.base_path / ".health_check"
            test_file.write_text("health_check")
            test_file.unlink()
            return True
        except Exception as e:
            self._logger.error(f"Filesystem health check failed: {e}")
            return False
    
    async def _get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            total_files = await self.db.scalar(select(TrainingFile).count())
            indexed_files = await self.db.scalar(
                select(TrainingFile).where(TrainingFile.is_indexed == True).count()
            )
            
            return {
                "total_files": total_files or 0,
                "indexed_files": indexed_files or 0,
                "indexing_percentage": (indexed_files / total_files * 100) if total_files else 0
            }
        except Exception:
            return {"stats_error": "Unable to retrieve statistics"}
    
    # Public API Methods
    
    async def save_training_file(
        self,
        filename: str,
        file_content: bytes,
        category: str,
        source_category: Optional[str] = None,
        description: Optional[str] = None
    ) -> TrainingFileResponse:
        """
        Save training file with proper error handling and validation
        
        Args:
            filename: Original filename
            file_content: File content as bytes
            category: File category (help_data or stream_templates)
            source_category: Source category for classification
            description: Optional file description
            
        Returns:
            TrainingFileResponse with file metadata
            
        Raises:
            ServiceOperationError: If operation fails
        """
        self._ensure_ready()
        
        if category not in ['help_data', 'stream_templates']:
            raise ServiceOperationError(f"Invalid category: {category}")
        
        if len(file_content) == 0:
            raise ServiceOperationError("Empty file content")
        
        if len(filename) > 255:
            raise ServiceOperationError("Filename too long")
        
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix.lower()
        
        try:
            # Generate unique filename
            unique_filename = f"{file_id}_{filename}"
            
            # File paths
            original_path = self.base_path / "originals" / category / unique_filename
            
            # Save original file
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            # Process file if processor available
            processed_path = None
            if file_extension.lstrip('.') in self._file_processors:
                processed_path = await self._process_file(original_path, category, file_extension)
            
            # Create database record
            training_file = TrainingFile(
                id=file_id,
                filename=filename,
                file_path=str(processed_path or original_path),
                category=category,
                file_size=len(file_content),
                is_indexed=False,
                status="ready",
                upload_date=datetime.utcnow(),
                manual_source_category=source_category,
                description=description,
                original_format=file_extension,
                processing_method=file_extension.lstrip('.') if processed_path else 'none'
            )
            
            self.db.add(training_file)
            await self.db.commit()
            
            self._log_operation("File saved", f"{filename} ({file_id})")
            
            return TrainingFileResponse(
                id=file_id,
                filename=filename,
                category=category,
                file_path=str(processed_path or original_path),
                file_size=len(file_content),
                status="ready",
                upload_date=training_file.upload_date,
                is_indexed=False
            )
            
        except Exception as e:
            await self.db.rollback()
            # Cleanup files on error
            for path in [original_path, processed_path]:
                if path and Path(path).exists():
                    try:
                        Path(path).unlink()
                    except:
                        pass
            
            raise ServiceOperationError(f"Failed to save training file: {e}") from e
    
    async def _process_file(self, file_path: Path, category: str, file_extension: str) -> Optional[Path]:
        """Process file using appropriate processor"""
        processor_key = file_extension.lstrip('.')
        if processor_key not in self._file_processors:
            return None
        
        processor = self._file_processors[processor_key]
        
        try:
            if processor_key == 'txt':
                optimized_dir = self.base_path / "optimized" / category
                return await processor.convert_txt_to_md(file_path, optimized_dir)
            elif hasattr(processor, 'process_file'):
                return await processor.process_file(file_path)
            else:
                self._logger.warning(f"No process method for processor: {processor_key}")
                return None
                
        except Exception as e:
            self._logger.error(f"File processing failed for {file_path}: {e}")
            return None
    
    async def get_training_files(
        self, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TrainingFileResponse]:
        """Get training files with optional filters"""
        self._ensure_ready()
        
        query = select(TrainingFile)
        
        if category:
            query = query.where(TrainingFile.category == category)
        if status:
            query = query.where(TrainingFile.status == status)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        query = query.order_by(TrainingFile.upload_date.desc())
        
        try:
            result = await self.db.execute(query)
            files = result.scalars().all()
            
            return [
                TrainingFileResponse(
                    id=file.id,
                    filename=file.filename,
                    category=file.category,
                    file_path=file.file_path,
                    file_size=file.file_size,
                    status=file.status,
                    upload_date=file.upload_date,
                    is_indexed=file.is_indexed,
                    indexed_at=file.indexed_at,
                    chunk_count=file.chunk_count or 0
                )
                for file in files
            ]
            
        except Exception as e:
            raise ServiceOperationError(f"Failed to retrieve training files: {e}") from e
    
    async def delete_training_file(self, file_id: str) -> bool:
        """Delete training file and associated resources"""
        self._ensure_ready()
        
        try:
            # Get file record
            result = await self.db.execute(
                select(TrainingFile).where(TrainingFile.id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                return False
            
            # Delete physical files
            await self._delete_physical_files(file_record)
            
            # Remove from database
            await self.db.delete(file_record)
            await self.db.commit()
            
            self._log_operation("File deleted", f"{file_record.filename} ({file_id})")
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise ServiceOperationError(f"Failed to delete training file: {e}") from e
    
    async def _delete_physical_files(self, file_record: TrainingFile) -> None:
        """Delete physical files associated with training file"""
        files_to_delete = []
        
        # Primary file
        if file_record.file_path and Path(file_record.file_path).exists():
            files_to_delete.append(Path(file_record.file_path))
        
        # Look for related files (original, processed, etc.)
        search_patterns = [
            f"{file_record.id}_*",
            f"*{file_record.id}*"
        ]
        
        search_dirs = [
            self.base_path / "originals" / file_record.category,
            self.base_path / "optimized" / file_record.category,
            self.base_path / "processed"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in search_patterns:
                    files_to_delete.extend(search_dir.glob(pattern))
        
        # Delete files
        for file_path in set(files_to_delete):  # Remove duplicates
            try:
                file_path.unlink()
                self._logger.debug(f"🗑️ Deleted file: {file_path}")
            except Exception as e:
                self._logger.warning(f"Failed to delete file {file_path}: {e}")
    
    async def get_training_status(self) -> TrainingStatusResponse:
        """Get comprehensive training status"""
        self._ensure_ready()
        
        try:
            # Get stats for each category
            help_data_stats = await self._get_category_stats('help_data')
            stream_template_stats = await self._get_category_stats('stream_templates')
            
            return TrainingStatusResponse(
                help_data_stats=help_data_stats,
                stream_template_stats=stream_template_stats,
                last_updated=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            raise ServiceOperationError(f"Failed to get training status: {e}") from e
    
    async def _get_category_stats(self, category: str) -> CategoryStats:
        """Get statistics for a specific category"""
        base_query = select(TrainingFile).where(TrainingFile.category == category)
        
        total = await self.db.scalar(base_query.count()) or 0
        ready = await self.db.scalar(
            base_query.where(TrainingFile.status == 'ready').count()
        ) or 0
        processing = await self.db.scalar(
            base_query.where(TrainingFile.status == 'processing').count()
        ) or 0
        error = await self.db.scalar(
            base_query.where(TrainingFile.status == 'error').count()
        ) or 0
        
        return CategoryStats(
            total=total,
            ready=ready,
            processing=processing,
            error=error
        )