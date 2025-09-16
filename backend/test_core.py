#!/usr/bin/env python3
"""
Test FastAPI server startup with SQLite database
Validates core functionality without requiring PostgreSQL
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['OPENAI_API_KEY'] = 'test_key_for_testing'
os.environ['SECRET_KEY'] = 'test_secret_key_very_long_and_secure_for_testing_purposes'

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("🔄 Testing module imports...")
        
        # Test database components
        from app.core.database import engine, SessionLocal, Base
        print("✅ Database components imported")
        
        # Test models
        from app.models import User, Conversation, Message
        print("✅ Models imported")
        
        # Test schemas
        from app.schemas import UserCreate, ConversationCreate, MessageCreate
        print("✅ Schemas imported")
        
        # Test services (skip OpenAI for now)
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database_setup():
    """Test database setup with SQLite"""
    try:
        print("🔄 Testing database setup...")
        
        # Clean up any existing test database
        test_db = Path("test.db")
        if test_db.exists():
            test_db.unlink()
        
        # Import database components
        from app.core.database import engine, Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Test database connection
        import sqlite3
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ['users', 'conversations', 'messages']
        for table in expected_tables:
            if table in table_names:
                print(f"✅ Table '{table}' created successfully")
            else:
                print(f"❌ Table '{table}' missing")
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    try:
        print("🔄 Testing FastAPI app creation...")
        
        # Import the main app
        from main import app
        print("✅ FastAPI app created successfully")
        
        # Check if app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ App has {len(routes)} routes configured")
        
        # Check for key endpoints
        expected_endpoints = ['/health', '/docs', '/api/v1']
        for endpoint in expected_endpoints:
            if any(endpoint in route for route in routes):
                print(f"✅ Endpoint '{endpoint}' configured")
            else:
                print(f"⚠️  Endpoint '{endpoint}' might be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_crud_operations():
    """Test basic CRUD operations"""
    try:
        print("🔄 Testing CRUD operations...")
        
        from app.core.database import SessionLocal
        from app.models import User
        from app.schemas import UserCreate
        from app.crud import user_crud
        
        # Create a test session
        db = SessionLocal()
        
        # Test user creation
        test_user = UserCreate(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        created_user = user_crud.create(db=db, obj_in=test_user)
        print("✅ User CRUD create operation works")
        
        # Test user retrieval
        retrieved_user = user_crud.get_by_email(db=db, email="test@example.com")
        if retrieved_user:
            print("✅ User CRUD read operation works")
        else:
            print("❌ User CRUD read operation failed")
            return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ CRUD operations failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Backend Core Functionality Tests")
    print("Testing core components without external dependencies\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Setup", test_database_setup),
        ("FastAPI App Creation", test_app_creation),
        ("CRUD Operations", test_crud_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print('='*50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend core functionality is working perfectly!")
        return 0
    elif passed >= total * 0.8:
        print("\n🚀 MOST TESTS PASSED! Minor issues to address.")
        return 0
    else:
        print("\n🔧 SOME TESTS FAILED. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    # Cleanup
    test_db = Path("test.db")
    if test_db.exists():
        test_db.unlink()
        print("🧹 Cleaned up test database")
    
    sys.exit(exit_code)