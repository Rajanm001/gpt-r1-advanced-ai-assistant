#!/usr/bin/env python3
"""
Debug Protected Endpoint
"""
import requests
import time

backend_url = "http://127.0.0.1:8001"
timestamp = int(time.time())

# Register and login to get a valid token
test_user = {
    "username": f"testuser_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!"
}

# Register
response = requests.post(f"{backend_url}/api/v1/auth/register", json=test_user)
print(f"Registration: {response.status_code}")

# Login
login_data = {"email": test_user["email"], "password": test_user["password"]}
response = requests.post(f"{backend_url}/api/v1/auth/login", json=login_data)
print(f"Login: {response.status_code}")

if response.status_code == 200:
    token = response.json().get("access_token")
    print(f"Token received: {bool(token)}")
    
    # Test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{backend_url}/api/v1/auth/me", headers=headers)
    print(f"Protected endpoint: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print("Failed to get token")