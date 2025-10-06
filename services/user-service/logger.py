import logging
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Remove default handlers
        self.logger.handlers.clear()
        
        # Add structured handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter(service_name))
        self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)

class StructuredFormatter(logging.Formatter):
    def __init__(self, service_name: str):
        self.service_name = service_name
        super().__init__()
    
    def format(self, record):
        # Sanitize message to prevent log injection
        sanitized_message = self._sanitize_log_message(record.getMessage())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "message": sanitized_message,
            "logger": record.name
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated', 
                              'thread', 'threadName', 'processName', 'process',
                              'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
        
        return json.dumps(log_entry)
    
    def _sanitize_log_message(self, message: str) -> str:
        """Sanitize log message to prevent injection attacks and data leaks"""
        if not isinstance(message, str):
            message = str(message)
        
        # Remove control characters and newlines that could break log format
        # This prevents log injection attacks
        sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', message)
        
        # Remove potential ANSI escape sequences
        sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
        
        # Mask sensitive data patterns
        sanitized = self._mask_sensitive_data(sanitized)
        
        # Limit message length to prevent log flooding
        if len(sanitized) > 1000:
            sanitized = sanitized[:997] + '...'
        
        return sanitized
    
    def _mask_sensitive_data(self, message: str) -> str:
        """Mask sensitive information in log messages"""
        # Mask email addresses (keep domain for debugging)
        message = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 
                        r'***@\2', message)
        
        # Mask potential passwords/tokens
        message = re.sub(r'(password|token|secret|key)\s*[:=]\s*["\']?([^\s"\',}]+)', 
                        r'\1: ***', message, flags=re.IGNORECASE)
        
        # Mask credit card numbers
        message = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 
                        '****-****-****-****', message)
        
        # Mask phone numbers
        message = re.sub(r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b', 
                        '***-***-****', message)
        
        return message

# Global logger instance
logger = StructuredLogger("user-service")