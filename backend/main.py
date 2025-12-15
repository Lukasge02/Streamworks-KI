"""
Streamworks Self Service - Backend API
KI-gestützte XML-Generierung für Streamworks Streams
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import domain routers
from domains.chat.router import router as chat_router
from domains.xml.router import router as xml_router
from domains.wizard.router import router as wizard_router
from domains.options.router import router as options_router
from domains.documents.router import router as documents_router
from domains.testing.router import router as testing_router
from domains.auth.router import router as auth_router

# Import DI container
from services.container import Container, get_health_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Streamworks Self Service API...")
    Container.initialize()
    yield
    # Shutdown
    print("👋 Shutting down Streamworks Self Service API...")


app = FastAPI(
    title="Streamworks Self Service API",
    description="KI-gestützte Erstellung von Streamworks XML Streams",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register domain routers
app.include_router(chat_router)
app.include_router(xml_router)
app.include_router(wizard_router)
app.include_router(options_router)
app.include_router(documents_router)
app.include_router(testing_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "service": "Streamworks Self Service API",
        "version": "2.0.0",
        "domains": ["chat", "xml", "wizard", "documents", "testing"],
    }


@app.get("/health")
async def health():
    """Quick health check for load balancers"""
    return {"status": "healthy"}


@app.get("/health/detailed")
async def health_detailed(health_service=Depends(get_health_service)):
    """
    Detailed health check with component status.

    Returns status for:
    - Qdrant (vector database)
    - MinIO (object storage)
    - Supabase (database)
    """
    return health_service.check_all()
