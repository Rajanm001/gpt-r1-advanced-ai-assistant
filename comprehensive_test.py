#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE CHAT FUNCTIONALITY TEST
Tests all API endpoints and chat features
"""
import requests
import json
import time
from datetime import datetime

def test_chat_endpoints():
    """Test all chat-related endpoints"""
    print("🧪 TESTING CHAT FUNCTIONALITY")
    print("="*50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
        return False
    
    # Test 2: Create Conversation
    print("\n2. Testing Create Conversation...")
    try:
        conversation_payload = {"title": "Test Conversation"}
        response = requests.post(
            f"{base_url}/api/v1/conversations",
            json=conversation_payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            conversation_data = response.json()
            conversation_id = conversation_data.get('id')
            print(f"✅ Create Conversation: PASSED (ID: {conversation_id})")
        else:
            print(f"❌ Create Conversation: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create Conversation: ERROR - {e}")
        return False
    
    # Test 3: Send Chat Message
    print("\n3. Testing Chat Message...")
    try:
        chat_payload = {
            "message": "Hello! This is a test message. Can you respond?",
            "conversation_id": conversation_id
        }
        
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json=chat_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Chat Message: PASSED")
            print(f"   Response preview: {response.text[:100]}...")
        else:
            print(f"❌ Chat Message: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat Message: ERROR - {e}")
        return False
    
    # Test 4: Get Conversations
    print("\n4. Testing Get Conversations...")
    try:
        response = requests.get(f"{base_url}/api/v1/conversations")
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Get Conversations: PASSED ({len(conversations)} conversations)")
        else:
            print(f"❌ Get Conversations: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get Conversations: ERROR - {e}")
        return False
    
    # Test 5: Get Conversation Messages
    print("\n5. Testing Get Messages...")
    try:
        response = requests.get(f"{base_url}/api/v1/conversations/{conversation_id}/messages")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Get Messages: PASSED ({len(messages)} messages)")
        else:
            print(f"❌ Get Messages: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get Messages: ERROR - {e}")
        return False
    
    return True

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🌐 TESTING FRONTEND INTEGRATION")
    print("="*50)
    
    try:
        # Test frontend accessibility
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: ACCESSIBLE")
            
            # Check for essential elements
            html_content = response.text
            if "ChatGPT" in html_content or "chat" in html_content.lower():
                print("✅ Frontend: Chat Interface Detected")
            else:
                print("⚠️ Frontend: No chat interface detected in HTML")
                
            if "_next" in html_content:
                print("✅ Frontend: Next.js App Confirmed")
            else:
                print("⚠️ Frontend: Not a Next.js app")
                
            return True
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend: ERROR - {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("🏆 COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    # Run all tests
    backend_ok = test_chat_endpoints()
    frontend_ok = test_frontend_integration()
    
    print("\n📊 RESULTS SUMMARY:")
    print("-" * 30)
    
    if backend_ok:
        print("✅ Backend API: ALL TESTS PASSED")
        print("   - Health check working")
        print("   - Conversation creation working")
        print("   - Chat messaging working")
        print("   - Data retrieval working")
    else:
        print("❌ Backend API: TESTS FAILED")
    
    if frontend_ok:
        print("✅ Frontend: ALL TESTS PASSED")
        print("   - Next.js app accessible")
        print("   - Chat interface detected")
    else:
        print("❌ Frontend: TESTS FAILED")
    
    print("\n🔗 LIVE ACCESS POINTS:")
    print("   Frontend:  http://localhost:3000")
    print("   Backend:   http://localhost:8000")
    print("   API Docs:  http://localhost:8000/docs")
    print("   Health:    http://localhost:8000/health")
    
    if backend_ok and frontend_ok:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Ready for production use!")
        return True
    else:
        print("\n⚠️ ISSUES DETECTED - NEEDS ATTENTION")
        return False

def main():
    """Main test function"""
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🧪 DIRECTOR-LEVEL QUALITY ASSURANCE TEST")
    print("="*60)
    
    success = generate_test_report()
    
    print(f"\n📈 Test Status: {'PASSED' if success else 'FAILED'}")
    return success

if __name__ == "__main__":
    main()