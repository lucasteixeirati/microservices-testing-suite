#!/usr/bin/env python3
"""
ML Integration Demo
Demonstra integração completa dos componentes ML aprimorados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_case_generator import AITestCaseGenerator
from bug_pattern_analyzer import BugPatternAnalyzer
from smart_test_prioritizer import SmartTestPrioritizer, TestCase, BusinessImpact
from advanced_ml_engine import AdvancedMLEngine, TestMetrics
from datetime import datetime, timedelta
import numpy as np
import json

class MLTestingSuite:
    """Suite integrada de ML para testing automation"""
    
    def __init__(self):
        self.test_generator = AITestCaseGenerator()
        self.bug_analyzer = BugPatternAnalyzer()
        self.test_prioritizer = SmartTestPrioritizer()
        self.ml_engine = AdvancedMLEngine()
        
        # Carregar modelos existentes
        self._load_all_models()
    
    def _load_all_models(self):
        """Carrega todos os modelos ML"""
        print("🔄 Loading ML models...")
        
        # Bug analyzer
        if self.bug_analyzer.load_model():
            print("✅ Bug pattern analyzer model loaded")
        else:
            print("⚠️ Bug analyzer: using traditional methods")
        
        # Test prioritizer
        if self.test_prioritizer.load_ml_model():
            print("✅ Test prioritizer ML model loaded")
        else:
            print("⚠️ Test prioritizer: using heuristic methods")
        
        # Advanced ML engine
        load_results = self.ml_engine.load_models()
        loaded_count = sum(load_results.values())
        print(f"📊 Advanced ML engine: {loaded_count}/{len(load_results)} models loaded")
    
    def run_complete_ml_analysis(self, project_path: str = "../services") -> Dict[str, Any]:
        """Executa análise ML completa do projeto"""
        print("\n🚀 Starting Complete ML Analysis")
        print("=" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_generation': {},
            'bug_analysis': {},
            'test_prioritization': {},
            'failure_prediction': {},
            'performance_analysis': {},
            'recommendations': []
        }
        
        # 1. Geração de testes com IA
        print("\n1️⃣ AI Test Generation")
        test_gen_results = self._run_test_generation(project_path)
        results['test_generation'] = test_gen_results
        
        # 2. Análise de padrões de bugs
        print("\n2️⃣ Bug Pattern Analysis")
        bug_analysis_results = self._run_bug_analysis()
        results['bug_analysis'] = bug_analysis_results
        
        # 3. Priorização inteligente
        print("\n3️⃣ Smart Test Prioritization")
        priority_results = self._run_test_prioritization()
        results['test_prioritization'] = priority_results
        
        # 4. Predição de falhas
        print("\n4️⃣ Failure Prediction")
        failure_results = self._run_failure_prediction()
        results['failure_prediction'] = failure_results
        
        # 5. Análise de performance
        print("\n5️⃣ Performance Analysis")
        performance_results = self._run_performance_analysis()
        results['performance_analysis'] = performance_results
        
        # 6. Gerar recomendações finais
        print("\n6️⃣ Generating ML Recommendations")
        recommendations = self._generate_ml_recommendations(results)
        results['recommendations'] = recommendations
        
        return results
    
    def _run_test_generation(self, project_path: str) -> Dict[str, Any]:
        """Executa geração de testes com IA"""
        try:
            # Simular análise de arquivos
            services = [
                f"{project_path}/user-service/main.py",
                f"{project_path}/order-service/app.js", 
                f"{project_path}/payment-service/main.go"
            ]
            
            all_test_cases = []
            analysis_results = []
            
            for service in services:
                print(f"   📁 Analyzing {service}...")
                
                # Análise do código (simulada se arquivo não existir)
                analysis = self.test_generator.analyze_code_file(service)
                analysis_results.append(analysis)
                
                if 'error' not in analysis:
                    test_cases = self.test_generator.generate_test_cases(analysis)
                    all_test_cases.extend(test_cases)
                    print(f"   ✅ Generated {len(test_cases)} test cases")
            
            # Relatório de geração
            report = self.test_generator.generate_test_report(all_test_cases)
            
            return {
                'total_tests_generated': len(all_test_cases),
                'services_analyzed': len([a for a in analysis_results if 'error' not in a]),
                'report': report,
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_bug_analysis(self) -> Dict[str, Any]:
        """Executa análise de padrões de bugs"""
        try:
            # Simular logs diversos para análise
            sample_logs = self._generate_sample_logs(50)
            
            print(f"   📊 Analyzing {len(sample_logs)} log entries...")
            
            # Analisar cada log
            for log in sample_logs:
                self.bug_analyzer.analyze_log_entry(log)
            
            # Gerar relatório ML
            report = self.bug_analyzer.generate_pattern_report()
            
            # Métricas ML
            ml_metrics = self.bug_analyzer.get_ml_metrics()
            
            print(f"   🤖 ML Model Active: {ml_metrics['model_trained']}")
            print(f"   📈 Detection Accuracy: {ml_metrics['accuracy']:.1%}")
            
            return {
                'logs_analyzed': len(sample_logs),
                'ml_metrics': ml_metrics,
                'report': report,
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_test_prioritization(self) -> Dict[str, Any]:
        """Executa priorização inteligente de testes"""
        try:
            # Criar test cases de exemplo
            sample_tests = self._generate_sample_test_cases(20)
            recent_changes = ["auth_service.py", "payment_api.py", "user_model.py"]
            
            print(f"   🎯 Prioritizing {len(sample_tests)} test cases...")
            
            # Priorizar testes
            priorities = self.test_prioritizer.prioritize_tests(sample_tests, recent_changes)
            
            # Gerar plano de execução
            execution_plan = self.test_prioritizer.generate_execution_plan(priorities)
            
            # Métricas ML
            ml_metrics = self.test_prioritizer.get_ml_metrics()
            
            print(f"   🤖 ML Model Active: {ml_metrics['model_trained']}")
            print(f"   📊 Top Priority Score: {max(p.priority_score for p in priorities):.3f}")
            
            return {
                'tests_prioritized': len(priorities),
                'execution_plan': execution_plan,
                'ml_metrics': ml_metrics,
                'top_priorities': [
                    {'name': p.test_case.name, 'score': p.priority_score, 'risk': p.risk_level.value}
                    for p in priorities[:5]
                ],
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_failure_prediction(self) -> Dict[str, Any]:
        """Executa predição de falhas"""
        try:
            # Criar métricas de teste para predição
            test_metrics = [
                TestMetrics("test_auth_critical", 45.0, 0.15, 85.0, "CRITICAL", datetime.now(), 0.2),
                TestMetrics("test_payment_flow", 120.0, 0.05, 92.0, "HIGH", datetime.now(), 0.1),
                TestMetrics("test_user_profile", 30.0, 0.25, 78.0, "MEDIUM", datetime.now(), 0.4),
                TestMetrics("test_flaky_integration", 200.0, 0.45, 65.0, "HIGH", datetime.now(), 0.8)
            ]
            
            predictions = []
            
            print(f"   🔮 Predicting failures for {len(test_metrics)} tests...")
            
            for metrics in test_metrics:
                prediction = self.ml_engine.predict_test_failure(metrics)
                predictions.append({
                    'test_name': metrics.test_name,
                    'failure_probability': prediction.prediction,
                    'confidence': prediction.confidence,
                    'reasoning': prediction.reasoning,
                    'model_used': prediction.model_used
                })
                
                risk_level = "🔴 HIGH" if prediction.prediction > 0.7 else "🟡 MEDIUM" if prediction.prediction > 0.4 else "🟢 LOW"
                print(f"   {risk_level} {metrics.test_name}: {prediction.prediction:.3f}")
            
            # Status dos modelos
            model_status = self.ml_engine.get_model_status()
            
            return {
                'predictions': predictions,
                'model_status': model_status,
                'high_risk_tests': len([p for p in predictions if p['failure_probability'] > 0.7]),
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_performance_analysis(self) -> Dict[str, Any]:
        """Executa análise de performance"""
        try:
            # Características de testes para predição de performance
            test_characteristics = [
                {'name': 'test_simple_unit', 'code_lines': 50, 'complexity_score': 2, 'network_calls': 0, 'io_operations': 1},
                {'name': 'test_complex_integration', 'code_lines': 300, 'complexity_score': 8, 'network_calls': 5, 'io_operations': 10},
                {'name': 'test_database_heavy', 'code_lines': 150, 'complexity_score': 5, 'network_calls': 2, 'io_operations': 15},
                {'name': 'test_api_endpoints', 'code_lines': 100, 'complexity_score': 4, 'network_calls': 8, 'io_operations': 3}
            ]
            
            performance_predictions = []
            
            print(f"   ⚡ Analyzing performance for {len(test_characteristics)} tests...")
            
            for char in test_characteristics:
                prediction = self.ml_engine.predict_execution_time(char)
                performance_predictions.append({
                    'test_name': char['name'],
                    'predicted_time': prediction.prediction,
                    'confidence': prediction.confidence,
                    'reasoning': prediction.reasoning,
                    'characteristics': char
                })
                
                time_category = "🐌 SLOW" if prediction.prediction > 180 else "🚀 FAST" if prediction.prediction < 60 else "⚡ MEDIUM"
                print(f"   {time_category} {char['name']}: {prediction.prediction:.1f}s")
            
            return {
                'performance_predictions': performance_predictions,
                'avg_predicted_time': np.mean([p['predicted_time'] for p in performance_predictions]),
                'slow_tests': len([p for p in performance_predictions if p['predicted_time'] > 180]),
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _generate_ml_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Gera recomendações baseadas em toda análise ML"""
        recommendations = []
        
        # Análise de geração de testes
        if results['test_generation'].get('success'):
            test_count = results['test_generation']['total_tests_generated']
            if test_count > 0:
                recommendations.append({
                    'category': 'TEST_GENERATION',
                    'priority': 'HIGH',
                    'title': f'AI Generated {test_count} Test Cases',
                    'description': 'Review and integrate AI-generated test cases into test suite',
                    'action': 'Implement generated test cases with highest risk scores first'
                })
        
        # Análise de bugs
        if results['bug_analysis'].get('success'):
            ml_active = results['bug_analysis']['ml_metrics']['model_trained']
            if ml_active:
                recommendations.append({
                    'category': 'BUG_DETECTION',
                    'priority': 'MEDIUM',
                    'title': 'ML Bug Detection Active',
                    'description': 'Machine learning model is actively detecting bug patterns',
                    'action': 'Monitor ML insights for proactive bug prevention'
                })
        
        # Análise de priorização
        if results['test_prioritization'].get('success'):
            high_priority_tests = len([p for p in results['test_prioritization']['top_priorities'] if p['score'] > 0.7])
            if high_priority_tests > 0:
                recommendations.append({
                    'category': 'TEST_PRIORITIZATION',
                    'priority': 'HIGH',
                    'title': f'{high_priority_tests} High-Priority Tests Identified',
                    'description': 'ML identified critical tests that should run first',
                    'action': 'Execute high-priority tests in every CI/CD pipeline'
                })
        
        # Análise de falhas
        if results['failure_prediction'].get('success'):
            high_risk_count = results['failure_prediction']['high_risk_tests']
            if high_risk_count > 0:
                recommendations.append({
                    'category': 'FAILURE_PREDICTION',
                    'priority': 'CRITICAL',
                    'title': f'{high_risk_count} Tests at High Risk of Failure',
                    'description': 'ML models predict high failure probability for specific tests',
                    'action': 'Investigate and stabilize high-risk tests immediately'
                })
        
        # Análise de performance
        if results['performance_analysis'].get('success'):
            slow_tests = results['performance_analysis']['slow_tests']
            if slow_tests > 0:
                recommendations.append({
                    'category': 'PERFORMANCE',
                    'priority': 'MEDIUM',
                    'title': f'{slow_tests} Slow Tests Detected',
                    'description': 'Performance analysis identified tests with long execution times',
                    'action': 'Optimize slow tests or run them in parallel/separate pipeline'
                })
        
        return recommendations
    
    def _generate_sample_logs(self, count: int) -> List[Dict[str, Any]]:
        """Gera logs de exemplo para análise"""
        log_templates = [
            "Connection timeout occurred while connecting to database",
            "NullPointerException in payment processing module",
            "Authentication failed for user request",
            "Memory leak detected in user session management",
            "Rate limit exceeded for API endpoint /users",
            "Database connection pool exhausted",
            "Validation error: invalid email format provided",
            "Network timeout during payment gateway communication",
            "SQL injection attempt detected and blocked",
            "Service mesh communication failure between services"
        ]
        
        services = ['user-service', 'order-service', 'payment-service', 'api-gateway']
        levels = ['ERROR', 'WARNING', 'CRITICAL', 'INFO']
        
        logs = []
        for i in range(count):
            logs.append({
                'message': np.random.choice(log_templates),
                'service': np.random.choice(services),
                'timestamp': (datetime.now() - timedelta(hours=np.random.randint(0, 48))).isoformat(),
                'level': np.random.choice(levels, p=[0.4, 0.3, 0.1, 0.2])
            })
        
        return logs
    
    def _generate_sample_test_cases(self, count: int) -> List[TestCase]:
        """Gera test cases de exemplo"""
        test_types = ['SECURITY', 'API', 'DATABASE', 'INTEGRATION', 'UNIT', 'UI']
        business_impacts = list(BusinessImpact)
        
        test_cases = []
        for i in range(count):
            test_cases.append(TestCase(
                name=f"test_sample_{i}",
                file_path=f"test_sample_{i}.py",
                test_type=np.random.choice(test_types),
                execution_time=np.random.uniform(10, 300),
                failure_count=np.random.randint(0, 8),
                code_coverage=np.random.uniform(40, 95),
                business_impact=np.random.choice(business_impacts),
                last_failure=datetime.now().isoformat() if np.random.random() > 0.7 else None,
                dependencies=[f"service_{j}" for j in range(np.random.randint(0, 3))]
            ))
        
        return test_cases
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Salva resultados da análise ML"""
        # Criar pasta reports_ml se não existir
        reports_dir = "reports_ml"
        os.makedirs(reports_dir, exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ml_analysis_results_{timestamp}.json"
        
        # Salvar na pasta reports_ml
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {filepath}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

def main():
    """Executa demo completa da integração ML"""
    print("🤖 ML Testing Suite Integration Demo")
    print("=" * 60)
    
    # Inicializar suite
    ml_suite = MLTestingSuite()
    
    # Executar análise completa
    results = ml_suite.run_complete_ml_analysis()
    
    # Mostrar resumo final
    print("\n" + "=" * 60)
    print("📊 ML ANALYSIS SUMMARY")
    print("=" * 60)
    
    if results['test_generation'].get('success'):
        print(f"✅ Test Generation: {results['test_generation']['total_tests_generated']} tests generated")
    
    if results['bug_analysis'].get('success'):
        print(f"✅ Bug Analysis: {results['bug_analysis']['logs_analyzed']} logs analyzed")
    
    if results['test_prioritization'].get('success'):
        print(f"✅ Test Prioritization: {results['test_prioritization']['tests_prioritized']} tests prioritized")
    
    if results['failure_prediction'].get('success'):
        high_risk = results['failure_prediction']['high_risk_tests']
        print(f"✅ Failure Prediction: {high_risk} high-risk tests identified")
    
    if results['performance_analysis'].get('success'):
        avg_time = results['performance_analysis']['avg_predicted_time']
        print(f"✅ Performance Analysis: {avg_time:.1f}s average predicted execution time")
    
    print(f"\n🎯 Total Recommendations: {len(results['recommendations'])}")
    
    # Mostrar top recommendations
    print("\n🔝 TOP ML RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'][:3], 1):
        priority_emoji = "🔴" if rec['priority'] == 'CRITICAL' else "🟡" if rec['priority'] == 'HIGH' else "🟢"
        print(f"{i}. {priority_emoji} {rec['title']}")
        print(f"   Action: {rec['action']}")
    
    # Salvar resultados
    ml_suite.save_results(results)
    
    print(f"\n🎉 ML Analysis Complete! Check the generated report for detailed insights.")

if __name__ == "__main__":
    main()