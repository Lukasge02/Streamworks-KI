"""
Pytest configuration with efficient test fixtures
Provides reusable components for all tests
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.database import Base, get_db
from app.services.rag_service import RAGService
from app.services.mistral_llm_service import MistralLLMService
from app.services.error_handler import StreamWorksErrorHandler

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def client(test_db) -> TestClient:
    """Create test client with database override"""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_rag_service():
    """Mock RAG service for testing"""
    service = RAGService()
    # Configure mock behavior
    return service

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    service = MistralLLMService()
    # Configure mock behavior
    return service


@pytest.fixture
def sample_training_file():
    """Sample training file data"""
    return {
        "id": "test-file-123",
        "filename": "test_training.txt",
        "category": "help_data",
        "content": "StreamWorks ist eine Plattform für Workflow-Automatisierung.",
        "file_size": 1024
    }

@pytest.fixture
def sample_chat_request():
    """Sample chat request data"""
    return {
        "message": "Was ist StreamWorks?",
        "conversation_id": "test-conv-123"
    }


# Performance testing fixtures
@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests"""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.metrics = {}
        
        def start(self, name: str):
            self.metrics[name] = {"start": time.time()}
        
        def end(self, name: str):
            if name in self.metrics:
                self.metrics[name]["end"] = time.time()
                self.metrics[name]["duration"] = (
                    self.metrics[name]["end"] - self.metrics[name]["start"]
                )
        
        def get_duration(self, name: str) -> float:
            return self.metrics.get(name, {}).get("duration", 0)
        
        def assert_performance(self, name: str, max_duration: float):
            duration = self.get_duration(name)
            assert duration < max_duration, (
                f"{name} took {duration:.2f}s, exceeding limit of {max_duration}s"
            )
    
    return PerformanceTracker()

# Async helpers
@pytest.fixture
def async_client():
    """Async test client for testing async endpoints"""
    from httpx import AsyncClient
    
    async def _get_client():
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    return _get_client()

# Test data generators
@pytest.fixture
def generate_test_documents():
    """Generate test documents for RAG testing"""
    def _generate(count: int = 10):
        documents = []
        for i in range(count):
            documents.append({
                "id": f"doc-{i}",
                "content": f"Test document {i} about StreamWorks features.",
                "metadata": {
                    "source": f"test-{i}.txt",
                    "category": "help_data"
                }
            })
        return documents
    
    return _generate

# Error simulation fixtures
@pytest.fixture
def simulate_errors():
    """Simulate various error conditions"""
    class ErrorSimulator:
        @staticmethod
        def connection_error():
            raise ConnectionError("Simulated connection error")
        
        @staticmethod
        def timeout_error():
            raise TimeoutError("Simulated timeout")
        
        @staticmethod
        def validation_error():
            raise ValueError("Simulated validation error")
    
    return ErrorSimulator()