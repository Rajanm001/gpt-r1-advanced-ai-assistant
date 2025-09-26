"""
Test script to verify backend functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import engine, Base
from app.services.chat_service import ChatService

def test_database():
    """Test database connection"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_chat_service():
    """Test chat service"""
    try:
        chat_service = ChatService()
        print("✅ Chat service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Chat service error: {e}")
        return False

def main():
    print("🚀 Testing backend components...")
    
    db_ok = test_database()
    chat_ok = test_chat_service()
    
    if db_ok and chat_ok:
        print("\n✅ All backend components working!")
        return True
    else:
        print("\n❌ Some components have issues")
        return False

if __name__ == "__main__":
    main()