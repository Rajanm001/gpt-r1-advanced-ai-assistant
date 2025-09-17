"""
GPT.R1 - Enhanced FastAPI Application with Advanced Agentic Workflow
PostgreSQL-powered ChatGPT clone with modular multi-step AI processing
Created by: Rajan Mishra
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, create_tables
from app.models.conversation import Base
from app.api.chat_enhanced import router as chat_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting GPT.R1 Enhanced Application...")
    
    # Create database tables
    try:
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Log startup completion
    logger.info("🎯 GPT.R1 Enhanced API ready with advanced agentic workflow!")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🔄 Shutting down GPT.R1 Enhanced Application...")

# Create FastAPI application with enhanced configuration
app = FastAPI(
    title="GPT.R1 Enhanced API",
    version="2.0.0",
    description="""
    🚀 GPT.R1 - Advanced ChatGPT Clone with Modular Agentic Workflow
    
    ## Features
    - **Advanced Multi-Step Agentic Processing**: Analyze → Search → Synthesize → Validate → Respond
    - **Real-time Streaming**: Server-Sent Events with workflow progress
    - **PostgreSQL Database**: Production-ready data persistence (FIXED: No SQLite fallback)
    - **DuckDuckGo Integration**: Enhanced RAG with internet search capabilities
    - **Modular Architecture**: Extensible and maintainable codebase
    - **Workflow Analytics**: Comprehensive execution statistics and monitoring
    
    ## Agentic Workflow Steps
    1. **ANALYZE**: Query intent analysis and requirement determination
    2. **SEARCH**: External information gathering via DuckDuckGo (when needed)
    3. **SYNTHESIZE**: Information integration and context building
    4. **VALIDATE**: Response quality assessment and accuracy verification
    5. **RESPOND**: Enhanced response generation with workflow metadata
    
    ## Technical Stack
    - FastAPI with async/await support
    - PostgreSQL with SQLAlchemy ORM
    - OpenAI GPT integration
    - Advanced error handling and recovery
    - Real-time streaming responses
    
    Created by: Rajan Mishra
    """,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development
        "http://localhost:3001",  # Alternative port
        "https://gpt-r1.vercel.app",  # Production domain
        "https://*.vercel.app"  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include enhanced chat router
app.include_router(chat_router, prefix="/api/v1", tags=["Enhanced Chat"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "GPT.R1 Enhanced API",
        "version": "2.0.0",
        "description": "Advanced ChatGPT clone with modular agentic workflow",
        "features": [
            "Multi-step agentic processing",
            "PostgreSQL database (specification compliant)",
            "Real-time streaming responses", 
            "DuckDuckGo search integration",
            "Workflow analytics and monitoring"
        ],
        "database": "PostgreSQL (REQUIRED - no SQLite fallback)",
        "agentic_flow": "Enhanced modular multi-step architecture",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "created_by": "Rajan Mishra"
    }

@app.get("/api", tags=["API Info"])
async def api_info():
    """API information endpoint"""
    return {
        "api_version": "v1",
        "endpoints": {
            "chat_stream": "/api/v1/chat/stream",
            "conversations": "/api/v1/conversations",
            "health": "/api/v1/health",
            "agentic_stats": "/api/v1/agentic/statistics"
        },
        "agentic_workflow": {
            "steps": ["analyze", "search", "synthesize", "validate", "respond"],
            "features": ["Real-time progress", "Quality validation", "Search integration"]
        }
    }


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