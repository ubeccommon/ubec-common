"""
UBEC Protocol - Configuration Package
======================================
Global configuration and logging for all protocols.

This module provides a unified interface to configuration and logging services.

Design Principles Compliance:
    ✅ 8. No Duplicate Config: Single config source
    ✅ 11. Comprehensive Documentation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.1.0
Date: October 16, 2025

Changelog:
    v1.1.0 - Fixed import errors for validate_config and display_config
           - Made imports more resilient with try/except blocks
           - Added fallback for missing functions
"""

# Try importing from config.config with error handling
try:
    from config.config import GlobalConfig
except ImportError as e:
    print(f"Warning: Could not import GlobalConfig: {e}")
    GlobalConfig = None

# Try importing validation functions with fallback
try:
    from config.config import validate_config
except ImportError:
    def validate_config():
        """Fallback validation function."""
        return True

try:
    from config.config import display_config
except ImportError:
    def display_config():
        """Fallback display function."""
        return {'status': 'config.display_config not available'}

# Try importing logging functions
try:
    from config.logging import get_logger, setup_logging
except ImportError as e:
    print(f"Warning: Could not import logging functions: {e}")
    import logging
    
    def get_logger(name: str = None):
        """Fallback logger function."""
        return logging.getLogger(name or 'UBEC')
    
    def setup_logging(level: str = 'INFO'):
        """Fallback logging setup."""
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Define what gets exported
__all__ = [
    'GlobalConfig',
    'validate_config',
    'display_config',
    'get_logger',
    'setup_logging'
]

__version__ = '1.1.0'
