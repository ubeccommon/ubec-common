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
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8001"))
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ========================================================================
    # BACKEND API CONFIGURATION
    # ========================================================================
    
    BACKEND_API_URL: str = os.getenv(
        "BACKEND_API_URL",
        "http://92.205.230.245:8000"
    )
    
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "")
    BACKEND_TIMEOUT: int = int(os.getenv("BACKEND_TIMEOUT", "30"))
    
    # ========================================================================
    # CACHE SETTINGS
    # ========================================================================
    
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "30"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # ========================================================================
    # CORS SETTINGS
    # ========================================================================
    
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:8001,http://127.0.0.1:8001,http://92.205.230.245:8001"
    ).split(",")
    
    ALLOWED_HOSTS: List[str] = os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,92.205.230.245,ubec.network,www.ubec.network"
    ).split(",")
    
    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    
    ENABLE_API_DOCS: bool = os.getenv("ENABLE_API_DOCS", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_WEBSOCKETS: bool = os.getenv("ENABLE_WEBSOCKETS", "false").lower() == "true"
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # ========================================================================
    # SECURITY
    # ========================================================================
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # ========================================================================
    # DATABASE (Optional)
    # ========================================================================
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ubec:ubec@localhost:5432/ubec_protocol"
    )
    
    # ========================================================================
    # STELLAR NETWORK (Optional)
    # ========================================================================
    
    STELLAR_NETWORK: str = os.getenv("STELLAR_NETWORK", "public")
    STELLAR_HORIZON_URL: str = os.getenv(
        "STELLAR_HORIZON_URL",
        "https://horizon.stellar.org"
    )
    
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
    
    @property
    def CONFIG_DIR(self) -> Path:
        """Configuration directory."""
        return self.BASE_DIR / "config"
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"
    
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.APP_ENV == "staging"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"
    
    def validate_security(self) -> List[str]:
        """
        Validate security settings and return warnings.
        
        Returns:
            List of security warnings (empty list if all good)
        """
        warnings = []
        
        if self.is_production():
            if self.SECRET_KEY == "dev-secret-key-change-in-production":
                warnings.append("⚠️  SECRET_KEY is using default value in production!")
            
            if len(self.SECRET_KEY) < 32:
                warnings.append("⚠️  SECRET_KEY should be at least 32 characters")
            
            if self.APP_HOST == "0.0.0.0":
                warnings.append("⚠️  APP_HOST exposed to all interfaces (use reverse proxy)")
            
            if self.ENABLE_API_DOCS:
                warnings.append("⚠️  API docs enabled in production")
            
            if self.BACKEND_API_URL.startswith("http://"):
                warnings.append("⚠️  Backend URL uses HTTP (not HTTPS)")
        
        return warnings
    
    def display_config(self) -> str:
        """Generate formatted display of configuration (safe for logging)."""
        lines = [
            "=" * 70,
            "UBEC PROTOCOL - CONFIGURATION",
            "=" * 70,
            f"Application:     {self.APP_NAME} v{self.APP_VERSION}",
            f"Environment:     {self.APP_ENV}",
            f"Host:            {self.APP_HOST}:{self.APP_PORT}",
            f"Log Level:       {self.LOG_LEVEL}",
            "",
            "Backend API:",
            f"  URL:           {self.BACKEND_API_URL}",
            f"  Timeout:       {self.BACKEND_TIMEOUT}s",
            f"  Auth:          {'Yes' if self.BACKEND_API_KEY else 'No'}",
            "",
            "Cache:",
            f"  TTL:           {self.CACHE_TTL_SECONDS}s",
            f"  Max Size:      {self.CACHE_MAX_SIZE} items",
            "",
            "Features:",
            f"  API Docs:      {self.ENABLE_API_DOCS}",
            f"  Metrics:       {self.ENABLE_METRICS}",
            f"  WebSockets:    {self.ENABLE_WEBSOCKETS}",
            f"  Rate Limiting: {self.RATE_LIMIT_ENABLED}",
            "",
            "CORS:",
            f"  Origins:       {len(self.ALLOWED_ORIGINS)} configured",
            f"  Hosts:         {len(self.ALLOWED_HOSTS)} configured",
            "",
            "Paths:",
            f"  Base:          {self.BASE_DIR}",
            f"  Templates:     {self.TEMPLATES_DIR}",
            f"  Static:        {self.STATIC_DIR}",
            "=" * 70,
        ]
        
        warnings = self.validate_security()
        if warnings:
            lines.append("")
            lines.append("SECURITY WARNINGS:")
            lines.extend(warnings)
            lines.append("=" * 70)
        
        return "\n".join(lines)
    
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
        
        # Validate backend URL
        if not self.BACKEND_API_URL.startswith(("http://", "https://")):
            raise ValueError(f"BACKEND_API_URL must start with http:// or https://")
    
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
            f"BACKEND_API_URL={self.BACKEND_API_URL}"
            f")"
        )


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

# Create a singleton instance
settings = Settings()


# Log security warnings on import if in production
if settings.is_production():
    warnings = settings.validate_security()
    if warnings:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("=" * 70)
        logger.warning("SECURITY WARNINGS:")
        for warning in warnings:
            logger.warning(f"  {warning}")
        logger.warning("=" * 70)


# ========================================================================
# USAGE EXAMPLES
# ========================================================================

if __name__ == "__main__":
    """
    Test configuration loading.
    
    Usage:
        python -m config.settings
    """
    print(settings.display_config())
    
    print("\n" + "=" * 70)
    print("VALIDATION TEST")
    print("=" * 70)
    
    security_warnings = settings.validate_security()
    if security_warnings:
        print("⚠️  Security issues detected:")
        for warning in security_warnings:
            print(f"  {warning}")
    else:
        print("✓ No security issues detected")
    
    print("=" * 70)
    print("✓ Configuration loaded successfully")
    print("=" * 70)
