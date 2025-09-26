# Rajan Bot Startup Script
Write-Host "Starting Rajan Bot Servers..." -ForegroundColor Green

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Rajan mishra Ji\Chatgpt\backend'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Rajan mishra Ji\Chatgpt\frontend'; npm run dev"

Write-Host "All servers started!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000 (or next available port)" -ForegroundColor Cyan
