@echo off
echo Starting Rajan Bot Servers...
echo.

echo Installing dependencies...
cd /d "C:\Users\Rajan mishra Ji\Chatgpt\backend"
pip install -r requirements.txt --quiet

echo.
echo Setting up database...
python -c "from app.database.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database ready')"

echo.
echo Starting Backend Server (Port 8000)...
start "Rajan Bot Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend Server...
cd /d "C:\Users\Rajan mishra Ji\Chatgpt\frontend"
start "Rajan Bot Frontend" npm run dev

echo.
echo Servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3002 (or next available port)
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause > nul
start http://localhost:3002
