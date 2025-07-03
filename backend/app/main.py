from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.chat import router as chat_router

app = FastAPI(title="StreamWorks-KI", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/health")
async def health():
    return {"status": "ok", "message": "StreamWorks-KI Backend läuft"}

@app.get("/")
async def root():
    return {"message": "StreamWorks-KI API - Funktioniert! 🚀"}