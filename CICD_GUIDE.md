# 🚀 CI/CD Pipeline Guide - AI-Powered Microservices

## 📋 **Visão Geral**

Este projeto implementa um pipeline CI/CD completo com **DevSecOps** para demonstrar expertise em automação de testes e IA/ML em ambiente empresarial.

## 🔄 **Pipelines Implementados**

### **1. CI Pipeline** (`ci.yml`)
**Trigger**: Push, PR, Manual
**Duração**: ~45 minutos
**Funcionalidades**:
- ✅ **Multi-linguagem**: Python 3.13, Node.js 18, Go 1.21
- ✅ **131+ Testes**: 8 categorias completas (incluindo 13 testes de chaos)
- ✅ **7 Componentes IA/ML**: Testados automaticamente
- ✅ **Health Checks**: Verificação robusta de serviços
- ✅ **Relatórios**: Artefatos completos com retenção 30 dias

### **2. Deploy Pipeline** (`deploy.yml`)
**Trigger**: Push main, Tags, Manual
**Duração**: ~30 minutos
**Funcionalidades**:
- ✅ **Multi-cloud**: AWS EKS, Google GKE, Azure AKS
- ✅ **Container Registry**: GitHub Container Registry
- ✅ **Multi-arch**: AMD64 + ARM64
- ✅ **Kubernetes**: Deploy automatizado com health checks
- ✅ **Smoke Tests**: Validação pós-deploy

### **3. Security Pipeline** (`security.yml`)
**Trigger**: Push, PR, Semanal, Manual
**Duração**: ~20 minutos
**Funcionalidades**:
- ✅ **SAST**: CodeQL para 3 linguagens
- ✅ **Vulnerability Scan**: Trivy filesystem + config
- ✅ **Dependency Scan**: Safety, npm audit, gosec
- ✅ **Secret Scan**: TruffleHog git + filesystem
- ✅ **Security Dashboard**: Relatórios consolidados

## 🛠️ **Configuração Inicial**

### **1. Secrets Necessários (Produção)**

```bash
# Para AWS EKS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
EKS_CLUSTER_NAME=your_cluster_name

# Para Google GKE
GCP_SA_KEY=your_service_account_json
GKE_CLUSTER_NAME=your_cluster_name
GCP_ZONE=us-central1-a

# Para Azure AKS
AZURE_CREDENTIALS=your_azure_credentials_json
AZURE_RESOURCE_GROUP=your_resource_group
AKS_CLUSTER_NAME=your_cluster_name

# Automático
GITHUB_TOKEN=automatically_provided
```

### **2. Environment Variables**

```yaml
# No repositório GitHub
CLOUD_PROVIDER=aws  # ou gcp, azure
```

## 🚀 **Como Executar**

### **Execução Manual (Recomendado para Testes)**

1. **CI Pipeline**:
   ```
   GitHub → Actions → AI-Powered Microservices CI/CD → Run workflow
   ```

2. **Deploy Pipeline**:
   ```
   GitHub → Actions → Production Deploy Pipeline → Run workflow
   Environment: staging/production
   ```

3. **Security Pipeline**:
   ```
   GitHub → Actions → DevSecOps Security Pipeline → Run workflow
   Scan Type: full/quick/dependencies-only
   ```

### **Execução Automática**

- **CI**: Automático em push/PR
- **Deploy**: Automático em push para main
- **Security**: Automático semanal (segunda-feira 2h UTC)

## 📊 **Resultados e Relatórios**

### **CI Pipeline**
- **Artifacts**: `test-reports-{run_number}`
- **Conteúdo**: 
  - HTML reports de todos os testes
  - Relatórios ML (JSON)
  - Logs de serviços
  - Coverage reports

### **Deploy Pipeline**
- **Images**: GitHub Container Registry
- **Tags**: `latest`, `{sha}`, `{branch}-{sha}`
- **Platforms**: linux/amd64, linux/arm64

### **Security Pipeline**
- **GitHub Security Tab**: Findings automáticos
- **Artifacts**: `security-dashboard-{run_number}`
- **Retenção**: 90 dias

## 🔍 **Validação dos Pipelines**

### **Validação de Sintaxe**
```bash
# Manual no GitHub Actions
Workflow: Validate CI/CD Pipelines
Input: syntax
```

### **Teste Completo**
```bash
# Manual no GitHub Actions  
Workflow: Validate CI/CD Pipelines
Input: full-test
```

## 🏗️ **Arquitetura dos Pipelines**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CI Pipeline   │    │ Deploy Pipeline │    │Security Pipeline│
│                 │    │                 │    │                 │
│ • 118+ Tests    │    │ • Multi-cloud   │    │ • SAST (CodeQL) │
│ • 7 AI/ML Mods  │    │ • K8s Deploy    │    │ • Vuln Scan     │
│ • 3 Services    │    │ • Smoke Tests   │    │ • Dep Scan      │
│ • Reports       │    │ • Health Check  │    │ • Secret Scan   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │            GitHub Actions Runner                │
         │  • Ubuntu Latest  • 45min Timeout  • Artifacts │
         └─────────────────────────────────────────────────┘
```

## 🎯 **Benefícios para Engenheiro de Qualidade**

### **Demonstração de Expertise**
1. **DevSecOps**: Pipeline completo com segurança integrada
2. **AI/ML Testing**: 7 componentes de IA testados automaticamente
3. **Multi-linguagem**: Python, Node.js, Go em um pipeline
4. **Enterprise Ready**: Multi-cloud, observabilidade, relatórios

### **Qualidade Assegurada**
1. **118+ Cenários**: Cobertura completa de testes
2. **8 Categorias**: Unit, Contract, Integration, Security, API, Performance, AI/ML, Chaos
3. **Automação Total**: Zero intervenção manual
4. **Feedback Rápido**: Falhas detectadas em minutos

### **Produção Ready**
1. **Security First**: 6 ferramentas de segurança
2. **Multi-cloud**: AWS, GCP, Azure suportados
3. **Observabilidade**: Logs, métricas, traces
4. **Rollback**: Deploy seguro com health checks

## 🔧 **Troubleshooting**

### **Problemas Comuns**

1. **CI Pipeline Falha**:
   ```bash
   # Verificar logs de serviços
   GitHub Actions → Failed Job → Show Service Logs on Failure
   ```

2. **Deploy Falha**:
   ```bash
   # Verificar autenticação cloud
   Secrets → Verificar CLOUD_PROVIDER e credenciais
   ```

3. **Security Scan Falha**:
   ```bash
   # Verificar permissões
   Settings → Actions → General → Workflow permissions
   ```

### **Validação Local**

```bash
# Testar Docker builds
docker build -t test-user services/user-service/
docker build -t test-order services/order-service/
docker build -t test-payment services/payment-service/

# Testar dependências ML
cd testing-suite
pip install -r requirements.txt
python -c "import sklearn, pandas, numpy, flask"
```

## 📈 **Métricas de Sucesso**

- **CI Success Rate**: >95%
- **Deploy Time**: <30 minutos
- **Security Findings**: Tracked no GitHub Security
- **Test Coverage**: 131+ cenários
- **AI/ML Components**: 7 módulos validados

## 🚀 **Próximos Passos**

1. **Configurar Secrets** para seu cloud provider
2. **Executar Validation Pipeline** para verificar setup
3. **Fazer primeiro Push** para testar CI automático
4. **Configurar Notifications** para falhas
5. **Monitorar Security Tab** para findings

---

**👨💻 Autor:** Lucas Teixeira - QA Senior + AI/ML Testing Specialist  
**🎯 Objetivo:** Demonstração de expertise em DevSecOps e AI Testing  
**📊 Status:** Production Ready - 100% Funcional