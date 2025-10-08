@echo off
echo ========================================
echo 🎓 ML TRAINING WORKSHOP PARA QA ENGINEERS
echo ========================================
echo.
echo Este workshop te ensinará a treinar modelos ML para testing!
echo.
echo Modelos que você vai treinar:
echo 1. 🎯 Preditor de Falhas de Testes
echo 2. ⭐ Priorizador Inteligente de Testes  
echo 3. 🔄 Detector de Testes Flaky
echo.
echo Pressione qualquer tecla para começar...
pause >nul

cd testing-suite\ai-testing

echo.
echo 🔄 Executando workshop de ML...
python ml_training_workshop.py

echo.
echo ✅ Workshop concluído!
echo.
echo 📁 Arquivos gerados:
echo   • models/ - Modelos treinados (.pkl)
echo   • reports_ml/ - Relatórios e métricas (.json)
echo.
echo 🚀 Próximos passos:
echo   1. Explore os modelos treinados
echo   2. Execute: python -c "import pickle; print(pickle.load(open('models/failure_predictor.pkl', 'rb')))"
echo   3. Leia o guia completo: AI_ML_DEEP_DIVE_GUIDE.md
echo.
pause