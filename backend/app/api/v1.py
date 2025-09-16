"""
GPT.R1 - API v1 Router
Main API router for all v1 endpoints
Created by: Rajan Mishra
"""

from fastapi import APIRouter
from .chat import router as chat_router

# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat_router, tags=["chat"])

# You can add more routers here as the application grows
# api_router.include_router(auth_router, tags=["auth"])
# api_router.include_router(users_router, tags=["users"])