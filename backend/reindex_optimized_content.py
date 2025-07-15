#!/usr/bin/env python3
"""
Script to clean ChromaDB and reindex with optimized markdown content
This will fix the Q&A quality issues by using the correct training data
"""

import asyncio
import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reindex_optimized_content():
    """Clean ChromaDB and reindex with optimized markdown files"""
    
    logger.info("🧹 Starting ChromaDB cleanup and reindexing...")
    
    try:
        # Step 1: Clean ChromaDB
        vector_db_path = Path("data/vector_db")
        if vector_db_path.exists():
            logger.info(f"🗑️ Removing old ChromaDB data: {vector_db_path}")
            shutil.rmtree(vector_db_path)
        
        # Step 2: Initialize services
        from app.services.rag_service import rag_service
        from app.services.training_service import TrainingService
        from app.models.database import AsyncSessionLocal
        
        logger.info("🔧 Initializing RAG service...")
        await rag_service.initialize()
        
        # Step 3: Get all optimized markdown files
        optimized_path = Path("data/training_data/optimized/help_data")
        md_files = list(optimized_path.glob("*.md"))
        
        logger.info(f"📚 Found {len(md_files)} optimized markdown files")
        
        # Step 4: Process each file
        async with AsyncSessionLocal() as db:
            training_service = TrainingService(db)
            await training_service.initialize()
            
            for md_file in md_files:
                logger.info(f"📄 Processing: {md_file.name}")
                
                try:
                    # Read content
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create document for RAG
                    from langchain.schema import Document
                    
                    # Extract filename without UUID prefix for cleaner metadata
                    clean_filename = md_file.name
                    if '_training_data_' in clean_filename:
                        parts = clean_filename.split('_training_data_')
                        if len(parts) > 1:
                            clean_filename = f"training_data_{parts[1]}"
                    
                    document = Document(
                        page_content=content,
                        metadata={
                            'source': clean_filename,
                            'filename': clean_filename,
                            'file_path': str(md_file),
                            'type': 'optimized_markdown',
                            'category': 'help_data'
                        }
                    )
                    
                    # Add to RAG
                    await rag_service.add_documents([document])
                    
                    logger.info(f"✅ Indexed: {clean_filename}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process {md_file.name}: {e}")
        
        # Step 5: Verify indexing
        stats = await rag_service.get_stats()
        logger.info(f"🎯 Reindexing complete! Total documents: {stats.get('documents_count', 0)}")
        
        # Step 6: Test search quality
        logger.info("🔍 Testing search quality...")
        
        test_queries = [
            "StreamWorks Datenverarbeitung",
            "Was ist StreamWorks", 
            "Batch Processing",
            "Stream Processing"
        ]
        
        for query in test_queries:
            try:
                documents = await rag_service.search_documents(query, top_k=3)
                logger.info(f"Query: '{query}' -> {len(documents)} documents found")
                
                if documents:
                    for i, doc in enumerate(documents[:2], 1):
                        source = doc.metadata.get('source', 'Unknown')
                        preview = doc.page_content[:100].strip().replace('\n', ' ')
                        logger.info(f"  {i}. {source}: {preview}...")
                
            except Exception as e:
                logger.error(f"❌ Test query failed for '{query}': {e}")
        
        logger.info("✅ Reindexing process completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Reindexing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(reindex_optimized_content())