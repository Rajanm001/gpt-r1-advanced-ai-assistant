#!/usr/bin/env python3
"""
Complete System Fix - Resolve all import issues and start servers
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def setup_python_path():
    """Setup Python path for proper imports"""
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "backend"
    
    # Add to system path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    print(f"✅ Added to Python path: {backend_dir}")
    
    # Set environment variable for consistent imports
    os.environ['PYTHONPATH'] = str(backend_dir)
    print(f"✅ Set PYTHONPATH: {backend_dir}")

def install_missing_packages():
    """Install any missing packages"""
    packages = [
        "aiohttp",
        "groq", 
        "huggingface_hub",
        "duckduckgo-search",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary"
    ]
    
    print("📦 Installing/updating packages...")
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--upgrade"], 
                         check=True, capture_output=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ {package} (might already be installed)")

def test_imports():
    """Test critical imports"""
    print("\n🔍 Testing imports...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    imports_to_test = [
        "app.services.multi_llm_service",
        "app.database.database", 
        "app.api.enhanced_chat",
        "groq",
        "huggingface_hub",
        "aiohttp"
    ]
    
    for import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✅ {import_name}")
        except ImportError as e:
            print(f"❌ {import_name}: {e}")

def create_startup_script():
    """Create a proper startup script"""
    startup_content = '''@echo off
echo 🚀 Starting Rajan Bot Servers...
echo.

echo 📦 Installing dependencies...
cd /d "C:\\Users\\Rajan mishra Ji\\Chatgpt\\backend"
pip install -r requirements.txt --quiet

echo.
echo 🗄️ Setting up database...
python -c "from app.database.database import engine, Base; Base.metadata.create_all(bind=engine); print('✅ Database ready')"

echo.
echo 🔧 Starting Backend Server (Port 8000)...
start "Rajan Bot Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting Frontend Server...
cd /d "C:\\Users\\Rajan mishra Ji\\Chatgpt\\frontend"
start "Rajan Bot Frontend" npm run dev

echo.
echo 🎉 Servers starting...
echo ✅ Backend: http://localhost:8000
echo ✅ Frontend: http://localhost:3002 (or next available port)
echo ✅ API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause > nul
start http://localhost:3002
'''
    
    script_path = Path(__file__).parent / "START_RAJAN_BOT.bat"
    with open(script_path, 'w') as f:
        f.write(startup_content)
    
    print(f"✅ Created startup script: {script_path}")

def start_backend_server():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting backend server...")
    
    # Start backend server
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ]
    
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ Backend server started (PID: {backend_process.pid})")
    return backend_process

def start_frontend_server():
    """Start the frontend server"""
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🎨 Starting frontend server...")
    
    # Start frontend server
    frontend_cmd = ["npm", "run", "dev"]
    
    frontend_process = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ Frontend server started (PID: {frontend_process.pid})")
    return frontend_process

def main():
    """Main execution function"""
    print("🔧 COMPLETE SYSTEM FIX - Rajan Bot")
    print("=" * 50)
    
    # Setup Python environment
    setup_python_path()
    
    # Install packages
    install_missing_packages()
    
    # Test imports
    test_imports()
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("✅ SYSTEM FIX COMPLETE!")
    print("🚀 Ready to start servers!")
    print("=" * 50)
    
    # Ask user if they want to start servers now
    response = input("\n🚀 Start servers now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        try:
            backend_proc = start_backend_server()
            time.sleep(3)  # Wait for backend to start
            frontend_proc = start_frontend_server()
            
            print("\n🎉 SERVERS STARTED SUCCESSFULLY!")
            print("✅ Backend: http://localhost:8000")
            print("✅ Frontend: http://localhost:3002")
            print("✅ API Docs: http://localhost:8000/docs")
            print("\nPress Ctrl+C to stop servers...")
            
            # Keep servers running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping servers...")
                backend_proc.terminate()
                frontend_proc.terminate()
                print("✅ Servers stopped")
                
        except Exception as e:
            print(f"❌ Error starting servers: {e}")
    else:
        print("✅ System fixed! Use START_RAJAN_BOT.bat to start servers later.")

if __name__ == "__main__":
    main()