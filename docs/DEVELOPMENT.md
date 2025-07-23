# 🛠️ StreamWorks-KI Development Guide

## Development Setup

### Prerequisites

#### System Requirements
- Python 3.9+ with pip
- Node.js 18+ with npm
- Docker Desktop
- Git
- VS Code (recommended) or your preferred IDE

#### Required Services
- PostgreSQL 15 (via Docker)
- Ollama with Mistral 7B model
- Redis (optional, for caching)

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Lukasge02/Streamworks-KI.git
   cd Streamworks-KI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Setup environment
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Setup environment
   cp .env.example .env
   # Edit .env if needed
   ```

4. **Database Setup**
   ```bash
   # Start PostgreSQL
   docker run --name streamworks-postgres \
     -e POSTGRES_USER=streamworks \
     -e POSTGRES_PASSWORD=streamworks_secure_2025 \
     -e POSTGRES_DB=streamworks_ki \
     -p 5432:5432 -d postgres:15
   
   # Run migrations (from backend directory)
   python scripts/migrate_to_postgres.py
   ```

5. **Start Ollama**
   ```bash
   ollama serve
   # In another terminal:
   ollama pull mistral:7b-instruct
   ```

## Code Standards & Guidelines

### Python Backend Standards

#### Code Style
- Follow PEP 8 with Black formatter
- Maximum line length: 100 characters
- Use type hints for all functions
- Docstrings for all public functions/classes

#### Example:
```python
from typing import List, Optional
from pydantic import BaseModel

class DocumentService:
    """Service for document processing operations."""
    
    async def process_document(
        self,
        file_path: str,
        options: Optional[dict] = None
    ) -> ProcessingResult:
        """
        Process a document for RAG indexing.
        
        Args:
            file_path: Path to the document
            options: Optional processing configuration
            
        Returns:
            ProcessingResult with status and metadata
            
        Raises:
            FileNotFoundError: If document doesn't exist
            ProcessingError: If processing fails
        """
        # Implementation
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# Local application imports
from app.core.config import settings
from app.services.rag_service import RAGService
```

### TypeScript Frontend Standards

#### Code Style
- ESLint + Prettier configuration
- Functional components with hooks
- Comprehensive TypeScript types
- No `any` types without justification

#### Example:
```typescript
import React, { useState, useCallback } from 'react';

interface DocumentUploadProps {
  onUpload: (file: File) => Promise<void>;
  maxSize?: number;
  allowedTypes?: string[];
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  maxSize = 50 * 1024 * 1024,
  allowedTypes = ['.pdf', '.txt', '.md']
}) => {
  const [uploading, setUploading] = useState(false);
  
  const handleUpload = useCallback(async (file: File) => {
    // Validation and upload logic
  }, [onUpload]);
  
  return (
    // Component JSX
  );
};
```

### Git Workflow

#### Branch Naming
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

#### Commit Messages
```bash
# Format: <type>(<scope>): <subject>

feat(qa): Add streaming response support
fix(upload): Handle large file uploads correctly
docs(api): Update endpoint documentation
refactor(services): Simplify RAG service architecture
test(documents): Add batch processing tests
```

## Testing Strategy

### Backend Testing

#### Unit Tests
```python
# tests/unit/test_document_service.py
import pytest
from app.services.document_service import DocumentService

@pytest.mark.asyncio
async def test_pdf_conversion():
    service = DocumentService()
    result = await service.convert_pdf_to_markdown("test.pdf", b"content")
    assert result.success
    assert result.markdown_content
```

#### Integration Tests
```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_document_service.py
```

### Frontend Testing

#### Component Tests
```typescript
// tests/components/DocumentUpload.test.tsx
import { render, screen } from '@testing-library/react';
import { DocumentUpload } from '@/components/DocumentUpload';

describe('DocumentUpload', () => {
  it('renders upload button', () => {
    render(<DocumentUpload onUpload={jest.fn()} />);
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
  });
});
```

#### Run Tests
```bash
# All tests
npm test

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Debugging & Troubleshooting

### Common Issues

#### Backend Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   docker ps | grep postgres
   
   # Check connection
   psql -h localhost -U streamworks -d streamworks_ki
   ```

2. **Ollama Not Responding**
   ```bash
   # Check Ollama service
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   ollama serve
   ```

3. **Import Errors**
   ```bash
   # Ensure you're in virtual environment
   which python  # Should show venv path
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

#### Frontend Issues

1. **Build Errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **TypeScript Errors**
   ```bash
   # Check for type issues
   npm run type-check
   ```

### Debug Configuration

#### VS Code Launch Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Frontend: React",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

### Logging

#### Backend Logging
```python
import logging
logger = logging.getLogger(__name__)

# Debug logging
logger.debug(f"Processing document: {file_path}")

# Info logging
logger.info(f"Document processed successfully: {doc_id}")

# Error logging
logger.error(f"Processing failed: {e}", exc_info=True)
```

#### Frontend Logging
```typescript
// Development logging
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
}

// Error logging
console.error('API Error:', error);
```

## Performance Profiling

### Backend Profiling
```python
# Using cProfile
python -m cProfile -o profile.stats app.main:app

# Analyze results
import pstats
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative').print_stats(20)
```

### Frontend Profiling
- Use React DevTools Profiler
- Chrome DevTools Performance tab
- Lighthouse for overall performance

## Environment Variables

### Backend (.env)
```env
# Application
APP_NAME=Streamworks-KI
DEBUG=true
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=streamworks_ki
POSTGRES_USER=streamworks
POSTGRES_PASSWORD=streamworks_secure_2025

# AI/ML
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Storage
DATA_PATH=./data
UPLOAD_MAX_SIZE=52428800
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_ANALYTICS=false
```