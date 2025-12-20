# Testing Guide

Enterprise testing infrastructure for Streamworks-KI.

## Quick Start

```bash
# Run all tests
cd backend && python3 -m pytest tests/ -v

# Run unit tests only
cd backend && python3 -m pytest tests/unit/ -v

# Run with coverage
cd backend && python3 -m pytest tests/ --cov=services --cov=domains
```

## Test Structure

```
backend/tests/
├── conftest.py          # Enterprise fixtures
├── factories.py         # Factory Boy patterns
├── mocks/               # Mock infrastructure
│   ├── openai_mock.py   # LLM mocking
│   ├── qdrant_mock.py   # Vector store mocking
│   └── supabase_mock.py # Database mocking
├── unit/                # Pure unit tests
├── integration/         # Mocked integrations
├── ai/                  # AI-specific tests
└── e2e/                 # End-to-end tests
```

## Test Markers

- `@pytest.mark.unit` - No I/O, mocked dependencies
- `@pytest.mark.integration` - Mocked external services
- `@pytest.mark.e2e` - Requires running services
- `@pytest.mark.slow` - Takes > 5 seconds
- `@pytest.mark.ai` - Involves LLM calls

## Using Fixtures

```python
def test_project_creation(mock_db, sample_project):
    """mock_db and sample_project from conftest.py"""
    service = TestingService()
    service.db = mock_db
    result = service.create_project("Test")
    assert result is not None
```

## Using Factories

```python
from tests.factories import UserFactory, ProjectFactory

def test_with_factory():
    user = UserFactory()           # Standard user
    admin = UserFactory(admin=True) # Admin user
    project = ProjectFactory()
```

## Using Mocks

```python
from tests.mocks.openai_mock import MockOpenAI

def test_llm_call():
    client = MockOpenAI()
    client.set_response("Test response")
    # Use in service testing
```

## CI/CD

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests

See `.github/workflows/ci.yml` for configuration.
