from dataclasses import dataclass
from typing import Optional

@dataclass
class ServiceConfig:
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"
    csrf_ttl: int = 3600
    max_csrf_tokens: int = 1000

class ConfigBuilder:
    def __init__(self):
        self._config = ServiceConfig()
    
    def host(self, host: str):
        self._config.host = host
        return self
    
    def port(self, port: int):
        self._config.port = port
        return self
    
    def log_level(self, level: str):
        self._config.log_level = level
        return self
    
    def csrf_settings(self, ttl: int, max_tokens: int):
        self._config.csrf_ttl = ttl
        self._config.max_csrf_tokens = max_tokens
        return self
    
    def build(self) -> ServiceConfig:
        return self._config

# Usage
def create_config() -> ServiceConfig:
    return (ConfigBuilder()
            .host("0.0.0.0")
            .port(8001)
            .log_level("INFO")
            .csrf_settings(ttl=3600, max_tokens=1000)
            .build())