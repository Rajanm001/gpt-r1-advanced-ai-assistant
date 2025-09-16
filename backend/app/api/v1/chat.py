import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas import ChatRequest, Message, MessageCreate, ConversationCreate
from app.crud import conversation_crud, message_crud
from app.services import openai_service, rag_service
from app.api.v1.auth import get_current_user
from app.models import User

router = APIRouter()


@router.post("/")
async def chat_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream chat response using Server-Sent Events."""
    
    # Get or create conversation
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        # Create new conversation
        conversation = conversation_crud.create_conversation(
            db=db, 
            conversation=ConversationCreate(title="New Chat"),
            user_id=current_user.id
        )
        conversation_id = conversation.id
    else:
        # Verify conversation exists and user has access
        conversation = conversation_crud.get_conversation(db=db, conversation_id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.user_id and conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Save user message
    user_message = message_crud.create_message(
        db=db,
        message=MessageCreate(role="user", content=chat_request.message),
        conversation_id=conversation_id
    )
    
    # Get conversation history
    messages = message_crud.get_messages_by_conversation(db=db, conversation_id=conversation_id)
    
    async def generate_response():
        """Generate streaming response."""
        try:
            # Send initial response with conversation ID
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"
            
            # Prepare system prompt and context
            system_prompt = None
            if chat_request.use_rag:
                # Get context from RAG service
                context = await rag_service.get_context_from_search(chat_request.message)
                system_prompt = rag_service.create_rag_system_prompt(context)
                
                # Send context info
                yield f"data: {json.dumps({'type': 'context', 'content': 'Searching the web for relevant information...'})}\n\n"
            
            # Generate response using OpenAI
            assistant_response = ""
            async for chunk in openai_service.create_chat_completion_stream(
                messages=messages, 
                system_prompt=system_prompt
            ):
                assistant_response += chunk
                # Send chunk to client
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                # Add small delay to make streaming visible
                await asyncio.sleep(0.01)
            
            # Save assistant message
            assistant_message = message_crud.create_message(
                db=db,
                message=MessageCreate(role="assistant", content=assistant_response),
                conversation_id=conversation_id
            )
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id})}\n\n"
            
        except Exception as e:
            # Send error message
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            
            # Save error message
            message_crud.create_message(
                db=db,
                message=MessageCreate(role="assistant", content=error_msg),
                conversation_id=conversation_id
            )
    
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


@router.post("/simple")
async def chat_simple(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Non-streaming chat endpoint for testing."""
    
    # Get or create conversation
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        conversation = conversation_crud.create_conversation(
            db=db, 
            conversation=ConversationCreate(title="New Chat"),
            user_id=current_user.id
        )
        conversation_id = conversation.id
    
    # Save user message
    user_message = message_crud.create_message(
        db=db,
        message=MessageCreate(role="user", content=chat_request.message),
        conversation_id=conversation_id
    )
    
    # Get conversation history
    messages = message_crud.get_messages_by_conversation(db=db, conversation_id=conversation_id)
    
    # Prepare system prompt if using RAG
    system_prompt = None
    if chat_request.use_rag:
        context = await rag_service.get_context_from_search(chat_request.message)
        system_prompt = rag_service.create_rag_system_prompt(context)
    
    # Generate response
    assistant_response = await openai_service.create_chat_completion(
        messages=messages,
        system_prompt=system_prompt
    )
    
    # Save assistant message
    assistant_message = message_crud.create_message(
        db=db,
        message=MessageCreate(role="assistant", content=assistant_response),
        conversation_id=conversation_id
    )
    
    return {
        "conversation_id": conversation_id,
        "message": assistant_message
    }