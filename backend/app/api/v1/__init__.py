from fastapi import APIRouter
from app.api.v1 import auth, conversations, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])