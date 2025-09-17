"""
GPT.R1 - Conversation CRUD Operations
PostgreSQL async CRUD operations for conversations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.schemas.chat import ConversationCreate, ConversationUpdate

class ConversationCRUD:
    """CRUD operations for conversations"""
    
    async def create(self, db: AsyncSession, *, obj_in: ConversationCreate) -> Conversation:
        """Create new conversation"""
        db_obj = Conversation(
            title=obj_in.title
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        result = await db.execute(
            select(Conversation).where(Conversation.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Conversation]:
        """Get multiple conversations"""
        result = await db.execute(
            select(Conversation)
            .offset(skip)
            .limit(limit)
            .order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_conversation_summaries(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get conversation summaries with message counts"""
        query = text("""
            SELECT 
                c.id,
                c.title,
                c.created_at,
                COALESCE(COUNT(m.id), 0) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id, c.title, c.created_at
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await db.execute(query, {"limit": limit, "skip": skip})
        rows = result.fetchall()
        
        return [
            {
                "id": row.id,
                "title": row.title,
                "created_at": row.created_at.isoformat(),
                "message_count": row.message_count
            }
            for row in rows
        ]
    
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
        
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: int) -> bool:
        """Delete conversation"""
        conversation = await self.get(db, id=id)
        if conversation:
            await db.delete(conversation)
            return True
        return False

# Create instance
conversation_crud = ConversationCRUD()