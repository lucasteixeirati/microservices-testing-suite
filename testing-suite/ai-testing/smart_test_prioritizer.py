#!/usr/bin/env python3
"""
Smart Test Prioritizer
Usa IA para priorizar testes baseado em risco, histórico e impacto
"""

import json
import math
from enum import Enum
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

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

    
    def calculate_priority_score(self, test_case: TestCase, 
                                recent_changes: List[str] = None) -> float:
        """Calcula score de prioridade para um test case"""
        
        # 1. Score baseado no histórico de falhas
        failure_score = self._calculate_failure_score(test_case)
        
        # 2. Score baseado no impacto de negócio
        business_score = self.config.business_impact_scores.get(test_case.business_impact, 0.5)
        
        # 3. Score baseado na cobertura de código
        coverage_score = test_case.code_coverage / 100.0
        
        # 4. Score baseado no tempo de execução (inverso - testes rápidos têm prioridade)
        time_score = 1.0 / (1.0 + test_case.execution_time / 60.0)  # Normalizar por minuto
        
        # 5. Score baseado em mudanças recentes no código
        change_score = self._calculate_change_impact_score(test_case, recent_changes or [])
        
        # 6. Score baseado no tipo de teste
        type_score = self.config.test_type_weights.get(test_case.test_type, 0.5)
        
        # Calcular score final ponderado
        final_score = (
            failure_score * self.config.weight_config['failure_history'] +
            business_score * self.config.weight_config['business_impact'] +
            coverage_score * self.config.weight_config['code_coverage'] +
            time_score * self.config.weight_config['execution_time'] +
            change_score * self.config.weight_config['code_changes']
        ) * type_score
        
        return min(final_score, 1.0)  # Normalizar entre 0 e 1
    
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
        """Gera plano de execução otimizado"""
        
        # Agrupar por nível de risco
        by_risk = defaultdict(list)
        for priority in priorities:
            by_risk[priority.risk_level.value].append(priority)
        
        # Calcular estatísticas
        total_tests = len(priorities)
        total_time = sum(p.test_case.execution_time for p in priorities)
        
        # Gerar plano
        plan = {
            'summary': {
                'total_tests': total_tests,
                'estimated_time_minutes': total_time / 60,
                'critical_tests': len(by_risk[RiskLevel.CRITICAL]),
                'high_priority_tests': len(by_risk[RiskLevel.HIGH])
            },
            'execution_phases': {
                'phase_1_critical': {
                    'tests': [p.test_case.name for p in by_risk[RiskLevel.CRITICAL]],
                    'estimated_time': sum(p.test_case.execution_time for p in by_risk[RiskLevel.CRITICAL]) / 60,
                    'description': 'Must run - critical for release'
                },
                'phase_2_high': {
                    'tests': [p.test_case.name for p in by_risk[RiskLevel.HIGH]],
                    'estimated_time': sum(p.test_case.execution_time for p in by_risk[RiskLevel.HIGH]) / 60,
                    'description': 'Should run - high impact'
                },
                'phase_3_medium': {
                    'tests': [p.test_case.name for p in by_risk[RiskLevel.MEDIUM]],
                    'estimated_time': sum(p.test_case.execution_time for p in by_risk[RiskLevel.MEDIUM]) / 60,
                    'description': 'Can run - medium priority'
                }
            },
            'recommendations': self._generate_plan_recommendations(priorities),
            'risk_analysis': {
                'high_risk_areas': self._identify_risk_areas(priorities),
                'suggested_improvements': self._suggest_improvements(priorities)
            }
        }
        
        return plan
    
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

def main():
    """Exemplo de uso do Smart Test Prioritizer"""
    prioritizer = SmartTestPrioritizer(Config())
    
    # Criar test cases de exemplo
    sample_tests = [
        TestCase(
            name="test_user_authentication",
            file_path="test_auth.py",
            test_type="SECURITY",
            execution_time=45.0,
            failure_count=2,
            code_coverage=85.0,
            business_impact=BusinessImpact.CRITICAL
        ),
        TestCase(
            name="test_payment_processing",
            file_path="test_payment.py", 
            test_type="API",
            execution_time=120.0,
            failure_count=0,
            code_coverage=92.0,
            business_impact=BusinessImpact.CRITICAL
        ),
        TestCase(
            name="test_user_profile_update",
            file_path="test_profile.py",
            test_type="UNIT",
            execution_time=15.0,
            failure_count=1,
            code_coverage=78.0,
            business_impact=BusinessImpact.MEDIUM
        )
    ]
    
    # Simular mudanças recentes
    recent_changes = ["test_auth.py", "auth_service.py"]
    
    print("Prioritizing tests...")
    priorities = prioritizer.prioritize_tests(sample_tests, recent_changes)
    
    for priority in priorities:
        print(f"\nTest: {priority.test_case.name}")
        print(f"Priority Score: {priority.priority_score:.3f}")
        print(f"Risk Level: {priority.risk_level.value}")
        print(f"Frequency: {priority.recommended_frequency.value}")
        print(f"Reasoning: {', '.join(priority.reasoning)}")
    
    # Gerar plano de execução
    plan = prioritizer.generate_execution_plan(priorities)
    print(f"\nExecution Plan:")
    print(json.dumps(plan, indent=2, default=str)) # Add default=str to handle Enums

if __name__ == "__main__":
    main()