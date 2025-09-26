@echo off
echo 🚀 DIRECTOR-LEVEL CHATGPT CLONE - STARTUP SCRIPT
echo ================================================
echo.

REM Change to project directory
cd /d "C:\Users\Rajan mishra Ji\Chatgpt"

echo 📋 Starting Services...
echo.

REM Start Backend Server
echo 🐍 Starting Backend Server...
start "Backend Server" cmd /k "cd /d \"C:\Users\Rajan mishra Ji\Chatgpt\backend\" && .\venv\Scripts\Activate.ps1 && uvicorn main:app --reload --port 8000 && pause"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start Frontend Server
echo 🌐 Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d \"C:\Users\Rajan mishra Ji\Chatgpt\frontend\" && npm run dev && pause"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ✅ SERVERS STARTING...
echo.
echo 🔗 Access Points:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📝 Note: Two terminal windows will open for the servers
echo    Keep them running while using the application
echo.

REM Test connectivity
echo 🧪 Testing connectivity...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 10; Write-Host '✅ Backend: ONLINE' -ForegroundColor Green } catch { Write-Host '⚠️ Backend: Starting...' -ForegroundColor Yellow }"

timeout /t 3 /nobreak >nul

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 10; Write-Host '✅ Frontend: ONLINE' -ForegroundColor Green } catch { Write-Host '⚠️ Frontend: Starting...' -ForegroundColor Yellow }"

echo.
echo 🎉 SETUP COMPLETE!
echo    Open http://localhost:3000 in your browser
echo.
pause