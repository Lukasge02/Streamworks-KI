from fastapi import APIRouter

from app.api.v1 import chat, streams, training, evaluation, search

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(streams.router, prefix="/streams", tags=["streams"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])