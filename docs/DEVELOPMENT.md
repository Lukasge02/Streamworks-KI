# 🛠️ Development Guide

> **Entwickler-Dokumentation für Streamworks-KI RAG System**  
> Code-Struktur, Best Practices und Contributing Guidelines

---

## 🎯 **Developer Overview**

Streamworks-KI ist ein **modernes, enterprise-grade RAG System** mit sauberer Architektur und entwicklerfreundlichen Patterns:

- **🏗️ Clean Architecture** - Service Layer Pattern mit klarer Trennung
- **⚡ Async-First Design** - Durchgehend async/await für optimale Performance
- **🔒 Type Safety** - Vollständige TypeScript/Pydantic Integration
- **🧪 Test Coverage** - Umfassende Test-Suite für alle Components
- **📊 Modern Stack** - FastAPI, Next.js 14, ChromaDB, PostgreSQL

---

## 🏗️ **Code Architecture**

### **Backend Structure (Python/FastAPI)**

```
backend/
├── main.py                  # FastAPI Application Entry Point
├── config.py               # Configuration Management
├── database.py             # Database Connection & Session Management
│
├── models/                 # SQLAlchemy Data Models
│   └── core.py            # Folder, Document, User models
│
├── schemas/               # Pydantic Request/Response Models
│   └── core.py           # API Schema Definitions
│
├── services/             # Business Logic Layer (16+ Services)
│   ├── document_service.py      # Document CRUD Operations
│   ├── folder_service.py        # Hierarchical Folder Management
│   ├── chat_service.py          # Chat Session Management
│   ├── docling_ingest.py        # Layout-aware Document Processing
│   ├── embeddings.py            # Embedding Generation Service
│   ├── vectorstore.py           # ChromaDB Vector Operations
│   ├── unified_rag_service.py   # RAG Pipeline Orchestration
│   ├── enterprise_cache.py     # Multi-level Caching System
│   ├── upload_job_manager.py    # Async Upload Processing
│   ├── websocket_manager.py     # Real-time Communication Hub
│   └── performance_monitor.py   # System Performance Tracking
│
├── routers/              # API Route Handlers
│   ├── folders.py        # Folder Management API
│   ├── documents.py      # Document Operations API
│   ├── chat.py          # Chat & RAG API
│   └── websockets.py    # WebSocket Endpoints
│
├── middleware/           # Custom Middleware
│   └── security.py      # Security & Authentication Middleware
│
└── requirements.txt     # Python Dependencies
```

### **Frontend Structure (TypeScript/Next.js)**

```
frontend/src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root Layout with Providers
│   ├── page.tsx           # Landing Page
│   ├── chat/              # Chat Interface Routes
│   ├── documents/         # Document Management Routes
│   └── dashboard/         # System Monitoring Dashboard
│
├── components/            # React Components (66+)
│   ├── chat/             # Chat System Components
│   │   ├── ChatInterface.tsx          # Main Chat Interface
│   │   ├── EnterpriseInputArea.tsx    # Advanced Input with Features
│   │   ├── MessageActions.tsx         # Message Action Buttons
│   │   └── SourcePreviewModal.tsx     # Source Citation Preview
│   ├── documents/        # Document Management Components
│   ├── dashboard/        # Monitoring & Analytics
│   ├── layout/          # Layout Components (Header, Sidebar)
│   └── ui/              # Reusable UI Components
│
├── services/            # API Client Layer
│   ├── localChatApiService.ts    # Chat API Client
│   ├── documentApiService.ts     # Document API Client
│   └── websocketService.ts       # WebSocket Client
│
├── hooks/               # Custom React Hooks
│   ├── useChatStorage.ts         # Chat State Management
│   ├── useDocuments.ts           # Document State Management
│   ├── useWebSocket.ts           # WebSocket Integration
│   └── useFormValidation.ts      # Form Validation Logic
│
├── types/               # TypeScript Type Definitions
│   ├── api.ts           # API Response Types
│   ├── chat.ts          # Chat-related Types
│   └── document.ts      # Document-related Types
│
└── utils/               # Utility Functions
    ├── api.ts           # API Helper Functions
    ├── formatting.ts    # Data Formatting Utils
    └── validation.ts    # Input Validation Utils
```

---

## 🔧 **Development Setup**

### **Prerequisites**
- **Python 3.11+** with pip and virtualenv
- **Node.js 18+** with npm
- **PostgreSQL** (optional, uses SQLite by default)
- **VS Code** (empfohlen mit Extensions)

### **Recommended VS Code Extensions**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylance", 
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-toolsai.jupyter",
    "charliermarsh.ruff"
  ]
}
```

### **Development Environment Setup**

#### **1. Backend Development**
```bash
cd backend

# Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Dependencies (with dev tools)
pip install -r requirements.txt
pip install pytest black ruff mypy  # Dev dependencies

# Environment Configuration
cp .env.example .env
# Edit .env with your settings

# Start development server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **2. Frontend Development**
```bash
cd frontend

# Dependencies
npm install

# Development server
npm run dev

# Available scripts
npm run build          # Production build
npm run type-check     # TypeScript checking
npm run lint           # ESLint checking  
npm run test           # Run tests
```

---

## 🧩 **Code Patterns & Best Practices**

### **Backend Patterns**

#### **Service Layer Pattern**
```python
# services/base_service.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema')
UpdateSchema = TypeVar('UpdateSchema')

class BaseService(ABC, Generic[T, CreateSchema, UpdateSchema]):
    """Base service with common CRUD operations"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    async def create(self, db: AsyncSession, obj_in: CreateSchema) -> T:
        """Create new entity"""
        db_obj = self.model_class(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, db: AsyncSession, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        result = await db.execute(select(self.model_class).where(self.model_class.id == id))
        return result.scalar_one_or_none()
    
    async def update(self, db: AsyncSession, db_obj: T, obj_in: UpdateSchema) -> T:
        """Update existing entity"""
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

# Concrete service implementation
class DocumentService(BaseService[Document, DocumentCreate, DocumentUpdate]):
    def __init__(self):
        super().__init__(Document)
        
    async def get_by_folder(self, db: AsyncSession, folder_id: UUID) -> List[Document]:
        """Get documents by folder - specific business logic"""
        result = await db.execute(
            select(Document)
            .where(Document.folder_id == folder_id)
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()
```

#### **Dependency Injection Pattern**
```python
# dependencies.py
from functools import lru_cache
from services.document_service import DocumentService
from services.embeddings import EmbeddingService
from services.vectorstore import VectorStoreService

@lru_cache()
def get_document_service() -> DocumentService:
    return DocumentService()

@lru_cache() 
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

@lru_cache()
def get_vectorstore_service() -> VectorStoreService:
    return VectorStoreService()

# Usage in routes
from fastapi import Depends

async def create_document(
    file: UploadFile,
    folder_id: Optional[UUID] = None,
    document_service: DocumentService = Depends(get_document_service),
    db: AsyncSession = Depends(get_database)
):
    return await document_service.create_from_upload(db, file, folder_id)
```

#### **Async Context Managers**
```python
# services/upload_job_manager.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class UploadJobManager:
    @asynccontextmanager
    async def track_upload_progress(
        self, 
        job_id: str, 
        websocket_manager: WebSocketManager
    ) -> AsyncGenerator[ProgressTracker, None]:
        """Context manager for tracking upload progress"""
        
        tracker = ProgressTracker(job_id, websocket_manager)
        
        try:
            await tracker.start()
            yield tracker
            
        except Exception as e:
            await tracker.error(str(e))
            raise
            
        finally:
            await tracker.complete()

# Usage
async def process_document(file: UploadFile, job_id: str):
    async with upload_manager.track_upload_progress(job_id, websocket_manager) as progress:
        await progress.update("Validating file...", 10)
        
        # Process file
        result = await docling_service.process(file)
        await progress.update("Generating embeddings...", 50)
        
        # Generate embeddings
        embeddings = await embedding_service.generate(result.chunks)
        await progress.update("Storing in vector database...", 90)
        
        # Store in vector database
        await vectorstore.store(embeddings)
```

### **Frontend Patterns**

#### **Custom Hook Pattern**
```typescript
// hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentApiService } from '../services/documentApiService';
import type { Document, DocumentFilter, UploadProgress } from '../types';

export const useDocuments = (folderId?: string, filters?: DocumentFilter) => {
  const queryClient = useQueryClient();

  // Query for documents list
  const documentsQuery = useQuery({
    queryKey: ['documents', folderId, filters],
    queryFn: () => documentApiService.getDocuments(folderId, filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  // Mutation for document upload
  const uploadMutation = useMutation({
    mutationFn: ({ files, folderId }: { files: FileList; folderId?: string }) =>
      documentApiService.uploadDocuments(files, folderId),
    onSuccess: () => {
      // Invalidate and refetch documents
      queryClient.invalidateQueries(['documents']);
    },
  });

  // Mutation for document deletion
  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => documentApiService.deleteDocument(documentId),
    onMutate: async (documentId) => {
      // Optimistic update
      await queryClient.cancelQueries(['documents']);
      const previousDocuments = queryClient.getQueryData<Document[]>(['documents']);
      
      queryClient.setQueryData<Document[]>(['documents'], (old) =>
        old?.filter((doc) => doc.id !== documentId) ?? []
      );

      return { previousDocuments };
    },
    onError: (err, documentId, context) => {
      // Rollback on error
      queryClient.setQueryData(['documents'], context?.previousDocuments);
    },
    onSettled: () => {
      queryClient.invalidateQueries(['documents']);
    },
  });

  return {
    documents: documentsQuery.data ?? [],
    isLoading: documentsQuery.isLoading,
    error: documentsQuery.error,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isLoading,
    isDeleting: deleteMutation.isLoading,
  };
};
```

#### **Component Composition Pattern**
```typescript
// components/documents/DocumentGrid.tsx
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DocumentCard } from './DocumentCard';
import { LoadingSkeleton } from '../ui/LoadingSkeleton';
import { EmptyState } from '../ui/EmptyState';
import type { Document } from '../../types';

interface DocumentGridProps {
  documents: Document[];
  isLoading: boolean;
  onDocumentSelect: (document: Document) => void;
  onDocumentDelete: (documentId: string) => void;
  selectedDocuments?: string[];
}

export const DocumentGrid: React.FC<DocumentGridProps> = ({
  documents,
  isLoading,
  onDocumentSelect,
  onDocumentDelete,
  selectedDocuments = [],
}) => {
  if (isLoading) {
    return <LoadingSkeleton count={12} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4" />;
  }

  if (!documents.length) {
    return (
      <EmptyState
        icon="FileText"
        title="Keine Dokumente vorhanden"
        description="Laden Sie Ihr erstes Dokument hoch, um zu beginnen."
        action={{
          label: "Dokument hochladen",
          onClick: () => {/* Handle upload */}
        }}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <AnimatePresence>
        {documents.map((document) => (
          <motion.div
            key={document.id}
            layout
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
          >
            <DocumentCard
              document={document}
              isSelected={selectedDocuments.includes(document.id)}
              onClick={() => onDocumentSelect(document)}
              onDelete={() => onDocumentDelete(document.id)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
```

#### **Form Validation Hook**
```typescript
// hooks/useFormValidation.ts
import { useState, useCallback } from 'react';
import { z } from 'zod';

type ValidationResult<T> = {
  isValid: boolean;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
};

export const useFormValidation = <T extends Record<string, any>>(
  schema: z.ZodSchema<T>,
  initialValues: T
) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const validate = useCallback((valuesToValidate: T): ValidationResult<T> => {
    try {
      schema.parse(valuesToValidate);
      return { isValid: true, errors: {}, touched };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors = error.flatten().fieldErrors;
        const errorMap: Partial<Record<keyof T, string>> = {};
        
        for (const [field, messages] of Object.entries(fieldErrors)) {
          errorMap[field as keyof T] = messages?.[0] ?? 'Invalid value';
        }
        
        return { isValid: false, errors: errorMap, touched };
      }
      return { isValid: false, errors: { root: 'Validation failed' } as any, touched };
    }
  }, [schema, touched]);

  const setValue = useCallback((field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }));
    setTouched(prev => ({ ...prev, [field]: true }));
    
    // Validate single field
    const newValues = { ...values, [field]: value };
    const validation = validate(newValues);
    setErrors(validation.errors);
  }, [values, validate]);

  const validateForm = useCallback(() => {
    const validation = validate(values);
    setErrors(validation.errors);
    return validation.isValid;
  }, [values, validate]);

  return {
    values,
    errors,
    touched,
    setValue,
    validateForm,
    isValid: Object.keys(errors).length === 0,
  };
};
```

---

## 🧪 **Testing Strategy**

### **Backend Testing**

#### **Test Structure**
```
backend/tests/
├── unit/                   # Unit Tests
│   ├── services/          # Service Layer Tests
│   ├── models/            # Model Tests  
│   └── utils/             # Utility Function Tests
│
├── integration/           # Integration Tests
│   ├── api/              # API Endpoint Tests
│   ├── database/         # Database Integration Tests
│   └── external/         # External Service Tests
│
└── conftest.py           # Pytest Configuration & Fixtures
```

#### **Service Testing Example**
```python
# tests/unit/services/test_document_service.py
import pytest
from unittest.mock import AsyncMock, patch
from services.document_service import DocumentService
from models.core import Document
from schemas.core import DocumentCreate

@pytest.mark.asyncio
class TestDocumentService:
    
    @pytest.fixture
    def document_service(self):
        return DocumentService()
    
    @pytest.fixture
    def mock_db_session(self):
        session = AsyncMock()
        return session
    
    async def test_create_document(self, document_service, mock_db_session):
        # Arrange
        document_data = DocumentCreate(
            filename="test.pdf",
            original_name="Test Document.pdf",
            folder_id="folder-123",
            file_size=1024,
            mime_type="application/pdf"
        )
        
        expected_document = Document(
            id="doc-123",
            **document_data.dict()
        )
        
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        with patch.object(Document, '__init__', return_value=None):
            with patch.object(document_service, 'model_class', return_value=expected_document):
                # Act
                result = await document_service.create(mock_db_session, document_data)
                
                # Assert
                assert result.filename == document_data.filename
                assert result.folder_id == document_data.folder_id
                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()

    async def test_get_by_folder(self, document_service, mock_db_session):
        # Arrange
        folder_id = "folder-123"
        expected_documents = [
            Document(id="doc-1", filename="doc1.pdf", folder_id=folder_id),
            Document(id="doc-2", filename="doc2.pdf", folder_id=folder_id)
        ]
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = expected_documents
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await document_service.get_by_folder(mock_db_session, folder_id)
        
        # Assert
        assert len(result) == 2
        assert all(doc.folder_id == folder_id for doc in result)
```

#### **API Testing Example**
```python
# tests/integration/api/test_documents_api.py
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
class TestDocumentsAPI:
    
    async def test_get_documents(self, async_client: AsyncClient):
        # Act
        response = await async_client.get("/documents/")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert isinstance(data["documents"], list)
    
    async def test_upload_document(self, async_client: AsyncClient, tmp_path):
        # Arrange
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"PDF content")
        
        files = {"files": ("test.pdf", test_file.open("rb"), "application/pdf")}
        
        # Act
        response = await async_client.post("/documents/upload", files=files)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "upload_job_id" in data
        assert len(data["uploaded_files"]) == 1
```

### **Frontend Testing**

#### **Component Testing with React Testing Library**
```typescript
// components/__tests__/DocumentCard.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DocumentCard } from '../documents/DocumentCard';
import type { Document } from '../../types';

const mockDocument: Document = {
  id: 'doc-123',
  filename: 'test-document.pdf',
  original_name: 'Test Document.pdf',
  file_size: 2048576,
  mime_type: 'application/pdf',
  status: 'processed',
  created_at: '2025-01-01T00:00:00Z',
  folder_id: 'folder-123',
};

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('DocumentCard', () => {
  it('renders document information correctly', () => {
    const mockOnClick = jest.fn();
    const mockOnDelete = jest.fn();

    renderWithProviders(
      <DocumentCard
        document={mockDocument}
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    expect(screen.getByText('2 MB')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', async () => {
    const mockOnClick = jest.fn();
    const mockOnDelete = jest.fn();

    renderWithProviders(
      <DocumentCard
        document={mockDocument}
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByTestId('document-card'));

    await waitFor(() => {
      expect(mockOnClick).toHaveBeenCalledWith(mockDocument);
    });
  });

  it('shows delete confirmation when delete button is clicked', async () => {
    const mockOnClick = jest.fn();
    const mockOnDelete = jest.fn();

    renderWithProviders(
      <DocumentCard
        document={mockDocument}
        onClick={mockOnClick}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByTestId('delete-button'));

    await waitFor(() => {
      expect(screen.getByText('Dokument löschen?')).toBeInTheDocument();
    });
  });
});
```

#### **Hook Testing**
```typescript
// hooks/__tests__/useDocuments.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDocuments } from '../useDocuments';
import { documentApiService } from '../../services/documentApiService';

// Mock API service
jest.mock('../../services/documentApiService');
const mockDocumentApiService = documentApiService as jest.Mocked<typeof documentApiService>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, cacheTime: 0 },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useDocuments', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches documents successfully', async () => {
    const mockDocuments = [
      { id: '1', filename: 'doc1.pdf', status: 'processed' },
      { id: '2', filename: 'doc2.pdf', status: 'processed' },
    ];

    mockDocumentApiService.getDocuments.mockResolvedValue(mockDocuments);

    const { result } = renderHook(() => useDocuments(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.documents).toEqual(mockDocuments);
    expect(result.current.error).toBeNull();
  });

  it('handles upload mutation correctly', async () => {
    mockDocumentApiService.getDocuments.mockResolvedValue([]);
    mockDocumentApiService.uploadDocuments.mockResolvedValue({
      upload_job_id: 'job-123',
      uploaded_files: [{ id: 'doc-1', filename: 'test.pdf' }],
    });

    const { result } = renderHook(() => useDocuments(), {
      wrapper: createWrapper(),
    });

    const mockFiles = new FileList();
    result.current.uploadDocument({ files: mockFiles });

    await waitFor(() => {
      expect(result.current.isUploading).toBe(true);
    });

    expect(mockDocumentApiService.uploadDocuments).toHaveBeenCalledWith(mockFiles, undefined);
  });
});
```

---

## 🔍 **Code Quality Tools**

### **Backend Tools**

#### **Ruff Configuration (pyproject.toml)**
```toml
[tool.ruff]
target-version = "py311"
line-length = 100
exclude = [
    ".git",
    "__pycache__",
    ".venv",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]

ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

#### **MyPy Configuration**
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False
```

### **Frontend Tools**

#### **ESLint Configuration**
```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint", "import"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "import/order": [
      "error",
      {
        "groups": [
          "builtin",
          "external", 
          "internal",
          "parent",
          "sibling",
          "index"
        ],
        "newlines-between": "always"
      }
    ],
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

#### **Prettier Configuration**
```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

---

## 🚀 **Development Workflow**

### **Git Workflow**

#### **Branch Strategy**
```bash
main                    # Production branch
├── develop            # Development branch
├── feature/RAG-123    # Feature branches
├── bugfix/RAG-456     # Bug fix branches  
└── hotfix/RAG-789     # Hotfix branches
```

#### **Commit Convention**
```bash
# Format: type(scope): description

feat(chat): add streaming response support
fix(upload): resolve memory leak in file processing
docs(api): update authentication documentation
refactor(services): extract common base service
test(documents): add integration tests for document API
chore(deps): update dependencies to latest versions
```

### **Code Review Checklist**

#### **Backend Review Checklist**
- [ ] **Architecture** - Follows service layer pattern
- [ ] **Type Safety** - Proper type hints and Pydantic models
- [ ] **Error Handling** - Comprehensive exception handling
- [ ] **Testing** - Unit tests for business logic, integration tests for APIs
- [ ] **Performance** - Async/await used properly, no blocking operations
- [ ] **Security** - Input validation, SQL injection prevention
- [ ] **Documentation** - Docstrings for public methods

#### **Frontend Review Checklist**  
- [ ] **Component Design** - Single responsibility, reusable
- [ ] **Type Safety** - Proper TypeScript types
- [ ] **Performance** - Proper memoization, lazy loading
- [ ] **Accessibility** - ARIA labels, keyboard navigation
- [ ] **Testing** - Component tests, hook tests
- [ ] **State Management** - Proper React Query usage
- [ ] **Styling** - Consistent Tailwind usage

### **CI/CD Pipeline**

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run linting
      run: |
        cd backend
        ruff check .
        mypy .
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linting
      run: |
        cd frontend
        npm run lint
        npm run type-check
    
    - name: Run tests
      run: |
        cd frontend
        npm run test -- --coverage --watchAll=false
    
    - name: Build
      run: |
        cd frontend
        npm run build
```

---

## 🤝 **Contributing Guidelines**

### **Getting Started**
1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch from `develop`
4. **Make** your changes following code standards
5. **Test** your changes thoroughly
6. **Submit** a pull request

### **Pull Request Process**

#### **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated  
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented where necessary
- [ ] Documentation updated if needed
- [ ] No new warnings or errors introduced
```

### **Development Commands**

#### **Backend Commands**
```bash
# Code formatting
ruff format .

# Linting  
ruff check . --fix

# Type checking
mypy .

# Testing
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # With coverage

# Database migrations (if using Alembic)
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

#### **Frontend Commands**
```bash
# Development
npm run dev           # Start dev server
npm run build         # Build for production  
npm run start         # Start production server

# Code Quality
npm run lint          # ESLint checking
npm run lint:fix      # Auto-fix ESLint issues
npm run type-check    # TypeScript checking
npm run format        # Prettier formatting

# Testing
npm run test          # Run tests
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Run tests with coverage
npm run test:e2e      # Run end-to-end tests
```

---

## 📊 **Performance Guidelines**

### **Backend Performance**
- **Database Queries**: Use async queries with proper indexing
- **Caching**: Implement multi-level caching (memory → Redis → DB)
- **File Processing**: Use streaming for large files
- **Concurrency**: Leverage asyncio for I/O operations
- **Memory Management**: Use generators for large datasets

### **Frontend Performance**
- **Bundle Size**: Keep bundle under 1MB gzipped
- **Code Splitting**: Implement route-based and component-based splitting
- **Image Optimization**: Use Next.js Image component
- **State Management**: Minimize unnecessary re-renders
- **Network Requests**: Implement proper caching and prefetching

---

## 🐛 **Debugging Guide**

### **Backend Debugging**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Profile performance
import cProfile
cProfile.run('your_function()')

# Memory profiling
from memory_profiler import profile
@profile
def your_function():
    pass
```

### **Frontend Debugging**
```typescript
// React Developer Tools
// Enable profiler mode in development

// Performance debugging
import { Profiler } from 'react';

const onRenderCallback = (id, phase, actualDuration) => {
  console.log('Component:', id, 'Phase:', phase, 'Duration:', actualDuration);
};

<Profiler id="DocumentGrid" onRender={onRenderCallback}>
  <DocumentGrid />
</Profiler>

// Network debugging
// Use React Query devtools in development
```

---

## 📚 **Resources & References**

### **Documentation**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### **Code Style Guides**
- [Python PEP 8](https://pep8.org/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [React Best Practices](https://react.dev/learn)

---

**🛠️ Development Status**: Enterprise-Ready | Fully Documented | Test-Covered

*Developer Guide Version 2.0.0 - Comprehensive development documentation*