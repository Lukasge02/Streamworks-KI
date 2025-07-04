"""
Unit tests for RAG Service
Target: 95%+ coverage for core functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
from typing import List

from app.services.rag_service import RAGService
from app.services.error_handler import RAGSearchError, RAGEmbeddingError


class TestRAGService:
    """Test suite for RAG Service with comprehensive coverage"""
    
    @pytest.fixture
    async def rag_service(self):
        """Create RAG service instance for testing"""
        service = RAGService()
        # Mock ChromaDB client
        service.client = Mock()
        service.collection = Mock()
        return service
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "id": "doc1",
                "content": "StreamWorks ist eine Plattform für Workflow-Automatisierung.",
                "metadata": {"source": "help.txt", "category": "intro"}
            },
            {
                "id": "doc2", 
                "content": "Batch-Jobs können täglich, wöchentlich oder monatlich ausgeführt werden.",
                "metadata": {"source": "batch.txt", "category": "batch"}
            }
        ]
    
    # Test initialization
    async def test_init_success(self):
        """Test successful RAG service initialization"""
        with patch('app.services.rag_service.chromadb.PersistentClient') as mock_client:
            service = RAGService()
            assert service.client is not None
            assert service.collection_name == "streamworks_docs"
            mock_client.assert_called_once()
    
    async def test_init_with_error_handling(self):
        """Test initialization with error handling"""
        with patch('app.services.rag_service.chromadb.PersistentClient', side_effect=Exception("DB Error")):
            with patch('app.services.rag_service.logger') as mock_logger:
                service = RAGService()
                mock_logger.error.assert_called()
    
    # Test document operations
    async def test_add_documents_success(self, rag_service, sample_documents):
        """Test successful document addition"""
        rag_service.collection.add = Mock()
        
        result = await rag_service.add_documents(
            documents=[doc["content"] for doc in sample_documents],
            metadatas=[doc["metadata"] for doc in sample_documents],
            ids=[doc["id"] for doc in sample_documents]
        )
        
        assert result == ["doc1", "doc2"]
        rag_service.collection.add.assert_called_once()
    
    async def test_add_documents_with_embedding_cache(self, rag_service):
        """Test document addition with embedding cache"""
        doc_content = "Test document"
        doc_id = "test_id"
        
        # First call - should compute embedding
        with patch.object(rag_service, '_compute_embeddings', return_value=[[0.1, 0.2, 0.3]]):
            await rag_service.add_documents([doc_content], [{"source": "test"}], [doc_id])
            assert doc_content in rag_service.embedding_cache
        
        # Second call - should use cache
        with patch.object(rag_service, '_compute_embeddings') as mock_compute:
            await rag_service.add_documents([doc_content], [{"source": "test"}], ["new_id"])
            mock_compute.assert_not_called()
    
    async def test_search_documents_with_results(self, rag_service):
        """Test document search with results"""
        mock_results = {
            'documents': [["StreamWorks documentation"]],
            'metadatas': [[{"source": "help.txt"}]],
            'distances': [[0.1]]
        }
        rag_service.collection.query = Mock(return_value=mock_results)
        
        results = await rag_service.search_documents("StreamWorks", k=1)
        
        assert len(results) == 1
        assert results[0].page_content == "StreamWorks documentation"
        assert results[0].metadata["source"] == "help.txt"
    
    async def test_search_documents_no_results(self, rag_service):
        """Test document search with no results"""
        mock_results = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        rag_service.collection.query = Mock(return_value=mock_results)
        
        results = await rag_service.search_documents("NonExistent", k=5)
        
        assert len(results) == 0
    
    async def test_search_with_query_cache(self, rag_service):
        """Test search with query caching"""
        query = "test query"
        mock_results = {
            'documents': [["Cached result"]],
            'metadatas': [[{"source": "cache.txt"}]],
            'distances': [[0.1]]
        }
        rag_service.collection.query = Mock(return_value=mock_results)
        
        # First search - should query collection
        results1 = await rag_service.search_documents(query)
        assert query in rag_service.query_cache
        
        # Second search - should use cache
        results2 = await rag_service.search_documents(query)
        assert results1 == results2
        rag_service.collection.query.assert_called_once()  # Only called once
    
    # Test error handling
    async def test_search_with_rag_search_error(self, rag_service):
        """Test search with RAG search error"""
        rag_service.collection.query = Mock(side_effect=Exception("Search failed"))
        
        with pytest.raises(RAGSearchError):
            await rag_service.search_documents("test")
    
    async def test_add_documents_with_embedding_error(self, rag_service):
        """Test document addition with embedding error"""
        with patch.object(rag_service, '_compute_embeddings', side_effect=Exception("Embedding failed")):
            with pytest.raises(RAGEmbeddingError):
                await rag_service.add_documents(["test"], [{}], ["id1"])
    
    # Test performance
    async def test_search_performance(self, rag_service, performance_tracker):
        """Test search performance is under 2 seconds"""
        mock_results = {
            'documents': [["Result " * 100]],  # Large result
            'metadatas': [[{"source": "test.txt"}]],
            'distances': [[0.1]]
        }
        rag_service.collection.query = Mock(return_value=mock_results)
        
        performance_tracker.start("search")
        await rag_service.search_documents("test")
        performance_tracker.end("search")
        
        performance_tracker.assert_performance("search", 2.0)
    
    # Test health check
    async def test_get_health_status(self, rag_service):
        """Test health status reporting"""
        rag_service.collection.count = Mock(return_value=100)
        
        health = await rag_service.get_health()
        
        assert health["status"] == "healthy"
        assert health["documents_count"] == 100
        assert "performance" in health
        assert health["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
    
    # Test batch operations
    async def test_batch_add_documents(self, rag_service):
        """Test batch document addition"""
        documents = [f"Document {i}" for i in range(100)]
        metadatas = [{"source": f"doc{i}.txt"} for i in range(100)]
        ids = [f"doc{i}" for i in range(100)]
        
        result = await rag_service.add_documents(documents, metadatas, ids)
        
        assert len(result) == 100
        rag_service.collection.add.assert_called()
    
    # Test cache management
    async def test_clear_caches(self, rag_service):
        """Test cache clearing"""
        # Add items to caches
        rag_service.query_cache["test"] = "cached"
        rag_service.document_cache["doc"] = "cached"
        rag_service.embedding_cache["embed"] = [0.1, 0.2]
        
        rag_service.clear_caches()
        
        assert len(rag_service.query_cache) == 0
        assert len(rag_service.document_cache) == 0
        assert len(rag_service.embedding_cache) == 0
    
    # Test metadata handling
    async def test_enhanced_metadata_processing(self, rag_service):
        """Test enhanced metadata processing"""
        content = "Test content"
        metadata = {"source": "test.txt"}
        
        enhanced = rag_service._enhance_metadata(metadata)
        
        assert "indexed_at" in enhanced
        assert enhanced["source"] == "test.txt"
        assert "chunk_size" in enhanced