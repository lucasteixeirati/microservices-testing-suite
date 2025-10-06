@echo off
echo ========================================
echo  TESTANDO TODAS AS FUNCIONALIDADES ML
echo ========================================

echo.
echo [1/6] Testando Simple ML Demo...
python ai-testing/simple_ml_demo.py
if %errorlevel% neq 0 (
    echo ERRO: Simple ML Demo falhou
    pause
    exit /b 1
)

echo.
echo [2/6] Testando Bug Pattern Analyzer...
python ai-testing/bug_pattern_analyzer.py
if %errorlevel% neq 0 (
    echo ERRO: Bug Pattern Analyzer falhou
    pause
    exit /b 1
)

echo.
echo [3/6] Testando Smart Test Prioritizer...
python ai-testing/smart_test_prioritizer.py
if %errorlevel% neq 0 (
    echo ERRO: Smart Test Prioritizer falhou
    pause
    exit /b 1
)

echo.
echo [4/6] Testando Advanced ML Engine...
python ai-testing/advanced_ml_engine.py
if %errorlevel% neq 0 (
    echo ERRO: Advanced ML Engine falhou
    pause
    exit /b 1
)

echo.
echo [5/6] Testando Test Case Generator...
python ai-testing/test_case_generator.py
if %errorlevel% neq 0 (
    echo ERRO: Test Case Generator falhou
    pause
    exit /b 1
)

echo.
echo [6/6] Testando ML Integration Suite Completa...
python ai-testing/ml_integration_demo_clean.py
if %errorlevel% neq 0 (
    echo ERRO: ML Integration Suite falhou
    pause
    exit /b 1
)

echo.
echo ========================================
echo  TODOS OS TESTES ML CONCLUIDOS!
echo ========================================
echo.
echo Arquivos gerados:
dir /b ml_analysis_results_*.json 2>nul
echo.
echo Para ver o dashboard AI:
echo python ai-testing/ai_testing_dashboard.py
echo.
pause