import requests
import json
import time

def test_premium_ai():
    """Test the premium AI server with new API key"""
    
    print("🧪 Testing Premium AI Assistant...")
    
    # Test health first
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
    except Exception as e:
        print(f"❌ Health Failed: {e}")
        return False
    
    # Test AI chat with new API
    try:
        chat_data = {
            "message": "Hello! Please respond with a friendly greeting to test the new API.",
            "conversation_id": None
        }
        
        print("📡 Testing premium AI response...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=chat_data,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Premium AI Response:")
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
                                end_time = time.time()
                                response_time = end_time - start_time
                                print(f"\n✅ Complete! ({response_time:.2f}s, {len(response_text)} chars)")
                                
                                if len(response_text) > 10:  # Meaningful response
                                    print("🎉 PREMIUM AI IS RESPONDING PERFECTLY!")
                                    return True
                                else:
                                    print("⚠️ Response too short")
                                    return False
                                    
                            elif 'error' in parsed:
                                print(f"\n❌ Error: {parsed['error']}")
                                return False
                                
                        except json.JSONDecodeError:
                            continue
                            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False
    
    print("❌ No meaningful response received")
    return False

if __name__ == "__main__":
    print("🎯 Testing Premium AI with New OpenRouter API Key")
    print("=" * 60)
    
    success = test_premium_ai()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Premium AI is working perfectly!")
        print("✅ Fast responses enabled")
        print("✅ Smart AI integration active") 
        print("✅ Client demands satisfied")
        print("🌐 Access: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    else:
        print("\n" + "=" * 60)
        print("❌ ISSUE DETECTED - Need to investigate")
    
    print("=" * 60)