"""
GPT.R1 - Chat API Endpoints
Streaming chat endpoint with conversation management
Created by: Rajan Mishra
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime

from ..core.database import get_db
from ..models.models import Conversation, Message, User
from ..services.openai_service import OpenAIService
from ..services.rag_service import RAGService
from ..core.security import get_current_user

router = APIRouter()
openai_service = OpenAIService()
rag_service = RAGService()

class ChatRequest:
    def __init__(self, message: str, conversation_id: Optional[int] = None, stream: bool = True):
        self.message = message
        self.conversation_id = conversation_id
        self.stream = stream

class MessageResponse:
    def __init__(self, role: str, content: str, timestamp: datetime):
        self.role = role
        self.content = content
        self.timestamp = timestamp

@router.post("/api/v1/chat")
async def stream_chat(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Streaming Chat Endpoint - As Required by Assignment
    
    POST /api/v1/chat
    - Accepts conversation history + new user message
    - Uses OpenAI with stream=True
    - Streams assistant response via StreamingResponse
    - Headers: Content-Type: text/event-stream
    """
    try:
        message = request.get("message", "")
        conversation_id = request.get("conversation_id")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(user_id=current_user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=message
        )
        db.add(user_message)
        db.commit()
        
        # Get conversation history for context
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp).all()
        
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Enhanced with RAG if needed
        enhanced_message = await rag_service.enhance_query(message)
        
        async def generate_response():
            """Generator for streaming response"""
            try:
                full_response = ""
                
                # Send conversation ID first
                yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"
                
                # Stream the response
                async for chunk in openai_service.stream_chat_completion(
                    messages=conversation_history,
                    enhanced_query=enhanced_message
                ):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)  # Small delay for better UX
                
                # Save assistant response
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_response
                )
                db.add(assistant_message)
                db.commit()
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/api/v1/conversations")
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all conversations for current user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    
    result = []
    for conv in conversations:
        # Get last message for preview
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.timestamp.desc()).first()
        
        result.append({
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "message_count": db.query(Message).filter(Message.conversation_id == conv.id).count(),
            "last_message": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
            "last_activity": last_message.timestamp.isoformat() if last_message else conv.created_at.isoformat()
        })
    
    return {"conversations": result}

@router.get("/api/v1/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch message history for a specific conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()
    
    return {
        "conversation_id": conversation_id,
        "created_at": conversation.created_at.isoformat(),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }

@router.post("/api/v1/conversations")
async def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    conversation = Conversation(user_id=current_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat(),
        "message_count": 0
    }

@router.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages first
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Delete conversation
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

# Health check endpoint
@router.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GPT.R1 Chat API",
        "version": "1.0.0",
        "author": "Rajan Mishra",
        "timestamp": datetime.now().isoformat()
    }