#!/bin/bash
# 🚀 ULTIMATE PRODUCTION LAUNCHER 🚀
# ✅ Start the complete production system

echo "=" * 60
echo "🚀 STARTING ULTIMATE PRODUCTION CHATGPT CLONE"
echo "=" * 60

# Start Backend Server
echo "🔧 Starting Production Backend Server..."
cd backend
start /B python PRODUCTION_SERVER.py

# Wait a moment
sleep 3

# Start Frontend Server  
echo "🎨 Starting Production Frontend Server..."
cd ../frontend
start /B npm run dev

echo "=" * 60
echo "🎯 PRODUCTION SYSTEM READY!"
echo "🌐 Frontend: http://localhost:3001"
echo "📡 Backend: http://localhost:8000" 
echo "=" * 60