# 🤖 AI-Powered Microservices Testing Suite

[![Tests](https://img.shields.io/badge/Tests-131+%20Scenarios-brightgreen.svg)](https://github.com/)
[![Chaos](https://img.shields.io/badge/Chaos-13%20Tests-orange.svg)](https://github.com/)
[![Status](https://img.shields.io/badge/Status-92%25%20Functional-brightgreen.svg)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://python.org/)
[![AI](https://img.shields.io/badge/AI-Powered-red.svg)](https://github.com/)

**Suite completa de microserviços com IA para desenvolvimento, teste e monitoramento em produção.**

---

## 🎯 **O que é este projeto?**

Demonstração **enterprise-grade** combinando:
- **3 Microserviços** (Python, Node.js, Go)
- **131+ Testes Automatizados** (8 categorias)
- **7 Componentes de IA/ML** para testing inteligente
- **13 Testes de Chaos Engineering** para resiliência
- **CI/CD DevSecOps** completo

### **🏗️ Arquitetura**
```
User Service (Python) ←→ Order Service (Node.js) ←→ Payment Service (Go)
                    ↓
            Istio Service Mesh + Observability
                    ↓
        AI Testing Suite + Chaos Engineering
```

---

## 🚀 **Quick Start**

### **1. Pré-requisitos**
- Python 3.13, Node.js 18+, Go 1.21+
- Docker (opcional)

### **2. Instalação Rápida**
```bash
# Clone e instale
git clone <repo-url>
cd microservices-testing-suite

# Instalar dependências
cd services/user-service && pip install -r requirements.txt && cd ../..
cd services/order-service && npm install && cd ../..
cd services/payment-service && go mod tidy && cd ../..
cd testing-suite && pip install -r requirements.txt && cd ..

# Iniciar serviços
run-local.bat
```

### **3. Executar Testes**
```bash
cd testing-suite

# Todos os testes (131+ cenários)
python utils/test_runner.py --test-type all

# Testes específicos
python utils/test_runner.py --test-type chaos    # 13 experimentos
python utils/test_runner.py --test-type contract # 6 contratos
python utils/test_runner.py --test-type load     # Performance
```

### **4. Componentes de IA**
```bash
# Teste rápido de todos os 7 componentes ML
test-all-ml.bat

# Dashboard de IA (http://localhost:5000)
python ai-testing/ai_testing_dashboard.py
```

---

## 🧪 **Testing Suite - 131+ Cenários**

| Tipo | Cenários | Status | Comando |
|------|----------|--------|---------|
| **Unit** | 68 | ✅ 100% | `--test-type unit` |
| **Integration** | 27 | ✅ 85% | `--test-type integration` |
| **Contract** | 6 | ✅ 100% | `--test-type contract` |
| **Chaos** | 13 | ✅ 92% | `--test-type chaos` |
| **Security** | 8 | ⚠️ 62% | `--test-type security` |
| **Performance** | 14 | ❌ 21% | `--test-type performance` |
| **API** | 13 | ✅ 100% | `--test-type api` |
| **Load** | 1 suite | ⚠️ 70% | `--test-type load` |

---

## 🤖 **AI/ML Components - 7 Módulos**

### **Componentes Funcionais:**
1. **AI Test Case Generator** - Geração automática de testes
2. **Bug Pattern Analyzer** - ML para detecção de padrões
3. **Smart Test Prioritizer** - Priorização baseada em risco
4. **Advanced ML Engine** - Múltiplos algoritmos
5. **ML Integration Suite** - Pipeline end-to-end
6. **AI Testing Dashboard** - Interface web
7. **Simple ML Demo** - Demonstração básica

### **Algoritmos Implementados:**
Random Forest, Isolation Forest, K-means, DBSCAN, Gradient Boosting, Neural Networks

---

## 🌪️ **Chaos Engineering - 13 Experimentos**

### **Testes Implementados:**
- ✅ Service Restart/Kill/Recovery (6 básicos)
- ✅ Memory/CPU/Network Stress (4 avançados)
- ✅ Cascade Failures & Dependencies (3 complexos)

### **Execução:**
```bash
# Local (recomendado)
run-chaos-tests.bat

# Docker (manipulação de containers)
run-chaos-tests-docker.bat
```

**Taxa de Sucesso:** 92.3% (12/13 testes)

---

## 🏗️ **Serviços**

| Serviço | Tecnologia | Porta | Features |
|---------|------------|-------|----------|
| **User** | Python/FastAPI | 8001 | CRUD, Logging, Health |
| **Order** | Node.js/Express | 8002 | Pedidos, Validação |
| **Payment** | Go/Gin | 8003 | Pagamentos, Processing |

**Health Checks:** `http://localhost:800X/health`

---

## 🔄 **CI/CD & DevSecOps**

### **3 Pipelines Production-Ready:**
- **CI Pipeline** - 131+ testes automatizados
- **Deploy Pipeline** - Multi-cloud (AWS/GCP/Azure)
- **Security Pipeline** - SAST, vulnerability scan, secrets

**Status:** 100% funcional com deploy automatizado

---

## 📚 **Documentação Completa**

| Arquivo | Propósito |
|---------|-----------|
| **[INSTALL.md](INSTALL.md)** | Guia de instalação detalhado |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Como executar todos os testes |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Diagramas e componentes técnicos |
| **[CICD_GUIDE.md](CICD_GUIDE.md)** | Pipeline DevSecOps completo |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Soluções para problemas comuns |

---

## 🎯 **Casos de Uso**

### **Para QA Engineers:**
- Suite completa de testes automatizados
- Componentes de IA para testing inteligente
- Chaos engineering para validação de resiliência

### **Para DevOps:**
- CI/CD pipeline production-ready
- Multi-cloud deployment
- Observabilidade completa

### **Para Desenvolvedores:**
- Arquitetura de microserviços moderna
- Exemplos de 3 linguagens (Python, Node.js, Go)
- Service mesh com Istio

---

## 🚀 **Próximos Passos**

1. **Instale** seguindo o Quick Start
2. **Execute** os testes para ver funcionando
3. **Explore** os componentes de IA
4. **Teste** chaos engineering
5. **Consulte** a documentação para detalhes

---

## 👨💻 **Autor**

**Lucas Teixeira**
- QA Senior + AI/ML Testing Specialist
- LinkedIn: [lucas-teixeira-67b08b47](https://linkedin.com/in/lucas-teixeira-67b08b47)
- Email: lucasteixeira.ti@gmail.com

---

⭐ **Se este projeto te ajudou, deixe uma estrela!**