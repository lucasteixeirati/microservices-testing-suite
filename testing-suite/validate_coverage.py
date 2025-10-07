#!/usr/bin/env python3
"""
Validador de Cobertura de Testes - AI-Powered Microservices Testing Suite
Executa validação completa da cobertura de testes e gera relatório detalhado.
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class TestCoverageValidator:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'details': {},
            'recommendations': []
        }
        
    def run_command(self, command, description):
        """Executa comando e captura resultado"""
        print(f"\n[RUN] {description}...")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutos timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out after 5 minutes',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def validate_unit_tests(self):
        """Valida testes unitários com cobertura"""
        result = self.run_command(
            'pytest unit-tests/ --cov=../services --cov-report=term --cov-report=json -v',
            'Validando Testes Unitários com Cobertura'
        )
        
        coverage_data = {}
        try:
            if Path('coverage.json').exists():
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
        except:
            pass
            
        self.results['details']['unit_tests'] = {
            'success': result['success'],
            'coverage_data': coverage_data,
            'output': result['stdout'][:1000]  # Limitar output
        }
        
        return result['success']
    
    def validate_contract_tests(self):
        """Valida testes de contrato"""
        result = self.run_command(
            'pytest contract-tests/ -v',
            'Validando Testes de Contrato'
        )
        
        self.results['details']['contract_tests'] = {
            'success': result['success'],
            'output': result['stdout'][:1000]
        }
        
        return result['success']
    
    def validate_integration_tests(self):
        """Valida testes de integração"""
        result = self.run_command(
            'pytest integration-tests/ -v --tb=short',
            'Validando Testes de Integração'
        )
        
        self.results['details']['integration_tests'] = {
            'success': result['success'],
            'output': result['stdout'][:1000]
        }
        
        return result['success']
    
    def validate_api_tests(self):
        """Valida testes de API"""
        result = self.run_command(
            'pytest api-tests/ -v',
            'Validando Testes de API'
        )
        
        self.results['details']['api_tests'] = {
            'success': result['success'],
            'output': result['stdout'][:1000]
        }
        
        return result['success']
    
    def validate_ml_components(self):
        """Valida componentes de IA/ML"""
        ml_tests = [
            ('python ai-testing/simple_ml_demo.py', 'Simple ML Demo'),
            ('python ai-testing/test_case_generator.py', 'AI Test Generator'),
            ('python ai-testing/bug_pattern_analyzer.py', 'Bug Pattern Analyzer'),
            ('python ai-testing/smart_test_prioritizer.py', 'Smart Test Prioritizer'),
            ('python ai-testing/advanced_ml_engine.py', 'Advanced ML Engine')
        ]
        
        ml_results = {}
        for command, name in ml_tests:
            result = self.run_command(command, f'Validando {name}')
            ml_results[name] = {
                'success': result['success'],
                'output': result['stdout'][:500]
            }
        
        self.results['details']['ml_components'] = ml_results
        
        # Retorna True se pelo menos 80% dos componentes ML funcionam
        success_count = sum(1 for r in ml_results.values() if r['success'])
        return success_count >= len(ml_tests) * 0.8
    
    def check_services_health(self):
        """Verifica saúde dos serviços"""
        import requests
        
        services = [
            ('http://localhost:8001/health', 'User Service'),
            ('http://localhost:8002/health', 'Order Service'),
            ('http://localhost:8003/health', 'Payment Service')
        ]
        
        health_results = {}
        for url, name in services:
            try:
                response = requests.get(url, timeout=5)
                health_results[name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                health_results[name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
        
        self.results['details']['services_health'] = health_results
        
        # Retorna True se todos os serviços estão saudáveis
        return all(r.get('status') == 'healthy' for r in health_results.values())
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de cobertura
        if 'unit_tests' in self.results['details']:
            coverage_data = self.results['details']['unit_tests'].get('coverage_data', {})
            if coverage_data:
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                if total_coverage < 80:
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'COVERAGE',
                        'title': f'Cobertura de código baixa: {total_coverage:.1f}%',
                        'action': 'Adicionar mais testes unitários para atingir 80%+'
                    })
                elif total_coverage < 90:
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': 'COVERAGE',
                        'title': f'Cobertura de código boa: {total_coverage:.1f}%',
                        'action': 'Considerar aumentar para 90%+ para excelência'
                    })
        
        # Análise de testes falhando
        failed_categories = []
        for category, details in self.results['details'].items():
            if isinstance(details, dict) and not details.get('success', True):
                failed_categories.append(category)
        
        if failed_categories:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'FAILURES',
                'title': f'Categorias com falhas: {", ".join(failed_categories)}',
                'action': 'Investigar e corrigir testes falhando'
            })
        
        # Análise de serviços
        services_health = self.results['details'].get('services_health', {})
        unhealthy_services = [name for name, health in services_health.items() 
                            if health.get('status') != 'healthy']
        
        if unhealthy_services:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'SERVICES',
                'title': f'Serviços não saudáveis: {", ".join(unhealthy_services)}',
                'action': 'Verificar e reiniciar serviços antes de executar testes'
            })
        
        self.results['recommendations'] = recommendations
    
    def generate_summary(self):
        """Gera resumo dos resultados"""
        summary = {
            'total_categories': len(self.results['details']),
            'successful_categories': 0,
            'failed_categories': 0,
            'overall_status': 'UNKNOWN'
        }
        
        for category, details in self.results['details'].items():
            if isinstance(details, dict):
                if details.get('success', False):
                    summary['successful_categories'] += 1
                else:
                    summary['failed_categories'] += 1
            elif isinstance(details, dict) and 'ml_components' in category:
                # Análise especial para componentes ML
                ml_success = sum(1 for comp in details.values() if comp.get('success', False))
                ml_total = len(details)
                if ml_success >= ml_total * 0.8:
                    summary['successful_categories'] += 1
                else:
                    summary['failed_categories'] += 1
        
        # Determinar status geral
        success_rate = summary['successful_categories'] / summary['total_categories'] if summary['total_categories'] > 0 else 0
        
        if success_rate >= 0.9:
            summary['overall_status'] = 'EXCELLENT'
        elif success_rate >= 0.7:
            summary['overall_status'] = 'GOOD'
        elif success_rate >= 0.5:
            summary['overall_status'] = 'FAIR'
        else:
            summary['overall_status'] = 'POOR'
        
        summary['success_rate'] = f"{success_rate:.1%}"
        
        self.results['summary'] = summary
    
    def save_results(self):
        """Salva resultados em arquivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/coverage_validation_{timestamp}.json"
        
        Path("reports").mkdir(exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVE] Resultados salvos em: {filename}")
        return filename
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print("[SUMMARY] RESUMO DA VALIDACAO DE COBERTURA")
        print("="*60)
        
        summary = self.results['summary']
        print(f"Status Geral: {summary['overall_status']}")
        print(f"Taxa de Sucesso: {summary['success_rate']}")
        print(f"Categorias Testadas: {summary['total_categories']}")
        print(f"Sucessos: {summary['successful_categories']}")
        print(f"Falhas: {summary['failed_categories']}")
        
        print("\n[DETAILS] DETALHES POR CATEGORIA:")
        for category, details in self.results['details'].items():
            if isinstance(details, dict):
                status = "[PASS]" if details.get('success', False) else "[FAIL]"
                print(f"  {category}: {status}")
        
        print("\n[RECOMMENDATIONS] RECOMENDACOES:")
        for i, rec in enumerate(self.results['recommendations'], 1):
            priority_icon = {"CRITICAL": "[CRIT]", "HIGH": "[HIGH]", "MEDIUM": "[MED]", "LOW": "[LOW]"}.get(rec['priority'], "[INFO]")
            print(f"  {i}. {priority_icon} [{rec['priority']}] {rec['title']}")
            print(f"     Acao: {rec['action']}")
    
    def run_full_validation(self):
        """Executa validação completa"""
        print("[INICIO] Iniciando Validacao Completa de Cobertura de Testes")
        print("="*60)
        
        start_time = time.time()
        
        # Verificar saude dos servicos primeiro
        print("\n[HEALTH] Verificando saude dos servicos...")
        services_healthy = self.check_services_health()
        
        if not services_healthy:
            print("[WARNING] Alguns servicos nao estao saudaveis. Continuando com validacao...")
        
        # Executar validações
        validations = [
            ('unit_tests', self.validate_unit_tests),
            ('contract_tests', self.validate_contract_tests),
            ('integration_tests', self.validate_integration_tests),
            ('api_tests', self.validate_api_tests),
            ('ml_components', self.validate_ml_components)
        ]
        
        for name, validation_func in validations:
            try:
                validation_func()
            except Exception as e:
                print(f"[ERROR] Erro na validacao {name}: {str(e)}")
                self.results['details'][name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Gerar análises
        self.generate_recommendations()
        self.generate_summary()
        
        # Salvar e exibir resultados
        filename = self.save_results()
        self.print_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n[TIME] Validacao concluida em {duration:.1f} segundos")
        print(f"[REPORT] Relatorio detalhado: {filename}")
        
        return self.results

def main():
    """Função principal"""
    validator = TestCoverageValidator()
    results = validator.run_full_validation()
    
    # Retornar código de saída baseado no status
    if results['summary']['overall_status'] in ['EXCELLENT', 'GOOD']:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()