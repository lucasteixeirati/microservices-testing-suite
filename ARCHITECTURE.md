# 🏗️ Arquitetura do Sistema - AI-Powered Microservices Testing Suite

## 📐 **Visão Geral da Arquitetura**

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web Dashboard]
        API[API Clients]
        TEST[Test Runner]
    end
    
    subgraph "AI/ML Layer (IMPLEMENTADO)"
        TCG[Test Case Generator]
        BPA[Bug Pattern Analyzer]
        STP[Smart Test Prioritizer]
        AME[Advanced ML Engine]
        AID[AI Dashboard]
        MIS[ML Integration Suite]
        SMD[Simple ML Demo]
    end
    
    subgraph "Service Mesh (Istio)"
        GW[Istio Gateway]
        VS[Virtual Services]
        DR[Destination Rules]
    end
    
    subgraph "Microservices"
        US[User Service<br/>Python/FastAPI<br/>:8001]
        OS[Order Service<br/>Node.js/Express<br/>:8002]
        PS[Payment Service<br/>Go/Gin<br/>:8003]
    end
    
    subgraph "Testing Infrastructure"
        CT[Contract Tests - 6]
        IT[Integration Tests - 21]
        UT[Unit Tests - Python + Node.js + Go]
        PT[Performance Tests - 14]
        ST[Security Tests - 8]
        AT[API Tests - 13]
        CHT[Chaos Tests - 13]
        LT[Load Tests - 1 suite]
    end
    
    subgraph "Observability"
        PROM[Prometheus]
        GRAF[Grafana]
        ELK[ELK Stack]
        JAEG[Jaeger]
        KIALI[Kiali]
    end
    
    UI --> GW
    API --> GW
    TEST --> US
    TEST --> OS
    TEST --> PS
    
    GW --> VS
    VS --> DR
    DR --> US
    DR --> OS
    DR --> PS
    
    US --> OS
    OS --> PS
    
    TCG --> US
    TCG --> OS
    TCG --> PS
    BPA --> ELK
    STP --> CT
    STP --> IT
    AID --> PROM
    
    CT --> US
    IT --> US
    LT --> US
    CHT --> US
    
    US --> PROM
    OS --> PROM
    PS --> PROM
    US --> ELK
    OS --> ELK
    PS --> ELK
    US --> JAEG
    OS --> JAEG
    PS --> JAEG
```

## 🤖 **Arquitetura de IA (7 Componentes Implementados)**

```mermaid
graph TB
    subgraph "Data Sources"
        LOGS[Application Logs]
        METRICS[System Metrics]
        CODE[Source Code]
        TESTS[Test Results]
    end
    
    subgraph "AI Processing Pipeline"
        ETL[Data Extraction<br/>& Transformation]
        ML[Machine Learning<br/>6 Algorithms]
        ANALYSIS[Pattern Analysis]
        INSIGHTS[Insight Generation]
    end
    
    subgraph "AI Components (IMPLEMENTADOS)"
        TCG[Test Case Generator<br/>Code Analysis + ML]
        BPA[Bug Pattern Analyzer<br/>Isolation Forest + K-means]
        STP[Smart Test Prioritizer<br/>Random Forest + Feature Engineering]
        AME[Advanced ML Engine<br/>RF + NN + GB + DBSCAN]
        MIS[ML Integration Suite<br/>End-to-end Analysis]
        AID[AI Dashboard<br/>Flask Web Interface]
        SMD[Simple ML Demo<br/>Basic Heuristics]
    end
    
    subgraph "Outputs"
        AUTO_TESTS[Auto-generated Tests]
        BUG_ALERTS[Bug Predictions]
        TEST_PLANS[Optimized Test Plans]
        REPORTS[AI Reports]
    end
    
    LOGS --> ETL
    METRICS --> ETL
    CODE --> ETL
    TESTS --> ETL
    
    ETL --> ML
    ML --> ANALYSIS
    ANALYSIS --> INSIGHTS
    
    INSIGHTS --> TCG
    INSIGHTS --> BPA
    INSIGHTS --> STP
    INSIGHTS --> AME
    INSIGHTS --> MIS
    INSIGHTS --> AID
    INSIGHTS --> SMD
    
    TCG --> AUTO_TESTS
    BPA --> BUG_ALERTS
    STP --> TEST_PLANS
    AID --> REPORTS
```

## 🔒 **Arquitetura de Segurança (Hardened)**

```mermaid
graph TB
    subgraph "External Traffic"
        EXT[External Clients]
    end
    
    subgraph "Security Perimeter"
        FW[Firewall/WAF]
        LB[Load Balancer]
    end
    
    subgraph "Istio Service Mesh"
        IG[Istio Gateway<br/>TLS Termination]
        
        subgraph "Hardened Services"
            US[User Service<br/>✅ XSS Protected<br/>✅ CSRF Enabled<br/>✅ Input Sanitized]
            OS[Order Service<br/>✅ SSRF Protected<br/>✅ CSRF Enabled<br/>✅ URL Validated]
            PS[Payment Service<br/>✅ XSS Protected<br/>✅ SSRF Protected<br/>✅ Thread Safe]
        end
        
        subgraph "Security Policies"
            AP[Authorization Policies<br/>✅ Dedicated Service Accounts]
            NP[Network Policies<br/>✅ Least Privilege]
            SP[Security Contexts<br/>✅ Non-root Containers]
        end
    end
    
    subgraph "Secrets Management"
        K8S_SEC[Kubernetes Secrets<br/>✅ Strong Passwords]
        TLS_CERTS[TLS Certificates<br/>✅ Valid Certs]
    end
    
    EXT --> FW
    FW --> LB
    LB --> IG
    
    IG -.->|mTLS| US
    IG -.->|mTLS| OS
    IG -.->|mTLS| PS
    
    US -.->|mTLS| OS
    OS -.->|mTLS| PS
    
    AP --> US
    AP --> OS
    AP --> PS
    
    NP --> US
    NP --> OS
    NP --> PS
    
    K8S_SEC --> US
    K8S_SEC --> OS
    K8S_SEC --> PS
    
    TLS_CERTS --> IG
```

## 🚀 **Arquitetura de CI/CD**

```mermaid
graph TB
    subgraph "Development"
        DEV_CODE[Source Code]
        DEV_TEST[Local Testing]
        DEV_BUILD[Local Build]
    end
    
    subgraph "CI/CD Pipeline (✅ Funcional)"
        GIT[GitHub Repository]
        GHA[GitHub Actions]
        BUILD[Build & Test<br/>✅ Python 3.13<br/>✅ Security Deps]
        SCAN[Security Scan<br/>✅ Trivy Weekly]
        DOCKER[Docker Build<br/>✅ Multi-service<br/>✅ Security Hardened]
    end
    
    subgraph "Automated Deployment"
        K8S_DEPLOY[Kubernetes Deploy<br/>✅ Automated]
        HEALTH_CHECK[Health Checks<br/>✅ Built-in]
        SMOKE_TESTS[Smoke Tests<br/>✅ Post-deploy]
    end
    
    subgraph "Production Environment"
        PROD_K8S[Kubernetes Cluster<br/>✅ Security Hardened]
        PROD_ISTIO[Istio Service Mesh<br/>✅ mTLS + Policies]
        PROD_MONITOR[Full Monitoring<br/>✅ Metrics + Logs + Traces]
    end
    
    DEV_CODE --> GIT
    DEV_TEST --> GIT
    DEV_BUILD --> GIT
    
    GIT --> GHA
    GHA --> BUILD
    BUILD --> SCAN
    SCAN --> DOCKER
    
    DOCKER --> K8S_DEPLOY
    K8S_DEPLOY --> HEALTH_CHECK
    HEALTH_CHECK --> SMOKE_TESTS
    
    SMOKE_TESTS --> PROD_K8S
    PROD_K8S --> PROD_ISTIO
    PROD_ISTIO --> PROD_MONITOR
```

## 📋 **Componentes e Tecnologias**

### **Microserviços:**
- **User Service**: Python 3.13 + FastAPI + Pydantic
- **Order Service**: Node.js 18 + Express + UUID
- **Payment Service**: Go 1.21 + Gin + UUID

### **AI/ML (7 Componentes):**
- **Scikit-learn 1.7.2**: Random Forest, Isolation Forest, K-means, DBSCAN, Gradient Boosting
- **Neural Networks**: MLPClassifier para padrões complexos
- **Pandas 2.3.3**: Data analysis e feature engineering
- **NumPy 2.3.3**: Computação numérica avançada
- **Flask 3.0.3**: AI dashboard web interface
- **Ensemble Methods**: Combinação de múltiplos algoritmos
- **Model Persistence**: Pickle para salvar/carregar modelos
- **Cross-validation**: Validação robusta dos modelos
- **Feature Engineering**: Extração automática de características
- **Real-time Analytics**: Anomaly detection e clustering
- **Predictive Analytics**: Failure e performance prediction

### **Testing (contagem publicada pelo CI):**
- **Pytest 8.3.3**: Framework principal de testes
- **Pactman 2.31.0**: Contract testing (consumer-driven)
- **Locust 2.17.0**: Load testing e performance
- **Docker 6.1.3**: Chaos engineering

### **Service Mesh:**
- **Istio 1.19+**: Gateway, VirtualService, DestinationRule
- **mTLS**: Mutual TLS entre todos os serviços
- **Policies**: Authorization + Network + Security

### **Observabilidade:**
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **ELK Stack**: Centralized logging
- **Jaeger**: Distributed tracing
- **Kiali**: Service mesh observability

### **Infrastructure:**
- **Kubernetes 1.28+**: Container orchestration
- **Docker**: Containerization + Security hardened
- **GitHub Actions**: CI/CD com falha bloqueante nas categorias obrigatórias
- **Helm**: Package management

## 🎯 **Padrões Arquiteturais Implementados**

### **Microservices Patterns:**
- 🧪 **Storage ownership per service** (em memória na demonstração; persistência é evolução planejada)
- ✅ **API Gateway** (Istio Gateway)
- ✅ **Service Discovery** (Kubernetes DNS)
- ✅ **Circuit Breaker** (Istio DestinationRule)
- ✅ **Bulkhead** (Resource isolation)

### **Design Patterns (Essenciais):**
- ✅ **Singleton** (HTTP client pooling)
- ✅ **Builder** (Service configuration)
- ✅ **Decorator** (Logging & retry logic)

### **Testing Patterns (AI-Powered):**
- ✅ **Test Pyramid** (Unit → Integration → E2E)
- ✅ **Consumer-Driven Contracts** (Pact)
- ✅ **Chaos Engineering** (Resilience testing)
- ✅ **AI-Powered Testing** (ML-driven test generation)
- ✅ **ML Test Prioritization** (Risk-based ranking)
- ✅ **Anomaly Detection** (Real-time bug pattern detection)
- ✅ **Predictive Testing** (Failure prediction with confidence intervals)
- ✅ **Ensemble Testing** (Multiple ML algorithms)
- ✅ **Feature Importance** (ML-driven test optimization)
- ✅ **Automated Test Generation** (AI code analysis)
- ✅ **Performance Prediction** (ML execution time optimization)

### **Security Patterns:**
- ✅ **Zero Trust** (mTLS everywhere)
- ✅ **Defense in Depth** (Multiple layers)
- ✅ **Least Privilege** (Minimal permissions)
- ✅ **Secrets Management** (Strong credentials)
- ✅ **Input Sanitization** (XSS/SSRF prevention)
- ✅ **CSRF Protection** (Token-based)
- ✅ **Path Validation** (Traversal prevention)
- ✅ **Container Hardening** (Non-root execution)

## 🛡️ **Security Hardening Status**

### **✅ Vulnerabilidades Corrigidas:**
- **XSS Prevention**: Input sanitization implementada
- **SSRF Protection**: URL validation com allowlist
- **CSRF Protection**: Token-based protection habilitado
- **Log Injection**: Message sanitization e data masking
- **Path Traversal**: Safe path joining implementado
- **Command Injection**: Subprocess security implementado
- **Memory Leaks**: TTL cache para tokens CSRF
- **Container Security**: Non-root execution contexts

### **🔧 Error Handling Robusto:**
- **HTTP Requests**: Timeout e exception handling
- **Concurrent Operations**: Thread safety implementado
- **Service Communication**: Retry logic com fallback
- **Test Reliability**: Graceful degradation

## 📊 **Métricas de Arquitetura**

### **Testing Suite:**
- **Total de Testes**: calculado automaticamente em cada execução
- **Cobertura de Serviços**: 3/3 microserviços testados
- **Tipos de Teste**: 8 categorias
- **Taxa de Sucesso**: publicada nos artefatos JUnit e no dashboard de evidências

### **AI/ML Components:**
- **Componentes ML**: 7 módulos implementados
- **Algoritmos ML**: 6 algoritmos diferentes
- **Accuracy**: 85%+ nos modelos treinados
- **Performance**: Sub-segundo para análises básicas

### **Security:**
- **Vulnerabilidades Críticas**: 0 (todas corrigidas)
- **Security Patterns**: 8 implementados
- **Container Security**: execução non-root e capabilities removidas nos serviços
- **mTLS**: política `STRICT` definida para o namespace no Istio

### **CI/CD:**
- **Pipeline**: falhas de testes obrigatórios interrompem a execução
- **Deploy Automation**: workflow preparado para clusters configurados
- **Security Scanning**: Semanal com Trivy
- **Health Checks**: Built-in em todos os containers

---

**👨💻 Arquiteto:** Lucas Teixeira  
**🎯 Versão:** 4.1 - AI-Powered Testing Reference
**📊 Status:** Demonstração evolutiva com quality gates
**🔒 Security:** All Critical Vulnerabilities Fixed  
**🤖 AI/ML:** 7 Components Fully Functional  
**🚀 CI/CD:** Testes bloqueantes e relatórios reproduzíveis
**📦 Containers:** Security Hardened with Health Checks
