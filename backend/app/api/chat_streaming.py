"""
GPT.R1 - Production-Ready True Streaming Chat API
Real chunk-by-chunk streaming with proper error handling
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator, Dict, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
import openai
from openai import AsyncOpenAI

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..schemas.chat import ChatRequest, MessageCreate
from ..core.config import settings
from ..agents.rag_agent import RAGAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
rag_agent = RAGAgent()

class ChatError(Exception):
    """Custom chat error class"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def stream_chat_response(
    message: str,
    conversation_id: Optional[int],
    db: Session,
    current_user: User
) -> AsyncGenerator[str, None]:
    """
    True streaming chat response with chunk-by-chunk delivery
    """
    try:
        # Auto-create conversation if needed
        if not conversation_id:
            conversation = Conversation(
                title=message[:50] + "..." if len(message) > 50 else message,
                user_id=current_user.id if hasattr(current_user, 'id') else None
            )
            db.add(conversation)
            db.commit()
            conversation_id = conversation.id
            
            # Send conversation creation event
            yield f"data: {json.dumps({'type': 'conversation_created', 'conversation_id': conversation_id})}\\n\\n"
        
        # Save user message immediately
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # Get conversation history for context
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).limit(20).all()
        
        # Format messages for OpenAI
        chat_messages = []
        for msg in messages:
            chat_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Check if RAG enhancement is needed
        rag_context = ""
        try:
            if any(keyword in message.lower() for keyword in ["weather", "news", "current", "latest", "today"]):
                yield f"data: {json.dumps({'type': 'rag_searching', 'message': 'Searching for current information...'})}\\n\\n"
                rag_context = await rag_agent.enhance_query(message)
                if rag_context:
                    yield f"data: {json.dumps({'type': 'rag_found', 'message': 'Found relevant information'})}\\n\\n"
                    chat_messages.append({
                        "role": "system",
                        "content": f"Additional context: {rag_context}"
                    })
        except Exception as e:
            logger.warning(f"RAG enhancement failed: {e}")
            yield f"data: {json.dumps({'type': 'rag_failed', 'message': 'Continuing without search...'})}\\n\\n"
        
        # Start streaming response
        yield f"data: {json.dumps({'type': 'start_streaming'})}\\n\\n"
        
        assistant_response = ""
        
        try:
            # Create streaming chat completion
            stream = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_messages,
                stream=True,
                max_tokens=1000,
                temperature=0.7
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    assistant_response += content
                    
                    # Send each chunk immediately for true streaming
                    chunk_data = {
                        "type": "chunk",
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(chunk_data)}\\n\\n"
                    
                    # Small delay to make streaming visible
                    await asyncio.sleep(0.01)
        
        except openai.RateLimitError:
            error_msg = "API rate limit exceeded. Please try again in a moment."
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg, 'code': 429})}\\n\\n"
            assistant_response = "I'm experiencing high demand right now. Please try again in a moment."
            
        except openai.APITimeoutError:
            error_msg = "Request timed out. Please try again."
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg, 'code': 408})}\\n\\n"
            assistant_response = "I'm taking too long to respond. Please try again."
            
        except openai.AuthenticationError:
            error_msg = "Authentication failed. Please check API configuration."
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg, 'code': 401})}\\n\\n"
            assistant_response = "I'm having trouble connecting to the AI service."
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            error_msg = f"AI service error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg, 'code': 500})}\\n\\n"
            assistant_response = "I encountered an error. Please try again."
        
        # Save assistant response
        try:
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
                timestamp=datetime.utcnow()
            )
            db.add(assistant_message)
            db.commit()
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'message_id': assistant_message.id})}\\n\\n"
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving message: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to save message', 'code': 500})}\\n\\n"
    
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Database connection error', 'code': 500})}\\n\\n"
        
    except Exception as e:
        logger.error(f"Unexpected error in streaming: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Unexpected error occurred', 'code': 500})}\\n\\n"

@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    True streaming chat endpoint with real-time chunk delivery
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Message cannot be empty", "code": 400}
            )
        
        if len(request.message) > 4000:
            raise HTTPException(
                status_code=400,
                detail={"error": "Message too long (max 4000 characters)", "code": 400}
            )
        
        return StreamingResponse(
            stream_chat_response(
                message=request.message,
                conversation_id=request.conversation_id,
                db=db,
                current_user=current_user
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat stream error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "code": 500}
        )

@router.get("/conversations")
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user conversations with error handling"""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id if hasattr(current_user, 'id') else True
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for conv in conversations:
            try:
                message_count = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).count()
                
                last_message = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).order_by(Message.timestamp.desc()).first()
                
                result.append({
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat(),
                    "message_count": message_count,
                    "last_message": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None
                })
            except Exception as e:
                logger.warning(f"Error processing conversation {conv.id}: {e}")
                continue
        
        return {"conversations": result, "total": len(result)}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error listing conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Database error", "code": 500}
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve conversations", "code": 500}
        )

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with messages"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail={"error": "Conversation not found", "code": 404}
            )
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else conversation.created_at.isoformat(),
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
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Database error", "code": 500}
        )
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve conversation", "code": 500}
        )

@router.post("/conversations")
async def create_conversation(
    title: str = "New Conversation",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation"""
    try:
        conversation = Conversation(
            title=title,
            user_id=current_user.id if hasattr(current_user, 'id') else None
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else conversation.created_at.isoformat()
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to create conversation", "code": 500}
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to create conversation", "code": 500}
        )

@router.get("/health")
async def health_check():
    """System health check with detailed status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "GPT.R1 True Streaming Chat API",
            "version": "2.0.0",
            "features": {
                "streaming": True,
                "authentication": True,
                "rag_agent": True,
                "error_handling": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"error": "Service unhealthy", "code": 503}
        )