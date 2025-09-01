#!/usr/bin/env python3
"""
Debug authentication issues
"""

import requests
import json

BASE_URL = "https://aitrainer-3.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@aiplatform.com"
TEST_USER_PASSWORD = "SecurePassword123!"

def test_duplicate_registration():
    """Test duplicate registration"""
    registration_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)
    print(f"Duplicate Registration - Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw Response: {response.text}")

def test_invalid_login():
    """Test invalid login"""
    invalid_login = {
        "email": TEST_USER_EMAIL,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
    print(f"Invalid Login - Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw Response: {response.text}")

if __name__ == "__main__":
    test_duplicate_registration()
    test_invalid_login()