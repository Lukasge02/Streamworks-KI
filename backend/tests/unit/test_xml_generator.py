"""
Unit tests for XML Generator Service
Target: 90%+ coverage for XML generation logic
"""
import pytest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
from datetime import datetime

from app.services.xml_generator import XMLGeneratorService
from app.services.error_handler import XMLGenerationError, XMLValidationError


class TestXMLGeneratorService:
    """Test suite for XML Generator Service"""
    
    @pytest.fixture
    def xml_generator(self):
        """Create XML generator instance for testing"""
        return XMLGeneratorService()
    
    @pytest.fixture
    def sample_job_config(self):
        """Sample job configuration for testing"""
        return {
            "job_name": "TestJob",
            "job_type": "batch",
            "source_path": "/data/input",
            "destination_path": "/data/output",
            "schedule": {
                "type": "daily",
                "time": "02:00"
            },
            "parameters": {
                "format": "csv",
                "delimiter": ","
            }
        }
    
    # Test initialization
    def test_init_success(self):
        """Test successful XML generator initialization"""
        generator = XMLGeneratorService()
        assert generator.generation_method == "professional_templates"
        assert generator.statistics["total_generated"] == 0
        assert len(generator.templates) > 0
    
    def test_load_templates(self, xml_generator):
        """Test template loading"""
        assert "batch_job" in xml_generator.templates
        assert "stream_processing" in xml_generator.templates
        assert "data_pipeline" in xml_generator.templates
    
    # Test XML generation
    def test_generate_batch_job_xml(self, xml_generator, sample_job_config):
        """Test batch job XML generation"""
        xml_content = xml_generator.generate_xml(sample_job_config)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_content)
        assert root.tag == "streamworks"
        
        # Check job name
        job_elem = root.find(".//job")
        assert job_elem.get("name") == "TestJob"
        assert job_elem.get("type") == "batch"
        
        # Verify statistics updated
        assert xml_generator.statistics["total_generated"] == 1
    
    def test_generate_stream_processing_xml(self, xml_generator):
        """Test stream processing XML generation"""
        config = {
            "job_name": "StreamProcessor",
            "job_type": "stream",
            "source_type": "kafka",
            "topic": "events",
            "processing_interval": 1000
        }
        
        xml_content = xml_generator.generate_xml(config)
        
        root = ET.fromstring(xml_content)
        assert root.find(".//job").get("type") == "stream"
        assert root.find(".//source/topic").text == "events"
    
    def test_generate_with_schedule(self, xml_generator):
        """Test XML generation with schedule configuration"""
        config = {
            "job_name": "ScheduledJob",
            "schedule": {
                "type": "cron",
                "expression": "0 2 * * *"
            }
        }
        
        xml_content = xml_generator.generate_xml(config)
        
        root = ET.fromstring(xml_content)
        schedule = root.find(".//schedule")
        assert schedule is not None
        assert schedule.find("cron").text == "0 2 * * *"
    
    # Test validation
    def test_validate_xml_success(self, xml_generator):
        """Test successful XML validation"""
        valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <streamworks>
            <job name="test" type="batch">
                <source>/data/input</source>
            </job>
        </streamworks>"""
        
        is_valid, errors = xml_generator.validate_xml(valid_xml)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_xml_with_errors(self, xml_generator):
        """Test XML validation with errors"""
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <streamworks>
            <job><!-- Missing required attributes -->
                <source>/data/input</source>
            </job>
        </streamworks>"""
        
        is_valid, errors = xml_generator.validate_xml(invalid_xml)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_malformed_xml(self, xml_generator):
        """Test validation of malformed XML"""
        malformed_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <streamworks>
            <job name="test">
                <source>/data/input
            </job><!-- Missing closing tag -->
        </streamworks>"""
        
        with pytest.raises(XMLValidationError):
            xml_generator.validate_xml(malformed_xml)
    
    # Test error handling
    def test_generate_with_missing_required_fields(self, xml_generator):
        """Test generation with missing required fields"""
        invalid_config = {
            "schedule": {"type": "daily"}  # Missing job_name
        }
        
        with pytest.raises(XMLGenerationError):
            xml_generator.generate_xml(invalid_config)
    
    def test_generate_with_invalid_job_type(self, xml_generator):
        """Test generation with invalid job type"""
        config = {
            "job_name": "Test",
            "job_type": "invalid_type"
        }
        
        with pytest.raises(XMLGenerationError):
            xml_generator.generate_xml(config)
    
    # Test template selection
    def test_select_template_batch(self, xml_generator):
        """Test template selection for batch job"""
        config = {"job_type": "batch"}
        template = xml_generator._select_template(config)
        assert "batch" in template.lower()
    
    def test_select_template_stream(self, xml_generator):
        """Test template selection for stream processing"""
        config = {"job_type": "stream"}
        template = xml_generator._select_template(config)
        assert "stream" in template.lower()
    
    def test_select_template_default(self, xml_generator):
        """Test default template selection"""
        config = {}
        template = xml_generator._select_template(config)
        assert template is not None
    
    # Test performance
    def test_generation_performance(self, xml_generator, performance_tracker):
        """Test XML generation performance"""
        config = {
            "job_name": "PerformanceTest",
            "job_type": "batch",
            "parameters": {f"param{i}": f"value{i}" for i in range(100)}
        }
        
        performance_tracker.start("xml_generation")
        xml_generator.generate_xml(config)
        performance_tracker.end("xml_generation")
        
        # XML generation should be fast
        performance_tracker.assert_performance("xml_generation", 0.5)
    
    # Test statistics
    def test_get_statistics(self, xml_generator):
        """Test statistics retrieval"""
        # Generate some XMLs
        config = {"job_name": "Test"}
        xml_generator.generate_xml(config)
        xml_generator.generate_xml(config)
        
        stats = xml_generator.get_statistics()
        assert stats["total_generated"] == 2
        assert stats["successful_validations"] >= 0
        assert "last_generation" in stats
    
    # Test health check
    def test_get_health(self, xml_generator):
        """Test health status"""
        health = xml_generator.get_health()
        
        assert health["status"] in ["healthy", "not_initialized"]
        assert health["xml_generation_enabled"] is True
        assert health["templates_loaded"] > 0
    
    # Test template variables
    def test_replace_template_variables(self, xml_generator):
        """Test template variable replacement"""
        template = "<job name='{{job_name}}' time='{{timestamp}}'></job>"
        config = {"job_name": "TestJob"}
        
        result = xml_generator._replace_variables(template, config)
        
        assert "TestJob" in result
        assert "{{job_name}}" not in result
        assert "{{timestamp}}" not in result  # Should be replaced with actual timestamp
    
    # Test complex configurations
    def test_generate_complex_pipeline(self, xml_generator):
        """Test generation of complex data pipeline"""
        config = {
            "job_name": "ComplexPipeline",
            "job_type": "batch",
            "steps": [
                {"type": "extract", "source": "database"},
                {"type": "transform", "operations": ["clean", "aggregate"]},
                {"type": "load", "destination": "warehouse"}
            ],
            "error_handling": {
                "retry_count": 3,
                "on_failure": "alert"
            }
        }
        
        xml_content = xml_generator.generate_xml(config)
        root = ET.fromstring(xml_content)
        
        # Verify complex structure
        assert root.find(".//steps") is not None
        assert len(root.findall(".//step")) >= 3