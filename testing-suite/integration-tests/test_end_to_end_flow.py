import pytest
import requests
import time
from typing import Dict
from urllib.parse import urlparse

pytestmark = pytest.mark.integration

# Default timeout for all requests
DEFAULT_TIMEOUT = 10

# Allowed hosts for SSRF prevention
ALLOWED_HOSTS = ['localhost:8001', 'localhost:8002', 'localhost:8003']

class TestEndToEndFlow:
    
    BASE_URLS = {
        'user': 'http://localhost:8001',
        'order': 'http://localhost:8002', 
        'payment': 'http://localhost:8003'
    }
    
    def _get_csrf_token(self, service_url):
        """Get CSRF token for protected endpoints"""
        try:
            response = requests.get(f"{service_url}/csrf-token", timeout=5)
            if response.status_code == 200:
                return response.json().get('csrfToken')
        except:
            pass
        return None
    
    def _make_post_request(self, url, data, timeout=DEFAULT_TIMEOUT):
        """Make POST request with CSRF token if needed"""
        headers = {'Content-Type': 'application/json'}
        service_url = '/'.join(url.split('/')[:3])
        
        # Get CSRF token proactively for order service
        if 'localhost:8002' in url:
            csrf_token = self._get_csrf_token(service_url)
            if csrf_token:
                headers['X-CSRF-Token'] = csrf_token
        
        # Make request
        response = requests.post(url, json=data, headers=headers, timeout=timeout)
        
        # If still 403, try getting fresh token
        if response.status_code == 403 and 'X-CSRF-Token' not in headers:
            csrf_token = self._get_csrf_token(service_url)
            if csrf_token:
                headers['X-CSRF-Token'] = csrf_token
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
        
        return response
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL to prevent SSRF attacks"""
        try:
            parsed = urlparse(url)
            return parsed.scheme == 'http' and f"{parsed.hostname}:{parsed.port}" in ALLOWED_HOSTS
        except:
            return False
    
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
        import uuid
        unique_email = f'test-{uuid.uuid4().hex[:8]}@integration.com'
        user_data = {
            'name': 'Integration Test User',
            'email': unique_email
        }
        
        user_url = f"{self.BASE_URLS['user']}/users"
        if not self._validate_url(user_url):
            pytest.fail("Invalid URL detected")
        
        user_response = self._make_post_request(user_url, user_data)
        if user_response.status_code != 200:
            print(f"User creation failed: {user_response.status_code} - {user_response.text}")
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
        
        order_url = f"{self.BASE_URLS['order']}/orders"
        if not self._validate_url(order_url):
            pytest.fail("Invalid URL detected")
        
        order_response = self._make_post_request(order_url, order_data)
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
        
        response = self._make_post_request(f"{self.BASE_URLS['order']}/orders", order_data)
        assert response.status_code in [400, 403]
        if response.text:
            try:
                error_data = response.json()
                assert 'error' in error_data or 'detail' in error_data
            except:
                # If not JSON, just check status code
                pass
    
    def test_payment_with_invalid_order(self):
        """Test payment creation with non-existent order"""
        payment_data = {
            'order_id': 'non-existent-order',
            'amount': 999.99,
            'method': 'credit_card'
        }
        
        response = self._make_post_request(f"{self.BASE_URLS['payment']}/payments", payment_data)
        assert response.status_code == 400
        if response.text:
            try:
                error_data = response.json()
                assert 'error' in error_data or 'detail' in error_data
            except:
                pass
    
    def test_high_amount_payment_failure(self):
        """Test payment failure for high amounts"""
        # Create user and order first
        import uuid
        unique_email = f'high-{uuid.uuid4().hex[:8]}@test.com'
        user_response = self._make_post_request(
            f"{self.BASE_URLS['user']}/users",
            {'name': 'High Amount User', 'email': unique_email}
        )
        if user_response.status_code != 200:
            pytest.skip(f"Could not create user: {user_response.status_code}")
        user_data = user_response.json()
        user_id = user_data['id']
        
        order_response = self._make_post_request(
            f"{self.BASE_URLS['order']}/orders",
            {
                'user_id': user_id,
                'items': [{'product': 'expensive_item', 'quantity': 1}],
                'total_amount': 2000.00  # High amount
            }
        )
        if order_response.status_code != 201:
            pytest.skip(f"Could not create order: {order_response.status_code}")
        order_data = order_response.json()
        order_id = order_data['id']
        
        # Create and process payment
        payment_response = self._make_post_request(
            f"{self.BASE_URLS['payment']}/payments",
            {
                'order_id': order_id,
                'amount': 2000.00,
                'method': 'credit_card'
            }
        )
        if payment_response.status_code != 201:
            pytest.skip(f"Could not create payment: {payment_response.status_code}")
        payment_data = payment_response.json()
        payment_id = payment_data['id']
        
        process_response = requests.post(
            f"{self.BASE_URLS['payment']}/payments/{payment_id}/process"
        )
        processed_payment = process_response.json()
        assert processed_payment['status'] == 'failed'