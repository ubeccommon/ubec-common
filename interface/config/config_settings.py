"""
UBEC Protocol - Configuration Settings
======================================

Centralized configuration management using environment variables.

This module implements:
    - Principle #4: Single Source of Truth for configuration
    - Principle #8: No Duplicate Configuration
    - Principle #11: Comprehensive Documentation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
from pathlib import Path
from typing import List


class Settings:
    """
    Application configuration settings.
    
    All settings are loaded from environment variables with sensible defaults.
    This ensures configuration is externalized and environment-specific.
    """
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    
    APP_NAME: str = "UBEC Protocol Network"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ========================================================================
    # API DOCUMENTATION
    # ========================================================================
    
    ENABLE_API_DOCS: bool = os.getenv("ENABLE_API_DOCS", "true").lower() == "true"
    
    # ========================================================================
    # CORS SETTINGS
    # ========================================================================
    
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000,http://92.205.230.245:8001"
    ).split(",")
    
    # ========================================================================
    # BACKEND API (Optional - falls back to local data if not available)
    # ========================================================================
    
    BACKEND_API_URL: str = os.getenv(
        "BACKEND_API_URL",
        "http://92.205.230.245:8000"  # Default backend URL
    )
    
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "")
    
    # ========================================================================
    # DATABASE (Optional - only if using database directly)
    # ========================================================================
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ubec:ubec@localhost:5432/ubec_protocol"
    )
    
    # ========================================================================
    # STELLAR NETWORK (Optional - for reference)
    # ========================================================================
    
    STELLAR_NETWORK: str = os.getenv("STELLAR_NETWORK", "public")
    STELLAR_HORIZON_URL: str = os.getenv(
        "STELLAR_HORIZON_URL",
        "https://horizon.stellar.org"
    )
    
    # ========================================================================
    # SECURITY
    # ========================================================================
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # ========================================================================
    # PATHS
    # ========================================================================
    
    @property
    def BASE_DIR(self) -> Path:
        """Base directory of the application."""
        return Path(__file__).parent.parent
    
    @property
    def TEMPLATES_DIR(self) -> Path:
        """Templates directory."""
        return self.BASE_DIR / "templates"
    
    @property
    def STATIC_DIR(self) -> Path:
        """Static files directory."""
        return self.BASE_DIR / "static"
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def __init__(self):
        """Initialize and validate settings."""
        self._validate()
    
    def _validate(self):
        """Validate critical settings."""
        # Validate port number
        if not (1 <= self.APP_PORT <= 65535):
            raise ValueError(f"Invalid APP_PORT: {self.APP_PORT}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {self.LOG_LEVEL}")
    
    # ========================================================================
    # DISPLAY
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of settings (safe - no secrets)."""
        return (
            f"Settings("
            f"APP_ENV={self.APP_ENV}, "
            f"APP_HOST={self.APP_HOST}, "
            f"APP_PORT={self.APP_PORT}, "
            f"LOG_LEVEL={self.LOG_LEVEL}"
            f")"
        )


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

# Create a singleton instance
settings = Settings()


# ========================================================================
# USAGE EXAMPLES
# ========================================================================

if __name__ == "__main__":
    """
    Test configuration loading.
    
    Usage:
        python -m config.settings
    """
    print("=" * 70)
    print("UBEC PROTOCOL - CONFIGURATION")
    print("=" * 70)
    print(f"Environment: {settings.APP_ENV}")
    print(f"Host: {settings.APP_HOST}")
    print(f"Port: {settings.APP_PORT}")
    print(f"Log Level: {settings.LOG_LEVEL}")
    print(f"Backend API: {settings.BACKEND_API_URL}")
    print(f"API Docs Enabled: {settings.ENABLE_API_DOCS}")
    print(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")
    print(f"Base Directory: {settings.BASE_DIR}")
    print(f"Templates Directory: {settings.TEMPLATES_DIR}")
    print(f"Static Directory: {settings.STATIC_DIR}")
    print("=" * 70)
    print("✓ Configuration loaded successfully")
    print("=" * 70)
