#!/bin/bash

# Setup script for ChatGPT Clone project

echo "🚀 Setting up ChatGPT Clone project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL service."
    echo "   You can also use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15-alpine"
fi

echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your OpenAI API key and database credentials"
fi

echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Update backend/.env with your OpenAI API key"
echo "2. Make sure PostgreSQL is running"
echo "3. Run database migrations: cd backend && alembic upgrade head"
echo "4. Start backend: cd backend && uvicorn main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Access your application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"