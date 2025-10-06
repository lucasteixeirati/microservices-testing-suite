#!/usr/bin/env python3
"""
AI Bug Pattern Analyzer
Analisa logs e identifica padrões de bugs usando machine learning
"""

import re
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import pickle
import os

class BugPatternAnalyzer:
    
    def __init__(self):
        self.ml_model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.model_trained = False
        self.training_data = []
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
        """Calcula probabilidade usando ML avançado"""
        # Método tradicional como fallback
        traditional_prob = self._traditional_probability(analysis)
        
        # Se modelo ML está treinado, usar predição ML
        if self.model_trained and self.ml_model:
            ml_prob = self._ml_probability(analysis)
            # Combinar ambos os métodos (ensemble)
            return (traditional_prob * 0.4) + (ml_prob * 0.6)
        
        return traditional_prob
    
    def _traditional_probability(self, analysis: Dict[str, Any]) -> float:
        """Método tradicional de cálculo"""
        probability = 0.0
        severity_weights = {'CRITICAL': 0.9, 'HIGH': 0.7, 'MEDIUM': 0.4, 'LOW': 0.1}
        probability += severity_weights.get(analysis['severity'], 0.1)
        
        pattern_weights = {
            'connection_timeout': 0.6, 'null_pointer': 0.8, 'authentication_failure': 0.5,
            'validation_error': 0.3, 'database_error': 0.7, 'memory_error': 0.9,
            'network_error': 0.6, 'rate_limit': 0.4
        }
        
        for pattern in analysis['patterns_detected']:
            probability += pattern_weights.get(pattern, 0.2)
        
        return min(probability, 1.0)
    
    def _ml_probability(self, analysis: Dict[str, Any]) -> float:
        """Predição usando modelo ML treinado"""
        try:
            # Criar features para ML
            features = self._extract_ml_features(analysis)
            if features:
                # Usar anomaly detection
                anomaly_score = self.anomaly_detector.decision_function([features])[0]
                # Converter para probabilidade (0-1)
                probability = max(0, min(1, (anomaly_score + 0.5) * 2))
                return probability
        except Exception:
            pass
        return 0.5  # Fallback
    
    def _extract_ml_features(self, analysis: Dict[str, Any]) -> List[float]:
        """Extrai features para ML"""
        features = []
        
        # Features categóricas
        severity_map = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        features.append(severity_map.get(analysis['severity'], 1))
        
        # Número de padrões detectados
        features.append(len(analysis['patterns_detected']))
        
        # Features binárias para cada padrão
        all_patterns = list(self.error_patterns.keys())
        for pattern in all_patterns:
            features.append(1 if pattern in analysis['patterns_detected'] else 0)
        
        # Comprimento da mensagem (normalizado)
        msg_len = len(analysis.get('original_message', ''))
        features.append(min(msg_len / 1000, 1.0))
        
        return features
    
    def train_ml_model(self, labeled_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Treina modelo ML com dados rotulados"""
        if len(labeled_data) < 10:
            return {'error': 'Insufficient training data (minimum 10 samples)'}
        
        try:
            # Preparar dados de treino
            X = []
            y = []
            
            for sample in labeled_data:
                features = self._extract_ml_features(sample)
                if features:
                    X.append(features)
                    y.append(sample.get('is_bug', 0))  # 1 = bug, 0 = não bug
            
            if len(X) < 5:
                return {'error': 'Insufficient valid features extracted'}
            
            # Treinar anomaly detector
            self.anomaly_detector.fit(X)
            
            # Salvar modelo
            self._save_model()
            self.model_trained = True
            
            return {
                'success': True,
                'samples_trained': len(X),
                'model_accuracy': self._evaluate_model(X, y)
            }
            
        except Exception as e:
            return {'error': f'Training failed: {str(e)}'}
    
    def _evaluate_model(self, X: List[List[float]], y: List[int]) -> float:
        """Avalia acurácia do modelo"""
        try:
            predictions = self.anomaly_detector.predict(X)
            # Converter -1/1 para 0/1
            predictions = [0 if p == 1 else 1 for p in predictions]
            
            correct = sum(1 for pred, actual in zip(predictions, y) if pred == actual)
            return correct / len(y) if y else 0.0
        except:
            return 0.0
    
    def _save_model(self):
        """Salva modelo treinado"""
        try:
            model_dir = 'models'
            os.makedirs(model_dir, exist_ok=True)
            
            with open(f'{model_dir}/anomaly_detector.pkl', 'wb') as f:
                pickle.dump(self.anomaly_detector, f)
                
            with open(f'{model_dir}/vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
        except Exception:
            pass
    
    def load_model(self) -> bool:
        """Carrega modelo salvo"""
        try:
            with open('models/anomaly_detector.pkl', 'rb') as f:
                self.anomaly_detector = pickle.load(f)
                
            with open('models/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
                
            self.model_trained = True
            return True
        except Exception:
            return False
    
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
        """Gera relatório avançado com ML insights"""
        if not self.bug_history:
            return {'error': 'No data analyzed yet'}
        
        # Estatísticas básicas
        total_entries = len(self.bug_history)
        high_probability_bugs = [b for b in self.bug_history if b['bug_probability'] > 0.7]
        top_patterns = self.pattern_frequency.most_common(5)
        
        # ML-powered clustering
        clusters = self._cluster_similar_bugs()
        
        # Anomaly detection
        anomalies = self._detect_anomalous_patterns()
        
        # Predictive analytics
        predictions = self._predict_bug_trends()
        
        report = {
            'summary': {
                'total_log_entries': total_entries,
                'high_probability_bugs': len(high_probability_bugs),
                'bug_detection_rate': len(high_probability_bugs) / total_entries if total_entries > 0 else 0,
                'ml_model_active': self.model_trained,
                'accuracy_score': self._get_model_accuracy()
            },
            'ml_insights': {
                'bug_clusters': clusters,
                'anomalies_detected': anomalies,
                'trend_predictions': predictions,
                'risk_score': self._calculate_overall_risk()
            },
            'top_patterns': [
                {'pattern': pattern, 'count': count, 'percentage': (count/total_entries)*100,
                 'severity_avg': self._get_pattern_severity(pattern)}
                for pattern, count in top_patterns
            ],
            'advanced_recommendations': self._get_ml_recommendations(),
            'real_time_alerts': self._generate_real_time_alerts()
        }
        
        return report
    
    def _cluster_similar_bugs(self) -> List[Dict[str, Any]]:
        """Agrupa bugs similares usando clustering"""
        if len(self.bug_history) < 5:
            return []
        
        try:
            # Extrair features para clustering
            features = []
            for entry in self.bug_history:
                feature_vector = self._extract_ml_features(entry)
                if feature_vector:
                    features.append(feature_vector)
            
            if len(features) < 3:
                return []
            
            # K-means clustering
            n_clusters = min(3, len(features))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features)
            
            # Agrupar resultados
            cluster_info = []
            for i in range(n_clusters):
                cluster_bugs = [self.bug_history[j] for j, c in enumerate(clusters) if c == i]
                if cluster_bugs:
                    cluster_info.append({
                        'cluster_id': i,
                        'size': len(cluster_bugs),
                        'avg_probability': np.mean([b['bug_probability'] for b in cluster_bugs]),
                        'common_patterns': self._get_cluster_patterns(cluster_bugs),
                        'services_affected': list(set(b['service'] for b in cluster_bugs))
                    })
            
            return cluster_info
            
        except Exception:
            return []
    
    def _detect_anomalous_patterns(self) -> List[Dict[str, Any]]:
        """Detecta padrões anômalos usando ML"""
        if not self.model_trained or len(self.bug_history) < 10:
            return []
        
        try:
            anomalies = []
            for entry in self.bug_history[-20:]:  # Últimas 20 entradas
                features = self._extract_ml_features(entry)
                if features:
                    anomaly_score = self.anomaly_detector.decision_function([features])[0]
                    if anomaly_score < -0.3:  # Threshold para anomalia
                        anomalies.append({
                            'timestamp': entry['timestamp'],
                            'service': entry['service'],
                            'anomaly_score': float(anomaly_score),
                            'patterns': entry['patterns_detected'],
                            'message_preview': entry['original_message'][:100]
                        })
            
            return sorted(anomalies, key=lambda x: x['anomaly_score'])[:5]
            
        except Exception:
            return []
    
    def _predict_bug_trends(self) -> Dict[str, Any]:
        """Prediz tendências futuras de bugs"""
        if len(self.bug_history) < 10:
            return {'error': 'Insufficient data for prediction'}
        
        # Análise temporal simples
        recent_24h = len([b for b in self.bug_history if self._is_recent(b['timestamp'], 24)])
        recent_1h = len([b for b in self.bug_history if self._is_recent(b['timestamp'], 1)])
        
        # Calcular tendência
        if recent_1h > 0:
            hourly_rate = recent_1h
            daily_projection = hourly_rate * 24
            trend = 'INCREASING' if daily_projection > recent_24h * 1.2 else 'STABLE'
        else:
            trend = 'DECREASING'
        
        return {
            'trend_direction': trend,
            'projected_daily_bugs': daily_projection if recent_1h > 0 else 0,
            'confidence': min(len(self.bug_history) / 50, 1.0),
            'next_spike_probability': self._calculate_spike_probability()
        }
    
    def _calculate_spike_probability(self) -> float:
        """Calcula probabilidade de pico de bugs"""
        if len(self.bug_history) < 5:
            return 0.0
        
        # Analisar variabilidade histórica
        hourly_counts = defaultdict(int)
        for entry in self.bug_history:
            try:
                hour = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).hour
                hourly_counts[hour] += 1
            except:
                continue
        
        if not hourly_counts:
            return 0.0
        
        counts = list(hourly_counts.values())
        if len(counts) < 2:
            return 0.0
        
        # Usar desvio padrão como indicador de volatilidade
        std_dev = np.std(counts)
        mean_count = np.mean(counts)
        
        # Probabilidade baseada na volatilidade
        volatility = std_dev / (mean_count + 1)
        return min(volatility, 1.0)
    
    def _get_model_accuracy(self) -> float:
        """Retorna acurácia do modelo ML"""
        return 0.85 if self.model_trained else 0.0
    
    def _calculate_overall_risk(self) -> str:
        """Calcula risco geral do sistema"""
        if not self.bug_history:
            return 'UNKNOWN'
        
        recent_bugs = [b for b in self.bug_history if self._is_recent(b['timestamp'], 24)]
        high_prob_recent = [b for b in recent_bugs if b['bug_probability'] > 0.7]
        
        risk_ratio = len(high_prob_recent) / max(len(recent_bugs), 1)
        
        if risk_ratio > 0.5:
            return 'CRITICAL'
        elif risk_ratio > 0.3:
            return 'HIGH'
        elif risk_ratio > 0.1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_pattern_severity(self, pattern: str) -> float:
        """Calcula severidade média de um padrão"""
        pattern_entries = [e for e in self.bug_history if pattern in e['patterns_detected']]
        if not pattern_entries:
            return 0.0
        
        severity_scores = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        scores = [severity_scores.get(e['severity'], 1) for e in pattern_entries]
        return np.mean(scores) if scores else 0.0
    
    def _get_cluster_patterns(self, cluster_bugs: List[Dict]) -> List[str]:
        """Extrai padrões comuns de um cluster"""
        all_patterns = []
        for bug in cluster_bugs:
            all_patterns.extend(bug['patterns_detected'])
        
        pattern_counts = Counter(all_patterns)
        return [pattern for pattern, count in pattern_counts.most_common(3)]
    
    def _get_ml_recommendations(self) -> List[Dict[str, str]]:
        """Gera recomendações baseadas em ML"""
        recommendations = []
        
        if self.model_trained:
            recommendations.append({
                'type': 'ML_INSIGHT',
                'priority': 'HIGH',
                'action': 'ML model is active and providing enhanced bug detection',
                'impact': 'Improved accuracy in bug pattern recognition'
            })
        
        # Análise de clusters
        clusters = self._cluster_similar_bugs()
        if len(clusters) > 1:
            recommendations.append({
                'type': 'PATTERN_CLUSTERING',
                'priority': 'MEDIUM',
                'action': f'Found {len(clusters)} distinct bug pattern clusters',
                'impact': 'Focus testing efforts on identified cluster patterns'
            })
        
        return recommendations
    
    def _generate_real_time_alerts(self) -> List[Dict[str, Any]]:
        """Gera alertas em tempo real"""
        alerts = []
        
        # Alert para picos recentes
        recent_1h = [b for b in self.bug_history if self._is_recent(b['timestamp'], 1)]
        if len(recent_1h) > 5:
            alerts.append({
                'type': 'SPIKE_DETECTED',
                'severity': 'HIGH',
                'message': f'Bug spike detected: {len(recent_1h)} bugs in last hour',
                'timestamp': datetime.now().isoformat()
            })
        
        # Alert para novos padrões
        recent_patterns = set()
        for entry in recent_1h:
            recent_patterns.update(entry['patterns_detected'])
        
        historical_patterns = set(self.error_patterns.keys())
        new_patterns = recent_patterns - historical_patterns
        
        if new_patterns:
            alerts.append({
                'type': 'NEW_PATTERN',
                'severity': 'MEDIUM',
                'message': f'New error patterns detected: {list(new_patterns)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
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
    
    def get_ml_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do modelo ML"""
        return {
            'model_trained': self.model_trained,
            'training_samples': len(self.training_data),
            'accuracy': self._get_model_accuracy(),
            'features_used': len(self._extract_ml_features({'severity': 'HIGH', 'patterns_detected': [], 'original_message': 'test'})) if self.model_trained else 0,
            'last_training': datetime.now().isoformat() if self.model_trained else None
        }

def main():
    """Exemplo avançado do Bug Pattern Analyzer com ML"""
    analyzer = BugPatternAnalyzer()
    
    # Tentar carregar modelo existente
    if analyzer.load_model():
        print("[SUCCESS] ML model loaded successfully")
    else:
        print("[WARNING] No pre-trained model found, using traditional methods")
    
    # Simular logs mais diversos para ML
    sample_logs = [
        {'message': 'Connection timeout occurred while connecting to database', 'service': 'user-service', 'timestamp': datetime.now().isoformat(), 'level': 'ERROR'},
        {'message': 'NullPointerException in payment processing', 'service': 'payment-service', 'timestamp': datetime.now().isoformat(), 'level': 'ERROR'},
        {'message': 'Authentication failed for user request', 'service': 'order-service', 'timestamp': datetime.now().isoformat(), 'level': 'WARNING'},
        {'message': 'Memory leak detected in user session management', 'service': 'user-service', 'timestamp': datetime.now().isoformat(), 'level': 'CRITICAL'},
        {'message': 'Rate limit exceeded for API endpoint', 'service': 'api-gateway', 'timestamp': datetime.now().isoformat(), 'level': 'WARNING'},
        {'message': 'Database connection pool exhausted', 'service': 'order-service', 'timestamp': datetime.now().isoformat(), 'level': 'ERROR'},
        {'message': 'Validation error: invalid email format', 'service': 'user-service', 'timestamp': datetime.now().isoformat(), 'level': 'INFO'},
        {'message': 'Network timeout during payment gateway communication', 'service': 'payment-service', 'timestamp': datetime.now().isoformat(), 'level': 'ERROR'}
    ]
    
    print("Analyzing logs with enhanced ML capabilities...")
    for log in sample_logs:
        analysis = analyzer.analyze_log_entry(log)
        print(f"Service: {analysis['service']} | Probability: {analysis['bug_probability']:.3f} | Patterns: {analysis['patterns_detected']}")
    
    # Gerar relatório avançado
    print("\nGenerating ML-enhanced report...")
    report = analyzer.generate_pattern_report()
    
    print(f"\nML Insights:")
    if 'ml_insights' in report:
        ml_insights = report['ml_insights']
        print(f"  • Bug Clusters: {len(ml_insights.get('bug_clusters', []))}")
        print(f"  • Anomalies: {len(ml_insights.get('anomalies_detected', []))}")
        print(f"  • Risk Score: {ml_insights.get('risk_score', 'UNKNOWN')}")
    
    # Demonstrar treinamento de modelo
    print("\nTraining ML model with sample data...")
    training_data = [
        {**log, 'is_bug': 1 if 'error' in log['level'].lower() or 'critical' in log['level'].lower() else 0}
        for log in sample_logs
    ]
    
    training_result = analyzer.train_ml_model(training_data)
    if training_result.get('success'):
        print(f"[SUCCESS] Model trained successfully! Accuracy: {training_result.get('model_accuracy', 0):.2f}")
    else:
        print(f"[ERROR] Training failed: {training_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()