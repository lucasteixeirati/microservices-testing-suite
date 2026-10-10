import json
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../services/user-service"))

from config import ConfigBuilder, ServiceConfig, create_config
from logger import StructuredFormatter


class TestUserServiceSupport:
    def test_default_and_built_configuration(self):
        assert ServiceConfig().port == 8001
        config = (
            ConfigBuilder()
            .host("127.0.0.1")
            .port(9001)
            .log_level("DEBUG")
            .csrf_settings(ttl=120, max_tokens=50)
            .build()
        )
        assert config == ServiceConfig(
            host="127.0.0.1",
            port=9001,
            log_level="DEBUG",
            csrf_ttl=120,
            max_csrf_tokens=50,
        )

    def test_application_configuration(self):
        config = create_config()
        assert config.host == "0.0.0.0"
        assert config.port == 8001
        assert config.csrf_ttl == 3600

    def test_log_sanitization_masks_sensitive_values(self):
        formatter = StructuredFormatter("test-service")
        message = formatter._sanitize_log_message(
            "user@example.com\npassword=secret 4111-1111-1111-1111"
        )
        assert "\n" not in message
        assert "user@example.com" not in message
        assert "password: ***" in message
        assert "4111-1111-1111-1111" not in message

    def test_structured_log_is_valid_json(self):
        formatter = StructuredFormatter("test-service")
        record = logging.LogRecord(
            name="unit",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="created user",
            args=(),
            exc_info=None,
        )
        record.request_id = "req-123"
        payload = json.loads(formatter.format(record))
        assert payload["service"] == "test-service"
        assert payload["message"] == "created user"
        assert payload["request_id"] == "req-123"

    def test_long_logs_are_bounded(self):
        formatter = StructuredFormatter("test-service")
        sanitized = formatter._sanitize_log_message("x" * 1200)
        assert len(sanitized) == 1000
        assert sanitized.endswith("...")
