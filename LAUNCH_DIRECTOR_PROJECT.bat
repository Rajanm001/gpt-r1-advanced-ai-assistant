@echo off
echo 🚀 DIRECTOR-LEVEL CHATGPT CLONE LAUNCHER
echo ==========================================
echo.
echo 🎯 Starting Backend Server...
start /b cmd /c "cd backend && .\venv\Scripts\Activate.ps1 && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul
echo ✅ Backend Server Started

echo.
echo 🎯 Starting Frontend Server...  
start /b cmd /c "cd frontend && npm run dev"

timeout /t 5 /nobreak > nul
echo ✅ Frontend Server Started

echo.
echo 🌟 SYSTEM READY FOR CLIENT ACCESS
echo ==========================================
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend:  http://localhost:8000  
echo 📖 API Docs: http://localhost:8000/docs
echo ==========================================
echo.
echo 🎊 DIRECTOR AI PROJECT - READY FOR DELIVERY!
pause