@echo off
title Rajan Bot - Ultimate ChatGPT Clone
echo ========================================
echo    RAJAN BOT - Advanced AI Assistant
echo ========================================
echo.

echo Installing dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet --disable-pip-version-check

echo Setting up database...
python -c "from app.database.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database ready')" 2>nul

echo Starting Backend Server...
start "Rajan Bot API" /min python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo Starting Frontend Server...
cd /d "%~dp0frontend"
start "Rajan Bot UI" npm run dev

echo.
echo ========================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3002
echo API Docs:    http://localhost:8000/docs
echo.
echo Waiting for servers to initialize...
timeout /t 8 /nobreak > nul

echo Opening Rajan Bot...
start http://localhost:3002

echo.
echo Press any key to stop all servers...
pause > nul

echo Stopping servers...
taskkill /F /IM "python.exe" > nul 2>&1
taskkill /F /IM "node.exe" > nul 2>&1
echo Servers stopped.