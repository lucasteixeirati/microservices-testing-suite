from locust import HttpUser, task, between
import random
import uuid

class UserServiceLoadTest(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8001"
    
    def on_start(self):
        """Setup method called when user starts"""
        self.created_users = []
    
    @task(3)
    def create_user(self):
        """Create a new user"""
        user_data = {
            'name': f'LoadTest User {random.randint(1, 10000)}',
            'email': f'loadtest{uuid.uuid4().hex[:8]}@example.com'
        }
        
        with self.client.post('/users', json=user_data, catch_response=True) as response:
            if response.status_code == 200:
                user = response.json()
                self.created_users.append(user['id'])
                response.success()
            else:
                response.failure(f"Failed to create user: {response.status_code}")
    
    @task(2)
    def get_user(self):
        """Get an existing user"""
        if self.created_users:
            user_id = random.choice(self.created_users)
            with self.client.get(f'/users/{user_id}', catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to get user: {response.status_code}")
    
    @task(1)
    def list_users(self):
        """List all users"""
        with self.client.get('/users', catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list users: {response.status_code}")

class OrderServiceLoadTest(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:8002"
    
    def on_start(self):
        # Create a test user first
        user_response = self.client.post(
            'http://localhost:8001/users',
            json={'name': 'Load Test User', 'email': f'load{uuid.uuid4()}@test.com'}
        )
        if user_response.status_code == 200:
            self.user_id = user_response.json()['id']
        else:
            self.user_id = 'test-user-id'
        
        self.created_orders = []
    
    @task(3)
    def create_order(self):
        """Create a new order"""
        order_data = {
            'user_id': self.user_id,
            'items': [
                {
                    'product': f'Product {random.randint(1, 100)}',
                    'quantity': random.randint(1, 5),
                    'price': round(random.uniform(10, 500), 2)
                }
            ],
            'total_amount': round(random.uniform(10, 500), 2)
        }
        
        # Get CSRF token for order service
        headers = {}
        csrf_response = self.client.get('/csrf-token', catch_response=True)
        if csrf_response.status_code == 200:
            csrf_token = csrf_response.json().get('csrfToken')
            if csrf_token:
                headers['X-CSRF-Token'] = csrf_token
        
        with self.client.post('/orders', json=order_data, headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                order = response.json()
                self.created_orders.append(order['id'])
                response.success()
            elif response.status_code == 403:
                # CSRF issue - get fresh token and retry once
                csrf_response = self.client.get('/csrf-token', catch_response=True)
                if csrf_response.status_code == 200:
                    csrf_token = csrf_response.json().get('csrfToken')
                    if csrf_token:
                        headers['X-CSRF-Token'] = csrf_token
                        retry_response = self.client.post('/orders', json=order_data, headers=headers, catch_response=True)
                        if retry_response.status_code == 201:
                            order = retry_response.json()
                            self.created_orders.append(order['id'])
                            response.success()
                        else:
                            response.failure(f"Failed to create order: {retry_response.status_code}")
                    else:
                        response.failure(f"Failed to create order: {response.status_code}")
                else:
                    response.failure(f"Failed to create order: {response.status_code}")
            else:
                response.failure(f"Failed to create order: {response.status_code}")
    
    @task(2)
    def get_order(self):
        """Get an existing order"""
        if self.created_orders:
            order_id = random.choice(self.created_orders)
            with self.client.get(f'/orders/{order_id}', catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to get order: {response.status_code}")
    
    @task(1)
    def update_order_status(self):
        """Update order status"""
        if self.created_orders:
            order_id = random.choice(self.created_orders)
            status = random.choice(['pending', 'completed', 'cancelled'])
            
            # Get CSRF token for PATCH
            headers = {}
            csrf_response = self.client.get('/csrf-token', catch_response=True)
            if csrf_response.status_code == 200:
                csrf_token = csrf_response.json().get('csrfToken')
                if csrf_token:
                    headers['X-CSRF-Token'] = csrf_token
            
            with self.client.patch(
                f'/orders/{order_id}/status',
                json={'status': status},
                headers=headers,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to update order: {response.status_code}")

class PaymentServiceLoadTest(HttpUser):
    wait_time = between(2, 5)  # Increased wait time
    host = "http://localhost:8003"
    
    def on_start(self):
        # Get CSRF token first
        self.csrf_token = self.get_csrf_token()
        
        # Create test user and order
        user_response = self.client.post(
            'http://localhost:8001/users',
            json={'name': 'Payment Test User', 'email': f'payment{uuid.uuid4()}@test.com'}
        )
        
        if user_response.status_code == 200:
            user_id = user_response.json()['id']
            
            order_response = self.client.post(
                'http://localhost:8002/orders',
                json={
                    'user_id': user_id,
                    'items': [{'product': 'test', 'quantity': 1}],
                    'total_amount': 100.0
                }
            )
            
            if order_response.status_code == 201:
                self.order_id = order_response.json()['id']
            else:
                self.order_id = 'test-order-id'
        else:
            self.order_id = 'test-order-id'
        
        self.created_payments = []
    
    def get_csrf_token(self):
        """Get CSRF token with retry logic"""
        for attempt in range(3):
            try:
                # Try to get a generated token from a failed request
                response = self.client.post('/payments', json={}, catch_response=True)
                if 'X-Generated-CSRF-Token' in response.headers:
                    return response.headers['X-Generated-CSRF-Token']
                # Wait before retry
                import time
                time.sleep(1)
            except:
                pass
        return None
    
    @task(3)
    def create_payment(self):
        """Create a new payment with retry logic"""
        payment_data = {
            'order_id': self.order_id,
            'amount': round(random.uniform(10, 1000), 2),
            'method': random.choice(['credit_card', 'debit_card', 'paypal'])
        }
        
        headers = {}
        if self.csrf_token:
            headers['X-CSRF-Token'] = self.csrf_token
        
        # Retry logic for payment creation
        for attempt in range(3):
            with self.client.post('/payments', json=payment_data, headers=headers, catch_response=True) as response:
                if response.status_code == 201:
                    payment = response.json()
                    self.created_payments.append(payment['id'])
                    response.success()
                    return
                elif response.status_code == 403 and 'X-Generated-CSRF-Token' in response.headers:
                    # Update CSRF token and retry
                    self.csrf_token = response.headers['X-Generated-CSRF-Token']
                    headers['X-CSRF-Token'] = self.csrf_token
                    continue
                elif attempt == 2:  # Last attempt
                    response.failure(f"Failed to create payment after retries: {response.status_code}")
                    return
            
            # Wait before retry
            import time
            time.sleep(0.5)
    
    @task(2)
    def process_payment(self):
        """Process an existing payment with retry"""
        if self.created_payments:
            payment_id = random.choice(self.created_payments)
            
            headers = {}
            if self.csrf_token:
                headers['X-CSRF-Token'] = self.csrf_token
            
            for attempt in range(2):
                with self.client.post(f'/payments/{payment_id}/process', headers=headers, catch_response=True) as response:
                    if response.status_code == 200:
                        response.success()
                        return
                    elif response.status_code == 403 and 'X-Generated-CSRF-Token' in response.headers:
                        self.csrf_token = response.headers['X-Generated-CSRF-Token']
                        headers['X-CSRF-Token'] = self.csrf_token
                        continue
                    elif attempt == 1:
                        response.failure(f"Failed to process payment: {response.status_code}")
                        return
    
    @task(1)
    def get_payment(self):
        """Get payment details"""
        if self.created_payments:
            payment_id = random.choice(self.created_payments)
            with self.client.get(f'/payments/{payment_id}', catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to get payment: {response.status_code}")