"""
GPT.R1 - Test with Database Mocking
Test that mocks database dependencies for isolated testing
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_app_with_mocked_database():
    """Test app creation with mocked database"""
    
    # Mock the database dependency
    mock_session = AsyncMock()
    
    with patch('app.core.database.get_db') as mock_get_db, \
         patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_engine:
        
        mock_get_db.return_value = mock_session
        mock_engine.return_value = MagicMock()
        
        try:
            from main import app
            from fastapi import FastAPI
            
            assert isinstance(app, FastAPI)
            print("✅ App creation with mocked database successful")
            return True
            
        except Exception as e:
            print(f"❌ App creation with mocked database failed: {e}")
            return False

def test_health_endpoint_with_mock():
    """Test health endpoint with mocked dependencies"""
    
    with patch('app.core.database.get_db') as mock_get_db, \
         patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_engine:
        
        mock_get_db.return_value = AsyncMock()
        mock_engine.return_value = MagicMock()
        
        try:
            from main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            
            print("✅ Health endpoint test with mocked database successful")
            return True
            
        except Exception as e:
            print(f"❌ Health endpoint test failed: {e}")
            return False

def test_imports():
    """Test that we can import key modules"""
    
    with patch('app.core.database.get_db') as mock_get_db, \
         patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_engine:
        
        mock_get_db.return_value = AsyncMock()
        mock_engine.return_value = MagicMock()
        
        try:
            # Test individual imports
            from app.services.chat_service import EnhancedChatService
            from app.services.agentic_service import AdvancedAgenticService
            from app.services.multi_tool_orchestrator import AdvancedToolOrchestrator
            
            print("✅ Service imports successful")
            
            from app.api.chat_enhanced import router
            from app.api.conversations import router as conv_router
            
            print("✅ API imports successful")
            
            return True
            
        except Exception as e:
            print(f"❌ Module imports failed: {e}")
            return False

def run_mocked_tests():
    """Run tests with database mocking"""
    print("🧪 Running mocked database tests...")
    
    tests = [
        test_imports,
        test_app_with_mocked_database,
        test_health_endpoint_with_mock
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Mocked Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All mocked tests passed!")
        return True
    else:
        print("🚨 Some mocked tests failed!")
        return False

if __name__ == "__main__":
    success = run_mocked_tests()
    sys.exit(0 if success else 1)