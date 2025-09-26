#!/usr/bin/env python3
"""
🧪 SERVER TESTING SCRIPT
Tests both frontend and backend servers
"""
import requests
import time
import subprocess
import sys
from urllib.parse import urljoin

def test_backend():
    """Test backend server"""
    print("🧪 Testing Backend Server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Health: WORKING")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend Health: FAILED ({response.status_code})")
            return False
            
        # Test API docs
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Docs: ACCESSIBLE")
        else:
            print(f"❌ API Docs: FAILED ({response.status_code})")
            
        # Test root endpoint
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Root: WORKING")
        else:
            print(f"❌ Backend Root: FAILED ({response.status_code})")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend: CONNECTION REFUSED")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ Backend: ERROR - {e}")
        return False

def test_frontend():
    """Test frontend server"""
    print("\n🧪 Testing Frontend Server...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: WORKING")
            print(f"   Content Length: {len(response.text)} bytes")
            
            # Check if it contains React/Next.js content
            if "React" in response.text or "_next" in response.text or "Next.js" in response.text:
                print("✅ Frontend: React/Next.js App Detected")
            else:
                print("⚠️  Frontend: No React content detected")
                
            return True
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend: CONNECTION REFUSED")
        return False
    except requests.exceptions.Timeout:
        print("❌ Frontend: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ Frontend: ERROR - {e}")
        return False

def check_processes():
    """Check if processes are running"""
    print("\n🔍 Checking Running Processes...")
    
    try:
        # Check for uvicorn (backend)
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            print("✅ Python processes found (likely backend)")
        else:
            print("❌ No Python processes found")
            
        # Check for node (frontend)
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], 
                              capture_output=True, text=True)
        if 'node.exe' in result.stdout:
            print("✅ Node.js processes found (likely frontend)")
        else:
            print("❌ No Node.js processes found")
            
    except Exception as e:
        print(f"⚠️ Process check failed: {e}")

def check_ports():
    """Check if ports are in use"""
    print("\n🔍 Checking Ports...")
    
    try:
        # Check port 8000
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':8000' in result.stdout:
            print("✅ Port 8000: IN USE")
        else:
            print("❌ Port 8000: NOT IN USE")
            
        # Check port 3000
        if ':3000' in result.stdout:
            print("✅ Port 3000: IN USE")
        else:
            print("❌ Port 3000: NOT IN USE")
            
    except Exception as e:
        print(f"⚠️ Port check failed: {e}")

def main():
    """Main testing function"""
    print("🚀 SERVER CONNECTIVITY TEST")
    print("="*50)
    
    # Check processes and ports first
    check_processes()
    check_ports()
    
    # Test servers
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "="*50)
    print("📋 FINAL RESULTS:")
    print("="*50)
    
    if backend_ok:
        print("✅ Backend: http://localhost:8000 - WORKING")
        print("✅ API Docs: http://localhost:8000/docs - WORKING")
    else:
        print("❌ Backend: FAILED")
        
    if frontend_ok:
        print("✅ Frontend: http://localhost:3000 - WORKING")
    else:
        print("❌ Frontend: FAILED")
        
    if backend_ok and frontend_ok:
        print("\n🎉 ALL SERVERS ARE WORKING!")
        print("🔗 Open http://localhost:3000 in your browser")
    else:
        print("\n⚠️ SOME SERVERS NEED ATTENTION!")
        
    return backend_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)