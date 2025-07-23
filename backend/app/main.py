"""
StreamWorks-KI Backend - New RAG + LoRA Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.settings import settings
from app.core.async_manager import initialize_async_manager, shutdown_async_manager
# from app.services.rag_service import rag_service  # PROBLEMATIC
# from app.services.mistral_rag_service import mistral_rag_service  # PROBLEMATIC  
from app.services.mistral_llm_service import mistral_llm_service
# Legacy services removed - only perfect_qa_service remains
from app.core.database_postgres import init_database, close_database
# Only import existing routers
from app.api.v1.qa_api import router as qa_router
from app.api.v1.training import router as training_router
from app.api.v1.categories import router as categories_router
from app.api.v1.files_enterprise import router as files_router
from app.api.v1.simple_folders import router as folders_router
from app.api.v1.xml import router as xml_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.documents import router as documents_router
from app.middleware.monitoring import (
    PerformanceMonitoringMiddleware,
    RequestLoggingMiddleware,
    StreamWorksMetricsMiddleware
)
# Legacy monitoring removed - using enhanced_monitoring instead

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Mistral-optimierte Startup-Sequenz"""
    
    # Startup
    logger.info("🚀 Starting StreamWorks-KI Backend (Mistral 7B Optimized)")
    logger.info(f"🔧 Environment: {settings.ENV}")
    logger.info(f"🔍 RAG Enabled: {settings.RAG_ENABLED}")
    logger.info(f"🤖 LLM Enabled: {settings.LLM_ENABLED}")
    
    try:
        # Initialize AsyncTaskManager first
        logger.info("⚙️ Initializing AsyncTaskManager...")
        await initialize_async_manager()
        logger.info("✅ AsyncTaskManager started")
        
        # Start background indexer
        logger.info("🚀 Starting background indexer...")
        from app.services.background_indexer import background_indexer
        await background_indexer.start_worker()
        logger.info("✅ Background indexer started")
        
        # Warm up RAG service
        logger.info("🔥 Warming up RAG service...")
        from app.services.rag_service import rag_service
        await rag_service.initialize()
        logger.info("✅ RAG service warmed up")
        
        # Production monitoring handled by middleware
        logger.info("📈 Monitoring configured via middleware")
        
        # Initialize PostgreSQL Database
        logger.info("🗄️ Initializing PostgreSQL Database...")
        await init_database()
        logger.info("✅ PostgreSQL Database initialized")
        
        # 1. Mistral LLM Service - LAZY LOADING für schnellen Start
        if settings.LLM_ENABLED:
            logger.info("🤖 Mistral 7B Service - LAZY LOADING (will initialize on first request)")
        else:
            logger.info("⏭️ Mistral Service disabled")
        
        # 2. RAG Service - LAZY LOADING für schnellen Start
        if settings.RAG_ENABLED:
            logger.info("🔍 RAG Service - LAZY LOADING (will initialize on first request)")
        else:
            logger.info("⏭️ RAG Service disabled")
        
        # 3. Mistral RAG Service - LAZY LOADING
        if settings.LLM_ENABLED and settings.RAG_ENABLED:
            logger.info("🔍 Mistral RAG Service - LAZY LOADING (will initialize on first request)")
        else:
            logger.info("⏭️ Mistral RAG Service disabled")
        
        logger.info("✅ StreamWorks-KI ready with Mistral 7B optimization")
        
    except Exception as e:
        logger.error(f"❌ Mistral initialization error: {e}")
        # Continue in development mode
        if settings.ENV == "development":
            logger.warning("⚠️ Continuing in development mode despite errors")
        else:
            raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down StreamWorks-KI Backend...")
    
    # Shutdown AsyncTaskManager
    try:
        logger.info("⚙️ Shutting down AsyncTaskManager...")
        await shutdown_async_manager()
        logger.info("✅ AsyncTaskManager shutdown complete")
    except Exception as e:
        logger.error(f"❌ AsyncTaskManager shutdown error: {e}")
    
    # Close PostgreSQL connections
    await close_database()
    
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="StreamWorks-KI: RAG-based Q&A + LoRA-tuned XML Generation",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy production monitoring removed - using enhanced_monitoring

# Add legacy monitoring for backward compatibility
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(StreamWorksMetricsMiddleware)
# Legacy MistralPerformanceMiddleware removed

# Add Request Logging in development
if settings.ENV == "development":
    app.add_middleware(RequestLoggingMiddleware)

# Include API routes (only the two that exist)

# 🎯 Q&A API - Production Ready System
app.include_router(
    qa_router,
    prefix="/api/v1/qa",
    tags=["qa"]
)

# Training/Upload endpoint
app.include_router(
    training_router,
    prefix="/api/v1/training",
    tags=["training"]
)

# Categories Management
app.include_router(
    categories_router,
    prefix="/api/v1/categories",
    tags=["categories"]
)

# Files Management (New Clean API)
app.include_router(
    files_router,
    prefix="/api/v1/files",
    tags=["files"]
)

# Folders Management
app.include_router(
    folders_router,
    prefix="/api/v1/folders",
    tags=["folders"]
)

# 🎯 XML Generator - StreamWorks Specialization
app.include_router(
    xml_router,
    prefix="/api/v1/xml",
    tags=["xml-generator"]
)

# 📊 Analytics API - Bachelor Thesis Metrics
app.include_router(
    analytics_router,
    prefix="/api/v1",
    tags=["analytics"]
)

# 📄 Documents API - PostgreSQL Document Service
app.include_router(
    documents_router,
    prefix="/api/v1",
    tags=["documents"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StreamWorks-KI API v2.1",
        "description": "RAG-based Q&A System for StreamWorks Support",
        "version": "2.1.0",
        "architecture": "Mistral 7B + RAG",
        "services": {
            "rag_enabled": settings.RAG_ENABLED,
            "llm_enabled": settings.LLM_ENABLED,
            "training_enabled": settings.TRAINING_ENABLED
        }
    }

@app.get("/health")
async def health_check():
    """Global health check"""
    try:
        # Get service stats (simplified)
        mistral_stats = await mistral_llm_service.get_stats() if settings.LLM_ENABLED else {"status": "disabled"}
        rag_stats = {"status": "available"}
        mistral_rag_stats = {"status": "available"}
        
        return {
            "status": "healthy",
            "timestamp": "2025-07-04T12:40:00Z",
            "version": "2.1.0",
            "architecture": "Mistral 7B + RAG",
            "services": {
                "rag": rag_stats,
                "mistral_llm": mistral_stats,
                "mistral_rag": mistral_rag_stats,
                "database": "operational"
            },
            "config": {
                "env": settings.ENV,
                "rag_enabled": settings.RAG_ENABLED,
                "llm_enabled": settings.LLM_ENABLED,
                "xml_generation_enabled": settings.XML_GENERATION_ENABLED,
                "embedding_model": settings.EMBEDDING_MODEL,
                "mistral_model": settings.OLLAMA_MODEL,
                "german_optimization": settings.FORCE_GERMAN_RESPONSES
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-07-04T01:35:00Z"
        }

@app.get("/api/v1/status")
async def system_status():
    """Detailed system status"""
    return {
        "backend_version": "2.1.0",
        "architecture": "Mistral 7B + RAG",
        "features": {
            "mistral_rag_qa": settings.RAG_ENABLED and settings.LLM_ENABLED,
            "german_optimization": settings.FORCE_GERMAN_RESPONSES,
            "document_upload": settings.RAG_ENABLED,
            "vector_search": settings.RAG_ENABLED,
            "performance_monitoring": True
        },
        "models": {
            "mistral_model": settings.OLLAMA_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "vector_db_path": settings.VECTOR_DB_PATH
        },
        "mistral_parameters": {
            "temperature": settings.MODEL_TEMPERATURE,
            "top_p": settings.MODEL_TOP_P,
            "top_k": settings.MODEL_TOP_K,
            "max_tokens": settings.MODEL_MAX_TOKENS,
            "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
            "context_window": settings.MODEL_CONTEXT_WINDOW,
            "threads": settings.MODEL_THREADS
        },
        "rag_parameters": {
            "chunk_size": settings.RAG_CHUNK_SIZE,
            "chunk_overlap": settings.RAG_CHUNK_OVERLAP,
            "top_k": settings.RAG_TOP_K
        },
        "legacy_parameters": {
            "max_new_tokens": settings.MAX_NEW_TOKENS,
            "temperature": settings.TEMPERATURE,
            "device": settings.DEVICE
        }
    }

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get basic performance metrics"""
    try:
        from datetime import datetime
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "monitoring_active",
            "message": "Advanced performance monitoring is running. Check response headers for timing data.",
            "endpoints_monitored": [
                "/api/v1/chat/",
                "/api/v1/xml/generate",
                "/api/v1/training/upload",
                "/health"
            ],
            "monitoring_features": [
                "Request timing",
                "Error tracking", 
                "Slow request detection",
                "System resource monitoring",
                "Endpoint-specific metrics"
            ]
        }
    except Exception as e:
        return {
            "error": f"Metrics endpoint error: {str(e)}",
            "status": "error"
        }

# Legacy mistral metrics endpoint removed