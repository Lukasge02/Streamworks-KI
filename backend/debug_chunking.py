#!/usr/bin/env python3
"""
Debug Script für Chunking-Probleme
"""

import logging
from services.intelligent_chunker import IntelligentChunker, ContentType

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

def debug_minimal_text():
    print("🔍 Debug: Minimal Text Chunking")
    
    chunker = IntelligentChunker()
    minimal_content = "Sehr kurzer Text mit nur wenigen Wörtern."
    
    print(f"Input: '{minimal_content}' ({len(minimal_content)} chars)")
    
    try:
        chunks = chunker.chunk_content(minimal_content, ContentType.TEXT)
        print(f"Result: {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: '{chunk['content'][:50]}...'")
            print(f"    Type: {chunk.get('metadata', {}).get('chunk_type', 'normal')}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_minimal_text()