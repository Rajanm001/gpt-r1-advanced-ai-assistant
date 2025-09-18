# 🚀 GPT.R1 - Advanced AI Assistant

> **Created by Rajan Mishra** - A professional-grade AI assistant with enterprise features

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant/actions)

GPT.R1 is an enterprise-grade AI assistant built with modern technologies, featuring real-time streaming, advanced RAG capabilities, and a beautiful user interface. This project demonstrates full-stack development expertise and professional software engineering practices.

## ✨ Key Features

- **🔄 Real-time Streaming**: Live response streaming with Server-Sent Events
- **💬 Conversation Management**: Persistent chat history with PostgreSQL
- **🔐 Authentication**: Secure JWT-based user authentication
- **🎨 Modern UI**: Beautiful, responsive interface with dark mode
- **📱 Mobile Responsive**: Optimized for all device sizes
- **🔍 RAG Enhancement**: Web search integration via DuckDuckGo
- **⚡ High Performance**: Async/await architecture with optimized queries
- **🛡️ Enterprise Security**: Input validation, rate limiting, secure headers
- **📊 Production Ready**: Docker support, health checks, monitoring
- **🧪 Comprehensive Testing**: Full test coverage with CI/CD pipeline

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│ (PostgreSQL)    │
│                 │    │                 │    │                 │
│ • React/TS      │    │ • Python 3.11+ │    │ • User Data     │
│ • Tailwind CSS  │    │ • SQLAlchemy    │    │ • Conversations │
│ • Real-time UI  │    │ • Streaming API │    │ • Messages      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                    ┌─────────────────┐
                    │  External APIs  │
                    │                 │
                    │ • OpenAI GPT    │
                    │ • DuckDuckGo    │
                    │ • Redis Cache   │
                    └─────────────────┘
```

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT tokens with secure password hashing
- **AI Integration**: OpenAI API with streaming responses
- **Search**: DuckDuckGo web search for RAG functionality
- **Documentation**: Auto-generated Swagger UI

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for modern design
- **State**: React hooks for efficient state management
- **Responsive**: Mobile-first responsive design
- **Performance**: Optimized bundle size and loading

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenAI API Key

### 1. Clone Repository
```bash
git clone https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant.git
cd gpt-r1-advanced-ai-assistant
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and database URL

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Environment Configuration

### Backend Environment Variables
```env
# Database Configuration (PostgreSQL ONLY)
DATABASE_URL=postgresql://user:password@localhost:5432/gpt_r1_db
POSTGRES_DB=gpt_r1_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Security Configuration
SECRET_KEY=your-super-secure-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Settings
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=GPT.R1 Advanced AI Assistant

# Optional: Analytics and Monitoring
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
npm run test:e2e

# Integration tests
docker-compose -f docker-compose.test.yml up --build
```

## 📋 API Documentation

### Core Endpoints

#### Authentication
```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password123"}'
```

#### Chat API
```bash
# Create new conversation
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'

# Send message with streaming
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "conversation_id": "uuid"}'
```

For complete API documentation, visit: http://localhost:8000/docs

## 🐳 Docker Deployment

### Development
```bash
# Start all services
docker-compose up --build

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

### Production
```bash
# Use production configuration
cp .env.production .env
docker-compose -f docker-compose.yml up -d --build

# Check service health
docker-compose ps
docker-compose logs -f
```

## 🌐 Production Deployment

### Deploy to Render (Recommended)
1. Fork this repository
2. Create services on [Render](https://render.com):
   - PostgreSQL database
   - Backend web service
   - Frontend static site
3. Configure environment variables
4. Deploy automatically from GitHub

### Deploy to Railway
1. Click: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/your-template)
2. Configure environment variables
3. Deploy with one click

### Deploy to AWS/GCP/Azure
Detailed deployment guides available in [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)

## 📁 Project Structure

```
gpt-r1-advanced-ai-assistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── migrations/         # Database migrations
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── types/         # TypeScript types
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── docs/                  # Documentation
├── docker-compose.yml     # Docker configuration
├── .github/               # GitHub Actions CI/CD
└── README.md             # This file
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Pydantic schemas for request validation
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Proper CORS setup for security
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection
- **XSS Protection**: Content Security Policy headers
- **HTTPS Enforcement**: SSL/TLS configuration for production

## 🚀 Performance Optimizations

- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Database connection optimization
- **Caching**: Redis caching for frequent requests
- **Code Splitting**: Frontend bundle optimization
- **Compression**: Gzip compression for responses
- **CDN Ready**: Optimized for CDN deployment
- **Database Indexing**: Optimized database queries

## 🛠️ Development Tools

- **Code Quality**: ESLint, Prettier, Black, isort
- **Type Safety**: TypeScript, Pydantic type checking
- **Testing**: Jest, pytest, Playwright
- **CI/CD**: GitHub Actions automated pipeline
- **Documentation**: Auto-generated API docs
- **Monitoring**: Health checks and logging

## 📊 Monitoring & Analytics

- **Health Checks**: Built-in health monitoring endpoints
- **Logging**: Structured logging with rotation
- **Metrics**: Performance and usage metrics
- **Error Tracking**: Comprehensive error handling
- **Database Monitoring**: Query performance tracking

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- FastAPI for the excellent Python framework
- Next.js for the React framework
- PostgreSQL for the robust database

## 📧 Contact

**Rajan Mishra** - AI Engineer

- GitHub: [@Rajanm001](https://github.com/Rajanm001)
- Project: [GPT.R1 Advanced AI Assistant](https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant)

---

<div align="center">

**⭐ Star this repository if you found it helpful! ⭐**

[🐛 Report Bug](https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant/issues) • [💡 Request Feature](https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant/discussions)

</div>