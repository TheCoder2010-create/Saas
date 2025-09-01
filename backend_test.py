#!/usr/bin/env python3
"""
Comprehensive Backend Testing for AI Model Training Platform
Tests all core backend functionality including authentication, dataset management,
AI model training, testing, deployment, and dashboard APIs.
"""

import requests
import json
import io
import time
from datetime import datetime
import os
import sys

# Configuration
BASE_URL = "https://aitrainer-3.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@aiplatform.com"
TEST_USER_PASSWORD = "SecurePassword123!"
TEST_USER_NAME = "AI Platform Test User"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_dataset_id = None
        self.test_model_id = None
        self.test_deployment_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "dataset_management": {"passed": 0, "failed": 0, "details": []},
            "model_training": {"passed": 0, "failed": 0, "details": []},
            "model_testing": {"passed": 0, "failed": 0, "details": []},
            "model_deployment": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []}
        }

    def log_result(self, category, test_name, success, details=""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        result_entry = f"{status}: {test_name}"
        if details:
            result_entry += f" - {details}"
        
        self.results[category]["details"].append(result_entry)
        print(result_entry)

    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token exists
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.access_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.access_token}"
        
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n=== Testing User Registration ===")
        
        # Test successful registration
        registration_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = self.make_request("POST", "/auth/register", json=registration_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("authentication", "User Registration", True, 
                              f"User created with ID: {self.user_id}")
            else:
                self.log_result("authentication", "User Registration", False, 
                              "Missing access_token or user in response")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("authentication", "User Registration", False, error_msg)

        # Test duplicate registration
        response = self.make_request("POST", "/auth/register", json=registration_data)
        if response and response.status_code == 400:
            self.log_result("authentication", "Duplicate Registration Prevention", True, 
                          "Correctly rejected duplicate email")
        else:
            self.log_result("authentication", "Duplicate Registration Prevention", False, 
                          "Should have rejected duplicate email")

    def test_user_login(self):
        """Test user login endpoint"""
        print("\n=== Testing User Login ===")
        
        # Test successful login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", json=login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                # Update token (should be same as registration)
                self.access_token = data["access_token"]
                self.log_result("authentication", "User Login", True, 
                              f"Login successful for user: {data['user']['email']}")
            else:
                self.log_result("authentication", "User Login", False, 
                              "Missing access_token or user in response")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("authentication", "User Login", False, error_msg)

        # Test invalid login
        invalid_login = {
            "email": TEST_USER_EMAIL,
            "password": "wrongpassword"
        }
        
        response = self.make_request("POST", "/auth/login", json=invalid_login)
        if response and response.status_code == 401:
            self.log_result("authentication", "Invalid Login Prevention", True, 
                          "Correctly rejected invalid credentials")
        else:
            self.log_result("authentication", "Invalid Login Prevention", False, 
                          "Should have rejected invalid credentials")

    def test_jwt_authentication(self):
        """Test JWT token validation"""
        print("\n=== Testing JWT Authentication ===")
        
        # Test protected endpoint with valid token
        response = self.make_request("GET", "/datasets")
        
        if response and response.status_code == 200:
            self.log_result("authentication", "JWT Token Validation", True, 
                          "Protected endpoint accessible with valid token")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("authentication", "JWT Token Validation", False, error_msg)

        # Test protected endpoint without token
        response = requests.get(f"{self.base_url}/datasets", timeout=30)
        if response.status_code == 403 or response.status_code == 401:
            self.log_result("authentication", "JWT Token Required", True, 
                          "Protected endpoint correctly requires authentication")
        else:
            self.log_result("authentication", "JWT Token Required", False, 
                          "Protected endpoint should require authentication")

    def test_dataset_upload(self):
        """Test dataset upload functionality"""
        print("\n=== Testing Dataset Upload ===")
        
        # Test CSV upload
        csv_content = "name,age,city\nJohn Doe,30,New York\nJane Smith,25,Los Angeles\nBob Johnson,35,Chicago"
        csv_file = io.BytesIO(csv_content.encode())
        
        files = {'file': ('test_data.csv', csv_file, 'text/csv')}
        data = {'name': 'Test CSV Dataset'}
        
        response = self.make_request("POST", "/datasets/upload", files=files, data=data)
        
        if response and response.status_code == 200:
            dataset_data = response.json()
            if "id" in dataset_data and dataset_data["file_type"] == "csv":
                self.test_dataset_id = dataset_data["id"]
                self.log_result("dataset_management", "CSV Dataset Upload", True, 
                              f"Dataset uploaded with ID: {self.test_dataset_id}")
            else:
                self.log_result("dataset_management", "CSV Dataset Upload", False, 
                              "Invalid dataset response structure")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("dataset_management", "CSV Dataset Upload", False, error_msg)

        # Test JSON upload
        json_content = json.dumps([
            {"product": "laptop", "price": 999, "category": "electronics"},
            {"product": "book", "price": 15, "category": "education"},
            {"product": "shirt", "price": 25, "category": "clothing"}
        ])
        json_file = io.BytesIO(json_content.encode())
        
        files = {'file': ('test_data.json', json_file, 'application/json')}
        data = {'name': 'Test JSON Dataset'}
        
        response = self.make_request("POST", "/datasets/upload", files=files, data=data)
        
        if response and response.status_code == 200:
            dataset_data = response.json()
            if dataset_data["file_type"] == "json":
                self.log_result("dataset_management", "JSON Dataset Upload", True, 
                              f"JSON dataset uploaded successfully")
            else:
                self.log_result("dataset_management", "JSON Dataset Upload", False, 
                              "Invalid JSON dataset response")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("dataset_management", "JSON Dataset Upload", False, error_msg)

        # Test TXT upload
        txt_content = "This is a sample text for AI training.\nAnother line of training data.\nMore text content for the model."
        txt_file = io.BytesIO(txt_content.encode())
        
        files = {'file': ('test_data.txt', txt_file, 'text/plain')}
        data = {'name': 'Test TXT Dataset'}
        
        response = self.make_request("POST", "/datasets/upload", files=files, data=data)
        
        if response and response.status_code == 200:
            dataset_data = response.json()
            if dataset_data["file_type"] == "txt":
                self.log_result("dataset_management", "TXT Dataset Upload", True, 
                              f"TXT dataset uploaded successfully")
            else:
                self.log_result("dataset_management", "TXT Dataset Upload", False, 
                              "Invalid TXT dataset response")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("dataset_management", "TXT Dataset Upload", False, error_msg)

    def test_dataset_retrieval(self):
        """Test dataset listing"""
        print("\n=== Testing Dataset Retrieval ===")
        
        response = self.make_request("GET", "/datasets")
        
        if response and response.status_code == 200:
            datasets = response.json()
            if isinstance(datasets, list) and len(datasets) > 0:
                self.log_result("dataset_management", "Dataset Listing", True, 
                              f"Retrieved {len(datasets)} datasets")
            else:
                self.log_result("dataset_management", "Dataset Listing", False, 
                              "No datasets found or invalid response format")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("dataset_management", "Dataset Listing", False, error_msg)

    def test_model_training(self):
        """Test AI model training with Gemini"""
        print("\n=== Testing Model Training ===")
        
        if not self.test_dataset_id:
            self.log_result("model_training", "Model Training", False, 
                          "No dataset available for training")
            return

        training_data = {
            'dataset_id': self.test_dataset_id,
            'model_name': 'Test Customer Service Model',
            'custom_prompt': 'You are a helpful customer service assistant. Respond professionally and helpfully to customer inquiries based on the training data provided.'
        }
        
        response = self.make_request("POST", "/models/train", data=training_data)
        
        if response and response.status_code == 200:
            model_data = response.json()
            if "id" in model_data and model_data["status"] == "completed":
                self.test_model_id = model_data["id"]
                self.log_result("model_training", "Model Training", True, 
                              f"Model trained successfully with ID: {self.test_model_id}")
            else:
                self.log_result("model_training", "Model Training", False, 
                              f"Training failed or incomplete: {model_data.get('status', 'unknown')}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_training", "Model Training", False, error_msg)

    def test_model_listing(self):
        """Test model listing"""
        print("\n=== Testing Model Listing ===")
        
        response = self.make_request("GET", "/models")
        
        if response and response.status_code == 200:
            models = response.json()
            if isinstance(models, list):
                self.log_result("model_training", "Model Listing", True, 
                              f"Retrieved {len(models)} trained models")
            else:
                self.log_result("model_training", "Model Listing", False, 
                              "Invalid response format for models")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_training", "Model Listing", False, error_msg)

    def test_model_testing(self):
        """Test model testing with Gemini API"""
        print("\n=== Testing Model Testing ===")
        
        if not self.test_model_id:
            self.log_result("model_testing", "Model Testing", False, 
                          "No trained model available for testing")
            return

        test_input = {
            "input_text": "Hello, I need help with my recent order. Can you assist me?"
        }
        
        response = self.make_request("POST", f"/models/{self.test_model_id}/test", json=test_input)
        
        if response and response.status_code == 200:
            test_result = response.json()
            if "output" in test_result and "confidence" in test_result and "processing_time" in test_result:
                self.log_result("model_testing", "Model Testing", True, 
                              f"Model responded in {test_result['processing_time']:.2f}s with confidence {test_result['confidence']}")
            else:
                self.log_result("model_testing", "Model Testing", False, 
                              "Invalid test response structure")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_testing", "Model Testing", False, error_msg)

        # Test with different input
        test_input2 = {
            "input_text": "What are your business hours?"
        }
        
        response = self.make_request("POST", f"/models/{self.test_model_id}/test", json=test_input2)
        
        if response and response.status_code == 200:
            self.log_result("model_testing", "Multiple Test Inputs", True, 
                          "Model handles different test inputs correctly")
        else:
            self.log_result("model_testing", "Multiple Test Inputs", False, 
                          "Model failed with different input")

    def test_model_deployment(self):
        """Test model deployment functionality"""
        print("\n=== Testing Model Deployment ===")
        
        if not self.test_model_id:
            self.log_result("model_deployment", "Model Deployment", False, 
                          "No trained model available for deployment")
            return

        response = self.make_request("POST", f"/models/{self.test_model_id}/deploy")
        
        if response and response.status_code == 200:
            deployment_data = response.json()
            if "id" in deployment_data and "api_endpoint" in deployment_data:
                self.test_deployment_id = deployment_data["id"]
                self.log_result("model_deployment", "Model Deployment", True, 
                              f"Model deployed with endpoint: {deployment_data['api_endpoint']}")
            else:
                self.log_result("model_deployment", "Model Deployment", False, 
                              "Invalid deployment response structure")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_deployment", "Model Deployment", False, error_msg)

    def test_deployed_model_listing(self):
        """Test deployed model listing"""
        print("\n=== Testing Deployed Model Listing ===")
        
        response = self.make_request("GET", "/models/deployed")
        
        if response and response.status_code == 200:
            deployed_models = response.json()
            if isinstance(deployed_models, list):
                self.log_result("model_deployment", "Deployed Model Listing", True, 
                              f"Retrieved {len(deployed_models)} deployed models")
            else:
                self.log_result("model_deployment", "Deployed Model Listing", False, 
                              "Invalid response format for deployed models")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_deployment", "Deployed Model Listing", False, error_msg)

    def test_api_prediction(self):
        """Test API prediction endpoint"""
        print("\n=== Testing API Prediction ===")
        
        if not self.test_model_id:
            self.log_result("model_deployment", "API Prediction", False, 
                          "No model available for prediction")
            return

        prediction_input = {
            "input_text": "I want to return a product I bought last week."
        }
        
        response = self.make_request("POST", f"/models/{self.test_model_id}/predict", json=prediction_input)
        
        if response and response.status_code == 200:
            prediction_result = response.json()
            if "output" in prediction_result:
                self.log_result("model_deployment", "API Prediction", True, 
                              "API prediction endpoint working correctly")
            else:
                self.log_result("model_deployment", "API Prediction", False, 
                              "Invalid prediction response structure")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("model_deployment", "API Prediction", False, error_msg)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n=== Testing Dashboard Statistics ===")
        
        response = self.make_request("GET", "/dashboard/stats")
        
        if response and response.status_code == 200:
            stats = response.json()
            expected_keys = ["datasets", "models", "deployed", "api_calls"]
            if all(key in stats for key in expected_keys):
                self.log_result("dashboard", "Dashboard Statistics", True, 
                              f"Stats: {stats['datasets']} datasets, {stats['models']} models, {stats['deployed']} deployed, {stats['api_calls']} API calls")
            else:
                self.log_result("dashboard", "Dashboard Statistics", False, 
                              f"Missing expected keys in stats response. Got: {list(stats.keys())}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("dashboard", "Dashboard Statistics", False, error_msg)

    def run_all_tests(self):
        """Run comprehensive backend tests"""
        print(f"🚀 Starting Comprehensive Backend Testing for AI Model Training Platform")
        print(f"📡 Testing against: {self.base_url}")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authentication Tests
        self.test_user_registration()
        self.test_user_login()
        self.test_jwt_authentication()
        
        # Dataset Management Tests
        self.test_dataset_upload()
        self.test_dataset_retrieval()
        
        # Model Training Tests
        self.test_model_training()
        self.test_model_listing()
        
        # Model Testing Tests
        self.test_model_testing()
        
        # Model Deployment Tests
        self.test_model_deployment()
        self.test_deployed_model_listing()
        self.test_api_prediction()
        
        # Dashboard Tests
        self.test_dashboard_stats()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("🏁 BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            print(f"\n{status_icon} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            for detail in results["details"]:
                print(f"  {detail}")
        
        print(f"\n{'='*80}")
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"⚠️ {total_failed} TESTS FAILED"
        print(f"🎯 OVERALL RESULT: {overall_status}")
        print(f"📊 TOTAL: {total_passed} passed, {total_failed} failed")
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()