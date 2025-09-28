#!/usr/bin/env python3
"""
Microservices Testing Suite Runner
Orchestrates different types of tests with proper setup and teardown
"""

import subprocess
import sys
import time
import requests
import argparse
from datetime import datetime
from typing import List, Dict

class TestRunner:
    
    def __init__(self, skip_payment=False):
        self.services = {
            'user-service': 'http://localhost:8001',
            'order-service': 'http://localhost:8002'
        }
        if not skip_payment:
            self.services['payment-service'] = 'http://localhost:8003'
    
    def wait_for_services(self, timeout: int = 60) -> bool:
        """Wait for all services to be ready"""
        print("[WAIT] Waiting for services to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_ready = True
            for service, url in self.services.items():
                try:
                    response = requests.get(f"{url}/health", timeout=5)
                    if response.status_code != 200:
                        all_ready = False
                        break
                except requests.RequestException:
                    all_ready = False
                    break
            
            if all_ready:
                print("[READY] All services are ready!")
                return True
            
            print("[WAIT] Services not ready yet, waiting...")
            time.sleep(5)
        
        print("[TIMEOUT] Services failed to start within timeout")
        print("\n💡 To start services, run:")
        print("   Windows: start-services.bat")
        print("   Linux/Mac: ./start-services.sh")
        print("   Or manually: docker-compose up -d")
        return False
    
    def run_contract_tests(self) -> bool:
        """Run Pact contract tests"""
        print("\n[CONTRACT] Running Contract Tests...")
        
        cmd = [
            'pytest', 
            'contract-tests/',
            '-m', 'contract',
            '--tb=short',
            '-v'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("[SUCCESS] Contract tests passed!")
                return True
            else:
                print("[FAILED] Contract tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Contract tests timed out")
            return False
        except FileNotFoundError:
            print("[ERROR] pytest not found. Install: pip install -r requirements.txt")
            return False
        except Exception as e:
            print(f"[ERROR] Error running contract tests: {e}")
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        print("\n[INTEGRATION] Running Integration Tests...")
        
        cmd = [
            'pytest',
            'integration-tests/',
            '-m', 'integration',
            '--tb=short',
            '-v'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("[SUCCESS] Integration tests passed!")
                return True
            else:
                print("[FAILED] Integration tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Integration tests timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error running integration tests: {e}")
            return False
    
    def run_load_tests(self, users: int = 10, duration: str = "30s") -> bool:
        """Run load tests with Locust"""
        print(f"\n[LOAD] Running Load Tests ({users} users, {duration})...")
        
        # Generate timestamp for unique report name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"load_test_report_{timestamp}.html"
        
        cmd = [
            'locust',
            '-f', 'load-tests/locustfile.py',
            '--headless',
            '--users', str(users),
            '--spawn-rate', '2',
            '--run-time', duration,
            '--html', f'reports/{report_name}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0:
                print("[SUCCESS] Load tests completed!")
                return True
            else:
                print("[FAILED] Load tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Load tests timed out")
            return False
        except FileNotFoundError:
            print("[ERROR] locust not found. Install: pip install locust")
            return False
        except Exception as e:
            print(f"[ERROR] Error running load tests: {e}")
            return False
    
    def run_chaos_tests(self) -> bool:
        """Run chaos engineering tests"""
        print("\n[CHAOS] Running Chaos Tests...")
        
        cmd = [
            'pytest',
            'chaos-tests/',
            '-m', 'chaos',
            '--tb=short',
            '-v',
            '-s'  # Don't capture output for chaos tests
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] Chaos tests passed!")
            return True
        else:
            print("[FAILED] Chaos tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
    
    def run_security_tests(self) -> bool:
        """Run security tests"""
        print("\n[SECURITY] Running Security Tests...")
        
        cmd = [
            'pytest',
            'security-tests/',
            '-m', 'security',
            '--tb=short',
            '-v'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("[SUCCESS] Security tests passed!")
                return True
            else:
                print("[FAILED] Security tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False
        except Exception as e:
            print(f"[ERROR] Error running security tests: {e}")
            return False
    
    def run_api_tests(self) -> bool:
        """Run API tests"""
        print("\n[API] Running API Tests...")
        
        cmd = [
            'pytest',
            'api-tests/',
            '-m', 'api',
            '--tb=short',
            '-v'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("[SUCCESS] API tests passed!")
                return True
            else:
                print("[FAILED] API tests failed!")
                print(result.stdout)
                print(result.stderr)
                return False
        except Exception as e:
            print(f"[ERROR] Error running API tests: {e}")
            return False
    
    def run_performance_tests(self) -> bool:
        """Run performance tests with report generation"""
        print("\n[PERFORMANCE] Running Performance Tests...")
        
        try:
            # Run performance test runner with report generation
            result = subprocess.run([
                sys.executable, "utils/run_performance_tests.py"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("[SUCCESS] Performance tests passed!")
                print(result.stdout)
                return True
            else:
                print("[FAILED] Performance tests failed!")
                print(result.stdout)
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Performance tests timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error running performance tests: {e}")
            return False
    
    def run_all_tests(self, skip_load: bool = False, skip_chaos: bool = False) -> bool:
        """Run all test suites"""
        print("[SUITE] Starting Enhanced Microservices Testing Suite")
        print("=" * 60)
        
        # Wait for services
        if not self.wait_for_services():
            return False
        
        results = []
        
        # Core tests
        results.append(self.run_contract_tests())
        results.append(self.run_integration_tests())
        
        # Extended tests
        results.append(self.run_security_tests())
        results.append(self.run_api_tests())
        results.append(self.run_performance_tests())
        
        # Load tests (optional)
        if not skip_load:
            results.append(self.run_load_tests())
        
        # Chaos tests (optional)
        if not skip_chaos:
            results.append(self.run_chaos_tests())
        
        # Summary
        print("\n" + "=" * 60)
        print("[SUMMARY] Enhanced Test Results Summary:")
        
        test_types = ['Contract', 'Integration', 'Security', 'API', 'Performance']
        if not skip_load:
            test_types.append('Load')
        if not skip_chaos:
            test_types.append('Chaos')
        
        for i, (test_type, passed) in enumerate(zip(test_types, results)):
            status = "[PASSED]" if passed else "[FAILED]"
            print(f"  {test_type} Tests: {status}")
        
        all_passed = all(results)
        overall_status = "[ALL PASSED]" if all_passed else "[SOME FAILED]"
        print(f"\nOverall: {overall_status}")
        
        return all_passed

def main():
    try:
        parser = argparse.ArgumentParser(description='Microservices Testing Suite')
        parser.add_argument('--test-type', choices=['all', 'contract', 'integration', 'security', 'api', 'performance', 'load', 'chaos'], 
                           default='all', help='Type of tests to run')
        parser.add_argument('--skip-load', action='store_true', help='Skip load tests')
        parser.add_argument('--skip-chaos', action='store_true', help='Skip chaos tests')
        parser.add_argument('--load-users', type=int, default=10, help='Number of users for load tests')
        parser.add_argument('--load-duration', default='30s', help='Duration for load tests')
        parser.add_argument('--skip-payment', action='store_true', help='Skip payment service')
        
        args = parser.parse_args()
        
        runner = TestRunner(skip_payment=args.skip_payment)
        
        if args.test_type == 'all':
            success = runner.run_all_tests(skip_load=args.skip_load, skip_chaos=args.skip_chaos)
        elif args.test_type == 'contract':
            success = runner.run_contract_tests()
        elif args.test_type == 'integration':
            success = runner.run_integration_tests()
        elif args.test_type == 'load':
            success = runner.run_load_tests(args.load_users, args.load_duration)
        elif args.test_type == 'security':
            success = runner.run_security_tests()
        elif args.test_type == 'api':
            success = runner.run_api_tests()
        elif args.test_type == 'performance':
            success = runner.run_performance_tests()
        elif args.test_type == 'chaos':
            success = runner.run_chaos_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"[FATAL] Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()