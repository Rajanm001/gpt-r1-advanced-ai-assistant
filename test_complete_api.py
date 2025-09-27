import requests
import json

def test_chat_api():
    """Test the chat API endpoint"""
    
    print("🧪 Testing ChatGPT Clone API...")
    
    # Test health endpoint
    try:
        health_response = requests.get("http://localhost:8000/health")
        print(f"✅ Health Check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test conversations endpoint
    try:
        conv_response = requests.get("http://localhost:8000/api/v1/conversations")
        print(f"✅ Conversations: {conv_response.status_code} - {len(conv_response.json())} conversations")
    except Exception as e:
        print(f"❌ Conversations Failed: {e}")
        return
    
    # Test chat endpoint (streaming)
    try:
        chat_data = {
            "message": "Hello! Please respond with just 'Hi there!' to test the API.",
            "conversation_id": None
        }
        
        print("📡 Testing chat streaming...")
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=chat_data,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Chat API Response:")
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data = line_text[6:]
                        try:
                            parsed = json.loads(data)
                            if 'content' in parsed:
                                print(f"🤖: {parsed['content']}", end='', flush=True)
                            elif 'done' in parsed:
                                print(f"\n✅ Streaming complete! Conversation ID: {parsed.get('conversation_id')}")
                                break
                        except:
                            pass
        else:
            print(f"❌ Chat API Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Chat Test Failed: {e}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == "__main__":
    test_chat_api()