from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import aiofiles
import uuid
from datetime import datetime
import logging

from app.core.config import settings
from app.models.schemas import TrainingFileResponse, TrainingFileCreate, TrainingStatusResponse, ManualSourceCategory
from app.services.training_service import TrainingService
from app.services.multi_format_processor import multi_format_processor
from app.models.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Multi-Format supported extensions (20+ formats)
ALLOWED_EXTENSIONS = [
    # Text & Documentation
    ".txt", ".md", ".rtf", ".log",
    # Office Documents  
    ".pdf", ".docx", ".doc", ".odt",
    # Structured Data
    ".csv", ".tsv", ".xlsx", ".xls", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    # XML Family
    ".xml", ".xsd", ".xsl", ".svg", ".rss", ".atom", 
    # Code & Scripts
    ".py", ".js", ".ts", ".java", ".sql", ".ps1", ".bat", ".sh", ".bash",
    # Web & Markup
    ".html", ".htm",
    # Configuration
    ".ini", ".cfg", ".conf",
    # Email
    ".msg", ".eml"
]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILES_PER_BATCH = 20  # Maximum files per upload

@router.post("/upload-batch")
async def upload_training_files_batch(
    files: List[UploadFile] = File(...),
    source_category: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload multiple training files with manual source categorization"""
    
    # Validate file count
    if len(files) > MAX_FILES_PER_BATCH:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES_PER_BATCH} files per batch."
        )
    
    # Validate source category
    try:
        category = ManualSourceCategory(source_category)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid source_category. Must be one of: {[c.value for c in ManualSourceCategory]}"
        )
    
    logger.info(f"📤 Batch upload: {len(files)} files as {category.value}")
    
    # Map categories to internal types
    category_mapping = {
        ManualSourceCategory.TESTDATEN: "help_data",
        ManualSourceCategory.STREAMWORKS_HILFE: "help_data", 
        ManualSourceCategory.SHAREPOINT: "help_data"
    }
    internal_category = category_mapping[category]
    
    uploaded_files = []
    failed_files = []
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        
        for file in files:
            try:
                # Validate file
                if not file.filename:
                    failed_files.append({"filename": "unknown", "error": "No filename provided"})
                    continue
                
                file_extension = os.path.splitext(file.filename)[1].lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    failed_files.append({
                        "filename": file.filename, 
                        "error": f"Invalid file extension. Allowed: {ALLOWED_EXTENSIONS}"
                    })
                    continue
                
                # Read and validate file size
                file_content = await file.read()
                if len(file_content) > MAX_FILE_SIZE:
                    failed_files.append({
                        "filename": file.filename,
                        "error": f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
                    })
                    continue
                
                # Save file using the working method
                training_file = await training_service.save_training_file(
                    filename=file.filename,
                    file_content=file_content,
                    category=internal_category
                )
                
                uploaded_files.append(training_file)
                logger.info(f"✅ Uploaded: {file.filename} ({len(file_content)} bytes)")
                
            except Exception as e:
                failed_files.append({"filename": file.filename, "error": str(e)})
                logger.error(f"❌ Failed to upload {file.filename}: {e}")
        
        # Note: Files will be processed asynchronously by the Production Document Processor
        # No need to manually add to RAG here - the async processing handles everything
        
        return {
            "message": f"Batch upload completed: {len(uploaded_files)} successful, {len(failed_files)} failed",
            "uploaded_files": len(uploaded_files),
            "failed_files": len(failed_files),
            "source_category": category.value,
            "details": {
                "successful": [f.filename for f in uploaded_files],
                "failed": failed_files
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

# Legacy single file upload (keep for compatibility)
@router.post("/upload", response_model=TrainingFileResponse)
async def upload_training_file(
    file: UploadFile = File(...),
    source_category: str = Form("Testdaten"),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload a single training file (legacy compatibility)"""
    # Convert to batch upload
    return await upload_training_files_batch([file], source_category, description, db)


@router.get("/files", response_model=List[TrainingFileResponse])
async def list_training_files(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all training files"""
    logger.info(f"📋 Listing training files - category: {category}, status: {status}")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        files = await training_service.get_training_files(category=category, status=status)
        
        logger.info(f"✅ Retrieved {len(files)} training files")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")

@router.get("/source-categories")
async def get_training_source_categories():
    """Get available source categories for training data upload"""
    return {
        "categories": [
            {
                "value": category.value,
                "description": f"Training Data aus {category.value}",
                "icon": "📚" if category == ManualSourceCategory.TESTDATEN else 
                       "🏢" if category == ManualSourceCategory.STREAMWORKS_HILFE else "☁️"
            }
            for category in ManualSourceCategory
        ],
        "upload_endpoint": "/api/v1/training/upload-batch",
        "max_files": MAX_FILES_PER_BATCH,
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "example_curl": f"""curl -X POST "http://localhost:8000/api/v1/training/upload-batch" \\
  -F "files=@document1.txt" \\
  -F "files=@document2.md" \\
  -F "source_category=StreamWorks Hilfe" \\
  -F "description=Batch upload from training tab\""""
    }

@router.delete("/files/{file_id}")
async def delete_training_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a training file"""
    logger.info(f"🗑️ Deleting training file: {file_id}")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        success = await training_service.delete_training_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File deleted successfully: {file_id}")
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status(db: AsyncSession = Depends(get_db)):
    """Get training status for both categories"""
    logger.info("📊 Getting training status")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        status = await training_service.get_training_status()
        
        logger.info("✅ Training status retrieved successfully")
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get training status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/process/{file_id}")
async def process_training_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Process a training file (mock implementation)"""
    logger.info(f"⚙️ Processing training file: {file_id}")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        success = await training_service.process_training_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File processing started: {file_id}")
        return {"message": "File processing started", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to process file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/index/{file_id}")
async def index_to_chromadb(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Index a training file to ChromaDB"""
    logger.info(f"🔍 Indexing file to ChromaDB: {file_id}")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        result = await training_service.index_file_to_chromadb(file_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File indexed successfully: {file_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to index file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index file: {str(e)}")


@router.post("/index/batch")
async def batch_index_to_chromadb(
    file_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Batch index multiple files to ChromaDB"""
    logger.info(f"🔍 Batch indexing {len(file_ids)} files to ChromaDB")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        results = await training_service.batch_index_to_chromadb(file_ids)
        
        logger.info(f"✅ Batch indexing completed")
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to batch index files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to batch index files: {str(e)}")


@router.delete("/index/{file_id}")
async def remove_from_chromadb(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a file from ChromaDB index"""
    logger.info(f"🗑️ Removing file from ChromaDB: {file_id}")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        success = await training_service.remove_from_chromadb(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or not indexed")
        
        logger.info(f"✅ File removed from index: {file_id}")
        return {"message": "File removed from index successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to remove from index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove from index: {str(e)}")


@router.get("/chromadb/stats")
async def get_chromadb_stats(db: AsyncSession = Depends(get_db)):
    """Get ChromaDB statistics"""
    logger.info("📊 Getting ChromaDB statistics")
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        stats = await training_service.get_chromadb_stats()
        
        logger.info("✅ ChromaDB stats retrieved successfully")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get ChromaDB stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/files/{file_id}/conversion-status")
async def get_conversion_status(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get TXT to MD conversion status"""
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        
        # Get file record
        files = await training_service.get_training_files()
        file_record = next((f for f in files if f.id == file_id), None)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "filename": file_record.filename,
            "original_format": getattr(file_record, 'original_format', None),
            "optimized_format": getattr(file_record, 'optimized_format', None),
            "conversion_status": getattr(file_record, 'conversion_status', None),
            "processed_file_path": getattr(file_record, 'processed_file_path', None),
            "conversion_error": getattr(file_record, 'conversion_error', None),
            "file_status": file_record.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get conversion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/optimized-content")
async def get_optimized_content(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get optimized markdown content"""
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        
        # Get file record
        files = await training_service.get_training_files()
        file_record = next((f for f in files if f.id == file_id), None)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if optimized file exists
        processed_file_path = getattr(file_record, 'processed_file_path', None)
        if not processed_file_path or not os.path.exists(processed_file_path):
            raise HTTPException(status_code=404, detail="Optimized file not found")
        
        # Read optimized content
        async with aiofiles.open(processed_file_path, 'r', encoding='utf-8') as f:
            optimized_content = await f.read()
        
        return {
            "file_id": file_id,
            "original_filename": file_record.filename,
            "optimized_filename": os.path.basename(processed_file_path),
            "optimized_content": optimized_content,
            "conversion_metadata": getattr(file_record, 'conversion_metadata', None),
            "file_size": len(optimized_content),
            "conversion_status": getattr(file_record, 'conversion_status', None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get optimized content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-stats")
async def get_conversion_stats(db: AsyncSession = Depends(get_db)):
    """Get TXT to MD conversion statistics"""
    
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        files = await training_service.get_training_files()
        
        # Filter TXT files
        txt_files = [f for f in files if f.filename.lower().endswith('.txt')]
        
        # Count conversion statuses
        conversion_stats = {
            "total_txt_files": len(txt_files),
            "conversions_completed": len([f for f in txt_files if getattr(f, 'conversion_status', None) == 'completed']),
            "conversions_failed": len([f for f in txt_files if getattr(f, 'conversion_status', None) == 'failed']),
            "conversions_pending": len([f for f in txt_files if getattr(f, 'conversion_status', None) is None]),
            "optimized_files_created": len([f for f in txt_files if getattr(f, 'processed_file_path', None) is not None])
        }
        
        # Calculate success rate
        if conversion_stats["total_txt_files"] > 0:
            conversion_stats["success_rate"] = round(
                (conversion_stats["conversions_completed"] / conversion_stats["total_txt_files"]) * 100, 2
            )
        else:
            conversion_stats["success_rate"] = 0.0
        
        return conversion_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get conversion stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 🚀 NEW MULTI-FORMAT API ENDPOINTS

@router.get("/formats/supported")
async def get_supported_formats():
    """Get list of all supported file formats"""
    logger.info("📋 Getting supported formats")
    
    try:
        formats = multi_format_processor.get_supported_formats()
        categories = multi_format_processor.get_supported_categories()
        stats = multi_format_processor.get_processing_stats()
        
        return {
            "supported_formats": formats,
            "document_categories": categories,
            "total_formats": len(formats),
            "total_categories": len(categories),
            "processing_stats": stats,
            "allowed_extensions": ALLOWED_EXTENSIONS
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get supported formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-file")
async def analyze_file_format(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a file and return format detection results without uploading"""
    logger.info(f"🔍 Analyzing file format: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Reset file position for potential reuse
        await file.seek(0)
        
        # Analyze with multi-format processor
        from app.services.multi_format_processor import FormatDetector
        detector = FormatDetector()
        
        # Create temporary file path for analysis
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=file.filename, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Detect format and category
            detected_format = detector.detect_format(temp_path, content[:1000])
            document_category = detector.categorize_document(detected_format, file.filename)
            
            # Check if format is supported
            is_supported = any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
            
            analysis_result = {
                "filename": file.filename,
                "file_size": len(content),
                "detected_format": detected_format.value,
                "document_category": document_category.value,
                "is_supported": is_supported,
                "processing_method": multi_format_processor._get_chunk_strategy(detected_format),
                "content_preview": content.decode('utf-8', errors='ignore')[:200] + "..." if len(content) > 200 else content.decode('utf-8', errors='ignore'),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ File analysis completed: {file.filename} -> {detected_format.value}")
            return analysis_result
            
        finally:
            # Cleanup temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {str(e)}")


@router.get("/processing/stats")
async def get_processing_statistics():
    """Get detailed processing statistics"""
    logger.info("📊 Getting processing statistics")
    
    try:
        stats = multi_format_processor.get_processing_stats()
        
        # Add additional insights
        enhanced_stats = {
            **stats,
            "most_processed_format": max(stats['formats_processed'].items(), key=lambda x: x[1])[0] if stats['formats_processed'] else None,
            "most_processed_category": max(stats['categories_processed'].items(), key=lambda x: x[1])[0] if stats['categories_processed'] else None,
            "supported_formats_count": len(multi_format_processor.get_supported_formats()),
            "supported_categories_count": len(multi_format_processor.get_supported_categories())
        }
        
        return enhanced_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get processing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-processing")
async def test_multi_format_processing(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Test multi-format processing without permanent storage (for debugging)"""
    logger.info(f"🧪 Testing multi-format processing: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Create temporary file for processing
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=file.filename, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process with multi-format processor
            processing_result = await multi_format_processor.process_file(temp_path, content)
            
            # Create response with processing details
            test_result = {
                "success": processing_result.success,
                "file_format": processing_result.file_format.value if processing_result.success else None,
                "document_category": processing_result.category.value if processing_result.success else None,
                "processing_method": processing_result.processing_method,
                "chunk_count": processing_result.chunk_count,
                "error_message": processing_result.error_message,
                "chunks_preview": [
                    {
                        "index": i,
                        "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for i, doc in enumerate(processing_result.documents[:3])  # First 3 chunks only
                ] if processing_result.success else [],
                "metadata": processing_result.metadata,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Test processing completed: {file.filename}")
            return test_result
            
        finally:
            # Cleanup temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"❌ Failed to test processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test processing: {str(e)}")


@router.post("/sync-filesystem")
async def sync_filesystem(db: AsyncSession = Depends(get_db)):
    """Sync database with filesystem - remove DB entries for deleted files and orphaned MD files"""
    try:
        training_service = TrainingService(db)
        await training_service.initialize()  # CRITICAL: Initialize RAG service connection
        files = await training_service.get_training_files()
        
        cleaned_count = 0
        orphaned_md_count = 0
        
        # Check database entries for missing original files
        for file in files:
            # Check if original file still exists
            if file.file_path and not os.path.exists(file.file_path):
                logger.info(f"🧹 Removing orphaned DB entry: {file.filename}")
                await training_service.delete_training_file(file.id)
                cleaned_count += 1
        
        # Check for orphaned MD files in optimized directory
        from pathlib import Path
        optimized_dir = Path("data/training_data/optimized/help_data")
        
        if optimized_dir.exists():
            # Get all MD files in optimized directory
            md_files = list(optimized_dir.glob("*.md"))
            
            for md_file in md_files:
                # Extract original filename pattern (remove _optimized.md suffix)
                original_name = md_file.stem.replace("_optimized", "") + ".txt"
                
                # Check if corresponding original TXT file exists
                original_file_path = Path("data/training_data/originals/help_data") / original_name
                
                if not original_file_path.exists():
                    logger.info(f"🧹 Removing orphaned MD file: {md_file.name}")
                    try:
                        md_file.unlink()  # Delete the orphaned MD file
                        orphaned_md_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to delete orphaned MD file {md_file.name}: {e}")
        
        return {
            "message": f"Filesystem sync completed",
            "cleaned_db_entries": cleaned_count,
            "cleaned_md_files": orphaned_md_count,
            "remaining_files": len(files) - cleaned_count,
            "total_cleaned": cleaned_count + orphaned_md_count
        }
        
    except Exception as e:
        logger.error(f"❌ Filesystem sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/health")
async def training_health_check():
    """Health check for training API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "training_api",
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE // (1024*1024),
        "features": {
            "txt_to_md_conversion": True,
            "rag_indexing": True,
            "conversion_tracking": True,
            "filesystem_sync": True
        }
    }