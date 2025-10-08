@echo off
echo 🚀 Starting Microservices...

REM Start services with Docker Compose
docker-compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak > nul

REM Check if services are running
echo 📊 Service Status:
docker-compose ps

echo ✅ Services started! You can now run tests with:
echo cd testing-suite ^&^& python utils/test_runner.py --test-type all