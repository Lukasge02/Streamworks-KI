#!/usr/bin/env python3
"""
Debug specific content in chunks to see why retrieval fails
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.production_rag_service import production_rag

async def debug_specific_content():
    """Debug why specific content isn't found"""
    print("🔍 DEBUGGING SPECIFIC CONTENT IN CHUNKS")
    print("=" * 60)
    
    # Initialize production RAG
    await production_rag.initialize()
    
    # Get all chunks
    collection = production_rag.collection
    all_data = collection.get(include=['documents', 'metadatas'])
    
    # Search for specific terms
    search_terms = [
        ("halbjährlich", "Certificate check frequency"),
        ("jährlich", "Certificate check frequency"),
        ("Margret", "Holiday list person"),
        ("sw-dl.arvato-systems.de", "Click Once URL")
    ]
    
    for term, description in search_terms:
        print(f"\n🎯 SEARCHING FOR: '{term}' ({description})")
        print("-" * 50)
        
        found_chunks = []
        for i, doc in enumerate(all_data['documents']):
            if term.lower() in doc.lower():
                metadata = all_data['metadatas'][i]
                found_chunks.append({
                    'index': i,
                    'filename': metadata.get('filename', 'unknown'),
                    'content': doc,
                    'metadata': metadata
                })
        
        if found_chunks:
            print(f"✅ FOUND in {len(found_chunks)} chunks:")
            for chunk in found_chunks:
                print(f"\n📄 Chunk {chunk['index']}: {chunk['filename']}")
                print(f"   Type: {chunk['metadata'].get('chunk_type', 'unknown')}")
                print(f"   Size: {chunk['metadata'].get('chunk_size', 'unknown')} chars")
                
                # Show context around the term
                content = chunk['content']
                term_pos = content.lower().find(term.lower())
                if term_pos >= 0:
                    start = max(0, term_pos - 100)
                    end = min(len(content), term_pos + 100)
                    context = content[start:end]
                    print(f"   Context: ...{context}...")
        else:
            print(f"❌ NOT FOUND in any chunk!")
            
    # Test keyword search for "halbjährlich"
    print(f"\n🧪 TESTING KEYWORD SEARCH FOR 'zertifikat halbjährlich'")
    print("-" * 50)
    
    # Test the keyword extraction
    test_question = "Wie oft sollten Zertifikate geprüft werden?"
    keywords = production_rag._extract_important_keywords(test_question)
    print(f"   Extracted keywords: {keywords}")
    
    # Test exact keyword search
    keyword_results = await production_rag._exact_keyword_search(test_question)
    print(f"   Keyword search results: {len(keyword_results)}")
    for i, result in enumerate(keyword_results[:3]):
        print(f"   [{i+1}] Relevance: {result['relevance']:.2f}")
        print(f"       Source: {result['source']}")
        print(f"       Exact matches: {result.get('exact_matches', 0)}")
        print(f"       Content preview: {result['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(debug_specific_content())