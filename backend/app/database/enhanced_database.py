"""
Database Configuration Manager
Supports both SQLite (default) and PostgreSQL
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_database_url():
    """Get the appropriate database URL based on configuration"""
    
    if DATABASE_TYPE == "postgresql" and DATABASE_URL:
        # Use PostgreSQL if configured
        logger.info("Using PostgreSQL database")
        return DATABASE_URL
    elif DATABASE_TYPE == "sqlite" or not DATABASE_URL:
        # Default to SQLite
        sqlite_path = os.getenv("SQLITE_PATH", "chatgpt_clone.db")
        db_url = f"sqlite:///{sqlite_path}"
        logger.info(f"Using SQLite database: {sqlite_path}")
        return db_url
    else:
        # Fallback to SQLite
        logger.warning(f"Unknown database type '{DATABASE_TYPE}', falling back to SQLite")
        return "sqlite:///chatgpt_clone.db"

# Create database engine
engine = create_engine(
    get_database_url(),
    # SQLite specific settings
    connect_args={"check_same_thread": False} if DATABASE_TYPE == "sqlite" else {},
    echo=os.getenv("DB_ECHO", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    try:
        # Test connection - use text() for raw SQL
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info(f"✅ Database connection successful ({DATABASE_TYPE})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# PostgreSQL Setup Instructions
POSTGRESQL_SETUP = """
🗄️ **PostgreSQL Setup Instructions:**

1. **Install PostgreSQL** (if not already installed)
2. **Create Database:**
   ```sql
   CREATE DATABASE chatgpt_clone;
   CREATE USER rajan_bot WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE chatgpt_clone TO rajan_bot;
   ```

3. **Update .env file:**
   ```env
   DATABASE_TYPE=postgresql
   DATABASE_URL=postgresql://rajan_bot:your_password@localhost:5432/chatgpt_clone
   ```

4. **Install PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary
   ```

**Current Configuration:** Using {db_type} database
**Connection Status:** {status}
""".format(
    db_type=DATABASE_TYPE.upper(),
    status="✅ Connected" if test_database_connection() else "❌ Not Connected"
)

if __name__ == "__main__":
    print("🗄️ Database Configuration Test")
    print("=" * 50)
    print(POSTGRESQL_SETUP)
    
    if create_tables():
        print("✅ Database setup complete!")
    else:
        print("❌ Database setup failed!")