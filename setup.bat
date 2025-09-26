@echo off
echo 🚀 Setting up ChatGPT Clone project...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo 📦 Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    copy .env.example .env
    echo ⚠️  Please update backend\.env with your OpenAI API key and database credentials
)

echo 📦 Setting up frontend...
cd ..\frontend

REM Install dependencies
npm install

echo ✅ Setup complete!
echo.
echo 🔧 Next steps:
echo 1. Update backend\.env with your OpenAI API key
echo 2. Make sure PostgreSQL is running
echo 3. Run database migrations: cd backend ^&^& alembic upgrade head
echo 4. Start backend: cd backend ^&^& uvicorn main:app --reload
echo 5. Start frontend: cd frontend ^&^& npm run dev
echo.
echo 🌐 Access your application at:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs

pause