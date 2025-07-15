#!/usr/bin/env python3
"""
RAG Retrieval Debug Script
Analyzes critical retrieval failures for specific queries
"""
import asyncio
import logging
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import os
import sys

# Add backend path for imports
sys.path.append(str(Path(__file__).parent))

from app.services.rag_service import rag_service
from app.core.config import settings
from langchain.schema import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGDebugger:
    """Debug RAG retrieval failures with detailed analysis"""
    
    def __init__(self):
        self.critical_queries = [
            {
                "query": "Wie oft sollten Zertifikate geprüft werden?",
                "expected_keywords": ["halbjährlich", "jährlich", "zertifikat", "prüfung"],
                "expected_source": "Regelmäßige Tätigkeiten"
            },
            {
                "query": "Wer ist für Feiertagslisten zuständig?",
                "expected_keywords": ["Margret", "feiertag", "liste", "zuständig"],
                "expected_source": "Regelmäßige Tätigkeiten"
            },
            {
                "query": "Welche URL ist für Click Once Installation?",
                "expected_keywords": ["https://sw-dl.arvato-systems.de", "click once", "installation", "url"],
                "expected_source": "Desktop Client"
            }
        ]
        
    async def debug_all_queries(self):
        """Debug all critical queries"""
        print("🔍 STARTING RAG RETRIEVAL DEBUG ANALYSIS")
        print("=" * 60)
        
        # Initialize RAG service
        await rag_service.initialize()
        
        for i, query_info in enumerate(self.critical_queries, 1):
            print(f"\n🧪 TEST {i}: {query_info['query']}")
            print("-" * 50)
            
            await self.debug_single_query(query_info)
            
        # Overall analysis
        await self.analyze_chunks_for_keywords()
        
    async def debug_single_query(self, query_info: Dict[str, Any]):
        """Debug a single query with detailed analysis"""
        query = query_info["query"]
        expected_keywords = query_info["expected_keywords"]
        expected_source = query_info["expected_source"]
        
        print(f"📋 Query: {query}")
        print(f"🎯 Expected keywords: {expected_keywords}")
        print(f"📄 Expected source: {expected_source}")
        
        # Step 1: Test raw similarity search
        print("\n1. RAW SIMILARITY SEARCH:")
        await self.test_raw_similarity_search(query, expected_keywords)
        
        # Step 2: Test different query formulations
        print("\n2. QUERY VARIATIONS:")
        await self.test_query_variations(query, expected_keywords)
        
        # Step 3: Test embedding analysis
        print("\n3. EMBEDDING ANALYSIS:")
        await self.analyze_embeddings(query, expected_keywords)
        
        # Step 4: Test full RAG pipeline
        print("\n4. FULL RAG PIPELINE:")
        await self.test_full_rag_pipeline(query)
        
    async def test_raw_similarity_search(self, query: str, expected_keywords: List[str]):
        """Test raw ChromaDB similarity search"""
        try:
            # Get raw documents from similarity search
            docs = await rag_service.search_documents(query, top_k=10)
            
            print(f"   Found {len(docs)} documents")
            
            if docs:
                for i, doc in enumerate(docs[:5]):  # Show top 5
                    filename = doc.metadata.get('filename', 'unknown')
                    content_preview = doc.page_content[:100].replace('\n', ' ')
                    
                    # Check for expected keywords
                    keyword_matches = [kw for kw in expected_keywords if kw.lower() in doc.page_content.lower()]
                    
                    print(f"   [{i+1}] {filename}")
                    print(f"       Content: {content_preview}...")
                    print(f"       Keyword matches: {keyword_matches}")
                    
                    if keyword_matches:
                        print(f"       ✅ Contains expected keywords!")
                    else:
                        print(f"       ❌ No expected keywords found")
            else:
                print("   ❌ No documents found!")
                
        except Exception as e:
            print(f"   ❌ Error in similarity search: {e}")
            
    async def test_query_variations(self, base_query: str, expected_keywords: List[str]):
        """Test different query formulations"""
        variations = [
            base_query,
            " ".join(expected_keywords),  # Keywords only
            f"{base_query} {' '.join(expected_keywords)}",  # Combined
            expected_keywords[0] if expected_keywords else base_query,  # First keyword only
        ]
        
        for i, variation in enumerate(variations):
            print(f"   Variation {i+1}: '{variation}'")
            
            try:
                docs = await rag_service.search_documents(variation, top_k=3)
                print(f"   Results: {len(docs)} documents")
                
                if docs:
                    for j, doc in enumerate(docs):
                        keyword_matches = [kw for kw in expected_keywords if kw.lower() in doc.page_content.lower()]
                        if keyword_matches:
                            print(f"      [{j+1}] ✅ {doc.metadata.get('filename', 'unknown')} - {keyword_matches}")
                            break
                    else:
                        print(f"      ❌ No matching documents")
                else:
                    print(f"      ❌ No results")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
                
    async def analyze_embeddings(self, query: str, expected_keywords: List[str]):
        """Analyze embedding quality and similarity scores"""
        try:
            # Get access to the vector store collection
            collection = rag_service.vector_store._collection
            
            # Prepare query embedding
            prepared_query = rag_service._prepare_text_for_e5(query, is_query=True)
            query_embedding = rag_service.embeddings.embed_query(prepared_query)
            
            print(f"   Query embedding shape: {len(query_embedding)}")
            print(f"   Prepared query: '{prepared_query}'")
            
            # Search with scores
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                include=['documents', 'metadatas', 'distances']
            )
            
            if results['documents'] and results['documents'][0]:
                print(f"   Found {len(results['documents'][0])} results with scores:")
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    filename = metadata.get('filename', 'unknown')
                    content_preview = doc[:100].replace('\n', ' ')
                    
                    # Check for expected keywords
                    keyword_matches = [kw for kw in expected_keywords if kw.lower() in doc.lower()]
                    
                    print(f"   [{i+1}] Distance: {distance:.4f} | {filename}")
                    print(f"       Keywords: {keyword_matches}")
                    print(f"       Content: {content_preview}...")
                    
                    if keyword_matches:
                        print(f"       ✅ MATCH FOUND! Distance: {distance:.4f}")
                        
                        # Show more context for matches
                        print(f"       Full context:")
                        context_lines = doc.split('\n')
                        for line in context_lines:
                            if any(kw.lower() in line.lower() for kw in expected_keywords):
                                print(f"         >> {line.strip()}")
                        break
            else:
                print("   ❌ No embedding results")
                
        except Exception as e:
            print(f"   ❌ Error in embedding analysis: {e}")
            
    async def test_full_rag_pipeline(self, query: str):
        """Test the complete RAG pipeline"""
        try:
            result = await rag_service.query(query)
            
            print(f"   Answer: {result['answer'][:200]}...")
            print(f"   Sources: {result['sources']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Search results: {result['search_results']}")
            
            if result['search_results'] > 0:
                print(f"   ✅ Pipeline found {result['search_results']} documents")
            else:
                print(f"   ❌ Pipeline found no documents")
                
        except Exception as e:
            print(f"   ❌ Error in RAG pipeline: {e}")
            
    async def analyze_chunks_for_keywords(self):
        """Analyze all chunks to find where expected content is located"""
        print("\n" + "=" * 60)
        print("🔍 ANALYZING ALL CHUNKS FOR EXPECTED CONTENT")
        print("=" * 60)
        
        # Get all chunks
        all_chunks = await rag_service.get_all_chunks(limit=1000)
        print(f"📊 Total chunks in database: {len(all_chunks)}")
        
        # Analyze for each query's keywords
        for query_info in self.critical_queries:
            print(f"\n🔍 Searching for: {query_info['expected_keywords']}")
            print("-" * 40)
            
            found_chunks = []
            for i, chunk in enumerate(all_chunks):
                content = chunk.page_content.lower()
                
                # Check if any expected keyword is in this chunk
                matches = [kw for kw in query_info['expected_keywords'] if kw.lower() in content]
                
                if matches:
                    found_chunks.append({
                        'chunk_index': i,
                        'filename': chunk.metadata.get('filename', 'unknown'),
                        'source': chunk.metadata.get('source', 'unknown'),
                        'matches': matches,
                        'content_preview': chunk.page_content[:200].replace('\n', ' ')
                    })
            
            if found_chunks:
                print(f"   ✅ Found {len(found_chunks)} chunks with expected content:")
                for chunk_info in found_chunks[:5]:  # Show first 5
                    print(f"     📄 {chunk_info['filename']}")
                    print(f"        Matches: {chunk_info['matches']}")
                    print(f"        Preview: {chunk_info['content_preview']}...")
                    print()
            else:
                print(f"   ❌ No chunks found with expected keywords: {query_info['expected_keywords']}")
                
                # Try partial matching
                partial_matches = []
                for keyword in query_info['expected_keywords']:
                    for chunk in all_chunks:
                        if keyword.lower()[:3] in chunk.page_content.lower():  # First 3 chars
                            partial_matches.append({
                                'keyword': keyword,
                                'filename': chunk.metadata.get('filename', 'unknown'),
                                'content': chunk.page_content[:100]
                            })
                            
                if partial_matches:
                    print(f"   🔍 Partial matches found:")
                    for match in partial_matches[:3]:
                        print(f"     '{match['keyword']}' in {match['filename']}: {match['content']}...")
                        
    async def check_pdf_content(self):
        """Check if PDFs are properly processed"""
        print("\n" + "=" * 60)
        print("📄 CHECKING PDF CONTENT PROCESSING")
        print("=" * 60)
        
        # Check for PDF-related chunks
        all_chunks = await rag_service.get_all_chunks(limit=1000)
        
        pdf_chunks = [chunk for chunk in all_chunks if 'pdf' in chunk.metadata.get('filename', '').lower()]
        
        print(f"📊 Total PDF chunks: {len(pdf_chunks)}")
        
        if pdf_chunks:
            for chunk in pdf_chunks[:5]:
                filename = chunk.metadata.get('filename', 'unknown')
                print(f"   📄 {filename}")
                print(f"      Content length: {len(chunk.page_content)}")
                print(f"      Preview: {chunk.page_content[:100].replace('\n', ' ')}...")
                print()
        else:
            print("   ❌ No PDF chunks found!")
            
            # Check what files are available
            unique_files = set()
            for chunk in all_chunks:
                filename = chunk.metadata.get('filename', 'unknown')
                unique_files.add(filename)
                
            print(f"   Available files: {sorted(unique_files)}")

async def main():
    """Main debug function"""
    debugger = RAGDebugger()
    
    try:
        await debugger.debug_all_queries()
        await debugger.check_pdf_content()
        
        print("\n" + "=" * 60)
        print("🎯 DEBUG ANALYSIS COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())