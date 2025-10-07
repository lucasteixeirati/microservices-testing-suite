import pytest
import requests
import docker
import time
import random
from typing import List

pytestmark = pytest.mark.chaos

class ChaosTestSuite:
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception:
            self.docker_client = None
            self.docker_available = False
        
        self.services = ['user-service', 'order-service', 'payment-service']
        self.base_urls = {
            'user-service': 'http://localhost:8001',
            'order-service': 'http://localhost:8002',
            'payment-service': 'http://localhost:8003'
        }
    
    def get_container(self, service_name: str):
        """Get container by service name"""
        if not self.docker_available:
            return None
        
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                if service_name in container.name:
                    return container
        except Exception:
            pass
        return None
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if service is responding"""
        try:
            url = self.base_urls[service_name]
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_service_recovery(self, service_name: str, timeout: int = 60):
        """Wait for service to recover"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_service_healthy(service_name):
                return True
            time.sleep(2)
        return False

class TestChaosExperiments:
    
    def setup_method(self):
        self.chaos_suite = ChaosTestSuite()
    
    @pytest.mark.chaos
    def test_service_restart_resilience(self):
        """Test system resilience when a service is restarted"""
        target_service = 'order-service'
        container = self.chaos_suite.get_container(target_service)
        
        if not container:
            pytest.skip(f"Container for {target_service} not found")
        
        # Verify service is initially healthy
        assert self.chaos_suite.is_service_healthy(target_service)
        
        # Restart container
        container.restart()
        
        # Wait for recovery
        recovered = self.chaos_suite.wait_for_service_recovery(target_service)
        assert recovered, f"{target_service} did not recover within timeout"
        
        # Test that other services are still functional
        assert self.chaos_suite.is_service_healthy('user-service')
        assert self.chaos_suite.is_service_healthy('payment-service')
    
    @pytest.mark.chaos
    def test_service_kill_and_recovery(self):
        """Test system behavior when a service is killed"""
        target_service = 'payment-service'
        container = self.chaos_suite.get_container(target_service)
        
        if not container:
            pytest.skip(f"Container for {target_service} not found")
        
        # Kill and restart container
        container.kill()
        container.start()
        
        # Wait for recovery
        recovered = self.chaos_suite.wait_for_service_recovery(target_service)
        assert recovered, f"{target_service} did not recover after restart"
    
    @pytest.mark.chaos
    def test_cascade_failure_simulation(self):
        """Test how system handles cascade failures"""
        # Create a user first
        user_response = requests.post(
            'http://localhost:8001/users',
            json={'name': 'Chaos User', 'email': 'chaos@test.com'}
        )
        
        if user_response.status_code != 200:
            pytest.skip("Could not create test user")
        
        user_id = user_response.json()['id']
        
        # Kill user service to simulate cascade failure
        user_container = self.chaos_suite.get_container('user-service')
        if user_container:
            user_container.kill()
        
        # Try to create order (should fail gracefully)
        order_response = requests.post(
            'http://localhost:8002/orders',
            json={
                'user_id': user_id,
                'items': [{'product': 'test', 'quantity': 1}],
                'total_amount': 100.0
            }
        )
        
        # Should fail with proper error handling
        assert order_response.status_code in [400, 500, 503]
        
        # Restart user service
        if user_container:
            user_container.start()
    
    @pytest.mark.chaos
    def test_random_service_disruption(self):
        """Randomly disrupt services and test recovery"""
        disruption_count = 3
        
        for _ in range(disruption_count):
            # Choose random service
            target_service = random.choice(self.chaos_suite.services)
            container = self.chaos_suite.get_container(target_service)
            
            if not container:
                continue
            
            print(f"Disrupting {target_service}...")
            
            # Random disruption type
            disruption_type = random.choice(['restart', 'pause', 'kill'])
            
            if disruption_type == 'restart':
                container.restart()
            elif disruption_type == 'pause':
                container.pause()
                time.sleep(5)  # Keep paused for 5 seconds
                container.unpause()
            elif disruption_type == 'kill':
                container.kill()
                time.sleep(2)
                container.start()
            
            # Wait for recovery
            recovered = self.chaos_suite.wait_for_service_recovery(target_service, timeout=30)
            assert recovered, f"{target_service} did not recover from {disruption_type}"
            
            # Brief pause between disruptions
            time.sleep(2)
    
    @pytest.mark.chaos
    def test_network_partition_simulation(self):
        """Simulate network partitions between services"""
        # Stop order service to simulate network partition
        order_container = self.chaos_suite.get_container('order-service')
        if order_container:
            order_container.stop()
        
        # Test that user service still works
        user_response = requests.post(
            'http://localhost:8001/users',
            json={'name': 'Partition Test', 'email': 'partition@test.com'}
        )
        assert user_response.status_code == 200
        
        # Test that payment service handles missing order service
        payment_response = requests.post(
            'http://localhost:8003/payments',
            json={
                'order_id': 'non-existent',
                'amount': 100.0,
                'method': 'credit_card'
            }
        )
        # Should fail gracefully
        assert payment_response.status_code in [400, 500, 503]
        
        # Restore order service
        if order_container:
            order_container.start()
            self.chaos_suite.wait_for_service_recovery('order-service')
    
    @pytest.mark.chaos
    def test_resource_exhaustion(self):
        """Test behavior under resource constraints"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_requests():
            for i in range(50):
                try:
                    response = requests.post(
                        'http://localhost:8001/users',
                        json={'name': f'Stress User {i}', 'email': f'stress{i}@test.com'},
                        timeout=10
                    )
                    results.put(response.status_code)
                except Exception as e:
                    results.put(f"Error: {e}")
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Analyze results
        success_count = 0
        total_requests = 0
        
        while not results.empty():
            result = results.get()
            total_requests += 1
            if result == 200:
                success_count += 1
        
        # At least 80% should succeed even under stress
        success_rate = success_count / total_requests if total_requests > 0 else 0
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"