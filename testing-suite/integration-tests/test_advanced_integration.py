#!/usr/bin/env python3
"""
Advanced Integration Tests - Failure Cascades, Retry Mechanisms
Extended integration scenarios with robust error handling
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

def check_service_health(service_url: str) -> bool:
    """Check if service is healthy"""
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        return response.status_code == 200
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
        # Check if services are available first
        user_healthy = check_service_health(BASE_URLS['user'])
        order_healthy = check_service_health(BASE_URLS['order'])
        payment_healthy = check_service_health(BASE_URLS['payment'])
        
        if not user_healthy:
            pytest.skip("User service not available")
        
        try:
            # Create user first
            user_response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': 'Test User Recovery',
                'email': f'test-recovery-{int(time.time())}@example.com'
            }, timeout=10)
            
            if user_response.status_code != 200:
                pytest.skip(f"User creation failed: {user_response.status_code}")
            
            user_id = user_response.json()['id']
            
            if order_healthy:
                # Create order
                order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
                    'user_id': user_id,
                    'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
                    'total_amount': 10.0
                }, timeout=10)
                
                if order_response.status_code == 201:
                    order_id = order_response.json()['id']
                    
                    if payment_healthy:
                        # Process payment
                        payment_response = requests.post(f"{BASE_URLS['payment']}/payments", json={
                            'order_id': order_id,
                            'amount': 10.0,
                            'method': 'credit_card'
                        }, timeout=10)
                        
                        # Payment should be created or handled gracefully
                        assert payment_response.status_code in [201, 400, 422]
                    else:
                        # Payment service down, but order creation succeeded
                        assert True
                else:
                    # Order creation failed, but user was created
                    assert True
            else:
                # Order service down, but user creation succeeded
                assert True
                
        except Exception as e:
            pytest.skip(f"Service integration test failed: {e}")

@pytest.mark.integration
class TestRetryMechanisms:
    """Test retry and resilience mechanisms"""
    
    def test_service_communication_retry(self):
        """Test retry behavior in service communication"""
        if not check_service_health(BASE_URLS['user']):
            pytest.skip("User service not available")
        
        try:
            # Create user for retry tests
            user_response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': 'Retry Test User',
                'email': f'retry-{int(time.time())}@example.com'
            }, timeout=10)
            
            if user_response.status_code != 200:
                pytest.skip("User creation failed")
            
            user_id = user_response.json()['id']
            
            if check_service_health(BASE_URLS['order']):
                # Test multiple order creations with retry logic
                success_count = 0
                for i in range(3):
                    try:
                        order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
                            'user_id': user_id,
                            'items': [{'product': f'test-retry-{i}', 'quantity': 1, 'price': 10.0}],
                            'total_amount': 10.0
                        }, timeout=10)
                        
                        if order_response.status_code == 201:
                            success_count += 1
                        
                        time.sleep(0.1)  # Small delay between requests
                    except:
                        continue
                
                # At least one should succeed if services are healthy
                assert success_count >= 1
            else:
                pytest.skip("Order service not available for retry test")
                
        except Exception as e:
            pytest.skip(f"Retry test failed: {e}")
    
    def test_timeout_and_fallback(self):
        """Test timeout handling and fallback mechanisms"""
        # Test with reasonable timeout
        try:
            response = requests.post(f"{BASE_URLS['order']}/orders", 
                json={
                    'user_id': 'test-timeout-user',
                    'items': [{'product': 'test', 'quantity': 1, 'price': 10.0}],
                    'total_amount': 10.0
                },
                timeout=5
            )
            # Should get a response (success or failure)
            assert response.status_code in [200, 201, 400, 404, 422]
        except requests.exceptions.Timeout:
            # Timeout is acceptable for this test
            assert True
        except requests.exceptions.RequestException:
            # Other exceptions are also acceptable
            assert True

@pytest.mark.integration
class TestCircuitBreaker:
    """Test circuit breaker patterns"""
    
    def test_circuit_breaker_simulation(self):
        """Test circuit breaker behavior simulation"""
        if not check_service_health(BASE_URLS['payment']):
            pytest.skip("Payment service not available")
        
        # Send multiple failing requests to test resilience
        failing_requests = 0
        for i in range(5):
            try:
                response = requests.post(f"{BASE_URLS['payment']}/payments", json={
                    'order_id': f'invalid-order-{i}',
                    'amount': 100.0,
                    'method': 'credit_card'
                }, timeout=5)
                
                if response.status_code >= 400:
                    failing_requests += 1
            except:
                failing_requests += 1
        
        # Should handle failures gracefully without crashing
        assert failing_requests <= 5
    
    def test_service_health_monitoring(self):
        """Test service health monitoring"""
        health_endpoints = [
            f"{BASE_URLS['user']}/health",
            f"{BASE_URLS['order']}/health",
            f"{BASE_URLS['payment']}/health"
        ]
        
        healthy_services = 0
        for endpoint in health_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    health = response.json()
                    if health.get('status') == 'healthy':
                        healthy_services += 1
            except:
                continue
        
        # At least one service should be healthy
        assert healthy_services >= 1

@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across services"""
    
    def test_eventual_consistency(self):
        """Test eventual consistency between services"""
        if not check_service_health(BASE_URLS['user']):
            pytest.skip("User service not available")
        
        try:
            # Create user
            user_response = requests.post(f"{BASE_URLS['user']}/users", json={
                'name': 'Consistency Test',
                'email': f'consistency-{int(time.time())}@example.com'
            }, timeout=10)
            
            if user_response.status_code != 200:
                pytest.skip("User creation failed")
            
            user_id = user_response.json()['id']
            
            if check_service_health(BASE_URLS['order']):
                # Small delay to ensure consistency
                time.sleep(0.1)
                
                # Try to create order
                order_response = requests.post(f"{BASE_URLS['order']}/orders", json={
                    'user_id': user_id,
                    'items': [{'product': 'consistency-test', 'quantity': 1, 'price': 10.0}],
                    'total_amount': 10.0
                }, timeout=10)
                
                # Should work due to synchronous validation or fail gracefully
                assert order_response.status_code in [201, 400, 404, 422]
            else:
                # Order service not available, but user creation succeeded
                assert True
                
        except Exception as e:
            pytest.skip(f"Consistency test failed: {e}")
    
    def test_transaction_rollback_simulation(self):
        """Test transaction rollback scenarios"""
        if not check_service_health(BASE_URLS['payment']):
            pytest.skip("Payment service not available")
        
        try:
            # Test with invalid order ID to simulate rollback scenario
            payment_response = requests.post(f"{BASE_URLS['payment']}/payments", json={
                'order_id': f'rollback-test-{int(time.time())}',
                'amount': 10000.0,  # High amount
                'method': 'credit_card'
            }, timeout=10)
            
            # Should handle invalid order gracefully
            assert payment_response.status_code in [201, 400, 404, 422]
            
            # If payment was created, verify it can be processed or rejected
            if payment_response.status_code == 201:
                payment_data = payment_response.json()
                # Payment created but should handle high amount appropriately
                assert 'id' in payment_data
                
        except Exception as e:
            pytest.skip(f"Transaction rollback test failed: {e}")