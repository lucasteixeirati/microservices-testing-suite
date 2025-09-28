#!/usr/bin/env python3
"""
Report History Viewer
Lists and manages historical test reports
"""

import os
import glob
from datetime import datetime
from pathlib import Path

def list_reports():
    """List all historical reports"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("[ERROR] Reports directory not found!")
        return
    
    # Get all timestamped reports
    patterns = [
        "load_test_report_*.html",
        "contract_report_*.html", 
        "integration_report_*.html",
        "unit_report_*.html",
        "chaos_report_*.html",
        "test_suite_report_*.html"
    ]
    
    all_reports = []
    for pattern in patterns:
        reports = glob.glob(str(reports_dir / pattern))
        all_reports.extend(reports)
    
    if not all_reports:
        print("[INFO] No historical reports found yet.")
        print("[TIP] Run tests to generate reports with timestamps!")
        return
    
    # Sort by modification time (newest first)
    all_reports.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print("HISTORICAL TEST REPORTS")
    print("=" * 50)
    
    for report in all_reports:
        report_path = Path(report)
        filename = report_path.name
        
        # Extract test type and timestamp
        if "load_test" in filename:
            test_type = "[LOAD] Load Test"
        elif "contract" in filename:
            test_type = "[CONTRACT] Contract Test"
        elif "integration" in filename:
            test_type = "[INTEGRATION] Integration Test"
        elif "unit" in filename:
            test_type = "[UNIT] Unit Test"
        elif "chaos" in filename:
            test_type = "[CHAOS] Chaos Test"
        elif "test_suite" in filename:
            test_type = "[SUITE] Full Suite"
        else:
            test_type = "[REPORT] Report"
        
        # Get file info
        file_size = os.path.getsize(report) / 1024  # KB
        mod_time = datetime.fromtimestamp(os.path.getmtime(report))
        
        print(f"{test_type}")
        print(f"  File: {filename}")
        print(f"  Generated: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Size: {file_size:.1f} KB")
        print(f"  Path: {report_path.absolute()}")
        print()

def cleanup_old_reports(keep_last: int = 10):
    """Clean up old reports, keeping only the most recent ones"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        return
    
    # Get all timestamped reports
    patterns = [
        "load_test_report_*.html",
        "contract_report_*.html", 
        "integration_report_*.html",
        "unit_report_*.html",
        "chaos_report_*.html",
        "test_suite_report_*.html"
    ]
    
    for pattern in patterns:
        reports = glob.glob(str(reports_dir / pattern))
        
        if len(reports) > keep_last:
            # Sort by modification time (oldest first)
            reports.sort(key=lambda x: os.path.getmtime(x))
            
            # Remove oldest reports
            to_remove = reports[:-keep_last]
            
            print(f"[CLEANUP] Cleaning up {len(to_remove)} old {pattern} reports...")
            
            for report in to_remove:
                try:
                    os.remove(report)
                    print(f"  [REMOVED] {Path(report).name}")
                except Exception as e:
                    print(f"  [ERROR] Failed to remove {Path(report).name}: {e}")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_reports()
        elif command == "cleanup":
            keep = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            cleanup_old_reports(keep)
            print(f"[SUCCESS] Cleanup completed! Kept last {keep} reports of each type.")
        else:
            print("Usage:")
            print("  python report_history.py list")
            print("  python report_history.py cleanup [keep_count]")
    else:
        list_reports()

if __name__ == '__main__':
    main()