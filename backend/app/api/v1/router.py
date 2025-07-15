from fastapi import APIRouter

from app.api.v1 import training, perfect_qa

api_router = APIRouter()

# 🎯 PERFECT Q&A - The Only Q&A System You Need
api_router.include_router(perfect_qa.router, prefix="/qa", tags=["perfect-qa"])

# Training endpoints (for document upload)
api_router.include_router(training.router, prefix="/training", tags=["training"])