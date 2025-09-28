import pytest
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestPerformanceScenarios:
    
    BASE_URLS = {
        'user': 'http://localhost:8001',
        'order': 'http://localhost:8002', 
        'payment': 'http://localhost:8003'
    }
    
    def test_response_time_user_service(self):
        """Test user service response time"""
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            try:
                response = requests.get(f"{self.BASE_URLS['user']}/health", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)  # Convert to ms
            except requests.RequestException:
                pytest.skip("User service not available")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            
            # Assert reasonable response times
            assert avg_response_time < 200  # Average < 200ms
            assert p95_response_time < 500  # P95 < 500ms
    
    def test_throughput_user_creation(self):
        """Test user creation throughput"""
        def create_user(user_id):
            try:
                user_data = {
                    'name': f'Throughput User {user_id}',
                    'email': f'throughput{user_id}@test.com'
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.BASE_URLS['user']}/users",
                    json=user_data,
                    timeout=10
                )
                end_time = time.time()
                
                return {
                    'success': response.status_code in [200, 201],
                    'response_time': (end_time - start_time) * 1000,
                    'user_id': user_id
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'user_id': user_id
                }
        
        # Test with 20 concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_user, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures, timeout=30)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in results if r.get('success', False)]
        
        if len(successful_requests) > 0:
            throughput = len(successful_requests) / total_time  # requests per second
            avg_response_time = statistics.mean([r['response_time'] for r in successful_requests])
            
            # Assert reasonable throughput
            assert throughput >= 5  # At least 5 requests per second
            assert avg_response_time < 1000  # Average response time < 1s
    
    def test_memory_usage_simulation(self):
        """Test memory usage with multiple operations"""
        operations = []
        
        # Simulate memory-intensive operations
        for i in range(50):
            try:
                # Create user
                user_data = {
                    'name': f'Memory Test User {i}',
                    'email': f'memory{i}@test.com'
                }
                
                user_response = requests.post(
                    f"{self.BASE_URLS['user']}/users",
                    json=user_data,
                    timeout=5
                )
                
                if user_response.status_code in [200, 201]:
                    operations.append('user_created')
                    
                    # List users (memory read operation)
                    list_response = requests.get(f"{self.BASE_URLS['user']}/users", timeout=5)
                    if list_response.status_code == 200:
                        operations.append('users_listed')
                        
                        # Verify the list grows
                        users = list_response.json()
                        assert len(users) >= i + 1
                
            except requests.RequestException:
                break
        
        # Should complete at least 10 operations
        assert len(operations) >= 20
    
    def test_database_connection_pooling(self):
        """Test database connection handling under load"""
        def make_db_intensive_request(request_id):
            try:
                # Multiple DB operations in sequence
                operations = []
                
                # Create user (INSERT)
                user_data = {
                    'name': f'DB Test User {request_id}',
                    'email': f'db{request_id}@test.com'
                }
                
                create_response = requests.post(
                    f"{self.BASE_URLS['user']}/users",
                    json=user_data,
                    timeout=10
                )
                
                if create_response.status_code in [200, 201]:
                    operations.append('create')
                    user_id = create_response.json()['id']
                    
                    # Read user (SELECT)
                    read_response = requests.get(
                        f"{self.BASE_URLS['user']}/users/{user_id}",
                        timeout=10
                    )
                    
                    if read_response.status_code == 200:
                        operations.append('read')
                    
                    # List users (SELECT with potential JOIN)
                    list_response = requests.get(
                        f"{self.BASE_URLS['user']}/users",
                        timeout=10
                    )
                    
                    if list_response.status_code == 200:
                        operations.append('list')
                
                return {
                    'request_id': request_id,
                    'operations': operations,
                    'success': len(operations) >= 2
                }
                
            except Exception as e:
                return {
                    'request_id': request_id,
                    'error': str(e),
                    'success': False
                }
        
        # Test with 15 concurrent database-intensive requests
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(make_db_intensive_request, i) for i in range(15)]
            results = [future.result() for future in as_completed(futures, timeout=45)]
        
        successful_requests = [r for r in results if r.get('success', False)]
        
        # At least 70% should succeed (database connection pooling working)
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.7
    
    def test_service_scalability_simulation(self):
        """Test service behavior under increasing load"""
        load_levels = [5, 10, 15, 20]  # Number of concurrent requests
        results = {}
        
        for load in load_levels:
            def make_request(req_id):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.BASE_URLS['user']}/health", timeout=10)
                    end_time = time.time()
                    
                    return {
                        'success': response.status_code == 200,
                        'response_time': (end_time - start_time) * 1000
                    }
                except Exception:
                    return {'success': False, 'response_time': float('inf')}
            
            # Execute requests for this load level
            with ThreadPoolExecutor(max_workers=load) as executor:
                futures = [executor.submit(make_request, i) for i in range(load)]
                load_results = [future.result() for future in as_completed(futures, timeout=30)]
            
            successful = [r for r in load_results if r['success']]
            
            if successful:
                avg_response_time = statistics.mean([r['response_time'] for r in successful])
                success_rate = len(successful) / len(load_results)
                
                results[load] = {
                    'avg_response_time': avg_response_time,
                    'success_rate': success_rate
                }
        
        # Verify scalability - response time shouldn't degrade too much
        if len(results) >= 2:
            load_levels_tested = sorted(results.keys())
            first_load = load_levels_tested[0]
            last_load = load_levels_tested[-1]
            
            first_response_time = results[first_load]['avg_response_time']
            last_response_time = results[last_load]['avg_response_time']
            
            # Response time shouldn't increase more than 3x under higher load
            assert last_response_time <= first_response_time * 3
    
    def test_resource_cleanup(self):
        """Test resource cleanup after operations"""
        initial_users = []
        
        try:
            # Get initial state
            initial_response = requests.get(f"{self.BASE_URLS['user']}/users", timeout=5)
            if initial_response.status_code == 200:
                initial_users = initial_response.json()
            
            # Create and delete users to test cleanup
            created_users = []
            
            for i in range(10):
                user_data = {
                    'name': f'Cleanup Test User {i}',
                    'email': f'cleanup{i}@test.com'
                }
                
                create_response = requests.post(
                    f"{self.BASE_URLS['user']}/users",
                    json=user_data,
                    timeout=5
                )
                
                if create_response.status_code in [200, 201]:
                    user_id = create_response.json()['id']
                    created_users.append(user_id)
            
            # Delete created users
            for user_id in created_users:
                requests.delete(f"{self.BASE_URLS['user']}/users/{user_id}", timeout=5)
            
            # Verify cleanup
            final_response = requests.get(f"{self.BASE_URLS['user']}/users", timeout=5)
            if final_response.status_code == 200:
                final_users = final_response.json()
                
                # Should be back to initial state (or close to it)
                assert len(final_users) <= len(initial_users) + 2  # Allow some margin
                
        except requests.RequestException:
            pytest.skip("Service not available for cleanup test")