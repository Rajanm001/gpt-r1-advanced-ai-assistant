from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.schemas import ChatRequest, MessageCreate, ConversationCreate
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
import json
import asyncio
from typing import AsyncGenerator

router = APIRouter()

@router.post("/chat")
async def stream_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Stream chat endpoint with conversation persistence"""
    
    chat_service = ChatService()
    conversation_service = ConversationService(db)
    
    # Get or create conversation
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        # Create new conversation
        new_conversation = conversation_service.create_conversation(
            ConversationCreate(title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message)
        )
        conversation_id = new_conversation.id
    
    # Save user message
    user_message = MessageCreate(
        role="user",
        content=chat_request.message,
        conversation_id=conversation_id
    )
    conversation_service.add_message(user_message)
    
    # Prepare conversation history
    messages = []
    
    # Add conversation history if provided
    if chat_request.conversation_history:
        for msg in chat_request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
    else:
        # Get from database
        db_messages = conversation_service.get_conversation_messages(conversation_id)
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})
    
    # Check if user wants to search the web
    use_search = any(keyword in chat_request.message.lower() for keyword in [
        "search", "latest", "recent", "current", "news", "today", "2024", "2025"
    ])
    
    async def generate_response() -> AsyncGenerator[str, None]:
        full_response = ""
        
        # Send conversation ID first
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"
        
        try:
            async for chunk in chat_service.stream_chat_response(messages, use_search=use_search):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                # Small delay to make streaming visible
                await asyncio.sleep(0.01)
            
            # Save assistant response
            assistant_message = MessageCreate(
                role="assistant",
                content=full_response,
                conversation_id=conversation_id
            )
            conversation_service.add_message(assistant_message)
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )