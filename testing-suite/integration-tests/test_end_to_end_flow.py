import pytest
import requests
import time
from typing import Dict

pytestmark = pytest.mark.integration, Any

# Default timeout for all requests
DEFAULT_TIMEOUT = 10

class TestEndToEndFlow:
    
    BASE_URLS = {
        'user': 'http://localhost:8001',
        'order': 'http://localhost:8002', 
        'payment': 'http://localhost:8003'
    }
    
    def setup_method(self):
        # Wait for services to be ready
        self._wait_for_services()
    
    def _wait_for_services(self, timeout=30):
        """Wait for all services to be healthy"""
        for service, url in self.BASE_URLS.items():
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{url}/health", timeout=DEFAULT_TIMEOUT)
                    if response.status_code == 200:
                        break
                except requests.RequestException:
                    time.sleep(1)
            else:
                pytest.fail(f"{service} service not ready after {timeout}s")
    
    def test_complete_order_flow(self):
        """Test complete flow: Create User -> Create Order -> Process Payment"""
        
        # 1. Create User
        user_data = {
            'name': 'Integration Test User',
            'email': 'test@integration.com'
        }
        
        user_response = requests.post(
            f"{self.BASE_URLS['user']}/users",
            json=user_data,
            timeout=DEFAULT_TIMEOUT
        )
        assert user_response.status_code == 200
        user = user_response.json()
        user_id = user['id']
        
        # 2. Create Order
        order_data = {
            'user_id': user_id,
            'items': [
                {'product': 'laptop', 'quantity': 1, 'price': 999.99}
            ],
            'total_amount': 999.99
        }
        
        order_response = requests.post(
            f"{self.BASE_URLS['order']}/orders",
            json=order_data,
            timeout=DEFAULT_TIMEOUT
        )
        assert order_response.status_code == 201
        order = order_response.json()
        order_id = order['id']
        
        # 3. Create Payment
        payment_data = {
            'order_id': order_id,
            'amount': 999.99,
            'method': 'credit_card'
        }
        
        payment_response = requests.post(
            f"{self.BASE_URLS['payment']}/payments",
            json=payment_data,
            timeout=DEFAULT_TIMEOUT
        )
        assert payment_response.status_code == 201
        payment = payment_response.json()
        payment_id = payment['id']
        
        # 4. Process Payment
        process_response = requests.post(
            f"{self.BASE_URLS['payment']}/payments/{payment_id}/process",
            timeout=DEFAULT_TIMEOUT
        )
        assert process_response.status_code == 200
        processed_payment = process_response.json()
        assert processed_payment['status'] == 'completed'
        
        # 5. Update Order Status
        status_response = requests.patch(
            f"{self.BASE_URLS['order']}/orders/{order_id}/status",
            json={'status': 'completed'},
            timeout=DEFAULT_TIMEOUT
        )
        assert status_response.status_code == 200
        
        # 6. Verify final state
        final_order = requests.get(f"{self.BASE_URLS['order']}/orders/{order_id}", timeout=DEFAULT_TIMEOUT)
        assert final_order.json()['status'] == 'completed'
    
    def test_order_with_invalid_user(self):
        """Test order creation with non-existent user"""
        order_data = {
            'user_id': 'non-existent-user',
            'items': [{'product': 'laptop', 'quantity': 1}],
            'total_amount': 999.99
        }
        
        response = requests.post(
            f"{self.BASE_URLS['order']}/orders",
            json=order_data
        )
        assert response.status_code == 400
        assert 'User not found' in response.json()['error']
    
    def test_payment_with_invalid_order(self):
        """Test payment creation with non-existent order"""
        payment_data = {
            'order_id': 'non-existent-order',
            'amount': 999.99,
            'method': 'credit_card'
        }
        
        response = requests.post(
            f"{self.BASE_URLS['payment']}/payments",
            json=payment_data
        )
        assert response.status_code == 400
        assert 'Order not found' in response.json()['error']
    
    def test_high_amount_payment_failure(self):
        """Test payment failure for high amounts"""
        # Create user and order first
        user_response = requests.post(
            f"{self.BASE_URLS['user']}/users",
            json={'name': 'High Amount User', 'email': 'high@test.com'}
        )
        user_id = user_response.json()['id']
        
        order_response = requests.post(
            f"{self.BASE_URLS['order']}/orders",
            json={
                'user_id': user_id,
                'items': [{'product': 'expensive_item', 'quantity': 1}],
                'total_amount': 2000.00  # High amount
            }
        )
        order_id = order_response.json()['id']
        
        # Create and process payment
        payment_response = requests.post(
            f"{self.BASE_URLS['payment']}/payments",
            json={
                'order_id': order_id,
                'amount': 2000.00,
                'method': 'credit_card'
            }
        )
        payment_id = payment_response.json()['id']
        
        process_response = requests.post(
            f"{self.BASE_URLS['payment']}/payments/{payment_id}/process"
        )
        processed_payment = process_response.json()
        assert processed_payment['status'] == 'failed'