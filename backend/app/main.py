"""
StreamWorks-KI Backend - New RAG + LoRA Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.async_manager import initialize_async_manager, shutdown_async_manager
from app.services.rag_service import rag_service
from app.services.mistral_rag_service import mistral_rag_service
from app.services.mistral_llm_service import mistral_llm_service
from app.services.simple_qa_service import simple_qa_service
from app.services.fast_qa_service import fast_qa_service
from app.models.database import init_db
from app.api.v1.chat import router as chat_router
from app.api.v1.qa import router as qa_router
from app.api.v1.training import router as training_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.health import router as health_router
from app.api.v1.ab_testing import router as ab_testing_router
from app.api.v1.chromadb_sync import router as chromadb_sync_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.chunks import router as chunks_router
from app.middleware.monitoring import (
    PerformanceMonitoringMiddleware,
    RequestLoggingMiddleware,
    StreamWorksMetricsMiddleware
)
from app.middleware.mistral_monitoring import MistralPerformanceMiddleware
from app.middleware.production_monitoring import (
    create_monitoring_middleware,
    start_monitoring,
    log_alert_handler,
    webhook_alert_handler
)

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
        
        # Start production monitoring
        try:
            await start_monitoring()
            logger.info("📈 Production monitoring started")
        except Exception as e:
            logger.error(f"❌ Monitoring startup failed: {e}")
        
        # Initialize Database
        logger.info("🗄️ Initializing Database...")
        await init_db()
        logger.info("✅ Database initialized")
        
        # 1. Mistral LLM Service zuerst initialisieren (für RAG Dependencies)
        if settings.LLM_ENABLED:
            logger.info("🤖 Initializing Mistral 7B Service...")
            await mistral_llm_service.initialize()
            
            mistral_stats = await mistral_llm_service.get_stats()
            logger.info(f"✅ Mistral 7B ready - Model: {mistral_stats.get('model_name', 'mistral:7b-instruct')}")
        else:
            logger.info("⏭️ Mistral Service disabled")
        
        # 2. RAG Service initialisieren (kann jetzt Mistral nutzen)
        if settings.RAG_ENABLED:
            logger.info("🔍 Initializing RAG Service...")
            # Inject Mistral service if available
            if settings.LLM_ENABLED and mistral_llm_service.is_initialized:
                rag_service.mistral_service = mistral_llm_service
                logger.info("✅ Mistral service injected into RAG")
            await rag_service.initialize()
            
            rag_stats = await rag_service.get_stats()
            logger.info(f"✅ RAG Service ready - {rag_stats.get('documents_count', 0)} documents indexed")
        else:
            logger.info("⏭️ RAG Service disabled")
        
        # 3. Mistral RAG Service (kombiniert beide Services)
        if settings.LLM_ENABLED and settings.RAG_ENABLED:
            logger.info("🔍 Initializing Mistral RAG Service...")
            await mistral_rag_service.initialize()
            logger.info("✅ Mistral RAG Service ready")
            
            # Initialize Q&A Services
            logger.info("🎯 Initializing Simple Q&A Service...")
            await simple_qa_service.initialize()
            logger.info("✅ Simple Q&A Service ready")
            
            logger.info("⚡ Initializing Fast Q&A Service...")
            await fast_qa_service.initialize()
            logger.info("✅ Fast Q&A Service ready")
        
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
    
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
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

# Add Production Monitoring Middleware (replaces old monitoring)
production_monitoring = create_monitoring_middleware(
    app,
    enable_prometheus=True,
    enable_alerts=True,
    enable_system_monitoring=True,
    system_monitor_interval=10.0
)

# Add alert handlers
if production_monitoring.alert_manager:
    production_monitoring.alert_manager.add_alert_handler(log_alert_handler)
    # Add webhook handler if URL is configured
    import os
    if os.environ.get('ALERT_WEBHOOK_URL'):
        production_monitoring.alert_manager.add_alert_handler(webhook_alert_handler)

# Add legacy monitoring for backward compatibility
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(StreamWorksMetricsMiddleware)
app.add_middleware(MistralPerformanceMiddleware)

# Add Request Logging in development
if settings.ENV == "development":
    app.add_middleware(RequestLoggingMiddleware)

# Include API routes
app.include_router(
    chat_router,
    prefix="/api/v1/chat",
    tags=["chat"]
)

app.include_router(
    qa_router,
    prefix="/api/v1/qa",
    tags=["qa"]
)

app.include_router(
    training_router,
    prefix="/api/v1/training",
    tags=["training"]
)

app.include_router(
    conversations_router,
    prefix="/api/v1/conversations",
    tags=["conversation_memory"]
)

app.include_router(
    evaluation_router,
    prefix="/api/v1/evaluation",
    tags=["evaluation"]
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["health"]
)

app.include_router(
    ab_testing_router,
    prefix="/api/v1/ab-testing",
    tags=["ab_testing"]
)

app.include_router(
    chromadb_sync_router,
    prefix="/api/v1",
    tags=["chromadb_sync"]
)

app.include_router(
    monitoring_router,
    prefix="/api/v1/monitoring",
    tags=["monitoring", "metrics", "health"]
)

app.include_router(
    chunks_router,
    prefix="/api/v1/chunks",
    tags=["chunks", "chromadb", "vectors"]
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
        # Get service stats
        rag_stats = await rag_service.get_stats() if settings.RAG_ENABLED else {"status": "disabled"}
        mistral_stats = await mistral_llm_service.get_stats() if settings.LLM_ENABLED else {"status": "disabled"}
        mistral_rag_stats = await mistral_rag_service.get_stats() if settings.RAG_ENABLED and settings.LLM_ENABLED else {"status": "disabled"}
        
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

@app.get("/api/v1/mistral-metrics")
async def get_mistral_metrics():
    """Dedicated Mistral performance metrics"""
    # Find Mistral middleware
    for middleware in app.middleware:
        if hasattr(middleware, 'cls') and middleware.cls == MistralPerformanceMiddleware:
            if hasattr(middleware, 'get_metrics'):
                return middleware.get_metrics()
    
    return {
        "error": "Mistral Performance Middleware not found",
        "status": "metrics_unavailable"
    }