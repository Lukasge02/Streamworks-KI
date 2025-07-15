#!/usr/bin/env python3
"""
Debug the exact context being sent to Mistral for Query 1
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.production_rag_service import production_rag

async def debug_context_sent():
    """Debug the exact context sent to Mistral"""
    print("🔍 DEBUGGING CONTEXT SENT TO MISTRAL")
    print("=" * 60)
    
    # Initialize production RAG
    await production_rag.initialize()
    
    # Test the problematic query
    question = "Wie oft sollten Zertifikate geprüft werden?"
    print(f"🎯 QUERY: {question}")
    print("-" * 50)
    
    # Step 1: Get retrieval results
    retrieval_results = await production_rag._production_retrieval(question)
    print(f"📊 RETRIEVAL RESULTS:")
    for strategy, docs in retrieval_results.items():
        if strategy != 'all_chunks':
            print(f"   {strategy}: {len(docs)} docs")
    
    # Step 2: Build context
    context, context_meta = production_rag._build_production_context(retrieval_results, question)
    print(f"\n📄 CONTEXT METADATA:")
    print(f"   Methods used: {context_meta['methods']}")
    print(f"   Chunks used: {context_meta['chunks_used']}")
    print(f"   Context length: {context_meta['context_length']}")
    
    # Step 3: Show full context
    print(f"\n📝 FULL CONTEXT SENT TO MISTRAL:")
    print("=" * 50)
    print(context)
    print("=" * 50)
    
    # Step 4: Check for specific terms
    context_lower = context.lower()
    search_terms = ["halbjährlich", "jährlich", "zertifikat", "prüf"]
    print(f"\n🔍 SEARCHING FOR KEY TERMS IN CONTEXT:")
    for term in search_terms:
        if term in context_lower:
            # Find position and show context around it
            pos = context_lower.find(term)
            start = max(0, pos - 50)
            end = min(len(context), pos + 50)
            context_snippet = context[start:end]
            print(f"   ✅ '{term}' found: ...{context_snippet}...")
        else:
            print(f"   ❌ '{term}' NOT found in context")

if __name__ == "__main__":
    asyncio.run(debug_context_sent())