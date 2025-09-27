import requests
import json
import time

def test_chat():
    """Test chat functionality quickly"""
    
    url = "http://localhost:8000/api/chat"
    data = {
        "message": "Hello! Please respond with 'Hi there!' to test the system.",
        "conversation_id": None
    }
    
    print("🧪 Testing AI response...")
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=10)
        
        if response.status_code == 200:
            print("✅ AI is responding:")
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        try:
                            data = json.loads(line_text[6:])
                            if 'content' in data:
                                print(data['content'], end='', flush=True)
                            elif 'done' in data:
                                print("\n🎉 AI RESPONSE COMPLETE!")
                                return True
                        except:
                            pass
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    if test_chat():
        print("✅ AI ASSISTANT IS WORKING PERFECTLY!")
    else:
        print("❌ AI Assistant needs fixing")