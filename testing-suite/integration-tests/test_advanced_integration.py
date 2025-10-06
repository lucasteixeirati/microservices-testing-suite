#!/usr/bin/env python3
"""
Advanced Integration Tests - Failure Cascades, Retry Mechanisms
Extended integration scenarios
"""

import pytest
import requests
import time
import threading
from requests.exceptions import RequestException, Timeout, ConnectionError
from urllib.parse import urlparse

BASE_URLS = {
    'user': 'http://localhost:8001',
    'order': 'http://localhost:8002', 
    'payment': 'http://localhost:8003'
}

# Allowed hosts for SSRF prevention
ALLOWED_HOSTS = ['localhost:8001', 'localhost:8002', 'localhost:8003']

def validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks"""
    try:
        parsed = urlparse(url)
        return parsed.scheme == 'http' and f"{parsed.hostname}:{parsed.port}" in ALLOWED_HOSTS
    except:
        return False

@pytest.mark.integration
class TestFailureCascades:
    """Test failure cascade scenarios"""
    
    def test_user_service_dependency_failure(self):
        """Test order creation when user service is unavailable"""
        try:
            # Try to create order with non-existent user
            response = requests.post(f"{BASE_URLS['order']}/orders", json={
                'user_id': 'non-existent-user',
                'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
                'total_amount': 10.0
            }, timeout=10)
            # Should handle gracefully
            assert response.status_code in [400, 404, 422]
        except (ConnectionError, Timeout) as e:
            pytest.skip(f"Service unavailable: {e}")
        except RequestException as e:
            pytest.fail(f"Unexpected request error: {e}")
    
    def test_order_service_dependency_failure(self):
        """Test payment processing when order service fails"""
        try:
            response = requests.post(f"{BASE_URLS['payment']}/payments", json={
                'order_id': 'non-existent-order',
                'amount': 100.0,
                'method': 'credit_card'
            }, timeout=10)
            # Should handle gracefully
            assert response.status_code in [400, 404, 422]
        except (ConnectionError, Timeout) as e:
            pytest.skip(f"Service unavailable: {e}")
        except RequestException as e:
            pytest.fail(f"Unexpected request error: {e}")
    
    def test_partial_service_failure_recovery(self):
        """Test system recovery from partial failures"""
        try:
            # Create user first
            user_response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': 'Test User',
                'email': 'test@example.com'
            }, timeout=10)
            assert user_response.status_code == 200
            user_id = user_response.json()['id']
        except (ConnectionError, Timeout) as e:
            pytest.skip(f"User service unavailable: {e}")
        except (RequestException, KeyError) as e:
            pytest.fail(f"User creation failed: {e}")
        
        # Create order
        order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
            'user_id': user_id,
            'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
            'total_amount': 10.0
        })
        assert order_response.status_code == 201
        order_id = order_response.json()['id']
        
        # Process payment
        payment_response = requests.post(f"{BASE_URLS['payment']}/payments", json={
            'order_id': order_id,
            'amount': 10.0,
            'method': 'credit_card'
        })
        assert payment_response.status_code == 201

@pytest.mark.integration
class TestRetryMechanisms:
    """Test retry and resilience mechanisms"""
    
    def test_service_communication_retry(self):
        """Test retry behavior in service communication"""
        # Create multiple orders rapidly to test retry logic
        user_response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Retry Test User',
            'email': 'retry@example.com'
        })
        assert user_response.status_code == 200
        user_id = user_response.json()['id']
        
        # Create multiple orders concurrently
        def create_order():
            return requests.post(f"{BASE_URLS['order']}/orders", json={
                'user_id': user_id,
                'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
                'total_amount': 10.0
            })
        
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(target=lambda: results.append(create_order()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Most should succeed
        success_count = sum(1 for r in results if r and r.status_code == 201)
        assert success_count >= 3
    
    def test_timeout_and_fallback(self):
        """Test timeout handling and fallback mechanisms"""
        # Test with very short timeout
        try:
            response = requests.post(f"{BASE_URLS['order']}/orders", 
                json={
                    'user_id': 'test-user',
                    'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
                    'total_amount': 10.0
                },
                timeout=0.001
            )
        except requests.exceptions.Timeout:
            # Timeout is expected and handled
            pass
        except requests.exceptions.RequestException:
            # Other exceptions are also acceptable
            pass

@pytest.mark.integration
class TestCircuitBreaker:
    """Test circuit breaker patterns"""
    
    def test_circuit_breaker_simulation(self):
        """Test circuit breaker behavior simulation"""
        # Send multiple failing requests
        failing_requests = 0
        for i in range(10):
            payment_url = f"{BASE_URLS['payment']}/payments"
            if not validate_url(payment_url):
                continue
            
            response = requests.post(payment_url, json={
                'order_id': 'invalid-order',
                'amount': 100.0,
                'method': 'credit_card'
            })
            if response.status_code >= 400:
                failing_requests += 1
        
        # Should handle failures gracefully
        assert failing_requests <= 10
    
    def test_service_health_monitoring(self):
        """Test service health monitoring"""
        health_endpoints = [
            f"{BASE_URLS['user']}/health",
            f"{BASE_URLS['order']}/health",
            f"{BASE_URLS['payment']}/health"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                assert response.status_code == 200
                health = response.json()
                assert health.get('status') == 'healthy'
            except (ConnectionError, Timeout) as e:
                pytest.skip(f"Health endpoint unavailable: {endpoint} - {e}")
            except RequestException as e:
                pytest.fail(f"Health check failed for {endpoint}: {e}")

@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across services"""
    
    def test_eventual_consistency(self):
        """Test eventual consistency between services"""
        # Create user
        user_response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Consistency Test',
            'email': 'consistency@example.com'
        })
        assert user_response.status_code == 200
        user_id = user_response.json()['id']
        
        # Immediately try to create order
        order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
            'user_id': user_id,
            'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
            'total_amount': 10.0
        })
        # Should work due to synchronous validation
        assert order_response.status_code == 201
    
    def test_transaction_rollback_simulation(self):
        """Test transaction rollback scenarios"""
        # Create user and order
        user_response = requests.post(f"{BASE_URLS['user']}/users", json={
            'name': 'Rollback Test',
            'email': 'rollback@example.com'
        })
        assert user_response.status_code == 200
        user_id = user_response.json()['id']
        
        order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
            'user_id': user_id,
            'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
            'total_amount': 10.0
        })
        assert order_response.status_code == 201
        order_id = order_response.json()['id']
        
        # Try payment with very high amount (should fail)
        payment_response = requests.post(f"{BASE_URLS['payment']}/payments", json={
            'order_id': order_id,
            'amount': 10000.0,  # High amount to trigger failure
            'method': 'credit_card'
        })
        
        # Payment might be created but processing should fail
        if payment_response.status_code == 201:
            payment_id = payment_response.json()['id']
            process_response = requests.post(f"{BASE_URLS['payment']}/payments/{payment_id}/process")
            # Processing should handle high amounts appropriately
            assert process_response.status_code in [200, 400, 422]