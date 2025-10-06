import json
import os
import html
from datetime import datetime
import statistics
from pathlib import Path

class PerformanceReportGenerator:
    
    def __init__(self):
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': [],
            'summary': {},
            'environment': {
                'python_version': '3.13.5',
                'platform': 'Windows-11',
                'test_framework': 'pytest'
            }
        }
    
    def add_test_result(self, test_name, metrics):
        """Add test result to the report"""
        self.report_data['test_results'].append({
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        })
    
    def calculate_summary(self):
        """Calculate summary statistics"""
        if not self.report_data['test_results']:
            return
        
        # Collect all response times
        all_response_times = []
        total_requests = 0
        failed_requests = 0
        
        for result in self.report_data['test_results']:
            metrics = result['metrics']
            
            if 'avg_response_time' in metrics:
                all_response_times.append(metrics['avg_response_time'])
            
            if 'total_requests' in metrics:
                total_requests += metrics['total_requests']
            
            if 'success_rate' in metrics and 'total_requests' in metrics:
                failed_requests += metrics['total_requests'] * (1 - metrics['success_rate'])
        
        self.report_data['summary'] = {
            'total_tests': len(self.report_data['test_results']),
            'total_requests': total_requests,
            'failed_requests': int(failed_requests),
            'overall_success_rate': (total_requests - failed_requests) / total_requests if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'test_duration': 'N/A'
        }
    
    def generate_html_report(self, output_dir='reports'):
        """Generate HTML performance report"""
        self.calculate_summary()
        
        # Secure path handling
        safe_output_dir = Path(output_dir).resolve()
        safe_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_report_{timestamp}.html'
        filepath = safe_output_dir / filename
        
        html_content = self._generate_html_content()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Performance report generated: {filepath}")
        return filepath
    
    def _generate_html_content(self):
        """Generate HTML content for the report"""
        summary = self.report_data['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Performance Test Report - {self.report_data['timestamp']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #333;
        }}
        .summary {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #2c5aa0;
        }}
        .test-result {{
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        .test-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 10px;
        }}
        .test-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Test Report</h1>
        <p><strong>Generated:</strong> {self.report_data['timestamp']}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="metric">
                <div class="metric-label">Total Tests:</div>
                <div class="metric-value">{summary.get('total_tests', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Requests:</div>
                <div class="metric-value">{summary.get('total_requests', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Success Rate:</div>
                <div class="metric-value {'success' if summary.get('overall_success_rate', 0) >= 0.95 else 'warning'}">{summary.get('overall_success_rate', 0):.1%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Response Time:</div>
                <div class="metric-value {'success' if summary.get('avg_response_time', 0) < 200 else 'warning'}">{summary.get('avg_response_time', 0):.2f}ms</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        {self._generate_test_results_html()}
        
        <h2>Performance Metrics Table</h2>
        {self._generate_metrics_table()}
        
        <div class="chart-container">
            <h3>Response Time Distribution</h3>
            <p><em>Chart visualization would be implemented with JavaScript charting library</em></p>
        </div>
        
        <h2>Environment Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Python Version</td><td>{self.report_data['environment']['python_version']}</td></tr>
            <tr><td>Platform</td><td>{self.report_data['environment']['platform']}</td></tr>
            <tr><td>Test Framework</td><td>{self.report_data['environment']['test_framework']}</td></tr>
        </table>
    </div>
</body>
</html>
        """
        return html
    
    def _generate_test_results_html(self):
        """Generate HTML for individual test results"""
        html = ""
        for result in self.report_data['test_results']:
            test_name = result['test_name']
            metrics = result['metrics']
            
            html += f"""
            <div class="test-result">
                <div class="test-name">{html.escape(str(test_name))}</div>
                <div class="test-metrics">
            """
            
            for key, value in metrics.items():
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                    if 'time' in key.lower():
                        formatted_value += "ms"
                    elif 'rate' in key.lower():
                        formatted_value = f"{value:.1%}"
                else:
                    formatted_value = str(value)
                
                html += f"""
                    <div class="metric">
                        <div class="metric-label">{html.escape(key.replace('_', ' ').title())}:</div>
                        <div class="metric-value">{html.escape(str(formatted_value))}</div>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        return html
    
    def _generate_metrics_table(self):
        """Generate metrics comparison table"""
        if not self.report_data['test_results']:
            return "<p>No test results available</p>"
        
        html = """
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Avg Response Time (ms)</th>
                    <th>Success Rate</th>
                    <th>Total Requests</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for result in self.report_data['test_results']:
            test_name = result['test_name']
            metrics = result['metrics']
            
            avg_time = metrics.get('avg_response_time', 0)
            success_rate = metrics.get('success_rate', 1.0)
            total_requests = metrics.get('total_requests', metrics.get('iterations', 'N/A'))
            
            # Determine status
            status = "PASS"
            status_class = "success"
            if avg_time > 500:
                status = "SLOW"
                status_class = "warning"
            if success_rate < 0.95:
                status = "FAIL"
                status_class = "danger"
            
            html += f"""
                <tr>
                    <td>{html.escape(str(test_name))}</td>
                    <td>{avg_time:.2f}</td>
                    <td>{success_rate:.1%}</td>
                    <td>{html.escape(str(total_requests))}</td>
                    <td class="{status_class}">{html.escape(status)}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        return html
    
    def generate_json_report(self, output_dir='reports'):
        """Generate JSON performance report"""
        self.calculate_summary()
        
        # Secure path handling
        safe_output_dir = Path(output_dir).resolve()
        safe_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_report_{timestamp}.json'
        filepath = safe_output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON performance report generated: {filepath}")
        return filepath