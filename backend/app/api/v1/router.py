from fastapi import APIRouter

from app.api.v1 import chat, xml_generation, training, evaluation, search

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(xml_generation.router, prefix="/xml", tags=["xml_generation"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])