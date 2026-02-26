# 🤖 AI-Powered Microservices Testing Suite

[![Tests](https://img.shields.io/badge/Tests-131+%20Scenarios-brightgreen.svg)](https://github.com/)
[![Chaos](https://img.shields.io/badge/Chaos-13%20Tests-orange.svg)](https://github.com/)
[![Status](https://img.shields.io/badge/Status-92%25%20Functional-brightgreen.svg)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://python.org/)
[![AI](https://img.shields.io/badge/AI-Powered-red.svg)](https://github.com/)

**Suite completa de microserviços com IA para desenvolvimento, teste e monitoramento em produção.**

---

## 🎯 **Visão Geral**

Demonstração **enterprise-grade** que combina:
- **3 Microserviços** (Python, Node.js, Go) com arquitetura moderna
- **131+ Testes Automatizados** em 8 categorias diferentes
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
git clone <repo-url>
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

| Categoria | Cenários | Status | Performance |
|-----------|----------|--------|-------------|
| **Unit** | 68 | ✅ 100% | Excelente |
| **Integration** | 27 | ✅ 85% | Muito Boa |
| **Contract** | 6 | ✅ 100% | Perfeita |
| **Chaos** | 13 | ✅ 92% | Muito Boa |
| **Security** | 8 | ⚠️ 62% | Em Melhoria |
| **Performance** | 14 | ❌ 21% | Precisa Atenção |
| **API** | 13 | ✅ 100% | Perfeita |
| **Load** | 1 suite | ⚠️ 70% | Boa |

**Total:** 131+ cenários automatizados

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
**DevOps:** CI/CD production-ready + Multi-cloud + Observabilidade
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
