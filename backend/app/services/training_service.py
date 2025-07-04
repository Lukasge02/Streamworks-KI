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
from pathlib import Path

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
            
            # Create database record with clean display name
            db_file = TrainingFile(
                id=file_id,
                filename=safe_filename,       # Technical filename with UUID
                display_name=filename,        # Clean user-friendly name
                category=category,
                file_path=original_path,
                file_size=len(file_content),
                status="ready"
            )
            
            self.db.add(db_file)
            await self.db.commit()
            await self.db.refresh(db_file)
            
            logger.info(f"📝 Database record created: {file_id}")
            
            # Process file asynchronously (TXT to MD conversion if needed)
            asyncio.create_task(self._process_uploaded_file(file_id, original_path, category))
            
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
                index_error=file.index_error
            )
            for file in files
        ]
    
    async def delete_training_file(self, file_id: str) -> bool:
        """Delete training file from filesystem and database"""
        
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        try:
            # Delete original file from filesystem
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
                logger.info(f"🗑️ Original file deleted: {file_record.file_path}")
            
            # Delete optimized MD file if it exists (Cascade Delete)
            if hasattr(file_record, 'processed_file_path') and file_record.processed_file_path:
                processed_path = file_record.processed_file_path
                if os.path.exists(processed_path):
                    os.remove(processed_path)
                    logger.info(f"🗑️ Optimized MD file deleted: {processed_path}")
                else:
                    logger.warning(f"⚠️ Optimized file not found: {processed_path}")
            
            # Delete database record
            await self.db.delete(file_record)
            await self.db.commit()
            
            logger.info(f"🗑️ Database record deleted: {file_id}")
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
    
    async def _process_uploaded_file(self, file_id: str, file_path: str, category: str):
        """Process uploaded file - erweitert für TXT zu MD Konvertierung"""
        
        try:
            logger.info(f"🔄 Processing uploaded file: {file_id}")
            
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
            
            # TXT zu MD Konvertierung
            final_file_path = file_path_obj
            conversion_metadata = {}
            
            if file_path_obj.suffix.lower() == '.txt':
                logger.info(f"🔄 TXT-Datei erkannt: {file_path_obj.name}")
                
                try:
                    # Bestimme optimized directory basierend auf Kategorie
                    optimized_dir = Path(self.base_path) / "optimized" / category
                    
                    # Konvertiere zu Markdown
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
                        "converter_version": "1.0.0"
                    }
                    
                    # Use MD file for RAG indexing
                    final_file_path = md_file_path
                    
                    logger.info(f"✅ TXT zu MD Konvertierung abgeschlossen: {md_file_path.name}")
                    
                except Exception as e:
                    logger.error(f"❌ TXT zu MD Konvertierung fehlgeschlagen: {e}")
                    file_record.conversion_status = "failed"
                    file_record.conversion_error = str(e)
                    # Continue with original TXT file
                    final_file_path = file_path_obj
            
            # Index file for RAG (using optimized MD if available, otherwise original)
            try:
                await self._index_for_rag(final_file_path, category, file_record)
                logger.info(f"✅ File indexed for RAG: {final_file_path.name}")
                
                # Update final status
                file_record.status = "ready"
                file_record.conversion_metadata = str(conversion_metadata) if conversion_metadata else None
                
            except Exception as e:
                logger.error(f"❌ RAG indexing failed: {e}")
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
    
    async def _index_for_rag(self, file_path: Path, category: str, file_record: TrainingFile):
        """Index optimierte Datei für RAG"""
        
        try:
            # Get RAG service
            rag_service = await self._get_or_create_rag_service()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document metadata
            metadata = {
                "source": file_record.filename,
                "category": category,
                "file_id": file_record.id,
                "upload_date": file_record.upload_date.isoformat(),
                "file_type": file_path.suffix,
                "optimized": file_path.suffix == '.md' and '_optimized' in file_path.name
            }
            
            # Add to RAG service
            from langchain.schema import Document
            document = Document(page_content=content, metadata=metadata)
            
            # Add document to RAG system
            chunk_count = await rag_service.add_documents([document])
            
            # Update file record
            file_record.is_indexed = True
            file_record.indexed_at = datetime.utcnow()
            file_record.chunk_count = chunk_count
            file_record.index_status = "indexed"
            
            logger.info(f"✅ File indexed to RAG: {file_path.name} ({chunk_count} chunks)")
            
        except Exception as e:
            logger.error(f"❌ RAG indexing failed: {e}")
            file_record.index_status = "failed"
            file_record.index_error = str(e)
            raise