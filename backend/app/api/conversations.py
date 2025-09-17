"""
GPT.R1 - Conversations API
FastAPI endpoints for conversation management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud import conversation_crud, message_crud
from app.schemas.chat import ConversationCreate, ConversationResponse, ConversationUpdate

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    try:
        db_conversation = await conversation_crud.create(db, obj_in=conversation)
        await db.commit()
        return db_conversation
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[dict])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of conversations"""
    try:
        conversations = await conversation_crud.get_conversation_summaries(
            db, skip=skip, limit=limit
        )
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation with messages"""
    try:
        conversation = await conversation_crud.get(db, id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await message_crud.get_messages_by_conversation(
            db, conversation_id=conversation_id
        )
        
        return {
            "conversation": conversation,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update conversation"""
    try:
        conversation = await conversation_crud.get(db, id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        updated_conversation = await conversation_crud.update(
            db, db_obj=conversation, obj_in=conversation_update
        )
        await db.commit()
        return updated_conversation
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete conversation"""
    try:
        conversation = await conversation_crud.get(db, id=conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        await conversation_crud.remove(db, id=conversation_id)
        await db.commit()
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))