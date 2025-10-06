#!/usr/bin/env python3
"""
Simple ML Demo - Sem dependências pesadas
Demonstra funcionalidades ML básicas sem scikit-learn
"""

import json
import math
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class SimpleBugAnalyzer:
    """Analisador de bugs simplificado sem ML pesado"""
    
    def __init__(self):
        self.patterns = {
            'timeout': r'timeout|connection.*timeout',
            'null_error': r'null|none.*type|nullpointer',
            'auth_fail': r'auth.*fail|unauthorized|403|401',
            'validation': r'validation.*error|invalid.*input',
            'memory': r'memory.*error|out.*of.*memory'
        }
        self.bug_history = []
    
    def analyze_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Análise simples de log"""
        message = log_entry.get('message', '').lower()
        
        # Detectar padrões
        detected_patterns = []
        for pattern_name, pattern in self.patterns.items():
            if pattern in message:
                detected_patterns.append(pattern_name)
        
        # Calcular probabilidade simples
        severity_scores = {'critical': 0.9, 'error': 0.7, 'warning': 0.4, 'info': 0.1}
        level = log_entry.get('level', 'info').lower()
        base_prob = severity_scores.get(level, 0.1)
        
        pattern_bonus = len(detected_patterns) * 0.2
        bug_probability = min(base_prob + pattern_bonus, 1.0)
        
        analysis = {
            'service': log_entry.get('service', 'unknown'),
            'patterns_detected': detected_patterns,
            'bug_probability': bug_probability,
            'severity': level.upper(),
            'timestamp': log_entry.get('timestamp', datetime.now().isoformat())
        }
        
        self.bug_history.append(analysis)
        return analysis
    
    def get_summary(self) -> Dict[str, Any]:
        """Resumo da análise"""
        if not self.bug_history:
            return {'total_logs': 0}
        
        high_prob_bugs = [b for b in self.bug_history if b['bug_probability'] > 0.7]
        pattern_counts = Counter()
        
        for entry in self.bug_history:
            for pattern in entry['patterns_detected']:
                pattern_counts[pattern] += 1
        
        return {
            'total_logs': len(self.bug_history),
            'high_probability_bugs': len(high_prob_bugs),
            'detection_rate': len(high_prob_bugs) / len(self.bug_history),
            'top_patterns': dict(pattern_counts.most_common(3)),
            'avg_bug_probability': sum(b['bug_probability'] for b in self.bug_history) / len(self.bug_history)
        }

class SimpleTestPrioritizer:
    """Priorizador de testes simplificado"""
    
    def __init__(self):
        self.weights = {
            'failure_rate': 0.3,
            'execution_time': 0.2,
            'business_impact': 0.25,
            'code_coverage': 0.15,
            'recent_changes': 0.1
        }
    
    def calculate_priority(self, test_info: Dict[str, Any]) -> float:
        """Calcula prioridade do teste"""
        # Normalizar failure rate
        failure_score = min(test_info.get('failure_count', 0) / 10.0, 1.0)
        
        # Tempo de execução (inverso - testes rápidos têm prioridade)
        time_score = 1.0 / (1.0 + test_info.get('execution_time', 60) / 60.0)
        
        # Impacto de negócio
        impact_map = {'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.2}
        business_score = impact_map.get(test_info.get('business_impact', 'medium').lower(), 0.5)
        
        # Cobertura de código
        coverage_score = test_info.get('code_coverage', 50) / 100.0
        
        # Mudanças recentes
        change_score = 1.0 if test_info.get('recent_changes', False) else 0.3
        
        # Score final ponderado
        priority_score = (
            failure_score * self.weights['failure_rate'] +
            time_score * self.weights['execution_time'] +
            business_score * self.weights['business_impact'] +
            coverage_score * self.weights['code_coverage'] +
            change_score * self.weights['recent_changes']
        )
        
        return min(priority_score, 1.0)
    
    def prioritize_tests(self, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriza lista de testes"""
        prioritized = []
        
        for test in tests:
            priority_score = self.calculate_priority(test)
            
            # Determinar nível de risco
            if priority_score > 0.8:
                risk_level = 'CRITICAL'
            elif priority_score > 0.6:
                risk_level = 'HIGH'
            elif priority_score > 0.4:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            prioritized.append({
                **test,
                'priority_score': priority_score,
                'risk_level': risk_level
            })
        
        # Ordenar por prioridade
        return sorted(prioritized, key=lambda x: x['priority_score'], reverse=True)

class SimplePerformancePredictor:
    """Preditor de performance simplificado"""
    
    def __init__(self):
        self.base_times = {
            'unit': 15,
            'integration': 120,
            'api': 60,
            'database': 90,
            'ui': 200,
            'security': 45
        }
    
    def predict_execution_time(self, test_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Prediz tempo de execução"""
        test_type = test_characteristics.get('test_type', 'unit').lower()
        base_time = self.base_times.get(test_type, 60)
        
        # Fatores de ajuste
        complexity = test_characteristics.get('complexity_score', 1)
        network_calls = test_characteristics.get('network_calls', 0)
        io_operations = test_characteristics.get('io_operations', 0)
        
        # Calcular tempo ajustado
        complexity_factor = 1 + (complexity - 1) * 0.2
        network_factor = 1 + network_calls * 0.1
        io_factor = 1 + io_operations * 0.05
        
        predicted_time = base_time * complexity_factor * network_factor * io_factor
        
        # Adicionar variabilidade
        variance = predicted_time * 0.2
        confidence = max(0.6, 1.0 - (variance / predicted_time))
        
        return {
            'predicted_time': predicted_time,
            'confidence': confidence,
            'base_time': base_time,
            'factors': {
                'complexity': complexity_factor,
                'network': network_factor,
                'io': io_factor
            }
        }

def run_simple_ml_demo():
    """Executa demo ML simplificado"""
    print("AI Simple ML Demo - Testing Intelligence")
    print("=" * 50)
    
    # 1. Bug Analysis Demo
    print("\n1. Bug Pattern Analysis")
    bug_analyzer = SimpleBugAnalyzer()
    
    sample_logs = [
        {'message': 'Connection timeout occurred', 'service': 'user-service', 'level': 'ERROR'},
        {'message': 'NullPointerException in payment', 'service': 'payment-service', 'level': 'ERROR'},
        {'message': 'Authentication failed', 'service': 'auth-service', 'level': 'WARNING'},
        {'message': 'Memory leak detected', 'service': 'user-service', 'level': 'CRITICAL'},
        {'message': 'Validation error: invalid email', 'service': 'user-service', 'level': 'INFO'}
    ]
    
    for log in sample_logs:
        analysis = bug_analyzer.analyze_log(log)
        print(f"   {analysis['service']}: {analysis['bug_probability']:.3f} | {analysis['patterns_detected']}")
    
    summary = bug_analyzer.get_summary()
    print(f"\n   Summary: {summary['high_probability_bugs']}/{summary['total_logs']} high-risk bugs")
    print(f"   Detection Rate: {summary['detection_rate']:.1%}")
    
    # 2. Test Prioritization Demo
    print("\n2. Test Prioritization")
    prioritizer = SimpleTestPrioritizer()
    
    sample_tests = [
        {'name': 'test_auth_critical', 'failure_count': 3, 'execution_time': 45, 'business_impact': 'critical', 'code_coverage': 85, 'recent_changes': True},
        {'name': 'test_payment_flow', 'failure_count': 0, 'execution_time': 120, 'business_impact': 'high', 'code_coverage': 92, 'recent_changes': False},
        {'name': 'test_user_profile', 'failure_count': 1, 'execution_time': 30, 'business_impact': 'medium', 'code_coverage': 78, 'recent_changes': False},
        {'name': 'test_ui_navigation', 'failure_count': 5, 'execution_time': 200, 'business_impact': 'low', 'code_coverage': 45, 'recent_changes': True}
    ]
    
    prioritized = prioritizer.prioritize_tests(sample_tests)
    
    for i, test in enumerate(prioritized, 1):
        risk_symbol = "[CRITICAL]" if test['risk_level'] == 'CRITICAL' else "[HIGH]" if test['risk_level'] == 'HIGH' else "[LOW]"
        print(f"   {i}. {risk_symbol} {test['name']}: {test['priority_score']:.3f} ({test['risk_level']})")
    
    # 3. Performance Prediction Demo
    print("\n3. Performance Prediction")
    predictor = SimplePerformancePredictor()
    
    test_scenarios = [
        {'name': 'Simple Unit Test', 'test_type': 'unit', 'complexity_score': 2, 'network_calls': 0, 'io_operations': 1},
        {'name': 'Complex Integration', 'test_type': 'integration', 'complexity_score': 8, 'network_calls': 5, 'io_operations': 10},
        {'name': 'API Endpoint Test', 'test_type': 'api', 'complexity_score': 4, 'network_calls': 3, 'io_operations': 2},
        {'name': 'Database Heavy Test', 'test_type': 'database', 'complexity_score': 6, 'network_calls': 1, 'io_operations': 15}
    ]
    
    for scenario in test_scenarios:
        prediction = predictor.predict_execution_time(scenario)
        time_category = "[SLOW]" if prediction['predicted_time'] > 180 else "[FAST]" if prediction['predicted_time'] < 60 else "[MEDIUM]"
        print(f"   {time_category} {scenario['name']}: {prediction['predicted_time']:.1f}s (confidence: {prediction['confidence']:.1%})")
    
    # 4. Generate Recommendations
    print("\n4. AI Recommendations")
    recommendations = []
    
    # Baseado na análise de bugs
    if summary['detection_rate'] > 0.4:
        recommendations.append("[HIGH] High bug detection rate - review code quality")
    
    # Baseado na priorização
    critical_tests = [t for t in prioritized if t['risk_level'] == 'CRITICAL']
    if critical_tests:
        recommendations.append(f"[MEDIUM] {len(critical_tests)} critical tests need immediate attention")
    
    # Baseado na performance
    slow_tests = [s for s in test_scenarios if predictor.predict_execution_time(s)['predicted_time'] > 180]
    if slow_tests:
        recommendations.append(f"[LOW] {len(slow_tests)} tests predicted to be slow - consider optimization")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\nSimple ML Analysis Complete!")
    print(f"Analyzed {len(sample_logs)} logs, prioritized {len(sample_tests)} tests, predicted {len(test_scenarios)} scenarios")

if __name__ == "__main__":
    run_simple_ml_demo()