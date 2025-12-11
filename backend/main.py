"""
Streamworks Self Service - Backend API
KI-gestützte XML-Generierung für Streamworks Streams
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import domain routers
from domains.chat.router import router as chat_router
from domains.xml.router import router as xml_router
from domains.wizard.router import router as wizard_router
from domains.options.router import router as options_router
from domains.documents.router import router as documents_router

app = FastAPI(
    title="Streamworks Self Service API",
    description="KI-gestützte Erstellung von Streamworks XML Streams",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
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


@app.get("/")
async def root():
    return {
        "service": "Streamworks Self Service API",
        "version": "2.0.0",
        "domains": ["chat", "xml", "wizard", "documents"]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}



