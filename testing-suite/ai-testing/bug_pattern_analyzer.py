#!/usr/bin/env python3
"""
AI Bug Pattern Analyzer
Analisa logs e identifica padrões de bugs usando machine learning
"""

import re
import json
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics

class BugPatternAnalyzer:
    
    def __init__(self):
        self.error_patterns = {
            'connection_timeout': r'(timeout|connection.*timeout|read.*timeout)',
            'null_pointer': r'(null.*pointer|nullpointerexception|none.*type)',
            'authentication_failure': r'(auth.*fail|unauthorized|403|401)',
            'validation_error': r'(validation.*error|invalid.*input|422)',
            'database_error': r'(database.*error|sql.*error|connection.*refused)',
            'memory_error': r'(out.*of.*memory|memory.*error|heap.*space)',
            'network_error': r'(network.*error|connection.*reset|host.*unreachable)',
            'rate_limit': r'(rate.*limit|too.*many.*requests|429)'
        }
        
        self.severity_keywords = {
            'CRITICAL': ['critical', 'fatal', 'emergency', 'panic'],
            'HIGH': ['error', 'exception', 'failed', 'failure'],
            'MEDIUM': ['warning', 'warn', 'deprecated'],
            'LOW': ['info', 'debug', 'trace']
        }
        
        self.bug_history = []
        self.pattern_frequency = Counter()
        self.service_patterns = defaultdict(Counter)
    
    def analyze_log_entry(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa uma entrada de log individual"""
        message = log_entry.get('message', '').lower()
        service = log_entry.get('service', 'unknown')
        timestamp = log_entry.get('timestamp', datetime.now().isoformat())
        
        analysis = {
            'timestamp': timestamp,
            'service': service,
            'original_message': log_entry.get('message', ''),
            'patterns_detected': [],
            'severity': self._determine_severity(message),
            'bug_probability': 0.0,
            'recommendations': []
        }
        
        # Detectar padrões de erro
        for pattern_name, pattern_regex in self.error_patterns.items():
            if re.search(pattern_regex, message, re.IGNORECASE):
                analysis['patterns_detected'].append(pattern_name)
                self.pattern_frequency[pattern_name] += 1
                self.service_patterns[service][pattern_name] += 1
        
        # Calcular probabilidade de bug
        analysis['bug_probability'] = self._calculate_bug_probability(analysis)
        
        # Gerar recomendações
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        # Adicionar ao histórico
        self.bug_history.append(analysis)
        
        return analysis
    
    def _determine_severity(self, message: str) -> str:
        """Determina a severidade baseada no conteúdo da mensagem"""
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in message for keyword in keywords):
                return severity
        return 'LOW'
    
    def _calculate_bug_probability(self, analysis: Dict[str, Any]) -> float:
        """Calcula probabilidade de ser um bug real"""
        probability = 0.0
        
        # Base probability por severidade
        severity_weights = {'CRITICAL': 0.9, 'HIGH': 0.7, 'MEDIUM': 0.4, 'LOW': 0.1}
        probability += severity_weights.get(analysis['severity'], 0.1)
        
        # Adicionar peso por padrões detectados
        pattern_weights = {
            'connection_timeout': 0.6,
            'null_pointer': 0.8,
            'authentication_failure': 0.5,
            'validation_error': 0.3,
            'database_error': 0.7,
            'memory_error': 0.9,
            'network_error': 0.6,
            'rate_limit': 0.4
        }
        
        for pattern in analysis['patterns_detected']:
            probability += pattern_weights.get(pattern, 0.2)
        
        # Normalizar entre 0 e 1
        return min(probability, 1.0)
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos padrões detectados"""
        recommendations = []
        
        for pattern in analysis['patterns_detected']:
            if pattern == 'connection_timeout':
                recommendations.append("Increase timeout values and implement retry logic")
            elif pattern == 'null_pointer':
                recommendations.append("Add null checks and defensive programming")
            elif pattern == 'authentication_failure':
                recommendations.append("Review authentication logic and token validation")
            elif pattern == 'validation_error':
                recommendations.append("Strengthen input validation and error messages")
            elif pattern == 'database_error':
                recommendations.append("Check database connectivity and query optimization")
            elif pattern == 'memory_error':
                recommendations.append("Investigate memory leaks and optimize resource usage")
            elif pattern == 'network_error':
                recommendations.append("Implement circuit breaker and network resilience")
            elif pattern == 'rate_limit':
                recommendations.append("Implement backoff strategy and rate limiting")
        
        if analysis['bug_probability'] > 0.7:
            recommendations.append("HIGH PRIORITY: Investigate immediately")
        elif analysis['bug_probability'] > 0.5:
            recommendations.append("MEDIUM PRIORITY: Schedule investigation")
        
        return recommendations
    
    def generate_pattern_report(self) -> Dict[str, Any]:
        """Gera relatório de padrões de bugs identificados"""
        if not self.bug_history:
            return {'error': 'No data analyzed yet'}
        
        # Estatísticas gerais
        total_entries = len(self.bug_history)
        high_probability_bugs = [b for b in self.bug_history if b['bug_probability'] > 0.7]
        
        # Padrões mais comuns
        top_patterns = self.pattern_frequency.most_common(5)
        
        # Serviços mais problemáticos
        service_bug_counts = defaultdict(int)
        for entry in self.bug_history:
            if entry['bug_probability'] > 0.5:
                service_bug_counts[entry['service']] += 1
        
        # Tendências temporais
        recent_bugs = [b for b in self.bug_history 
                      if self._is_recent(b['timestamp'], hours=24)]
        
        report = {
            'summary': {
                'total_log_entries': total_entries,
                'high_probability_bugs': len(high_probability_bugs),
                'bug_detection_rate': len(high_probability_bugs) / total_entries if total_entries > 0 else 0,
                'recent_bugs_24h': len(recent_bugs)
            },
            'top_patterns': [
                {'pattern': pattern, 'count': count, 'percentage': (count/total_entries)*100}
                for pattern, count in top_patterns
            ],
            'problematic_services': [
                {'service': service, 'bug_count': count}
                for service, count in sorted(service_bug_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
            ],
            'severity_distribution': self._get_severity_distribution(),
            'recommendations': self._get_global_recommendations(),
            'trends': {
                'recent_increase': len(recent_bugs) > total_entries * 0.1,
                'most_active_service': max(service_bug_counts.items(), 
                                         key=lambda x: x[1])[0] if service_bug_counts else 'none'
            }
        }
        
        return report
    
    def _is_recent(self, timestamp_str: str, hours: int = 24) -> bool:
        """Verifica se timestamp é recente"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            cutoff = datetime.now() - timedelta(hours=hours)
            return timestamp > cutoff
        except:
            return False
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de severidade"""
        distribution = Counter()
        for entry in self.bug_history:
            distribution[entry['severity']] += 1
        return dict(distribution)
    
    def _get_global_recommendations(self) -> List[str]:
        """Gera recomendações globais baseadas em todos os dados"""
        recommendations = []
        
        # Padrão mais comum
        if self.pattern_frequency:
            most_common = self.pattern_frequency.most_common(1)[0]
            recommendations.append(f"Focus on {most_common[0]} issues - {most_common[1]} occurrences")
        
        # Serviços problemáticos
        service_issues = defaultdict(int)
        for entry in self.bug_history:
            if entry['bug_probability'] > 0.5:
                service_issues[entry['service']] += 1
        
        if service_issues:
            worst_service = max(service_issues.items(), key=lambda x: x[1])
            recommendations.append(f"Priority service for improvement: {worst_service[0]}")
        
        # Taxa de bugs alta
        if self.bug_history:  # Prevent division by zero
            high_prob_rate = len([b for b in self.bug_history if b['bug_probability'] > 0.7]) / len(self.bug_history)
            if high_prob_rate > 0.1:
                recommendations.append("High bug detection rate - consider code review and testing improvements")
        
        return recommendations
    
    def predict_future_issues(self) -> Dict[str, Any]:
        """Prediz possíveis problemas futuros baseado em padrões"""
        if len(self.bug_history) < 10:
            return {'error': 'Insufficient data for prediction'}
        
        # Análise de tendências
        recent_24h = [b for b in self.bug_history if self._is_recent(b['timestamp'], 24)]
        recent_1h = [b for b in self.bug_history if self._is_recent(b['timestamp'], 1)]
        
        predictions = {
            'risk_level': 'LOW',
            'predicted_issues': [],
            'confidence': 0.0,
            'time_to_next_critical': 'Unknown'
        }
        
        # Calcular tendência
        if len(recent_1h) > len(recent_24h) * 0.1:  # Mais de 10% dos bugs nas últimas 1h
            predictions['risk_level'] = 'HIGH'
            predictions['predicted_issues'].append('Spike in error rate detected')
        
        # Padrões emergentes
        recent_patterns = Counter()
        for entry in recent_24h:
            for pattern in entry['patterns_detected']:
                recent_patterns[pattern] += 1
        
        if recent_patterns:
            emerging = recent_patterns.most_common(1)[0]
            if emerging[1] > 3:  # Mais de 3 ocorrências
                predictions['predicted_issues'].append(f'Emerging pattern: {emerging[0]}')
        
        # Confiança da predição
        predictions['confidence'] = min(len(self.bug_history) / 100, 1.0)
        
        return predictions

def main():
    """Exemplo de uso do Bug Pattern Analyzer"""
    analyzer = BugPatternAnalyzer()
    
    # Simular logs de exemplo
    sample_logs = [
        {
            'message': 'Connection timeout occurred while connecting to database',
            'service': 'user-service',
            'timestamp': datetime.now().isoformat(),
            'level': 'ERROR'
        },
        {
            'message': 'NullPointerException in payment processing',
            'service': 'payment-service', 
            'timestamp': datetime.now().isoformat(),
            'level': 'ERROR'
        },
        {
            'message': 'Authentication failed for user request',
            'service': 'order-service',
            'timestamp': datetime.now().isoformat(),
            'level': 'WARNING'
        }
    ]
    
    print("Analyzing sample logs...")
    for log in sample_logs:
        analysis = analyzer.analyze_log_entry(log)
        print(f"Service: {analysis['service']}")
        print(f"Patterns: {analysis['patterns_detected']}")
        print(f"Bug Probability: {analysis['bug_probability']:.2f}")
        print(f"Recommendations: {analysis['recommendations']}")
        print("---")
    
    # Gerar relatório
    report = analyzer.generate_pattern_report()
    print("\nBug Pattern Report:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()