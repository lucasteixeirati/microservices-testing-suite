#!/usr/bin/env python3
"""
AI Testing Dashboard
Interface web para visualizar insights de IA sobre testes
"""

from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime
from test_case_generator import AITestCaseGenerator
from bug_pattern_analyzer import BugPatternAnalyzer
from smart_test_prioritizer import SmartTestPrioritizer, TestCase

app = Flask(__name__)

# Instâncias globais dos componentes de IA
test_generator = AITestCaseGenerator()
bug_analyzer = BugPatternAnalyzer()
test_prioritizer = SmartTestPrioritizer()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Testing Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #f8f9fa; }
        .ai-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .metric-card { transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-5px); }
        .ai-insight { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 10px 0; }
        .priority-high { border-left-color: #f44336; }
        .priority-medium { border-left-color: #ff9800; }
        .priority-low { border-left-color: #4caf50; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🤖 AI Testing Dashboard</span>
            <span class="badge bg-success">LIVE</span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- AI Overview -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="ai-card p-4 rounded">
                    <h2>🧠 AI Testing Intelligence</h2>
                    <p>Automated test generation, bug pattern analysis, and smart prioritization</p>
                    <div class="row">
                        <div class="col-md-3">
                            <h4 id="generatedTests">0</h4>
                            <small>Tests Generated</small>
                        </div>
                        <div class="col-md-3">
                            <h4 id="bugsDetected">0</h4>
                            <small>Bug Patterns Detected</small>
                        </div>
                        <div class="col-md-3">
                            <h4 id="prioritizedTests">0</h4>
                            <small>Tests Prioritized</small>
                        </div>
                        <div class="col-md-3">
                            <h4 id="aiAccuracy">95%</h4>
                            <small>AI Accuracy</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- AI Components -->
        <div class="row">
            <div class="col-md-4">
                <div class="card metric-card">
                    <div class="card-header bg-primary text-white">
                        <h5>🔧 Test Case Generator</h5>
                    </div>
                    <div class="card-body">
                        <p>AI analyzes code and generates test cases automatically</p>
                        <button class="btn btn-primary" onclick="generateTests()">Generate Tests</button>
                        <div id="generatedTestsResult" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card metric-card">
                    <div class="card-header bg-warning text-white">
                        <h5>🐛 Bug Pattern Analyzer</h5>
                    </div>
                    <div class="card-body">
                        <p>ML detects bug patterns in logs and code</p>
                        <button class="btn btn-warning" onclick="analyzeBugs()">Analyze Patterns</button>
                        <div id="bugAnalysisResult" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card metric-card">
                    <div class="card-header bg-success text-white">
                        <h5>🎯 Smart Prioritizer</h5>
                    </div>
                    <div class="card-body">
                        <p>AI prioritizes tests based on risk and impact</p>
                        <button class="btn btn-success" onclick="prioritizeTests()">Prioritize Tests</button>
                        <div id="prioritizationResult" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- AI Insights -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>🔍 AI Insights & Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <div id="aiInsights">
                            <div class="ai-insight">
                                <h6>💡 Smart Recommendation</h6>
                                <p>Based on code analysis, focus on API endpoint testing - 12 endpoints detected with medium risk level.</p>
                            </div>
                            <div class="ai-insight priority-high">
                                <h6>⚠️ High Priority Alert</h6>
                                <p>Authentication patterns show potential security vulnerabilities. Recommend immediate security test generation.</p>
                            </div>
                            <div class="ai-insight priority-medium">
                                <h6>📊 Pattern Detection</h6>
                                <p>Database connection timeouts detected in 15% of recent logs. Consider resilience testing.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Real-time Charts -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Test Generation Trends</div>
                    <div class="card-body">
                        <canvas id="testGenerationChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Bug Pattern Distribution</div>
                    <div class="card-body">
                        <canvas id="bugPatternChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Test Priority Matrix -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">🎯 Test Priority Matrix</div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Test Name</th>
                                        <th>Priority Score</th>
                                        <th>Risk Level</th>
                                        <th>Type</th>
                                        <th>Execution Time</th>
                                        <th>AI Reasoning</th>
                                    </tr>
                                </thead>
                                <tbody id="priorityMatrix">
                                    <tr>
                                        <td>test_user_authentication</td>
                                        <td><span class="badge bg-danger">0.95</span></td>
                                        <td><span class="badge bg-danger">CRITICAL</span></td>
                                        <td>SECURITY</td>
                                        <td>45s</td>
                                        <td>High failure rate, critical business impact</td>
                                    </tr>
                                    <tr>
                                        <td>test_payment_processing</td>
                                        <td><span class="badge bg-warning">0.78</span></td>
                                        <td><span class="badge bg-warning">HIGH</span></td>
                                        <td>API</td>
                                        <td>120s</td>
                                        <td>Critical business function, recent changes</td>
                                    </tr>
                                    <tr>
                                        <td>test_user_profile_update</td>
                                        <td><span class="badge bg-success">0.42</span></td>
                                        <td><span class="badge bg-success">MEDIUM</span></td>
                                        <td>UNIT</td>
                                        <td>15s</td>
                                        <td>Fast execution, medium impact</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize charts
        const ctx1 = document.getElementById('testGenerationChart').getContext('2d');
        new Chart(ctx1, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                datasets: [{
                    label: 'Tests Generated',
                    data: [12, 19, 15, 25, 22],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });

        const ctx2 = document.getElementById('bugPatternChart').getContext('2d');
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Connection Timeout', 'Null Pointer', 'Auth Failure', 'Validation Error'],
                datasets: [{
                    data: [30, 25, 20, 25],
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });

        // AI Functions
        function generateTests() {
            document.getElementById('generatedTestsResult').innerHTML = 
                '<div class="spinner-border spinner-border-sm" role="status"></div> Analyzing code...';
            
            fetch('/api/generate-tests', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('generatedTestsResult').innerHTML = 
                        `<div class="alert alert-success">Generated ${data.count} test cases</div>`;
                    document.getElementById('generatedTests').textContent = data.count;
                });
        }

        function analyzeBugs() {
            document.getElementById('bugAnalysisResult').innerHTML = 
                '<div class="spinner-border spinner-border-sm" role="status"></div> Analyzing patterns...';
            
            fetch('/api/analyze-bugs', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('bugAnalysisResult').innerHTML = 
                        `<div class="alert alert-warning">Found ${data.patterns} bug patterns</div>`;
                    document.getElementById('bugsDetected').textContent = data.patterns;
                });
        }

        function prioritizeTests() {
            document.getElementById('prioritizationResult').innerHTML = 
                '<div class="spinner-border spinner-border-sm" role="status"></div> Prioritizing...';
            
            fetch('/api/prioritize-tests', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('prioritizationResult').innerHTML = 
                        `<div class="alert alert-info">Prioritized ${data.count} tests</div>`;
                    document.getElementById('prioritizedTests').textContent = data.count;
                });
        }

        // Auto-refresh every 30 seconds
        setInterval(() => {
            console.log('Auto-refreshing AI metrics...');
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/generate-tests', methods=['POST'])
def api_generate_tests():
    """API para gerar test cases com IA"""
    try:
        # Simular geração de testes
        # Em implementação real, analisaria arquivos de código
        generated_count = 15
        
        return jsonify({
            'success': True,
            'count': generated_count,
            'message': f'Generated {generated_count} AI-powered test cases'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze-bugs', methods=['POST'])
def api_analyze_bugs():
    """API para análise de padrões de bugs"""
    try:
        # Simular análise de bugs
        patterns_found = 8
        
        return jsonify({
            'success': True,
            'patterns': patterns_found,
            'message': f'Detected {patterns_found} bug patterns'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/prioritize-tests', methods=['POST'])
def api_prioritize_tests():
    """API para priorização inteligente de testes"""
    try:
        # Simular priorização
        prioritized_count = 28
        
        return jsonify({
            'success': True,
            'count': prioritized_count,
            'message': f'Prioritized {prioritized_count} tests using AI'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/insights')
def api_insights():
    """API para obter insights de IA"""
    insights = [
        {
            'type': 'recommendation',
            'priority': 'high',
            'title': 'Security Test Gap Detected',
            'description': 'AI detected authentication endpoints without corresponding security tests',
            'action': 'Generate security test cases for /auth endpoints'
        },
        {
            'type': 'pattern',
            'priority': 'medium', 
            'title': 'Flaky Test Pattern',
            'description': 'ML identified 3 tests with intermittent failures',
            'action': 'Review and stabilize identified flaky tests'
        },
        {
            'type': 'optimization',
            'priority': 'low',
            'title': 'Test Execution Optimization',
            'description': 'AI suggests parallel execution could reduce test time by 40%',
            'action': 'Implement parallel test execution strategy'
        }
    ]
    
    return jsonify({'insights': insights})

def main():
    """Executar dashboard de IA"""
    print("🤖 Starting AI Testing Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🧠 AI components loaded and ready")
    
    app.run(debug=False, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    main()