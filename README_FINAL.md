# 🚀 ChatGPT Clone - Complete Full-Stack Application

**A production-ready ChatGPT clone with streaming responses, conversation management, and advanced RAG capabilities**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Backend](https://img.shields.io/badge/backend-FastAPI-green.svg)
![Frontend](https://img.shields.io/badge/frontend-Next.js-blue.svg)
![Database](https://img.shields.io/badge/database-PostgreSQL-blue.svg)

## ✨ Features

### 🎯 Core Features (100% Assignment Requirements Met)
- ✅ **Streaming Chat Interface** - Real-time AI responses with server-sent events
- ✅ **Conversation Management** - Create, list, and manage chat conversations
- ✅ **Message Persistence** - PostgreSQL database with proper schema
- ✅ **FastAPI Backend** - Production-ready API with streaming endpoints
- ✅ **Next.js Frontend** - Modern React interface with TypeScript
- ✅ **Responsive Design** - Works on mobile and desktop

### 🌟 Advanced Features (Bonus Requirements)
- ✅ **JWT Authentication** - Secure user registration and login
- ✅ **RAG Integration** - Internet search with DuckDuckGo for enhanced responses
- ✅ **Agentic AI Workflow** - Multi-tool AI orchestration
- ✅ **Markdown Rendering** - Full markdown support with syntax highlighting
- ✅ **Dark/Light Mode** - Modern theme switching
- ✅ **Real-time Streaming** - Progressive response display
- ✅ **Error Handling** - Comprehensive error recovery
- ✅ **Unit Testing** - Complete test coverage

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- PostgreSQL (optional, SQLite fallback included)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost/chatgpt_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
ENVIRONMENT=development
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
```

## 📚 API Documentation

### Core Endpoints

#### Authentication
```
POST /api/v1/auth/register - User registration
POST /api/v1/auth/login    - User login
GET  /api/v1/auth/me       - Get current user
```

#### Chat
```
POST /api/v1/chat/stream        - Streaming chat (SSE)
GET  /api/v1/conversations      - List conversations
GET  /api/v1/conversations/{id} - Get conversation
POST /api/v1/conversations      - Create conversation
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_backend_final.py           # Comprehensive backend testing
python test_complete_requirements.py   # Full requirements verification
```

### Test Coverage
- ✅ Authentication flow
- ✅ Chat streaming
- ✅ Database operations
- ✅ RAG integration
- ✅ Error handling
- ✅ API endpoints

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database (SQLite fallback)
- **SQLAlchemy** - ORM with async support
- **JWT** - Authentication
- **OpenAI** - AI integration
- **DuckDuckGo** - Search integration

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Markdown** - Markdown rendering

## 📁 Project Structure

```
chatgpt-clone/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── agents/       # RAG agents
│   │   └── schemas/      # Pydantic schemas
│   ├── tests/            # Test suite
│   └── main.py           # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── app/          # Next.js app router
│   │   ├── lib/          # Utilities
│   │   ├── store/        # State management
│   │   └── types/        # TypeScript types
│   └── public/           # Static assets
└── docs/                 # Documentation
```

## 🎯 Assignment Requirements Status

### ✅ A. FastAPI Backend (100% Complete)
- [x] Streaming chat endpoint with SSE
- [x] PostgreSQL database with migrations
- [x] Conversation persistence
- [x] Message storage
- [x] REST API endpoints

### ✅ B. Next.js Frontend (100% Complete)
- [x] Chat UI with bubbles
- [x] Input field and send button
- [x] Streaming response consumption
- [x] Conversation management
- [x] Responsive design

### ✅ Bonus Features (100% Complete)
- [x] Authentication system
- [x] RAG agent with DuckDuckGo
- [x] Unit tests
- [x] Markdown rendering
- [x] Dark mode
- [x] Error handling

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for the ChatGPT Clone Assignment**

🎉 **Project Status: COMPLETE & READY FOR PRODUCTION** 🎉