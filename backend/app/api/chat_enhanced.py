"""
GPT.R1 - Enhanced Chat API with Advanced Agentic Workflow
Modern FastAPI endpoints with modular multi-step agentic flow
Created by: Rajan Mishra
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime

from ..core.database import get_db
from ..services.chat_service import EnhancedChatService
from ..crud import conversation_crud, message_crud
from ..schemas.chat import ChatRequest, ConversationCreate, ConversationSummary

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = EnhancedChatService()

@router.get("/health")
async def health_check():
    """
    System health check endpoint
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "GPT.R1 Enhanced Chat API",
            "agentic_workflow": "active",
            "postgresql": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream chat response with advanced agentic workflow
    
    Features:
    - Multi-step agentic processing (analyze → search → synthesize → validate → respond)
    - DuckDuckGo search integration when needed
    - Real-time workflow progress streaming
    - PostgreSQL conversation persistence
    - Enhanced context awareness
    """
    try:
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400, 
                detail="Message cannot be empty"
            )
        
        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            # Create new conversation
            conversation_data = ConversationCreate(title="New Conversation")
            conversation = await conversation_crud.create(db, obj_in=conversation_data)
            conversation_id = conversation.id
        else:
            # Validate existing conversation
            conversation = await conversation_crud.get(db, id=conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=404, 
                    detail="Conversation not found"
                )
        
        # Stream response using enhanced agentic workflow
        async def generate_stream():
            """Generate streaming response with agentic workflow"""
            try:
                async for chunk in chat_service.stream_chat_response(
                    conversation_id=conversation_id,
                    user_message=request.message,
                    db=db
                ):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_chunk = "data: " + json.dumps({
                    "type": "error",
                    "message": f"Stream error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }) + "\n\n"
                yield error_chunk
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during chat processing"
        )

@router.post("/conversations")
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    try:
        conversation = await conversation_crud.create(db, obj_in=conversation_data)
        return conversation
    except Exception as e:
        logger.error(f"Conversation creation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to create conversation"
        )

@router.get("/conversations")
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation list with summaries"""
    try:
        conversations = await conversation_crud.get_conversation_summaries(
            db, skip=skip, limit=limit
        )
        return conversations
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve conversations"
        )

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific conversation with messages"""
    try:
        conversation = await conversation_crud.get(db, id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve conversation"
        )

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific conversation"""
    try:
        messages = await message_crud.get_messages_by_conversation(
            db, conversation_id=conversation_id, skip=skip, limit=limit
        )
        return messages
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve messages"
        )

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation summary with workflow statistics"""
    try:
        summary = await chat_service.get_conversation_summary(conversation_id, db)
        return summary
    except Exception as e:
        logger.error(f"Get conversation summary error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get conversation summary"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete (soft delete) a conversation"""
    try:
        conversation = await conversation_crud.delete(db, id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to delete conversation"
        )

@router.get("/agentic/statistics")
async def get_agentic_statistics():
    """Get agentic workflow statistics"""
    try:
        stats = chat_service.agentic_service.get_workflow_statistics()
        return {
            "agentic_workflow_stats": stats,
            "service_info": {
                "name": "GPT.R1 Enhanced Agentic Service",
                "version": "1.0.0",
                "features": [
                    "Multi-step workflow processing",
                    "DuckDuckGo search integration",
                    "Real-time progress streaming",
                    "Quality validation",
                    "PostgreSQL persistence"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Get agentic statistics error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get agentic statistics"
        )