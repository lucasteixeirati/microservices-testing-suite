import pytest
import re
from datetime import datetime

class TestValidationUtils:
    """Test utility functions for validation across services"""
    
    def test_email_validation_comprehensive(self):
        """Test comprehensive email validation"""
        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            # Check for consecutive dots
            if '..' in email:
                return False
            return re.match(pattern, email) is not None and len(email) <= 254
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@example.com"
        ]
        
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user@domain",
            "user..name@domain.com",
            "a" * 250 + "@domain.com"  # Too long
        ]
        
        for email in valid_emails:
            assert is_valid_email(email), f"Should be valid: {email}"
        
        for email in invalid_emails:
            assert not is_valid_email(email), f"Should be invalid: {email}"
    
    def test_id_validation_utility(self):
        """Test ID validation utility function"""
        def is_valid_id(id_value, max_length=50):
            pattern = r'^[a-zA-Z0-9-]+$'
            return (re.match(pattern, id_value) is not None and 
                   0 < len(id_value) <= max_length)
        
        valid_ids = ["user-123", "ORDER-456", "abc123", "a"]
        invalid_ids = ["", "user@123", "user 123", "a" * 51]
        
        for id_val in valid_ids:
            assert is_valid_id(id_val), f"Should be valid: {id_val}"
        
        for id_val in invalid_ids:
            assert not is_valid_id(id_val), f"Should be invalid: {id_val}"
    
    def test_amount_validation_utility(self):
        """Test amount validation utility"""
        def is_valid_amount(amount, min_val=0.01, max_val=10000.00):
            return (isinstance(amount, (int, float)) and 
                   min_val <= amount <= max_val)
        
        valid_amounts = [0.01, 10.50, 999.99, 10000.00]
        invalid_amounts = [0, -1, 10000.01, "100", None]
        
        for amount in valid_amounts:
            assert is_valid_amount(amount), f"Should be valid: {amount}"
        
        for amount in invalid_amounts:
            assert not is_valid_amount(amount), f"Should be invalid: {amount}"
    
    def test_string_sanitization_utility(self):
        """Test string sanitization utility"""
        def sanitize_string(text, max_length=100):
            if not isinstance(text, str):
                return ""
            sanitized = text.strip()
            return sanitized[:max_length] if len(sanitized) <= max_length else ""
        
        test_cases = [
            ("  hello world  ", "hello world"),
            ("valid text", "valid text"),
            ("", ""),
            ("a" * 101, ""),  # Too long
            (123, ""),  # Not a string
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_string(input_text)
            assert result == expected, f"Input: {input_text}, Expected: {expected}, Got: {result}"
    
    def test_timestamp_validation_utility(self):
        """Test timestamp validation utility"""
        def is_valid_timestamp(timestamp):
            if isinstance(timestamp, datetime):
                return True
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return True
                except ValueError:
                    return False
            return False
        
        valid_timestamps = [
            datetime.now(),
            "2024-01-01T10:00:00",
            "2024-12-31T23:59:59Z"
        ]
        
        invalid_timestamps = [
            "invalid-date",
            "2024-13-01T10:00:00",  # Invalid month
            123456789,
            None
        ]
        
        for ts in valid_timestamps:
            assert is_valid_timestamp(ts), f"Should be valid: {ts}"
        
        for ts in invalid_timestamps:
            assert not is_valid_timestamp(ts), f"Should be invalid: {ts}"
    
    def test_status_validation_utility(self):
        """Test status validation utility"""
        def is_valid_status(status, valid_statuses):
            return isinstance(status, str) and status in valid_statuses
        
        order_statuses = ["pending", "confirmed", "processing", "completed", "cancelled"]
        payment_statuses = ["pending", "processing", "completed", "failed"]
        
        # Test order statuses
        assert is_valid_status("pending", order_statuses)
        assert is_valid_status("completed", order_statuses)
        assert not is_valid_status("invalid", order_statuses)
        assert not is_valid_status(123, order_statuses)
        
        # Test payment statuses
        assert is_valid_status("pending", payment_statuses)
        assert is_valid_status("failed", payment_statuses)
        assert not is_valid_status("cancelled", payment_statuses)  # Not valid for payments
    
    def test_url_validation_utility(self):
        """Test URL validation utility for SSRF prevention"""
        def is_allowed_url(url, allowed_hosts):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return (parsed.scheme == 'http' and 
                       parsed.hostname in allowed_hosts)
            except:
                return False
        
        allowed_hosts = ['localhost', 'user-service', 'order-service']
        
        valid_urls = [
            "http://localhost:8001/users/123",
            "http://user-service:8001/health",
            "http://order-service:8002/orders"
        ]
        
        invalid_urls = [
            "https://localhost:8001/users",  # Wrong scheme
            "http://evil.com/users",         # Not allowed host
            "ftp://localhost/file",          # Wrong scheme
            "invalid-url"                    # Invalid format
        ]
        
        for url in valid_urls:
            assert is_allowed_url(url, allowed_hosts), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not is_allowed_url(url, allowed_hosts), f"Should be invalid: {url}"