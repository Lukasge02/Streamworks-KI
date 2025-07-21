# ⚙️ Backend - StreamWorks-KI
**FastAPI + Python Enterprise Backend System**

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Tech Stack**
- **FastAPI**: Modern async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0**: Async ORM with comprehensive relationship mapping
- **Pydantic v2**: Data validation with comprehensive type checking
- **ChromaDB**: Vector database for RAG implementation
- **Sentence Transformers**: E5-Multilingual-Large embeddings
- **Mistral 7B**: LLM integration via Ollama
- **SQLite**: Metadata storage with future PostgreSQL migration path

### **Service Architecture**
```python
app/
├── api/v1/                    # REST API Layer
│   ├── qa_api.py             # Q&A System Endpoints
│   ├── training.py           # File Upload & Processing
│   ├── categories.py         # Category Management
│   ├── simple_folders.py     # Folder CRUD Operations
│   └── files_enterprise.py   # Enterprise File Operations
├── services/                  # Business Logic Layer
│   ├── rag_service.py        # RAG Implementation
│   ├── mistral_llm_service.py # LLM Integration Service
│   ├── training_service.py   # Document Processing Service
│   └── enterprise_file_manager.py # File Management Service
├── models/                    # Data Layer
│   ├── database.py           # SQLAlchemy Models
│   └── pydantic_models.py    # API Request/Response Schemas
├── core/                     # Infrastructure Layer
│   ├── config.py             # Configuration Management
│   ├── async_manager.py      # Background Task Management
│   └── base_service.py       # Base Service Class
└── middleware/               # Request/Response Middleware
    └── monitoring.py         # Performance & Request Monitoring
```

---

## 🔧 **CORE SERVICES**

### **RAG Service Implementation**
```python
class RAGService:
    """Enterprise RAG implementation with ChromaDB and E5 embeddings"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
        self.chroma_client = chromadb.PersistentClient(path="./data/vector_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="streamworks_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def semantic_search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Perform semantic search with relevance scoring"""
        query_embedding = self.embedding_model.encode([f"query: {query}"])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=limit,
            include=['documents', 'metadatas', 'distances']
        )
        
        return self._process_search_results(results, query)
    
    async def generate_response(self, query: str, context: List[str]) -> str:
        """Generate contextual response using Mistral 7B"""
        context_text = "\n\n".join(context)
        
        prompt = f"""Kontext aus StreamWorks Dokumentation:
{context_text}

Frage: {query}

Antworte auf Deutsch, basierend auf dem bereitgestellten Kontext."""
        
        return await self.mistral_service.generate_response(prompt)
```

### **Enterprise File Manager**
```python
class EnterpriseFileManager:
    """Comprehensive file management with hierarchical structure"""
    
    async def save_file(
        self, 
        file_content: bytes, 
        filename: str,
        category_slug: str,
        folder_id: Optional[str] = None
    ) -> FileRecord:
        """Save file with proper organization and metadata"""
        
        # Create directory structure
        storage_path = self._build_storage_path(category_slug, folder_id)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename and save file
        unique_filename = self._generate_unique_filename(filename)
        file_path = storage_path / unique_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Create database record
        file_record = await self._create_file_record(
            filename=filename,
            file_path=str(file_path),
            file_size=len(file_content),
            folder_id=folder_id
        )
        
        # Schedule background processing
        await self.async_manager.schedule_task(
            "process_document",
            file_id=file_record.id
        )
        
        return file_record
    
    async def delete_file(self, file_id: str) -> bool:
        """Complete file deletion (database + filesystem + vector store)"""
        file_record = await self._get_file_record(file_id)
        
        # Remove from vector database
        await self.rag_service.remove_document(file_id)
        
        # Remove from filesystem
        if file_record.file_path and Path(file_record.file_path).exists():
            Path(file_record.file_path).unlink()
        
        # Remove from database (soft delete)
        await self._soft_delete_file(file_id)
        
        return True
```

### **Background Task Management**
```python
class AsyncTaskManager:
    """Enterprise background task management"""
    
    def __init__(self):
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.worker_tasks: List[asyncio.Task] = []
        self.is_running = False
    
    async def schedule_task(self, task_type: str, **kwargs) -> str:
        """Schedule background task with unique ID"""
        task_id = str(uuid.uuid4())
        
        task_data = {
            "id": task_id,
            "type": task_type,
            "params": kwargs,
            "created_at": datetime.now(timezone.utc),
            "status": "pending"
        }
        
        await self.task_queue.put(task_data)
        logger.info(f"Task {task_id} scheduled: {task_type}")
        
        return task_id
    
    async def process_document(self, file_id: str) -> None:
        """Process uploaded document for RAG indexing"""
        try:
            file_record = await self.get_file_record(file_id)
            
            # Read and process file content
            content = await self.extract_text_content(file_record.file_path)
            
            # Create embeddings and store in vector database
            await self.rag_service.index_document(
                document_id=file_id,
                content=content,
                metadata={
                    "filename": file_record.filename,
                    "category": file_record.category_slug,
                    "folder_id": file_record.folder_id
                }
            )
            
            # Update file status
            await self.update_file_status(file_id, "indexed")
            
            logger.info(f"Document {file_id} successfully indexed")
            
        except Exception as e:
            logger.error(f"Document processing failed for {file_id}: {e}")
            await self.update_file_status(file_id, "error", str(e))
```

---

## 🗄️ **DATABASE ARCHITECTURE**

### **SQLAlchemy Models**
```python
class DocumentCategory(Base):
    __tablename__ = "document_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    folders = relationship("DocumentFolder", back_populates="category", cascade="all, delete-orphan")
    files = relationship("TrainingFileV2", back_populates="category", cascade="all, delete-orphan")

class DocumentFolder(Base):
    __tablename__ = "document_folders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("document_categories.id"), nullable=False, index=True)
    parent_folder_id = Column(String(36), ForeignKey("document_folders.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("DocumentCategory", back_populates="folders")
    parent_folder = relationship("DocumentFolder", remote_side=[id])
    subfolders = relationship("DocumentFolder", back_populates="parent_folder", cascade="all, delete-orphan")
    files = relationship("TrainingFileV2", back_populates="folder", cascade="all, delete-orphan")
```

### **Database Operations Pattern**
```python
async def get_folders_by_category(
    category_slug: str, 
    db: AsyncSession,
    include_inactive: bool = False
) -> List[DocumentFolder]:
    """Get folders with optimized query and proper error handling"""
    
    query = (
        select(DocumentFolder)
        .join(DocumentCategory)
        .where(DocumentCategory.slug == category_slug)
        .options(selectinload(DocumentFolder.files))
    )
    
    if not include_inactive:
        query = query.where(DocumentFolder.is_active == True)
    
    result = await db.execute(query.order_by(DocumentFolder.sort_order, DocumentFolder.name))
    return result.scalars().all()
```

---

## 🔌 **API DESIGN PATTERNS**

### **FastAPI Endpoint Pattern**
```python
@router.post("/folders", response_model=CreateFolderResponse)
async def create_folder(
    category_slug: str,
    folder_data: CreateFolderRequest,
    db: AsyncSession = Depends(get_db)
) -> CreateFolderResponse:
    """Create new folder with comprehensive validation"""
    
    try:
        # Validate category exists
        category = await get_category_by_slug(category_slug, db)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Validate folder name uniqueness
        existing_folder = await get_folder_by_name(
            category_slug, folder_data.name, db
        )
        if existing_folder:
            raise HTTPException(
                status_code=409, 
                detail="Folder name already exists in this category"
            )
        
        # Create folder
        folder = await create_folder_in_category(
            category_id=category.id,
            folder_data=folder_data,
            db=db
        )
        
        await db.commit()
        
        return CreateFolderResponse(
            id=folder.id,
            name=folder.name,
            slug=folder.slug,
            message="Folder created successfully"
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Folder creation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during folder creation"
        )
```

### **Pydantic Schema Pattern**
```python
class FileResponse(BaseModel):
    """Comprehensive file response schema"""
    
    id: str
    filename: str
    category_slug: str
    category_name: str
    folder_id: Optional[str] = None
    folder_slug: Optional[str] = None
    folder_name: Optional[str] = None
    file_size: int
    upload_date: datetime
    status: Literal["pending", "processing", "indexed", "error"]
    error_message: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class CreateFolderRequest(BaseModel):
    """Folder creation request with validation"""
    
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Optional[Annotated[str, Field(max_length=1000)]] = None
    parent_folder_id: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Folder name cannot be empty')
        if '/' in v or '\\' in v:
            raise ValueError('Folder name cannot contain path separators')
        return v.strip()
```

---

## 🔄 **ASYNC PATTERNS**

### **Database Session Management**
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency with proper cleanup"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### **Background Task Patterns**
```python
async def process_file_batch(file_ids: List[str]) -> Dict[str, str]:
    """Process multiple files with proper error handling"""
    
    results = {}
    semaphore = asyncio.Semaphore(3)  # Limit concurrent operations
    
    async def process_single_file(file_id: str) -> Tuple[str, str]:
        async with semaphore:
            try:
                await process_document(file_id)
                return file_id, "success"
            except Exception as e:
                logger.error(f"File {file_id} processing failed: {e}")
                return file_id, f"error: {str(e)}"
    
    tasks = [process_single_file(file_id) for file_id in file_ids]
    completed = await asyncio.gather(*tasks, return_exceptions=True)
    
    for file_id, status in completed:
        if not isinstance(status, Exception):
            results[file_id] = status
        else:
            results[file_id] = f"error: {str(status)}"
    
    return results
```

---

## 🔧 **CONFIGURATION & DEPLOYMENT**

### **Settings Management**
```python
class Settings(BaseSettings):
    """Comprehensive configuration with environment variable support"""
    
    # Application
    PROJECT_NAME: str = "StreamWorks-KI API"
    VERSION: str = "4.0.0"
    ENV: Literal["development", "staging", "production"] = "development"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./streamworks_ki.db"
    ECHO_SQL: bool = False
    
    # AI Services
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MISTRAL_MODEL: str = "mistral:7b-instruct"
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"
    
    # File Storage
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".txt", ".md", ".json", ".xml", ".docx", ".xlsx"}
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 60
    BACKGROUND_WORKERS: int = 2
    
    # Security
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
```

### **Production Deployment**
```python
# Production ASGI configuration
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info",
        access_log=True,
        use_colors=True,
        reload=False  # Disabled in production
    )
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **Request Monitoring Middleware**
```python
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Comprehensive request monitoring and metrics collection"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(
                f"Request {request_id}: {request.method} {request.url.path} "
                f"completed in {process_time:.3f}s with status {response.status_code}"
            )
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request {request_id}: {request.method} {request.url.path} "
                f"failed after {process_time:.3f}s: {str(e)}"
            )
            raise
```

---

## 🎯 **DEVELOPMENT GUIDELINES**

### **Code Quality Standards**
- **Type Hints**: All functions must have comprehensive type annotations
- **Error Handling**: Proper exception handling with meaningful error messages
- **Logging**: Structured logging with appropriate log levels
- **Documentation**: Docstrings for all public functions and classes
- **Testing**: Unit tests for critical business logic

### **API Design Principles**
- **RESTful**: Follow REST conventions for resource naming and HTTP methods
- **Validation**: Comprehensive input validation with Pydantic
- **Error Responses**: Consistent error response format across all endpoints
- **Documentation**: Automatic OpenAPI documentation generation
- **Versioning**: API versioning strategy for backward compatibility

---

**🎯 This backend represents enterprise-level Python development with FastAPI, comprehensive async patterns, and robust data management systems.**