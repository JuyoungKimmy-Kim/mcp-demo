"""Configuration management for MCP Hub MCP Server"""

import os
from typing import Optional


class Config:
    """Application configuration"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        # API Configuration
        self.api_base_url = os.getenv("MCP_HUB_URL", "http://localhost:8000/api/v1")

        # SSL Configuration
        verify_ssl_env = os.getenv("VERIFY_SSL", "true").lower()
        self.verify_ssl = verify_ssl_env not in ("false", "0", "no")

        # Server Configuration
        self.server_host = os.getenv("HOST", "0.0.0.0")
        self.server_port = int(os.getenv("PORT", "8080"))

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def api_timeout(self) -> float:
        """HTTP request timeout in seconds"""
        return 30.0


# Global config instance
config = Config()
