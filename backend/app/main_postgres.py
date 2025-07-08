"""
PostgreSQL-optimized FastAPI application for StreamWorks-KI
Enhanced for production RAG workloads with PostgreSQL backend
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

# PostgreSQL-optimized imports
from app.core.config_postgres import postgres_settings as settings
from app.models.database_postgres import postgres_db_manager as db_manager

# Import services (using PostgreSQL versions)
from app.services.mistral_llm_service import mistral_llm_service
from app.services.rag_service import rag_service
from app.services.mistral_rag_service import mistral_rag_service
from app.services.xml_generator import xml_generator

# Import API routers
from app.api.v1.chat import router as chat_router
from app.api.v1.training import router as training_router
from app.api.v1.health import router as health_router
from app.api.v1.search import router as search_router
from app.api.v1.xml_generation import router as xml_router
from app.api.v1.chromadb_sync import router as chromadb_sync_router

# Import middleware
from app.middleware.monitoring import PerformanceMonitoringMiddleware
from app.middleware.mistral_monitoring import MistralPerformanceMiddleware

logger = logging.getLogger(__name__)

# PostgreSQL-optimized lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced lifespan management with PostgreSQL optimization"""
    logger.info("🚀 Starting StreamWorks-KI Backend (PostgreSQL Optimized)")
    logger.info(f"🔧 Environment: {settings.ENV}")
    logger.info(f"🔍 RAG Enabled: {settings.RAG_ENABLED}")
    logger.info(f"🤖 LLM Enabled: {settings.LLM_ENABLED}")
    logger.info(f"🔧 XML Generation Enabled: {settings.XML_GENERATION_ENABLED}")
    
    # Initialize PostgreSQL with enhanced connection pooling
    logger.info("🗄️ Initializing PostgreSQL Database...")
    db_success = await db_manager.initialize()
    if db_success:
        logger.info("✅ PostgreSQL initialized with connection pooling")
        
        # Get initial database stats
        health = await db_manager.get_health_status()
        if health["status"] == "healthy":
            stats = health.get("database_stats", {})
            pool = health.get("connection_pool", {})
            logger.info(f"📊 Database: {stats.get('total_files', 0)} files, {stats.get('database_size_mb', 0)}MB")
            logger.info(f"🔗 Pool: {pool.get('pool_size', 0)} connections configured")
        else:
            logger.warning(f"⚠️ PostgreSQL health check warning: {health.get('error', 'Unknown')}")
    else:
        logger.error("❌ PostgreSQL initialization failed")
        raise RuntimeError("Database initialization failed")
    
    # Initialize Mistral 7B Service (optimized for PostgreSQL workloads)
    logger.info("🤖 Initializing Mistral 7B Service...")
    try:
        await mistral_llm_service.initialize()
        if mistral_llm_service.is_initialized:
            logger.info(f"✅ Mistral 7B ready - Model: {settings.OLLAMA_MODEL}")
        else:
            logger.warning("⚠️ Mistral 7B initialization incomplete")
    except Exception as e:
        logger.error(f"❌ Mistral 7B initialization failed: {e}")
    
    # Initialize RAG Service with PostgreSQL backend
    logger.info("🔍 Initializing RAG Service...")
    try:
        # Inject PostgreSQL-optimized database manager
        rag_service.db_manager = db_manager
        logger.info("✅ PostgreSQL database manager injected into RAG")
        
        await rag_service.initialize()
        if rag_service.is_initialized:
            collection_info = await rag_service.get_collection_info()
            doc_count = collection_info.get("document_count", 0)
            logger.info(f"✅ RAG Service ready - {doc_count} documents indexed")
        else:
            logger.warning("⚠️ RAG Service initialization incomplete")
    except Exception as e:
        logger.error(f"❌ RAG Service initialization failed: {e}")
    
    # Initialize Mistral RAG Service (PostgreSQL-enhanced)
    logger.info("🔍 Initializing Mistral RAG Service...")
    try:
        await mistral_rag_service.initialize()
        if mistral_rag_service.is_initialized:
            logger.info("✅ Mistral RAG Service ready")
        else:
            logger.warning("⚠️ Mistral RAG Service initialization incomplete")
    except Exception as e:
        logger.error(f"❌ Mistral RAG Service initialization failed: {e}")
    
    # Initialize XML Generator
    logger.info("🔧 Initializing XML Generator...")
    try:
        await xml_generator.initialize()
        if xml_generator.is_initialized:
            templates_count = len(xml_generator.templates)
            logger.info(f"✅ XML Generator ready - {templates_count} templates loaded")
        else:
            logger.warning("⚠️ XML Generator initialization incomplete")
    except Exception as e:
        logger.error(f"❌ XML Generator initialization failed: {e}")
    
    logger.info("✅ StreamWorks-KI ready with PostgreSQL optimization")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down StreamWorks-KI Backend...")
    await db_manager.close()
    logger.info("✅ Shutdown complete")

# Create FastAPI app with PostgreSQL optimizations
app = FastAPI(
    title="StreamWorks-KI API (PostgreSQL)",
    description="Intelligente Workload-Automatisierung für StreamWorks mit PostgreSQL Backend",
    version="2.1.0-postgresql",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enhanced CORS for PostgreSQL deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time", "X-Database-Backend"]
)

# Compression middleware for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# PostgreSQL-optimized performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(MistralPerformanceMiddleware)

# PostgreSQL-specific middleware
@app.middleware("http")
async def database_performance_middleware(request: Request, call_next):
    """Monitor PostgreSQL performance per request"""
    start_time = time.time()
    
    # Add PostgreSQL identification header
    response = await call_next(request)
    
    # Add performance headers
    process_time = time.time() - start_time
    response.headers["X-Response-Time"] = str(round(process_time * 1000, 2))
    response.headers["X-Database-Backend"] = "PostgreSQL"
    
    # Log slow queries
    if process_time > settings.SLOW_QUERY_THRESHOLD:
        logger.warning(f"🐌 Slow request: {request.url.path} took {process_time:.2f}s")
    
    return response

# Enhanced error handling for PostgreSQL
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Enhanced error handling with PostgreSQL context"""
    logger.error(f"❌ Unhandled exception on {request.url.path}: {exc}")
    
    # Check if it's a database-related error
    if "asyncpg" in str(exc) or "postgresql" in str(exc).lower():
        return JSONResponse(
            status_code=503,
            content={
                "error": "Database service temporarily unavailable",
                "detail": "PostgreSQL connection issue",
                "timestamp": time.time()
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENV == "development" else "An unexpected error occurred",
            "timestamp": time.time()
        }
    )

# Include API routers with PostgreSQL prefix
app.include_router(health_router, prefix=settings.API_V1_STR + "/health", tags=["Health"])
app.include_router(chat_router, prefix=settings.API_V1_STR + "/chat", tags=["Chat"])
app.include_router(training_router, prefix=settings.API_V1_STR + "/training", tags=["Training"])
app.include_router(search_router, prefix=settings.API_V1_STR + "/search", tags=["Search"])
app.include_router(xml_router, prefix=settings.API_V1_STR + "/xml", tags=["XML Generation"])
app.include_router(chromadb_sync_router, prefix=settings.API_V1_STR + "/chromadb-sync", tags=["ChromaDB Sync"])

# PostgreSQL-specific endpoints
@app.get("/")
async def root():
    """Root endpoint with PostgreSQL status"""
    return {
        "message": "StreamWorks-KI API with PostgreSQL Backend",
        "version": "2.1.0-postgresql",
        "database": "PostgreSQL",
        "status": "ready",
        "docs": "/docs"
    }

@app.get("/postgres-status")
async def postgres_status():
    """Detailed PostgreSQL status endpoint"""
    try:
        health = await db_manager.get_health_status()
        return {
            "database": "PostgreSQL",
            "status": health["status"],
            "connection_pool": health.get("connection_pool", {}),
            "database_stats": health.get("database_stats", {}),
            "performance": {
                "query_logging": settings.ENABLE_QUERY_LOGGING,
                "slow_query_threshold": settings.SLOW_QUERY_THRESHOLD,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_POOL_MAX_OVERFLOW,
            }
        }
    except Exception as e:
        return {
            "database": "PostgreSQL",
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_postgres:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )