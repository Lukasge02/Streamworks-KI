"""
LlamaIndex Integration Tests

Tests for the new LlamaIndex RAG pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLlamaIndexSettings:
    """Test LlamaIndex configuration"""
    
    def test_settings_configuration(self):
        """Test that settings are properly configured"""
        from services.llamaindex.settings import LlamaIndexSettings
        
        assert LlamaIndexSettings.LLM_MODEL == "gpt-4o-mini"
        assert LlamaIndexSettings.EMBEDDING_MODEL == "text-embedding-3-small"
        assert LlamaIndexSettings.EMBEDDING_DIMENSION == 1536
        assert LlamaIndexSettings.CHUNK_SIZE == 1024
        assert LlamaIndexSettings.CHUNK_OVERLAP == 200
    
    def test_configure_llamaindex(self):
        """Test LlamaIndex global configuration"""
        from services.llamaindex.settings import configure_llamaindex
        
        # Should not raise
        configure_llamaindex()
        
        from llama_index.core import Settings
        assert Settings.llm is not None
        assert Settings.embed_model is not None


class TestChatService:
    """Test ChatService functionality"""
    
    def test_chat_service_initialization(self):
        """Test ChatService initializes correctly"""
        from services.llamaindex.chat_service import get_chat_service
        
        service = get_chat_service()
        assert service is not None
        
        stats = service.get_stats()
        assert stats["ready"] == True
        assert stats["framework"] == "LlamaIndex"
        assert "model" in stats
    
    def test_chat_simple_returns_correct_format(self):
        """Test chat_simple returns API-compatible format"""
        from services.llamaindex.chat_service import ChatService
        from services.llamaindex.query_service import QueryResult
        
        service = ChatService()
        
        # Mock the internal query service method
        with patch.object(service, '_query_service') as mock_query:
            mock_query.query.return_value = QueryResult(
                answer="Test answer",
                sources=[{"doc_id": "123", "filename": "test.pdf", "content": "...", "score": 0.9}],
                has_context=True,
                chunks_found=1,
                confidence=0.85,
                confidence_level="high",
                query_type="general",
                warnings=[],
            )
            
            # Force using the mock
            service._query_service = mock_query
            
            result = service.chat_simple("Test query")
            
            # Verify API-compatible format
            assert "answer" in result
            assert "sources" in result
            assert "has_context" in result
            assert "chunks_found" in result
            assert "confidence" in result
            assert "confidence_level" in result
            assert "query_type" in result


class TestQueryService:
    """Test QueryService functionality"""
    
    def test_query_service_initialization(self):
        """Test QueryService initializes correctly"""
        from services.llamaindex.query_service import get_query_service
        
        service = get_query_service()
        assert service is not None
    
    def test_query_type_classification(self):
        """Test query type classification"""
        from services.llamaindex.query_service import QueryService
        
        service = QueryService()
        
        assert service._classify_query("Wie konfiguriere ich X?") == "how_to"
        assert service._classify_query("Welche Parameter gibt es?") == "configuration"
        assert service._classify_query("Fehler beim Start") == "troubleshooting"
        assert service._classify_query("Was ist StreamWorks?") == "explanation"
        assert service._classify_query("Hallo") == "general"


class TestIngestionService:
    """Test IngestionService functionality"""
    
    def test_ingestion_service_initialization(self):
        """Test IngestionService initializes correctly"""
        from services.llamaindex.ingestion_service import get_ingestion_service
        
        service = get_ingestion_service()
        assert service is not None
    
    def test_supported_types(self):
        """Test supported file types"""
        from services.llamaindex.ingestion_service import get_ingestion_service
        
        service = get_ingestion_service()
        types = service.get_supported_types()
        
        assert "pdf" in types
        assert "docx" in types
        assert "txt" in types
    
    def test_metadata_extraction(self):
        """Test metadata extraction from filename"""
        from services.llamaindex.ingestion_service import IngestionService
        
        service = IngestionService()
        
        # Version extraction
        assert service._extract_version("doc_v2.0.pdf", "") == "2.0"
        assert service._extract_version("Version_1.5.docx", "") == "1.5"
        
        # Year extraction
        assert service._extract_year("report_2024.pdf") == 2024
        assert service._extract_year("old_doc.pdf") is None
        
        # Category extraction
        assert service._extract_category("IT_Guide.pdf") == "IT"
        assert service._extract_category("HR_Policy.docx") == "HR"
        assert service._extract_category("random.pdf") is None


class TestIndexService:
    """Test IndexService functionality"""
    
    def test_index_service_initialization(self):
        """Test IndexService initializes correctly"""
        from services.llamaindex.index_service import get_index_service
        
        service = get_index_service()
        assert service is not None
    
    def test_index_stats(self):
        """Test index statistics"""
        from services.llamaindex.index_service import get_index_service
        
        service = get_index_service()
        stats = service.get_stats()
        
        assert "collection" in stats
        assert stats["collection"] == "streamworks_documents"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
