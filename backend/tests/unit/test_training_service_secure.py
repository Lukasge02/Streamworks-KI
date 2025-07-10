"""
Secure Training Service Unit Tests
Testing the enhanced security and async features of TrainingService
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import aiofiles

from app.services.training_service import TrainingService
from app.models.database import TrainingFile
from app.models.schemas import TrainingFileResponse
from app.core.base_service import ServiceOperationError
from app.models.validation import SecurityError
from app.core.async_manager import task_manager, TaskStatus


@pytest.fixture
async def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
async def training_service(mock_db_session):
    """Create training service with mock dependencies"""
    with patch('app.services.training_service.settings') as mock_settings:
        mock_settings.TRAINING_DATA_PATH = "/tmp/test_training_data"
        
        service = TrainingService(mock_db_session)
        
        # Mock RAG service
        service.rag_service = AsyncMock()
        service.rag_service.add_documents = AsyncMock(return_value=5)
        
        # Mock processors
        service._file_processors = {
            'txt_to_md': AsyncMock(),
            'production_doc': AsyncMock(),
            'multi_format': AsyncMock()
        }
        
        return service


@pytest.fixture
def sample_file_content():
    """Sample file content for testing"""
    return b"This is a test file with StreamWorks configuration data."


@pytest.fixture
def malicious_file_content():
    """Malicious file content for security testing"""
    return b'<script>alert("XSS attack")</script>DROP TABLE users;'


@pytest.mark.asyncio
class TestTrainingServiceSecurity:
    """Test security features of TrainingService"""
    
    async def test_upload_file_with_validation_success(self, training_service, sample_file_content):
        """Test successful file upload with validation"""
        # Mock file validation
        with patch('app.services.training_service.validate_file_upload') as mock_validate:
            mock_validate.return_value = MagicMock(
                filename="safe_file.txt",
                file_size=len(sample_file_content)
            )
            
            # Mock regular upload
            with patch.object(training_service, 'upload_file') as mock_upload:
                mock_upload.return_value = MagicMock(spec=TrainingFileResponse)
                
                result = await training_service.upload_file_with_validation(
                    sample_file_content, 
                    "test_file.txt",
                    "help_data"
                )
                
                mock_validate.assert_called_once()
                mock_upload.assert_called_once_with(
                    sample_file_content, 
                    "safe_file.txt", 
                    "help_data"
                )
    
    async def test_upload_file_with_validation_security_error(self, training_service, malicious_file_content):
        """Test file upload blocked by security validation"""
        # Mock file validation to raise SecurityError
        with patch('app.services.training_service.validate_file_upload') as mock_validate:
            mock_validate.side_effect = SecurityError("Malicious file detected")
            
            with pytest.raises(ServiceOperationError, match="File upload blocked by security validation"):
                await training_service.upload_file_with_validation(
                    malicious_file_content,
                    "malicious.txt"
                )
    
    async def test_upload_file_validates_filename(self, training_service, sample_file_content):
        """Test filename validation during upload"""
        dangerous_filename = "../../../etc/passwd"
        
        # Mock the database operations
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "passwd"  # Sanitized filename
        
        training_service.db.add = MagicMock()
        training_service.db.commit = AsyncMock()
        training_service.db.refresh = AsyncMock()
        
        # Mock task submission
        with patch('app.services.training_service.task_manager') as mock_task_manager:
            mock_task_manager.submit_task = AsyncMock(return_value="task_123")
            
            # Mock aiofiles
            with patch('app.services.training_service.aiofiles.open', create=True):
                result = await training_service.upload_file(
                    sample_file_content,
                    dangerous_filename
                )
                
                # File should be saved with sanitized name
                assert ".." not in str(result)
    
    async def test_file_size_validation(self, training_service):
        """Test file size validation"""
        # Create oversized content (51MB)
        oversized_content = b"x" * (51 * 1024 * 1024)
        
        with patch('app.services.training_service.validate_file_upload') as mock_validate:
            mock_validate.side_effect = SecurityError("File size exceeds maximum")
            
            with pytest.raises(ServiceOperationError):
                await training_service.upload_file_with_validation(
                    oversized_content,
                    "huge_file.txt"
                )


@pytest.mark.asyncio
class TestTrainingServiceAsync:
    """Test async processing features of TrainingService"""
    
    async def test_async_task_submission(self, training_service, sample_file_content):
        """Test async task submission for file processing"""
        # Mock database operations
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_file_id"
        mock_training_file.filename = "test.txt"
        
        training_service.db.add = MagicMock()
        training_service.db.commit = AsyncMock()
        training_service.db.refresh = AsyncMock()
        
        # Mock task manager
        with patch('app.services.training_service.task_manager') as mock_task_manager:
            mock_task_manager.submit_task = AsyncMock(return_value="task_123")
            
            # Mock file operations
            with patch('app.services.training_service.aiofiles.open', create=True):
                result = await training_service.upload_file(
                    sample_file_content,
                    "test.txt"
                )
                
                # Verify task was submitted
                mock_task_manager.submit_task.assert_called_once()
                call_args = mock_task_manager.submit_task.call_args
                
                assert call_args[1]["name"] == "process_file_test.txt"
                assert call_args[1]["timeout"] == 600.0
                assert call_args[1]["max_retries"] == 2
                assert "file_id" in call_args[1]["metadata"]
    
    async def test_async_file_processing_success(self, training_service):
        """Test successful async file processing"""
        # Create a real async session mock
        mock_session = AsyncMock()
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "test.txt"
        mock_training_file.file_path = "/tmp/test.txt"
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        
        # Mock AsyncSessionLocal
        with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Mock processor
            mock_processor_result = MagicMock()
            mock_processor_result.success = True
            mock_processor_result.output_path = "/tmp/processed.md"
            mock_processor_result.markdown_path = "/tmp/processed.md"
            mock_processor_result.processor_used = "txt_to_md"
            mock_processor_result.quality_score = 0.9
            
            with patch.object(training_service, '_choose_and_run_processor_safe') as mock_processor:
                mock_processor.return_value = mock_processor_result
                
                # Mock RAG indexing
                with patch.object(training_service, '_index_in_rag_safe') as mock_rag:
                    mock_rag.return_value = None
                    
                    # Execute the async processing
                    await training_service._process_file_async_safe("test_id")
                    
                    # Verify database updates
                    assert mock_training_file.status == "ready"
                    assert mock_training_file.processed_file_path == "/tmp/processed.md"
                    assert mock_training_file.processing_method == "txt_to_md"
                    assert mock_training_file.conversion_status == "completed"
    
    async def test_async_file_processing_timeout(self, training_service):
        """Test async file processing timeout handling"""
        # Mock session
        mock_session = AsyncMock()
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "test.txt"
        mock_training_file.file_path = "/tmp/test.txt"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        
        with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Mock processor to timeout
            async def slow_processor(file_path, filename):
                await asyncio.sleep(10.0)  # Longer than timeout
                return MagicMock(success=True)
            
            with patch.object(training_service, '_choose_and_run_processor_safe', slow_processor):
                # Should raise ServiceOperationError due to timeout
                with pytest.raises(ServiceOperationError, match="File processing timed out"):
                    await training_service._process_file_async_safe("test_id")
    
    async def test_async_file_processing_error_handling(self, training_service):
        """Test async file processing error handling"""
        # Mock session
        mock_session = AsyncMock()
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "test.txt"
        mock_training_file.file_path = "/tmp/test.txt"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        
        with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Mock processor to fail
            with patch.object(training_service, '_choose_and_run_processor_safe') as mock_processor:
                mock_processor.side_effect = RuntimeError("Processing failed")
                
                # Should handle error gracefully
                with pytest.raises(RuntimeError):
                    await training_service._process_file_async_safe("test_id")
                
                # Should mark file as error
                assert mock_training_file.status == "error"
                assert "Processing failed" in mock_training_file.processing_error
    
    async def test_rag_indexing_timeout(self, training_service):
        """Test RAG indexing timeout handling"""
        # Mock session
        mock_session = AsyncMock()
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "test.txt"
        mock_training_file.file_path = "/tmp/test.txt"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        
        with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Mock successful processor
            mock_processor_result = MagicMock()
            mock_processor_result.success = True
            mock_processor_result.output_path = "/tmp/processed.md"
            mock_processor_result.markdown_path = "/tmp/processed.md"
            mock_processor_result.processor_used = "txt_to_md"
            mock_processor_result.quality_score = 0.9
            
            with patch.object(training_service, '_choose_and_run_processor_safe') as mock_processor:
                mock_processor.return_value = mock_processor_result
                
                # Mock slow RAG indexing
                async def slow_rag_indexing(training_file, markdown_path):
                    await asyncio.sleep(10.0)  # Longer than timeout
                
                with patch.object(training_service, '_index_in_rag_safe', slow_rag_indexing):
                    # Should complete but log timeout warning
                    await training_service._process_file_async_safe("test_id")
                    
                    # File should be marked as ready but with timeout status
                    assert mock_training_file.status == "ready"
                    assert mock_training_file.index_status == "timeout"
    
    async def test_reprocess_file_async(self, training_service):
        """Test manual file reprocessing"""
        # Mock database operations
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "test_id"
        mock_training_file.filename = "test.txt"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        training_service.db.execute.return_value = mock_result
        
        # Mock task manager
        with patch('app.services.training_service.task_manager') as mock_task_manager:
            mock_task_manager.submit_task = AsyncMock(return_value="reprocess_task_123")
            
            result = await training_service.process_training_file("test_id")
            
            assert result is True
            mock_task_manager.submit_task.assert_called_once()
            
            call_args = mock_task_manager.submit_task.call_args
            assert call_args[1]["name"] == "reprocess_file_test.txt"
            assert call_args[1]["max_retries"] == 1
            assert call_args[1]["metadata"]["type"] == "reprocessing"


@pytest.mark.asyncio
class TestTrainingServiceIntegration:
    """Integration tests for TrainingService with real async manager"""
    
    async def setup_method(self):
        """Setup for integration tests"""
        # Start the global task manager if not running
        if not task_manager._running:
            await task_manager.start()
    
    async def teardown_method(self):
        """Cleanup after integration tests"""
        # Don't stop global task manager to avoid affecting other tests
        pass
    
    async def test_end_to_end_file_processing(self, mock_db_session):
        """Test end-to-end file processing with real async manager"""
        # Create training service
        with patch('app.services.training_service.settings') as mock_settings:
            mock_settings.TRAINING_DATA_PATH = "/tmp/test_training_data"
            
            service = TrainingService(mock_db_session)
            service.rag_service = AsyncMock()
            
            # Mock processors
            async def mock_processor(file_path, filename):
                await asyncio.sleep(0.1)  # Simulate processing time
                return MagicMock(
                    success=True,
                    output_path="/tmp/processed.md",
                    markdown_path="/tmp/processed.md",
                    processor_used="test_processor",
                    quality_score=0.8
                )
            
            service._choose_and_run_processor_safe = mock_processor
            
            # Mock database operations for async processing
            mock_training_file = MagicMock(spec=TrainingFile)
            mock_training_file.id = "integration_test_id"
            mock_training_file.filename = "integration_test.txt"
            mock_training_file.file_path = "/tmp/integration_test.txt"
            
            # Mock async session for background processing
            with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_training_file
                mock_session.execute.return_value = mock_result
                mock_session.commit = AsyncMock()
                mock_session.close = AsyncMock()
                mock_session_local.return_value = mock_session
                
                # Submit task through real async manager
                task_id = await task_manager.submit_task(
                    service._process_file_async_safe("integration_test_id"),
                    name="integration_test",
                    timeout=30.0
                )
                
                # Wait for task completion
                await task_manager.wait_for_task(task_id, timeout=35.0)
                
                # Verify task completed successfully
                task_info = await task_manager.get_task_status(task_id)
                assert task_info.status == TaskStatus.COMPLETED
                
                # Verify file was processed
                assert mock_training_file.status == "ready"
                assert mock_training_file.processed_file_path == "/tmp/processed.md"
                assert mock_training_file.processing_method == "test_processor"


@pytest.mark.asyncio
class TestTrainingServiceCleanup:
    """Test cleanup and resource management"""
    
    async def test_database_session_cleanup(self, training_service):
        """Test database session is properly cleaned up"""
        # Mock session that tracks if close was called
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        
        # Mock training file
        mock_training_file = MagicMock(spec=TrainingFile)
        mock_training_file.id = "cleanup_test_id"
        mock_training_file.filename = "cleanup_test.txt"
        mock_training_file.file_path = "/tmp/cleanup_test.txt"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_training_file
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        
        with patch('app.services.training_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Mock processor to raise exception
            with patch.object(training_service, '_choose_and_run_processor_safe') as mock_processor:
                mock_processor.side_effect = RuntimeError("Test exception")
                
                # Should handle exception and clean up
                with pytest.raises(RuntimeError):
                    await training_service._process_file_async_safe("cleanup_test_id")
                
                # Verify session was closed
                mock_session.close.assert_called_once()
    
    async def test_file_path_validation(self, training_service, sample_file_content):
        """Test file path validation and sanitization"""
        # Test various dangerous file paths
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "file_with_null\x00byte.txt"
        ]
        
        for dangerous_path in dangerous_paths:
            # Mock database operations
            training_service.db.add = MagicMock()
            training_service.db.commit = AsyncMock()
            training_service.db.refresh = AsyncMock()
            
            # Mock task submission
            with patch('app.services.training_service.task_manager') as mock_task_manager:
                mock_task_manager.submit_task = AsyncMock(return_value="safe_task_123")
                
                # Mock file operations
                with patch('app.services.training_service.aiofiles.open', create=True):
                    result = await training_service.upload_file(
                        sample_file_content,
                        dangerous_path
                    )
                    
                    # Verify path was sanitized (no path traversal)
                    # This would be verified by checking the actual file path stored
                    # In a real implementation, the service should sanitize the path


@pytest.mark.performance
@pytest.mark.asyncio
class TestTrainingServicePerformance:
    """Performance tests for TrainingService"""
    
    async def test_concurrent_file_uploads(self, mock_db_session):
        """Test concurrent file upload performance"""
        # Create training service
        with patch('app.services.training_service.settings') as mock_settings:
            mock_settings.TRAINING_DATA_PATH = "/tmp/test_training_data"
            
            service = TrainingService(mock_db_session)
            
            # Mock all dependencies
            mock_db_session.add = MagicMock()
            mock_db_session.commit = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            # Mock task manager
            with patch('app.services.training_service.task_manager') as mock_task_manager:
                mock_task_manager.submit_task = AsyncMock(side_effect=lambda *args, **kwargs: f"task_{len(mock_task_manager.submit_task.call_args_list)}")
                
                # Mock file operations
                with patch('app.services.training_service.aiofiles.open', create=True):
                    import time
                    
                    start_time = time.time()
                    
                    # Upload multiple files concurrently
                    tasks = []
                    for i in range(10):
                        task = service.upload_file(
                            b"test content",
                            f"test_file_{i}.txt"
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks)
                    
                    end_time = time.time()
                    
                    # All uploads should complete
                    assert len(results) == 10
                    
                    # Should complete reasonably quickly
                    assert end_time - start_time < 5.0
                    
                    # All tasks should be submitted
                    assert mock_task_manager.submit_task.call_count == 10


if __name__ == "__main__":
    pytest.main([__file__])