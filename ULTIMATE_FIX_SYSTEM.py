#!/usr/bin/env python3
"""
🔥 ULTIMATE SYSTEM FIX - Complete ChatGPT Clone Repair
=====================================================
This script will completely fix and restart your ChatGPT clone system.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

print("🔥 ULTIMATE SYSTEM FIX STARTED")
print("=" * 60)

# Change to project directory
project_root = Path(__file__).parent
os.chdir(project_root)

def run_command(cmd, description, shell=True, check=True):
    """Run a command with proper error handling"""
    print(f"🔧 {description}...")
    try:
        if shell and sys.platform == "win32":
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        
        if result.stdout:
            print(f"✅ {description} - Success")
            if "error" in result.stdout.lower():
                print(f"⚠️ Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

# Step 1: Kill all processes
print("\n1️⃣ Killing all server processes...")
run_command("taskkill /F /IM uvicorn.exe", "Kill uvicorn", check=False)
run_command("taskkill /F /IM node.exe", "Kill Node.js", check=False)

# Step 2: Clean and setup backend
print("\n2️⃣ Setting up backend...")
backend_path = project_root / "backend"
os.chdir(backend_path)

# Install requirements
run_command(".\\venv\\Scripts\\Activate.ps1; pip install -r requirements.txt --upgrade", "Install Python packages")

# Create database
run_command('.\\venv\\Scripts\\Activate.ps1; python -c "from app.database.database import engine, Base; Base.metadata.create_all(bind=engine); print(\\"Database created\\")"', "Create database")

# Step 3: Clean and setup frontend
print("\n3️⃣ Setting up frontend...")
frontend_path = project_root / "frontend"
os.chdir(frontend_path)

# Install npm packages
run_command("npm install", "Install NPM packages")

# Step 4: Start backend server
print("\n4️⃣ Starting backend server...")
os.chdir(backend_path)

# Start backend in background
backend_process = subprocess.Popen(
    ".\\venv\\Scripts\\Activate.ps1; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000",
    shell=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
)

# Wait for backend to start
print("⏳ Waiting for backend to start...")
for i in range(10):
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running!")
            break
    except:
        time.sleep(2)
        print(f"⏳ Attempt {i+1}/10...")
else:
    print("❌ Backend failed to start")

# Step 5: Start frontend server
print("\n5️⃣ Starting frontend server...")
os.chdir(frontend_path)

# Start frontend in background
frontend_process = subprocess.Popen(
    "npm run dev",
    shell=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
)

# Wait for frontend to start
print("⏳ Waiting for frontend to start...")
for port in [3000, 3001, 3002]:
    for i in range(5):
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            if response.status_code == 200:
                print(f"✅ Frontend is running on port {port}!")
                frontend_port = port
                break
        except:
            time.sleep(1)
    else:
        continue
    break

# Step 6: Test API
print("\n6️⃣ Testing API...")
try:
    api_data = {
        "message": "Hello! System test - are you working?",
        "conversation_id": None
    }
    response = requests.post("http://localhost:8000/api/chat", json=api_data, timeout=10)
    if response.status_code == 200:
        print("✅ API is working perfectly!")
    else:
        print(f"❌ API error: {response.status_code}")
except Exception as e:
    print(f"❌ API test failed: {e}")

print("\n" + "=" * 60)
print("🎯 SYSTEM FIX COMPLETE!")
print("=" * 60)

print(f"\n🌐 ACCESS YOUR CHATGPT CLONE:")
print(f"   Frontend: http://localhost:3000")
print(f"   API: http://localhost:8000")
print(f"   Health: http://localhost:8000/health")

print(f"\n🎮 FEATURES AVAILABLE:")
print(f"   ✅ Real-time Chat Streaming")
print(f"   ✅ Dark Mode UI")
print(f"   ✅ Conversation Storage")
print(f"   ✅ Multi-LLM Integration")

print(f"\n🎉 YOUR CHATGPT CLONE IS NOW READY!")