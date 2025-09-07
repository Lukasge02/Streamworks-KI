# StreamWorks Document Management System

> **Enterprise-Grade Document Management with Hierarchical Organization**  
> Modern FastAPI backend + Next.js frontend for scalable document workflows

[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.18-000000?style=flat&logo=next.js)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=flat&logo=postgresql)](https://supabase.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)

---

## 🎯 **What is StreamWorks?**

StreamWorks is a production-ready document management system designed for enterprise environments requiring:

- **Hierarchical Folder Structure** - Organize documents in nested folders like a traditional file system
- **Enterprise File Handling** - Upload, preview, download, and manage large document collections
- **RESTful API Architecture** - Clean, documented APIs for seamless integration
- **Real-time Operations** - Instant feedback and bulk operations support
- **Modern Web Interface** - Responsive React-based frontend with dark/light themes

### 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   Next.js 14    │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   TypeScript     │    │   Python 3.11   │    │   (Supabase)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 **Quick Start**

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL** database (Supabase recommended)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd StreamWorks-KI
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start backend
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🏛️ **System Architecture**

### **Backend Stack (FastAPI)**
- **Framework**: FastAPI 2.0 with async/await throughout
- **Database**: PostgreSQL with SQLAlchemy ORM + Alembic migrations  
- **Authentication**: JWT-based (ready for integration)
- **File Storage**: Local filesystem with configurable paths
- **API Design**: RESTful with comprehensive OpenAPI documentation

### **Frontend Stack (Next.js 14)**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **UI Library**: Headless UI + Lucide React icons
- **Styling**: TailwindCSS with custom design system
- **State Management**: React Query for server state
- **File Handling**: React Dropzone with progress tracking

### **Database Schema**
```sql
-- Hierarchical folder structure
folders: id, name, parent_id, description, created_at, updated_at

-- Documents with metadata  
documents: id, folder_id, filename, original_name, file_path, 
          file_size, mime_type, created_at, updated_at
```

---

## 🎨 **Key Features**

### **📁 Document Management**
- **Hierarchical Organization** - Unlimited nested folder depth
- **Bulk Operations** - Upload multiple files, create folders in batches
- **File Metadata** - Automatic MIME type detection, size tracking
- **Search & Filter** - Find documents by name, type, or folder

### **🔧 Enterprise Features**  
- **Health Monitoring** - Comprehensive health checks and system info
- **Error Handling** - Graceful error responses with detailed logging
- **CORS Configuration** - Production-ready cross-origin setup
- **Database Migrations** - Version-controlled schema changes

### **💻 Developer Experience**
- **Auto-Generated Docs** - Interactive API documentation at `/docs`
- **Type Safety** - Full TypeScript coverage in frontend
- **Hot Reload** - Development servers with instant feedback
- **Clean Architecture** - Separation of concerns, testable components

---

## 📊 **API Endpoints**

### **Folder Management**
```http
GET    /folders/               # List all folders with hierarchy
POST   /folders/               # Create new folder
GET    /folders/{id}           # Get folder details
PUT    /folders/{id}           # Update folder
DELETE /folders/{id}           # Delete folder (and contents)
GET    /folders/{id}/documents # List documents in folder
```

### **Document Management**
```http
GET    /documents/           # List all documents
POST   /documents/upload     # Upload new document(s)
GET    /documents/{id}       # Get document metadata
GET    /documents/{id}/download # Download document file
DELETE /documents/{id}       # Delete document
```

### **System Endpoints**
```http
GET /health                 # Basic health check
GET /health/database        # Database connectivity check  
GET /health/detailed        # Comprehensive system status
GET /system/info           # System information and statistics
```

---

## 🛠️ **Development**

### **Project Structure**
```
StreamWorks-KI/
├── backend/                 # FastAPI Backend
│   ├── routers/            # API route definitions
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic layer
│   ├── database.py         # Database configuration
│   └── main.py            # Application entry point
├── frontend/               # Next.js Frontend
│   ├── src/app/           # App Router pages
│   ├── src/components/    # React components
│   ├── src/services/      # API client functions
│   ├── src/types/         # TypeScript definitions
│   └── src/utils/         # Utility functions
└── docs/                  # Project documentation
```

### **Key Technologies**

**Backend Dependencies:**
- `fastapi[all]` - Web framework with automatic docs
- `sqlalchemy[asyncio]` - Async ORM for PostgreSQL
- `asyncpg` - High-performance PostgreSQL driver  
- `pydantic` - Data validation and serialization
- `python-multipart` - File upload support

**Frontend Dependencies:**
- `next` - React framework with SSR/SSG
- `@tanstack/react-query` - Server state management
- `@headlessui/react` - Accessible UI components
- `tailwindcss` - Utility-first CSS framework
- `lucide-react` - Modern icon library

---

## 🚀 **Deployment**

### **Environment Configuration**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
STORAGE_PATH=/app/storage/documents
LOG_LEVEL=INFO

# Frontend (.env.local)  
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Production Checklist**
- [ ] Configure production database credentials
- [ ] Set up file storage (local/S3/GCS)
- [ ] Configure CORS origins for production domains
- [ ] Set up SSL certificates for HTTPS
- [ ] Configure monitoring and logging
- [ ] Set up database backups

---

## 📈 **Performance & Scalability**

### **Current Metrics**
- **Response Time**: <100ms for typical operations
- **Database**: Optimized queries with proper indexing
- **File Handling**: Streaming uploads/downloads for large files
- **Frontend**: Code splitting and lazy loading

### **Scaling Considerations**
- **Database**: PostgreSQL handles enterprise workloads
- **File Storage**: Can be configured for cloud storage
- **Caching**: Ready for Redis integration
- **Load Balancing**: Stateless design supports horizontal scaling

---

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

---

## 📄 **License**

This project is part of a Bachelor Thesis and is available for educational and commercial use.

---

## 🔗 **Links**

- **Live Demo**: [Coming Soon]
- **API Documentation**: http://localhost:8000/docs (when running)
- **Issue Tracker**: [GitHub Issues]
- **Thesis Documentation**: [Academic Repository]

---

**Built with ❤️ for modern document management workflows**