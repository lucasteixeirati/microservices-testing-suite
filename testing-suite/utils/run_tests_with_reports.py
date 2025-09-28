#!/usr/bin/env python3
"""
Enhanced Test Runner with Timestamped Reports
Generates historical reports for all test types
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def run_pytest_with_timestamp(test_dir: str, test_type: str, additional_args: list = None) -> bool:
    """Run pytest with timestamped HTML report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"{test_type}_report_{timestamp}.html"
    coverage_dir = f"coverage_{test_type}_{timestamp}"
    
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    cmd = [
        'pytest',
        test_dir,
        '--html', f'reports/{report_name}',
        '--self-contained-html',
        '--cov=../services',
        f'--cov-report=html:reports/{coverage_dir}',
        '--cov-report=term-missing',
        '--tb=short',
        '-v'
    ]
    
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"[{test_type.upper()}] Running tests with timestamped report...")
    print(f"[REPORT] Will generate: reports/{report_name}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {test_type} tests completed!")
            print(f"[REPORT] Generated: reports/{report_name}")
            print(f"[COVERAGE] Generated: reports/{coverage_dir}/")
            return True
        else:
            print(f"[FAILED] {test_type} tests failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {test_type} tests timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Error running {test_type} tests: {e}")
        return False

def run_all_tests_with_reports() -> bool:
    """Run all test suites with timestamped reports"""
    print("🧪 Starting Enhanced Testing Suite with Historical Reports")
    print("=" * 60)
    
    results = []
    
    # Contract Tests
    results.append(run_pytest_with_timestamp(
        "contract-tests/", 
        "contract", 
        ['-m', 'contract']
    ))
    
    # Integration Tests  
    results.append(run_pytest_with_timestamp(
        "integration-tests/", 
        "integration",
        ['-m', 'integration']
    ))
    
    # Unit Tests
    results.append(run_pytest_with_timestamp(
        "unit-tests/", 
        "unit"
    ))
    
    # Chaos Tests
    results.append(run_pytest_with_timestamp(
        "chaos-tests/", 
        "chaos",
        ['-m', 'chaos', '-s']
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HISTORICAL REPORTS SUMMARY:")
    
    test_types = ['Contract', 'Integration', 'Unit', 'Chaos']
    for test_type, passed in zip(test_types, results):
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_type} Tests: {status}")
    
    all_passed = all(results)
    overall_status = "🎉 ALL PASSED" if all_passed else "⚠️ SOME FAILED"
    print(f"\nOverall: {overall_status}")
    
    # List generated reports
    print(f"\n📁 Reports saved in: {Path('reports').absolute()}")
    
    return all_passed

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "contract":
            success = run_pytest_with_timestamp("contract-tests/", "contract", ['-m', 'contract'])
        elif test_type == "integration":
            success = run_pytest_with_timestamp("integration-tests/", "integration", ['-m', 'integration'])
        elif test_type == "unit":
            success = run_pytest_with_timestamp("unit-tests/", "unit")
        elif test_type == "chaos":
            success = run_pytest_with_timestamp("chaos-tests/", "chaos", ['-m', 'chaos', '-s'])
        elif test_type == "all":
            success = run_all_tests_with_reports()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available: contract, integration, unit, chaos, all")
            sys.exit(1)
    else:
        success = run_all_tests_with_reports()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()