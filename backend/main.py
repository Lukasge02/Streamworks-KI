"""
Streamworks Document Management System
Enterprise-grade FastAPI backend with clean architecture
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Import database and routers
from database import init_database, close_database, check_database_health
from routers import folders, documents, websockets, upload_progress_websocket, feature_flags, health
from routers.xml_generator import router as xml_generator
from routers.xml_streams import router as xml_streams
from routers.chat_rag_test import router as chat
# from routers.chat_xml import router as chat_xml
from routers.chat_xml_unified import router as chat_xml_unified  # Unified Chat XML
from routers.langextract_chat import router as langextract_chat  # NEW: LangExtract-First System
from routers.debug import router as debug
from routers.auth import router as auth  # RBAC Auth Router
from routers.performance import router as performance  # Performance Analytics
from routers.rag_metrics import router as rag_metrics  # Enhanced RAG Metrics
from middleware.performance import PerformanceMiddleware
from middleware.cors_error_handler import CORSErrorHandlerMiddleware
from middleware.rag_metrics_middleware import rag_metrics_middleware_func

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        # Startup
        logger.info("🚀 Starting Streamworks Document Management System")
        
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Initialize services
        from services.service_initializer import initialize_services
        await initialize_services()
        logger.info("✅ Services initialized successfully")
        
        # Add startup seed data if needed
        await create_default_folder_if_needed()
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Streamworks")
        from services.service_initializer import shutdown_services
        await shutdown_services()
        await close_database()


async def create_default_folder_if_needed():
    """Create default folder structure if database is empty"""
    try:
        from database import AsyncSessionLocal
        from services.folder_service import FolderService
        from schemas.core import FolderCreate
        
        async with AsyncSessionLocal() as db:
            # Check if any folders exist
            folders = await FolderService.get_folders_list(db)
            
            if not folders:
                # Create default root folder
                default_folder = FolderCreate(
                    name="Documents",
                    description="Default document folder"
                )
                await FolderService.create_folder(db, default_folder)
                logger.info("✅ Created default folder structure")
                
    except Exception as e:
        logger.warning(f"⚠️  Could not create default folders: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Streamworks Document Management",
    description="Enterprise-grade document management system with hierarchical folders",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS error handling middleware (must be first)
app.add_middleware(CORSErrorHandlerMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002", "http://localhost:3003", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Add RAG metrics tracking middleware
app.middleware("http")(rag_metrics_middleware_func)

# Add response compression middleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Compress responses larger than 1KB
    compresslevel=6      # Balance between speed and compression
)

# Include routers (minimal set)
app.include_router(auth)  # RBAC Authentication (first for docs organization)
app.include_router(folders)
app.include_router(documents)
app.include_router(websockets)
app.include_router(chat)
# app.include_router(chat_xml)
app.include_router(chat_xml_unified)  # New Unified Chat XML System
app.include_router(langextract_chat)  # 🚀 NEW: LangExtract-First System
app.include_router(upload_progress_websocket)
app.include_router(xml_generator)
app.include_router(xml_streams)
app.include_router(feature_flags)
app.include_router(health)
app.include_router(performance, prefix="/api", tags=["performance"])  # Performance Analytics API
app.include_router(rag_metrics, prefix="/api", tags=["rag-metrics"])  # Enhanced RAG Metrics API
app.include_router(debug, prefix="/debug", tags=["debug"])


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "Streamworks Document Management"}


@app.get("/health/database")
async def database_health():
    """Database health check"""
    is_healthy = await check_database_health()
    if not is_healthy:
        return {"status": "unhealthy", "database": "disconnected"}
    return {"status": "healthy", "database": "connected"}


@app.get("/health/detailed")
async def detailed_health():
    """Detailed system health check"""
    try:
        # Check database
        db_healthy = await check_database_health()
        
        # Check storage
        from pathlib import Path
        storage_healthy = Path("storage/documents").exists()
        
        timestamp = datetime.utcnow().isoformat()

        return {
            "status": "healthy" if db_healthy and storage_healthy else "degraded",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "storage": "healthy" if storage_healthy else "unhealthy"
            },
            "version": "2.0.0",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# System info endpoint
@app.get("/system/info")
async def system_info():
    """Get system information"""
    try:
        from database import AsyncSessionLocal
        from sqlalchemy import select, func, text
        from models.core import Folder, Document
        
        async with AsyncSessionLocal() as db:
            # Count folders
            folder_count_result = await db.execute(select(func.count(Folder.id)))
            folder_count = folder_count_result.scalar()
            
            # Count documents
            doc_count_result = await db.execute(select(func.count(Document.id)))
            doc_count = doc_count_result.scalar()
            
            # Get database version
            db_version_result = await db.execute(text("SELECT version()"))
            db_version = db_version_result.scalar()
            
            return {
                "service": "Streamworks Document Management",
                "version": "2.0.0",
                "database": {
                    "type": "PostgreSQL (Supabase)",
                    "version": db_version.split()[1] if db_version else "unknown"
                },
                "statistics": {
                    "total_folders": folder_count,
                    "total_documents": doc_count
                },
                "features": [
                    "Hierarchical folder structure",
                    "Enterprise document management",
                    "RESTful API",
                    "File upload/download",
                    "Bulk operations",
                    "Search and filtering"
                ]
            }
            
    except Exception as e:
        logger.error(f"System info failed: {str(e)}")
        return {
            "service": "Streamworks Document Management",
            "version": "2.0.0",
            "error": str(e)
        }


# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
