# 🧪 Testing Guide - Guia Completo de Testes

## 📊 **Visão Geral**

### **8 Tipos de Testes Implementados:**

| Tipo | Cenários | Propósito | Comando |
|------|----------|-----------|----------|
| **Contract** | 6 | API contracts estruturais | `--test-type contract` |
| **Integration** | 21 | End-to-end flows + error scenarios | `--test-type integration` |
| **Unit** | Contagem automática | Python (pytest), Node.js (Jest) e Go (`go test`) | comandos abaixo |
| **Performance** | 14 | Response time + throughput | `--test-type performance` |
| **Security** | 8 | SQL injection + XSS + CSRF | `--test-type security` |
| **API** | 13 | HTTP validation + error handling | `--test-type api` |
| **Chaos** | 13 | Resilience + advanced chaos | `--test-type chaos` |
| **Load** | 1 suite | Performance/Scale com Locust | `--test-type load` |

---

## 🚀 **Execução Rápida**

### **Pré-requisitos:**
```bash
# 1. Iniciar serviços
run-local.bat
# Aguardar 30s

# 2. Instalar dependências de teste
cd testing-suite
pip install -r requirements.txt
```

### **Executar Todos os Testes:**
```bash
python utils/test_runner.py --test-type all
```

### **Testes Específicos:**
```bash
# Contract tests (estruturais)
python utils/test_runner.py --test-type contract

# Integration tests (end-to-end)
python utils/test_runner.py --test-type integration

# Unit tests (lógica de negócio)
python utils/test_runner.py --test-type unit

# Load tests (performance)
python utils/test_runner.py --test-type load --load-users 100
```

---

## 🤖 **AI-Powered Testing Suite - 7 Componentes ML**

### **Teste Rápido - Todos os Componentes ML:**
```bash
test-all-ml.bat  # Testa todos os 7 componentes automaticamente
```

### **Menu Interativo:**
```bash
test-specific-ml.bat  # Menu para escolher componente específico
```

### **Componentes Individuais:**

#### **1. Simple ML Demo (Básico)**
```bash
python ai-testing/simple_ml_demo.py
```
- ✅ Funciona sem dependências pesadas
- 🎯 Análise básica de bugs, priorização e performance
- ⚡ Execução rápida (~10 segundos)

#### **2. AI Test Case Generator**
```bash
python ai-testing/test_case_generator.py
```
- 🔧 Análise automática de código
- 📝 Geração de test cases
- 🎯 Avaliação de riscos

#### **3. Bug Pattern Analyzer (ML Avançado)**
```bash
python ai-testing/bug_pattern_analyzer.py
```
- 🧠 Machine Learning para detecção de padrões
- 📊 Clustering de bugs similares (K-means)
- 🚨 Detecção de anomalias (Isolation Forest)

#### **4. Smart Test Prioritizer**
```bash
python ai-testing/smart_test_prioritizer.py
```
- 🎯 Priorização baseada em ML (Random Forest)
- 📈 Feature importance analysis
- ⚡ Otimização de sequência de execução

#### **5. Advanced ML Engine**
```bash
python ai-testing/advanced_ml_engine.py
```
- 🤖 Múltiplos algoritmos (RF + NN + GB + DBSCAN)
- 🔮 Predição de falhas
- 📊 Detecção de flakiness

#### **6. ML Integration Suite**
```bash
python ai-testing/ml_integration_demo.py
```
- 🚀 Todos os componentes integrados
- 📋 Relatório JSON completo
- 💡 Recomendações inteligentes

#### **7. AI Testing Dashboard**
```bash
python ai-testing/ai_testing_dashboard.py
# Acesse: http://localhost:5000
```
- 🌐 Interface web interativa
- 📊 Visualizações em tempo real
- 🎛️ APIs REST para integração

---

## 📋 **Detalhamento por Categoria**

### **1. Contract Tests (6 cenários)**
**Propósito:** Validação estrutural de APIs
```bash
# Testes implementados:
- test_user_service_contract_structure
- test_order_service_contract_structure
- test_payment_service_contract_structure
- test_error_response_contract
- test_health_check_contract
- test_pagination_contract
```

### **2. Integration Tests (21 cenários)**
**Propósito:** Fluxos end-to-end e cenários de erro

#### **Advanced Integration (9 testes):**
- Service dependency failures
- Partial service failure recovery
- Communication retry logic
- Circuit breaker simulation
- Health monitoring
- Eventual consistency
- Transaction rollback

#### **End-to-End Flow (4 testes):**
- Complete order flow
- Invalid user scenarios
- Invalid order scenarios
- High amount payment failures

#### **Error Scenarios (8 testes):**
- Cascade failures
- Timeout handling
- Malformed requests
- Large payload handling
- Special characters
- Concurrent operations

### **3. Unit Tests**
**Propósito:** Lógica de negócio individual

```bash
# Python/FastAPI + regras e utilitários compartilhados
cd testing-suite
pytest unit-tests --cov=../services/user-service --cov-report=term-missing

# Node.js/Express exercitando handlers reais com Supertest
cd ../services/order-service
npm run test:coverage

# Go/Gin exercitando o router real com httptest
cd ../payment-service
go test -cover ./...
```

As três suítes cobrem health checks, validação, CRUD, comunicação com dependências, SSRF allowlist, ciclo de pedidos/pagamentos e proteção CSRF para requisições de navegador. A contagem exata é publicada pelo CI, evitando números manuais desatualizados.

### **4. Performance Tests (14 cenários)**
**Propósito:** Response time e throughput

#### **Advanced Performance (9 testes):**
- Concurrent user creation
- High volume processing
- Memory usage under load
- Traffic spikes
- Database performance

#### **Comprehensive Performance (5 testes):**
- Response time consistency
- Throughput measurement
- Latency analysis

### **5. Security Tests (8 cenários)**
**Propósito:** Vulnerabilidades de segurança
- SQL injection prevention
- XSS prevention
- CSRF token validation
- Rate limiting
- Sensitive data exposure
- Error message disclosure

### **6. API Tests (13 cenários)**
**Propósito:** Validação HTTP e error handling
- Database connection resilience
- Unauthorized access
- Input validation
- Content type validation
- HTTP status codes
- Timeout handling

### **7. Chaos Tests (13 cenários)**
**Propósito:** Resiliência e recuperação

#### **Basic Chaos (6 testes):**
- Service restart resilience
- Service kill and recovery
- Cascade failure simulation
- Random disruption
- Network partition
- Resource exhaustion

#### **Advanced Chaos (7 testes):**
- Rolling restart chaos
- Memory pressure simulation
- Network latency simulation
- CPU intensive load
- Disk I/O stress
- Gradual load increase
- Dependency failure cascade

### **8. Load Tests (1 suite)**
**Propósito:** Performance e escala
```bash
# Locust load testing
python utils/test_runner.py --test-type load --load-users 100 --load-duration 5m
```

---

## 📊 **Relatórios de Teste**

### **Relatórios Automáticos:**
```bash
# Relatório consolidado
python utils/report_generator.py
# Gera: reports/test_suite_report.html

# Relatório com coverage
pytest --cov=../services --cov-report=html:reports/coverage --html=reports/coverage_report.html

# Relatório específico
pytest contract-tests/ --html=reports/contract_report.html --self-contained-html
```

### **Estrutura dos Relatórios:**
- ✅ **Test Coverage Summary** - Total de cenários
- ✅ **Test Suites Breakdown** - Detalhes por tipo
- ✅ **Architecture Coverage** - Serviços testados
- ✅ **Quality Metrics** - Métricas de qualidade
- ✅ **Execution Commands** - Comandos para execução

---

## 🎯 **Interpretando Resultados ML**

### **Scores de Prioridade:**
- **0.8-1.0**: CRITICAL - Execute imediatamente
- **0.6-0.8**: HIGH - Alta prioridade
- **0.4-0.6**: MEDIUM - Prioridade média
- **0.0-0.4**: LOW - Baixa prioridade

### **Probabilidade de Bug:**
- **>0.7**: Alto risco de ser bug real
- **0.4-0.7**: Risco médio
- **<0.4**: Baixo risco

### **Tempo de Execução Predito:**
- **>180s**: SLOW - Considere otimização
- **60-180s**: MEDIUM - Tempo aceitável
- **<60s**: FAST - Execução rápida

---

## 🔧 **Troubleshooting**

### **Problemas Comuns:**

#### **Serviços não respondem:**
```bash
# Verificar se serviços estão rodando
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Reiniciar se necessário
run-local.bat
```

#### **Testes falhando:**
```bash
# Aguardar serviços iniciarem (30s)
# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Verificar portas em uso
netstat -an | findstr "8001 8002 8003"
```

#### **Erro de encoding (emojis):**
```bash
# Usar arquivos *_clean.py
python ai-testing/ml_integration_demo_clean.py

# Ou configurar encoding
chcp 65001
```

### **Dependências ML:**
```bash
# Se der erro de dependências ML
pip install scikit-learn pandas numpy flask

# Para componentes específicos
pip install -r requirements.txt
```

---

## 📈 **Métricas de Qualidade**

### **Status Atual:**
- **Total de Testes**: 118+ cenários implementados
- **Taxa de Sucesso**: calculada em cada execução a partir dos arquivos JUnit

### **Dashboard visual e evidências**

```bash
python testing-suite/utils/generate_test_dashboard.py
```

O comando combina JUnit e as coberturas Python, Node.js e Go em `docs/evidence/latest-test-dashboard.html`. Os arquivos gerados são reproduzíveis e publicados como artefatos do GitHub Actions; capturas selecionadas podem ser adicionadas em `docs/evidence/screenshots/`.
- **Cobertura de Serviços**: 3/3 microserviços testados
- **Tipos de Teste**: 8 categorias completas
- **Componentes ML**: 7 módulos funcionais
- **Algoritmos ML**: 6 algoritmos diferentes
- **Accuracy ML**: 85%+ nos modelos treinados

### **Cobertura por Serviço:**
- **User Service**: 100% (Health, CRUD, Business Logic)
- **Order Service**: 100% (Orders, Validation, Status)
- **Payment Service**: 100% (Payments, Processing, Validation)

---

## 🚀 **Próximos Passos**

### **Após Executar os Testes:**
1. **Analise os relatórios HTML** gerados em `reports/`
2. **Implemente as recomendações ML** de alta prioridade
3. **Treine modelos** com seus dados reais
4. **Integre com CI/CD** pipeline
5. **Use o dashboard** para monitoramento contínuo

### **Expansão da Suite:**
1. **Property-Based Testing** - Testes com dados gerados
2. **Mutation Testing** - Validação da qualidade dos testes
3. **Visual Testing** - Testes de interface
4. **Accessibility Testing** - Testes de acessibilidade

---

## 📞 **Comandos de Referência Rápida**

```bash
# Setup inicial
run-local.bat
cd testing-suite
pip install -r requirements.txt

# Todos os testes
python utils/test_runner.py --test-type all

# Testes específicos
python utils/test_runner.py --test-type contract
python utils/test_runner.py --test-type integration
python utils/test_runner.py --test-type unit

# Testes ML
test-all-ml.bat
test-specific-ml.bat
python ai-testing/ai_testing_dashboard.py

# Relatórios
python utils/report_generator.py
pytest --html=reports/full_report.html --self-contained-html

# Load testing
python utils/test_runner.py --test-type load --load-users 100
```

---

**👨💻 QA Engineer:** Lucas Teixeira  
**🎯 Projeto:** AI-Powered Microservices Testing Suite  
**📊 Status:** suíte multi-stack com resultados publicados por execução
**🤖 AI Features:** Fully Implemented and Operational
