"""
Unit tests for Database Service
Target: 85%+ coverage for database operations
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError

from app.models.database import TrainingFile, DatabaseManager
from app.services.error_handler import DatabaseConnectionError, DatabaseQueryError


class TestDatabaseManager:
    """Test suite for Database Manager"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create database manager instance for testing"""
        manager = DatabaseManager()
        manager.engine = Mock()
        manager.session_factory = Mock()
        return manager
    
    @pytest.fixture
    def sample_training_file(self):
        """Sample training file data"""
        return TrainingFile(
            id="test-123",
            filename="test.txt",
            display_name="Test File",
            category="help_data",
            file_path="/data/test.txt",
            file_size=1024,
            status="ready"
        )
    
    # Test initialization
    async def test_init_db_success(self, db_manager):
        """Test successful database initialization"""
        mock_conn = AsyncMock()
        db_manager.engine.begin = AsyncMock(return_value=mock_conn.__aenter__())
        
        await db_manager.init_db()
        
        assert db_manager.is_initialized is True
        assert db_manager.connection_retries == 0
    
    async def test_init_db_with_retries(self, db_manager):
        """Test database initialization with retries"""
        # First two attempts fail, third succeeds
        mock_conn = AsyncMock()
        db_manager.engine.begin = AsyncMock(
            side_effect=[
                Exception("Connection failed"),
                Exception("Connection failed"),
                mock_conn.__aenter__()
            ]
        )
        
        with patch('asyncio.sleep'):  # Skip actual sleep in tests
            await db_manager.init_db()
        
        assert db_manager.is_initialized is True
        assert db_manager.engine.begin.call_count == 3
    
    async def test_init_db_max_retries_exceeded(self, db_manager):
        """Test database initialization fails after max retries"""
        db_manager.engine.begin = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('asyncio.sleep'):
            with pytest.raises(DatabaseConnectionError):
                await db_manager.init_db()
        
        assert db_manager.is_initialized is False
    
    # Test session management
    async def test_get_session_with_retry_success(self, db_manager):
        """Test successful session creation with retry"""
        mock_session = AsyncMock(spec=AsyncSession)
        db_manager.session_factory.return_value = mock_session
        
        async with db_manager.get_session_with_retry() as session:
            assert session == mock_session
            
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    async def test_get_session_with_retry_rollback_on_error(self, db_manager):
        """Test session rollback on error"""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit.side_effect = Exception("Commit failed")
        db_manager.session_factory.return_value = mock_session
        
        with pytest.raises(Exception):
            async with db_manager.get_session_with_retry() as session:
                pass
        
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()
    
    # Test performance tracking
    async def test_performance_tracking(self, db_manager):
        """Test performance metrics tracking"""
        mock_session = AsyncMock(spec=AsyncSession)
        db_manager.session_factory.return_value = mock_session
        
        # Execute multiple operations
        for _ in range(5):
            async with db_manager.get_session_with_retry() as session:
                pass
        
        assert db_manager.performance_stats["total_queries"] == 5
        assert db_manager.performance_stats["avg_response_time"] > 0
    
    async def test_failed_query_tracking(self, db_manager):
        """Test failed query tracking"""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit.side_effect = Exception("Query failed")
        db_manager.session_factory.return_value = mock_session
        
        try:
            async with db_manager.get_session_with_retry() as session:
                pass
        except:
            pass
        
        assert db_manager.performance_stats["failed_queries"] == 1
    
    # Test connection testing
    async def test_test_connection_success(self, db_manager):
        """Test successful connection test"""
        mock_conn = AsyncMock()
        db_manager.engine.begin = AsyncMock(return_value=mock_conn.__aenter__())
        
        result = await db_manager.test_connection()
        assert result is True
    
    async def test_test_connection_failure(self, db_manager):
        """Test failed connection test"""
        db_manager.engine.begin = AsyncMock(side_effect=Exception("Connection failed"))
        
        result = await db_manager.test_connection()
        assert result is False
    
    # Test health status
    async def test_get_health_status_healthy(self, db_manager):
        """Test health status when healthy"""
        mock_conn = AsyncMock()
        mock_result = Mock()
        mock_result.fetchall.return_value = [("training_files",), ("evaluation_metrics",)]
        
        db_manager.engine.begin = AsyncMock(return_value=mock_conn.__aenter__())
        mock_conn.__aenter__.return_value.execute = AsyncMock(return_value=mock_result)
        
        health = await db_manager.get_health_status()
        
        assert health["status"] == "healthy"
        assert health["connection"] is True
        assert health["tables_count"] == 2
        assert "training_files" in health["tables"]
    
    async def test_get_health_status_unhealthy(self, db_manager):
        """Test health status when unhealthy"""
        db_manager.engine.begin = AsyncMock(side_effect=Exception("DB Error"))
        
        health = await db_manager.get_health_status()
        
        assert health["status"] == "unhealthy"
        assert health["connection"] is False
        assert "error" in health
    
    # Test cleanup
    async def test_cleanup(self, db_manager):
        """Test database cleanup"""
        db_manager.engine.dispose = AsyncMock()
        
        await db_manager.cleanup()
        
        db_manager.engine.dispose.assert_called_once()
    
    async def test_cleanup_with_error(self, db_manager):
        """Test database cleanup with error handling"""
        db_manager.engine.dispose = AsyncMock(side_effect=Exception("Cleanup failed"))
        
        # Should not raise exception
        await db_manager.cleanup()
    
    # Test run in session helper
    async def test_run_in_session_async_function(self, db_manager):
        """Test running async function in session"""
        mock_session = AsyncMock(spec=AsyncSession)
        db_manager.session_factory.return_value = mock_session
        
        async def test_func(session, value):
            return value * 2
        
        result = await db_manager._run_in_session(test_func, 5)
        assert result == 10
    
    async def test_run_in_session_sync_function(self, db_manager):
        """Test running sync function in session"""
        mock_session = AsyncMock(spec=AsyncSession)
        db_manager.session_factory.return_value = mock_session
        
        def test_func(session, value):
            return value * 2
        
        result = await db_manager._run_in_session(test_func, 5)
        assert result == 10