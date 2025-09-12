#!/usr/bin/env python3
"""
Example Python Code for Testing Code-Specific Chunking
This script demonstrates various Python patterns and structures.
"""

import os
import sys
from typing import List, Dict, Optional
import asyncio
import logging

# Global configuration
CHUNK_SIZE = 500
MAX_RETRIES = 3

class DocumentProcessor:
    """Process documents with intelligent chunking."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE):
        self.chunk_size = chunk_size
        self.processed_count = 0
        self.logger = logging.getLogger(__name__)
    
    async def process_document(self, document_path: str) -> Dict[str, any]:
        """
        Process a single document and return metadata.
        
        Args:
            document_path: Path to the document to process
            
        Returns:
            Dictionary containing processing results
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process the content
            chunks = self._create_chunks(content)
            metadata = self._extract_metadata(content)
            
            self.processed_count += 1
            self.logger.info(f"Processed document: {document_path}")
            
            return {
                'path': document_path,
                'chunks': len(chunks),
                'size': len(content),
                'metadata': metadata,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing {document_path}: {e}")
            return {
                'path': document_path,
                'status': 'error',
                'error': str(e)
            }
    
    def _create_chunks(self, content: str) -> List[str]:
        """Create chunks from content."""
        if not content.strip():
            return []
        
        chunks = []
        words = content.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 for space
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _extract_metadata(self, content: str) -> Dict[str, any]:
        """Extract basic metadata from content."""
        lines = content.split('\n')
        return {
            'word_count': len(content.split()),
            'line_count': len(lines),
            'char_count': len(content),
            'has_code': 'def ' in content or 'class ' in content,
            'language': 'python' if content.strip().startswith('#!') else 'unknown'
        }

async def main():
    """Main processing function."""
    processor = DocumentProcessor()
    
    # Test files to process
    test_files = [
        'document1.txt',
        'document2.pdf', 
        'document3.md'
    ]
    
    results = []
    for file_path in test_files:
        result = await processor.process_document(file_path)
        results.append(result)
    
    # Print summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"Processed {successful}/{len(results)} documents successfully")
    
    return results

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the main function
    try:
        results = asyncio.run(main())
        sys.exit(0)
    except KeyboardInterrupt:
        print("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)