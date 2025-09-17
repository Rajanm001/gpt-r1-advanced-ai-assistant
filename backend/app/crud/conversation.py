"""
CRUD operations for conversations and messages
PostgreSQL-optimized database operations
Created by: Rajan Mishra
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from sqlalchemy.orm import selectinload

from ..models.conversation import Conversation, Message
from ..schemas.chat import ConversationCreate, ConversationUpdate, MessageCreate, MessageUpdate

class ConversationCRUD:
    """CRUD operations for conversations"""
    
    async def create(self, db: AsyncSession, *, obj_in: ConversationCreate) -> Conversation:
        """Create a new conversation"""
        db_obj = Conversation(
            title=obj_in.title
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Conversation]:
        """Get multiple conversations"""
        query = select(Conversation).order_by(desc(Conversation.updated_at))
        
        if active_only:
            query = query.where(Conversation.is_active == True)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Conversation, 
        obj_in: ConversationUpdate
    ) -> Conversation:
        """Update conversation"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> Optional[Conversation]:
        """Soft delete conversation (set is_active to False)"""
        db_obj = await self.get(db, id=id)
        if db_obj:
            db_obj.is_active = False
            await db.commit()
            await db.refresh(db_obj)
        return db_obj
    
    async def get_conversation_summaries(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get conversation summaries with message counts"""
        query = select(
            Conversation.id,
            Conversation.title,
            Conversation.created_at,
            Conversation.updated_at,
            func.count(Message.id).label('message_count'),
            func.max(Message.created_at).label('last_message_at')
        ).select_from(
            Conversation
        ).outerjoin(
            Message, Conversation.id == Message.conversation_id
        ).where(
            Conversation.is_active == True
        ).group_by(
            Conversation.id,
            Conversation.title,
            Conversation.created_at,
            Conversation.updated_at
        ).order_by(
            desc(func.max(Message.created_at))
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return [
            {
                "id": row.id,
                "title": row.title,
                "created_at": row.created_at,
                "message_count": row.message_count or 0,
                "last_message_at": row.last_message_at
            }
            for row in result
        ]

class MessageCRUD:
    """CRUD operations for messages"""
    
    async def create(self, db: AsyncSession, *, obj_in: MessageCreate) -> Message:
        """Create a new message"""
        db_obj = Message(
            conversation_id=obj_in.conversation_id,
            content=obj_in.content,
            role=obj_in.role.value if hasattr(obj_in.role, 'value') else obj_in.role,
            workflow_id=getattr(obj_in, 'workflow_id', None)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update conversation's updated_at timestamp
        await db.execute(
            f"UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = {obj_in.conversation_id}"
        )
        await db.commit()
        
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
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for a specific conversation"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_messages(
        self, 
        db: AsyncSession, 
        *, 
        conversation_id: int,
        count: int = 10
    ) -> List[Message]:
        """Get recent messages for context"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(count)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Message, 
        obj_in: MessageUpdate
    ) -> Message:
        """Update message"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> Optional[Message]:
        """Delete message"""
        db_obj = await self.get(db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj
    
    async def get_conversation_stats(
        self, 
        db: AsyncSession, 
        *, 
        conversation_id: int
    ) -> dict:
        """Get statistics for a conversation"""
        result = await db.execute(
            select(
                func.count(Message.id).label('total_messages'),
                func.count().filter(Message.role == 'user').label('user_messages'),
                func.count().filter(Message.role == 'assistant').label('assistant_messages'),
                func.min(Message.created_at).label('first_message_at'),
                func.max(Message.created_at).label('last_message_at'),
                func.avg(Message.token_count).label('avg_token_count'),
                func.sum(Message.token_count).label('total_tokens')
            ).where(Message.conversation_id == conversation_id)
        )
        
        row = result.first()
        return {
            "total_messages": row.total_messages or 0,
            "user_messages": row.user_messages or 0,
            "assistant_messages": row.assistant_messages or 0,
            "first_message_at": row.first_message_at,
            "last_message_at": row.last_message_at,
            "avg_token_count": float(row.avg_token_count) if row.avg_token_count else 0,
            "total_tokens": row.total_tokens or 0
        }

# Create instances for use in the application
conversation_crud = ConversationCRUD()
message_crud = MessageCRUD()