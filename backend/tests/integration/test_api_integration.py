"""
Integration tests for API endpoints
Tests complete workflows and component interactions
"""
import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime
import os

from app.main import app


class TestAPIIntegration:
    """Integration tests for StreamWorks-KI API"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_file_content(self):
        """Sample file content for upload tests"""
        return "StreamWorks ist eine Plattform für Workflow-Automatisierung."
    
    # Health endpoint tests
    def test_health_check_complete(self, client):
        """Test complete health check endpoint"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_status" in data
        assert "components" in data
        assert len(data["components"]) > 0
        
        # Check specific components
        component_names = [c["component"] for c in data["components"]]
        assert "database" in component_names
        assert "rag_service" in component_names
        assert "xml_generator" in component_names
    
    def test_quick_health_check(self, client):
        """Test quick health check for load balancers"""
        response = client.get("/api/v1/health/quick")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_component_health_check(self, client):
        """Test individual component health check"""
        components = ["database", "rag_service", "xml_generator", "system_resources"]
        
        for component in components:
            response = client.get(f"/api/v1/health/component/{component}")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "component" in data
            assert data["component"] == component
    
    # Chat endpoint tests
    def test_chat_flow_complete(self, client):
        """Test complete chat flow"""
        # 1. Send chat message
        chat_request = {
            "message": "Was ist StreamWorks?",
            "conversation_id": "test-conv-123"
        }
        
        response = client.post("/api/v1/chat/", json=chat_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert len(data["response"]) > 0
        assert "mode" in data
        assert data["mode"] in ["mistral_rag", "rag_only", "fallback"]
        
        # Check response headers for monitoring
        assert "x-process-time" in response.headers
        assert "x-request-id" in response.headers
    
    def test_chat_with_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post("/api/v1/chat/", json={"message": ""})
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_with_long_message(self, client):
        """Test chat with very long message"""
        long_message = "Test " * 1000  # 5000 characters
        response = client.post("/api/v1/chat/", json={"message": long_message})
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 422]
    
    # XML generation tests
    def test_xml_generation_flow(self, client):
        """Test complete XML generation flow"""
        xml_request = {
            "job_name": "TestJob",
            "job_type": "batch",
            "source_path": "/data/input",
            "destination_path": "/data/output",
            "schedule": {
                "type": "daily",
                "time": "02:00"
            }
        }
        
        response = client.post("/api/v1/xml/generate", json=xml_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "xml_content" in data
        assert "<?xml" in data["xml_content"]
        assert "is_valid" in data
        assert data["generation_method"] == "professional_templates"
    
    def test_xml_validation(self, client):
        """Test XML validation endpoint"""
        valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <streamworks>
            <job name="test" type="batch">
                <source>/data/input</source>
            </job>
        </streamworks>"""
        
        response = client.post(
            "/api/v1/xml/validate",
            json={"xml_content": valid_xml}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
    
    # Training data tests
    def test_training_file_upload_and_list(self, client, tmp_path):
        """Test file upload and listing flow"""
        # Create test file
        test_file = tmp_path / "test_training.txt"
        test_file.write_text("Test training content")
        
        # Upload file
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/training/upload",
                files={"file": ("test_training.txt", f, "text/plain")},
                data={"category": "help_data"}
            )
        
        if response.status_code == 200:
            upload_data = response.json()
            assert "file_id" in upload_data
            assert upload_data["status"] in ["processing", "ready"]
            
            # List files
            list_response = client.get("/api/v1/training/files")
            assert list_response.status_code == 200
            files = list_response.json()
            assert isinstance(files, list)
    
    # Search functionality tests
    def test_search_documents(self, client):
        """Test document search functionality"""
        response = client.get("/api/v1/search?query=StreamWorks&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "query" in data
        assert data["query"] == "StreamWorks"
        assert isinstance(data["results"], list)
    
    # Conversation tests
    def test_conversation_flow(self, client):
        """Test conversation management"""
        # Start conversation
        start_response = client.post("/api/v1/conversations/start")
        
        if start_response.status_code == 200:
            data = start_response.json()
            conversation_id = data["conversation_id"]
            
            # Add messages
            client.post(
                "/api/v1/chat/",
                json={
                    "message": "Hello",
                    "conversation_id": conversation_id
                }
            )
            
            # Get conversation
            get_response = client.get(f"/api/v1/conversations/{conversation_id}")
            assert get_response.status_code == 200
    
    # Evaluation tests
    def test_evaluation_metrics(self, client):
        """Test evaluation metrics endpoint"""
        response = client.get("/api/v1/evaluation/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert "recent_evaluations" in data
    
    # Performance tests
    def test_api_response_times(self, client, performance_tracker):
        """Test API response times are within limits"""
        endpoints = [
            ("/health", "GET", None),
            ("/api/v1/health/quick", "GET", None),
            ("/api/v1/chat/", "POST", {"message": "Test"}),
        ]
        
        for endpoint, method, data in endpoints:
            performance_tracker.start(endpoint)
            
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=data)
            
            performance_tracker.end(endpoint)
            
            # All endpoints should respond within 2 seconds
            performance_tracker.assert_performance(endpoint, 2.0)
            
            # Check monitoring headers
            if "x-process-time" in response.headers:
                process_time = float(response.headers["x-process-time"])
                assert process_time < 2.0
    
    # Error handling tests
    def test_error_handling_404(self, client):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_error_handling_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/chat/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    # Metrics endpoint test
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "monitoring_active"
        assert "monitoring_features" in data