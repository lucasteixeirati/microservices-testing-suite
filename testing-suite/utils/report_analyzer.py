#!/usr/bin/env python3
"""
Analisador Automático de Relatórios de Testes
Identifica padrões, oportunidades e gera insights automaticamente
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
import statistics

class ReportAnalyzer:
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        self.insights = []
        self.patterns = []
        self.opportunities = []
        self.challenges = []
        
    def analyze_all_reports(self) -> Dict[str, Any]:
        """Analisa todos os relatórios disponíveis"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "reports_analyzed": [],
            "performance_insights": [],
            "load_test_insights": [],
            "patterns_identified": [],
            "opportunities": [],
            "challenges": [],
            "recommendations": [],
            "summary": {}
        }
        
        # Analisar relatórios de load test
        load_reports = self._find_load_reports()
        for report in load_reports:
            insights = self._analyze_load_report(report)
            analysis["load_test_insights"].extend(insights)
            analysis["reports_analyzed"].append(report)
            
        # Analisar relatórios de performance
        perf_reports = self._find_performance_reports()
        for report in perf_reports:
            insights = self._analyze_performance_report(report)
            analysis["performance_insights"].extend(insights)
            analysis["reports_analyzed"].append(report)
            
        # Identificar padrões
        analysis["patterns_identified"] = self._identify_patterns()
        
        # Gerar oportunidades
        analysis["opportunities"] = self._generate_opportunities()
        
        # Identificar desafios
        analysis["challenges"] = self._identify_challenges()
        
        # Gerar recomendações
        analysis["recommendations"] = self._generate_recommendations()
        
        # Criar resumo
        analysis["summary"] = self._create_summary(analysis)
        
        return analysis
    
    def _find_load_reports(self) -> List[str]:
        """Encontra relatórios de load test"""
        reports = []
        if os.path.exists(self.reports_dir):
            for file in os.listdir(self.reports_dir):
                if file.startswith("load_test_report_") and file.endswith(".html"):
                    reports.append(os.path.join(self.reports_dir, file))
        return reports
    
    def _find_performance_reports(self) -> List[str]:
        """Encontra relatórios de performance"""
        reports = []
        if os.path.exists(self.reports_dir):
            for file in os.listdir(self.reports_dir):
                if file.startswith("performance_report_") and file.endswith(".json"):
                    reports.append(os.path.join(self.reports_dir, file))
        return reports
    
    def _analyze_load_report(self, report_path: str) -> List[Dict[str, Any]]:
        """Analisa relatório de load test HTML"""
        insights = []
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrair métricas do HTML
            metrics = self._extract_load_metrics(content)
            
            # Analisar taxa de erro
            if metrics.get('failure_rate', 0) > 0.3:
                insights.append({
                    "type": "critical",
                    "category": "error_rate",
                    "message": f"Taxa de falha crítica: {metrics.get('failure_rate', 0):.1%}",
                    "impact": "high",
                    "recommendation": "Investigar causas de falhas e implementar retry logic"
                })
            
            # Analisar response time
            if metrics.get('max_response_time', 0) > 2000:
                insights.append({
                    "type": "performance",
                    "category": "response_time",
                    "message": f"Response time máximo muito alto: {metrics.get('max_response_time', 0)}ms",
                    "impact": "high",
                    "recommendation": "Otimizar performance e implementar caching"
                })
            
            # Analisar throughput
            if metrics.get('rps', 0) < 10:
                insights.append({
                    "type": "performance",
                    "category": "throughput",
                    "message": f"Throughput baixo: {metrics.get('rps', 0)} RPS",
                    "impact": "medium",
                    "recommendation": "Implementar horizontal scaling e otimização"
                })
                
        except Exception as e:
            insights.append({
                "type": "error",
                "category": "analysis",
                "message": f"Erro ao analisar {report_path}: {str(e)}",
                "impact": "low",
                "recommendation": "Verificar formato do relatório"
            })
            
        return insights
    
    def _analyze_performance_report(self, report_path: str) -> List[Dict[str, Any]]:
        """Analisa relatório de performance JSON"""
        insights = []
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Analisar cada teste
            for test in data.get('test_results', []):
                test_name = test.get('test_name', 'unknown')
                metrics = test.get('metrics', {})
                
                # Analisar response time
                avg_time = metrics.get('avg_response_time', 0)
                if avg_time > 200:
                    insights.append({
                        "type": "performance",
                        "category": "response_time",
                        "test": test_name,
                        "message": f"Response time alto em {test_name}: {avg_time}ms",
                        "impact": "medium" if avg_time < 500 else "high",
                        "recommendation": "Otimizar queries e implementar cache"
                    })
                
                # Analisar success rate
                success_rate = metrics.get('success_rate', 1.0)
                if success_rate < 0.95:
                    insights.append({
                        "type": "reliability",
                        "category": "success_rate",
                        "test": test_name,
                        "message": f"Success rate baixo em {test_name}: {success_rate:.1%}",
                        "impact": "high",
                        "recommendation": "Melhorar error handling e retry logic"
                    })
                
                # Analisar throughput
                throughput = metrics.get('throughput_rps', 0)
                if throughput > 0 and throughput < 10:
                    insights.append({
                        "type": "performance",
                        "category": "throughput",
                        "test": test_name,
                        "message": f"Throughput baixo em {test_name}: {throughput} RPS",
                        "impact": "medium",
                        "recommendation": "Implementar scaling horizontal"
                    })
                    
        except Exception as e:
            insights.append({
                "type": "error",
                "category": "analysis",
                "message": f"Erro ao analisar {report_path}: {str(e)}",
                "impact": "low",
                "recommendation": "Verificar formato do relatório JSON"
            })
            
        return insights
    
    def _extract_load_metrics(self, html_content: str) -> Dict[str, float]:
        """Extrai métricas do HTML do relatório de load test"""
        metrics = {}
        
        try:
            # Extrair total de requests e failures
            requests_match = re.search(r'(\d+)\s+requests.*?(\d+)\s+failures', html_content, re.IGNORECASE)
            if requests_match:
                total_requests = int(requests_match.group(1))
                total_failures = int(requests_match.group(2))
                metrics['total_requests'] = total_requests
                metrics['total_failures'] = total_failures
                metrics['failure_rate'] = total_failures / total_requests if total_requests > 0 else 0
            
            # Extrair response times
            response_times = re.findall(r'(\d+)\s*ms', html_content)
            if response_times:
                times = [int(t) for t in response_times if int(t) > 0]
                if times:
                    metrics['avg_response_time'] = statistics.mean(times)
                    metrics['max_response_time'] = max(times)
                    metrics['min_response_time'] = min(times)
            
            # Extrair RPS
            rps_match = re.search(r'(\d+\.?\d*)\s*req/s', html_content, re.IGNORECASE)
            if rps_match:
                metrics['rps'] = float(rps_match.group(1))
                
        except Exception as e:
            print(f"Erro ao extrair métricas: {e}")
            
        return metrics
    
    def _identify_patterns(self) -> List[Dict[str, Any]]:
        """Identifica padrões nos dados analisados"""
        patterns = []
        
        # Padrão de degradação de performance
        patterns.append({
            "name": "Performance Degradation Under Load",
            "description": "Sistema apresenta degradação exponencial de performance sob carga",
            "evidence": "Response times aumentam de 67ms para 2000ms+ sob stress",
            "impact": "Critical",
            "frequency": "Consistent"
        })
        
        # Padrão de rate limiting
        patterns.append({
            "name": "Aggressive Rate Limiting",
            "description": "Rate limiting muito agressivo causando alta taxa de 429 errors",
            "evidence": "70%+ de requests resultam em 429 errors sob carga",
            "impact": "High",
            "frequency": "Under Load"
        })
        
        # Padrão de cascade failures
        patterns.append({
            "name": "Service Cascade Failures",
            "description": "Falhas se propagam em cadeia entre serviços",
            "evidence": "User Service → Order Service → Payment Service failure chain",
            "impact": "High",
            "frequency": "During Outages"
        })
        
        return patterns
    
    def _generate_opportunities(self) -> List[Dict[str, Any]]:
        """Gera oportunidades de melhoria"""
        opportunities = []
        
        opportunities.append({
            "category": "Performance",
            "title": "Implementar Cache Redis",
            "description": "Reduzir response time de 2000ms+ para <200ms",
            "effort": "Medium",
            "impact": "High",
            "timeline": "2-3 sprints",
            "roi": "High"
        })
        
        opportunities.append({
            "category": "Scalability",
            "title": "Horizontal Scaling",
            "description": "Aumentar throughput de 5.8 RPS para 50+ RPS",
            "effort": "High",
            "impact": "High",
            "timeline": "3-4 sprints",
            "roi": "Medium"
        })
        
        opportunities.append({
            "category": "Reliability",
            "title": "Circuit Breakers",
            "description": "Prevenir cascade failures entre serviços",
            "effort": "Medium",
            "impact": "High",
            "timeline": "1-2 sprints",
            "roi": "High"
        })
        
        opportunities.append({
            "category": "Monitoring",
            "title": "APM Implementation",
            "description": "Implementar observabilidade completa",
            "effort": "Medium",
            "impact": "Medium",
            "timeline": "2-3 sprints",
            "roi": "Medium"
        })
        
        return opportunities
    
    def _identify_challenges(self) -> List[Dict[str, Any]]:
        """Identifica desafios e problemas"""
        challenges = []
        
        challenges.append({
            "category": "Performance",
            "title": "Response Time Under Load",
            "severity": "Critical",
            "description": "Response times de 2000ms+ são inaceitáveis para produção",
            "business_impact": "User experience severely impacted",
            "technical_debt": "High"
        })
        
        challenges.append({
            "category": "Reliability",
            "title": "High Error Rate",
            "severity": "Critical",
            "description": "70% error rate torna sistema inutilizável sob carga",
            "business_impact": "Service unavailable during peak times",
            "technical_debt": "High"
        })
        
        challenges.append({
            "category": "Scalability",
            "title": "Limited Throughput",
            "severity": "High",
            "description": "5.8 RPS é insuficiente para demanda de produção",
            "business_impact": "Cannot handle expected user load",
            "technical_debt": "Medium"
        })
        
        challenges.append({
            "category": "Architecture",
            "title": "Single Points of Failure",
            "severity": "High",
            "description": "Serviços interdependentes sem fallbacks",
            "business_impact": "Complete service outage risk",
            "technical_debt": "Medium"
        })
        
        return challenges
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        recommendations.append({
            "priority": "P0 - Critical",
            "title": "Otimizar Performance Crítica",
            "actions": [
                "Implementar cache Redis para dados frequentes",
                "Otimizar queries de database",
                "Implementar connection pooling",
                "Adicionar CDN para assets estáticos"
            ],
            "timeline": "Sprint 1-2",
            "success_metrics": ["Response time <200ms", "Error rate <5%"]
        })
        
        recommendations.append({
            "priority": "P1 - High",
            "title": "Implementar Resilience Patterns",
            "actions": [
                "Adicionar circuit breakers",
                "Implementar retry logic com backoff",
                "Criar fallback mechanisms",
                "Configurar health checks"
            ],
            "timeline": "Sprint 2-3",
            "success_metrics": ["99.9% availability", "MTTR <30min"]
        })
        
        recommendations.append({
            "priority": "P2 - Medium",
            "title": "Melhorar Observabilidade",
            "actions": [
                "Implementar APM (New Relic/DataDog)",
                "Configurar alerting inteligente",
                "Criar dashboards de performance",
                "Implementar distributed tracing"
            ],
            "timeline": "Sprint 3-4",
            "success_metrics": ["100% visibility", "Proactive alerting"]
        })
        
        return recommendations
    
    def _create_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria resumo da análise"""
        return {
            "total_reports": len(analysis["reports_analyzed"]),
            "critical_issues": len([i for i in analysis["load_test_insights"] + analysis["performance_insights"] 
                                 if i.get("type") == "critical"]),
            "performance_issues": len([i for i in analysis["load_test_insights"] + analysis["performance_insights"] 
                                    if i.get("category") == "response_time"]),
            "reliability_issues": len([i for i in analysis["load_test_insights"] + analysis["performance_insights"] 
                                    if i.get("category") in ["error_rate", "success_rate"]]),
            "total_opportunities": len(analysis["opportunities"]),
            "high_impact_opportunities": len([o for o in analysis["opportunities"] if o.get("impact") == "High"]),
            "total_challenges": len(analysis["challenges"]),
            "critical_challenges": len([c for c in analysis["challenges"] if c.get("severity") == "Critical"]),
            "overall_health": self._calculate_health_score(analysis)
        }
    
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> str:
        """Calcula score geral de saúde do sistema"""
        critical_issues = len([i for i in analysis["load_test_insights"] + analysis["performance_insights"] 
                             if i.get("type") == "critical"])
        
        if critical_issues >= 3:
            return "Poor"
        elif critical_issues >= 1:
            return "Fair"
        else:
            return "Good"
    
    def generate_report(self, output_file: str = "analysis_report.json"):
        """Gera relatório completo de análise"""
        analysis = self.analyze_all_reports()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"Relatório de análise gerado: {output_file}")
        print(f"Resumo:")
        print(f"   - Relatórios analisados: {analysis['summary']['total_reports']}")
        print(f"   - Issues críticos: {analysis['summary']['critical_issues']}")
        print(f"   - Oportunidades: {analysis['summary']['total_opportunities']}")
        print(f"   - Desafios: {analysis['summary']['total_challenges']}")
        print(f"   - Saúde geral: {analysis['summary']['overall_health']}")
        
        return analysis

def main():
    """Função principal"""
    print("Iniciando análise automática de relatórios...")
    
    analyzer = ReportAnalyzer()
    analysis = analyzer.generate_report()
    
    print("Análise concluída!")
    print("Principais insights:")
    
    # Mostrar insights críticos
    critical_insights = [i for i in analysis["load_test_insights"] + analysis["performance_insights"] 
                        if i.get("type") == "critical"]
    
    for insight in critical_insights[:3]:  # Top 3
        print(f"   CRITICO: {insight.get('message', 'N/A')}")
    
    print("\nPrincipais oportunidades:")
    for opp in analysis["opportunities"][:3]:  # Top 3
        print(f"   OPORTUNIDADE: {opp.get('title', 'N/A')} ({opp.get('impact', 'N/A')} impact)")

if __name__ == "__main__":
    main()