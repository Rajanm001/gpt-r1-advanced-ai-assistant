from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.schemas import Conversation, ConversationCreate, Message
from app.services.conversation_service import ConversationService
from typing import List

router = APIRouter()

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all conversations"""
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_conversations(skip=skip, limit=limit)
    return conversations

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate = ConversationCreate(),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation_service = ConversationService(db)
    return conversation_service.create_conversation(conversation)

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with messages"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation_service = ConversationService(db)
    if not conversation_service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages for a conversation"""
    conversation_service = ConversationService(db)
    messages = conversation_service.get_conversation_messages(conversation_id)
    return messages