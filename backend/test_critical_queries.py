#!/usr/bin/env python3
"""
Quick test for critical queries after fixing chunk sizes
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.production_rag_service import production_rag

async def test_critical_queries():
    """Test the critical queries that failed before"""
    print("🧪 TESTING CRITICAL QUERIES WITH NEW CHUNK SETTINGS")
    print("=" * 60)
    
    # Initialize production RAG
    await production_rag.initialize()
    
    critical_queries = [
        "Wie oft sollten Zertifikate geprüft werden?",
        "Wer ist für Feiertagslisten zuständig?", 
        "Welche URL ist für Click Once Installation?"
    ]
    
    for i, query in enumerate(critical_queries, 1):
        print(f"\n🔍 TEST {i}: {query}")
        print("-" * 50)
        
        try:
            result = await production_rag.ask(query)
            print(f"✅ ANSWER: {result.answer}")
            print(f"📊 CONFIDENCE: {result.confidence}")
            print(f"📄 SOURCES: {result.sources}")
            print(f"⏱️ TIME: {result.processing_time}s")
            print(f"📈 CHUNKS: {result.chunks_analyzed}")
            
            # Check for specific expected content
            answer_lower = result.answer.lower()
            if i == 1 and ("halbjährlich" in answer_lower or "jährlich" in answer_lower):
                print("🎯 SUCCESS: Found certificate check frequency!")
            elif i == 2 and "margret" in answer_lower:
                print("🎯 SUCCESS: Found Margret for holiday lists!")
            elif i == 3 and "https://sw-dl.arvato-systems.de" in result.answer:
                print("🎯 SUCCESS: Found Click Once URL!")
            elif "keine informationen" not in answer_lower:
                print("✅ Got specific answer (not 'keine Informationen')")
            else:
                print("⚠️ Still generic/empty answer")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_critical_queries())