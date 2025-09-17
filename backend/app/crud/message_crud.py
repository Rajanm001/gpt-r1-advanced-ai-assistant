"""
GPT.R1 - Message CRUD Operations
PostgreSQL async CRUD operations for messages
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.message import Message
from app.schemas.chat import MessageCreate

class MessageCRUD:
    """CRUD operations for messages"""
    
    async def create(self, db: AsyncSession, *, obj_in: MessageCreate) -> Message:
        """Create new message"""
        db_obj = Message(
            conversation_id=obj_in.conversation_id,
            role=obj_in.role,
            content=obj_in.content
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Optional[Message]:
        """Get message by ID"""
        result = await db.execute(
            select(Message).where(Message.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_messages_by_conversation(
        self, 
        db: AsyncSession, 
        *, 
        conversation_id: int
    ) -> List[Message]:
        """Get all messages for a conversation"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Message]:
        """Get multiple messages"""
        result = await db.execute(
            select(Message)
            .offset(skip)
            .limit(limit)
            .order_by(Message.created_at.desc())
        )
        return result.scalars().all()
    
    async def remove(self, db: AsyncSession, *, id: int) -> bool:
        """Delete message"""
        message = await self.get(db, id=id)
        if message:
            await db.delete(message)
            return True
        return False

# Create instance
message_crud = MessageCRUD()