# backend/app/main.py - QUICK FIX ohne Database
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings
from app.services.llm_service import llm_service
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting StreamWorks-KI Backend...")
    logger.info(f"🔧 Mode: {settings.ENV}")
    logger.info(f"🤖 LLM Enabled: {settings.ENABLE_LLM}")
    
    try:
        # Skip database initialization for quick fix
        logger.info("⏭️ Skipping database initialization (Quick Fix)")
        
        # Initialize LLM service (async)
        if settings.ENABLE_LLM:
            logger.info("🧠 Initializing LLM service...")
            llm_service.initialize()
        else:
            logger.info("🎭 Mock mode - LLM initialization skipped")
            llm_service.is_initialized = True
        
        logger.info("✅ Services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Continue anyway in development
        if settings.ENV == "development":
            logger.warning("⚠️ Continuing in development mode despite errors")
        else:
            raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down...")
    logger.info("✅ Shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
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

# Include API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StreamWorks-KI API",
        "version": "1.0.0",
        "status": "running",
        "mode": "mock" if not settings.ENABLE_LLM else "llm"
    }

@app.get("/health")
async def health_check():
    """Global health check"""
    return {
        "status": "healthy",
        "timestamp": "2025-07-04T01:20:00Z",
        "services": {
            "api": "healthy",
            "llm": "healthy" if llm_service.is_initialized else "mock",
            "database": "skipped"
        },
        "config": {
            "env": settings.ENV,
            "llm_enabled": settings.ENABLE_LLM,
            "model": settings.MODEL_NAME if settings.ENABLE_LLM else "mock"
        }
    }