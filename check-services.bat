@echo off
echo 🔍 Checking Docker and Services Status...

echo.
echo 📊 Docker Status:
docker --version
if %errorlevel% neq 0 (
    echo ❌ Docker not found or not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

echo.
echo 📊 Docker Compose Status:
docker-compose ps

echo.
echo 📊 Service Health Checks:
echo Checking User Service...
curl -s http://localhost:8001/health || echo ❌ User Service not responding

echo Checking Order Service...
curl -s http://localhost:8002/health || echo ❌ Order Service not responding

echo Checking Payment Service...
curl -s http://localhost:8003/health || echo ❌ Payment Service not responding

echo.
echo 📊 Docker Containers:
docker ps

pause