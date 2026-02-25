from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import health, wizard, rag, documents, options

settings = get_settings()

app = FastAPI(title="Streamworks-KI", version="2.0.0")

allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(wizard.router, prefix="/api/wizard", tags=["wizard"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(options.router, prefix="/api/options", tags=["options"])

if __name__ == "__main__":
    import uvicorn
    is_dev = settings.environment == "development"
    uvicorn.run("main:app", host=settings.backend_host, port=settings.backend_port, reload=is_dev)
