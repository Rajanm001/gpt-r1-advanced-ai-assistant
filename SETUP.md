# 🚀 Quick Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 18+
- npm/yarn

## Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Access
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Backend: http://localhost:8000

## Environment Variables
Create `.env` files in both directories:

**Backend (.env):**
```
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/gpt_r1_db
SECRET_KEY=your_secret_key
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Ready to run! 🎉