from fastapi import APIRouter

from app.api.v1 import training, qa_api

api_router = APIRouter()

# 🎯 Q&A API - The Only Q&A System You Need
api_router.include_router(qa_api.router, prefix="/qa", tags=["qa"])

# Training endpoints (for document upload)
api_router.include_router(training.router, prefix="/training", tags=["training"])