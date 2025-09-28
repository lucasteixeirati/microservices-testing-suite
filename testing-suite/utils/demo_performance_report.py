#!/usr/bin/env python3
"""
Demo Performance Report Generator
Generates sample performance reports to demonstrate functionality
"""

import sys
import os
from datetime import datetime
from performance_report_generator import PerformanceReportGenerator

def generate_demo_performance_data():
    """Generate demo performance data"""
    return [
        {
            'test_name': 'user_service_response_time',
            'metrics': {
                'iterations': 50,
                'avg_response_time': 67.5,
                'p95_response_time': 125.3,
                'min_response_time': 23.1,
                'max_response_time': 189.7
            }
        },
        {
            'test_name': 'concurrent_user_creation',
            'metrics': {
                'concurrent_users': 10,
                'total_requests': 50,
                'success_rate': 0.98,
                'avg_response_time': 234.6
            }
        },
        {
            'test_name': 'order_service_throughput',
            'metrics': {
                'duration': 10,
                'total_requests': 58,
                'throughput_rps': 5.8,
                'avg_response_time': 198.4
            }
        },
        {
            'test_name': 'payment_processing_latency',
            'metrics': {
                'iterations': 20,
                'avg_creation_time': 78.2,
                'avg_processing_time': 102.5
            }
        },
        {
            'test_name': 'memory_usage_simulation',
            'metrics': {
                'initial_memory_mb': 65.4,
                'peak_memory_mb': 98.7,
                'memory_increase_mb': 33.3,
                'memory_cleanup_mb': 28.9
            }
        }
    ]

def main():
    """Generate demo performance report"""
    print("[DEMO] Generating Demo Performance Report...")
    
    # Create performance report generator
    report_generator = PerformanceReportGenerator()
    
    # Add demo test results
    demo_data = generate_demo_performance_data()
    
    for test_data in demo_data:
        report_generator.add_test_result(
            test_data['test_name'],
            test_data['metrics']
        )
    
    # Generate reports
    html_report = report_generator.generate_html_report()
    json_report = report_generator.generate_json_report()
    
    print(f"[SUCCESS] Demo reports generated:")
    print(f"  HTML: {html_report}")
    print(f"  JSON: {json_report}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())