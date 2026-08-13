"""
UBEC Protocol - Logging Configuration
======================================
Centralized logging setup for all protocols.

This module provides a standardized logging interface for the entire UBEC system,
ensuring consistent log formatting, level management, and output handling across
all modules and services.

Design Principles Applied:
- Single Source of Truth: Configuration values sourced from GlobalConfig
- No Duplicate Configuration: All logging settings defined once in GlobalConfig
- Clear Separation of Concerns: Logging logic isolated from business logic
- Comprehensive Documentation: Full docstrings for all public functions

Attribution:
This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Version: 1.1
Date: October 12, 2025
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = 'ubec',
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_to_file: Optional[bool] = None
) -> logging.Logger:
    """
    Setup and configure logger for UBEC protocols.
    
    This function creates a properly configured logger with both console and 
    optional file output. It respects the project's configuration management
    principles by sourcing defaults from GlobalConfig while allowing override.
    
    Args:
        name: Logger name (default: 'ubec'). Use module name for hierarchical logging.
        log_level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, uses GlobalConfig.LOG_LEVEL.
        log_file: Path to log file. If None, uses GlobalConfig.LOG_FILE_PATH.
        log_to_file: Enable file logging. If None, determines from GlobalConfig.
        
    Returns:
        Configured logger instance ready for use.
        
    Raises:
        ValueError: If log_level is invalid.
        OSError: If log file directory cannot be created.
        
    Example:
        >>> logger = setup_logging('my_module', log_level='DEBUG')
        >>> logger.info("Module initialized")
    """
    # Import here to avoid circular imports at module level
    try:
        from config.config import GlobalConfig
    except ImportError:
        # Fallback if config not available
        GlobalConfig = None
    
    # Safely get configuration values with fallbacks
    if GlobalConfig:
        if log_level is None:
            log_level = getattr(GlobalConfig, 'LOG_LEVEL', 'INFO')
            # Handle case where LOG_LEVEL might be a property
            if hasattr(log_level, '__call__'):
                log_level = 'INFO'
            elif not isinstance(log_level, str):
                log_level = 'INFO'
                
        if log_file is None:
            log_file = getattr(GlobalConfig, 'LOG_FILE_PATH', None)
            
        if log_to_file is None:
            # Check for explicit LOG_TO_FILE flag, fallback to checking if path exists
            log_to_file = getattr(GlobalConfig, 'LOG_TO_FILE', None)
            if log_to_file is None:
                # Enable file logging if a log file path is configured
                log_to_file = bool(log_file)
    else:
        # Fallback defaults when GlobalConfig unavailable
        log_level = log_level or 'INFO'
        log_file = log_file or None
        log_to_file = log_to_file if log_to_file is not None else False
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Set log level - validate and convert to logging constant
    try:
        level = getattr(logging, str(log_level).upper(), None)
        if level is None:
            raise ValueError(f"Invalid log level: {log_level}")
    except (AttributeError, TypeError):
        level = logging.INFO
        
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Get format strings from config with fallbacks
    if GlobalConfig:
        log_format = getattr(
            GlobalConfig, 
            'LOG_FORMAT', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        log_date_format = getattr(
            GlobalConfig,
            'LOG_DATE_FORMAT',
            '%Y-%m-%d %H:%M:%S'
        )
        log_max_bytes = getattr(GlobalConfig, 'LOG_MAX_BYTES', 10485760)  # 10MB
        log_backup_count = getattr(GlobalConfig, 'LOG_BACKUP_COUNT', 5)
    else:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_date_format = '%Y-%m-%d %H:%M:%S'
        log_max_bytes = 10485760  # 10MB
        log_backup_count = 5
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=log_date_format)
    
    # Console handler - always enabled
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - optional
    if log_to_file and log_file:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_max_bytes,
                backupCount=log_backup_count
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # Log to console if file handler fails
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a configured logger for a module.
    
    This function provides a convenient interface for modules to obtain their
    own logger instance. It follows the hierarchical naming pattern 'ubec.{name}'
    to maintain clear logger relationships and enable granular control.
    
    Args:
        name: Logger name, typically the module name (e.g., 'database', 'api').
              Will be prefixed with 'ubec.' automatically.
        
    Returns:
        Configured logger instance for the specified module.
        
    Example:
        >>> logger = get_logger('market_data')
        >>> logger.info("Fetching market data...")
        
    Note:
        The root 'ubec' logger is automatically configured on first call.
        All child loggers inherit the root logger's configuration.
    """
    # Check if root logger is already configured
    root_logger = logging.getLogger('ubec')
    if not root_logger.handlers:
        # Setup root logger first
        setup_logging('ubec')
    
    # Return child logger with hierarchical naming
    return logging.getLogger(f'ubec.{name}')


def configure_module_logger(
    module_name: str,
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Configure a module-specific logger with optional level override.
    
    This function allows individual modules to have different log levels
    while maintaining the standard UBEC logging configuration.
    
    Args:
        module_name: Name of the module requesting the logger.
        log_level: Optional log level override for this specific module.
        
    Returns:
        Configured logger instance for the module.
        
    Example:
        >>> logger = configure_module_logger('api', log_level='DEBUG')
        >>> logger.debug("Detailed API debugging enabled")
    """
    logger = get_logger(module_name)
    
    if log_level:
        try:
            level = getattr(logging, log_level.upper(), None)
            if level:
                logger.setLevel(level)
        except (AttributeError, TypeError):
            pass  # Keep existing level if invalid
    
    return logger


# Module initialization
# Note: Deferred initialization to avoid issues during import
_logger: Optional[logging.Logger] = None


def get_module_logger() -> logging.Logger:
    """
    Get the logging module's own logger instance.
    
    Returns:
        Logger instance for the logging module itself.
    """
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


if __name__ == '__main__':
    """
    Test logging configuration with various scenarios.
    
    This test suite validates:
    - Different log levels
    - Module-specific loggers
    - Hierarchical logger relationships
    - Format consistency
    """
    print("=" * 60)
    print("Testing UBEC Logging Configuration")
    print("=" * 60)
    print()
    
    # Test main logger
    print("1. Testing main logger with different levels:")
    print("-" * 60)
    logger = get_logger('test')
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    print()
    
    # Test protocol-specific loggers
    print("2. Testing protocol-specific loggers:")
    print("-" * 60)
    
    ubec_logger = get_logger('UBEC')
    ubec_logger.info("Air protocol (UBEC) logger test")
    
    ubecrc_logger = get_logger('UBECrc')
    ubecrc_logger.info("Water protocol (UBECrc) logger test")
    
    ubecgpi_logger = get_logger('UBECgpi')
    ubecgpi_logger.info("Earth protocol (UBECgpi) logger test")
    
    ubectt_logger = get_logger('UBECtt')
    ubectt_logger.info("Fire protocol (UBECtt) logger test")
    print()
    
    # Test module logger configuration
    print("3. Testing module-specific configuration:")
    print("-" * 60)
    debug_logger = configure_module_logger('debug_module', log_level='DEBUG')
    debug_logger.debug("This DEBUG message should be visible")
    debug_logger.info("This INFO message should also be visible")
    print()
    
    print("=" * 60)
    print("Logging test complete!")
    print("=" * 60)
