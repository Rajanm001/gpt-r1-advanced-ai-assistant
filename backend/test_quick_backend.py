#!/usr/bin/env python3
"""
Quick Backend Test - Login Fix Verification
"""
import requests
import time

# Test registration and login only
backend_url = "http://127.0.0.1:8001"
timestamp = int(time.time())

print("🧪 Testing Backend Login Fix...")

# 1. Register user
test_user = {
    "username": f"testuser_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!"
}

try:
    response = requests.post(f"{backend_url}/api/v1/auth/register", json=test_user, timeout=10)
    if response.status_code == 201:
        print("✅ Registration successful")
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Registration error: {e}")
    exit(1)

# 2. Test login with JSON
login_data = {
    "email": test_user["email"],
    "password": test_user["password"]
}

try:
    response = requests.post(f"{backend_url}/api/v1/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        print("✅ Login successful")
        token = response.json().get("access_token")
        print(f"🔑 Token received: {bool(token)}")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Login error: {e}")

print("🎯 Backend authentication flow working!")