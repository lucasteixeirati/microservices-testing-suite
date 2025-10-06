@echo off
echo ========================================
echo  MENU DE TESTES ML INDIVIDUAIS
echo ========================================
echo.
echo Escolha o componente para testar:
echo.
echo 1. Simple ML Demo (basico, sem dependencias pesadas)
echo 2. Bug Pattern Analyzer (ML avancado)
echo 3. Smart Test Prioritizer (ML + otimizacao)
echo 4. Advanced ML Engine (multiplos algoritmos)
echo 5. Test Case Generator (geracao automatica)
echo 6. AI Testing Dashboard (interface web)
echo 7. ML Integration Suite (todos juntos)
echo 8. Testar TODOS os componentes
echo 9. Sair
echo.
set /p choice="Digite sua escolha (1-9): "

if "%choice%"=="1" (
    echo Executando Simple ML Demo...
    python ai-testing/simple_ml_demo.py
) else if "%choice%"=="2" (
    echo Executando Bug Pattern Analyzer...
    python ai-testing/bug_pattern_analyzer.py
) else if "%choice%"=="3" (
    echo Executando Smart Test Prioritizer...
    python ai-testing/smart_test_prioritizer.py
) else if "%choice%"=="4" (
    echo Executando Advanced ML Engine...
    python ai-testing/advanced_ml_engine.py
) else if "%choice%"=="5" (
    echo Executando Test Case Generator...
    python ai-testing/test_case_generator.py
) else if "%choice%"=="6" (
    echo Iniciando AI Testing Dashboard...
    echo Acesse: http://localhost:5000
    python ai-testing/ai_testing_dashboard.py
) else if "%choice%"=="7" (
    echo Executando ML Integration Suite...
    python ai-testing/ml_integration_demo_clean.py
) else if "%choice%"=="8" (
    call test-all-ml.bat
) else if "%choice%"=="9" (
    exit /b 0
) else (
    echo Opcao invalida!
    pause
    goto :eof
)

echo.
echo Teste concluido!
pause