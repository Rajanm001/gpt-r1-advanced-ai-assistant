"""
Development Database Helper
Creates a temporary PostgreSQL connection for testing or falls back to SQLite for development
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

logger = logging.getLogger(__name__)

async def check_postgresql_connection():
    """Check if PostgreSQL is available and create database if needed"""
    try:
        # Try to connect to PostgreSQL server (without specific database)
        engine = create_async_engine("postgresql+asyncpg://postgres:admin@localhost:5432/postgres", echo=False)
        
        async with engine.begin() as conn:
            # Check if our database exists
            result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'gpt_r1_db'"))
            exists = result.fetchone()
            
            if not exists:
                # Create the database
                await conn.execute(text("CREATE DATABASE gpt_r1_db"))
                logger.info("✅ Created database 'gpt_r1_db'")
            else:
                logger.info("✅ Database 'gpt_r1_db' already exists")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def create_development_database_url():
    """Create appropriate database URL for development"""
    # For development, we'll use SQLite if PostgreSQL is not available
    # But production should ALWAYS use PostgreSQL
    
    postgres_url = "postgresql+asyncpg://postgres:admin@localhost:5432/gpt_r1_db"
    sqlite_url = "sqlite+aiosqlite:///./gpt_r1_dev.db"
    
    # Check environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return postgres_url  # Production MUST use PostgreSQL
    
    # For development, try PostgreSQL first, fall back to SQLite
    try:
        # Quick sync check for PostgreSQL availability
        sync_engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres")
        sync_engine.connect()
        sync_engine.dispose()
        logger.info("🐘 Using PostgreSQL for development")
        return postgres_url
    except:
        logger.warning("⚠️ PostgreSQL not available, using SQLite for development")
        logger.warning("📝 For production deployment, ensure PostgreSQL is properly configured")
        return sqlite_url

if __name__ == "__main__":
    # Test the connection
    asyncio.run(check_postgresql_connection())