from fastapi import APIRouter

from app.api.v1 import chat, streams

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(streams.router, prefix="/streams", tags=["streams"])