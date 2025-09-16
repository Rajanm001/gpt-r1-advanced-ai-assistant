#!/bin/bash

# ChatGPT Clone Setup Script
# This script sets up the entire development environment

set -e

echo "🚀 Setting up ChatGPT Clone Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
    PYTHON_CMD="python"
    VENV_ACTIVATE="venv\\Scripts\\activate"
else
    IS_WINDOWS=false
    PYTHON_CMD="python3"
    VENV_ACTIVATE="venv/bin/activate"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists $PYTHON_CMD; then
    print_error "Python is not installed. Please install Python 3.11 or higher."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

if ! command_exists psql; then
    print_warning "PostgreSQL client not found. Please ensure PostgreSQL is installed."
fi

print_success "Prerequisites check completed!"

# Setup environment files
print_status "Setting up environment files..."

# Backend environment
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    print_success "Created backend/.env from example"
    print_warning "Please update backend/.env with your OpenAI API key and database credentials"
else
    print_warning "backend/.env already exists, skipping..."
fi

# Frontend environment
if [ ! -f "frontend/.env.local" ]; then
    cp frontend/.env.example frontend/.env.local
    print_success "Created frontend/.env.local from example"
else
    print_warning "frontend/.env.local already exists, skipping..."
fi

# Setup backend
print_status "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
if [ "$IS_WINDOWS" = true ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

cd ..

# Database setup instructions
print_status "Database setup instructions:"
echo "1. Make sure PostgreSQL is running"
echo "2. Create a database named 'chatgpt_clone'"
echo "3. Update the DATABASE_URL in backend/.env"
echo "4. Run database migrations:"
echo "   cd backend"
if [ "$IS_WINDOWS" = true ]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   alembic upgrade head"

print_success "Setup completed! 🎉"

print_status "To start the development servers:"
echo ""
echo "Backend (in backend/ directory):"
if [ "$IS_WINDOWS" = true ]; then
    echo "  venv\\Scripts\\activate"
else
    echo "  source venv/bin/activate"
fi
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "Frontend (in frontend/ directory):"
echo "  npm run dev"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
print_warning "Don't forget to update your OpenAI API key in backend/.env!"
print_warning "Make sure PostgreSQL is running and the database is created!"

# Optional: Docker setup
read -p "Do you want to setup with Docker instead? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command_exists docker && command_exists docker-compose; then
        print_status "Setting up with Docker..."
        print_warning "Make sure to update .env with your OpenAI API key before starting"
        echo "Run: docker-compose up -d"
        print_success "Docker setup ready!"
    else
        print_error "Docker or docker-compose not found. Please install Docker first."
    fi
fi