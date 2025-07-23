"""
Integration Tests für PostgreSQL Document Service
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from io import BytesIO
import uuid
from datetime import datetime, timezone

# Import test dependencies
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Import application modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.document_service import document_service, ConversionResult
from app.utils.batch_converter import batch_converter, PostgreSQLBatchConverter
from app.core.database_postgres import get_db_session
from app.models.postgres_models import Document, SystemMetric
from app.api.v1.documents import router
from app.main import app

# Test constants
TEST_PDF_CONTENT = b"""
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF
"""

TEST_TXT_CONTENT = b"""StreamWorks Documentation

This is a test document for the StreamWorks Q&A system.

## Important Information
- StreamWorks is a data processing platform
- It supports batch processing
- Configuration is done via XML files

### Troubleshooting
Common issues:
1. Connection problems
2. Performance issues
3. Configuration errors

This content will be used for RAG-based question answering.
"""

class TestDocumentService:
    """Test class for Document Service functionality"""
    
    @pytest.mark.asyncio
    async def test_pdf_conversion_success(self):
        """Test successful PDF to Markdown conversion"""
        
        with patch('pypdf.PdfReader') as mock_reader:
            # Mock PDF reader
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF Content\nPage 1 content"
            mock_reader.return_value.pages = [mock_page]
            
            # Mock database operations
            with patch.object(document_service, '_log_conversion_performance') as mock_log_perf, \
                 patch.object(document_service, '_create_document_record') as mock_create_record, \
                 patch.object(document_service, 'save_markdown') as mock_save:
                
                mock_log_perf.return_value = None
                mock_create_record.return_value = "test-doc-id"
                mock_save.return_value = "/path/to/output.md"
                
                # Test conversion
                result = await document_service.convert_pdf_to_markdown(
                    "test.pdf", TEST_PDF_CONTENT
                )
                
                # Assertions
                assert result.success == True
                assert result.markdown_content is not None
                assert "Test PDF Content" in result.markdown_content
                assert result.pages_processed == 1
                assert result.processing_time > 0
                
                # Verify mocks were called
                mock_log_perf.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_txt_conversion_success(self):
        """Test successful TXT to Markdown conversion"""
        
        with patch.object(document_service, '_log_conversion_performance') as mock_log_perf:
            mock_log_perf.return_value = None
            
            # Test conversion
            result = await document_service.convert_txt_to_markdown(
                "test.txt", TEST_TXT_CONTENT
            )
            
            # Assertions
            assert result.success == True
            assert result.markdown_content is not None
            assert "StreamWorks Documentation" in result.markdown_content
            assert result.pages_processed == 1
            assert result.processing_time > 0
            
            # Verify RAG optimization
            assert "# test" in result.markdown_content
    
    @pytest.mark.asyncio
    async def test_convert_and_save_integration(self):
        """Test complete conversion and save process"""
        
        with patch.object(document_service, '_create_document_record') as mock_create_record, \
             patch.object(document_service, 'save_markdown') as mock_save, \
             patch.object(document_service, '_log_conversion_performance') as mock_log_perf, \
             patch.object(document_service, '_update_stats') as mock_update_stats:
            
            mock_create_record.return_value = "test-doc-id"
            mock_save.return_value = "/test/output.md"
            mock_log_perf.return_value = None
            mock_update_stats.return_value = None
            
            # Test conversion
            result = await document_service.convert_and_save(
                "test.txt", TEST_TXT_CONTENT
            )
            
            # Assertions
            assert result.success == True
            assert result.document_id == "test-doc-id"
            assert result.output_path == "/test/output.md"
            
            # Verify all steps were called
            mock_create_record.assert_called_once()
            mock_save.assert_called_once()
            mock_update_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_pdf(self):
        """Test error handling for invalid PDF content"""
        
        with patch('pypdf.PdfReader') as mock_reader:
            mock_reader.side_effect = Exception("Invalid PDF")
            
            with patch.object(document_service, '_log_conversion_error') as mock_log_error:
                mock_log_error.return_value = None
                
                # Test conversion with invalid PDF
                result = await document_service.convert_pdf_to_markdown(
                    "invalid.pdf", b"invalid content"
                )
                
                # Assertions
                assert result.success == False
                assert result.error_message and "Invalid PDF" in result.error_message
                mock_log_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_text_cleaning_for_rag(self):
        """Test RAG-optimized text cleaning"""
        
        # Test input with various formatting issues
        messy_text = """
        
        This    has   multiple    spaces.
        
        
        This has multiple line breaks.
        
        
        This is a very long line that exceeds 200 characters and should be broken down into smaller sentences for better RAG processing. This sentence continues to test the sentence splitting functionality that should work properly.
        
        """
        
        cleaned = document_service._clean_text_for_rag(messy_text)
        
        # Assertions
        assert "multiple    spaces" not in cleaned  # Multiple spaces removed
        assert "\n\n\n" not in cleaned  # Multiple line breaks removed
        lines = cleaned.split('\n')
        
        # Check that long lines were broken down
        long_lines = [line for line in lines if len(line) > 200]
        assert len(long_lines) == 0, "Long lines should be broken down"

class TestBatchConverter:
    """Test class for Batch Converter functionality"""
    
    @pytest.mark.asyncio
    async def test_filter_already_converted(self):
        """Test PostgreSQL deduplication filtering"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = []
            for i in range(3):
                file_path = Path(temp_dir) / f"test_{i}.pdf"
                file_path.write_bytes(TEST_PDF_CONTENT)
                test_files.append(file_path)
            
            converter = PostgreSQLBatchConverter(temp_dir)
            
            # Mock database session to simulate some files already converted
            with patch('app.utils.batch_converter.get_db_session') as mock_session:
                mock_db = AsyncMock()
                mock_session.return_value.__aenter__.return_value = mock_db
                
                # Mock query results - simulate first file already exists
                mock_result = Mock()
                mock_result.first.side_effect = [
                    Mock(),  # File 0 exists
                    None,    # File 1 doesn't exist
                    None     # File 2 doesn't exist
                ]
                mock_db.execute.return_value = mock_result
                
                # Test filtering
                filtered_files = await converter._filter_already_converted(test_files)
                
                # Assertions
                assert len(filtered_files) == 2  # Only 2 files should need conversion
                assert converter.stats["already_converted"] == 1
    
    @pytest.mark.asyncio
    async def test_batch_conversion_with_parallel_processing(self):
        """Test batch conversion with parallel processing"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            for i in range(3):
                file_path = Path(temp_dir) / f"test_{i}.txt"
                file_path.write_bytes(TEST_TXT_CONTENT)
            
            converter = PostgreSQLBatchConverter(temp_dir)
            
            # Mock all dependencies
            with patch.object(converter, '_filter_already_converted') as mock_filter, \
                 patch.object(converter, '_convert_single_file') as mock_convert, \
                 patch.object(converter, '_log_batch_completion') as mock_log:
                
                # Setup mocks
                mock_filter.return_value = [Path(temp_dir) / f"test_{i}.txt" for i in range(3)]
                mock_convert.return_value = {
                    "success": True,
                    "processing_time": 0.5,
                    "file": "test.txt"
                }
                mock_log.return_value = None
                
                # Run batch conversion
                result = await converter.convert_all_documents()
                
                # Assertions
                assert "error" not in result
                assert result["stats"]["newly_converted"] == 3
                assert result["success_rate"] == 100.0
                assert mock_convert.call_count == 3  # All 3 files processed
    
    @pytest.mark.asyncio
    async def test_semaphore_concurrency_limiting(self):
        """Test that semaphore limits concurrent processing"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many test files
            for i in range(10):
                file_path = Path(temp_dir) / f"test_{i}.txt"
                file_path.write_bytes(TEST_TXT_CONTENT)
            
            converter = PostgreSQLBatchConverter(temp_dir)
            
            # Track concurrent executions
            concurrent_count = 0
            max_concurrent = 0
            
            async def mock_convert_with_tracking(file_path):
                nonlocal concurrent_count, max_concurrent
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                
                await asyncio.sleep(0.01)  # Simulate processing time
                
                concurrent_count -= 1
                return {"success": True, "processing_time": 0.01}
            
            with patch.object(converter, '_filter_already_converted') as mock_filter, \
                 patch.object(converter, '_convert_single_file', side_effect=mock_convert_with_tracking), \
                 patch.object(converter, '_log_batch_completion'):
                
                mock_filter.return_value = [Path(temp_dir) / f"test_{i}.txt" for i in range(10)]
                
                # Run batch conversion
                await converter.convert_all_documents()
                
                # Assert semaphore worked (max 5 concurrent as per implementation)
                assert max_concurrent <= 5

class TestDocumentAPI:
    """Test class for Document API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/v1/documents/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "document_service"
        assert data["status"] == "healthy"
        assert data["database"] == "postgresql"
        assert data["storage"] == "unified_storage"
    
    @patch('app.api.v1.documents.document_service')
    @patch('app.core.database_postgres.get_db')
    def test_upload_endpoint_success(self, mock_get_db, mock_service):
        """Test successful file upload"""
        
        # Mock database
        mock_get_db.return_value = AsyncMock()
        
        # Mock service response
        mock_result = ConversionResult(
            success=True,
            document_id="test-doc-id",
            output_path="/test/output.md",
            processing_time=1.5,
            pages_processed=2,
            file_size=1024
        )
        mock_service.convert_and_save.return_value = mock_result
        
        # Test upload
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(TEST_TXT_CONTENT)
            temp_file.seek(0)
            
            response = self.client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", temp_file, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["document_id"] == "test-doc-id"
    
    def test_upload_endpoint_invalid_file_type(self):
        """Test upload with invalid file type"""
        
        with tempfile.NamedTemporaryFile(suffix=".exe") as temp_file:
            temp_file.write(b"invalid content")
            temp_file.seek(0)
            
            response = self.client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.exe", temp_file, "application/octet-stream")}
            )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    @patch('app.api.v1.documents.batch_converter')
    @patch('app.core.database_postgres.get_db')
    def test_batch_convert_endpoint(self, mock_get_db, mock_batch_converter):
        """Test batch convert endpoint"""
        
        # Mock database
        mock_get_db.return_value = AsyncMock()
        
        response = self.client.post("/api/v1/documents/batch-convert?overwrite=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Batch conversion started" in data["message"]
    
    @patch('app.api.v1.documents.document_service')
    @patch('app.core.database_postgres.get_db')
    def test_conversion_stats_endpoint(self, mock_get_db, mock_service):
        """Test conversion statistics endpoint"""
        
        # Mock database
        mock_get_db.return_value = AsyncMock()
        
        # Mock statistics
        from app.services.document_service import ConversionStats
        mock_stats = ConversionStats(
            total_files=10,
            successful_conversions=8,
            failed_conversions=2,
            total_processing_time=15.5,
            average_processing_time=1.55,
            total_size_mb=5.2
        )
        mock_service.get_stats.return_value = mock_stats
        
        response = self.client.get("/api/v1/documents/conversion-stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service_stats"]["total_files"] == 10
        assert data["service_stats"]["success_rate"] == "80.0%"

class TestPerformanceAndLoad:
    """Test class for performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_conversions_performance(self):
        """Test performance under concurrent load"""
        
        # Create multiple conversion tasks
        tasks = []
        for i in range(10):
            task = document_service.convert_txt_to_markdown(
                f"test_{i}.txt", TEST_TXT_CONTENT
            )
            tasks.append(task)
        
        with patch.object(document_service, '_log_conversion_performance'):
            # Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            
            # Assertions
            assert len(results) == 10
            assert all(result.success for result in results)
            
            # Performance assertion - should complete in reasonable time
            total_time = end_time - start_time
            assert total_time < 5.0, f"Concurrent processing took too long: {total_time}s"
    
    @pytest.mark.asyncio
    async def test_large_file_processing(self):
        """Test processing of large files"""
        
        # Create large text content
        large_content = (TEST_TXT_CONTENT * 100).decode('utf-8')
        large_content_bytes = large_content.encode('utf-8')
        
        with patch.object(document_service, '_log_conversion_performance'):
            result = await document_service.convert_txt_to_markdown(
                "large_test.txt", large_content_bytes
            )
            
            # Assertions
            assert result.success == True
            assert result.markdown_content and len(result.markdown_content) > len(large_content)
            assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage_during_batch_processing(self):
        """Test memory usage during batch processing"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many test files
            for i in range(20):
                file_path = Path(temp_dir) / f"test_{i}.txt"
                file_path.write_bytes(TEST_TXT_CONTENT * 10)
            
            converter = PostgreSQLBatchConverter(temp_dir)
            
            with patch.object(converter, '_log_batch_completion'), \
                 patch('app.utils.batch_converter.get_db_session'):
                
                # Mock database operations to avoid actual DB calls
                mock_session = AsyncMock()
                mock_result = Mock()
                mock_result.first.return_value = None  # No files exist
                mock_session.execute.return_value = mock_result
                
                with patch('app.utils.batch_converter.get_db_session') as mock_get_session:
                    mock_get_session.return_value.__aenter__.return_value = mock_session
                    
                    # Run batch processing
                    await converter.convert_all_documents()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assert memory usage is reasonable (less than 100MB increase)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB"

class TestPostgreSQLIntegration:
    """Test class for PostgreSQL integration"""
    
    @pytest.mark.asyncio
    async def test_document_record_creation(self):
        """Test document record creation in PostgreSQL"""
        
        with patch('app.services.document_service.get_db_session') as mock_session:
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            # Mock document creation
            mock_document = Mock()
            mock_document.id = "test-doc-id"
            mock_db.refresh.return_value = None
            
            result = ConversionResult(success=True, processing_time=1.0, pages_processed=1, file_size=1024)
            
            document_id = await document_service._create_document_record(
                "test.txt", "/input/test.txt", "/output/test.md", result
            )
            
            # Assertions
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_performance_metrics_logging(self):
        """Test PostgreSQL performance metrics logging"""
        
        with patch('app.services.document_service.get_db_session') as mock_session:
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            await document_service._log_conversion_performance(
                "pdf_conversion", 2.5, 3, "test.pdf"
            )
            
            # Verify SystemMetric was created and saved
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Check the metric data
            call_args = mock_db.add.call_args[0][0]
            assert call_args.metric_category == "performance"
            assert call_args.metric_name == "pdf_conversion_time"
            assert call_args.metric_value == 2.5
            assert call_args.metric_unit == "seconds"
    
    @pytest.mark.asyncio
    async def test_error_logging_to_postgresql(self):
        """Test error logging to PostgreSQL"""
        
        with patch('app.services.document_service.get_db_session') as mock_session:
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            await document_service._log_conversion_error(
                "Test error message", "test.pdf"
            )
            
            # Verify error metric was created
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Check the error metric data
            call_args = mock_db.add.call_args[0][0]
            assert call_args.metric_category == "error"
            assert call_args.metric_name == "conversion_error"
            assert call_args.metric_value == 1

# Pytest configuration and fixtures
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_db_session():
    """Mock database session for testing"""
    session = AsyncMock(spec=AsyncSession)
    return session

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])