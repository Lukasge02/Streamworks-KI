#!/usr/bin/env python3
"""
Quick script to ingest existing documents into ChromaDB
"""

import asyncio
import sys
from pathlib import Path
from services.docling_ingest import DoclingIngestService  
from services.embeddings import EmbeddingService
from services.vectorstore import VectorStoreService

async def ingest_documents():
    """Ingest existing PDF documents into ChromaDB for RAG"""
    
    print("🚀 Starting document ingestion...")
    
    # Initialize services
    ingester = DoclingIngestService()
    embedder = EmbeddingService()  
    vectorstore = VectorStoreService()
    
    try:
        # Initialize vector store
        await vectorstore.initialize()
        print("✅ VectorStore initialized")
        
        # Initialize embeddings
        await embedder.initialize()
        print("✅ EmbeddingService initialized")
        
        # Find existing documents
        docs_path = Path('storage/documents')
        pdf_files = list(docs_path.glob('**/*.pdf'))
        txt_files = list(docs_path.glob('**/*.txt'))
        
        all_files = pdf_files + txt_files
        print(f"🔍 Found {len(all_files)} documents to process")
        
        total_chunks = 0
        
        for doc_file in all_files[:3]:  # Process first 3 files
            try:
                print(f"📄 Processing: {doc_file.name}")
                
                # Process document with Docling
                chunks = await ingester.process_document(str(doc_file))
                print(f"   - Extracted {len(chunks)} chunks")
                
                if not chunks:
                    continue
                
                # Process chunks with embeddings (using async method)
                chunks_with_embeddings = await embedder.embed_chunks(chunks[:10])  # First 10 chunks
                print(f"   - Generated embeddings for {len(chunks_with_embeddings)} chunks")
                
                # Store in vector database
                doc_id = doc_file.stem
                await vectorstore.store_chunks(chunks_with_embeddings, doc_id)
                print(f"   ✅ Stored in ChromaDB")
                
                total_chunks += len(chunks_with_embeddings)
                
            except Exception as e:
                print(f"   ❌ Error processing {doc_file.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Verify storage
        if hasattr(vectorstore, 'collection') and vectorstore.collection:
            final_count = vectorstore.collection.count()
            print(f"✅ Final ChromaDB document count: {final_count}")
        else:
            print("⚠️ Could not verify final count")
            
        print(f"🎉 Ingestion completed! Processed {total_chunks} chunks total")
        
    except Exception as e:
        print(f"❌ Critical error during ingestion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(ingest_documents())