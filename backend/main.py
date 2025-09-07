"""
StreamWorks Document Management System
Enterprise-grade FastAPI backend with clean architecture
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database and routers
from database import init_database, close_database, check_database_health
from routers import folders, documents, websockets, upload_progress_websocket, chat

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
        logger.info("🚀 Starting StreamWorks Document Management System")
        
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Add startup seed data if needed
        await create_default_folder_if_needed()
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down StreamWorks")
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
    title="StreamWorks Document Management",
    description="Enterprise-grade document management system with hierarchical folders",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(folders.router)
app.include_router(documents.router)
app.include_router(websockets.router)
app.include_router(chat.router)
app.include_router(upload_progress_websocket.router)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "StreamWorks Document Management"}


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
        
        return {
            "status": "healthy" if db_healthy and storage_healthy else "degraded",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "storage": "healthy" if storage_healthy else "unhealthy"
            },
            "version": "2.0.0",
            "timestamp": "2025-09-05T21:28:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-09-05T21:28:00Z"
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
                "service": "StreamWorks Document Management",
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
            "service": "StreamWorks Document Management",
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
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )