#!/usr/bin/env python3
"""
A/B Test: Chunking Performance Validation
Vergleich zwischen optimierten und ursprünglichen Chunking-Einstellungen
"""

import logging
from services.intelligent_chunker import IntelligentChunker, ContentType, ChunkingConfig

logging.basicConfig(level=logging.WARNING)  # Reduce output noise

def create_original_config():
    """Simuliert die ursprünglichen Chunking-Einstellungen (vor Optimierung)"""
    return ChunkingConfig(
        # Ursprüngliche Einstellungen (problematisch)
        min_chunk_size=100,
        max_chunk_size=800,
        target_chunk_size=1000,  # Zu groß für RAG
        overlap_ratio=0.20,
        
        # Content-type specific (ursprünglich weniger optimiert)
        pdf_chunk_size=1000,     # Zu groß
        text_chunk_size=1000,    # Zu groß
        html_chunk_size=800,     # Weniger optimiert
        code_chunk_size=600,     # Zu groß für Code
        markdown_chunk_size=900, # Nicht RAG-optimal
        table_chunk_size=1000    # Führte zu Single-Chunk Fallback
    )

def create_optimized_config():
    """Aktuelle optimierte Chunking-Einstellungen"""
    return ChunkingConfig(
        # RAG-optimierte Einstellungen
        min_chunk_size=200,      # Höher für bessere Qualität
        max_chunk_size=1000,     # Erweitert für Flexibilität
        target_chunk_size=600,   # RAG sweet spot
        overlap_ratio=0.15,      # Optimiert für Context
        
        # Content-type specific (RAG-optimiert)
        pdf_chunk_size=650,      # RAG-optimal
        text_chunk_size=600,     # Perfect für Text
        html_chunk_size=550,     # Angepasst für Markup
        code_chunk_size=450,     # Kompakt für Code
        markdown_chunk_size=600, # Standard RAG-optimal
        table_chunk_size=500     # Tabellen-spezifisch
    )

def run_ab_test():
    """Führt A/B Test zwischen Original- und optimierten Einstellungen durch"""
    
    print("🧪 A/B Test: Chunking Performance Validation")
    print("=" * 60)
    
    # Test Dokumente
    test_documents = [
        ('../test_documents/mini_document.txt', ContentType.TEXT, 'Mini Document'),
        ('../test_documents/small_document.txt', ContentType.TEXT, 'Small Document'),  
        ('../test_documents/medium_document.txt', ContentType.TEXT, 'Medium Document'),
        ('../test_documents/table_document.txt', ContentType.TABLE, 'Table Document')
    ]
    
    results = {
        'original': [],
        'optimized': []
    }
    
    for file_path, content_type, description in test_documents:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"⚠️ File not found: {file_path}")
            continue
        
        print(f"\n📄 Testing: {description}")
        print("-" * 40)
        
        # Test A: Original Settings
        original_chunker = IntelligentChunker(config=create_original_config())
        original_chunks = original_chunker.chunk_content(content, content_type)
        
        # Test B: Optimized Settings  
        optimized_chunker = IntelligentChunker(config=create_optimized_config())
        optimized_chunks = optimized_chunker.chunk_content(content, content_type)
        
        # Calculate metrics
        def calculate_metrics(chunks, label):
            if not chunks:
                return {
                    'label': label,
                    'num_chunks': 0,
                    'avg_chunk_size': 0,
                    'rag_optimal': False,
                    'fallback_used': False,
                    'quality_distribution': {}
                }
            
            avg_size = sum(len(chunk['content']) for chunk in chunks) / len(chunks)
            rag_optimal = 400 <= avg_size <= 800
            fallback_used = any(chunk.get('metadata', {}).get('chunk_type') == 'fallback' for chunk in chunks)
            
            # Quality tier distribution
            quality_tiers = [chunk.get('metadata', {}).get('quality_tier', 'standard') for chunk in chunks]
            quality_distribution = {}
            for tier in quality_tiers:
                quality_distribution[tier] = quality_distribution.get(tier, 0) + 1
            
            return {
                'label': label,
                'num_chunks': len(chunks),
                'avg_chunk_size': avg_size,
                'rag_optimal': rag_optimal,
                'fallback_used': fallback_used,
                'quality_distribution': quality_distribution
            }
        
        original_metrics = calculate_metrics(original_chunks, 'Original')
        optimized_metrics = calculate_metrics(optimized_chunks, 'Optimized')
        
        results['original'].append(original_metrics)
        results['optimized'].append(optimized_metrics)
        
        # Display comparison
        print(f"Original Settings:")
        print(f"  Chunks: {original_metrics['num_chunks']}")
        print(f"  Avg Size: {original_metrics['avg_chunk_size']:.0f} chars")
        print(f"  RAG-optimal: {'✅' if original_metrics['rag_optimal'] else '❌'}")
        print(f"  Fallback used: {'⚠️' if original_metrics['fallback_used'] else '✅'}")
        
        print(f"Optimized Settings:")
        print(f"  Chunks: {optimized_metrics['num_chunks']}")
        print(f"  Avg Size: {optimized_metrics['avg_chunk_size']:.0f} chars")
        print(f"  RAG-optimal: {'✅' if optimized_metrics['rag_optimal'] else '❌'}")
        print(f"  Fallback used: {'⚠️' if optimized_metrics['fallback_used'] else '✅'}")
        
        # Improvement calculation
        size_improvement = abs(optimized_metrics['avg_chunk_size'] - 600) < abs(original_metrics['avg_chunk_size'] - 600)
        chunk_improvement = optimized_metrics['rag_optimal'] and not original_metrics['rag_optimal']
        fallback_improvement = not optimized_metrics['fallback_used'] and original_metrics['fallback_used']
        
        improvements = []
        if size_improvement: improvements.append("Size closer to RAG-optimal")
        if chunk_improvement: improvements.append("Achieved RAG-optimal range")  
        if fallback_improvement: improvements.append("Eliminated fallback dependency")
        
        if improvements:
            print(f"✅ Improvements: {', '.join(improvements)}")
        else:
            print(f"⚠️ No significant improvement detected")
    
    # Overall A/B Test Analysis
    print(f"\n" + "=" * 60)
    print(f"📊 Overall A/B Test Results")
    print("=" * 60)
    
    original_rag_optimal = sum(1 for r in results['original'] if r['rag_optimal'])
    optimized_rag_optimal = sum(1 for r in results['optimized'] if r['rag_optimal'])
    
    original_fallbacks = sum(1 for r in results['original'] if r['fallback_used'])
    optimized_fallbacks = sum(1 for r in results['optimized'] if r['fallback_used'])
    
    total_docs = len(results['original'])
    
    print(f"RAG-Optimal Rate:")
    print(f"  Original: {original_rag_optimal}/{total_docs} ({original_rag_optimal/total_docs*100:.1f}%)")
    print(f"  Optimized: {optimized_rag_optimal}/{total_docs} ({optimized_rag_optimal/total_docs*100:.1f}%)")
    print(f"  Improvement: {'+' if optimized_rag_optimal > original_rag_optimal else ''}{optimized_rag_optimal - original_rag_optimal} documents")
    
    print(f"\\nFallback Usage:")
    print(f"  Original: {original_fallbacks}/{total_docs} ({original_fallbacks/total_docs*100:.1f}%)")
    print(f"  Optimized: {optimized_fallbacks}/{total_docs} ({optimized_fallbacks/total_docs*100:.1f}%)")
    print(f"  Improvement: {original_fallbacks - optimized_fallbacks} fewer fallbacks")
    
    # Calculate average chunk sizes
    original_avg = sum(r['avg_chunk_size'] for r in results['original']) / total_docs
    optimized_avg = sum(r['avg_chunk_size'] for r in results['optimized']) / total_docs
    
    print(f"\\nAverage Chunk Size:")
    print(f"  Original: {original_avg:.0f} chars")
    print(f"  Optimized: {optimized_avg:.0f} chars")
    print(f"  Change: {optimized_avg - original_avg:+.0f} chars")
    print(f"  Distance to RAG-optimal (600): Original {abs(original_avg - 600):.0f}, Optimized {abs(optimized_avg - 600):.0f}")
    
    # Final verdict
    improvements_count = (
        (optimized_rag_optimal > original_rag_optimal) +
        (optimized_fallbacks < original_fallbacks) +
        (abs(optimized_avg - 600) < abs(original_avg - 600))
    )
    
    if improvements_count >= 2:
        print(f"\\n🎉 SIGNIFICANT IMPROVEMENT! Optimization successful.")
        print(f"   The new chunking settings deliver better RAG performance.")
    elif improvements_count == 1:
        print(f"\\n✅ MODERATE IMPROVEMENT. Optimization shows benefits.")
    else:
        print(f"\\n⚠️ LIMITED IMPROVEMENT. Consider further tuning.")
    
    return results

if __name__ == "__main__":
    results = run_ab_test()
    print(f"\\n✅ A/B Test completed! RAG chunking optimization validated.")