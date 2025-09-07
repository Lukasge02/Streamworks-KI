# 🛠️ Development Guide

> **Complete setup, workflow, and contribution guide for StreamWorks development**

---

## 🚀 **Quick Setup**

### **Prerequisites**
```bash
# Check required versions
python --version    # Python 3.11+
node --version      # Node.js 18+
npm --version       # npm 9+
git --version       # Git 2.30+
```

### **1. Clone Repository**
```bash
git clone https://github.com/your-org/StreamWorks-KI.git
cd StreamWorks-KI
```

### **2. Backend Setup**
```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### **3. Frontend Setup**
```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local if needed
```

### **4. Database Setup**
```bash
# Option A: Local PostgreSQL
createdb streamworks_dev

# Option B: Supabase (recommended)
# 1. Create project at https://supabase.com
# 2. Get connection string from Settings > Database
# 3. Add to backend/.env as DATABASE_URL
```

### **5. Start Development Servers**

**Terminal 1 (Backend):**
```bash
cd backend
python main.py
# Server starts at http://localhost:8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend  
npm run dev
# Server starts at http://localhost:3000
```

### **6. Verify Setup**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🏗️ **Project Structure**

```
StreamWorks-KI/
├── 📁 backend/                 # FastAPI Application
│   ├── 📁 routers/            # API route handlers
│   │   ├── folders.py         # Folder CRUD operations
│   │   └── documents.py       # Document management
│   ├── 📁 models/             # SQLAlchemy models
│   │   └── core.py           # Folder/Document models
│   ├── 📁 schemas/            # Pydantic schemas
│   │   └── core.py           # Request/response models
│   ├── 📁 services/           # Business logic layer
│   │   ├── folder_service.py  # Folder operations
│   │   └── document_service.py # Document operations
│   ├── database.py            # Database configuration
│   ├── main.py               # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env                  # Environment variables
├── 📁 frontend/               # Next.js Application
│   ├── 📁 src/
│   │   ├── 📁 app/           # App Router (Next.js 14)
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Home page
│   │   │   ├── dashboard/     # Dashboard pages
│   │   │   └── upload/        # File upload page
│   │   ├── 📁 components/     # React components
│   │   │   ├── 📁 ui/        # Base UI components
│   │   │   ├── 📁 documents/ # Document components
│   │   │   └── 📁 folders/   # Folder components
│   │   ├── 📁 services/       # API client functions
│   │   ├── 📁 types/         # TypeScript definitions
│   │   └── 📁 utils/         # Helper functions
│   ├── package.json          # Node dependencies
│   └── .env.local           # Environment variables
├── 📁 docs/                  # Project documentation
└── 📁 Export-Streams/        # StreamWorks XML templates
```

---

## 🔧 **Development Workflow**

### **Backend Development**

**Starting Backend:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py            # Start with hot reload
```

**Making Changes:**
1. **Models** (`models/core.py`) - Database schema changes
2. **Schemas** (`schemas/core.py`) - API request/response models
3. **Services** (`services/`) - Business logic implementation
4. **Routers** (`routers/`) - HTTP endpoint definitions

**Example: Adding New Endpoint**
```python
# 1. Update schema (schemas/core.py)
class DocumentSearch(BaseModel):
    query: str = Field(..., min_length=1)
    folder_id: Optional[int] = None

# 2. Add service method (services/document_service.py)  
async def search_documents(db: AsyncSession, query: str, folder_id: Optional[int] = None):
    # Implementation here
    pass

# 3. Add router endpoint (routers/documents.py)
@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(
    query: str,
    folder_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    return await DocumentService.search_documents(db, query, folder_id)
```

### **Frontend Development**

**Starting Frontend:**
```bash
cd frontend
npm run dev  # Start with hot reload
```

**Making Changes:**
1. **Pages** (`src/app/`) - Route-based pages
2. **Components** (`src/components/`) - Reusable UI components
3. **Services** (`src/services/`) - API client functions
4. **Types** (`src/types/`) - TypeScript definitions

**Example: Adding New Component**
```typescript
// 1. Define types (src/types/document.types.ts)
export interface SearchFilters {
  query: string;
  folderId?: number;
}

// 2. Create API service (src/services/document.service.ts)
export const searchDocuments = async (filters: SearchFilters): Promise<Document[]> => {
  const params = new URLSearchParams();
  params.append('query', filters.query);
  if (filters.folderId) params.append('folder_id', filters.folderId.toString());
  
  const response = await fetch(`${API_BASE_URL}/documents/search?${params}`);
  return response.json();
};

// 3. Create component (src/components/documents/DocumentSearch.tsx)
export const DocumentSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const { data: results, isLoading } = useQuery({
    queryKey: ['documents', 'search', query],
    queryFn: () => searchDocuments({ query }),
    enabled: query.length > 0
  });
  
  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documents..."
      />
      {isLoading && <Spinner />}
      {results?.map(doc => <DocumentCard key={doc.id} document={doc} />)}
    </div>
  );
};
```

---

## 🧪 **Testing Strategy**

### **Backend Testing**

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

**Test Structure:**
```python
# tests/test_folders.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_folder():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/folders/", json={
            "name": "Test Folder",
            "description": "Test folder description"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Folder"
```

### **Frontend Testing**

```bash
# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

**Test Structure:**
```typescript
// src/components/__tests__/DocumentCard.test.tsx
import { render, screen } from '@testing-library/react';
import { DocumentCard } from '../DocumentCard';

const mockDocument = {
  id: 1,
  filename: 'test.pdf',
  file_size: 1024,
  created_at: '2025-09-05T10:00:00Z'
};

test('renders document card with filename', () => {
  render(<DocumentCard document={mockDocument} />);
  expect(screen.getByText('test.pdf')).toBeInTheDocument();
});
```

---

## 🔍 **Code Quality & Standards**

### **Backend Code Quality**

**Linting & Formatting:**
```bash
# Install tools
pip install ruff mypy

# Run linter
ruff check backend/

# Run type checker
mypy backend/

# Auto-format code
ruff format backend/
```

**Code Standards:**
- **PEP 8** compliance via Ruff
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Async/await** for I/O operations

### **Frontend Code Quality**

**Linting & Formatting:**
```bash
# Run linter
npm run lint

# Run type checker
npm run type-check

# Auto-format code
npm run format
```

**Code Standards:**
- **ESLint** with React rules
- **TypeScript strict mode**
- **Prettier** for consistent formatting
- **React best practices**

---

## 🔄 **Git Workflow**

### **Branch Strategy**
```bash
main        # Production branch
develop     # Development branch  
feature/*   # Feature branches
hotfix/*    # Emergency fixes
```

### **Development Process**

```bash
# 1. Create feature branch
git checkout -b feature/document-search

# 2. Make changes and commit
git add .
git commit -m "feat: add document search functionality

- Add search endpoint to documents router
- Implement search service with filters  
- Add SearchFilters TypeScript interface
- Create DocumentSearch React component"

# 3. Push and create PR
git push origin feature/document-search
# Create Pull Request on GitHub
```

### **Commit Message Format**
```
type(scope): brief description

Optional longer description explaining the change.

- Bullet points for detailed changes
- Reference issue numbers: Fixes #123
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes  
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

---

## 🚀 **Deployment**

### **Development Deployment**
```bash
# Using Docker Compose
docker-compose up -d

# Manual deployment
# Backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend  
cd frontend && npm run build && npm start
```

### **Production Deployment**

**Environment Variables:**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@prod-host:5432/streamworks
STORAGE_PATH=/app/storage/documents
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Docker Production:**
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile  
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🐛 **Debugging & Troubleshooting**

### **Common Backend Issues**

**Database Connection Error:**
```bash
# Check connection string
echo $DATABASE_URL

# Test connection
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('your-db-url')
    print('Connected!')
    await conn.close()
asyncio.run(test())
"
```

**Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install in development mode  
pip install -e .
```

### **Common Frontend Issues**

**Module Not Found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues:**
```typescript
// Check API URL configuration
console.log('API Base URL:', process.env.NEXT_PUBLIC_API_URL);

// Test API connectivity
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log);
```

### **Performance Debugging**

**Backend Profiling:**
```python
# Add timing middleware
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Frontend Profiling:**
```typescript
// React DevTools Profiler
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log(`Component ${id} took ${actualDuration}ms to render`);
}

<Profiler id="DocumentManager" onRender={onRenderCallback}>
  <DocumentManager />
</Profiler>
```

---

## 🤝 **Contributing Guidelines**

### **Before Contributing**
1. **Read** the codebase to understand the architecture
2. **Check** existing issues and PRs  
3. **Create** an issue for new features
4. **Follow** the coding standards

### **Pull Request Process**
1. **Fork** the repository
2. **Create** feature branch from `develop`
3. **Write** tests for new functionality
4. **Update** documentation if needed
5. **Ensure** all tests pass
6. **Create** PR with clear description

### **Code Review Checklist**
- [ ] Code follows style guidelines
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] No breaking changes without migration path
- [ ] Performance impact considered
- [ ] Security implications reviewed

---

## 📚 **Resources**

### **Documentation Links**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Query Documentation](https://tanstack.com/query/latest)

### **Development Tools**
- **VS Code Extensions**: Python, TypeScript, Prettier, ESLint
- **Database Tools**: pgAdmin, DBeaver, Supabase Dashboard
- **API Testing**: Postman, Insomnia, curl
- **Git GUI**: GitKraken, SourceTree, GitHub Desktop

---

**Happy coding! 🚀**