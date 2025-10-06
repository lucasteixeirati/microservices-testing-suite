@echo off
echo 🧪 Running Simple Test Suite...

echo.
echo [1/4] Contract Tests...
pytest contract-tests/ -v --tb=short

echo.
echo [2/4] Integration Tests...
pytest integration-tests/test_end_to_end_flow.py::TestEndToEndFlow::test_complete_order_flow -v --tb=short

echo.
echo [3/4] API Tests...
pytest api-tests/ -v --tb=short

echo.
echo [4/4] Performance Tests...
python utils/run_performance_tests.py

echo.
echo ✅ Simple test suite completed!
pause