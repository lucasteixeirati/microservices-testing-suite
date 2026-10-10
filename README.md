# 🤖 AI-Powered Microservices Testing Suite

[![CI](https://github.com/lucasteixeirati/microservices-testing-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/lucasteixeirati/microservices-testing-suite/actions/workflows/ci.yml)
[![Chaos](https://img.shields.io/badge/Chaos-13%20Tests-orange.svg)](https://github.com/)
[![Stacks](https://img.shields.io/badge/tests-Python%20%7C%20Node.js%20%7C%20Go-blue.svg)](TESTING_GUIDE.md)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://python.org/)
[![AI](https://img.shields.io/badge/AI-Powered-red.svg)](https://github.com/)

**Suite completa de microserviços com IA para desenvolvimento, teste e monitoramento em produção.**

---

## 🎯 **Visão Geral**

Demonstração **enterprise-grade** que combina:
- **3 Microserviços** (Python, Node.js, Go) com arquitetura moderna
- **Testes automatizados** em 8 categorias, com contagem publicada por execução
- **7 Componentes de IA/ML** para testing inteligente
- **13 Testes de Chaos Engineering** para validação de resiliência
- **CI/CD DevSecOps** completo com 3 pipelines

### **🏗️ Arquitetura Simplificada**
```
User Service (Python) ←→ Order Service (Node.js) ←→ Payment Service (Go)
                    ↓
            Istio Service Mesh + Observability
                    ↓
        AI Testing Suite + Chaos Engineering
```

---

## 🚀 **Quick Start**

### **1. Instalação Rápida**
```bash
git clone https://github.com/lucasteixeirati/microservices-testing-suite.git
cd microservices-testing-suite

# Instalar todas as dependências
cd services/user-service && pip install -r requirements.txt && cd ../..
cd services/order-service && npm install && cd ../..
cd services/payment-service && go mod tidy && cd ../..
cd testing-suite && pip install -r requirements.txt && cd ..

# Iniciar todos os serviços
run-local.bat
```

### **2. Executar Testes**
```bash
cd testing-suite

# Todos os testes
python utils/test_runner.py --test-type all

# Componentes de IA
test-all-ml.bat

# Dashboard de IA
python ai-testing/ai_testing_dashboard.py
```

**Pré-requisitos:** Python 3.13, Node.js 18+, Go 1.21+

---

## 📊 **Resultados dos Testes**

Os números não são mantidos manualmente. Cada execução do CI publica resultados JUnit, relatórios HTML e cobertura. A base inclui testes Python, além de testes nativos em Jest/Supertest e Go/`httptest`.

O dashboard visual mais recente é gerado em `docs/evidence/latest-test-dashboard.html`. Consulte [Evidências visuais](docs/evidence/README.md) para reproduzir os relatórios e adicionar capturas da aplicação.

---

## 🤖 **Componentes de IA/ML**

**7 Módulos Funcionais:**
1. **AI Test Case Generator** - Geração automática de casos de teste
2. **Bug Pattern Analyzer** - Detecção inteligente de padrões de bugs
3. **Smart Test Prioritizer** - Priorização baseada em risco e ML
4. **Advanced ML Engine** - Motor com múltiplos algoritmos
5. **ML Integration Suite** - Pipeline completo de ML
6. **AI Testing Dashboard** - Interface web para visualização
7. **Simple ML Demo** - Demonstração básica dos conceitos

**Algoritmos:** Random Forest, Isolation Forest, K-means, DBSCAN, Gradient Boosting, Neural Networks

---

## 🏗️ **Serviços**

| Serviço | Tecnologia | Porta | Status |
|---------|------------|-------|--------|
| **User** | Python/FastAPI | 8001 | ✅ Ativo |
| **Order** | Node.js/Express | 8002 | ✅ Ativo |
| **Payment** | Go/Gin | 8003 | ✅ Ativo |

**Health Checks:** `http://localhost:800X/health`

---

## 📚 **Documentação Especializada**

| Guia | Foco | Quando Usar |
|------|------|-------------|
| **[INSTALL.md](INSTALL.md)** | Instalação detalhada | Configuração inicial |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Execução de testes | Executar e entender testes |
| **[AI_ML_DEEP_DIVE_GUIDE.md](AI_ML_DEEP_DIVE_GUIDE.md)** | IA/ML em QA | Aprender sobre componentes ML |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Arquitetura técnica | Entender design e componentes |
| **[CICD_GUIDE.md](CICD_GUIDE.md)** | DevSecOps | Configurar pipelines |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Solução de problemas | Resolver erros comuns |

---

## 🎯 **Casos de Uso**

**QA Engineers:** Suite completa + IA para testing inteligente + Chaos engineering
**DevOps:** CI/CD com quality gates, Kubernetes, service mesh e observabilidade
**Desenvolvedores:** Arquitetura moderna + 3 linguagens + Service mesh

---

## 🚀 **Próximos Passos**

1. **[Instale](INSTALL.md)** seguindo o guia detalhado
2. **[Execute os testes](TESTING_GUIDE.md)** para validar funcionamento
3. **[Explore os componentes de IA](AI_ML_DEEP_DIVE_GUIDE.md)** para entender ML
4. **[Configure CI/CD](CICD_GUIDE.md)** para automação completa
5. **[Consulte troubleshooting](TROUBLESHOOTING.md)** se encontrar problemas

---

## 👨💻 **Autor**

**Lucas Teixeira** - QA Senior + AI/ML Testing Specialist
- LinkedIn: [lucas-teixeira-67b08b47](https://linkedin.com/in/lucas-teixeira-67b08b47)
- Email: lucasteixeira.ti@gmail.com

---
⭐ **Se este projeto te ajudou, deixe uma estrela!**
