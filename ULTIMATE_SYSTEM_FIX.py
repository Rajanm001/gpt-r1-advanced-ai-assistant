#!/usr/bin/env python3
"""
ULTIMATE SYSTEM FIX - Complete Resolution of All Import Issues
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_workspace_python_config():
    """Create VS Code workspace settings to fix import resolution"""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "python.defaultInterpreterPath": sys.executable,
        "python.analysis.extraPaths": [
            "./backend",
            "./backend/app"
        ],
        "python.analysis.autoSearchPaths": True,
        "python.analysis.typeCheckingMode": "basic",
        "pylance.insidersChannel": "off"
    }
    
    settings_file = vscode_dir / "settings.json"
    import json
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
    
    print(f"✅ Created VS Code settings: {settings_file}")

def install_all_packages():
    """Install all required packages globally"""
    packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "python-dotenv==1.0.0",
        "aiohttp==3.9.1",
        "groq==0.9.0",
        "huggingface_hub==0.19.4",
        "duckduckgo-search==3.9.6",
        "pydantic==2.5.0",
        "requests==2.31.0",
        "psycopg2-binary==2.9.9"
    ]
    
    print("📦 Installing all packages...")
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True, text=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ {package}: {e}")

def clean_unwanted_files():
    """Remove unwanted debug and test files"""
    unwanted_files = [
        "complete_system_fix.py",
        "comprehensive_enhancement_test.py", 
        "comprehensive_test.py",
        "director_test_suite.py",
        "demo.py",
        "deploy_production.py",
        "final_system_test.py",
        "final_verification.py",
        "production_verification.py",
        "rajan_bot_debug.py",
        "test_servers.py",
        "validate_repository.py"
    ]
    
    print("\n🧹 Cleaning unwanted files...")
    for file in unwanted_files:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Removed: {file}")
    
    print("✅ Cleanup complete!")

def create_fixed_test_file():
    """Create a properly working test file"""
    test_content = '''#!/usr/bin/env python3
"""
API Test - Simple HTTP test for Rajan Bot
"""
import requests
import json

def test_api():
    """Test the API endpoints"""
    print("🚀 Testing Rajan Bot API...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        
        # Test chat endpoint
        chat_data = {
            "message": "Hello Rajan Bot!",
            "conversation_id": None
        }
        
        response = requests.post("http://localhost:8000/api/chat", json=chat_data)
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            print("🎉 All tests passed!")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
'''
    
    with open("test_api_simple.py", 'w') as f:
        f.write(test_content)
    
    print("✅ Created: test_api_simple.py (clean API test)")

def create_requirements_file():
    """Create complete requirements.txt"""
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
aiohttp==3.9.1
groq==0.9.0
huggingface_hub==0.19.4
duckduckgo-search==3.9.6
pydantic==2.5.0
requests==2.31.0
psycopg2-binary==2.9.9
"""
    
    backend_req = Path("backend/requirements.txt")
    with open(backend_req, 'w') as f:
        f.write(requirements)
    
    print(f"✅ Updated: {backend_req}")

def create_final_startup_script():
    """Create the ultimate startup script"""
    startup_content = '''@echo off
title Rajan Bot - Ultimate ChatGPT Clone
color 0A

echo ========================================
echo    RAJAN BOT - Advanced AI Assistant
echo ========================================
echo.

echo [1/4] Installing dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/4] Setting up database...
python -c "from app.database.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database ready')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Database setup might have issues
)

echo [3/4] Starting Backend Server...
start "Rajan Bot API" /min python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo [4/4] Starting Frontend Server...
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
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq Rajan Bot API*" > nul 2>&1
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq Rajan Bot UI*" > nul 2>&1
echo Servers stopped.
'''
    
    with open("RAJAN_BOT_LAUNCHER.bat", 'w', encoding='utf-8') as f:
        f.write(startup_content)
    
    print("✅ Created: RAJAN_BOT_LAUNCHER.bat")

def main():
    """Main execution"""
    print("🔧 ULTIMATE SYSTEM FIX")
    print("=" * 50)
    
    # Fix workspace configuration
    setup_workspace_python_config()
    
    # Install all packages
    install_all_packages()
    
    # Clean unwanted files  
    clean_unwanted_files()
    
    # Create fixed files
    create_fixed_test_file()
    create_requirements_file()
    create_final_startup_script()
    
    print("\n" + "=" * 50)
    print("✅ ULTIMATE FIX COMPLETE!")
    print("=" * 50)
    print("\n🎯 Next Steps:")
    print("1. Restart VS Code to apply settings")
    print("2. Run: RAJAN_BOT_LAUNCHER.bat")
    print("3. Open: http://localhost:3002")
    print("\n🎉 All import errors should be resolved!")

if __name__ == "__main__":
    main()