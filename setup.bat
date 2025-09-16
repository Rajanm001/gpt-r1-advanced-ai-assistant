@echo off
REM ChatGPT Clone Setup Script for Windows
REM This script sets up the entire development environment

echo 🚀 Setting up ChatGPT Clone Development Environment...

REM Check prerequisites
echo [INFO] Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo [SUCCESS] Prerequisites check completed!

REM Setup environment files
echo [INFO] Setting up environment files...

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo [SUCCESS] Created backend\.env from example
    echo [WARNING] Please update backend\.env with your OpenAI API key and database credentials
) else (
    echo [WARNING] backend\.env already exists, skipping...
)

if not exist "frontend\.env.local" (
    copy "frontend\.env.example" "frontend\.env.local"
    echo [SUCCESS] Created frontend\.env.local from example
) else (
    echo [WARNING] frontend\.env.local already exists, skipping...
)

REM Setup backend
echo [INFO] Setting up backend...
cd backend

if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)

echo [INFO] Installing Python dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Python dependencies installed
call deactivate

cd ..

REM Setup frontend
echo [INFO] Setting up frontend...
cd frontend

echo [INFO] Installing Node.js dependencies...
npm install
echo [SUCCESS] Node.js dependencies installed

cd ..

REM Database setup instructions
echo [INFO] Database setup instructions:
echo 1. Make sure PostgreSQL is running
echo 2. Create a database named 'chatgpt_clone'
echo 3. Update the DATABASE_URL in backend\.env
echo 4. Run database migrations:
echo    cd backend
echo    venv\Scripts\activate
echo    alembic upgrade head

echo [SUCCESS] Setup completed! 🎉

echo [INFO] To start the development servers:
echo.
echo Backend (in backend\ directory):
echo   venv\Scripts\activate
echo   uvicorn main:app --reload --port 8000
echo.
echo Frontend (in frontend\ directory):
echo   npm run dev
echo.
echo Access the application at:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo.
echo [WARNING] Don't forget to update your OpenAI API key in backend\.env!
echo [WARNING] Make sure PostgreSQL is running and the database is created!

pause