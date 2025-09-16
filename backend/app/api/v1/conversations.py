from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas import Conversation, ConversationCreate, Message
from app.crud import conversation_crud, message_crud
from app.api.v1.auth import get_current_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[Conversation])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for the current user."""
    conversations = conversation_crud.get_conversations(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return conversations


@router.post("/", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    return conversation_crud.create_conversation(
        db=db, conversation=conversation, user_id=current_user.id
    )


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages."""
    conversation = conversation_crud.get_conversation(db=db, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user owns this conversation (or allow public access for demo)
    if conversation.user_id and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Load messages
    messages = message_crud.get_messages_by_conversation(db=db, conversation_id=conversation_id)
    conversation.messages = messages
    
    return conversation


@router.put("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title."""
    conversation = conversation_crud.get_conversation(db=db, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user owns this conversation
    if conversation.user_id and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_conversation = conversation_crud.update_conversation_title(
        db=db, conversation_id=conversation_id, title=title
    )
    return updated_conversation