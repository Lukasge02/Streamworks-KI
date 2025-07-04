"""
Unit tests for Citation Service
Tests multi-source citation functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock
from langchain.schema import Document

from app.services.citation_service import CitationService
from app.models.schemas import SourceType, DocumentType, Citation, CitationSummary


class TestCitationService:
    """Test suite for Citation Service"""
    
    @pytest.fixture
    def citation_service(self):
        """Create citation service instance"""
        return CitationService()
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            Document(
                page_content="StreamWorks FAQ: Wie erstelle ich einen neuen Stream? Antwort: Über das Portal.",
                metadata={
                    "source": "streamworks_faq.txt",
                    "score": 0.85,
                    "chunk_id": "chunk_001"
                }
            ),
            Document(
                page_content="Batch-Jobs Anleitung: Jobs werden täglich um 2 Uhr ausgeführt.",
                metadata={
                    "source": "training_data_01.txt",
                    "score": 0.72,
                    "chunk_id": "chunk_002"
                }
            ),
            Document(
                page_content="PowerShell Integration für StreamWorks ermöglicht Automatisierung.",
                metadata={
                    "source": "powershell_streamworks.txt",
                    "score": 0.68,
                    "chunk_id": "chunk_003"
                }
            )
        ]
    
    # Test source type determination
    def test_determine_source_type_faq(self, citation_service):
        """Test source type detection for FAQ"""
        result = citation_service._determine_source_type("streamworks_faq.txt")
        assert result == SourceType.FAQ
    
    def test_determine_source_type_streamworks(self, citation_service):
        """Test source type detection for StreamWorks"""
        result = citation_service._determine_source_type("streamworks_batch_hilfe.txt")
        assert result == SourceType.STREAMWORKS
    
    def test_determine_source_type_training(self, citation_service):
        """Test source type detection for training data"""
        result = citation_service._determine_source_type("training_data_05.txt")
        assert result == SourceType.DOCUMENTATION
    
    def test_determine_source_type_unknown(self, citation_service):
        """Test source type detection for unknown files"""
        result = citation_service._determine_source_type("unknown_file.txt")
        assert result == SourceType.DOCUMENTATION  # Default fallback
    
    # Test document type determination
    def test_determine_document_type_faq_filename(self, citation_service):
        """Test document type detection from filename"""
        result = citation_service._determine_document_type("streamworks_faq.txt")
        assert result == DocumentType.FAQ
    
    def test_determine_document_type_faq_content(self, citation_service):
        """Test document type detection from content"""
        content = "F: Wie mache ich das?\nA: So geht es..."
        result = citation_service._determine_document_type("test.txt", content)
        assert result == DocumentType.FAQ
    
    def test_determine_document_type_guide_content(self, citation_service):
        """Test document type detection for guides"""
        content = "Schritt 1: Öffnen Sie das Portal\nSchritt 2: Klicken Sie auf..."
        result = citation_service._determine_document_type("anleitung.txt", content)
        assert result == DocumentType.GUIDE
    
    def test_determine_document_type_troubleshooting(self, citation_service):
        """Test document type detection for troubleshooting"""
        content = "Fehler: Connection timeout\nLösung: Überprüfen Sie..."
        result = citation_service._determine_document_type("hilfe.txt", content)
        assert result == DocumentType.TROUBLESHOOTING
    
    # Test title extraction
    def test_extract_source_title_from_content(self, citation_service):
        """Test title extraction from content"""
        content = "StreamWorks FAQ - Häufig gestellte Fragen\n\nF: Was ist..."
        result = citation_service._extract_source_title("test.txt", content)
        assert "StreamWorks FAQ" in result
    
    def test_extract_source_title_from_filename(self, citation_service):
        """Test title extraction from filename"""
        result = citation_service._extract_source_title("csv_verarbeitung_tipps.txt", "")
        assert "Csv Verarbeitung Tipps" in result
    
    # Test relevance scoring
    def test_calculate_relevance_score_with_metadata(self, citation_service):
        """Test relevance calculation with metadata score"""
        doc = Document(
            page_content="Test content",
            metadata={"score": 0.85}
        )
        result = citation_service._calculate_relevance_score(doc, "test query")
        assert result == 0.85
    
    def test_calculate_relevance_score_word_overlap(self, citation_service):
        """Test relevance calculation with word overlap"""
        doc = Document(page_content="StreamWorks batch job processing")
        query = "StreamWorks job"
        result = citation_service._calculate_relevance_score(doc, query)
        assert result > 0.0  # Should have some overlap
    
    def test_calculate_relevance_score_no_overlap(self, citation_service):
        """Test relevance calculation with no overlap"""
        doc = Document(page_content="Completely different content")
        query = "StreamWorks job"
        result = citation_service._calculate_relevance_score(doc, query)
        assert result == 0.0
    
    # Test citation creation
    @pytest.mark.asyncio
    async def test_create_citations_from_documents(self, citation_service, sample_documents):
        """Test creating citations from documents"""
        query = "Wie erstelle ich einen StreamWorks Job?"
        citations = await citation_service.create_citations_from_documents(sample_documents, query)
        
        assert len(citations) == 3
        assert all(isinstance(c, Citation) for c in citations)
        
        # Check that citations are sorted by relevance
        relevance_scores = [c.relevance_score for c in citations]
        assert relevance_scores == sorted(relevance_scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_create_citations_empty_documents(self, citation_service):
        """Test creating citations from empty document list"""
        citations = await citation_service.create_citations_from_documents([], "test query")
        assert citations == []
    
    @pytest.mark.asyncio
    async def test_create_citations_with_invalid_document(self, citation_service):
        """Test creating citations with invalid document"""
        invalid_doc = Document(page_content="Test", metadata=None)
        citations = await citation_service.create_citations_from_documents([invalid_doc], "test")
        
        # Should handle gracefully
        assert len(citations) <= 1  # May create citation with defaults or skip
    
    # Test citation summary
    def test_create_citation_summary_empty(self, citation_service):
        """Test creating summary from empty citations"""
        summary = citation_service.create_citation_summary([])
        
        assert summary.total_citations == 0
        assert summary.source_breakdown == {}
        assert summary.highest_relevance == 0.0
        assert summary.coverage_score == 0.0
    
    def test_create_citation_summary_with_citations(self, citation_service):
        """Test creating summary from citations"""
        citations = [
            Citation(
                source_type=SourceType.FAQ,
                source_title="Test FAQ",
                document_type=DocumentType.FAQ,
                filename="faq.txt",
                relevance_score=0.9,
                page_content="content"
            ),
            Citation(
                source_type=SourceType.STREAMWORKS,
                source_title="Test Guide",
                document_type=DocumentType.GUIDE,
                filename="guide.txt",
                relevance_score=0.7,
                page_content="content"
            )
        ]
        
        summary = citation_service.create_citation_summary(citations)
        
        assert summary.total_citations == 2
        assert summary.source_breakdown["FAQ"] == 1
        assert summary.source_breakdown["StreamWorks"] == 1
        assert summary.highest_relevance == 0.9
        assert summary.coverage_score > 0.0
    
    # Test citation formatting
    def test_format_citations_for_response_empty(self, citation_service):
        """Test formatting empty citations"""
        result = citation_service.format_citations_for_response([])
        assert result == ""
    
    def test_format_citations_for_response_with_citations(self, citation_service):
        """Test formatting citations for response"""
        citations = [
            Citation(
                source_type=SourceType.FAQ,
                source_title="StreamWorks FAQ",
                document_type=DocumentType.FAQ,
                filename="faq.txt",
                relevance_score=0.9,
                page_content="content"
            )
        ]
        
        result = citation_service.format_citations_for_response(citations)
        
        assert "Quellen:" in result
        assert "StreamWorks FAQ" in result
        assert "FAQ" in result
        assert "90.0%" in result  # Relevance percentage
    
    def test_format_citations_max_limit(self, citation_service):
        """Test formatting citations with max limit"""
        citations = [
            Citation(
                source_type=SourceType.FAQ,
                source_title=f"Source {i}",
                document_type=DocumentType.FAQ,
                filename=f"file{i}.txt",
                relevance_score=0.8,
                page_content="content"
            ) for i in range(5)
        ]
        
        result = citation_service.format_citations_for_response(citations, max_citations=2)
        
        # Should only include 2 citations
        citation_lines = [line for line in result.split('\n') if line.strip() and line[0].isdigit()]
        assert len(citation_lines) <= 2
    
    # Test document enhancement
    def test_enhance_documents_with_metadata(self, citation_service, sample_documents):
        """Test enhancing documents with citation metadata"""
        enhanced_docs = citation_service.enhance_documents_with_metadata(sample_documents)
        
        assert len(enhanced_docs) == len(sample_documents)
        
        for doc in enhanced_docs:
            assert 'citation_source_type' in doc.metadata
            assert 'citation_document_type' in doc.metadata
            assert 'citation_title' in doc.metadata
    
    def test_enhance_documents_preserves_original_metadata(self, citation_service):
        """Test that document enhancement preserves original metadata"""
        original_doc = Document(
            page_content="Test content",
            metadata={"original_field": "original_value", "score": 0.8}
        )
        
        enhanced_docs = citation_service.enhance_documents_with_metadata([original_doc])
        enhanced_doc = enhanced_docs[0]
        
        # Original metadata should be preserved
        assert enhanced_doc.metadata["original_field"] == "original_value"
        assert enhanced_doc.metadata["score"] == 0.8
        
        # New citation metadata should be added
        assert 'citation_source_type' in enhanced_doc.metadata