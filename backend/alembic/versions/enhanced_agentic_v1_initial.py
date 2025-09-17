"""Enhanced PostgreSQL schema with agentic workflow support

Revision ID: enhanced_agentic_v1
Revises: 
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'enhanced_agentic_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create enhanced PostgreSQL schema for GPT.R1 with agentic workflow support"""
    
    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for conversations
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'], unique=False)
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'], unique=False)
    op.create_index('ix_conversations_is_active', 'conversations', ['is_active'], unique=False)
    
    # Create messages table with agentic workflow support
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Integer(), nullable=True),
        sa.Column('workflow_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for messages
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)
    op.create_index('ix_messages_role', 'messages', ['role'], unique=False)
    op.create_index('ix_messages_workflow_id', 'messages', ['workflow_id'], unique=False)
    
    # Create composite indexes for common queries
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'], unique=False)
    op.create_index('ix_conversations_active_updated', 'conversations', ['is_active', 'updated_at'], unique=False)


def downgrade() -> None:
    """Drop the enhanced PostgreSQL schema"""
    
    # Drop indexes first
    op.drop_index('ix_conversations_active_updated', table_name='conversations')
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_workflow_id', table_name='messages')
    op.drop_index('ix_messages_role', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    
    op.drop_index('ix_conversations_is_active', table_name='conversations')
    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    
    # Drop tables
    op.drop_table('messages')
    op.drop_table('conversations')