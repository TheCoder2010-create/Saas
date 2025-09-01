#!/usr/bin/env python3
"""
Debug test to understand the specific errors in model testing
"""

import requests
import json

BASE_URL = "https://aitrainer-3.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@aiplatform.com"
TEST_USER_PASSWORD = "SecurePassword123!"

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_model_testing_detailed():
    """Test model testing with detailed error reporting"""
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get models first
    models_response = requests.get(f"{BASE_URL}/models", headers=headers)
    if models_response.status_code != 200:
        print("Failed to get models")
        return
    
    models = models_response.json()
    if not models:
        print("No models found")
        return
    
    model_id = models[0]["id"]
    print(f"Testing model: {model_id}")
    
    # Test the model
    test_input = {
        "input_text": "Hello, I need help with my recent order."
    }
    
    response = requests.post(f"{BASE_URL}/models/{model_id}/test", 
                           json=test_input, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"Response Body: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Raw Response: {response.text}")

if __name__ == "__main__":
    test_model_testing_detailed()