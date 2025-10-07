import pytest
import requests
import docker
import time
import random
import threading
from typing import List
from docker.errors import APIError, NotFound

class AdvancedChaosTestSuite:
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.services = ['user-service', 'order-service', 'payment-service']
        self.base_urls = {
            'user-service': 'http://localhost:8001',
            'order-service': 'http://localhost:8002',
            'payment-service': 'http://localhost:8003'
        }
    
    def get_container(self, service_name: str):
        """Get container by service name"""
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                if service_name in container.name:
                    return container
        except (APIError, NotFound) as e:
            print(f"Docker error getting container {service_name}: {e}")
        except Exception as e:
            print(f"Unexpected error getting container {service_name}: {e}")
        return None
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if service is responding"""
        try:
            url = self.base_urls[service_name]
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
        except Exception as e:
            print(f"Unexpected error checking health for {service_name}: {e}")
            return False

class TestAdvancedChaosExperiments(AdvancedChaosTestSuite):
    
    @pytest.mark.chaos
    def test_rolling_restart_chaos(self):
        """Test rolling restart of all services"""
        services_to_restart = ['user-service', 'order-service', 'payment-service']
        restart_results = {}
        
        for service in services_to_restart:
            container = self.get_container(service)
            if not container:
                continue
            
            print(f"Rolling restart: {service}")
            
            # Record initial state
            initial_health = self.is_service_healthy(service)
            
            # Restart service
            try:
                container.restart()
                time.sleep(5)  # Wait for restart
                
                # Check recovery
                recovery_time = 0
                max_wait = 60
                
                while recovery_time < max_wait:
                    if self.is_service_healthy(service):
                        break
                    time.sleep(2)
                    recovery_time += 2
                
                final_health = self.is_service_healthy(service)
                
                restart_results[service] = {
                    'initial_health': initial_health,
                    'final_health': final_health,
                    'recovery_time': recovery_time
                }
                
            except Exception as e:
                restart_results[service] = {
                    'error': str(e),
                    'final_health': False
                }
        
        # Verify at least one service recovered
        recovered_services = [s for s, r in restart_results.items() if r.get('final_health', False)]
        assert len(recovered_services) >= 1, "No services recovered from rolling restart"
    
    @pytest.mark.chaos
    def test_memory_pressure_simulation(self):
        """Test system behavior under memory pressure"""
        # Simulate memory pressure by creating many requests
        def memory_intensive_operation(thread_id):
            results = []
            
            for i in range(20):  # 20 operations per thread
                try:
                    # Create user (memory allocation)
                    user_data = {
                        'name': f'Memory Pressure User {thread_id}-{i}',
                        'email': f'memory{thread_id}_{i}@test.com'
                    }
                    
                    response = requests.post(
                        'http://localhost:8001/users',
                        json=user_data,
                        timeout=10
                    )
                    
                    results.append({
                        'thread_id': thread_id,
                        'operation': i,
                        'success': response.status_code in [200, 201],
                        'status_code': response.status_code
                    })
                    
                except Exception as e:
                    results.append({
                        'thread_id': thread_id,
                        'operation': i,
                        'success': False,
                        'error': str(e)
                    })
            
            return results
        
        # Start 5 threads with memory-intensive operations
        threads = []
        thread_results = []
        
        for thread_id in range(5):
            thread = threading.Thread(
                target=lambda tid=thread_id: thread_results.extend(memory_intensive_operation(tid))
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=60)
        
        # Analyze results
        successful_operations = [r for r in thread_results if r.get('success', False)]
        total_operations = len(thread_results)
        
        if total_operations > 0:
            success_rate = len(successful_operations) / total_operations
            # Under memory pressure, at least 50% should still succeed
            assert success_rate >= 0.5, f"Success rate too low under memory pressure: {success_rate:.2%}"
    
    @pytest.mark.chaos
    def test_network_latency_simulation(self):
        """Test system behavior with network latency"""
        # Simulate network latency by making requests with delays
        latency_results = []
        
        for delay in [0, 0.1, 0.5, 1.0]:  # Different latency levels
            start_time = time.time()
            
            try:
                # Add artificial delay
                time.sleep(delay)
                
                response = requests.get('http://localhost:8001/health', timeout=5)
                end_time = time.time()
                
                total_time = (end_time - start_time) * 1000  # Convert to ms
                
                latency_results.append({
                    'artificial_delay': delay * 1000,  # Convert to ms
                    'total_time': total_time,
                    'success': response.status_code == 200,
                    'actual_service_time': total_time - (delay * 1000)
                })
                
            except Exception as e:
                latency_results.append({
                    'artificial_delay': delay * 1000,
                    'error': str(e),
                    'success': False
                })
        
        # Verify service still responds under latency
        successful_requests = [r for r in latency_results if r.get('success', False)]
        assert len(successful_requests) >= 2, "Service should handle network latency"
    
    @pytest.mark.chaos
    def test_cpu_intensive_load(self):
        """Test system behavior under CPU-intensive load"""
        def cpu_intensive_task():
            # Simulate CPU-intensive work
            results = []
            
            for i in range(10):
                start_time = time.time()
                
                # CPU-intensive calculation
                total = sum(j * j for j in range(1000))
                
                # Make service request during CPU load
                try:
                    response = requests.get('http://localhost:8001/health', timeout=5)
                    end_time = time.time()
                    
                    results.append({
                        'iteration': i,
                        'cpu_work': total,
                        'response_time': (end_time - start_time) * 1000,
                        'success': response.status_code == 200
                    })
                    
                except Exception as e:
                    results.append({
                        'iteration': i,
                        'error': str(e),
                        'success': False
                    })
            
            return results
        
        # Run CPU-intensive tasks
        results = cpu_intensive_task()
        
        successful_requests = [r for r in results if r.get('success', False)]
        
        # Service should still respond during CPU load
        if len(results) > 0:
            success_rate = len(successful_requests) / len(results)
            assert success_rate >= 0.7, f"Service degraded too much under CPU load: {success_rate:.2%}"
    
    @pytest.mark.chaos
    def test_disk_io_stress(self):
        """Test system behavior under disk I/O stress"""
        # Simulate disk I/O stress by creating many users (database writes)
        io_results = []
        
        for batch in range(5):  # 5 batches of operations
            batch_results = []
            
            # Create multiple users in quick succession (disk I/O stress)
            for i in range(10):
                try:
                    user_data = {
                        'name': f'IO Stress User {batch}-{i}',
                        'email': f'iostress{batch}_{i}@test.com'
                    }
                    
                    start_time = time.time()
                    response = requests.post(
                        'http://localhost:8001/users',
                        json=user_data,
                        timeout=10
                    )
                    end_time = time.time()
                    
                    batch_results.append({
                        'batch': batch,
                        'user': i,
                        'response_time': (end_time - start_time) * 1000,
                        'success': response.status_code in [200, 201]
                    })
                    
                except Exception as e:
                    batch_results.append({
                        'batch': batch,
                        'user': i,
                        'error': str(e),
                        'success': False
                    })
            
            io_results.extend(batch_results)
            time.sleep(1)  # Brief pause between batches
        
        # Analyze I/O stress results
        successful_operations = [r for r in io_results if r.get('success', False)]
        
        if len(io_results) > 0:
            success_rate = len(successful_operations) / len(io_results)
            avg_response_time = sum(r.get('response_time', 0) for r in successful_operations) / len(successful_operations) if successful_operations else 0
            
            # Under I/O stress, should maintain reasonable performance
            assert success_rate >= 0.6, f"I/O stress caused too many failures: {success_rate:.2%}"
            assert avg_response_time < 2000, f"I/O stress caused excessive response times: {avg_response_time:.2f}ms"
    
    @pytest.mark.chaos
    def test_gradual_load_increase(self):
        """Test system behavior with gradually increasing load"""
        load_levels = [1, 3, 5, 8, 10]  # Gradual increase
        load_results = {}
        
        for load_level in load_levels:
            print(f"Testing load level: {load_level}")
            
            def make_request(req_id):
                try:
                    start_time = time.time()
                    response = requests.get('http://localhost:8001/health', timeout=10)
                    end_time = time.time()
                    
                    return {
                        'request_id': req_id,
                        'response_time': (end_time - start_time) * 1000,
                        'success': response.status_code == 200
                    }
                except Exception as e:
                    return {
                        'request_id': req_id,
                        'error': str(e),
                        'success': False
                    }
            
            # Execute concurrent requests
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=load_level) as executor:
                futures = [executor.submit(make_request, i) for i in range(load_level)]
                level_results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=30)]
            
            successful_requests = [r for r in level_results if r.get('success', False)]
            
            if successful_requests:
                avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
                success_rate = len(successful_requests) / len(level_results)
                
                load_results[load_level] = {
                    'avg_response_time': avg_response_time,
                    'success_rate': success_rate,
                    'total_requests': len(level_results)
                }
            
            time.sleep(2)  # Brief pause between load levels
        
        # Verify graceful degradation
        if len(load_results) >= 2:
            # System should handle increasing load reasonably
            first_level = min(load_results.keys())
            last_level = max(load_results.keys())
            
            first_success_rate = load_results[first_level]['success_rate']
            last_success_rate = load_results[last_level]['success_rate']
            
            # Success rate shouldn't drop below 50% even under high load
            assert last_success_rate >= 0.5, f"System failed under load: {last_success_rate:.2%}"
    
    @pytest.mark.chaos
    def test_service_dependency_failure_cascade(self):
        """Test cascade failure when dependencies fail"""
        # Test order service behavior when user service fails
        user_container = self.get_container('user-service')
        
        if user_container:
            try:
                # Stop user service
                user_container.stop()
                time.sleep(5)
                
                # Try to create order (should fail gracefully)
                order_data = {
                    'user_id': 'test-user',
                    'items': [{'product': 'test', 'quantity': 1}],
                    'total_amount': 100.0
                }
                
                try:
                    response = requests.post(
                        'http://localhost:8002/orders',
                        json=order_data,
                        timeout=10
                    )
                    
                    # Should fail gracefully, not crash
                    assert response.status_code in [400, 500, 503, 504]
                    
                except requests.RequestException:
                    # Connection error is acceptable
                    pass
                
                # Restart user service
                user_container.start()
                time.sleep(10)
                
                # Verify recovery
                recovery_successful = False
                for attempt in range(10):
                    if self.is_service_healthy('user-service'):
                        recovery_successful = True
                        break
                    time.sleep(2)
                
                assert recovery_successful, "User service failed to recover"
                
            except Exception as e:
                # Ensure service is restarted even if test fails
                try:
                    user_container.start()
                except:
                    pass
                raise e