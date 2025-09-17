"""
GPT.R1 - Simple Test Verification
Basic test to verify the test framework is working
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_simple_import():
    """Test that we can import the main app"""
    try:
        from main import app
        assert app is not None
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    print("✅ Basic functionality test passed")
    return True

def test_fastapi_app_creation():
    """Test FastAPI app creation"""
    try:
        from fastapi import FastAPI
        from main import app
        
        assert isinstance(app, FastAPI)
        print("✅ FastAPI app creation test passed")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation test failed: {e}")
        return False

def run_verification_tests():
    """Run all verification tests"""
    print("🧪 Running test verification...")
    
    tests = [
        test_basic_functionality,
        test_simple_import,
        test_fastapi_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        return True
    else:
        print("🚨 Some verification tests failed!")
        return False

if __name__ == "__main__":
    success = run_verification_tests()
    sys.exit(0 if success else 1)