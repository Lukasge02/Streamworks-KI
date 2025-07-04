"""
StreamWorks-KI Backend - New RAG + LoRA Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.services.rag_service import rag_service
from app.services.xml_generator import xml_generator
from app.api.v1.chat import router as chat_router
from app.api.v1.xml_generation import router as xml_router

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting StreamWorks-KI Backend (RAG + LoRA Architecture)")
    logger.info(f"🔧 Environment: {settings.ENV}")
    logger.info(f"🔍 RAG Enabled: {settings.RAG_ENABLED}")
    logger.info(f"🔧 XML Generation Enabled: {settings.XML_GENERATION_ENABLED}")
    
    try:
        # Initialize RAG Service
        if settings.RAG_ENABLED:
            logger.info("🔍 Initializing RAG Service...")
            await rag_service.initialize()
            
            # Get initial stats
            rag_stats = await rag_service.get_stats()
            logger.info(f"✅ RAG Service ready - {rag_stats.get('documents_count', 0)} documents indexed")
        else:
            logger.info("⏭️ RAG Service disabled")
        
        # Initialize XML Generator
        if settings.XML_GENERATION_ENABLED:
            logger.info("🔧 Initializing XML Generator...")
            await xml_generator.initialize()
            
            xml_stats = await xml_generator.get_stats()
            logger.info(f"✅ XML Generator ready - LoRA: {xml_stats.get('is_fine_tuned', False)}")
        else:
            logger.info("⏭️ XML Generator disabled (Mock mode)")
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Service initialization error: {e}")
        # Continue in development mode
        if settings.ENV == "development":
            logger.warning("⚠️ Continuing in development mode despite errors")
        else:
            raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down StreamWorks-KI Backend...")
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

# Include API routes
app.include_router(
    chat_router,
    prefix="/api/v1/chat",
    tags=["chat"]
)

app.include_router(
    xml_router,
    prefix="/api/v1/xml",
    tags=["xml_generation"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StreamWorks-KI API v2.0",
        "description": "RAG-based Q&A + LoRA-tuned XML Generation",
        "version": "2.0.0",
        "architecture": "RAG + LoRA",
        "services": {
            "rag_enabled": settings.RAG_ENABLED,
            "xml_generation_enabled": settings.XML_GENERATION_ENABLED,
            "training_enabled": settings.TRAINING_ENABLED
        }
    }

@app.get("/health")
async def health_check():
    """Global health check"""
    try:
        # Get service stats
        rag_stats = await rag_service.get_stats() if settings.RAG_ENABLED else {"status": "disabled"}
        xml_stats = await xml_generator.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": "2025-07-04T01:35:00Z",
            "version": "2.0.0",
            "architecture": "RAG + LoRA",
            "services": {
                "rag": rag_stats,
                "xml_generation": xml_stats,
                "database": "operational"
            },
            "config": {
                "env": settings.ENV,
                "rag_enabled": settings.RAG_ENABLED,
                "xml_generation_enabled": settings.XML_GENERATION_ENABLED,
                "embedding_model": settings.EMBEDDING_MODEL,
                "base_model": settings.BASE_MODEL
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
        "backend_version": "2.0.0",
        "architecture": "RAG + LoRA",
        "features": {
            "rag_qa": settings.RAG_ENABLED,
            "xml_generation": settings.XML_GENERATION_ENABLED,
            "lora_training": settings.TRAINING_ENABLED,
            "document_upload": settings.RAG_ENABLED,
            "vector_search": settings.RAG_ENABLED
        },
        "models": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "base_model": settings.BASE_MODEL,
            "vector_db_path": settings.VECTOR_DB_PATH,
            "lora_adapter_path": settings.LORA_ADAPTER_PATH
        },
        "parameters": {
            "rag_chunk_size": settings.RAG_CHUNK_SIZE,
            "rag_top_k": settings.RAG_TOP_K,
            "max_new_tokens": settings.MAX_NEW_TOKENS,
            "temperature": settings.TEMPERATURE,
            "device": settings.DEVICE
        }
    }