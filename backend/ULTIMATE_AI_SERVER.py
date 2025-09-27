from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import uvicorn
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Optional
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key - try environment first, then fallback
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    # Fallback for demo purposes
    OPENROUTER_API_KEY = "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"
    
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

app = FastAPI(title="AI Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

def init_db():
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, 
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {
        "service": "AI Assistant", 
        "status": "🟢 Online & Ready",
        "version": "Enhanced v2.0",
        "frontend": "http://localhost:8000/static/MODERN_CHATGPT_UI.html",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Assistant",
        "version": "Enhanced v2.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/conversations")
def get_conversations():
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
    conversations = [{"id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return conversations

@app.post("/api/v1/conversations")
def create_conversation(request: dict):
    conversation_id = str(uuid.uuid4())
    title = request.get("title", "New Conversation")
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", (conversation_id, title))
    conn.commit()
    conn.close()
    return {"id": conversation_id, "title": title, "created_at": datetime.now().isoformat()}

@app.post("/api/chat")
async def enhanced_chat_stream(request: ChatRequest):
    """Enhanced streaming chat with faster, smarter responses"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Database operations
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # Get or create conversation
    cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", 
                      (conversation_id, f"Chat {conversation_id[:8]}"))
    
    # Save user message
    message_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                   (message_id, conversation_id, "user", request.message))
    
    # Get conversation history (limit to last 10 messages for faster processing)
    cursor.execute("""SELECT role, content FROM messages 
                     WHERE conversation_id = ? 
                     ORDER BY timestamp ASC 
                     LIMIT 10""", (conversation_id,))
    messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
    
    conn.commit()
    conn.close()
    
    async def generate_smart_response():
        """Generate enhanced AI responses"""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Assistant"
        }
        
        # Enhanced system prompt for smarter responses
        enhanced_messages = [
            {"role": "system", "content": """You are an advanced AI assistant. Respond intelligently, concisely, and helpfully. 
            Be professional yet friendly. Provide accurate information and practical solutions. 
            If asked about coding, provide clean, working examples. 
            Be creative and engaging while staying focused on the user's needs."""}
        ] + messages
        
        payload = {
            "model": MODEL_NAME,
            "messages": enhanced_messages,
            "stream": True,
            "temperature": 0.8,  # Slightly higher for more creative responses
            "max_tokens": 2500,  # More tokens for detailed responses
            "top_p": 0.9,       # Better response quality
            "frequency_penalty": 0.1,  # Reduce repetition
            "presence_penalty": 0.1    # Encourage diverse vocabulary
        }
        
        full_response = ""
        print(f"🤖 Enhanced AI processing: {request.message[:50]}...")
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                async with client.stream("POST", f"{OPENROUTER_BASE_URL}/chat/completions", 
                                       headers=headers, json=payload) as response:
                    
                    if response.status_code != 200:
                        error_content = await response.aread()
                        error_text = error_content.decode('utf-8')
                        print(f"❌ API Error {response.status_code}: {error_text}")
                        yield f"data: {json.dumps({'error': f'API Error: {response.status_code}'})}\n\n"
                        return
                    
                    print("✅ Streaming AI response...")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                json_data = json.loads(data)
                                if "choices" in json_data and json_data["choices"]:
                                    delta = json_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response += content
                                        # Send content in smaller chunks for smoother streaming
                                        yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                                        await asyncio.sleep(0.01)  # Small delay for smooth streaming
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                print(f"⚠️ Parse error: {e}")
                                continue
            
            # Save AI response
            if full_response.strip():
                conn = sqlite3.connect("conversations.db")
                cursor = conn.cursor()
                ai_message_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                               (ai_message_id, conversation_id, "assistant", full_response.strip()))
                conn.commit()
                conn.close()
                print(f"✅ Response saved ({len(full_response)} chars)")
            else:
                print("⚠️ Empty response received")
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except asyncio.TimeoutError:
            print("❌ Request timeout")
            yield f"data: {json.dumps({'error': 'Request timeout. Please try again.'})}\n\n"
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            yield f"data: {json.dumps({'error': f'Connection error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_smart_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Assistant Server...")
    print("🧠 Smart & Fast AI Responses")
    print("⚡ Optimized for Speed & Intelligence")
    print("🌐 Frontend: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    print("📡 Server: http://localhost:8000")
    print("💚 Health: http://localhost:8000/health")
    print("="*60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )