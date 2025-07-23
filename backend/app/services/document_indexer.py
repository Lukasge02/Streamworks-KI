"""
⚡ DOCUMENT INDEXER - PRODUCTION READY
Efficient, fast, and reliable document indexing service
"""
import logging
from pathlib import Path
from typing import Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.multi_format_processor import multi_format_processor

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """⚡ DOCUMENT INDEXER - PRODUCTION READY"""
    
    def __init__(self):
        self.embedding_model = None
        self.chromadb_client = None
        self.collection = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize document indexer"""
        if self.is_initialized:
            return
            
        try:
            logger.info("⚡ Document Indexer initializing...")
            
            # CPU-only model - WARM UP
            import asyncio
            def load_model():
                return SentenceTransformer(
                    "intfloat/multilingual-e5-large",
                    device="cpu"
                )
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(None, load_model)
            
            # ChromaDB
            self.chromadb_client = chromadb.PersistentClient(
                path="./data/vector_db_production",
                settings=Settings(anonymized_telemetry=False)
            )
            
            try:
                self.collection = self.chromadb_client.get_collection("streamworks_training_v2")
            except:
                self.collection = self.chromadb_client.create_collection("streamworks_training_v2")
            
            self.is_initialized = True
            logger.info("✅ Document Indexer ready")
            
        except Exception as e:
            logger.error(f"❌ Document Indexer failed: {e}")
            raise
    
    async def index_file_ultra_simple(self, file_id: str, db: AsyncSession) -> Dict[str, Any]:
        """⚡ DOCUMENT INDEXING"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get file
            result = await db.execute(text("""
                SELECT tf.*, dc.name as category_name, df.name as folder_name
                FROM training_files_v2 tf
                JOIN document_categories dc ON tf.category_id = dc.id
                LEFT JOIN document_folders df ON tf.folder_id = df.id
                WHERE tf.id = :file_id AND tf.is_active = true
            """), {"file_id": file_id})
            
            file_record = result.first()
            if not file_record:
                raise ValueError(f"File {file_id} not found")
            
            # Already indexed?
            if file_record.chunk_count > 0:
                return {
                    "file_id": file_id,
                    "status": "already_indexed",
                    "chunk_count": file_record.chunk_count
                }
            
            # Look for markdown file first (for PDFs that were converted)
            storage_path = Path(file_record.storage_path)
            
            # Check if a markdown version exists
            markdown_path = None
            if storage_path.suffix.lower() == '.pdf':
                # Look for markdown file in same directory with timestamp
                storage_dir = storage_path.parent
                filename_base = storage_path.stem
                
                # Find markdown file with timestamp pattern
                for md_file in storage_dir.glob(f"{filename_base}_*.md"):
                    markdown_path = md_file
                    break
            
            # Use markdown file if available, otherwise original file
            if markdown_path and markdown_path.exists():
                logger.info(f"📄 Using markdown file: {markdown_path}")
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read().encode('utf-8')
                process_path = str(markdown_path)
            else:
                logger.info(f"📄 Using original file: {storage_path}")
                if not storage_path.exists():
                    raise FileNotFoundError(f"File not found: {storage_path}")
                with open(storage_path, 'rb') as f:
                    content = f.read()
                process_path = str(storage_path)
            
            # Process
            logger.info(f"🔄 Processing {file_record.original_filename}...")
            process_result = await multi_format_processor.process_file(process_path, content)
            
            if not process_result.success:
                raise ValueError(f"Processing failed: {process_result.error_message}")
            
            # Get total text
            if process_result.documents:
                total_text = " ".join([doc.page_content for doc in process_result.documents])
            else:
                raise ValueError("No content processed")
            
            # SIMPLE: Split into max 1000 char chunks
            chunks = []
            chunk_size = 1000
            for i in range(0, len(total_text), chunk_size):
                chunk_text = total_text[i:i + chunk_size]
                if chunk_text.strip():
                    chunks.append(chunk_text)
            
            if not chunks:
                raise ValueError("No chunks created")
            
            # Generate embeddings - BATCH für Geschwindigkeit
            logger.info(f"🧠 Generating embeddings for {len(chunks)} chunks...")
            prefixed_texts = [f"passage: {text}" for text in chunks]
            
            # Batch encoding für bessere Performance
            batch_embeddings = self.embedding_model.encode(
                prefixed_texts,
                batch_size=32,
                show_progress_bar=False
            )
            
            # Convert to lists
            embeddings = [emb.tolist() for emb in batch_embeddings]
            
            # Prepare metadata
            metadatas = []
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_ids.append(f"{file_id}_chunk_{i}")
                metadatas.append({
                    "source": file_record.original_filename,
                    "file_id": file_id,
                    "category": file_record.category_name or "unknown",
                    "folder": file_record.folder_name or "root",
                    "file_type": file_record.file_type or "unknown",
                    "chunk_index": i
                })
            
            # Add to ChromaDB
            logger.info(f"💾 Adding {len(chunks)} chunks to ChromaDB...")
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Update database
            await db.execute(text("""
                UPDATE training_files_v2 
                SET 
                    chunk_count = :count,
                    embedding_model = 'intfloat/multilingual-e5-large',
                    last_indexed_at = CURRENT_TIMESTAMP,
                    processing_status = 'indexed'
                WHERE id = :file_id
            """), {"file_id": file_id, "count": len(chunks)})
            
            await db.commit()
            
            logger.info(f"✅ Document indexing complete: {file_record.original_filename} ({len(chunks)} chunks)")
            
            return {
                "file_id": file_id,
                "filename": file_record.original_filename,
                "status": "indexed",
                "chunk_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"❌ Document indexing failed: {e}")
            
            # Update error
            try:
                await db.execute(text("""
                    UPDATE training_files_v2 
                    SET processing_status = 'error', error_message = :error
                    WHERE id = :file_id
                """), {"file_id": file_id, "error": str(e)})
                await db.commit()
            except:
                pass
            
            raise


# Global instance
document_indexer = DocumentIndexer()