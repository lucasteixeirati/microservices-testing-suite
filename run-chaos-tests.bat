@echo off
echo ========================================
echo    CHAOS ENGINEERING TESTS RUNNER
echo ========================================
echo.

REM Check if services are running
echo [INFO] Checking if services are running...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] User Service not running on port 8001
    echo [INFO] Please start services first:
    echo   - Docker: start-services-docker.bat
    echo   - Local: run-local.bat
    pause
    exit /b 1
)

curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Order Service not running on port 8002
    echo [INFO] Please start services first
    pause
    exit /b 1
)

curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Payment Service not running on port 8003
    echo [INFO] Please start services first
    pause
    exit /b 1
)

echo [SUCCESS] All services are running!
echo.

REM Set environment variable for local testing
set DOCKER_ENV=false

echo [INFO] Running Chaos Engineering Tests...
echo [INFO] Environment: Local Mode
echo [INFO] Total Tests: 13 chaos scenarios
echo.

cd testing-suite

REM Run chaos tests with detailed output
python -m pytest chaos-tests/ -v --tb=short -s --maxfail=5

echo.
echo ========================================
echo         CHAOS TESTS COMPLETED
echo ========================================
echo.
echo Results saved in testing-suite/.pytest_cache/
echo.
pause