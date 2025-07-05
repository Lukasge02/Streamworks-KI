import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging
import asyncio

from app.models.database import TrainingFile
from app.models.schemas import TrainingFileResponse, TrainingFileCreate, TrainingStatusResponse, CategoryStats
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.txt_to_md_converter import txt_to_md_converter
from app.services.multi_format_processor import multi_format_processor, FileProcessingResult
from pathlib import Path
from langchain.schema import Document

logger = logging.getLogger(__name__)

class TrainingService:
    """Service for managing training data files"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_path = "data/training_data"
        self.rag_service = None
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure training data directories exist"""
        directories = [
            self.base_path,
            # Original files
            os.path.join(self.base_path, "originals", "help_data"),
            os.path.join(self.base_path, "originals", "stream_templates"),
            # Optimized MD files
            os.path.join(self.base_path, "optimized", "help_data"),
            os.path.join(self.base_path, "optimized", "stream_templates"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Ensured directory exists: {directory}")
    
    async def save_training_file_with_source(
        self,
        filename: str,
        file_content: bytes,
        category: str,
        source_category: str,
        description: Optional[str] = None
    ) -> TrainingFileResponse:
        """Save training file with manual source categorization"""
        
        # Generate unique filename to avoid conflicts
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{file_id}_{filename}"
        
        # File paths
        original_path = os.path.join(self.base_path, "originals", category, unique_filename)
        optimized_filename = f"{file_id}_{os.path.splitext(filename)[0]}_optimized.md"
        optimized_path = os.path.join(self.base_path, "optimized", category, optimized_filename)
        
        try:
            # Save original file
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            # Convert to optimized MD if needed
            if file_extension.lower() == '.txt':
                # Save original as temp file for conversion
                temp_txt_path = Path(original_path)
                optimized_dir = Path(self.base_path) / "optimized" / category
                
                # Convert using the correct method
                from app.services.txt_to_md_converter import txt_to_md_converter
                optimized_md_path = await txt_to_md_converter.convert_txt_to_md(temp_txt_path, optimized_dir)
                optimized_path = str(optimized_md_path)
            else:
                # Copy other files as-is to optimized directory
                async with aiofiles.open(optimized_path, 'w', encoding='utf-8') as f:
                    await f.write(file_content.decode('utf-8'))
            
            # Create database record with minimal fields (to avoid schema issues)
            training_file = TrainingFile(
                id=file_id,
                filename=filename,
                file_path=optimized_path,
                category=category,
                file_size=len(file_content),
                is_indexed=False,
                status="ready"  # Ready for use
            )
            
            self.db.add(training_file)
            await self.db.commit()
            await self.db.refresh(training_file)
            
            logger.info(f"✅ Saved training file with source: {filename} -> {source_category}")
            
            return TrainingFileResponse(
                id=training_file.id,
                filename=training_file.filename,
                file_path=training_file.file_path,
                category=training_file.category,
                file_size=training_file.file_size,
                is_indexed=training_file.is_indexed,
                status=training_file.status,
                source_category=source_category,
                created_at=training_file.created_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to save training file {filename}: {e}")
            # Cleanup files on error
            for path in [original_path, optimized_path]:
                if os.path.exists(path):
                    os.remove(path)
            raise
    
    async def save_training_file(
        self,
        filename: str,
        file_content: bytes,
        category: str
    ) -> TrainingFileResponse:
        """Save training file to filesystem and database"""
        
        # Generate unique file ID and paths
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{filename}"
        
        # Separate paths for originals and optimized files
        original_path = os.path.join(self.base_path, "originals", category, safe_filename)
        optimized_dir = os.path.join(self.base_path, "optimized", category)
        
        try:
            # Save original file
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"💾 Original file saved to: {original_path}")
            
            # Create database record with simple fields
            db_file = TrainingFile(
                id=file_id,
                filename=filename,  # Clean user-friendly name
                display_name=filename,  # Same as filename for user-friendly display
                category=category,
                file_path=original_path,
                file_size=len(file_content),
                status="ready",
                is_indexed=False,
                chunk_count=0
            )
            
            self.db.add(db_file)
            await self.db.commit()
            await self.db.refresh(db_file)
            
            logger.info(f"📝 Database record created: {file_id}")
            
            # Process file asynchronously with separate DB session
            asyncio.create_task(self._process_uploaded_file_async(file_id, original_path, category))
            
            # Convert to response model
            return TrainingFileResponse(
                id=db_file.id,
                filename=db_file.filename,
                display_name=db_file.display_name,
                category=db_file.category,
                file_path=db_file.file_path,
                upload_date=db_file.upload_date.isoformat(),
                file_size=db_file.file_size,
                status=db_file.status,
                is_indexed=db_file.is_indexed,
                indexed_at=db_file.indexed_at.isoformat() if db_file.indexed_at else None,
                chunk_count=db_file.chunk_count,
                index_status=db_file.index_status,
                index_error=db_file.index_error
            )
            
        except Exception as e:
            # Clean up file if database operation fails
            if os.path.exists(original_path):
                os.remove(original_path)
            raise e
    
    async def get_training_files(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[TrainingFileResponse]:
        """Get list of training files with optional filtering"""
        
        query = select(TrainingFile)
        
        if category:
            query = query.where(TrainingFile.category == category)
        
        if status:
            query = query.where(TrainingFile.status == status)
        
        query = query.order_by(TrainingFile.upload_date.desc())
        
        result = await self.db.execute(query)
        files = result.scalars().all()
        
        return [
            TrainingFileResponse(
                id=file.id,
                filename=file.filename,
                display_name=file.display_name,
                category=file.category,
                file_path=file.file_path,
                upload_date=file.upload_date.isoformat(),
                file_size=file.file_size,
                status=file.status,
                is_indexed=file.is_indexed,
                indexed_at=file.indexed_at.isoformat() if file.indexed_at else None,
                chunk_count=file.chunk_count,
                index_status=file.index_status,
                index_error=file.index_error,
                manual_source_category=file.manual_source_category
            )
            for file in files
        ]
    
    async def add_files_to_rag(self, training_files: List[TrainingFileResponse]):
        """Add uploaded files to RAG system for immediate availability"""
        try:
            from app.services.rag_service import rag_service
            from langchain.docstore.document import Document
            
            if not rag_service.is_initialized:
                await rag_service.initialize()
            
            documents = []
            for training_file in training_files:
                try:
                    # Read the optimized file content
                    async with aiofiles.open(training_file.file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    # Create ChromaDB-compatible metadata
                    source_category = getattr(training_file, 'manual_source_category', None) or 'Testdaten'
                    metadata = {
                        "filename": str(training_file.filename),
                        "source": str(training_file.file_path),
                        "type": "training_document",
                        "category": str(training_file.category),
                        "source_type": str(source_category),
                        "description": f"Training data from {source_category}",
                        "upload_timestamp": datetime.now().isoformat(),
                        "training_file_id": str(training_file.id)
                    }
                    
                    # Ensure all metadata values are ChromaDB-compatible (no None, all strings/numbers/bools)
                    filtered_metadata = {}
                    for k, v in metadata.items():
                        if v is not None:
                            if isinstance(v, (str, int, float, bool)):
                                filtered_metadata[k] = v
                            else:
                                filtered_metadata[k] = str(v)
                    
                    doc = Document(
                        page_content=content,
                        metadata=filtered_metadata
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read training file {training_file.filename}: {e}")
            
            if documents:
                # Add to RAG vector database
                try:
                    chunks_created = await rag_service.add_documents(documents)
                    logger.info(f"✅ Created {chunks_created} chunks for {len(documents)} documents")
                    
                    # Update training files as indexed
                    for training_file in training_files:
                        await self._mark_file_as_indexed(training_file.id, chunks_created // len(documents) if len(documents) > 0 else 1)
                        
                except Exception as e:
                    logger.error(f"❌ ChromaDB indexing failed: {e}")
                    # Mark files as failed
                    for training_file in training_files:
                        await self._mark_file_as_failed(training_file.id, str(e))
                    raise
                
                logger.info(f"✅ Added {len(documents)} training files to RAG ({chunks_created} chunks)")
            
        except Exception as e:
            logger.error(f"❌ Failed to add files to RAG: {e}")
            raise
    
    async def _mark_file_as_indexed(self, file_id: str, chunk_count: int):
        """Mark training file as indexed in RAG"""
        try:
            update_query = update(TrainingFile).where(
                TrainingFile.id == file_id
            ).values(
                is_indexed=True,
                status="indexed",
                indexed_at=datetime.now(),
                chunk_count=chunk_count,
                index_status="indexed"
            )
            await self.db.execute(update_query)
            await self.db.commit()
        except Exception as e:
            logger.warning(f"⚠️ Failed to mark file as indexed: {e}")

    async def _mark_file_as_failed(self, file_id: str, error_message: str):
        """Mark training file as failed to index"""
        try:
            update_query = update(TrainingFile).where(
                TrainingFile.id == file_id
            ).values(
                is_indexed=False,
                status="error",
                index_status="failed",
                index_error=error_message[:500]  # Limit error length
            )
            await self.db.execute(update_query)
            await self.db.commit()
        except Exception as e:
            logger.warning(f"⚠️ Failed to mark file as failed: {e}")
    
    async def delete_training_file(self, file_id: str) -> bool:
        """Delete training file from filesystem and database"""
        
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        try:
            files_deleted = []
            
            # Delete original file from filesystem
            if file_record.file_path and os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
                files_deleted.append(f"Original: {file_record.file_path}")
                logger.info(f"🗑️ Original file deleted: {file_record.file_path}")
            
            # Delete optimized MD file if it exists (Cascade Delete)
            if file_record.processed_file_path and os.path.exists(file_record.processed_file_path):
                os.remove(file_record.processed_file_path)
                files_deleted.append(f"Optimized: {file_record.processed_file_path}")
                logger.info(f"🗑️ Optimized MD file deleted: {file_record.processed_file_path}")
            
            # Also try to find and delete MD files by pattern (fallback)
            # Pattern: {file_id}_{filename}_optimized.md
            base_filename = os.path.splitext(file_record.filename)[0]
            optimized_pattern = f"{file_record.id}_{base_filename}_optimized.md"
            
            # Check common optimized directories
            optimized_dirs = [
                "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/backend/data/training_data/optimized/help_data",
                "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/backend/data/training_data/optimized/stream_templates"
            ]
            
            for opt_dir in optimized_dirs:
                if os.path.exists(opt_dir):
                    for filename in os.listdir(opt_dir):
                        if file_record.id in filename and filename.endswith('_optimized.md'):
                            opt_file_path = os.path.join(opt_dir, filename)
                            os.remove(opt_file_path)
                            files_deleted.append(f"Found optimized: {opt_file_path}")
                            logger.info(f"🗑️ Found and deleted optimized file: {opt_file_path}")
            
            # Remove from ChromaDB if indexed
            if file_record.is_indexed:
                try:
                    await self.remove_from_chromadb(file_id)
                    logger.info(f"🗑️ Removed from ChromaDB: {file_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove from ChromaDB: {e}")
            
            # Delete database record
            await self.db.delete(file_record)
            await self.db.commit()
            
            logger.info(f"🗑️ Complete deletion for {file_id}. Files removed: {', '.join(files_deleted) if files_deleted else 'None'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_id}: {e}")
            await self.db.rollback()
            raise e
    
    async def get_training_status(self) -> TrainingStatusResponse:
        """Get training status statistics for both categories"""
        
        # Get all files
        all_files = await self.get_training_files()
        
        # Calculate stats for help_data
        help_files = [f for f in all_files if f.category == "help_data"]
        help_stats = CategoryStats(
            total=len(help_files),
            ready=len([f for f in help_files if f.status == "ready"]),
            processing=len([f for f in help_files if f.status == "processing"]),
            error=len([f for f in help_files if f.status == "error"])
        )
        
        # Calculate stats for stream_templates
        template_files = [f for f in all_files if f.category == "stream_templates"]
        template_stats = CategoryStats(
            total=len(template_files),
            ready=len([f for f in template_files if f.status == "ready"]),
            processing=len([f for f in template_files if f.status == "processing"]),
            error=len([f for f in template_files if f.status == "error"])
        )
        
        return TrainingStatusResponse(
            help_data_stats=help_stats,
            stream_template_stats=template_stats,
            last_updated=datetime.utcnow().isoformat()
        )
    
    async def process_training_file(self, file_id: str) -> bool:
        """Process training file (mock implementation)"""
        
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        try:
            # Mock processing: update status to processing
            file_record.status = "processing"
            await self.db.commit()
            
            logger.info(f"⚙️ File processing started (mock): {file_id}")
            
            # In a real implementation, here you would:
            # 1. For help_data: Parse and convert to Q&A pairs
            # 2. For stream_templates: Prepare for LoRA training
            # 3. Update status to "ready" when complete
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process file {file_id}: {e}")
            await self.db.rollback()
            raise e
    
    async def _get_or_create_rag_service(self) -> RAGService:
        """Get or create RAG service instance"""
        if self.rag_service is None:
            self.rag_service = RAGService()
            await self.rag_service.initialize()
        return self.rag_service
    
    async def index_file_to_chromadb(self, file_id: str) -> Dict[str, Any]:
        """Index a training file to ChromaDB"""
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return None
        
        try:
            # Update status to indexing
            file_record.index_status = "indexing"
            await self.db.commit()
            
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Read file content
            async with aiofiles.open(file_record.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Add to ChromaDB
            chromadb_ids = await rag_service.add_documents(
                documents=[content],
                metadata=[{
                    "source": file_record.filename,
                    "category": file_record.category,
                    "file_id": file_id,
                    "upload_date": file_record.upload_date.isoformat()
                }]
            )
            
            # Update database record
            file_record.is_indexed = True
            file_record.indexed_at = datetime.utcnow()
            file_record.chromadb_ids = chromadb_ids
            file_record.chunk_count = len(chromadb_ids)
            file_record.index_status = "indexed"
            file_record.status = "indexed"
            
            await self.db.commit()
            await self.db.refresh(file_record)
            
            logger.info(f"✅ File indexed to ChromaDB: {file_id} ({len(chromadb_ids)} chunks)")
            
            return {
                "file_id": file_id,
                "filename": file_record.filename,
                "chunk_count": len(chromadb_ids),
                "indexed_at": file_record.indexed_at.isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to index file {file_id}: {e}")
            
            # Update error status
            file_record.index_status = "failed"
            file_record.index_error = str(e)
            await self.db.commit()
            
            raise e
    
    async def batch_index_to_chromadb(self, file_ids: List[str]) -> Dict[str, Any]:
        """Batch index multiple files to ChromaDB"""
        results = {
            "success": [],
            "failed": [],
            "not_found": []
        }
        
        for file_id in file_ids:
            try:
                result = await self.index_file_to_chromadb(file_id)
                if result:
                    results["success"].append(result)
                else:
                    results["not_found"].append(file_id)
            except Exception as e:
                results["failed"].append({
                    "file_id": file_id,
                    "error": str(e)
                })
        
        return results
    
    async def remove_from_chromadb(self, file_id: str) -> bool:
        """Remove a file from ChromaDB index"""
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record or not file_record.is_indexed:
            return False
        
        try:
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Remove from ChromaDB
            if file_record.chromadb_ids:
                for doc_id in file_record.chromadb_ids:
                    await rag_service.delete_document(doc_id)
            
            # Update database record
            file_record.is_indexed = False
            file_record.indexed_at = None
            file_record.chromadb_ids = None
            file_record.chunk_count = 0
            file_record.index_status = None
            
            await self.db.commit()
            
            logger.info(f"✅ File removed from ChromaDB: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove file {file_id} from index: {e}")
            await self.db.rollback()
            raise e
    
    async def get_chromadb_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics"""
        try:
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Get indexed files count
            query = select(TrainingFile).where(TrainingFile.is_indexed == True)
            result = await self.db.execute(query)
            indexed_files = result.scalars().all()
            
            # Calculate stats
            total_chunks = sum(file.chunk_count for file in indexed_files)
            
            # Get ChromaDB collection info
            collection_count = await rag_service.get_document_count()
            
            return {
                "indexed_files": len(indexed_files),
                "total_chunks": total_chunks,
                "collection_documents": collection_count,
                "by_category": {
                    "help_data": len([f for f in indexed_files if f.category == "help_data"]),
                    "stream_templates": len([f for f in indexed_files if f.category == "stream_templates"])
                },
                "vector_db_path": "data/vector_db/",
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get ChromaDB stats: {e}")
            
            return {
                "indexed_files": 0,
                "total_chunks": 0,
                "collection_documents": 0,
                "by_category": {"help_data": 0, "stream_templates": 0},
                "vector_db_path": "data/vector_db/",
                "embedding_model": "all-MiniLM-L6-v2",
                "error": str(e)
            }
    
    async def _process_uploaded_file_async(self, file_id: str, file_path: str, category: str):
        """Process uploaded file with separate DB session"""
        # Create NEW database session for async processing
        from app.models.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db_session:
            service = TrainingService(db_session)
            await service._process_uploaded_file(file_id, file_path, category)

    async def _process_uploaded_file(self, file_id: str, file_path: str, category: str):
        """Enhanced file processing with Multi-Format support"""
        
        try:
            logger.info(f"🚀 Processing uploaded file with Multi-Format Processor: {file_id}")
            
            file_path_obj = Path(file_path)
            
            # Get file record for updates
            query = select(TrainingFile).where(TrainingFile.id == file_id)
            result = await self.db.execute(query)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                logger.error(f"❌ File record not found: {file_id}")
                return
            
            # Update status to processing
            file_record.status = "processing"
            await self.db.commit()
            
            # 🚀 NEW: Multi-Format Processing
            try:
                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Process with Multi-Format Processor
                processing_result: FileProcessingResult = await multi_format_processor.process_file(
                    file_path=str(file_path_obj),
                    content=file_content
                )
                
                if not processing_result.success:
                    raise ValueError(f"Multi-format processing failed: {processing_result.error_message}")
                
                # Update file record with enhanced metadata
                file_record.original_format = processing_result.file_format.value
                file_record.optimized_format = "chunked_documents"
                file_record.conversion_status = "completed"
                file_record.document_category = processing_result.category.value
                file_record.processing_method = processing_result.processing_method
                
                processing_metadata = {
                    "file_format": processing_result.file_format.value,
                    "document_category": processing_result.category.value,
                    "processing_method": processing_result.processing_method,
                    "chunk_count": processing_result.chunk_count,
                    "original_size": len(file_content),
                    "processing_date": datetime.utcnow().isoformat(),
                    "processor_version": "2.0.0_multiformat"
                }
                
                # Index processed documents for RAG
                await self._index_processed_documents_for_rag(
                    processing_result.documents, 
                    file_record, 
                    processing_result
                )
                
                logger.info(f"✅ Multi-format processing completed: {file_path_obj.name} "
                           f"({processing_result.file_format.value}, {processing_result.chunk_count} chunks)")
                
                # Update final status
                file_record.status = "ready"
                file_record.conversion_metadata = str(processing_metadata)
                
            except Exception as multiformat_error:
                logger.warning(f"⚠️ Multi-format processing failed, falling back to legacy: {multiformat_error}")
                
                # FALLBACK: Legacy TXT zu MD Konvertierung
                final_file_path = file_path_obj
                conversion_metadata = {}
                
                if file_path_obj.suffix.lower() == '.txt':
                    logger.info(f"🔄 Fallback: TXT-Datei erkannt: {file_path_obj.name}")
                    
                    try:
                        # Bestimme optimized directory basierend auf Kategorie
                        optimized_dir = Path(self.base_path) / "optimized" / category
                        
                        # Konvertiere zu Markdown
                        from app.services.txt_to_md_converter import txt_to_md_converter
                        md_file_path = await txt_to_md_converter.convert_txt_to_md(file_path_obj, optimized_dir)
                        
                        # Update file record with conversion info
                        file_record.processed_file_path = str(md_file_path)
                        file_record.original_format = "txt"
                        file_record.optimized_format = "md"
                        file_record.conversion_status = "completed"
                        
                        conversion_metadata = {
                            "original_file": str(file_path_obj),
                            "optimized_file": str(md_file_path),
                            "conversion_date": datetime.utcnow().isoformat(),
                            "converter_version": "1.0.0_legacy"
                        }
                        
                        # Use MD file for RAG indexing
                        final_file_path = md_file_path
                        
                        logger.info(f"✅ Fallback TXT zu MD Konvertierung abgeschlossen: {md_file_path.name}")
                        
                    except Exception as e:
                        logger.error(f"❌ Fallback TXT zu MD Konvertierung fehlgeschlagen: {e}")
                        file_record.conversion_status = "failed"
                        file_record.conversion_error = str(e)
                        # Continue with original TXT file
                        final_file_path = file_path_obj
                
                # Legacy RAG indexing
                try:
                    await self._index_for_rag(final_file_path, category, file_record)
                    logger.info(f"✅ Legacy file indexed for RAG: {final_file_path.name}")
                    
                    # Update final status
                    file_record.status = "ready"
                    file_record.conversion_metadata = str(conversion_metadata) if conversion_metadata else None
                    
                except Exception as e:
                    logger.error(f"❌ Legacy RAG indexing failed: {e}")
                    file_record.status = "error"
                    file_record.index_error = str(e)
            
            await self.db.commit()
            logger.info(f"✅ File processing completed: {file_id}")
            
        except Exception as e:
            logger.error(f"❌ File processing failed for {file_id}: {e}")
            
            # Update error status
            try:
                query = select(TrainingFile).where(TrainingFile.id == file_id)
                result = await self.db.execute(query)
                file_record = result.scalar_one_or_none()
                
                if file_record:
                    file_record.status = "error"
                    file_record.processing_error = str(e)
                    await self.db.commit()
            except Exception as db_error:
                logger.error(f"❌ Failed to update error status: {db_error}")
    
    async def _index_processed_documents_for_rag(
        self, 
        documents: List[Document], 
        file_record: TrainingFile, 
        processing_result: FileProcessingResult
    ):
        """Index multi-format processed documents for RAG"""
        
        try:
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Enhance document metadata for ChromaDB compatibility
            enhanced_documents = []
            for i, doc in enumerate(documents):
                # Create clean metadata for ChromaDB
                clean_metadata = {
                    "source": str(file_record.filename),
                    "category": str(file_record.category),
                    "file_id": str(file_record.id),
                    "upload_date": file_record.upload_date.isoformat(),
                    "file_format": str(processing_result.file_format.value),
                    "document_category": str(processing_result.category.value),
                    "processing_method": str(processing_result.processing_method),
                    "chunk_index": int(i),
                    "chunk_type": str(doc.metadata.get('chunk_type', 'default')),
                    "optimized": True,
                    "source_type": str(getattr(file_record, 'manual_source_category', 'Testdaten') or 'Testdaten')
                }
                
                # Filter and ensure ChromaDB compatibility
                filtered_metadata = {}
                for key, value in clean_metadata.items():
                    if value is not None:
                        if isinstance(value, (str, int, float, bool)):
                            filtered_metadata[key] = value
                        else:
                            filtered_metadata[key] = str(value)
                
                # Create enhanced document
                enhanced_doc = Document(
                    page_content=doc.page_content,
                    metadata=filtered_metadata
                )
                enhanced_documents.append(enhanced_doc)
            
            # Add documents to RAG system
            chunk_count = await rag_service.add_documents(enhanced_documents)
            
            # Update file record
            file_record.is_indexed = True
            file_record.indexed_at = datetime.utcnow()
            file_record.chunk_count = chunk_count if isinstance(chunk_count, int) else len(enhanced_documents)
            file_record.index_status = "indexed"
            
            logger.info(f"✅ Multi-format documents indexed to RAG: {file_record.filename} "
                       f"({len(enhanced_documents)} chunks, format: {processing_result.file_format.value})")
            
        except Exception as e:
            logger.error(f"❌ Multi-format RAG indexing failed: {e}")
            file_record.index_status = "failed"
            file_record.index_error = str(e)[:500]  # Limit error message length
            raise
    
    async def _index_for_rag(self, file_path: Path, category: str, file_record: TrainingFile):
        """Index optimierte Datei für RAG"""
        
        try:
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Read file content asynchronously
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Create clean document metadata (ChromaDB compatible)
            metadata = {
                "source": str(file_record.filename),
                "category": str(category),
                "file_id": str(file_record.id),
                "upload_date": file_record.upload_date.isoformat(),
                "file_type": str(file_path.suffix),
                "optimized": bool(file_path.suffix == '.md' and '_optimized' in file_path.name),
                "source_type": str(getattr(file_record, 'manual_source_category', 'Testdaten') or 'Testdaten')
            }
            
            # Filter None values and ensure all values are ChromaDB-compatible
            clean_metadata = {}
            for key, value in metadata.items():
                if value is not None:
                    if isinstance(value, (str, int, float, bool)):
                        clean_metadata[key] = value
                    else:
                        clean_metadata[key] = str(value)
            
            # Add to RAG service
            from langchain.docstore.document import Document
            document = Document(page_content=content, metadata=clean_metadata)
            
            # Add document to RAG system
            chunk_count = await rag_service.add_documents([document])
            
            # Update file record
            file_record.is_indexed = True
            file_record.indexed_at = datetime.utcnow()
            file_record.chunk_count = chunk_count if isinstance(chunk_count, int) else 1
            file_record.index_status = "indexed"
            
            logger.info(f"✅ File indexed to RAG: {file_path.name} ({chunk_count} chunks)")
            
        except Exception as e:
            logger.error(f"❌ RAG indexing failed: {e}")
            file_record.index_status = "failed"
            file_record.index_error = str(e)[:500]  # Limit error message length
            raise