@echo off
echo 🚀 Starting services locally without Docker...

echo Starting User Service...
start "User Service" cmd /k "cd services\user-service && python main.py"

timeout /t 3

echo Starting Order Service...
start "Order Service" cmd /k "cd services\order-service && npm install && npm start"

timeout /t 3

echo Starting Payment Service...
start "Payment Service" cmd /k "cd services\payment-service && go run main.go"

echo ✅ All services starting in separate windows
echo Wait 30 seconds then run tests with:
echo cd testing-suite && python utils/test_runner.py --test-type integration