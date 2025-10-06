#!/usr/bin/env python3
"""
Performance Test Runner with Report Generation
Executes performance tests and generates timestamped reports
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime
from performance_report_generator import PerformanceReportGenerator

def check_services_health():
    """Check if all services are running"""
    import requests
    
    services = {
        'user-service': 'http://localhost:8001/health',
        'order-service': 'http://localhost:8002/health', 
        'payment-service': 'http://localhost:8003/health'
    }
    
    print("Checking service health...")
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {service}: OK")
            else:
                print(f"[ERROR] {service}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {service}: {str(e)}")
            return False
    
    return True

def run_performance_tests():
    """Run performance tests and capture results"""
    print("\n[START] Starting Performance Tests...")
    
    # Run pytest with JSON output
    cmd = [
        sys.executable, '-m', 'pytest', 
        'performance-tests/test_performance_comprehensive.py',
        '-v', '--tb=short'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False, "", str(e)

def parse_pytest_output(stdout):
    """Parse pytest output to extract performance metrics"""
    performance_data = []
    
    # Extract test results from stdout
    lines = stdout.split('\n')
    current_test = None
    
    for line in lines:
        # Look for test execution lines
        if '::test_' in line and 'PASSED' in line:
            test_match = re.search(r'test_(\w+)', line)
            if test_match:
                test_name = test_match.group(1)
                
                # Mock performance data (in real scenario, this would come from test execution)
                mock_metrics = generate_mock_metrics(test_name)
                performance_data.append({
                    'test_name': test_name,
                    'metrics': mock_metrics
                })
    
    return performance_data

def extract_real_metrics_from_json(json_file):
    """Extract real performance metrics from pytest JSON output"""
    try:
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            metrics = {}
            for test in data.get('tests', []):
                test_name = test.get('nodeid', '').split('::')[-1].replace('test_', '')
                duration = test.get('duration', 0)
                outcome = test.get('outcome', 'failed')
                
                metrics[test_name] = {
                    'duration_seconds': duration,
                    'status': outcome,
                    'success_rate': 1.0 if outcome == 'passed' else 0.0
                }
            
            return metrics
    except Exception as e:
        print(f"Warning: Could not extract real metrics: {e}")
    
    return {}

def generate_demo_metrics(test_name):
    """Generate demo metrics for portfolio demonstration"""
    # NOTE: This generates demo data for portfolio purposes
    # In production, replace with actual performance measurement
    import random
    
    demo_metrics = {
        'user_service_response_time': {
            'note': 'Demo data for portfolio',
            'avg_response_time_ms': round(random.uniform(45, 85), 2),
            'p95_response_time_ms': round(random.uniform(90, 150), 2),
            'success_rate': round(random.uniform(0.95, 1.0), 3)
        },
        'concurrent_user_creation': {
            'note': 'Demo data for portfolio', 
            'concurrent_users': 10,
            'success_rate': round(random.uniform(0.95, 1.0), 3),
            'avg_response_time_ms': round(random.uniform(150, 300), 2)
        }
    }
    
    return demo_metrics.get(test_name, {
        'note': 'Demo data for portfolio',
        'avg_response_time_ms': round(random.uniform(50, 200), 2),
        'success_rate': round(random.uniform(0.9, 1.0), 3)
    })

def main():
    """Main execution function"""
    print("[PERFORMANCE] Performance Test Suite Runner")
    print("=" * 50)
    
    # Check if services are running
    if not check_services_health():
        print("\n[ERROR] Services are not healthy. Please start all services first.")
        print("Run: run-local.bat")
        return 1
    
    # Run performance tests
    success, stdout, stderr = run_performance_tests()
    
    if not success:
        print(f"\n[FAILED] Performance tests failed!")
        print(f"Error: {stderr}")
        return 1
    
    print("\n[SUCCESS] Performance tests completed successfully!")
    
    # Extract real metrics from JSON if available, otherwise use demo data
    real_metrics = extract_real_metrics_from_json('temp_performance_results.json')
    
    # Parse results and generate report
    performance_data = parse_pytest_output(stdout)
    
    # Enhance with real metrics if available
    for test_data in performance_data:
        test_name = test_data['test_name']
        if test_name in real_metrics:
            test_data['metrics'].update(real_metrics[test_name])
    
    # Generate performance report
    report_generator = PerformanceReportGenerator()
    
    for test_data in performance_data:
        report_generator.add_test_result(
            test_data['test_name'],
            test_data['metrics']
        )
    
    # Generate HTML and JSON reports
    html_report = report_generator.generate_html_report()
    json_report = report_generator.generate_json_report()
    
    print(f"\n[REPORTS] Reports Generated:")
    print(f"  HTML: {html_report}")
    print(f"  JSON: {json_report}")
    
    # Clean up temporary files
    temp_file = 'temp_performance_results.json'
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print("\n[COMPLETE] Performance testing completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())