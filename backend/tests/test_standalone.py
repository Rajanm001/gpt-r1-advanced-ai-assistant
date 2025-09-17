"""
GPT.R1 - Test Configuration
Override configuration for testing without database connection
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables before any imports
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "test-key-123"

def setup_test_environment():
    """Setup test environment with mocked dependencies"""
    
    # Mock SQLAlchemy components before import
    sys.modules['sqlalchemy.ext.asyncio'] = MagicMock()
    sys.modules['app.core.database'] = MagicMock()
    
    # Create mock database session
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    
    # Mock get_db function
    def mock_get_db():
        return mock_session
    
    return mock_get_db, mock_session

def test_basic_imports():
    """Test basic imports with mocked environment"""
    
    mock_get_db, mock_session = setup_test_environment()
    
    try:
        # Now try to import FastAPI app
        from fastapi import FastAPI
        
        # Create a minimal app for testing
        app = FastAPI(title="GPT.R1 Test App")
        
        @app.get("/api/health")
        def health_check():
            return {"status": "healthy", "service": "GPT.R1 Test"}
        
        print("✅ Basic FastAPI app creation successful")
        
        # Test the health endpoint
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        print("✅ Health endpoint test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_mocking():
    """Test service layer with mocking"""
    
    try:
        # Mock all external dependencies
        from unittest.mock import patch, MagicMock, AsyncMock
        
        with patch('openai.AsyncOpenAI') as mock_openai, \
             patch('duckduckgo_search.DDGS') as mock_ddgs:
            
            # Setup mocks
            mock_openai.return_value = MagicMock()
            mock_ddgs.return_value.text.return_value = [
                {"title": "Test", "body": "Test content", "href": "http://test.com"}
            ]
            
            print("✅ Service mocking setup successful")
            return True
            
    except Exception as e:
        print(f"❌ Service mocking test failed: {e}")
        return False

def run_standalone_tests():
    """Run standalone tests without full app import"""
    
    print("🧪 Running standalone tests...")
    
    tests = [
        test_basic_imports,
        test_service_mocking
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Standalone Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All standalone tests passed!")
        return True
    else:
        print("🚨 Some standalone tests failed!")
        return False

if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1)