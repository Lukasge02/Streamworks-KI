"""
🏢 ENTERPRISE CHROMADB INDEXER - WORLD-CLASS RAG SYSTEM
Integrated with Enterprise Intelligent Chunker for optimal performance
Advanced indexing with chunk quality metrics and visualization support

Updated: 2025-07-16 - Full Enterprise Integration
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..core.config import settings
from ..services.multi_format_processor import multi_format_processor
from .enterprise_intelligent_chunker import enterprise_chunker, ChunkStrategy

logger = logging.getLogger(__name__)


class EnterpriseChromaDBIndexer:
    """
    🏆 ENTERPRISE CHROMADB INDEXER - WORLD-CLASS PERFORMANCE
    Integrated with intelligent chunking for optimal RAG results
    """
    
    def __init__(self):
        self.embedding_model = None
        self.chromadb_client = None
        self.collection = None
        # Will be replaced by Enterprise Intelligent Chunker
        self.legacy_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Enterprise configuration
        self.enterprise_config = {
            "use_intelligent_chunking": True,
            "chunk_strategy": ChunkStrategy.HYBRID_INTELLIGENT,
            "store_chunk_metadata": True,
            "quality_threshold": 0.6,
            "max_chunks_per_file": 50
        }
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize ChromaDB connection and models"""
        if self.is_initialized:
            return
            
        try:
            # Load embedding model
            logger.info("🚀 Loading embedding model...")
            self.embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")
            
            # Initialize ChromaDB
            logger.info("🗄️ Connecting to ChromaDB...")
            self.chromadb_client = chromadb.PersistentClient(
                path="./data/vector_db_production",
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.chromadb_client.get_collection("streamworks_training_v2")
            except:
                self.collection = self.chromadb_client.create_collection(
                    name="streamworks_training_v2",
                    metadata={"description": "Enterprise training documents"}
                )
            
            self.is_initialized = True
            logger.info("✅ Enterprise ChromaDB Indexer initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize indexer: {e}")
            raise
    
    async def index_file(self, file_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Index a single file to ChromaDB
        Returns indexing results with chunk count
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get file from database
            query = """
            SELECT 
                tf.*, 
                dc.name as category_name, 
                df.name as folder_name
            FROM training_files_v2 tf
            JOIN document_categories dc ON tf.category_id = dc.id
            LEFT JOIN document_folders df ON tf.folder_id = df.id
            WHERE tf.id = :file_id AND tf.is_active = true
            """
            
            result = await db.execute(text(query), {"file_id": file_id})
            file_record = result.first()
            
            if not file_record:
                raise ValueError(f"File {file_id} not found")
            
            # Check if already indexed
            if file_record.last_indexed_at and file_record.chunk_count > 0:
                logger.info(f"📋 File already indexed: {file_record.original_filename}")
                return {
                    "file_id": file_id,
                    "status": "already_indexed",
                    "chunk_count": file_record.chunk_count
                }
            
            # Read file content
            storage_path = Path(file_record.storage_path)
            if not storage_path.exists():
                raise FileNotFoundError(f"File not found: {storage_path}")
            
            # Process file based on type
            with open(storage_path, 'rb') as f:
                content = f.read()
            
            # Use multi-format processor
            process_result = await multi_format_processor.process_file(
                str(storage_path), 
                content
            )
            
            if not process_result.success:
                error_msg = process_result.error_message or "Unknown processing error"
                raise ValueError(f"Failed to process file: {error_msg}")
            
            # 🧠 ENTERPRISE INTELLIGENT CHUNKING
            if self.enterprise_config["use_intelligent_chunking"]:
                # Get raw content for intelligent chunking
                combined_content = "\n".join([doc.page_content for doc in process_result.documents]) if process_result.documents else "No content processed"
                
                # Apply enterprise intelligent chunking
                enterprise_chunks = await enterprise_chunker.intelligent_chunking(
                    combined_content,
                    file_record.original_filename,
                    self.enterprise_config["chunk_strategy"]
                )
                
                # Filter by quality threshold
                quality_chunks = [
                    chunk for chunk in enterprise_chunks
                    if chunk.quality_score >= self.enterprise_config["quality_threshold"]
                ]
                
                # Limit chunks per file
                if len(quality_chunks) > self.enterprise_config["max_chunks_per_file"]:
                    quality_chunks = quality_chunks[:self.enterprise_config["max_chunks_per_file"]]
                
                # Convert to Document format for ChromaDB
                chunks = []
                for chunk in quality_chunks:
                    doc = Document(
                        page_content=chunk.content,
                        metadata={
                            "source": file_record.original_filename,
                            "file_id": file_id,
                            "category": file_record.category_name,
                            "folder": file_record.folder_name or "root",
                            "file_type": file_record.file_type,
                            "upload_date": str(file_record.created_at),
                            # Enterprise chunk metadata
                            "chunk_id": chunk.id,
                            "chunk_index": chunk.chunk_index,
                            "quality_score": chunk.quality_score,
                            "semantic_density": chunk.semantic_density,
                            "readability_score": chunk.readability_score,
                            "chunk_type": chunk.chunk_type,
                            "strategy_used": chunk.strategy_used.value,
                            "quality_assessment": chunk.quality_assessment.value,
                            "key_concepts": ",".join(chunk.key_concepts),
                            "entities": ",".join(chunk.entities),
                            "start_char": chunk.start_char,
                            "end_char": chunk.end_char
                        }
                    )
                    chunks.append(doc)
                
                logger.info(f"🧠 Created {len(chunks)} enterprise chunks (filtered from {len(enterprise_chunks)})")
                
            else:
                # Legacy chunking fallback
                if process_result.documents:
                    # Update metadata for each document
                    for doc in process_result.documents:
                        doc.metadata.update({
                            "source": file_record.original_filename,
                            "file_id": file_id,
                            "category": file_record.category_name,
                            "folder": file_record.folder_name or "root",
                            "file_type": file_record.file_type,
                            "upload_date": str(file_record.created_at)
                        })
                    
                    chunks = process_result.documents
                else:
                    # Create single document from content
                    combined_content = "\n".join([doc.page_content for doc in process_result.documents]) if process_result.documents else "No content processed"
                    
                    documents = [
                        Document(
                            page_content=combined_content,
                            metadata={
                                "source": file_record.original_filename,
                                "file_id": file_id,
                                "category": file_record.category_name,
                                "folder": file_record.folder_name or "root",
                                "file_type": file_record.file_type,
                                "upload_date": str(file_record.created_at)
                            }
                        )
                    ]
                    chunks = self.legacy_text_splitter.split_documents(documents)
            
            # 🚀 ENTERPRISE CHROMADB INDEXING
            if chunks:
                chunk_texts = [chunk.page_content for chunk in chunks]
                chunk_metadatas = [chunk.metadata for chunk in chunks]
                
                # Generate enterprise chunk IDs
                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    if hasattr(chunk, 'metadata') and 'chunk_id' in chunk.metadata:
                        chunk_ids.append(chunk.metadata['chunk_id'])
                    else:
                        chunk_ids.append(f"{file_id}_chunk_{i}")
                
                # Add with E5 prefix for better embeddings
                prefixed_texts = [f"passage: {text}" for text in chunk_texts]
                
                if self.embedding_model:
                    embeddings = self.embedding_model.encode(prefixed_texts)
                    
                    # Add to collection with embeddings
                    self.collection.add(
                        documents=chunk_texts,
                        embeddings=embeddings.tolist(),
                        metadatas=chunk_metadatas,
                        ids=chunk_ids
                    )
                else:
                    # Add without embeddings (ChromaDB will generate)
                    self.collection.add(
                        documents=chunk_texts,
                        metadatas=chunk_metadatas,
                        ids=chunk_ids
                    )
            else:
                logger.warning(f"⚠️ No chunks created for file {file_record.original_filename}")
                chunks = []
            
            # Update database
            update_query = """
            UPDATE training_files_v2 
            SET 
                chunk_count = :chunk_count,
                processing_status = 'indexed',
                embedding_model = :model,
                last_indexed_at = CURRENT_TIMESTAMP,
                processing_status = 'indexed'
            WHERE id = :file_id
            """
            
            await db.execute(text(update_query), {
                "file_id": file_id,
                "chunk_count": len(chunks),
                "model": "intfloat/multilingual-e5-large"
            })
            
            await db.commit()
            
            logger.info(f"✅ Indexed {len(chunks)} chunks for: {file_record.original_filename}")
            
            return {
                "file_id": file_id,
                "filename": file_record.original_filename,
                "status": "indexed",
                "chunk_count": len(chunks),
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to index file {file_id}: {e}")
            
            # Update error status
            try:
                error_query = """
                UPDATE training_files_v2 
                SET 
                    processing_status = 'error',
                    error_message = :error
                WHERE id = :file_id
                """
                await db.execute(text(error_query), {
                    "file_id": file_id,
                    "error": str(e)
                })
                await db.commit()
            except:
                pass
            
            raise
    
    async def batch_index_files(self, file_ids: List[str], db: AsyncSession) -> Dict[str, Any]:
        """Batch index multiple files"""
        results = {
            "total": len(file_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for file_id in file_ids:
            try:
                result = await self.index_file(file_id, db)
                results["successful"] += 1
                results["results"].append(result)
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "file_id": file_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    async def remove_file_from_index(self, file_id: str, db: AsyncSession) -> bool:
        """Remove all chunks for a file from ChromaDB"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get all chunk IDs for this file
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                # Delete chunks
                self.collection.delete(ids=results['ids'])
                
                # Update database
                update_query = """
                UPDATE training_files_v2 
                SET 
                    chunk_count = 0,
                    last_indexed_at = NULL,
                    processing_status = 'pending'
                WHERE id = :file_id
                """
                await db.execute(text(update_query), {"file_id": file_id})
                await db.commit()
                
                logger.info(f"🗑️ Removed {len(results['ids'])} chunks for file {file_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove file {file_id} from index: {e}")
            raise


# Global instance
enterprise_indexer = EnterpriseChromaDBIndexer()