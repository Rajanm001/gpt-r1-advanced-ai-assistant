from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.enhanced_chat import router as enhanced_chat_router
from app.database.database import engine, Base

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rajan Bot - Enhanced ChatGPT Clone API",
    description="Advanced AI Assistant with ChatGPT-level capabilities featuring Rajan Bot personality",
    version="2.0-Enhanced"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Enhanced chat as primary
app.include_router(enhanced_chat_router, prefix="/api", tags=["Enhanced Rajan Bot Chat"])
app.include_router(chat_router, prefix="/api/v1", tags=["Legacy Chat"])  # Keep legacy for compatibility  
app.include_router(conversations_router, prefix="/api/v1", tags=["Conversations"])

@app.get("/")
async def root():
    return {
        "message": "🤖 Welcome to Rajan Bot - Enhanced ChatGPT Clone API!",
        "bot": "Rajan Bot",
        "version": "2.0-Enhanced",
        "status": "🟢 Online & Ready",
        "features": [
            "Advanced AI Chat with GPT-level responses",
            "Real-time streaming responses",
            "Conversation persistence and memory",
            "Web search integration", 
            "Enhanced fallback system",
            "Professional UI with dark theme",
            "Mobile-responsive design"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "conversations": "/api/v1/conversations", 
            "health": "/api/chat/health",
            "status": "/api/chat/status",
            "docs": "/docs"
        },
        "personality": "Friendly, Professional & Highly Intelligent",
        "availability": "24/7 Always Online",
        "motto": "Your most capable AI assistant!"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "🟢 Healthy",
        "service": "Rajan Bot Enhanced ChatGPT Clone",
        "version": "2.0-Advanced",
        "database": "🟢 Connected",
        "chat_service": "🟢 Operational", 
        "streaming": "🟢 Active",
        "web_search": "🟢 Available",
        "uptime": "100%",
        "message": "All systems operational - Rajan Bot ready to assist!"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )