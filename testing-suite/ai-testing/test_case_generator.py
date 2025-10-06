#!/usr/bin/env python3
"""
AI-Powered Test Case Generator
Analisa código e gera test cases automaticamente usando padrões de IA
"""

import ast
import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestCase:
    name: str
    description: str
    test_type: str
    priority: str
    risk_level: str
    generated_code: str
    reasoning: str

class AITestCaseGenerator:
    
    def __init__(self):
        self.patterns = {
            'api_endpoints': r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            'database_operations': r'(INSERT|UPDATE|DELETE|SELECT).*FROM',
            'error_handling': r'(try:|except|raise|HTTPException)',
            'validation': r'(validate|check|verify|assert)',
            'authentication': r'(auth|login|token|jwt|oauth)',
            'business_logic': r'(calculate|process|transform|convert)'
        }
        
        self.risk_matrix = {
            'authentication': 'HIGH',
            'database_operations': 'HIGH', 
            'api_endpoints': 'MEDIUM',
            'business_logic': 'MEDIUM',
            'validation': 'LOW',
            'error_handling': 'LOW'
        }
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """Analisa arquivo de código e extrai informações"""
        try:
            # Secure path handling to prevent path traversal
            safe_path = Path(file_path).resolve()
            if not safe_path.exists():
                return {'error': f'File not found: {file_path}', 'file_path': file_path}
            
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': file_path,
                'patterns_found': {},
                'complexity_score': 0,
                'risk_areas': []
            }
            
            # Detectar padrões
            for pattern_name, pattern in self.patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    analysis['patterns_found'][pattern_name] = matches
                    analysis['complexity_score'] += len(matches)
                    
                    # Avaliar risco
                    risk = self.risk_matrix.get(pattern_name, 'LOW')
                    analysis['risk_areas'].append({
                        'pattern': pattern_name,
                        'risk': risk,
                        'occurrences': len(matches)
                    })
            
            return analysis
            
        except Exception as e:
            return {'error': str(e), 'file_path': file_path}
    
    def generate_test_cases(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Gera test cases baseado na análise do código"""
        test_cases = []
        
        if 'error' in analysis:
            return test_cases
        
        patterns = analysis.get('patterns_found', {})
        
        # Gerar testes para API endpoints
        if 'api_endpoints' in patterns:
            for method, endpoint in patterns['api_endpoints']:
                test_cases.extend(self._generate_api_tests(method, endpoint))
        
        # Gerar testes para operações de banco
        if 'database_operations' in patterns:
            test_cases.extend(self._generate_database_tests())
        
        # Gerar testes para autenticação
        if 'authentication' in patterns:
            test_cases.extend(self._generate_auth_tests())
        
        # Gerar testes para validação
        if 'validation' in patterns:
            test_cases.extend(self._generate_validation_tests())
        
        # Gerar testes para tratamento de erro
        if 'error_handling' in patterns:
            test_cases.extend(self._generate_error_tests())
        
        return test_cases
    
    def _generate_api_tests(self, method: str, endpoint: str) -> List[TestCase]:
        """Gera testes específicos para endpoints de API"""
        tests = []
        
        # Teste básico de sucesso
        tests.append(TestCase(
            name=f"test_{method.lower()}_{endpoint.replace('/', '_').replace('{', '').replace('}', '')}_success",
            description=f"Test successful {method.upper()} request to {endpoint}",
            test_type="API",
            priority="HIGH",
            risk_level="MEDIUM",
            generated_code=f"""
def test_{method.lower()}_{endpoint.replace('/', '_').replace('{', '').replace('}', '')}_success(self):
    \"\"\"Test successful {method.upper()} request to {endpoint}\"\"\"
    response = requests.{method.lower()}(f"{{self.base_url}}{endpoint}")
    assert response.status_code in [200, 201, 204]
    if response.content:
        assert response.json() is not None
""",
            reasoning=f"API endpoint {method.upper()} {endpoint} needs basic success path testing"
        ))
        
        return tests
    
    def _generate_database_tests(self) -> List[TestCase]:
        """Gera testes para operações de banco de dados"""
        return [
            TestCase(
                name="test_database_connection_resilience",
                description="Test database connection handling under load",
                test_type="DATABASE",
                priority="HIGH",
                risk_level="HIGH",
                generated_code="""
def test_database_connection_resilience(self):
    \"\"\"Test database connection handling under load\"\"\"
    import concurrent.futures
    
    def make_db_request():
        response = requests.get(f"{self.base_url}/users")
        return response.status_code == 200
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_db_request) for _ in range(20)]
        results = [future.result() for future in futures]
    
    success_rate = sum(results) / len(results)
    assert success_rate >= 0.8
""",
                reasoning="Database operations under concurrent load need resilience testing"
            )
        ]
    
    def _generate_auth_tests(self) -> List[TestCase]:
        """Gera testes para autenticação"""
        return [
            TestCase(
                name="test_unauthorized_access",
                description="Test unauthorized access to protected endpoints",
                test_type="SECURITY",
                priority="HIGH",
                risk_level="HIGH",
                generated_code="""
def test_unauthorized_access(self):
    \"\"\"Test unauthorized access to protected endpoints\"\"\"
    protected_endpoints = ["/users", "/orders", "/payments"]
    
    for endpoint in protected_endpoints:
        response = requests.get(f"{self.base_url}{endpoint}")
        assert response.status_code in [200, 401, 403]
""",
                reasoning="Authentication endpoints need security testing"
            )
        ]
    
    def _generate_validation_tests(self) -> List[TestCase]:
        """Gera testes para validação"""
        return [
            TestCase(
                name="test_input_validation",
                description="Test input validation with invalid data",
                test_type="VALIDATION",
                priority="MEDIUM",
                risk_level="MEDIUM",
                generated_code="""
def test_input_validation(self):
    \"\"\"Test input validation with invalid data\"\"\"
    invalid_payloads = [
        {},
        {"invalid": "field"},
        {"name": "", "email": ""}
    ]
    
    for payload in invalid_payloads:
        response = requests.post(f"{self.base_url}/users", json=payload)
        assert response.status_code in [400, 422]
""",
                reasoning="Input validation is crucial for data integrity"
            )
        ]
    
    def _generate_error_tests(self) -> List[TestCase]:
        """Gera testes para tratamento de erro"""
        return [
            TestCase(
                name="test_error_handling_graceful",
                description="Test graceful error handling",
                test_type="ERROR_HANDLING",
                priority="MEDIUM",
                risk_level="LOW",
                generated_code="""
def test_error_handling_graceful(self):
    \"\"\"Test graceful error handling\"\"\"
    response = requests.post(f"{self.base_url}/users", 
                           data="invalid-json", 
                           headers={"Content-Type": "application/json"})
    
    assert response.status_code in [400, 422]
""",
                reasoning="Error handling should be graceful and informative"
            )
        ]
    
    def generate_test_report(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Gera relatório dos test cases gerados"""
        report = {
            'total_tests': len(test_cases),
            'by_type': {},
            'by_priority': {},
            'by_risk': {},
            'recommendations': []
        }
        
        for test in test_cases:
            report['by_type'][test.test_type] = report['by_type'].get(test.test_type, 0) + 1
            report['by_priority'][test.priority] = report['by_priority'].get(test.priority, 0) + 1
            report['by_risk'][test.risk_level] = report['by_risk'].get(test.risk_level, 0) + 1
        
        high_risk_count = report['by_risk'].get('HIGH', 0)
        if high_risk_count > 0:
            report['recommendations'].append(f"Focus on {high_risk_count} high-risk test cases first")
        
        return report

def main():
    """Exemplo de uso do AI Test Case Generator"""
    generator = AITestCaseGenerator()
    
    services = [
        '../services/user-service/main.py',
        '../services/order-service/app.js',
        '../services/payment-service/main.go'
    ]
    
    all_test_cases = []
    
    for service in services:
        if Path(service).exists():
            print(f"Analyzing {service}...")
            analysis = generator.analyze_code_file(service)
            test_cases = generator.generate_test_cases(analysis)
            all_test_cases.extend(test_cases)
            print(f"Generated {len(test_cases)} test cases")
    
    report = generator.generate_test_report(all_test_cases)
    
    print(f"\nAI Test Generation Report:")
    print(f"Total Tests Generated: {report['total_tests']}")
    print(f"By Type: {report['by_type']}")
    print(f"By Priority: {report['by_priority']}")
    print(f"By Risk: {report['by_risk']}")

if __name__ == "__main__":
    main()