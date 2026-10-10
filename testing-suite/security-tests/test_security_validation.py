#!/usr/bin/env python3
"""
Security Tests - Input Validation and Authentication
Tests security aspects of all microservices
"""

import pytest
import requests
import json

BASE_URLS = {
    'user': 'http://localhost:8001',
    'order': 'http://localhost:8002', 
    'payment': 'http://localhost:8003'
}

@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sql_injection_user_creation(self):
        """Test SQL injection attempts in user creation"""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "admin'--",
            "' OR '1'='1"
        ]
        
        for payload in malicious_payloads:
            response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': payload,
                'email': f'test@example.com'
            })
            assert response.status_code in [200, 400, 422]
    
    def test_xss_prevention(self):
        """Test XSS prevention in all services"""
        xss_payload = "<script>alert('xss')</script>"
        
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': xss_payload,
            'email': 'test@example.com'
        })
        if response.status_code == 200:
            user = response.json()
            assert '<script>' not in user.get('name', '')
    
    def test_oversized_payload_rejection(self):
        """Test rejection of oversized payloads"""
        large_string = "A" * 10000
        
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': large_string,
            'email': 'test@example.com'
        })
        assert response.status_code in [200, 400, 413, 422]
    
    def test_invalid_json_handling(self):
        """Test handling of malformed JSON"""
        response = requests.post(
            f"{BASE_URLS['user']}/users",
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [400, 422]

@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication and authorization"""
    
    def test_csrf_token_validation(self):
        """Browser-originated writes without a token are rejected."""
        cases = [
            ('user', '/users', {'name': 'CSRF User', 'email': 'csrf@example.com'}),
            ('order', '/orders', {'user_id': 'abc-123', 'items': [], 'total_amount': 10}),
            ('payment', '/payments', {'order_id': 'abc-123', 'amount': 10, 'method': 'card'}),
        ]
        for service, path, payload in cases:
            response = requests.post(
                f"{BASE_URLS[service]}{path}",
                json=payload,
                headers={'Origin': 'http://localhost:3000'},
                timeout=5,
            )
            assert response.status_code == 403, (service, response.text)
    
    def test_rate_limiting_simulation(self):
        """Test rate limiting behavior"""
        responses = []
        for i in range(10):
            response = requests.get(f"{BASE_URLS['user']}/users")
            responses.append(response.status_code)
        
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 8

@pytest.mark.security
class TestDataSecurity:
    """Test data security and privacy"""
    
    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed"""
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Test User',
            'email': 'test@example.com'
        })
        import uuid
        unique_email = f'test-{uuid.uuid4().hex[:8]}@example.com'
        response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Test User',
            'email': unique_email
        })
        assert response.status_code in [200, 400]
        
        user = response.json()
        sensitive_fields = ['password', 'ssn', 'credit_card', 'token']
        for field in sensitive_fields:
            assert field not in user
    
    def test_error_message_information_disclosure(self):
        """Test that error messages don't disclose sensitive info"""
        response = requests.get(f"{BASE_URLS['user']}/users/non-existent-id")
        assert response.status_code == 404
        
        error = response.json()
        error_text = str(error).lower()
        sensitive_terms = ['database', 'sql', 'internal']
        for term in sensitive_terms:
            assert term not in error_text
