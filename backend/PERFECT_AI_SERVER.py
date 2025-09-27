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

app = FastAPI(title="AI Assistant API")

# CORS middleware for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, 
        title TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, 
        conversation_id TEXT, 
        role TEXT, 
        content TEXT, 
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.get("/")
def root():
    return {
        "service": "AI Assistant", 
        "status": "🟢 Online & Ready",
        "frontend": "http://localhost:8000/static/MODERN_CHATGPT_UI.html",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Assistant",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/conversations")
def get_conversations():
    """Get all conversations"""
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
    conversations = [{"id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return conversations

@app.post("/api/v1/conversations")
def create_conversation(request: dict):
    """Create new conversation"""
    conversation_id = str(uuid.uuid4())
    title = request.get("title", "New Conversation")
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", (conversation_id, title))
    conn.commit()
    conn.close()
    return {"id": conversation_id, "title": title, "created_at": datetime.now().isoformat()}

@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Enhanced streaming chat endpoint - Fast & Smart AI responses"""
    
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
    
    # Get conversation history
    cursor.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC LIMIT 20", 
                   (conversation_id,))
    messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
    
    conn.commit()
    conn.close()
    
    async def generate_response():
        """Generate smart, fast AI responses"""
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Assistant"
        }
        
        # Optimized payload for fast, smart responses
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        full_response = ""
        print(f"🤖 Processing: {request.message[:50]}...")
        
        try:
            timeout = httpx.Timeout(60.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", f"{OPENROUTER_BASE_URL}/chat/completions", 
                                       headers=headers, json=payload) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = error_text.decode('utf-8')
                        print(f"❌ API Error: {response.status_code} - {error_msg}")
                        yield f"data: {json.dumps({'error': f'Sorry, I encountered an error. Please try again.'})}\n\n"
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
                                    content = json_data["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        full_response += content
                                        yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                                        # Small delay for smooth streaming
                                        await asyncio.sleep(0.01)
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                print(f"⚠️ Parse error: {e}")
                                continue
            
            # Save AI response to database
            if full_response.strip():
                conn = sqlite3.connect("conversations.db")
                cursor = conn.cursor()
                ai_message_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                               (ai_message_id, conversation_id, "assistant", full_response))
                conn.commit()
                conn.close()
                print(f"✅ Response saved: {len(full_response)} characters")
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except httpx.TimeoutException:
            print("❌ Request timeout")
            yield f"data: {json.dumps({'error': 'Request timed out. Please try again.'})}\n\n"
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            yield f"data: {json.dumps({'error': 'I encountered an unexpected error. Please try again.'})}\n\n"
    
    return StreamingResponse(
        generate_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

if __name__ == "__main__":
    print("🚀 Starting Advanced AI Assistant...")
    print("✨ Fast, Smart, and Responsive")
    print(f"🤖 Model: {MODEL_NAME}")
    print("🌐 Frontend: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    print("📡 Server: http://localhost:8000")
    print("💚 Health: http://localhost:8000/health")
    print("=" * 50)
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )