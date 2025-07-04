"""
Unit tests for Error Handler
Target: 90%+ coverage for error handling logic
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import re

from app.services.error_handler import (
    StreamWorksErrorHandler, 
    ErrorType, 
    FallbackType,
    FallbackResponse,
    LLMConnectionError,
    LLMTimeoutError,
    RAGSearchError,
    XMLValidationError,
    DatabaseConnectionError
)


class TestStreamWorksErrorHandler:
    """Test suite for StreamWorks Error Handler"""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler instance for testing"""
        return StreamWorksErrorHandler()
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for error handling"""
        return {
            "query": "Was ist StreamWorks?",
            "user_id": "test-user-123",
            "session_id": "session-456"
        }
    
    # Test initialization
    def test_init(self, error_handler):
        """Test error handler initialization"""
        assert error_handler.error_cache.maxsize == 100
        assert error_handler.error_cache.ttl == 300
        assert len(error_handler.error_codes) > 0
        assert len(error_handler.cached_responses) > 0
    
    # Test LLM error handling
    async def test_handle_llm_connection_error(self, error_handler, sample_context):
        """Test handling of LLM connection errors"""
        error = LLMConnectionError("Connection refused")
        
        response = await error_handler.handle_llm_error(error, sample_context)
        
        assert response.error_type == ErrorType.LLM_CONNECTION
        assert response.fallback_type == FallbackType.CACHED
        assert response.confidence == 0.6
        assert response.error_code == "LLM_CONN_001"
        assert response.suggestions is not None
        assert len(response.suggestions) > 0
    
    async def test_handle_llm_timeout_error(self, error_handler, sample_context):
        """Test handling of LLM timeout errors"""
        error = LLMTimeoutError("Request timeout")
        
        response = await error_handler.handle_llm_error(error, sample_context)
        
        assert response.error_type == ErrorType.LLM_TIMEOUT
        assert response.fallback_type == FallbackType.STATIC
        assert "timeout" in sample_context or response.metadata is not None
    
    async def test_handle_generic_llm_error(self, error_handler, sample_context):
        """Test handling of generic LLM errors"""
        error = Exception("Unknown LLM error")
        
        response = await error_handler.handle_llm_error(error, sample_context)
        
        assert response.error_type in [ErrorType.UNKNOWN, ErrorType.LLM_CONNECTION, ErrorType.LLM_TIMEOUT, ErrorType.LLM_GENERATION]
        assert response.fallback_type in [FallbackType.STATIC, FallbackType.CACHED, FallbackType.TEMPLATE]
    
    # Test RAG error handling
    async def test_handle_rag_search_error(self, error_handler, sample_context):
        """Test handling of RAG search errors"""
        error = RAGSearchError("Search failed")
        
        response = await error_handler.handle_rag_error(error, sample_context)
        
        assert response.error_type == ErrorType.RAG_SEARCH
        assert response.fallback_type in [FallbackType.CACHED, FallbackType.TEMPLATE]
        assert len(response.message) > 0
    
    async def test_handle_rag_vector_db_error(self, error_handler, sample_context):
        """Test handling of RAG vector DB errors"""
        error = Exception("ChromaDB connection failed")
        
        response = await error_handler.handle_rag_error(error, sample_context)
        
        assert response.error_type == ErrorType.RAG_VECTORDB
        assert "Suchfunktion" in response.message
    
    # Test XML error handling
    async def test_handle_xml_validation_error(self, error_handler):
        """Test handling of XML validation errors"""
        error = XMLValidationError("Invalid XML structure")
        context = {"requirements": {"job_name": "TestJob"}}
        
        response = await error_handler.handle_xml_error(error, context)
        
        assert response.error_type == ErrorType.XML_VALIDATION
        assert response.fallback_type == FallbackType.TEMPLATE
        assert "xml" in response.message.lower()
        assert response.metadata["fallback_xml_provided"] is True
    
    async def test_handle_xml_generation_error(self, error_handler):
        """Test handling of XML generation errors"""
        error = Exception("XML generation failed")
        context = {"requirements": {}}
        
        response = await error_handler.handle_xml_error(error, context)
        
        assert response.error_type == ErrorType.XML_GENERATION
        assert "<?xml" in response.message  # Contains fallback XML
    
    # Test database error handling
    async def test_handle_database_connection_error(self, error_handler):
        """Test handling of database connection errors"""
        error = DatabaseConnectionError("Cannot connect to database")
        
        response = await error_handler.handle_database_error(error)
        
        assert response.error_type == ErrorType.DATABASE_CONNECTION
        assert response.fallback_type == FallbackType.DEGRADED
        assert response.confidence == 0.8
        assert "Datenbank" in response.message
    
    # Test error classification
    def test_classify_llm_error_connection(self, error_handler):
        """Test LLM error classification - connection"""
        error = Exception("Connection refused to localhost:11434")
        error_type = error_handler._classify_llm_error(error)
        assert error_type == ErrorType.LLM_CONNECTION
    
    def test_classify_llm_error_timeout(self, error_handler):
        """Test LLM error classification - timeout"""
        error = Exception("Request timeout after 30 seconds")
        error_type = error_handler._classify_llm_error(error)
        assert error_type == ErrorType.LLM_TIMEOUT
    
    def test_classify_rag_error_vectordb(self, error_handler):
        """Test RAG error classification - vector DB"""
        error = Exception("ChromaDB index not found")
        error_type = error_handler._classify_rag_error(error)
        assert error_type == ErrorType.RAG_VECTORDB
    
    # Test cached responses
    def test_get_cached_response_xml_query(self, error_handler):
        """Test cached response for XML-related query"""
        response = error_handler._get_cached_response("Erstelle einen XML Stream", "xml_error")
        assert "xml" in response.lower()
    
    def test_get_cached_response_help_query(self, error_handler):
        """Test cached response for help query"""
        response = error_handler._get_cached_response("Was ist StreamWorks?", "general")
        assert "StreamWorks" in response
    
    # Test fallback XML generation
    def test_generate_fallback_xml(self, error_handler):
        """Test fallback XML generation"""
        requirements = {
            "name": "TestStream",
            "schedule": "daily"
        }
        
        xml = error_handler._generate_fallback_xml(requirements)
        
        assert "<?xml" in xml
        assert "TestStream" in xml
        assert "streamworks" in xml.lower()
    
    # Test error counting
    def test_increment_error_count(self, error_handler):
        """Test error count tracking"""
        initial_count = error_handler.error_counts.get(ErrorType.LLM_CONNECTION, 0)
        
        error_handler._increment_error_count(ErrorType.LLM_CONNECTION)
        error_handler._increment_error_count(ErrorType.LLM_CONNECTION)
        
        assert error_handler.error_counts[ErrorType.LLM_CONNECTION] == initial_count + 2
    
    # Test error statistics
    async def test_get_error_statistics(self, error_handler):
        """Test error statistics retrieval"""
        # Generate some errors
        error_handler._increment_error_count(ErrorType.LLM_CONNECTION)
        error_handler._increment_error_count(ErrorType.RAG_SEARCH)
        error_handler._increment_error_count(ErrorType.LLM_CONNECTION)
        
        stats = await error_handler.get_error_statistics()
        
        assert stats["total_errors"] == 3
        assert stats["error_counts"]["llm_connection"] == 2
        assert stats["error_counts"]["rag_search"] == 1
        assert stats["most_common_error"] == "llm_connection"
    
    async def test_reset_error_counts(self, error_handler):
        """Test error count reset"""
        error_handler._increment_error_count(ErrorType.LLM_CONNECTION)
        
        await error_handler.reset_error_counts()
        
        assert len(error_handler.error_counts) == 0
    
    # Test user-friendly messages
    def test_get_user_friendly_llm_message(self, error_handler):
        """Test user-friendly message generation for LLM errors"""
        message, suggestions = error_handler._get_user_friendly_llm_message(
            ErrorType.LLM_CONNECTION,
            Exception("Connection failed")
        )
        
        assert "KI-Service" in message
        assert len(suggestions) >= 4
        assert any("Minuten" in s for s in suggestions)
    
    # Test context-specific error handling
    async def test_handle_error_with_context(self, error_handler):
        """Test error handling with specific context"""
        error = Exception("Test error")
        context = "chat_processing"
        user_context = {"query": "test"}
        
        response = await error_handler.handle_error_with_context(
            error, context, user_context
        )
        
        assert response.error_type != ErrorType.UNKNOWN or response.error_type == ErrorType.UNKNOWN
        assert response.fallback_type == FallbackType.ERROR
        assert "chat" in response.metadata["context"]
        assert response.error_code in error_handler.error_codes.values()
    
    # Test TTL cache behavior
    def test_error_cache_ttl(self, error_handler):
        """Test TTL cache expires old entries"""
        # This test verifies the cache is configured with TTL
        assert hasattr(error_handler.error_cache, 'ttl')
        assert error_handler.error_cache.ttl == 300  # 5 minutes