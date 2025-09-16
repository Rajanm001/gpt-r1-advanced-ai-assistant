from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Use the smart database URL selection
database_url = settings.DATABASE_URL

print(f"🗄️ Database URL: {database_url}")

# Configure engine based on database type
if database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},  # Required for SQLite
        echo=settings.DEBUG  # Show SQL queries in debug mode
    )
    print("📊 Database: SQLite (Fallback Mode)")
else:
    # PostgreSQL configuration
    engine = create_engine(
        database_url,
        echo=settings.DEBUG
    )
    print("🐘 Database: PostgreSQL (Production Mode)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    from app.models import User, Conversation, Message  # Import models
    Base.metadata.create_all(bind=engine)