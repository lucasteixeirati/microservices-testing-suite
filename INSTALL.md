# 🛠️ Guia de Instalação Completo

## ✅ **Instalação Simplificada (Método Principal)**

O projeto foi otimizado para usar dependências que **não exigem** as Ferramentas de Build do Microsoft C++. A instalação agora é direta:

### **Pré-requisitos:**
- **Python 3.13** - https://www.python.org/downloads/ 
- **Node.js 18+** - https://nodejs.org/
- **Go 1.21+** - https://golang.org/dl/ 

**⚠️ IMPORTANTE: Reinicie o terminal/VS Code após instalar Go**

### **Verificar Instalação:**
```bash
python --version  # Deve mostrar 3.13+
node --version    # Deve mostrar 24+
go version        # Deve mostrar 1.21+
```

---

## 🚀 **Instalação Passo a Passo**

### **Passo 1: Navegar para o Projeto**
```criar pasta para o projeto exemplo:
cd C:\Users\microservices-testing-suite
```

### **Passo 2: Instalar Dependências dos Serviços**

#### **User Service (Python):**
```bash
cd services\user-service
pip install fastapi uvicorn pydantic cachetools email-validator
cd ..\..
```

#### **Order Service (Node.js):**
```bash
cd services\order-service
npm install
cd ..\..
```

#### **Payment Service (Go):**
```bash
cd services\payment-service
go mod tidy
cd ..\..
```

### **Passo 3: Instalar Dependências de Teste**
```bash
cd testing-suite
pip install -r requirements.txt
```

### **Passo 4: Iniciar Serviços**
```bash
run-local.bat
```
**Isso abrirá 3 janelas CMD:**
- User Service (Python) - Porta 8001
- Order Service (Node.js) - Porta 8002  
- Payment Service (Go) - Porta 8003

### **Passo 5: Aguardar Serviços Iniciarem (30 segundos)**

### **Passo 6: Verificar se Serviços Estão Rodando**
```bash
# No navegador ou novo terminal:
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Deve retornar: {"status": "healthy", "service": "nome-do-servico"}
```

### **Passo 7: Executar Testes**
```bash
cd testing-suite

# Todos os testes
python utils/test_runner.py --test-type all

# Testes específicos
python utils/test_runner.py --test-type contract
python utils/test_runner.py --test-type integration
```

---

## 🤖 **Instalação dos Componentes ML**

### **Dependências ML (já incluídas no requirements.txt):**
```bash
# Já instaladas no Passo 3, mas se necessário:
pip install scikit-learn pandas numpy flask matplotlib seaborn
```

### **Testar Componentes ML:**
```bash
# Teste rápido de todos os componentes
test-all-ml.bat

# Menu interativo
test-specific-ml.bat

# Dashboard de IA
python ai-testing/ai_testing_dashboard.py
# Acesse: http://localhost:5000
```

---

## 🔧 **Métodos Alternativos de Instalação**

### **Método 2: Usar Conda (Recomendado para ML)**
```bash
# 1. Instalar Anaconda/Miniconda
# https://www.anaconda.com/products/distribution

# 2. Criar ambiente
conda create -n microservices python=3.11
conda activate microservices

# 3. Instalar dependências via conda-forge
conda install -c conda-forge pytest requests locust flask docker scikit-learn pandas numpy
pip install pactman pytest-html pytest-cov fastapi uvicorn

# 4. Continuar com Passos 2-7 acima
```

### **Método 3: Usar Docker (Mais Simples)**
```bash
# 1. Instalar Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Executar em container
docker run -it --rm -v ${PWD}:/app -w /app python:3.11 bash
pip install -r testing-suite/requirements.txt
cd testing-suite
python utils/test_runner.py --test-type all
```

### **Método 4: Usar WSL2 (Linux no Windows)**
```bash
# 1. Habilitar WSL2
wsl --install

# 2. Instalar Ubuntu
wsl --install -d Ubuntu

# 3. No Ubuntu WSL
sudo apt update
sudo apt install python3-pip nodejs npm golang-go
pip install -r requirements.txt

# 4. Continuar com execução normal
```

### **Método 5: Build Tools (Se Necessário)**
```bash
# Se ainda encontrar erros de build:
# 1. Baixar Microsoft C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. Instalar com workload "C++ build tools"

# 3. Reiniciar terminal e instalar dependências
pip install -r requirements.txt
```

---

## 📊 **Verificação da Instalação**

### **Serviços Funcionando:**
```bash
# Deve retornar status healthy para todos:
curl http://localhost:8001/health  # User Service
curl http://localhost:8002/health  # Order Service  
curl http://localhost:8003/health  # Payment Service
```

### **Testes Funcionando:**
```bash
cd testing-suite
python utils/test_runner.py --help
# Deve mostrar opções de teste disponíveis
```

### **Componentes ML Funcionando:**
```bash
python ai-testing/simple_ml_demo.py
# Deve executar análise ML básica sem erros
```

---

## 🔧 **Resolução de Problemas**

### **"go" não é reconhecido:**
1. Reinstalar Go: https://golang.org/dl/
2. Reiniciar terminal/VS Code completamente
3. Verificar: `go version`
4. Se ainda não funcionar, adicionar manualmente ao PATH

### **Serviços não iniciam:**
```bash
# Verificar portas em uso
netstat -an | findstr "8001 8002 8003"

# Matar processos se necessário
taskkill /f /im python.exe
taskkill /f /im node.exe
taskkill /f /im go.exe

# Reiniciar
run-local.bat
```

### **Testes falham:**
1. Verificar se os 3 serviços estão rodando
2. Aguardar mais tempo para os serviços iniciarem (30-60s)
3. Reinstalar dependências: `pip install --upgrade -r requirements.txt`
4. Verificar se não há firewall bloqueando

### **Erro "Microsoft Visual C++ 14.0":**
- Use Método 2 (Conda) ou Método 3 (Docker)
- Ou instale Build Tools (Método 5)

### **Erro de encoding (emojis):**
```bash
# Configurar encoding
chcp 65001

# Ou usar arquivos *_clean.py
python ai-testing/ml_integration_demo_clean.py
```

### **Dependências ML falhando:**
```bash
# Instalar individualmente
pip install scikit-learn
pip install pandas
pip install numpy
pip install flask

# Ou usar conda
conda install scikit-learn pandas numpy flask
```

---

## 📋 **Estrutura Após Instalação**

```
microservices-testing-suite/
├── services/
│   ├── user-service/     # Python/FastAPI - Port 8001
│   ├── order-service/    # Node.js/Express - Port 8002
│   └── payment-service/  # Go/Gin - Port 8003
├── testing-suite/
│   ├── ai-testing/       # 7 componentes ML
│   ├── integration-tests/
│   ├── contract-tests/
│   ├── unit-tests/
│   ├── utils/
│   └── reports/
├── run-local.bat         # Script para iniciar serviços
├── test-all-ml.bat       # Script para testar ML
└── check-services.bat    # Script para verificar status
```

---

## 🎯 **Comandos de Instalação Rápida**

### **Windows (PowerShell/CMD):**
```bash
# Instalar pré-requisitos (se necessário)
# Python: https://www.python.org/downloads/
# Node.js: https://nodejs.org/
# Go: https://golang.org/dl/

# Clonar e instalar
cd C:\Users\Lucas\Downloads\microservices-testing-suite
cd services\user-service && pip install fastapi uvicorn pydantic cachetools email-validator && cd ..\..
cd services\order-service && npm install && cd ..\..
cd services\payment-service && go mod tidy && cd ..\..
cd testing-suite && pip install -r requirements.txt && cd ..

# Iniciar e testar
run-local.bat
# Aguardar 30s
cd testing-suite
python utils/test_runner.py --test-type all
```

### **Linux/macOS:**
```bash
# Instalar pré-requisitos
sudo apt update && sudo apt install python3-pip nodejs npm golang-go  # Ubuntu
brew install python node go  # macOS

# Instalar dependências
cd services/user-service && pip3 install fastapi uvicorn pydantic cachetools email-validator && cd ../..
cd services/order-service && npm install && cd ../..
cd services/payment-service && go mod tidy && cd ../..
cd testing-suite && pip3 install -r requirements.txt

# Iniciar serviços manualmente (3 terminais)
cd services/user-service && python3 main.py &
cd services/order-service && node app.js &
cd services/payment-service && go run main.go &

# Testar
cd testing-suite
python3 utils/test_runner.py --test-type all
```

---

## 🎉 **Resultados Esperados**

### **Serviços Rodando:**
```json
// http://localhost:8001/health
{"status": "healthy", "service": "user-service"}

// http://localhost:8002/health  
{"status": "healthy", "service": "order-service"}

// http://localhost:8003/health
{"status": "healthy", "service": "payment-service"}
```

### **Testes Executando:**
```
🚀 Starting Microservices Testing Suite
==================================================
✅ All services are ready!

[CONTRACT] Running Contract Tests...
✅ Contract tests passed!

[INTEGRATION] Running Integration Tests...
✅ Integration tests passed!

📊 Test Results Summary:
  Contract Tests: ✅ PASSED
  Integration Tests: ✅ PASSED

Overall: ✅ ALL TESTS PASSED
```

### **Componentes ML Funcionando:**
```
AI Simple ML Demo - Testing Intelligence
==================================================

1. Bug Pattern Analysis
   user-service: 0.700 | []
   Summary: 1/5 high-risk bugs
   Detection Rate: 20.0%

2. Test Prioritization
   1. [HIGH] test_auth_critical: 0.682 (HIGH)
   
3. Performance Prediction
   [FAST] Simple Unit Test: 18.9s (confidence: 80.0%)
   
4. AI Recommendations
   1. [LOW] 2 tests predicted to be slow - consider optimization
```

---

**👨💻 DevOps Engineer:** Lucas Teixeira  
**🎯 Projeto:** AI-Powered Microservices Testing Suite  
**📊 Status:** Guia de instalação para ambiente local e Docker
**🤖 ML Components:** 7 Componentes Implementados
