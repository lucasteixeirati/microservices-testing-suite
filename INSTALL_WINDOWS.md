# 🛠️ Instalação no Windows

## ✅ Instalação Simplificada (Método Principal)

O projeto foi atualizado para usar dependências que **não exigem** as Ferramentas de Build do Microsoft C++. A instalação agora é direta:

```cmd
cd testing-suite
pip install -r requirements.txt

# Se tudo correr bem, você está pronto!
```

### Solução Alternativa: Build Tools (Se necessário)
```cmd
# 1. Baixar Microsoft C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. Instalar com workload "C++ build tools"

# 3. Reiniciar terminal e instalar dependências
cd testing-suite
pip install -r requirements.txt
```

### Solução 2: Usar Conda (Alternativa)
```cmd
# 1. Instalar Anaconda/Miniconda
# https://www.anaconda.com/products/distribution

# 2. Criar ambiente
conda create -n microservices python=3.11
conda activate microservices

# 3. Instalar dependências via conda-forge
conda install -c conda-forge pytest requests locust flask docker
pip install pactman pytest-html pytest-cov allure-pytest
```

### Solução 3: Usar Docker (Mais Simples)
```cmd
# 1. Instalar Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Executar testes em container
docker run -it --rm -v ${PWD}:/app -w /app python:3.11 bash
pip install -r testing-suite/requirements.txt
cd testing-suite
python utils/test_runner.py --test-type all
```

### Solução 4: Usar WSL2 (Linux no Windows)
```cmd
# 1. Habilitar WSL2
wsl --install

# 2. Instalar Ubuntu
wsl --install -d Ubuntu

# 3. No Ubuntu WSL
sudo apt update
sudo apt install python3-pip
pip install -r requirements.txt
```

## Verificar Instalação
```cmd
cd testing-suite
python utils/test_runner.py --help
```

## Troubleshooting
- **Erro "Microsoft Visual C++ 14.0"**: Use Solução 1 ou 2
- **Erro "docker not found"**: Instale Docker Desktop
- **Erro "pact not found"**: Use conda ou build tools
- **Timeout errors**: Aguarde serviços iniciarem (30s)