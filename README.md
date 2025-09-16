# 🤖 ChatGPT Clone - Full-Stack AI Assistant

A sophisticated, full-featured ChatGPT clone built with **FastAPI** and **Next.js**, featuring real-time streaming responses, conversation management, RAG capabilities with web search, and modern authentication.

![ChatGPT Clone](https://img.shields.io/badge/ChatGPT-Clone-blue?style=for-the-badge&logo=openai)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)

## ✨ Features

### 🔥 Core Features
- **Real-time Streaming**: Server-Sent Events for live message streaming
- **Conversation Management**: Persistent chat history with PostgreSQL
- **Modern UI**: Responsive design with dark/light mode
- **Authentication**: Secure JWT-based user authentication
- **Message History**: Full conversation persistence and retrieval

### 🚀 Advanced Features
- **RAG Integration**: Enhanced responses with DuckDuckGo web search
- **Markdown Support**: Rich text rendering with syntax highlighting
- **Mobile Responsive**: Optimized for all device sizes
- **Error Handling**: Comprehensive error management and user feedback
- **Performance Optimized**: Efficient database queries and caching

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI   │◄──►│   FastAPI API    │◄──►│  PostgreSQL DB  │
│   (Frontend)    │    │   (Backend)      │    │   (Database)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       
         │                       ▼                       
         │              ┌──────────────────┐             
         │              │   OpenAI API     │             
         │              │   + RAG Search   │             
         │              └──────────────────┘             
         │                                               
         ▼                                               
┌─────────────────┐                                     
│  Authentication │                                     
│  State Mgmt     │                                     
│  Theme System   │                                     
└─────────────────┘                                     
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Advanced open source database
- **Alembic**: Database migration tool
- **OpenAI API**: GPT integration for chat responses
- **DuckDuckGo Search**: Web search for RAG functionality
- **JWT Authentication**: Secure token-based auth

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: State management
- **React Markdown**: Markdown rendering
- **Lucide Icons**: Beautiful icon library
- **React Hot Toast**: Elegant notifications

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 13+
- OpenAI API Key

### 1. Clone Repository
```bash
git clone https://github.com/your-username/chatgpt-clone.git
cd chatgpt-clone
```

### 2. Environment Setup

#### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/chatgpt_clone
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Database Setup
```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
createdb chatgpt_clone

# Run migrations
cd backend
alembic upgrade head
```

### 4. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 6. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Quick Start with Docker Compose
```bash
# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Individual Services
```bash
# Backend only
docker build -t chatgpt-backend ./backend
docker run -p 8000:8000 chatgpt-backend

# Frontend only
docker build -t chatgpt-frontend ./frontend
docker run -p 3000:3000 chatgpt-frontend
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Chat Endpoints
- `POST /api/v1/chat` - Streaming chat (SSE)
- `POST /api/v1/chat/simple` - Non-streaming chat

### Conversation Endpoints
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation
- `POST /api/v1/conversations` - Create conversation
- `PUT /api/v1/conversations/{id}/title` - Update title

### Example API Usage

#### Streaming Chat
```javascript
const response = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: "Hello, how are you?",
    conversation_id: 1,
    use_rag: true
  })
});

const reader = response.body.getReader();
// Process streaming response...
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test with curl
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'
```

## 🔧 Configuration

### Backend Configuration
Key settings in `backend/app/core/config.py`:
- Database connection
- OpenAI API settings
- Authentication parameters
- CORS origins

### Frontend Configuration
Environment variables:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_NAME`: Application name

## 📱 Features Deep Dive

### Real-time Streaming
- Server-Sent Events (SSE) for live responses
- Chunk-by-chunk message delivery
- Real-time typing indicators
- Connection error handling

### RAG Integration
- DuckDuckGo search integration
- Context-aware responses
- Source attribution
- Fallback to base model

### Authentication System
- JWT token-based authentication
- Secure password hashing
- Session management
- Role-based access (extensible)

### Database Design
```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER REFERENCES conversations(id),
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Deployment

### Production Deployment

#### 1. Environment Variables
```bash
# Production .env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/chatgpt_clone
OPENAI_API_KEY=your_production_key
SECRET_KEY=your_secure_production_key
```

#### 2. Database Migration
```bash
alembic upgrade head
```

#### 3. Build & Deploy
```bash
# Backend
docker build -t chatgpt-backend:prod ./backend
docker run -d -p 8000:8000 chatgpt-backend:prod

# Frontend
docker build -t chatgpt-frontend:prod ./frontend
docker run -d -p 3000:3000 chatgpt-frontend:prod
```

### Cloud Deployment Options
- **Vercel**: Frontend deployment
- **Railway/Render**: Backend + Database
- **AWS/GCP**: Full stack deployment
- **Docker**: Containerized deployment

## 🔐 Security

### Implemented Security Measures
- JWT token authentication
- Password hashing with bcrypt
- SQL injection prevention
- CORS configuration
- Input validation
- Rate limiting (recommended)

### Security Best Practices
```python
# Secure headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Style
- **Backend**: Black, isort, flake8
- **Frontend**: Prettier, ESLint
- **Commits**: Conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- FastAPI team for the excellent framework
- Next.js team for the React framework
- All open source contributors

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Email**: your-email@example.com

---

**Built with ❤️ for the AI Engineer Assignment**

*This project demonstrates modern full-stack development practices with AI integration, streaming responses, and production-ready architecture.*