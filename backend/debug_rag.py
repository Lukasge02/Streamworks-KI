#!/usr/bin/env python3
"""
Debug script for RAG Service
For VS Code debugging configuration
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import RAGService
from app.core.config import settings


async def debug_rag_service():
    """Debug RAG service functionality"""
    print("🔍 Debugging RAG Service")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        print("✅ RAG Service initialized")
        
        # Test query
        test_query = "What is StreamWorks?"
        print(f"🔍 Testing query: {test_query}")
        
        # Perform search
        result = await rag_service.search_documents(test_query)
        print(f"📊 Search result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_rag_service())