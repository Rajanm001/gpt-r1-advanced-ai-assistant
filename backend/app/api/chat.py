"""
GPT.R1 - Production-Ready Chat API Endpoints with Advanced Agentic Workflow
Enhanced streaming chat with modular multi-step agentic flow
Created by: Rajan Mishra
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, AsyncGenerator
import json
import asyncio
import logging
from datetime import datetime

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..services.chat_service import EnhancedChatService
from ..crud import conversation_crud, message_crud
from ..schemas.chat import ChatRequest, ConversationCreate, ConversationSummary
from ..models.conversation import Conversation, Message

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = EnhancedChatService()

@router.get("/api/v1/health")
async def health_check():
    """
    Comprehensive system health check endpoint
    """
    try:
        health_status = await system_health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/api/v1/chat")
async def stream_chat(
    request: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Production-Ready Streaming Chat Endpoint
    
    Features:
    - True chunk-by-chunk streaming with SSE
    - Auto-create conversations seamlessly
    - Comprehensive error handling with recovery
    - User-scoped conversations with ownership validation
    - Graceful OpenAI API failure recovery
    - Database transaction safety
    - Logging and monitoring
    """
    try:
        # Enhanced input validation
        validated_request = validate_chat_request(request)
        message = validated_request["message"]
        conversation_id = validated_request["conversation_id"]
        use_rag = validated_request["use_rag"]
        
        logger.info(f"Processing chat request for user {current_user.id}: {message[:50]}...")
        
        # Validate conversation ownership if conversation_id provided
        conversation = None
        if conversation_id:
            try:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
                
                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "error": "Conversation not found",
                            "code": "CONVERSATION_NOT_FOUND",
                            "message": "The specified conversation does not exist or you don't have access to it"
                        }
                    )
            except SQLAlchemyError as e:
                logger.error(f"Database error checking conversation: {e}")
                raise handle_database_error(e, "conversation validation")
        
        # Log request for monitoring
        logger.info(f"Chat request from user {current_user.id}: conversation_id={conversation_id}, use_rag={use_rag}")
        
        # Handle conversation retrieval/creation with proper error handling
        conversation = None
        if conversation_id:
            try:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
                
                if not conversation:
                    raise HTTPException(
                        status_code=404, 
                        detail={
                            "error": "Conversation not found",
                            "code": "CONVERSATION_NOT_FOUND",
                            "message": f"Conversation {conversation_id} not found or not accessible"
                        }
                    )
            except SQLAlchemyError as e:
                logger.error(f"Database error retrieving conversation: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Database error",
                        "code": "DB_CONNECTION_ERROR",
                        "message": "Unable to access conversation history"
                    }
                )
        
        # Auto-create conversation if none provided
        if not conversation:
            try:
                conversation = Conversation(
                    title=message[:50] + "..." if len(message) > 50 else message,
                    user_id=current_user.id
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                logger.info(f"Created new conversation {conversation.id} for user {current_user.id}")
            except SQLAlchemyError as e:
                logger.error(f"Database error creating conversation: {e}")
                db.rollback()
                raise handle_database_error(e, "conversation creation")
        
        # Save user message with transaction safety
        user_message = None
        try:
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=message
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving user message: {e}")
            db.rollback()
            raise handle_database_error(e, "message saving")
        
        # Get conversation history for context
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp).all()
            
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving history: {e}")
            # Use minimal history but don't fail
            conversation_history = [{"role": "user", "content": message}]
        
        # Enhanced with RAG if requested
        enhanced_message = message
        search_context = ""
        if use_rag:
            try:
                search_context = await rag_service.get_context_from_search(message)
                if search_context:
                    enhanced_message = f"{message}\n\nRelevant context: {search_context}"
                logger.info(f"RAG enhancement successful for user {current_user.id}")
            except Exception as e:
                # RAG failure shouldn't break the chat
                logger.warning(f"RAG service failed for user {current_user.id}: {e}")
                # Continue with original message
                logger.warning(f"RAG enhancement failed: {e}")
                search_context = ""
        
        async def generate_sse_response():
            """Production-ready SSE streaming generator with comprehensive error handling"""
            try:
                # Send initial metadata
                initial_data = {
                    'type': 'start',
                    'conversation_id': conversation.id,
                    'user_message_id': user_message.id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'rag_enabled': bool(search_context)
                }
                yield f"data: {json.dumps(initial_data)}\n\n"
                
                # Add search context if available
                if search_context:
                    context_data = {
                        'type': 'search_context', 
                        'context': search_context[:500],  # Limit context size
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(context_data)}\n\n"
                
                full_response = ""
                chunk_count = 0
                start_time = datetime.utcnow()
                api_error = None
                
                try:
                    # Stream from OpenAI with enhanced error recovery
                    async for chunk in openai_service.create_chat_completion_stream(
                        messages=conversation_history,
                        system_prompt=f"You are GPT.R1, a helpful AI assistant. Context: {search_context}" if search_context else None
                    ):
                        if chunk and chunk.strip():
                            full_response += chunk
                            chunk_count += 1
                            
                            # Send chunk with metadata
                            chunk_data = {
                                'type': 'content',
                                'content': chunk,
                                'chunk_id': chunk_count,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            
                            # Small delay for better streaming UX
                            await asyncio.sleep(0.02)
                
                except Exception as openai_error:
                    # OpenAI API failure - use comprehensive error recovery
                    api_error = openai_error
                    error_info = handle_openai_error(openai_error, fallback_available=True)
                    
                    logger.error(f"OpenAI API error for user {current_user.id}: {openai_error}")
                    
                    # Send error notification with recovery info
                    warning_data = {
                        'type': 'api_error',
                        'error_info': error_info,
                        'recovering': True,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(warning_data)}\n\n"
                    
                    # Use intelligent fallback response with error recovery
                    try:
                        fallback_response = await ErrorRecoveryService.recover_from_openai_error(
                            openai_error, message
                        )
                        full_response = fallback_response
                        
                        # Stream fallback response chunk by chunk
                        words = fallback_response.split(' ')
                        for i, word in enumerate(words):
                            chunk = word + ' '
                            chunk_data = {
                                'type': 'content',
                                'content': chunk,
                                'chunk_id': i+1,
                                'fallback': True,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            await asyncio.sleep(0.05)  # Slower for fallback visibility
                    
                    except Exception as fallback_error:
                        logger.error(f"Fallback error for user {current_user.id}: {fallback_error}")
                        # Last resort response
                        full_response = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
                        error_data = {
                            'type': 'content',
                            'content': full_response,
                            'chunk_id': 1,
                            'critical_fallback': True,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(error_data)}\n\n"
                        messages=conversation_history,
                        system_prompt=f"You are GPT.R1, a helpful AI assistant. Context: {search_context}" if search_context else None
                    ):
                        if chunk and chunk.strip():
                            full_response += chunk
                            chunk_count += 1
                            
                            # Send chunk with metadata
                            chunk_data = {
                                'type': 'content',
                                'content': chunk,
                                'chunk_id': chunk_count,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            
                            # Small delay for better streaming UX
                            await asyncio.sleep(0.02)
                
                except Exception as openai_error:
                    # OpenAI API failure - use intelligent fallback
                    logger.error(f"OpenAI API error: {openai_error}")
                    
                    # Send error notification but continue with fallback
                    warning_data = {
                        'type': 'warning',
                        'message': 'API temporarily unavailable, using intelligent fallback',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(warning_data)}\n\n"
                    
                    # Use intelligent fallback response
                    fallback_response = openai_service._create_intelligent_response(message)
                    full_response = fallback_response
                    
                    # Stream fallback response chunk by chunk
                    words = fallback_response.split(' ')
                    for i, word in enumerate(words):
                        chunk = word + ' '
                        chunk_data = {
                            'type': 'content',
                            'content': chunk,
                            'chunk_id': i+1,
                            'fallback': True,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        await asyncio.sleep(0.05)  # Slower for fallback
                
                # Ensure we have some response
                if not full_response.strip():
                    full_response = "I apologize, but I'm having trouble generating a response right now. Please try again."
                    error_data = {
                        'type': 'content',
                        'content': full_response,
                        'chunk_id': 1,
                        'error_fallback': True,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                
                # Save assistant response to database
                assistant_message = None
                try:
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=full_response.strip()
                    )
                    db.add(assistant_message)
                    db.commit()
                    db.refresh(assistant_message)
                    
                    logger.info(f"Saved assistant message {assistant_message.id} for conversation {conversation.id}")
                    
                except SQLAlchemyError as db_error:
                    # Database save failed - log but don't break stream
                    logger.error(f"Database save error: {db_error}")
                    db.rollback()
                    warning_data = {
                        'type': 'warning',
                        'message': 'Response generated but not saved to history due to database issue',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(warning_data)}\n\n"
                
                # Calculate performance metrics
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds()
                
                # Send completion with metadata
                completion_data = {
                    'type': 'complete',
                    'assistant_message_id': assistant_message.id if assistant_message else None,
                    'total_chunks': chunk_count,
                    'response_time_seconds': response_time,
                    'word_count': len(full_response.split()),
                    'timestamp': end_time.isoformat()
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                # Final fallback for any unexpected errors
                logger.error(f"Streaming error: {e}")
                error_data = {
                    'type': 'error',
                    'error': str(e),
                    'code': 'STREAMING_ERROR',
                    'timestamp': datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
            
            finally:
                # Always send end signal
                end_data = {
                    'type': 'end',
                    'timestamp': datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(end_data)}\n\n"
        
        # Return streaming response with proper SSE headers
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache", 
            "Expires": "0",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control, Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        }
        
        return StreamingResponse(
            generate_sse_response(),
            media_type="text/event-stream",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Unable to process chat request",
                "code": "INTERNAL_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/api/v1/conversations")
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all conversations with pagination"""
    try:
        conversations = db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Add message count for each conversation
        result = []
        for conv in conversations:
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            conv_data = {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat(),
                "message_count": message_count
            }
            result.append(conv_data)
        
        return {
            "conversations": result,
            "total": len(result),
            "skip": skip,
            "limit": limit
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error listing conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error",
                "code": "CONVERSATIONS_LIST_ERROR",
                "message": "Unable to retrieve conversations"
            }
        )

@router.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific conversation with all messages"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": f"Conversation {conversation_id} not found or not accessible"
                }
            )
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).all()
        
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
        logger.error(f"Database error retrieving conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error", 
                "code": "CONVERSATION_RETRIEVE_ERROR",
                "message": "Unable to retrieve conversation"
            }
        )

@router.post("/api/v1/conversations")
async def create_conversation(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    try:
        title = request.get("title", "New Conversation")
        
        conversation = Conversation(
            title=title[:100],  # Limit title length
            user_id=current_user.id
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user {current_user.id}")
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "message_count": 0
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error",
                "code": "CONVERSATION_CREATE_ERROR",
                "message": "Unable to create conversation"
            }
        )

@router.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": f"Conversation {conversation_id} not found or not accessible"
                }
            )
        
        # Delete all messages first (cascade should handle this, but being explicit)
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Deleted conversation {conversation_id} for user {current_user.id}")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error",
                "code": "CONVERSATION_DELETE_ERROR", 
                "message": "Unable to delete conversation"
            }
        )

@router.put("/api/v1/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update conversation title"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": f"Conversation {conversation_id} not found or not accessible"
                }
            )
        
        new_title = request.get("title", "").strip()
        if not new_title:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Title cannot be empty",
                    "code": "EMPTY_TITLE",
                    "message": "Please provide a valid title"
                }
            )
        
        conversation.title = new_title[:100]  # Limit title length
        db.commit()
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else conversation.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating conversation title: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error",
                "code": "CONVERSATION_UPDATE_ERROR",
                "message": "Unable to update conversation title"
            }
        )

# Health check endpoint
@router.get("/api/v1/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "streaming": True,
            "rag": True,
            "authentication": True,
            "error_recovery": True
        }
    }