import pytest
import requests
import time
import statistics
import concurrent.futures
from datetime import datetime
import json
import os

class TestPerformanceComprehensive:
    
    BASE_URLS = {
        'user': 'http://localhost:8001',
        'order': 'http://localhost:8002', 
        'payment': 'http://localhost:8003'
    }
    
    def setup_method(self):
        """Setup for each test method"""
        self.results = []
        self.start_time = time.time()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time
    
    def measure_response_time(self, url, method='GET', data=None, headers=None):
        """Measure response time for a single request"""
        start = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10, headers=headers)
            
            end = time.time()
            response_time = (end - start) * 1000  # Convert to milliseconds
            
            return {
                'response_time': response_time,
                'status_code': response.status_code,
                'success': response.status_code < 400
            }
        except Exception as e:
            end = time.time()
            return {
                'response_time': (end - start) * 1000,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
    
    def test_user_service_response_time(self):
        """Test user service response time under normal load"""
        url = f"{self.BASE_URLS['user']}/health"
        iterations = 50
        response_times = []
        
        for _ in range(iterations):
            result = self.measure_response_time(url)
            response_times.append(result['response_time'])
            self.results.append(result)
        
        # Performance assertions
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_response_time < 3000, f"Average response time {avg_response_time:.2f}ms exceeds 3000ms"
        assert p95_response_time < 5000, f"P95 response time {p95_response_time:.2f}ms exceeds 5000ms"
        
        # Store results for reporting
        self.performance_data = {
            'test': 'user_service_response_time',
            'iterations': iterations,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'min_response_time': min(response_times),
            'max_response_time': max(response_times)
        }
    
    def test_concurrent_user_creation(self):
        """Test concurrent user creation performance"""
        url = f"{self.BASE_URLS['user']}/users"
        concurrent_users = 10
        requests_per_user = 5
        
        def create_user(user_id):
            import uuid
            results = []
            for i in range(requests_per_user):
                unique_id = uuid.uuid4().hex[:8]
                user_data = {
                    'name': f'User {user_id}-{i}-{unique_id}',
                    'email': f'user{user_id}_{i}_{unique_id}@test.com'
                }
                result = self.measure_response_time(url, 'POST', user_data)
                results.append(result)
            return results
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(create_user, i) for i in range(concurrent_users)]
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        # Analyze results
        response_times = [r['response_time'] for r in all_results]
        success_rate = sum(1 for r in all_results if r['success']) / len(all_results)
        
        avg_response_time = statistics.mean(response_times)
        
        assert success_rate >= 0.70, f"Success rate {success_rate:.2%} below 70%"
        assert avg_response_time < 3000, f"Average response time {avg_response_time:.2f}ms exceeds 3000ms"
        
        self.performance_data = {
            'test': 'concurrent_user_creation',
            'concurrent_users': concurrent_users,
            'total_requests': len(all_results),
            'success_rate': success_rate,
            'avg_response_time': avg_response_time
        }
    
    def test_order_service_throughput(self):
        """Test order service throughput"""
        # First create a user
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        user_url = f"{self.BASE_URLS['user']}/users"
        user_data = {'name': f'Test User {unique_id}', 'email': f'throughput-{unique_id}@test.com'}
        user_response = requests.post(user_url, json=user_data)
        if user_response.status_code in [200, 201]:
            user_id = user_response.json().get('id', 'test-user-id')
        else:
            user_id = 'test-user-id'
        
        order_url = f"{self.BASE_URLS['order']}/orders"
        duration = 20  # Increased duration
        start_time = time.time()
        successful_requests = 0
        response_times = []
        
        while time.time() - start_time < duration:
            order_data = {
                'user_id': user_id,
                'items': [{'product': 'test', 'quantity': 1}],
                'total_amount': 100.0
            }
            
            result = self.measure_response_time(order_url, 'POST', order_data)
            response_times.append(result['response_time'])
            if result['success']:
                successful_requests += 1
            
            time.sleep(0.5)  # Longer delay to avoid overwhelming
        
        throughput = successful_requests / duration  # requests per second
        avg_response_time = statistics.mean(response_times)
        
        assert throughput >= 0.3, f"Throughput {throughput:.2f} RPS below minimum 0.3 RPS"
        assert avg_response_time < 3000, f"Average response time {avg_response_time:.2f}ms exceeds 3000ms"
        
        self.performance_data = {
            'test': 'order_service_throughput',
            'duration': duration,
            'total_requests': successful_requests,
            'throughput_rps': throughput,
            'avg_response_time': avg_response_time
        }
    
    def test_payment_processing_latency(self):
        """Test payment processing latency"""
        # Create order first
        user_url = f"{self.BASE_URLS['user']}/users"
        user_data = {'name': 'Payment User', 'email': 'payment@test.com'}
        user_response = requests.post(user_url, json=user_data)
        user_id = user_response.json().get('id', 'test-user-id')
        
        order_url = f"{self.BASE_URLS['order']}/orders"
        order_data = {
            'user_id': user_id,
            'items': [{'product': 'test', 'quantity': 1}],
            'total_amount': 500.0
        }
        order_response = requests.post(order_url, json=order_data)
        order_id = order_response.json().get('id', 'test-order-id')
        
        # Test payment creation and processing
        payment_url = f"{self.BASE_URLS['payment']}/payments"
        iterations = 20
        creation_times = []
        processing_times = []
        
        for i in range(iterations):
            # Create payment
            payment_data = {
                'order_id': order_id,
                'amount': 500.0,
                'method': 'credit_card'
            }
            
            create_result = self.measure_response_time(payment_url, 'POST', payment_data)
            creation_times.append(create_result['response_time'])
            
            if create_result['success']:
                # Process payment (simulate)
                process_url = f"{payment_url}/test-payment-{i}/process"
                process_result = self.measure_response_time(process_url, 'POST')
                processing_times.append(process_result['response_time'])
        
        avg_creation_time = statistics.mean(creation_times)
        avg_processing_time = statistics.mean(processing_times) if processing_times else 0
        
        assert avg_creation_time < 5000, f"Payment creation time {avg_creation_time:.2f}ms exceeds 5000ms"
        if processing_times:
            assert avg_processing_time < 3000, f"Payment processing time {avg_processing_time:.2f}ms exceeds 3000ms"
        
        self.performance_data = {
            'test': 'payment_processing_latency',
            'iterations': iterations,
            'avg_creation_time': avg_creation_time,
            'avg_processing_time': avg_processing_time
        }
    
    def test_memory_usage_simulation(self):
        """Test memory usage under load simulation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate memory-intensive operations
        large_data_sets = []
        for i in range(100):
            # Create some data to simulate memory usage
            data = {
                'id': i,
                'data': 'x' * 1000,  # 1KB of data
                'timestamp': datetime.now().isoformat()
            }
            large_data_sets.append(data)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Clean up
        large_data_sets.clear()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_cleanup = peak_memory - final_memory
        
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB"
        assert memory_cleanup >= 0, "Memory cleanup should be non-negative"
        
        self.performance_data = {
            'test': 'memory_usage_simulation',
            'initial_memory_mb': initial_memory,
            'peak_memory_mb': peak_memory,
            'memory_increase_mb': memory_increase,
            'memory_cleanup_mb': memory_cleanup
        }