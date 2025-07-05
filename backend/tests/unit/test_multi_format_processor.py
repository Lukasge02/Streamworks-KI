"""
Unit tests for Multi-Format Document Processor
"""
import pytest
import tempfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.services.multi_format_processor import (
    MultiFormatProcessor, FormatDetector, SmartChunker,
    SupportedFormat, DocumentCategory, FileProcessingResult
)
from langchain.schema import Document


class TestFormatDetector:
    """Test format detection functionality"""
    
    def setup_method(self):
        self.detector = FormatDetector()
    
    def test_detect_python_format(self):
        """Test Python file detection"""
        content = b'import os\ndef main():\n    print("Hello World")'
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            detected = self.detector.detect_format(temp_path, content)
            assert detected == SupportedFormat.PY
        finally:
            Path(temp_path).unlink()
    
    def test_detect_json_format(self):
        """Test JSON file detection"""
        content = b'{"name": "test", "value": 123}'
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            detected = self.detector.detect_format(temp_path, content)
            assert detected == SupportedFormat.JSON
        finally:
            Path(temp_path).unlink()
    
    def test_detect_xml_format(self):
        """Test XML file detection"""
        content = b'<?xml version="1.0"?><root><item>test</item></root>'
        
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            detected = self.detector.detect_format(temp_path, content)
            assert detected == SupportedFormat.XML
        finally:
            Path(temp_path).unlink()
    
    def test_categorize_help_document(self):
        """Test document categorization"""
        category = self.detector.categorize_document(SupportedFormat.MD, "help_guide.md")
        assert category == DocumentCategory.HELP_DOCUMENTATION
    
    def test_categorize_code_script(self):
        """Test code script categorization"""
        category = self.detector.categorize_document(SupportedFormat.PY, "script.py")
        assert category == DocumentCategory.CODE_SCRIPT
    
    def test_categorize_xml_config(self):
        """Test XML configuration categorization"""
        category = self.detector.categorize_document(SupportedFormat.XML, "config.xml")
        assert category == DocumentCategory.XML_CONFIGURATION


class TestSmartChunker:
    """Test intelligent chunking strategies"""
    
    def setup_method(self):
        self.chunker = SmartChunker()
    
    def test_chunk_python_code(self):
        """Test Python code chunking"""
        python_content = """
import os

def function_one():
    '''First function'''
    return "hello"

class TestClass:
    '''Test class'''
    def method_one(self):
        return "world"

def function_two():
    '''Second function'''
    return "test"
"""
        
        document = Document(
            page_content=python_content,
            metadata={"source": "test.py"}
        )
        
        chunks = self.chunker.chunk_document(document, SupportedFormat.PY)
        
        # Should have multiple chunks for functions/classes
        assert len(chunks) > 1
        
        # Check metadata
        for chunk in chunks:
            assert "source" in chunk.metadata
    
    def test_chunk_json_document(self):
        """Test JSON document chunking"""
        json_content = json.dumps({
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "settings": {
                "theme": "dark",
                "language": "en"
            }
        }, indent=2)
        
        document = Document(
            page_content=json_content,
            metadata={"source": "test.json"}
        )
        
        chunks = self.chunker.chunk_document(document, SupportedFormat.JSON)
        
        # Should create chunks for different top-level keys
        assert len(chunks) >= 1
        
        # Check chunk types
        chunk_types = [chunk.metadata.get('chunk_type') for chunk in chunks]
        assert any('json_object_key' in str(ct) for ct in chunk_types)
    
    def test_chunk_xml_document(self):
        """Test XML document chunking"""
        xml_content = """<?xml version="1.0"?>
<root>
    <user id="1">
        <name>Alice</name>
        <email>alice@test.com</email>
    </user>
    <user id="2">
        <name>Bob</name>
        <email>bob@test.com</email>
    </user>
    <settings>
        <theme>dark</theme>
        <language>en</language>
    </settings>
</root>"""
        
        document = Document(
            page_content=xml_content,
            metadata={"source": "test.xml"}
        )
        
        chunks = self.chunker.chunk_document(document, SupportedFormat.XML)
        
        # Should create chunks for XML elements
        assert len(chunks) >= 1
        
        # Check chunk metadata
        for chunk in chunks:
            if chunk.metadata.get('chunk_type') == 'xml_element':
                assert 'element_tag' in chunk.metadata
    
    def test_chunk_csv_document(self):
        """Test CSV document chunking"""
        csv_content = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago
Diana,28,Boston
Eve,32,Seattle"""
        
        document = Document(
            page_content=csv_content,
            metadata={"source": "test.csv"}
        )
        
        chunks = self.chunker.chunk_document(document, SupportedFormat.CSV)
        
        # Should create chunks with CSV rows
        assert len(chunks) >= 1
        
        # Each chunk should contain the header
        for chunk in chunks:
            assert "name,age,city" in chunk.page_content
            assert chunk.metadata.get('chunk_type') == 'csv_rows'


class TestMultiFormatProcessor:
    """Test complete multi-format processing"""
    
    def setup_method(self):
        self.processor = MultiFormatProcessor()
    
    @pytest.mark.asyncio
    async def test_process_text_file(self):
        """Test processing a simple text file"""
        content = b"This is a test text file with some content for testing."
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = await self.processor.process_file(temp_path, content)
            
            assert result.success
            assert result.file_format == SupportedFormat.TXT
            assert result.category == DocumentCategory.HELP_DOCUMENTATION
            assert len(result.documents) >= 1
            
            # Check metadata
            for doc in result.documents:
                assert doc.metadata['file_format'] == 'txt'
                assert doc.metadata['processing_method'] == 'multi_format_processor'
                assert 'original_filename' in doc.metadata
                
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_process_python_file(self):
        """Test processing a Python file"""
        content = b'''import os
import sys

def main():
    """Main function"""
    print("Hello, World!")
    return 0

class TestClass:
    """Test class"""
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    main()
'''
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = await self.processor.process_file(temp_path, content)
            
            assert result.success
            assert result.file_format == SupportedFormat.PY
            assert result.category == DocumentCategory.CODE_SCRIPT
            assert len(result.documents) >= 1
            
            # Check processing method
            assert result.processing_method == "function_based"
            
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_process_json_file(self):
        """Test processing a JSON file"""
        json_data = {
            "api_config": {
                "base_url": "https://api.example.com",
                "timeout": 30,
                "retries": 3
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "test_db"
            },
            "features": [
                {"name": "feature1", "enabled": True},
                {"name": "feature2", "enabled": False}
            ]
        }
        content = json.dumps(json_data, indent=2).encode('utf-8')
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = await self.processor.process_file(temp_path, content)
            
            assert result.success
            assert result.file_format == SupportedFormat.JSON
            assert result.category == DocumentCategory.STRUCTURED_DATA
            assert len(result.documents) >= 1
            
            # Check processing method
            assert result.processing_method == "structure_based"
            
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_process_xml_file(self):
        """Test processing an XML file"""
        xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<stream_config>
    <metadata>
        <name>Test Stream</name>
        <version>1.0</version>
        <description>Test configuration for StreamWorks</description>
    </metadata>
    <processing>
        <input_format>CSV</input_format>
        <output_format>JSON</output_format>
        <batch_size>1000</batch_size>
    </processing>
    <schedule>
        <frequency>daily</frequency>
        <time>02:00</time>
        <timezone>UTC</timezone>
    </schedule>
</stream_config>'''
        
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_file:
            temp_file.write(xml_content)
            temp_path = temp_file.name
        
        try:
            result = await self.processor.process_file(temp_path, xml_content)
            
            assert result.success
            assert result.file_format == SupportedFormat.XML
            # Should be categorized as config since filename doesn't have specific indicators
            assert result.category in [DocumentCategory.XML_CONFIGURATION, DocumentCategory.SCHEMA_DEFINITION]
            assert len(result.documents) >= 1
            
            # Check processing method
            assert result.processing_method == "element_based"
            
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_process_unsupported_file(self):
        """Test graceful handling of unsupported file types"""
        # Binary content that can't be decoded
        content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = await self.processor.process_file(temp_path, content)
            
            # Should either succeed with text fallback or fail gracefully
            if result.success:
                assert len(result.documents) >= 0
            else:
                assert result.error_message is not None
                
        finally:
            Path(temp_path).unlink()
    
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = self.processor.get_supported_formats()
        
        assert isinstance(formats, list)
        assert len(formats) > 20  # Should support 20+ formats
        assert 'txt' in formats
        assert 'py' in formats
        assert 'json' in formats
        assert 'xml' in formats
    
    def test_get_supported_categories(self):
        """Test getting supported categories"""
        categories = self.processor.get_supported_categories()
        
        assert isinstance(categories, list)
        assert 'help_docs' in categories
        assert 'code_script' in categories
        assert 'structured_data' in categories
    
    def test_get_processing_stats(self):
        """Test getting processing statistics"""
        stats = self.processor.get_processing_stats()
        
        assert isinstance(stats, dict)
        assert 'total_files' in stats
        assert 'successful_files' in stats
        assert 'failed_files' in stats
        assert 'success_rate_percent' in stats
        assert 'formats_processed' in stats
        assert 'categories_processed' in stats


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow"""
    processor = MultiFormatProcessor()
    
    # Test multiple file types in sequence
    test_files = [
        ('.txt', b'Simple text content for testing'),
        ('.py', b'def test():\n    return "hello"'),
        ('.json', b'{"test": "value", "number": 123}'),
        ('.xml', b'<?xml version="1.0"?><root><test>value</test></root>')
    ]
    
    results = []
    
    for suffix, content in test_files:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = await processor.process_file(temp_path, content)
            results.append(result)
        finally:
            Path(temp_path).unlink()
    
    # All should succeed
    assert all(result.success for result in results)
    
    # Should have different formats and categories
    formats = {result.file_format for result in results}
    assert len(formats) == 4  # All different formats
    
    # Check statistics
    stats = processor.get_processing_stats()
    assert stats['total_files'] >= 4
    assert stats['successful_files'] >= 4
    assert stats['success_rate_percent'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])