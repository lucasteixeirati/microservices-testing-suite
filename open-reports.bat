@echo off
echo Abrindo todos os relatorios automaticamente...

REM Dashboard Principal
start "" "dashboard\index.html"

REM Relatorio de Load Test mais recente
start "" "testing-suite\reports\load_test_report_20251006_120743.html"

REM Relatorio de Testes Completo
start "" "testing-suite\reports\test_suite_report.html"

REM Dashboards de Observabilidade
start "" "dashboard\grafana-demo.html"
start "" "dashboard\kibana-demo.html"
start "" "dashboard\kiali-demo.html"

echo Todos os relatorios foram abertos no navegador!
echo.
echo Para iniciar o AI Dashboard interativo:
echo cd testing-suite\ai-testing
echo python ai_testing_dashboard.py
echo Depois acesse: http://localhost:5000
pause