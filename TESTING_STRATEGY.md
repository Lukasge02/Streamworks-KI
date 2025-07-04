# 🧪 StreamWorks-KI - Testing Strategy

## 🎯 **Testing Philosophy**
**"Code ohne Tests ist kaputt by design"** - Wir schreiben Tests für alles, was wichtig ist.

### **Testing Pyramid**
```
     /\
    /  \    E2E Tests (10%)
   /____\   Integration Tests (20%)
  /______\  Unit Tests (70%)
```

---

## 🔬 **Unit Testing Strategy**

### **Backend Unit Tests** (Python + pytest)

#### **1. RAG Service Tests**
```python
# tests/services/test_rag_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.rag_service import RAGService

class TestRAGService:
    
    @pytest.fixture
    def rag_service(self):
        return RAGService()
    
    @patch('app.services.rag_service.ChromaDB')
    def test_add_document_success(self, mock_chromadb, rag_service):
        """Test successful document addition"""
        # Arrange
        mock_chromadb.add_documents.return_value = True
        document = "Test document content"
        
        # Act
        result = rag_service.add_document(document)
        
        # Assert
        assert result is True
        mock_chromadb.add_documents.assert_called_once()
    
    def test_search_documents_with_results(self, rag_service):
        """Test document search with results"""
        # Test implementation
        pass
    
    def test_search_documents_no_results(self, rag_service):
        """Test document search with no results"""
        # Test implementation
        pass
        
    def test_search_with_invalid_query(self, rag_service):
        """Test search with invalid query"""
        # Test implementation
        pass
```

#### **2. XML Generator Tests**
```python
# tests/services/test_xml_generator.py
import pytest
from app.services.xml_generator import XMLGenerator

class TestXMLGenerator:
    
    @pytest.fixture
    def xml_generator(self):
        return XMLGenerator()
    
    def test_generate_batch_job_xml(self, xml_generator):
        """Test batch job XML generation"""
        # Arrange
        job_config = {
            "name": "test_job",
            "schedule": "daily",
            "source": "csv_file.csv"
        }
        
        # Act
        xml_result = xml_generator.generate_batch_job(job_config)
        
        # Assert
        assert xml_result is not None
        assert "test_job" in xml_result
        assert xml_result.startswith("<?xml")
    
    def test_validate_xml_structure(self, xml_generator):
        """Test XML validation"""
        # Test implementation
        pass
```

#### **3. Database Service Tests**
```python
# tests/services/test_database_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import TrainingFile
from app.services.database_service import DatabaseService

class TestDatabaseService:
    
    @pytest.fixture
    def db_service(self):
        # In-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")
        return DatabaseService(engine)
    
    def test_create_training_file(self, db_service):
        """Test training file creation"""
        # Test implementation
        pass
    
    def test_get_training_files(self, db_service):
        """Test retrieving training files"""
        # Test implementation
        pass
```

#### **4. Health Check Tests**
```python
# tests/api/test_health.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoints:
    
    def test_health_check_success(self):
        """Test basic health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_detailed_health_check(self):
        """Test detailed health check"""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        assert "components" in response.json()
    
    def test_component_health_check(self):
        """Test individual component health"""
        response = client.get("/api/v1/health/component/database")
        assert response.status_code == 200
```

### **Frontend Unit Tests** (React + Jest + Testing Library)

#### **1. Component Tests**
```typescript
// tests/components/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '../components/ChatInterface';

describe('ChatInterface', () => {
  test('renders chat input', () => {
    render(<ChatInterface />);
    const inputElement = screen.getByPlaceholderText(/nachricht eingeben/i);
    expect(inputElement).toBeInTheDocument();
  });

  test('sends message on form submit', async () => {
    const mockSendMessage = jest.fn();
    render(<ChatInterface onSendMessage={mockSendMessage} />);
    
    const input = screen.getByPlaceholderText(/nachricht eingeben/i);
    const sendButton = screen.getByRole('button', { name: /senden/i });
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
  });
});
```

#### **2. Hook Tests**
```typescript
// tests/hooks/useChat.test.ts
import { renderHook, act } from '@testing-library/react';
import { useChat } from '../hooks/useChat';

describe('useChat', () => {
  test('initializes with empty messages', () => {
    const { result } = renderHook(() => useChat());
    expect(result.current.messages).toEqual([]);
  });

  test('adds message correctly', () => {
    const { result } = renderHook(() => useChat());
    
    act(() => {
      result.current.addMessage('Test message', 'user');
    });
    
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe('Test message');
  });
});
```

---

## 🔗 **Integration Testing**

### **API Integration Tests**
```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIIntegration:
    
    def test_chat_flow_integration(self):
        """Test complete chat flow"""
        # 1. Upload training data
        response = client.post("/api/v1/training/upload", ...)
        assert response.status_code == 200
        
        # 2. Send chat message
        response = client.post("/api/v1/chat/", 
                              json={"message": "Was ist StreamWorks?"})
        assert response.status_code == 200
        assert "response" in response.json()
    
    def test_xml_generation_flow(self):
        """Test XML generation flow"""
        # Test complete XML generation workflow
        pass
```

### **Database Integration Tests**
```python
# tests/integration/test_database_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

class TestDatabaseIntegration:
    
    @pytest.fixture
    def test_db(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine
    
    def test_full_database_workflow(self, test_db):
        """Test complete database operations"""
        # Test CRUD operations
        pass
```

---

## 🎭 **End-to-End Testing**

### **E2E Test Setup** (Playwright)
```typescript
// tests/e2e/chat-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Workflow', () => {
  test('user can upload training data and chat', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Upload training data
    await page.click('[data-testid="training-data-tab"]');
    await page.setInputFiles('[data-testid="file-upload"]', 'test-data.txt');
    await page.click('[data-testid="upload-button"]');
    
    // Wait for upload to complete
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Switch to chat
    await page.click('[data-testid="chat-tab"]');
    
    // Send message
    await page.fill('[data-testid="chat-input"]', 'Was ist StreamWorks?');
    await page.click('[data-testid="send-button"]');
    
    // Verify response
    await expect(page.locator('[data-testid="chat-response"]')).toBeVisible();
  });
});
```

---

## 📊 **Performance Testing**

### **Load Testing** (Python + locust)
```python
# tests/performance/load_test.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def chat_message(self):
        self.client.post("/api/v1/chat/", 
                        json={"message": "Was ist StreamWorks?"})
    
    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")
```

### **Memory & Performance Tests**
```python
# tests/performance/test_memory_usage.py
import pytest
import psutil
import os
from app.services.rag_service import RAGService

class TestPerformance:
    
    def test_memory_usage_within_limits(self):
        """Test that memory usage stays within acceptable limits"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operation
        rag_service = RAGService()
        rag_service.process_large_document("large_test_document.txt")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Assert memory increase is reasonable (< 100MB)
        assert memory_increase < 100 * 1024 * 1024
    
    def test_response_time_under_2_seconds(self):
        """Test that RAG responses are under 2 seconds"""
        import time
        
        start_time = time.time()
        # Perform operation
        end_time = time.time()
        
        assert (end_time - start_time) < 2.0
```

---

## 🚀 **Test Automation & CI/CD**

### **GitHub Actions Workflow**
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run backend tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test -- --coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

---

## 📈 **Test Coverage Goals**

### **Coverage Targets**
- **Backend**: 80%+ overall, 90%+ for critical services
- **Frontend**: 70%+ overall, 80%+ for business logic
- **Integration**: 60%+ API endpoint coverage
- **E2E**: 50%+ user workflow coverage

### **Critical Path Testing**
1. **RAG Pipeline**: 95% coverage (core functionality)
2. **XML Generation**: 90% coverage (business logic)
3. **Database Operations**: 85% coverage (data integrity)
4. **Health Checks**: 100% coverage (monitoring)

### **Test Quality Metrics**
- **Test Speed**: Unit tests < 1s each
- **Test Isolation**: No shared state between tests
- **Test Readability**: Clear AAA pattern (Arrange, Act, Assert)
- **Test Maintainability**: Regular refactoring

---

## 🎯 **Testing Best Practices**

### **Unit Test Principles**
1. **Fast**: Tests should run quickly
2. **Independent**: Tests should not depend on each other
3. **Repeatable**: Same results every time
4. **Self-Validating**: Clear pass/fail
5. **Timely**: Written before or with production code

### **Test Organization**
```
tests/
├── unit/
│   ├── services/
│   ├── api/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
├── e2e/
│   ├── chat-workflow/
│   └── admin-workflow/
└── performance/
    ├── load/
    └── memory/
```

### **Mock Strategy**
- **External APIs**: Always mock
- **Database**: Use in-memory DB for unit tests
- **File System**: Mock file operations
- **Time**: Mock time-dependent functions

---

**🎯 Ziel**: 100% getestete, zuverlässige Anwendung mit automatisierter Qualitätssicherung für die Bachelorarbeit.

*Letzte Aktualisierung: 2025-07-04 12:00*