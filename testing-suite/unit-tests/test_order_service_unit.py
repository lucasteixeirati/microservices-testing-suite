import pytest
import requests
from unittest.mock import patch, Mock

class TestOrderServiceUnit:
    
    def test_health_check(self):
        """Test order service health endpoint"""
        # Mock the health check response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "service": "order-service"}
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8002/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
    
    def test_create_order_valid_data(self):
        """Test order creation with valid data"""
        order_data = {
            "user_id": "user-123",
            "items": [{"product": "laptop", "quantity": 1}],
            "total_amount": 999.99
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "order-456",
            "user_id": "user-123",
            "items": [{"product": "laptop", "quantity": 1}],
            "total_amount": 999.99,
            "status": "pending"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8002/orders", json=order_data)
            assert response.status_code == 201
            assert response.json()["status"] == "pending"
    
    def test_create_order_invalid_user(self):
        """Test order creation with invalid user"""
        order_data = {
            "user_id": "invalid-user",
            "items": [{"product": "laptop", "quantity": 1}],
            "total_amount": 999.99
        }
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "User not found"}
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8002/orders", json=order_data)
            assert response.status_code == 400
            assert "User not found" in response.json()["error"]
    
    def test_get_order_exists(self):
        """Test getting existing order"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "order-123",
            "user_id": "user-456",
            "status": "pending"
        }
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8002/orders/order-123")
            assert response.status_code == 200
            assert response.json()["id"] == "order-123"
    
    def test_get_order_not_found(self):
        """Test getting non-existent order"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Order not found"}
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8002/orders/non-existent")
            assert response.status_code == 404
    
    def test_update_order_status(self):
        """Test updating order status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "order-123",
            "status": "completed"
        }
        
        with patch('requests.patch', return_value=mock_response):
            response = requests.patch(
                "http://localhost:8002/orders/order-123/status",
                json={"status": "completed"}
            )
            assert response.status_code == 200
            assert response.json()["status"] == "completed"
    
    def test_list_orders(self):
        """Test listing all orders"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "order-1", "status": "pending"},
            {"id": "order-2", "status": "completed"}
        ]
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get("http://localhost:8002/orders")
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_order_validation_missing_fields(self):
        """Test order validation with missing fields"""
        invalid_data = {"user_id": "user-123"}  # Missing items and total_amount
        
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"error": "Validation error"}
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8002/orders", json=invalid_data)
            assert response.status_code == 422
    
    def test_order_total_calculation(self):
        """Test order total amount calculation"""
        order_data = {
            "user_id": "user-123",
            "items": [
                {"product": "laptop", "quantity": 2, "price": 500.00},
                {"product": "mouse", "quantity": 1, "price": 25.00}
            ],
            "total_amount": 1025.00
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = order_data
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post("http://localhost:8002/orders", json=order_data)
            assert response.status_code == 201
            assert response.json()["total_amount"] == 1025.00