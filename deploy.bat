@echo off
REM Production deployment script for Windows

echo 🚀 Starting ChatGPT Clone production deployment...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please create one from .env.production template.
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo ✅ Environment checks passed

REM Build and start services
echo 🔨 Building Docker images...
docker-compose build --no-cache

echo 🚀 Starting services...
docker-compose up -d

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Run database migrations
echo 📊 Running database migrations...
docker-compose exec -T backend alembic upgrade head

REM Check service health
echo 🏥 Checking service health...
timeout /t 5 /nobreak >nul

REM Check backend health
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend health check failed
    docker-compose logs backend
    exit /b 1
) else (
    echo ✅ Backend is healthy
)

REM Check frontend health
curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend health check failed
    docker-compose logs frontend
) else (
    echo ✅ Frontend is healthy
)

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📍 Services are running at:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/api/docs
echo    Database: localhost:5432
echo.
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo 🔄 To restart: docker-compose restart