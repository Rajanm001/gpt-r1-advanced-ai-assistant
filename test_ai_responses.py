import requests
import json
import time

def test_ai_responses():
    """Test if AI responses are working"""
    
    print("🧪 Testing AI Assistant Responses...")
    
    # Test health first
    try:
        health_response = requests.get("http://localhost:8000/health")
        print(f"✅ Health: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"❌ Health Failed: {e}")
        return
    
    # Test AI chat
    try:
        chat_data = {
            "message": "Hi! Just say 'Hello!' back to test.",
            "conversation_id": None
        }
        
        print("📡 Testing AI response...")
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=chat_data,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ AI Response received:")
            response_text = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data = line_text[6:]
                        try:
                            parsed = json.loads(data)
                            if 'content' in parsed:
                                content = parsed['content']
                                response_text += content
                                print(content, end='', flush=True)
                            elif 'done' in parsed:
                                print(f"\n✅ Complete! Response length: {len(response_text)} characters")
                                if len(response_text) > 0:
                                    print("🎉 AI IS RESPONDING CORRECTLY!")
                                    return True
                                else:
                                    print("❌ Empty response received")
                                    return False
                            elif 'error' in parsed:
                                print(f"\n❌ Error: {parsed['error']}")
                                return False
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False
    
    print("❌ No response received")
    return False

if __name__ == "__main__":
    success = test_ai_responses()
    if success:
        print("\n🎉 ALL TESTS PASSED - AI IS WORKING!")
    else:
        print("\n❌ TESTS FAILED - AI NOT RESPONDING")
    
    input("\nPress Enter to close...")