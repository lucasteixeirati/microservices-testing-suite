# Contract Tests

## Pactman vs Pact-Python

Este projeto usa **Pactman** em vez de **pact-python** por:

### ✅ Vantagens do Pactman:
- **Puro Python** - Sem dependências Ruby/C++
- **Sem Build Tools** - Instala em qualquer Windows
- **API Compatível** - Mesma sintaxe do Pact
- **Mais Estável** - Menos problemas de instalação

### 📋 Funcionalidades Mantidas:
- Consumer-Driven Contract Testing
- Mock Server Integration  
- Pact File Generation
- Contract Verification
- Like/Term Matchers

### 🚀 Uso:
```python
from pactman import Consumer, Provider, Like, Term

pact = Consumer('OrderService').has_pact_with(Provider('UserService'))
```

### 📚 Documentação:
- [Pactman GitHub](https://github.com/reecetech/pactman)
- [Pact Specification](https://docs.pact.io/)

**Resultado: Mesma funcionalidade, instalação mais simples!**