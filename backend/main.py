from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, create_tables
from app.models import Base
from app.api.v1 import api_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GPT.R1 - A professional AI assistant with advanced streaming, RAG capabilities, and enterprise-grade performance",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Create database tables
    create_tables()
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting...")
    print(f"📊 Database: {settings.get_database_url()}")
    print(f"🤖 OpenAI: {'✅ Configured' if settings.is_openai_configured() else '❌ Not configured (using mock responses)'}")
    print(f"🔍 Web Search: {'✅ Enabled' if settings.ENABLE_WEB_SEARCH else '❌ Disabled'}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GPT.R1 - Advanced AI Assistant API",
        "version": settings.VERSION,
        "docs": "/docs",
        "author": "Rajan Mishra",
        "features": [
            "Real-time streaming chat",
            "RAG with web search",
            "Advanced authentication",
            "Conversation management",
            "Enterprise performance"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )