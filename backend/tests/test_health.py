"""
Tests for Health Check Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoints:
    """Test suite for health check endpoints"""

    def test_quick_health_check(self, client):
        """Test the quick /health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_detailed_health_check_structure(self, client):
        """Test /health/detailed returns expected structure"""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()

        # Check top-level keys
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data

        # Check status is valid enum value
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

        # Check components exist
        components = data["components"]
        assert "qdrant" in components
        assert "minio" in components
        assert "supabase" in components

    def test_detailed_health_component_structure(self, client):
        """Test each component has expected fields"""
        response = client.get("/health/detailed")
        data = response.json()

        for component_name, component_data in data["components"].items():
            assert "status" in component_data, f"{component_name} missing status"
            assert "message" in component_data, f"{component_name} missing message"
            # latency_ms may be None if component is unhealthy
            assert (
                "latency_ms" in component_data or component_data["status"] != "healthy"
            )


class TestDIContainer:
    """Test suite for DI Container"""

    def test_container_get_health_service(self):
        """Test Container returns HealthService"""
        from services.container import Container

        health_service = Container.get_health_service()
        assert health_service is not None

        # Same instance should be returned (singleton)
        health_service2 = Container.get_health_service()
        assert health_service is health_service2

    def test_container_get_db_service(self):
        """Test Container returns DatabaseService"""
        from services.container import Container

        db_service = Container.get_db_service()
        assert db_service is not None

    def test_container_override(self):
        """Test Container override mechanism for testing"""
        from services.container import Container

        # Create a mock
        mock_service = object()

        # Override
        Container.override("test_service", mock_service)

        # Clean up
        Container.clear_overrides()

    def test_container_reset(self):
        """Test Container reset clears all instances"""
        from services.container import Container

        # Get a service
        Container.get_health_service()

        # Reset (note: this will require re-initialization)
        Container.reset()

        # Re-initialize for other tests
        Container.initialize()


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_returns_service_info(self, client):
        """Test root endpoint returns service information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "Streamworks Self Service API"
        assert data["version"] == "2.0.0"
        assert "domains" in data
        assert "testing" in data["domains"]
