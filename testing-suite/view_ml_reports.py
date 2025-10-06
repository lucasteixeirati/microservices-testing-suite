#!/usr/bin/env python3
"""
ML Reports Viewer
Visualiza relatórios JSON de forma organizada
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

def list_reports():
    """Lista todos os relatórios disponíveis"""
    reports_dir = "reports_ml"
    if not os.path.exists(reports_dir):
        print("❌ Pasta reports_ml não encontrada")
        return []
    
    files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
    files.sort(reverse=True)  # Mais recentes primeiro
    
    print(f"📊 {len(files)} relatórios encontrados:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    return files

def format_json_pretty(data: Dict[str, Any], indent: int = 0) -> str:
    """Formata JSON de forma legível"""
    result = ""
    spacing = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result += f"{spacing}📋 {key}:\n"
                result += format_json_pretty(value, indent + 1)
            else:
                # Formatação especial para valores importantes
                if key in ['success', 'model_trained']:
                    emoji = "✅" if value else "❌"
                    result += f"{spacing}{emoji} {key}: {value}\n"
                elif key in ['priority', 'risk_level']:
                    emoji = "🔴" if value == 'CRITICAL' else "🟡" if value == 'HIGH' else "🟢"
                    result += f"{spacing}{emoji} {key}: {value}\n"
                elif 'score' in key or 'accuracy' in key:
                    result += f"{spacing}📈 {key}: {value}\n"
                elif 'time' in key:
                    result += f"{spacing}⏱️ {key}: {value}\n"
                else:
                    result += f"{spacing}• {key}: {value}\n"
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            result += f"{spacing}[{i+1}] "
            if isinstance(item, dict):
                result += "\n" + format_json_pretty(item, indent + 1)
            else:
                result += f"{item}\n"
    
    return result

def view_report(filename: str):
    """Visualiza um relatório específico"""
    filepath = os.path.join("reports_ml", filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO: {filename}")
        print(f"{'='*60}")
        
        # Timestamp
        if 'timestamp' in data:
            print(f"🕐 Gerado em: {data['timestamp']}")
        
        # Resumo executivo
        print(f"\n🎯 RESUMO EXECUTIVO:")
        summary_items = []
        
        for section, content in data.items():
            if isinstance(content, dict) and content.get('success'):
                if section == 'test_generation':
                    count = content.get('total_tests_generated', 0)
                    summary_items.append(f"✅ Geração de Testes: {count} testes")
                elif section == 'bug_analysis':
                    count = content.get('logs_analyzed', 0)
                    summary_items.append(f"✅ Análise de Bugs: {count} logs")
                elif section == 'test_prioritization':
                    count = content.get('tests_prioritized', 0)
                    summary_items.append(f"✅ Priorização: {count} testes")
                elif section == 'failure_prediction':
                    count = content.get('high_risk_tests', 0)
                    summary_items.append(f"✅ Predição: {count} testes de risco")
        
        for item in summary_items:
            print(f"  {item}")
        
        # Recomendações (se existirem)
        if 'recommendations' in data and data['recommendations']:
            print(f"\n🔝 TOP RECOMENDAÇÕES:")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                priority_emoji = "🔴" if rec.get('priority') == 'CRITICAL' else "🟡" if rec.get('priority') == 'HIGH' else "🟢"
                print(f"  {i}. {priority_emoji} {rec.get('title', 'N/A')}")
                print(f"     Ação: {rec.get('action', 'N/A')}")
        
        # Detalhes completos
        print(f"\n📋 DETALHES COMPLETOS:")
        print(format_json_pretty(data))
        
    except Exception as e:
        print(f"❌ Erro ao ler relatório: {e}")

def interactive_viewer():
    """Interface interativa para visualizar relatórios"""
    while True:
        print(f"\n{'='*60}")
        print("🤖 ML REPORTS VIEWER")
        print(f"{'='*60}")
        
        files = list_reports()
        if not files:
            break
        
        print(f"\nOpções:")
        print(f"0. Sair")
        print(f"A. Ver todos os relatórios")
        
        choice = input(f"\nEscolha um relatório (0-{len(files)}) ou 'A': ").strip()
        
        if choice == '0':
            break
        elif choice.upper() == 'A':
            for file in files:
                view_report(file)
                input("\nPressione Enter para continuar...")
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(files):
                    view_report(files[index])
                    input("\nPressione Enter para continuar...")
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Entrada inválida")

def main():
    """Função principal"""
    print("🚀 Iniciando ML Reports Viewer...")
    interactive_viewer()
    print("👋 Obrigado por usar o ML Reports Viewer!")

if __name__ == "__main__":
    main()