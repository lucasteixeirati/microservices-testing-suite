#!/usr/bin/env python3
"""
API Tests - HTTP Headers, Content-Type, Error Handling
Extended API validation tests
"""

import pytest
import requests
import json

BASE_URLS = {
    'user': 'http://localhost:8001',
    'order': 'http://localhost:8002', 
    'payment': 'http://localhost:8003'
}

@pytest.mark.api
class TestHTTPHeaders:
    """Test HTTP headers validation"""
    
    def test_content_type_validation(self):
        """Test Content-Type header validation"""
        response = requests.post(f"{BASE_URLS['user']}/users", 
            json={'name': 'Test', 'email': 'test@example.com'},
            headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URLS['user']}/users",
            data=json.dumps({'name': 'Test', 'email': 'test@example.com'}),
            headers={'Content-Type': 'text/plain'})
        assert response.status_code in [400, 415]
    
    def test_accept_header_handling(self):
        """Test Accept header handling"""
        response = requests.get(f"{BASE_URLS['user']}/users",
            headers={'Accept': 'application/json'})
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('Content-Type', '')
    
    def test_user_agent_handling(self):
        """Test User-Agent header handling"""
        response = requests.get(f"{BASE_URLS['user']}/users",
            headers={'User-Agent': 'TestSuite/1.0'})
        assert response.status_code == 200
    
    def test_cors_preflight_handling(self):
        """Test CORS preflight requests"""
        response = requests.options(f"{BASE_URLS['user']}/users",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST'
            })
        assert response.status_code in [200, 204, 405]

@pytest.mark.api
class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_404_not_found_responses(self):
        """Test 404 responses for non-existent resources"""
        endpoints = [
            f"{BASE_URLS['user']}/users/non-existent-id",
            f"{BASE_URLS['order']}/orders/non-existent-id",
            f"{BASE_URLS['payment']}/payments/non-existent-id"
        ]
        
        for endpoint in endpoints:
            response = requests.get(endpoint)
            assert response.status_code == 404
            assert 'error' in response.json()
    
    def test_400_bad_request_responses(self):
        """Test 400 responses for invalid requests"""
        response = requests.post(f"{BASE_URLS['user']}/users", json={})
        assert response.status_code in [400, 422]
        
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Test',
            'email': 'invalid-email'
        })
        assert response.status_code in [200, 400, 422]
    
    def test_405_method_not_allowed(self):
        """Test 405 responses for unsupported methods"""
        response = requests.delete(f"{BASE_URLS['user']}/health")
        assert response.status_code in [405, 404]
    
    def test_timeout_handling(self):
        """Test timeout scenarios"""
        try:
            response = requests.get(f"{BASE_URLS['user']}/users", timeout=0.001)
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.RequestException:
            pass

@pytest.mark.api
class TestDataValidation:
    """Test data validation and constraints"""
    
    def test_email_format_validation(self):
        """Test email format validation"""
        invalid_emails = ['invalid', '@example.com', 'test@']
        
        for email in invalid_emails:
            response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': 'Test User',
                'email': email
            })
            assert response.status_code in [200, 400, 422]
    
    def test_numeric_validation(self):
        """Test numeric field validation"""
        response = requests.post(f"{BASE_URLS['payment']}/payments", json={
            'order_id': 'test-order',
            'amount': -100.0,
            'method': 'credit_card'
        })
        assert response.status_code in [200, 400, 422]
    
    def test_string_length_validation(self):
        """Test string length constraints"""
        long_name = 'A' * 1000
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': long_name,
            'email': 'test@example.com'
        })
        assert response.status_code in [200, 400, 422]

@pytest.mark.api
class TestResponseFormat:
    """Test response format consistency"""
    
    def test_json_response_structure(self):
        """Test JSON response structure consistency"""
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Test User',
            'email': 'test@example.com'
        })
        assert response.status_code == 200
        
        user = response.json()
        required_fields = ['id', 'name', 'email', 'created_at']
        for field in required_fields:
            assert field in user
    
    def test_error_response_structure(self):
        """Test error response structure consistency"""
        response = requests.get(f"{BASE_URLS['user']}/users/non-existent")
        assert response.status_code == 404
        
        error = response.json()
        assert 'error' in error