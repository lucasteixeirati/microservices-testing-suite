@echo off
echo ========================================
echo   CHAOS TESTS - DOCKER ENVIRONMENT
echo ========================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found or not running
    echo [INFO] Please install and start Docker Desktop
    pause
    exit /b 1
)

REM Check if containers are running
echo [INFO] Checking Docker containers...
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr microservices-testing-suite >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Microservices containers not found
    echo [INFO] Starting containers with docker-compose...
    docker-compose up -d
    
    REM Wait for services to be ready
    echo [INFO] Waiting for services to be ready...
    timeout /t 30 /nobreak >nul
)

REM Verify services are responding
echo [INFO] Verifying services are responding...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] User Service not responding
    echo [INFO] Check container logs: docker-compose logs user-service
    pause
    exit /b 1
)

curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Order Service not responding
    echo [INFO] Check container logs: docker-compose logs order-service
    pause
    exit /b 1
)

curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Payment Service not responding
    echo [INFO] Check container logs: docker-compose logs payment-service
    pause
    exit /b 1
)

echo [SUCCESS] All services are running in Docker!
echo.

REM Set environment variable for Docker testing
set DOCKER_ENV=true

echo [INFO] Running Chaos Engineering Tests...
echo [INFO] Environment: Docker Mode (with container manipulation)
echo [INFO] Total Tests: 13 chaos scenarios
echo [INFO] Note: Docker tests include container restart/kill/pause operations
echo.

cd testing-suite

REM Install docker library if not present
python -c "import docker" 2>nul || pip install docker

REM Run chaos tests with detailed output
python -m pytest chaos-tests/ -v --tb=short -s --maxfail=3

echo.
echo ========================================
echo         CHAOS TESTS COMPLETED
echo ========================================
echo.
echo Container status after tests:
docker ps --format "table {{.Names}}\t{{.Status}}"
echo.
pause