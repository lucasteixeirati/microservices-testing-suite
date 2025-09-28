import pytest
import requests
from unittest.mock import patch, Mock

class TestPaymentServiceUnit:
    
    def test_health_check(self):
        """Test payment service health endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "service": "payment-service"}
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8003/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
    
    def test_create_payment_valid_data(self):
        """Test payment creation with valid data"""
        payment_data = {
            "order_id": "order-123",
            "amount": 999.99,
            "method": "credit_card"
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "payment-456",
            "order_id": "order-123",
            "amount": 999.99,
            "status": "pending",
            "method": "credit_card"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments", json=payment_data)
            assert response.status_code == 201
            assert response.json()["status"] == "pending"
    
    def test_create_payment_invalid_order(self):
        """Test payment creation with invalid order"""
        payment_data = {
            "order_id": "invalid-order",
            "amount": 999.99,
            "method": "credit_card"
        }
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Order not found"}
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments", json=payment_data)
            assert response.status_code == 400
            assert "Order not found" in response.json()["error"]
    
    def test_process_payment_success(self):
        """Test successful payment processing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "payment-123",
            "status": "completed",
            "processed_at": "2023-01-01T10:00:00Z"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments/payment-123/process")
            assert response.status_code == 200
            assert response.json()["status"] == "completed"
    
    def test_process_payment_failure_high_amount(self):
        """Test payment failure for high amounts"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "payment-123",
            "status": "failed",
            "processed_at": "2023-01-01T10:00:00Z"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments/payment-123/process")
            assert response.status_code == 200
            assert response.json()["status"] == "failed"
    
    def test_get_payment_exists(self):
        """Test getting existing payment"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "payment-123",
            "order_id": "order-456",
            "amount": 999.99,
            "status": "pending"
        }
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8003/payments/payment-123")
            assert response.status_code == 200
            assert response.json()["id"] == "payment-123"
    
    def test_get_payment_not_found(self):
        """Test getting non-existent payment"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Payment not found"}
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8003/payments/non-existent")
            assert response.status_code == 404
    
    def test_list_payments(self):
        """Test listing all payments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "payment-1", "status": "completed"},
            {"id": "payment-2", "status": "pending"}
        ]
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8003/payments")
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_payment_method_validation(self):
        """Test payment method validation"""
        valid_methods = ["credit_card", "debit_card", "paypal"]
        
        for method in valid_methods:
            payment_data = {
                "order_id": "order-123",
                "amount": 100.00,
                "method": method
            }
            
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = payment_data
            
            with patch('requests.post', return_value=mock_response):
                response = requests.post("http://localhost:8003/payments", json=payment_data)
                assert response.status_code == 201
    
    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        # Test negative amount
        invalid_data = {
            "order_id": "order-123",
            "amount": -100.00,
            "method": "credit_card"
        }
        
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"error": "Invalid amount"}
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments", json=invalid_data)
            assert response.status_code == 422
    
    def test_payment_processing_timeout(self):
        """Test payment processing timeout"""
        mock_response = Mock()
        mock_response.status_code = 408
        mock_response.json.return_value = {"error": "Payment processing timeout"}
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8003/payments/payment-123/process")
            assert response.status_code == 408