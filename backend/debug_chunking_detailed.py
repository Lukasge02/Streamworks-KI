#!/usr/bin/env python3
"""
Detailed Debug Script für Chunking-Analyse
"""

import logging
from services.intelligent_chunker import IntelligentChunker, ContentType

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

def debug_chunking_process():
    """Debug des kompletten Chunking-Prozesses"""
    
    chunker = IntelligentChunker()
    
    # Test mit dem medium document
    with open('../test_documents/small_document.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Debugging Chunking Process")
    print(f"Input content ({len(content)} chars):")
    print("-" * 50)
    print(content[:200] + "...")
    
    print("\n1. Structure splitting:")
    sections = chunker._split_by_structure(content, ContentType.TEXT)
    print(f"   Found {len(sections)} sections:")
    for i, (section_content, section_meta) in enumerate(sections[:3]):
        print(f"   Section {i+1}: {len(section_content)} chars - {section_content[:50]}...")
    
    print(f"\n2. Target chunk size: {chunker._get_target_chunk_size(ContentType.TEXT)}")
    
    print("\n3. Semantic boundary chunking for first section:")
    if sections:
        first_section_content = sections[0][0]
        target_size = chunker._get_target_chunk_size(ContentType.TEXT)
        
        semantic_chunks = chunker._chunk_with_semantic_boundaries(
            first_section_content, 
            target_size, 
            ContentType.TEXT
        )
        
        print(f"   Input: {len(first_section_content)} chars")
        print(f"   Target size: {target_size}")
        print(f"   Result: {len(semantic_chunks)} chunks")
        
        for i, (chunk_content, start, end) in enumerate(semantic_chunks):
            print(f"   Chunk {i+1}: {len(chunk_content)} chars - '{chunk_content[:50]}...'")
    
    print("\n4. Full chunking result:")
    chunks = chunker.chunk_content(content, ContentType.TEXT)
    print(f"   Final chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"   Final Chunk {i+1}: {len(chunk['content'])} chars")
        print(f"     Type: {chunk.get('metadata', {}).get('chunk_type', 'normal')}")
        print(f"     Content: '{chunk['content'][:80]}...'")

if __name__ == "__main__":
    debug_chunking_process()