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

# Get API key from environment or use default for demo
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

app = FastAPI(title="ChatGPT Clone API")

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
        "service": "ChatGPT Clone API", 
        "status": "🟢 Online & Ready",
        "model": MODEL_NAME,
        "frontend": "http://localhost:8000/static/MODERN_CHATGPT_UI.html",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ChatGPT Clone API",
        "model": MODEL_NAME,
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
async def chat_stream(request: ChatRequest):
    """Enhanced streaming chat endpoint"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
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
    cursor.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", 
                   (conversation_id,))
    messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
    
    conn.commit()
    conn.close()
    
    async def generate():
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "ChatGPT Clone"
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        full_response = ""
        print(f"🤖 Streaming from OpenRouter for: {request.message}...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", f"{OPENROUTER_BASE_URL}/chat/completions", 
                                       headers=headers, json=payload) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.atext()
                        print(f"❌ OpenRouter API Error: {response.status_code} - {error_text}")
                        yield f"data: {json.dumps({'error': f'API Error {response.status_code}: {error_text}'})}\n\n"
                        return
                    
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
                            except json.JSONDecodeError:
                                continue
            
            # Save AI response to database
            if full_response:
                conn = sqlite3.connect("conversations.db")
                cursor = conn.cursor()
                message_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                               (message_id, conversation_id, "assistant", full_response))
                conn.commit()
                conn.close()
                print(f"✅ AI response saved to database")
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            print(f"❌ Error in chat stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    print("🚀 Starting ChatGPT Clone Server...")
    print(f"🤖 Model: {MODEL_NAME}")
    print("✅ OpenRouter API Integration")
    print("🌐 Frontend: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    print("📡 Server: http://localhost:8000")
    print("💚 Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)