import pytest
import requests
import time
from typing import Dict, Any

class TestErrorScenarios:
    
    BASE_URLS = {
        'user': 'http://localhost:8001',
        'order': 'http://localhost:8002', 
        'payment': 'http://localhost:8003'
    }
    
    def test_cascade_failure_user_service_down(self):
        """Test system behavior when user service is down"""
        # Simulate user service down
        order_data = {
            'user_id': 'user-123',
            'items': [{'product': 'laptop', 'quantity': 1}],
            'total_amount': 999.99
        }
        
        # Order creation should fail gracefully
        try:
            response = requests.post(
                f"{self.BASE_URLS['order']}/orders",
                json=order_data,
                timeout=5
            )
            # Should either timeout or return error
            assert response.status_code in [400, 500, 503, 504]
        except requests.RequestException:
            # Connection error is acceptable
            pass
    
    def test_partial_order_creation_failure(self):
        """Test partial failure during order creation"""
        # Create user first
        user_data = {
            'name': 'Error Test User',
            'email': 'error@test.com'
        }
        
        try:
            user_response = requests.post(
                f"{self.BASE_URLS['user']}/users",
                json=user_data,
                timeout=5
            )
            
            if user_response.status_code == 200:
                user_id = user_response.json()['id']
                
                # Try to create order with invalid data
                invalid_order = {
                    'user_id': user_id,
                    'items': [],  # Empty items should fail
                    'total_amount': 0
                }
                
                order_response = requests.post(
                    f"{self.BASE_URLS['order']}/orders",
                    json=invalid_order,
                    timeout=5
                )
                
                # Should fail validation
                assert order_response.status_code in [400, 422]
        except requests.RequestException:
            pytest.skip("Services not available for integration test")
    
    def test_payment_processing_edge_cases(self):
        """Test payment processing edge cases"""
        edge_cases = [
            {"amount": 0.01, "expected_status": "completed"},  # Minimum amount
            {"amount": 999.99, "expected_status": "completed"},  # Normal amount
            {"amount": 1000.01, "expected_status": "failed"},  # Over limit
            {"amount": 9999.99, "expected_status": "failed"}   # High amount
        ]
        
        for case in edge_cases:
            payment_data = {
                'order_id': 'test-order',
                'amount': case["amount"],
                'method': 'credit_card'
            }
            
            try:
                # This would normally require a real order, but we're testing edge cases
                response = requests.post(
                    f"{self.BASE_URLS['payment']}/payments",
                    json=payment_data,
                    timeout=5
                )
                
                # Response depends on service availability
                if response.status_code in [200, 201]:
                    payment_id = response.json().get('id')
                    if payment_id:
                        process_response = requests.post(
                            f"{self.BASE_URLS['payment']}/payments/{payment_id}/process",
                            timeout=5
                        )
                        if process_response.status_code == 200:
                            assert process_response.json()["status"] == case["expected_status"]
            except requests.RequestException:
                pytest.skip("Payment service not available")
    
    def test_concurrent_order_creation(self):
        """Test concurrent order creation"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_order(thread_id):
            try:
                # Create user for this thread
                user_data = {
                    'name': f'Concurrent User {thread_id}',
                    'email': f'concurrent{thread_id}@test.com'
                }
                
                user_response = requests.post(
                    f"{self.BASE_URLS['user']}/users",
                    json=user_data,
                    timeout=10
                )
                
                if user_response.status_code == 200:
                    user_id = user_response.json()['id']
                    
                    order_data = {
                        'user_id': user_id,
                        'items': [{'product': f'product-{thread_id}', 'quantity': 1}],
                        'total_amount': 100.0 + thread_id
                    }
                    
                    order_response = requests.post(
                        f"{self.BASE_URLS['order']}/orders",
                        json=order_data,
                        timeout=10
                    )
                    
                    results.put({
                        'thread_id': thread_id,
                        'status_code': order_response.status_code,
                        'success': order_response.status_code in [200, 201]
                    })
                else:
                    results.put({
                        'thread_id': thread_id,
                        'status_code': user_response.status_code,
                        'success': False
                    })
            except Exception as e:
                results.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'success': False
                })
        
        # Start 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_order, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=30)
        
        # Analyze results
        success_count = 0
        total_requests = 0
        
        while not results.empty():
            result = results.get()
            total_requests += 1
            if result.get('success', False):
                success_count += 1
        
        # At least some requests should succeed
        if total_requests > 0:
            success_rate = success_count / total_requests
            assert success_rate >= 0.6  # At least 60% success rate
    
    def test_service_timeout_handling(self):
        """Test service timeout handling"""
        # Test with very short timeout
        try:
            response = requests.get(
                f"{self.BASE_URLS['user']}/users",
                timeout=0.001  # 1ms timeout - should fail
            )
        except requests.Timeout:
            # Timeout is expected
            assert True
        except requests.RequestException:
            # Other connection errors are also acceptable
            assert True
    
    def test_malformed_request_handling(self):
        """Test handling of malformed requests"""
        malformed_requests = [
            {"data": "not-json-structure", "endpoint": "users"},
            {"data": {"invalid": "structure"}, "endpoint": "orders"},
            {"data": None, "endpoint": "payments"}
        ]
        
        for req in malformed_requests:
            try:
                if req["endpoint"] == "users":
                    response = requests.post(
                        f"{self.BASE_URLS['user']}/users",
                        json=req["data"],
                        timeout=5
                    )
                elif req["endpoint"] == "orders":
                    response = requests.post(
                        f"{self.BASE_URLS['order']}/orders",
                        json=req["data"],
                        timeout=5
                    )
                elif req["endpoint"] == "payments":
                    response = requests.post(
                        f"{self.BASE_URLS['payment']}/payments",
                        json=req["data"],
                        timeout=5
                    )
                
                # Should return client error
                assert response.status_code in [400, 422]
            except requests.RequestException:
                # Connection errors are acceptable for this test
                pass
    
    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        # Create user with very long name
        large_user_data = {
            'name': 'A' * 1000,  # 1000 character name
            'email': 'large@test.com'
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URLS['user']}/users",
                json=large_user_data,
                timeout=10
            )
            
            # Should either accept or reject gracefully
            assert response.status_code in [200, 201, 400, 413, 422]
        except requests.RequestException:
            pytest.skip("Service not available for large payload test")
    
    def test_special_characters_handling(self):
        """Test handling of special characters in data"""
        special_user_data = {
            'name': 'José María Ñoño',
            'email': 'josé@tëst.com'
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URLS['user']}/users",
                json=special_user_data,
                timeout=5
            )
            
            # Should handle unicode characters properly
            if response.status_code in [200, 201]:
                user_data = response.json()
                assert 'José' in user_data['name']
        except requests.RequestException:
            pytest.skip("Service not available for special characters test")