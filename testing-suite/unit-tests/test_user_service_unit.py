import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/user-service'))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestUserServiceUnit:
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "user-service"
    
    def test_create_user_valid_data(self):
        """Test user creation with valid data"""
        user_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["active"] is True
    
    def test_create_user_invalid_data(self):
        """Test user creation with invalid data"""
        invalid_data = {"name": "Test User"}  # Missing email
        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_user_exists(self):
        """Test getting existing user"""
        # Create user first
        user_data = {"name": "Get Test User", "email": "get@example.com"}
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Get user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_user_not_found(self):
        """Test getting non-existent user"""
        response = client.get("/users/non-existent-id")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_list_users(self):
        """Test listing users"""
        response = client.get("/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_delete_user_exists(self):
        """Test deleting existing user"""
        # Create user first
        user_data = {"name": "Delete Test User", "email": "delete@example.com"}
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Delete user
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 200
        assert "User deleted" in response.json()["message"]
        
        # Verify user is deleted
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        response = client.delete("/users/non-existent-id")
        assert response.status_code == 404