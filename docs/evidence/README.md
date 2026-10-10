# Evidências visuais

Esta pasta reúne evidências reproduzíveis da aplicação e dos testes. O CI gera automaticamente:

- `latest-test-dashboard.html`: visão executiva dos resultados JUnit e da cobertura;
- `latest-test-summary.md`: resumo publicado no GitHub Actions;
- relatórios HTML detalhados, disponíveis no artefato `test-reports-<run>`.

## Capturas recomendadas

Salve imagens em `screenshots/` usando o padrão `AAAA-MM-DD-nome-da-tela.png`:

1. `docker-compose-healthy`: `docker compose ps` com os três serviços saudáveis;
2. `fluxo-e2e`: criação de usuário, pedido e pagamento concluída;
3. `test-dashboard`: o arquivo `latest-test-dashboard.html` aberto no navegador;
4. `coverage-python`: `testing-suite/reports/coverage/index.html`;
5. `github-actions`: execução verde mostrando as etapas Python, Node.js e Go;
6. `observability`: dashboard Grafana/Kiali com tráfego entre serviços.

Não inclua tokens, cookies, e-mails reais, segredos, nomes de clusters ou outros dados sensíveis nas capturas.

## Como atualizar

Após executar os testes com relatórios JUnit:

```bash
python testing-suite/utils/generate_test_dashboard.py
```

Abra `docs/evidence/latest-test-dashboard.html`, revise os números e faça a captura.
