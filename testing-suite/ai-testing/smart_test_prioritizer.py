#!/usr/bin/env python3
"""
Smart Test Prioritizer
Usa IA para priorizar testes baseado em risco, histórico e impacto
"""

import json
import math
import numpy as np
from enum import Enum
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

class BusinessImpact(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ExecutionFrequency(str, Enum):
    EVERY_COMMIT = "Every commit"
    EVERY_BUILD = "Every build"
    DAILY = "Daily"
    WEEKLY = "Weekly"

@dataclass
class TestCase:
    name: str
    file_path: str
    test_type: str
    execution_time: float
    last_failure: str = None
    failure_count: int = 0
    code_coverage: float = 0.0
    business_impact: BusinessImpact = BusinessImpact.MEDIUM
    dependencies: List[str] = None

@dataclass
class TestPriority:
    test_case: TestCase
    priority_score: float
    risk_level: RiskLevel
    reasoning: List[str]
    recommended_frequency: ExecutionFrequency

class Config:
    """Centralized configuration for the prioritizer."""
    def __init__(self):
        self.weight_config = {
            'failure_history': 0.3,
            'business_impact': 0.25,
            'code_coverage': 0.2,
            'execution_time': 0.1,
            'code_changes': 0.15
        }
        self.business_impact_scores = {
            BusinessImpact.CRITICAL: 1.0,
            BusinessImpact.HIGH: 0.8,
            BusinessImpact.MEDIUM: 0.5,
            BusinessImpact.LOW: 0.2
        }
        self.test_type_weights = {
            'SECURITY': 1.0,
            'API': 0.9,
            'DATABASE': 0.8,
            'INTEGRATION': 0.7,
            'UNIT': 0.5,
            'UI': 0.6
        }
        self.risk_thresholds = [
            (0.8, RiskLevel.CRITICAL),
            (0.6, RiskLevel.HIGH),
            (0.4, RiskLevel.MEDIUM),
            (0.0, RiskLevel.LOW)
        ]

class SmartTestPrioritizer:
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.execution_history = []
        self.code_change_impact = {}
        self.ml_model = None
        self.scaler = StandardScaler()
        self.model_trained = False
        self.feature_importance = {}
        self.historical_performance = defaultdict(list)

    
    def calculate_priority_score(self, test_case: TestCase, 
                                recent_changes: List[str] = None) -> float:
        """Calcula score usando ML + heurísticas tradicionais"""
        
        # Score tradicional como baseline
        traditional_score = self._calculate_traditional_score(test_case, recent_changes)
        
        # Se modelo ML está treinado, usar predição ML
        if self.model_trained and self.ml_model:
            ml_score = self._calculate_ml_score(test_case, recent_changes)
            # Ensemble: combinar ambos os métodos
            return (traditional_score * 0.3) + (ml_score * 0.7)
        
        return traditional_score
    
    def _calculate_traditional_score(self, test_case: TestCase, recent_changes: List[str] = None) -> float:
        """Método tradicional de cálculo"""
        failure_score = self._calculate_failure_score(test_case)
        business_score = self.config.business_impact_scores.get(test_case.business_impact, 0.5)
        coverage_score = test_case.code_coverage / 100.0
        time_score = 1.0 / (1.0 + test_case.execution_time / 60.0)
        change_score = self._calculate_change_impact_score(test_case, recent_changes or [])
        type_score = self.config.test_type_weights.get(test_case.test_type, 0.5)
        
        final_score = (
            failure_score * self.config.weight_config['failure_history'] +
            business_score * self.config.weight_config['business_impact'] +
            coverage_score * self.config.weight_config['code_coverage'] +
            time_score * self.config.weight_config['execution_time'] +
            change_score * self.config.weight_config['code_changes']
        ) * type_score
        
        return min(final_score, 1.0)
    
    def _calculate_ml_score(self, test_case: TestCase, recent_changes: List[str] = None) -> float:
        """Calcula score usando modelo ML treinado"""
        try:
            features = self._extract_ml_features(test_case, recent_changes)
            if features:
                # Normalizar features
                features_scaled = self.scaler.transform([features])
                # Predição ML
                prediction = self.ml_model.predict(features_scaled)[0]
                return max(0.0, min(1.0, prediction))
        except Exception:
            pass
        return 0.5  # Fallback
    
    def _extract_ml_features(self, test_case: TestCase, recent_changes: List[str] = None) -> List[float]:
        """Extrai features para modelo ML"""
        features = []
        
        # Features numéricas básicas
        features.append(test_case.failure_count)
        features.append(test_case.execution_time)
        features.append(test_case.code_coverage)
        
        # Features categóricas (one-hot encoding)
        business_impact_map = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        features.append(business_impact_map.get(test_case.business_impact.value, 2))
        
        # Features de tipo de teste
        test_types = ['SECURITY', 'API', 'DATABASE', 'INTEGRATION', 'UNIT', 'UI']
        for test_type in test_types:
            features.append(1 if test_case.test_type == test_type else 0)
        
        # Features temporais
        if test_case.last_failure:
            try:
                last_failure_date = datetime.fromisoformat(test_case.last_failure)
                days_since_failure = (datetime.now() - last_failure_date).days
                features.append(days_since_failure)
            except:
                features.append(999)  # Valor padrão para falha antiga/inválida
        else:
            features.append(999)
        
        # Features de mudanças recentes
        change_impact = self._calculate_change_impact_score(test_case, recent_changes or [])
        features.append(change_impact)
        
        # Features de performance histórica
        historical_avg = np.mean(self.historical_performance.get(test_case.name, [0.5]))
        features.append(historical_avg)
        
        return features
    
    def train_ml_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Treina modelo ML para priorização"""
        if len(training_data) < 20:
            return {'error': 'Insufficient training data (minimum 20 samples)'}
        
        try:
            X = []
            y = []
            
            for sample in training_data:
                test_case = sample['test_case']
                actual_priority = sample['actual_priority']  # 0-1 score real
                recent_changes = sample.get('recent_changes', [])
                
                features = self._extract_ml_features(test_case, recent_changes)
                if features:
                    X.append(features)
                    y.append(actual_priority)
            
            if len(X) < 10:
                return {'error': 'Insufficient valid features extracted'}
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Treinar Random Forest
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.ml_model.fit(X_scaled, y)
            
            # Calcular importância das features
            self._calculate_feature_importance()
            
            # Salvar modelo
            self._save_ml_model()
            self.model_trained = True
            
            # Avaliar modelo
            score = self.ml_model.score(X_scaled, y)
            
            return {
                'success': True,
                'samples_trained': len(X),
                'r2_score': score,
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            return {'error': f'Training failed: {str(e)}'}
    
    def _calculate_feature_importance(self):
        """Calcula importância das features"""
        if self.ml_model and hasattr(self.ml_model, 'feature_importances_'):
            feature_names = [
                'failure_count', 'execution_time', 'code_coverage', 'business_impact',
                'is_security', 'is_api', 'is_database', 'is_integration', 'is_unit', 'is_ui',
                'days_since_failure', 'change_impact', 'historical_performance'
            ]
            
            importances = self.ml_model.feature_importances_
            self.feature_importance = dict(zip(feature_names, importances))
    
    def _save_ml_model(self):
        """Salva modelo ML treinado"""
        try:
            model_dir = 'models'
            os.makedirs(model_dir, exist_ok=True)
            
            with open(f'{model_dir}/priority_model.pkl', 'wb') as f:
                pickle.dump(self.ml_model, f)
                
            with open(f'{model_dir}/priority_scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)
                
            # Criar pasta reports_ml se não existir
            reports_dir = '../reports_ml'
            os.makedirs(reports_dir, exist_ok=True)
            
            with open(f'{model_dir}/feature_importance.json', 'w') as f:
                json.dump(self.feature_importance, f, indent=2)
                
            # Salvar cópia em reports_ml também
            with open(f'{reports_dir}/feature_importance.json', 'w') as f:
                json.dump(self.feature_importance, f, indent=2)
        except Exception:
            pass
    
    def load_ml_model(self) -> bool:
        """Carrega modelo ML salvo"""
        try:
            with open('models/priority_model.pkl', 'rb') as f:
                self.ml_model = pickle.load(f)
                
            with open('models/priority_scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
                
            # Tentar carregar de reports_ml primeiro, depois models
            feature_file = None
            for path in ['../reports_ml/feature_importance.json', 'models/feature_importance.json']:
                if os.path.exists(path):
                    feature_file = path
                    break
            
            if feature_file:
                with open(feature_file, 'r') as f:
                    self.feature_importance = json.load(f)
                
            self.model_trained = True
            return True
        except Exception:
            return False
    
    def _calculate_failure_score(self, test_case: TestCase) -> float:
        """Calcula score baseado no histórico de falhas"""
        if test_case.failure_count == 0:
            return 0.1  # Score baixo para testes que nunca falharam
        
        # Score baseado na frequência de falhas
        failure_frequency = min(test_case.failure_count / 10.0, 1.0)
        
        # Score baseado na recência da última falha
        recency_score = 0.5  # Default
        if test_case.last_failure:
            try:
                last_failure_date = datetime.fromisoformat(test_case.last_failure)
                days_since_failure = (datetime.now() - last_failure_date).days
                recency_score = 1.0 / (1.0 + days_since_failure / 7.0)  # Decay por semana
            except:
                pass
        
        return (failure_frequency + recency_score) / 2.0
    
    def _calculate_change_impact_score(self, test_case: TestCase, 
                                     recent_changes: List[str]) -> float:
        """Calcula score baseado no impacto de mudanças recentes"""
        if not recent_changes:
            return 0.1
        
        # Verificar se o teste ou suas dependências foram afetadas
        impact_score = 0.0
        
        # Impacto direto - arquivo do teste foi modificado
        if test_case.file_path in recent_changes:
            impact_score += 0.8
        
        # Impacto indireto - dependências foram modificadas
        if test_case.dependencies:
            for dependency in test_case.dependencies:
                if any(dependency in change for change in recent_changes):
                    impact_score += 0.3
        
        # Impacto por tipo de mudança
        critical_patterns = ['auth', 'security', 'payment', 'database']
        for change in recent_changes:
            if any(pattern in change.lower() for pattern in critical_patterns):
                impact_score += 0.2
        
        return min(impact_score, 1.0)
    
    def prioritize_tests(self, test_cases: List[TestCase], 
                        recent_changes: List[str] = None,
                        time_budget: int = None) -> List[TestPriority]:
        """Prioriza lista de test cases"""
        
        priorities = []
        
        for test_case in test_cases:
            score = self.calculate_priority_score(test_case, recent_changes)
            risk_level = self._determine_risk_level(score)
            reasoning = self._generate_reasoning(test_case, score, recent_changes)
            frequency = self._recommend_frequency(score, test_case.test_type)
            
            priority = TestPriority(
                test_case=test_case,
                priority_score=score,
                risk_level=risk_level,
                reasoning=reasoning,
                recommended_frequency=frequency
            )
            
            priorities.append(priority)
        
        # Ordenar por score de prioridade
        priorities.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Se há budget de tempo, otimizar seleção
        if time_budget:
            priorities = self._optimize_for_time_budget(priorities, time_budget)
        
        return priorities
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determina nível de risco baseado no score"""
        for threshold, level in self.config.risk_thresholds:
            if score >= threshold:
                return level
        return RiskLevel.LOW # Fallback
    
    def _generate_reasoning(self, test_case: TestCase, score: float, 
                          recent_changes: List[str]) -> List[str]:
        """Gera explicação para a priorização"""
        reasoning = []
        if test_case.failure_count > 5:
            reasoning.append(f"High failure rate: {test_case.failure_count} recent failures")
        
        if test_case.business_impact in ['CRITICAL', 'HIGH']:
            reasoning.append(f"High business impact: {test_case.business_impact}")
        
        if test_case.code_coverage > 80:
            reasoning.append(f"High code coverage: {test_case.code_coverage}%")
        
        if recent_changes and test_case.file_path in recent_changes:
            reasoning.append("Test file recently modified")
        
        if test_case.test_type in ['SECURITY', 'API']:
            reasoning.append(f"Critical test type: {test_case.test_type}")
        
        if test_case.execution_time < 30:  # Menos de 30 segundos
            reasoning.append("Fast execution time")
        
        if score >= 0.8:
            reasoning.append("URGENT: Run immediately")
        elif score >= 0.6:
            reasoning.append("HIGH PRIORITY: Run in next cycle")
        
        return reasoning
    
    def _recommend_frequency(self, score: float, test_type: str) -> ExecutionFrequency:
        """Recomenda frequência de execução"""
        if score >= 0.8:
            return ExecutionFrequency.EVERY_COMMIT
        elif score >= 0.6:
            return ExecutionFrequency.EVERY_BUILD
        elif score >= 0.4:
            return ExecutionFrequency.DAILY
        elif test_type == "UNIT":
            return ExecutionFrequency.EVERY_BUILD  # Unit tests sempre frequentes
        else:
            return ExecutionFrequency.WEEKLY
    
    def _optimize_for_time_budget(self, priorities: List[TestPriority], 
                                 time_budget: int) -> List[TestPriority]:
        """Otimiza seleção de testes para budget de tempo"""
        selected = []
        total_time = 0
        
        # Algoritmo greedy: selecionar testes com melhor ratio score/tempo
        remaining = priorities.copy()
        remaining.sort(key=lambda x: x.priority_score / max(x.test_case.execution_time, 1), 
                      reverse=True)
        
        for priority in remaining:
            if total_time + priority.test_case.execution_time <= time_budget:
                selected.append(priority)
                total_time += priority.test_case.execution_time
        
        return selected
    
    def generate_execution_plan(self, priorities: List[TestPriority]) -> Dict[str, Any]:
        """Gera plano de execução otimizado com ML insights"""
        
        # Agrupar por nível de risco
        by_risk = defaultdict(list)
        for priority in priorities:
            by_risk[priority.risk_level.value].append(priority)
        
        # Calcular estatísticas
        total_tests = len(priorities)
        total_time = sum(p.test_case.execution_time for p in priorities)
        
        # ML-powered optimizations
        ml_insights = self._generate_ml_insights(priorities)
        optimal_sequence = self._optimize_test_sequence(priorities)
        
        plan = {
            'summary': {
                'total_tests': total_tests,
                'estimated_time_minutes': total_time / 60,
                'ml_model_active': self.model_trained,
                'optimization_score': self._calculate_optimization_score(priorities)
            },
            'ml_insights': ml_insights,
            'optimal_sequence': optimal_sequence,
            'execution_phases': self._generate_smart_phases(by_risk),
            'advanced_recommendations': self._generate_plan_recommendations(priorities),
            'performance_predictions': self._predict_execution_performance(priorities)
        }
        
        return plan
    
    def _generate_ml_insights(self, priorities: List[TestPriority]) -> Dict[str, Any]:
        """Gera insights usando ML"""
        insights = {
            'feature_importance': self.feature_importance if self.model_trained else {},
            'priority_distribution': self._analyze_priority_distribution(priorities),
            'risk_patterns': self._identify_risk_patterns(priorities),
            'optimization_opportunities': self._find_optimization_opportunities(priorities)
        }
        
        return insights
    
    def _optimize_test_sequence(self, priorities: List[TestPriority]) -> List[Dict[str, Any]]:
        """Otimiza sequência de execução usando algoritmo genético simplificado"""
        if not priorities:
            return []
        
        # Ordenar por score/tempo ratio para otimização greedy
        sorted_tests = sorted(priorities, 
                            key=lambda p: p.priority_score / max(p.test_case.execution_time, 1), 
                            reverse=True)
        
        sequence = []
        for i, priority in enumerate(sorted_tests[:10]):  # Top 10 para demonstração
            sequence.append({
                'position': i + 1,
                'test_name': priority.test_case.name,
                'priority_score': priority.priority_score,
                'efficiency_ratio': priority.priority_score / max(priority.test_case.execution_time, 1),
                'estimated_start_time': sum(p.test_case.execution_time for p in sorted_tests[:i])
            })
        
        return sequence
    
    def _generate_smart_phases(self, by_risk: Dict[str, List[TestPriority]]) -> Dict[str, Any]:
        """Gera fases inteligentes de execução"""
        phases = {}
        
        # Fase crítica com paralelização
        critical_tests = by_risk.get('CRITICAL', [])
        if critical_tests:
            fast_critical = [p for p in critical_tests if p.test_case.execution_time < 60]
            slow_critical = [p for p in critical_tests if p.test_case.execution_time >= 60]
            
            phases['phase_1_critical'] = {
                'parallel_batch_1': [p.test_case.name for p in fast_critical],
                'sequential_batch': [p.test_case.name for p in slow_critical],
                'estimated_time': max(
                    sum(p.test_case.execution_time for p in fast_critical) / min(len(fast_critical), 4),
                    sum(p.test_case.execution_time for p in slow_critical)
                ) / 60 if critical_tests else 0,
                'parallelization_factor': min(len(fast_critical), 4)
            }
        
        return phases
    
    def _analyze_priority_distribution(self, priorities: List[TestPriority]) -> Dict[str, float]:
        """Analisa distribuição de prioridades"""
        scores = [p.priority_score for p in priorities]
        if not scores:
            return {}
        
        return {
            'mean_priority': np.mean(scores),
            'std_priority': np.std(scores),
            'high_priority_ratio': len([s for s in scores if s > 0.7]) / len(scores),
            'low_priority_ratio': len([s for s in scores if s < 0.3]) / len(scores)
        }
    
    def _identify_risk_patterns(self, priorities: List[TestPriority]) -> List[Dict[str, Any]]:
        """Identifica padrões de risco"""
        patterns = []
        
        # Agrupar por tipo de teste
        by_type = defaultdict(list)
        for p in priorities:
            by_type[p.test_case.test_type].append(p)
        
        for test_type, tests in by_type.items():
            avg_score = np.mean([t.priority_score for t in tests])
            if avg_score > 0.7:
                patterns.append({
                    'pattern_type': 'HIGH_RISK_TEST_TYPE',
                    'test_type': test_type,
                    'average_score': avg_score,
                    'test_count': len(tests),
                    'recommendation': f'Focus on {test_type} test stability'
                })
        
        return patterns
    
    def _find_optimization_opportunities(self, priorities: List[TestPriority]) -> List[Dict[str, str]]:
        """Encontra oportunidades de otimização"""
        opportunities = []
        
        # Testes lentos com baixa prioridade
        slow_low_priority = [p for p in priorities 
                           if p.test_case.execution_time > 300 and p.priority_score < 0.4]
        
        if slow_low_priority:
            opportunities.append({
                'type': 'SLOW_LOW_PRIORITY',
                'description': f'{len(slow_low_priority)} slow tests with low priority',
                'action': 'Consider optimizing or reducing frequency'
            })
        
        # Testes com alta taxa de falha
        flaky_tests = [p for p in priorities if p.test_case.failure_count > 5]
        if flaky_tests:
            opportunities.append({
                'type': 'FLAKY_TESTS',
                'description': f'{len(flaky_tests)} tests with high failure rate',
                'action': 'Investigate and stabilize flaky tests'
            })
        
        return opportunities
    
    def _calculate_optimization_score(self, priorities: List[TestPriority]) -> float:
        """Calcula score de otimização do plano"""
        if not priorities:
            return 0.0
        
        # Fatores de otimização
        total_time = sum(p.test_case.execution_time for p in priorities)
        avg_priority = np.mean([p.priority_score for p in priorities])
        
        # Score baseado em eficiência (alta prioridade / baixo tempo)
        efficiency_scores = [p.priority_score / max(p.test_case.execution_time, 1) for p in priorities]
        avg_efficiency = np.mean(efficiency_scores)
        
        # Normalizar e combinar
        time_factor = max(0, 1 - (total_time / 3600))  # Penalizar se > 1 hora
        priority_factor = avg_priority
        efficiency_factor = min(avg_efficiency / 0.01, 1.0)  # Normalizar
        
        return (time_factor * 0.3 + priority_factor * 0.4 + efficiency_factor * 0.3)
    
    def _predict_execution_performance(self, priorities: List[TestPriority]) -> Dict[str, Any]:
        """Prediz performance da execução"""
        if not priorities:
            return {}
        
        total_time = sum(p.test_case.execution_time for p in priorities)
        high_risk_tests = [p for p in priorities if p.priority_score > 0.7]
        
        # Predições baseadas em heurísticas
        predictions = {
            'estimated_total_time_minutes': total_time / 60,
            'parallel_execution_time_minutes': total_time / min(len(priorities), 8) / 60,
            'expected_failures': len([p for p in priorities if p.test_case.failure_count > 2]),
            'success_probability': max(0.5, 1.0 - (len(high_risk_tests) / len(priorities) * 0.3)),
            'bottleneck_tests': [p.test_case.name for p in priorities if p.test_case.execution_time > 300][:3]
        }
        
        return predictions
    
    def _generate_plan_recommendations(self, priorities: List[TestPriority]) -> List[str]:
        """Gera recomendações para o plano de execução"""
        recommendations = []
        
        critical_count = len([p for p in priorities if p.risk_level == RiskLevel.CRITICAL])
        if critical_count > 10:
            recommendations.append(f"High number of critical tests ({critical_count}) - consider code quality review")
        
        slow_tests = [p for p in priorities if p.test_case.execution_time > 300]  # > 5 min
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow tests for better CI performance")
        
        security_tests = [p for p in priorities if p.test_case.test_type == 'SECURITY']
        if security_tests:
            recommendations.append(f"Prioritize {len(security_tests)} security tests in every build")
        
        return recommendations
    
    def _identify_risk_areas(self, priorities: List[TestPriority]) -> List[str]:
        """Identifica áreas de risco baseado nos testes"""
        risk_areas = []
        
        # Agrupar por tipo de teste
        by_type = defaultdict(list)
        for priority in priorities:
            by_type[priority.test_case.test_type].append(priority)
        
        # Identificar tipos com muitos testes de alta prioridade
        for test_type, tests in by_type.items():
            high_priority = [t for t in tests if t.priority_score > 0.6]
            if len(high_priority) > len(tests) * 0.5:  # Mais de 50% são alta prioridade
                risk_areas.append(f"{test_type} tests show high risk patterns")
        
        return risk_areas
    
    def _suggest_improvements(self, priorities: List[TestPriority]) -> List[str]:
        """Sugere melhorias baseado na análise"""
        suggestions = []
        
        # Testes com baixa cobertura mas alta prioridade
        low_coverage_high_priority = [
            p for p in priorities 
            if p.priority_score > 0.6 and p.test_case.code_coverage < 50
        ]
        
        if low_coverage_high_priority:
            suggestions.append("Improve code coverage for high-priority test areas")
        
        # Testes com muitas falhas
        flaky_tests = [p for p in priorities if p.test_case.failure_count > 3]
        if flaky_tests:
            suggestions.append(f"Investigate and fix {len(flaky_tests)} flaky tests")
        
        return suggestions
    
    def get_ml_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do modelo ML"""
        return {
            'model_trained': self.model_trained,
            'feature_importance': self.feature_importance,
            'historical_data_points': sum(len(perf) for perf in self.historical_performance.values()),
            'model_accuracy': self.ml_model.score if self.model_trained else 0.0,
            'last_training': datetime.now().isoformat() if self.model_trained else None
        }
    
    def update_performance_history(self, test_name: str, actual_priority: float):
        """Atualiza histórico de performance para aprendizado contínuo"""
        self.historical_performance[test_name].append(actual_priority)
        # Manter apenas últimas 50 execuções
        if len(self.historical_performance[test_name]) > 50:
            self.historical_performance[test_name] = self.historical_performance[test_name][-50:]

def main():
    """Exemplo avançado do Smart Test Prioritizer com ML"""
    prioritizer = SmartTestPrioritizer(Config())
    
    # Tentar carregar modelo ML
    if prioritizer.load_ml_model():
        print("[SUCCESS] ML model loaded successfully")
    else:
        print("[WARNING] No pre-trained model found, using traditional methods")
    
    # Criar test cases mais diversos
    sample_tests = [
        TestCase(name="test_user_authentication", file_path="test_auth.py", test_type="SECURITY", execution_time=45.0, failure_count=2, code_coverage=85.0, business_impact=BusinessImpact.CRITICAL),
        TestCase(name="test_payment_processing", file_path="test_payment.py", test_type="API", execution_time=120.0, failure_count=0, code_coverage=92.0, business_impact=BusinessImpact.CRITICAL),
        TestCase(name="test_user_profile_update", file_path="test_profile.py", test_type="UNIT", execution_time=15.0, failure_count=1, code_coverage=78.0, business_impact=BusinessImpact.MEDIUM),
        TestCase(name="test_database_connection", file_path="test_db.py", test_type="DATABASE", execution_time=200.0, failure_count=5, code_coverage=65.0, business_impact=BusinessImpact.HIGH),
        TestCase(name="test_ui_navigation", file_path="test_ui.py", test_type="UI", execution_time=300.0, failure_count=3, code_coverage=45.0, business_impact=BusinessImpact.LOW),
        TestCase(name="test_integration_flow", file_path="test_integration.py", test_type="INTEGRATION", execution_time=180.0, failure_count=1, code_coverage=88.0, business_impact=BusinessImpact.HIGH)
    ]
    
    recent_changes = ["test_auth.py", "auth_service.py", "payment_service.py"]
    
    print("Prioritizing tests with ML-enhanced algorithm...")
    priorities = prioritizer.prioritize_tests(sample_tests, recent_changes)
    
    print("\nTest Priority Results:")
    for i, priority in enumerate(priorities[:5], 1):
        print(f"{i}. {priority.test_case.name} | Score: {priority.priority_score:.3f} | Risk: {priority.risk_level.value}")
    
    # Demonstrar treinamento ML
    print("\nTraining ML model with sample data...")
    training_data = []
    for test_case in sample_tests:
        # Simular dados históricos de prioridade
        actual_priority = 0.8 if test_case.business_impact == BusinessImpact.CRITICAL else 0.6 if test_case.business_impact == BusinessImpact.HIGH else 0.4
        training_data.append({
            'test_case': test_case,
            'actual_priority': actual_priority + (test_case.failure_count * 0.05),  # Ajustar por falhas
            'recent_changes': recent_changes
        })
    
    # Adicionar mais dados sintéticos
    for i in range(15):
        synthetic_test = TestCase(
            name=f"synthetic_test_{i}",
            file_path=f"test_synthetic_{i}.py",
            test_type=np.random.choice(['UNIT', 'API', 'INTEGRATION']),
            execution_time=np.random.uniform(10, 300),
            failure_count=np.random.randint(0, 8),
            code_coverage=np.random.uniform(40, 95),
            business_impact=np.random.choice(list(BusinessImpact))
        )
        training_data.append({
            'test_case': synthetic_test,
            'actual_priority': np.random.uniform(0.2, 0.9),
            'recent_changes': []
        })
    
    training_result = prioritizer.train_ml_model(training_data)
    if training_result.get('success'):
        print(f"[SUCCESS] ML model trained! R² Score: {training_result.get('r2_score', 0):.3f}")
        print(f"Feature Importance: {list(training_result.get('feature_importance', {}).keys())[:3]}")
    
    # Gerar plano avançado
    print("\nGenerating ML-enhanced execution plan...")
    plan = prioritizer.generate_execution_plan(priorities)
    
    print(f"\nExecution Plan Summary:")
    if 'summary' in plan:
        summary = plan['summary']
        print(f"  • Total Tests: {summary.get('total_tests', 0)}")
        print(f"  • Estimated Time: {summary.get('estimated_time_minutes', 0):.1f} minutes")
        print(f"  • ML Model Active: {summary.get('ml_model_active', False)}")
        print(f"  • Optimization Score: {summary.get('optimization_score', 0):.3f}")
    
    if 'ml_insights' in plan and plan['ml_insights']:
        ml_insights = plan['ml_insights']
        print(f"\nML Insights:")
        if 'priority_distribution' in ml_insights:
            dist = ml_insights['priority_distribution']
            print(f"  • Mean Priority: {dist.get('mean_priority', 0):.3f}")
            print(f"  • High Priority Ratio: {dist.get('high_priority_ratio', 0):.1%}")

if __name__ == "__main__":
    main()