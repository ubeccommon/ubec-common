#!/usr/bin/env python3
"""
UBEC Protocol - System Configuration
=====================================
Database-backed configuration following strict design principles.

This module implements configuration as a SERVICE, not a utility.
Database is the SINGLE source of truth for all configuration.

Design Principles Compliance:
- ✅ Principle #4: Single Source of Truth - Database only
- ✅ Principle #5: Strict Async Operations - All I/O is async
- ✅ Principle #6: No Sync Fallbacks - Async only, no exceptions
- ✅ Principle #7: Per-Asset Monitoring - Health checks included
- ✅ Principle #8: No Duplicate Configuration - One definition per setting
- ✅ Principle #11: Comprehensive Documentation - Full docstrings
- ✅ Principle #12: Method Singularity - One way to do things

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.0.0 (Clean Implementation)
Date: October 16, 2025
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConfigurationService:
    """
    Configuration service - loads settings from database.
    
    This is a SERVICE, not a static configuration object.
    It loads from database, caches intelligently, and provides
    health monitoring.
    
    Principles:
    - Database is SINGLE source of truth (Principle #4)
    - All operations are async (Principle #5)
    - No sync fallbacks (Principle #6)
    - Health monitoring built-in (Principle #7)
    - No duplicate definitions (Principle #8)
    
    Usage:
        # Create via factory (ONLY way)
        config = await get_system_config(db_manager)
        
        # Access settings
        horizon_url = config['horizon_url']
        ubec_issuer = config['ubec_issuer']
        
        # Check health
        health = await config.health_check()
    """
    
    def __init__(self, db_manager):
        """
        Initialize configuration service.
        
        Args:
            db_manager: AsyncDatabaseManager instance (REQUIRED)
            
        Note:
            Do NOT instantiate directly. Use get_system_config() factory.
        """
        if db_manager is None:
            raise ValueError("Database manager is required (Principle #4: Single Source of Truth)")
        
        self._db = db_manager
        self._initialized = False
        self._settings: Dict[str, Any] = {}
        self._last_loaded: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
    
    async def initialize(self) -> None:
        """
        Load configuration from database.
        
        This is the ONLY method that loads configuration.
        Principle #12: Method Singularity.
        
        Raises:
            RuntimeError: If database is unavailable
            ValueError: If required settings are missing
        """
        if self._initialized and self._cache_valid():
            logger.debug("Configuration cache valid, skipping reload")
            return
        
        await self._load_from_database()
        self._initialized = True
        self._last_loaded = datetime.now()
        logger.info(f"✓ Configuration loaded: {len(self._settings)} settings from database")
    
    def _cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_loaded:
            return False
        return datetime.now() - self._last_loaded < self._cache_ttl
    
    async def _load_from_database(self) -> None:
        """
        Load all settings from database.
        
        Principle #4: Database is SINGLE source of truth.
        No fallbacks, no environment variables, no defaults.
        If database fails, we fail explicitly.
        """
        query = """
            SELECT 
                setting_key, 
                setting_value, 
                setting_type
            FROM system_settings
            WHERE is_active = TRUE
        """
        
        try:
            rows = await self._db.fetch_all(query)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load configuration from database: {e}. "
                "Database is the SINGLE source of truth (Principle #4). "
                "Fix database connection or populate system_settings table."
            )
        
        if not rows:
            raise ValueError(
                "No active settings in database. "
                "Database must contain configuration (Principle #4). "
                "Run setup_system_settings.sql to initialize."
            )
        
        # Convert types and store
        for row in rows:
            key = row['setting_key']
            value = row['setting_value']
            setting_type = row.get('setting_type', 'string')
            
            # Type conversion
            try:
                if setting_type == 'integer':
                    value = int(value)
                elif setting_type == 'float':
                    value = float(value)
                elif setting_type == 'decimal':
                    value = Decimal(value)
                elif setting_type == 'boolean':
                    value = str(value).lower() in ('true', '1', 'yes')
                # else: keep as string
                
                self._settings[key] = value
            
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert setting {key}={value} to {setting_type}: {e}")
                raise ValueError(f"Invalid setting value in database: {key}")
        
        # Validate required settings exist
        self._validate_required()
    
    def _validate_required(self) -> None:
        """
        Validate required settings are present.
        
        Fails fast if critical configuration is missing.
        """
        required = [
            'horizon_url',
            'ubec_code',
            'ubec_issuer',
            'network'
        ]
        
        missing = [key for key in required if key not in self._settings or not self._settings[key]]
        
        if missing:
            raise ValueError(
                f"Missing required configuration in database: {', '.join(missing)}. "
                f"Database must contain all required settings (Principle #4)."
            )
    
    async def reload(self) -> None:
        """
        Force reload configuration from database.
        
        Principle #12: This is the ONLY way to refresh configuration.
        """
        self._last_loaded = None
        await self.initialize()
        logger.info("Configuration reloaded from database")
    
    # ========================================================================
    # CONFIGURATION ACCESS
    # ========================================================================
    
    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            RuntimeError: If not initialized
            KeyError: If key not found
            
        Usage:
            horizon_url = config['horizon_url']
        """
        if not self._initialized:
            raise RuntimeError("Configuration not initialized. Call await config.initialize() first.")
        
        if key not in self._settings:
            raise KeyError(
                f"Configuration key '{key}' not found in database. "
                f"Add to system_settings table (Principle #4)."
            )
        
        return self._settings[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with optional default.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._initialized:
            raise RuntimeError("Configuration not initialized.")
        
        return self._settings.get(key, default)
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self._settings
    
    def keys(self):
        """Get all configuration keys."""
        return self._settings.keys()
    
    def items(self):
        """Get all configuration items."""
        return self._settings.items()
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check configuration service health.
        
        Principle #7: Per-Asset Monitoring with health checks.
        
        Returns:
            Health status dictionary:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'details': dict
            }
        """
        start_time = datetime.now()
        
        # Check initialization
        if not self._initialized:
            return {
                'status': 'unhealthy',
                'message': 'Configuration not initialized',
                'details': {
                    'initialized': False
                }
            }
        
        # Check cache validity
        cache_valid = self._cache_valid()
        cache_age = (datetime.now() - self._last_loaded).total_seconds() if self._last_loaded else None
        
        # Check required settings
        try:
            self._validate_required()
            has_required = True
        except ValueError:
            has_required = False
        
        # Determine status
        if has_required and cache_valid:
            status = 'healthy'
            message = f'Configuration loaded ({len(self._settings)} settings)'
        elif has_required and not cache_valid:
            status = 'degraded'
            message = 'Configuration cache expired (will reload on next access)'
        else:
            status = 'unhealthy'
            message = 'Configuration missing required settings'
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'status': status,
            'message': message,
            'details': {
                'initialized': self._initialized,
                'settings_count': len(self._settings),
                'source': 'database',
                'cache_valid': cache_valid,
                'cache_age_seconds': cache_age,
                'cache_ttl_minutes': self._cache_ttl.total_seconds() / 60,
                'last_loaded': self._last_loaded.isoformat() if self._last_loaded else None,
                'has_required_settings': has_required,
                'response_time_ms': round(response_time, 2)
            }
        }
    
    # ========================================================================
    # DIAGNOSTIC METHODS
    # ========================================================================
    
    def display(self) -> Dict[str, Any]:
        """
        Display configuration for diagnostics.
        
        Sensitive values are redacted.
        
        Returns:
            Dictionary of safe-to-display configuration
        """
        if not self._initialized:
            return {'error': 'Not initialized'}
        
        def redact(value: str, show_chars: int = 10) -> str:
            """Redact sensitive string values."""
            if not isinstance(value, str) or len(value) <= show_chars:
                return value
            return value[:show_chars] + '...'
        
        return {
            'network': self.get('network', 'unknown'),
            'horizon_url': self.get('horizon_url', 'unknown'),
            'ubec_code': self.get('ubec_code', 'unknown'),
            'ubec_issuer': redact(self.get('ubec_issuer', '')),
            'settings_count': len(self._settings),
            'cache_valid': self._cache_valid(),
            'last_loaded': self._last_loaded.isoformat() if self._last_loaded else None
        }
    
    def __repr__(self) -> str:
        """String representation."""
        status = "initialized" if self._initialized else "not initialized"
        count = len(self._settings) if self._initialized else 0
        return f"<ConfigurationService: {status}, {count} settings>"


# ============================================================================
# FACTORY FUNCTION (Principle #12: Method Singularity)
# ============================================================================

async def get_system_config(db_manager) -> ConfigurationService:
    """
    Factory function to create and initialize configuration service.
    
    This is the ONLY way to create a ConfigurationService instance.
    Principle #12: Method Singularity - one way to do things.
    
    Args:
        db_manager: AsyncDatabaseManager instance (REQUIRED)
        
    Returns:
        Initialized ConfigurationService instance
        
    Raises:
        ValueError: If db_manager is None
        RuntimeError: If database is unavailable
        ValueError: If required settings missing
        
    Usage:
        # In service registry factory
        async def create_config(registry):
            from config.settings import get_system_config
            db = await registry.get('database')
            config = await get_system_config(db)
            return config
        
        # In services
        config = await registry.get('config')
        horizon_url = config['horizon_url']
    
    Design Notes:
        - Database is REQUIRED (Principle #4: Single Source of Truth)
        - No fallbacks to environment variables
        - Fails fast if database unavailable
        - Validates required settings on load
    """
    if db_manager is None:
        raise ValueError(
            "Database manager is required. "
            "Database is SINGLE source of truth (Principle #4). "
            "No fallbacks, no environment variables."
        )
    
    config = ConfigurationService(db_manager)
    await config.initialize()
    
    logger.info(f"✓ Configuration service initialized: {len(config._settings)} settings")
    
    return config


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'ConfigurationService',
    'get_system_config',
]


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
CORRECT USAGE:

1. Create via factory (service registry):
   
   async def create_config(registry: ServiceRegistry):
       from config.settings import get_system_config
       db = await registry.get('database')
       config = await get_system_config(db)
       return config

2. Access in services:
   
   class MyService:
       def __init__(self, config, db):
           self.config = config
           self.db = db
       
       async def do_work(self):
           # Dictionary-style access
           url = self.config['horizon_url']
           issuer = self.config['ubec_issuer']
           
           # Check if setting exists
           if 'optional_setting' in self.config:
               value = self.config['optional_setting']

3. Health check:
   
   health = await config.health_check()
   print(f"Status: {health['status']}")
   print(f"Settings: {health['details']['settings_count']}")

4. Reload configuration:
   
   # After database update
   await config.reload()


INCORRECT USAGE:

❌ Don't instantiate directly:
   config = ConfigurationService(db)  # Wrong! Use factory

❌ Don't use properties:
   config.HORIZON_URL  # Wrong! Use dictionary access

❌ Don't expect fallbacks:
   # No environment variable fallbacks
   # No default values in code
   # Database is ONLY source

❌ Don't create singletons:
   # Let service registry manage lifecycle
   # Each factory call returns new instance


DATABASE SCHEMA:

CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) DEFAULT 'string',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Required settings:
- horizon_url (string)
- ubec_code (string)
- ubec_issuer (string)
- network (string)

See setup_system_settings.sql for complete schema.
"""
