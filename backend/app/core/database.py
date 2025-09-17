"""
GPT.R1 - Async Database Configuration (PostgreSQL Primary, Development Fallback)
Production-ready PostgreSQL with async support and development SQLite fallback
Created by: Rajan Mishra
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database Configuration with Development Fallback
def get_database_url():
    """Get database URL - PostgreSQL for production, SQLite fallback for development"""
    environment = getattr(settings, 'ENVIRONMENT', 'development')
    
    if environment == 'production':
        # Production MUST use PostgreSQL
        return settings.get_database_url()
    else:
        # Development: try PostgreSQL first, fallback to SQLite
        postgres_url = settings.DATABASE_URL
        sqlite_url = "sqlite+aiosqlite:///./gpt_r1_dev.db"
        
        try:
            # Quick test for PostgreSQL availability (sync check)
            from sqlalchemy import create_engine
            sync_engine = create_engine(postgres_url.replace('+asyncpg', ''))
            sync_engine.connect()
            sync_engine.dispose()
            logger.info("🐘 Using PostgreSQL (Primary Database)")
            return postgres_url
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL not available ({e}), using SQLite for development")
            logger.warning("📝 For production, ensure PostgreSQL is configured")
            return sqlite_url

# Get Database URL
database_url = get_database_url()

# Create appropriate engine based on database type
if "sqlite" in database_url:
    # SQLite configuration for development
    engine = create_async_engine(
        database_url,
        echo=getattr(settings, 'DEBUG', False)
    )
    logger.info("📁 Development Database: SQLite with aiosqlite")
else:
    # PostgreSQL configuration for production
    engine = create_async_engine(
        database_url,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=getattr(settings, 'DEBUG', False)
    )
    logger.info(f"🐘 Production Database: PostgreSQL with AsyncPG")

print(f"🗄️ Database: {database_url.split('://')[0].upper().replace('+AIOSQLITE', '').replace('+ASYNCPG', '')} ({'Production' if 'postgresql' in database_url else 'Development'})")

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
    environment = getattr(settings, 'ENVIRONMENT', 'development')
    
    if environment == 'production' and "postgresql" not in database_url:
        raise RuntimeError("❌ CRITICAL: Production database must be PostgreSQL as per specification!")
    
    if "postgresql" in database_url:
        logger.info("✅ PostgreSQL specification compliance verified")
    else:
        logger.warning("⚠️ Development mode: Using SQLite fallback (Production requires PostgreSQL)")
    
    return True

# Run compliance check
verify_postgresql_compliance()