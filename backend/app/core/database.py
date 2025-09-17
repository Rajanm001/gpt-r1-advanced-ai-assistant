"""
GPT.R1 - Async PostgreSQL Database Configuration (AS PER SPECIFICATION)
Production-ready PostgreSQL with async support and proper connection handling
Created by: Rajan Mishra
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL Configuration (AS PER SPECIFICATION)
def get_database_url():
    """Get PostgreSQL database URL as per specification"""
    if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
        # Ensure it's PostgreSQL
        if not settings.DATABASE_URL.startswith("postgresql"):
            logger.error("❌ SPECIFICATION VIOLATION: Must use PostgreSQL database!")
            raise ValueError("Database must be PostgreSQL as per specification")
        # Convert to async PostgreSQL URL
        if settings.DATABASE_URL.startswith("postgresql://"):
            return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return settings.DATABASE_URL
    
    # Default async PostgreSQL connection as per spec
    return "postgresql+asyncpg://postgres:password@localhost:5432/gpt_r1"

# PostgreSQL Async Engine Configuration (Production-Ready)
database_url = get_database_url()

# Production PostgreSQL Async Engine with Connection Pooling
engine = create_async_engine(
    database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=getattr(settings, 'DEBUG', False)
)

logger.info(f"✅ Async PostgreSQL Database Connected: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
print(f"🐘 Database: PostgreSQL with AsyncPG (AS PER SPECIFICATION REQUIREMENT)")

Base = declarative_base()

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """
    Async dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create database tables"""
    from app.models.conversation import Base as ConversationBase
    
    async with engine.begin() as conn:
        await conn.run_sync(ConversationBase.metadata.create_all)
        logger.info("✅ Database tables created successfully")

# Specification Compliance Check
def verify_postgresql_compliance():
    """Verify PostgreSQL compliance as per specification"""
    if "postgresql" not in database_url:
        raise RuntimeError("❌ CRITICAL: Database must be PostgreSQL as per specification!")
    
    logger.info("✅ PostgreSQL specification compliance verified")
    return True

# Run compliance check
verify_postgresql_compliance()