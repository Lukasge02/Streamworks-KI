#!/usr/bin/env python3
"""
Test script for the Multi-Source Citation System
Tests Citation Service, RAG with Citations, and API endpoints
"""
import asyncio
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.citation_service import CitationService
from app.services.rag_service import RAGService
from app.models.schemas import SourceType, DocumentType
from langchain.schema import Document


async def test_citation_service():
    """Test the Citation Service functionality"""
    print("🧪 Testing Citation Service...")
    
    citation_service = CitationService()
    
    # Test documents with metadata
    test_documents = [
        Document(
            page_content="StreamWorks ist eine Plattform für Datenverarbeitung. Jobs können über das Portal erstellt werden.",
            metadata={
                "source": "streamworks_faq.txt",
                "score": 0.85,
                "chunk_id": "chunk_001"
            }
        ),
        Document(
            page_content="Batch-Jobs werden täglich um 2 Uhr ausgeführt. Die Konfiguration erfolgt über XML-Dateien.",
            metadata={
                "source": "training_data_01.txt",
                "score": 0.72,
                "chunk_id": "chunk_002"
            }
        ),
        Document(
            page_content="PowerShell-Integration ermöglicht automatisierte Workflows. Skripte können direkt ausgeführt werden.",
            metadata={
                "source": "powershell_streamworks.txt",
                "score": 0.68,
                "chunk_id": "chunk_003"
            }
        )
    ]
    
    # Test citation creation
    query = "Wie erstelle ich einen StreamWorks Job?"
    citations = await citation_service.create_citations_from_documents(test_documents, query)
    
    print(f"✅ Created {len(citations)} citations")
    
    for i, citation in enumerate(citations, 1):
        print(f"   {i}. {citation.source_title} ({citation.source_type.value}) - Relevanz: {citation.relevance_score:.2f}")
    
    # Test citation summary
    summary = citation_service.create_citation_summary(citations)
    print(f"📊 Citation Summary:")
    print(f"   Total: {summary.total_citations}")
    print(f"   Highest relevance: {summary.highest_relevance:.2f}")
    print(f"   Coverage score: {summary.coverage_score:.2f}")
    print(f"   Source breakdown: {summary.source_breakdown}")
    
    # Test citation formatting
    citation_text = citation_service.format_citations_for_response(citations)
    print(f"📝 Formatted citations:\n{citation_text}")
    
    return True


async def test_rag_with_citations():
    """Test RAG Service with citation support"""
    print("\n🧪 Testing RAG with Citations...")
    
    try:
        rag_service = RAGService()
        
        # Test citation-enhanced search
        test_query = "Wie konfiguriere ich einen Batch-Job?"
        
        result = await rag_service.search_documents_with_citations(
            query=test_query,
            top_k=3,
            include_citations=True
        )
        
        documents = result["documents"]
        citations = result["citations"]
        citation_summary = result["citation_summary"]
        
        print(f"✅ RAG Citation Search Results:")
        print(f"   Documents found: {len(documents)}")
        print(f"   Citations generated: {len(citations)}")
        
        if citation_summary:
            print(f"   Coverage score: {citation_summary.coverage_score:.2f}")
            print(f"   Source breakdown: {citation_summary.source_breakdown}")
        
        if citations:
            print(f"📚 Top citations:")
            for i, citation in enumerate(citations[:3], 1):
                print(f"   {i}. {citation.source_title} (Relevanz: {citation.relevance_score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Citation test failed: {e}")
        return False


async def test_citation_metadata_extraction():
    """Test citation metadata extraction logic"""
    print("\n🧪 Testing Citation Metadata Extraction...")
    
    citation_service = CitationService()
    
    test_files = [
        ("streamworks_faq.txt", "F: Wie erstelle ich einen Stream?\nA: Über das Portal..."),
        ("csv_verarbeitung_tipps.txt", "CSV-Verarbeitung Tipps\n\nSchritt 1: Daten laden..."),
        ("training_data_05.txt", "StreamWorks Batch-Jobs\n\nBatch-Jobs ermöglichen..."),
        ("powershell_streamworks.txt", "PowerShell Integration\n\nDieser Guide zeigt...")
    ]
    
    for filename, content in test_files:
        source_type = citation_service._determine_source_type(filename)
        doc_type = citation_service._determine_document_type(filename, content)
        title = citation_service._extract_source_title(filename, content)
        
        print(f"📄 {filename}:")
        print(f"   Source Type: {source_type.value}")
        print(f"   Document Type: {doc_type.value}")
        print(f"   Title: {title}")
    
    return True


async def test_citation_api_format():
    """Test citation API response format"""
    print("\n🧪 Testing Citation API Format...")
    
    # Simulate API response structure
    from app.models.schemas import ChatResponseWithCitations, Citation, CitationSummary
    from datetime import datetime
    
    sample_citations = [
        Citation(
            source_type=SourceType.FAQ,
            source_title="StreamWorks FAQ",
            document_type=DocumentType.FAQ,
            filename="streamworks_faq.txt",
            relevance_score=0.85,
            page_content="Beispielinhalt für FAQ...",
            tags=["FAQ", "StreamWorks"]
        ),
        Citation(
            source_type=SourceType.STREAMWORKS,
            source_title="Batch-Jobs Anleitung",
            document_type=DocumentType.GUIDE,
            filename="batch_anleitung.txt",
            relevance_score=0.72,
            page_content="Batch-Jobs können...",
            tags=["Batch", "Guide"]
        )
    ]
    
    citation_summary = CitationSummary(
        total_citations=2,
        source_breakdown={"FAQ": 1, "StreamWorks": 1},
        highest_relevance=0.85,
        coverage_score=0.75
    )
    
    response = ChatResponseWithCitations(
        response="Hier ist die Antwort mit Quellenangaben...",
        citations=sample_citations,
        citation_summary=citation_summary,
        conversation_id="test-123",
        timestamp=datetime.now(),
        response_quality=0.8
    )
    
    # Test JSON serialization
    try:
        response_json = response.model_dump()
        print(f"✅ API Response Format Test:")
        print(f"   Response length: {len(response.response)} chars")
        print(f"   Citations count: {len(response.citations)}")
        print(f"   Coverage score: {response.citation_summary.coverage_score}")
        print(f"   JSON serializable: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ API format test failed: {e}")
        return False


async def run_all_tests():
    """Run all citation system tests"""
    print("🚀 Running Citation System Tests")
    print("=" * 50)
    
    tests = [
        ("Citation Service", test_citation_service),
        ("RAG with Citations", test_rag_with_citations),
        ("Metadata Extraction", test_citation_metadata_extraction),
        ("API Format", test_citation_api_format)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name}...")
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All citation system tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)