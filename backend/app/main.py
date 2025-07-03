from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting StreamWorks-KI Backend...")
    logger.info("✅ Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down...")
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="StreamWorks-KI API",
    description="Intelligente Workload-Automatisierung für StreamWorks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "StreamWorks-KI",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "StreamWorks-KI Backend läuft! 🚀"}