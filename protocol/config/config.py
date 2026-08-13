#!/usr/bin/env python3
# config/config.py
"""
UBEC Protocol Suite - Configuration Service Wrapper
====================================================
Property-style access wrapper around database-backed ConfigurationService.

This module provides a property-based interface to the ConfigurationService
for backward compatibility with code expecting property-style access patterns.

Architecture:
- ConfigurationService (settings.py): Actual implementation, database-backed
- Config (this file): Property-style wrapper for convenience
- Service Registry: Discovers and manages Config instances

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained wrapper with clear boundaries
    ✅ #2  Service Pattern: Factory-based, no standalone execution
    ✅ #3  Service Registry: Accessed through service registry
    ✅ #4  Single Source of Truth: All data from database via ConfigurationService
    ✅ #5  Strict Async: Health checks and initialization use async
    ✅ #6  No Sync Fallbacks: Property access wraps sync over async storage
    ✅ #7  Per-Asset Monitoring: Comprehensive health check implementation
    ✅ #8  No Duplicate Config: Single wrapper, delegates to ConfigurationService
    ✅ #9  Integrated Rate Limiting: N/A (configuration service)
    ✅ #10 Separation of Concerns: Wrapper separated from storage logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Single factory, single wrapper implementation
══════════════════════════════════════════════════════════════════════════════

Key Features:
- Property-style access (config.HORIZON_URL)
- Dictionary-style access (config['horizon_url'])
- Async health check for service registry
- Automatic reload capability
- Type conversion (Decimal, int, bool)
- Backward compatibility with GlobalConfig

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 4.1.0 (Added ACCOUNTS Property - Config Access Fix)
Date: October 17, 2025
Author: UBEC Protocol Team with Claude AI assistance

Changes from v4.0.0:
- Added ACCOUNTS property for account address access
- Maps database settings to expected account structure
- Supports both single stewardship and stewardship list
- Enhanced documentation with account access examples
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

# Import ConfigurationService (actual implementation)
from config.settings import ConfigurationService, get_system_config

# Import health check utilities (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION WRAPPER CLASS
# ============================================================================

class Config:
    """
    Property-style configuration wrapper around ConfigurationService.
    
    This class provides convenient property-based access to configuration
    while delegating all actual storage and retrieval to the database-backed
    ConfigurationService.
    
    Architecture Pattern:
        Config (wrapper) → ConfigurationService (implementation) → Database (truth)
    
    The service registry discovers the health_check() method on this wrapper,
    allowing the entire configuration system to participate in health monitoring.
    
    Usage:
        # Via service registry (PREFERRED)
        from core.service_registry import registry
        config = await registry.get('config')
        
        # Property access
        url = config.HORIZON_URL
        issuer = config.UBEC_ISSUER
        network = config.NETWORK
        
        # Account access (NEW in v4.1.0)
        admin_addr = config.ACCOUNTS['administration']
        steward_addr = config.ACCOUNTS['stewardship']
        general_addr = config.ACCOUNTS['general']
        
        # Dictionary access (also supported)
        url = config['horizon_url']
        issuer = config.get('ubec_issuer', 'default')
        
        # Health check (async)
        health = await config.health_check()
        if health['status'] == 'healthy':
            print("Configuration loaded and valid")
        
        # Reload from database
        await config.reload()
    
    Design Notes:
        - All properties delegate to ConfigurationService
        - ConfigurationService loads from database (Principle #4)
        - Health check uses ServiceHealthCheck utility (Principle #12)
        - No duplicate configuration logic (Principle #8)
    """
    
    def __init__(self, config_service: ConfigurationService):
        """
        Initialize configuration wrapper.
        
        Args:
            config_service: Initialized ConfigurationService instance from settings.py
        
        Note:
            Do NOT instantiate directly. Use create_config_service() factory function.
        
        Example:
            # Correct (via factory)
            config = await create_config_service(db_manager)
            
            # Incorrect (don't do this)
            config = Config(some_service)  # Wrong! Use factory
        """
        if not isinstance(config_service, ConfigurationService):
            raise TypeError(
                f"Expected ConfigurationService, got {type(config_service).__name__}. "
                f"Use create_config_service() factory function."
            )
        
        self._config = config_service
        self._initialized = config_service._initialized
        
        logger.debug(f"Config wrapper initialized (wrapping {len(config_service._settings)} settings)")
    
    # ========================================================================
    # CORE NETWORK PROPERTIES
    # ========================================================================
    
    @property
    def NETWORK(self) -> str:
        """
        Stellar network: 'mainnet' or 'testnet'.
        
        Returns:
            Network identifier string
        
        Example:
            if config.NETWORK == 'mainnet':
                print("Running on production network")
        """
        return self._config.get('network', 'mainnet')
    
    @property
    def HORIZON_URL(self) -> str:
        """
        Horizon API URL for Stellar blockchain access.
        
        Returns:
            Full Horizon server URL
        
        Example:
            client = StellarClient(horizon_url=config.HORIZON_URL)
        """
        return self._config.get('horizon_url', 'https://horizon.stellar.org')
    
    @property
    def horizon_url(self) -> str:
        """
        Alias for HORIZON_URL (backward compatibility).
        
        Returns:
            Full Horizon server URL
        """
        return self.HORIZON_URL
    
    # ========================================================================
    # UBEC TOKEN PROPERTIES (All Four Elements)
    # ========================================================================
    
    @property
    def UBEC_CODE(self) -> str:
        """UBEC token code (Air element - Gateway)."""
        return self._config.get('ubec_code', 'UBEC')
    
    @property
    def UBEC_ISSUER(self) -> str:
        """UBEC token issuer address (Air element)."""
        return self._config.get('ubec_issuer', '')
    
    @property
    def UBECRC_CODE(self) -> str:
        """UBECrc token code (Water element - Reciprocity)."""
        return self._config.get('ubecrc_code', 'UBECrc')
    
    @property
    def UBECRC_ISSUER(self) -> str:
        """UBECrc token issuer address (Water element)."""
        return self._config.get('ubecrc_issuer', '')
    
    @property
    def UBECGPI_CODE(self) -> str:
        """UBECgpi token code (Earth element - Stability)."""
        return self._config.get('ubecgpi_code', 'UBECgpi')
    
    @property
    def UBECGPI_ISSUER(self) -> str:
        """UBECgpi token issuer address (Earth element)."""
        return self._config.get('ubecgpi_issuer', '')
    
    @property
    def UBECTT_CODE(self) -> str:
        """UBECtt token code (Fire element - Transformation)."""
        return self._config.get('ubectt_code', 'UBECtt')
    
    @property
    def UBECTT_ISSUER(self) -> str:
        """UBECtt token issuer address (Fire element)."""
        return self._config.get('ubectt_issuer', '')
    
    # ========================================================================
    # ACCOUNT PROPERTIES (NEW in v4.1.0 - Config Access Fix)
    # ========================================================================
    
    @property
    def ACCOUNTS(self) -> Dict[str, Any]:
        """
        Get managed account addresses dictionary.
        
        Maps database settings to account structure expected by services.
        
        Database Settings → ACCOUNTS Structure:
            administration_account → {'administration': 'GXXX...'}
            stewardship_account    → {'stewardship': 'GXXX...' or ['GXXX...', ...]}
            general_account        → {'general': 'GXXX...'}
        
        Returns:
            Dictionary with account types as keys and addresses as values:
            {
                'administration': str,           # Admin account address
                'stewardship': str or List[str], # Steward account(s)
                'general': str,                  # General account address
                'stewardship_management': str,   # Individual steward accounts
                'stewardship_infrastructure': str,
                'stewardship_liquidity': str
            }
        
        Example:
            # Access individual accounts
            admin_addr = config.ACCOUNTS['administration']
            general_addr = config.ACCOUNTS['general']
            
            # Stewardship can be single or list
            steward = config.ACCOUNTS['stewardship']
            if isinstance(steward, list):
                for addr in steward:
                    process_steward_account(addr)
            else:
                process_steward_account(steward)
            
            # Access specific stewardship accounts
            mgmt_addr = config.ACCOUNTS.get('stewardship_management', '')
            infra_addr = config.ACCOUNTS.get('stewardship_infrastructure', '')
            liq_addr = config.ACCOUNTS.get('stewardship_liquidity', '')
        
        Design Notes:
            - Principle #4: Database is single source of truth
            - Principle #8: No duplicate config - built from database settings
            - Supports legacy code expecting either single or list stewardship
        """
        accounts = {}
        
        # Get account addresses from database settings
        admin = self._config.get('administration_account', '')
        steward = self._config.get('stewardship_account', '')
        general = self._config.get('general_account', '')
        
        # Additional stewardship accounts if present (for multi-account stewardship)
        steward_mgmt = self._config.get('stewardship_management_account', '')
        steward_infra = self._config.get('stewardship_infrastructure_account', '')
        steward_liquidity = self._config.get('stewardship_liquidity_account', '')
        
        # Build accounts dictionary
        if admin:
            accounts['administration'] = admin
        
        # Stewardship: Handle both single and multi-account scenarios
        if steward:
            # Single stewardship account (backward compatibility)
            accounts['stewardship'] = steward
        elif steward_mgmt:
            # Multi-account stewardship - provide as list
            steward_list = [s for s in [steward_mgmt, steward_infra, steward_liquidity] if s]
            if len(steward_list) == 1:
                # Only one stewardship account - provide as string
                accounts['stewardship'] = steward_list[0]
            else:
                # Multiple stewardship accounts - provide as list
                accounts['stewardship'] = steward_list
        
        if general:
            accounts['general'] = general
        
        # Add individual stewardship accounts for direct access
        if steward_mgmt:
            accounts['stewardship_management'] = steward_mgmt
        if steward_infra:
            accounts['stewardship_infrastructure'] = steward_infra
        if steward_liquidity:
            accounts['stewardship_liquidity'] = steward_liquidity
        
        return accounts
    
    # ========================================================================
    # SUPPLY CALCULATION PROPERTIES
    # ========================================================================
    
    @property
    def FALLBACK_SUPPLY(self) -> Decimal:
        """
        Fallback supply value for calculations.
        
        Returns:
            Decimal supply value
        """
        val = self._config.get('fallback_supply', '191766039.00')
        return Decimal(str(val))
    
    @property
    def ALWAYS_LOAD_FROM_NETWORK(self) -> bool:
        """
        Whether to always load supply data from network.
        
        Returns:
            Boolean flag
        """
        return bool(self._config.get('always_load_from_network', True))
    
    @property
    def SUPPLY_CALCULATION_METHOD(self) -> str:
        """
        Supply calculation method: 'PRECISE' or 'ESTIMATED'.
        
        Returns:
            Calculation method string
        """
        return self._config.get('supply_calculation_method', 'PRECISE')
    
    @property
    def SUPPLY_SAFETY_FACTOR(self) -> Decimal:
        """
        Safety factor for supply calculations (e.g., 0.02 = 2%).
        
        Returns:
            Decimal safety factor
        """
        val = self._config.get('supply_safety_factor', '0.02')
        return Decimal(str(val))
    
    @property
    def SUPPLY_CHECK_INTERVAL(self) -> int:
        """
        Interval for supply checks in seconds.
        
        Returns:
            Integer seconds
        """
        return int(self._config.get('supply_check_interval', 86400))
    
    # ========================================================================
    # DISTRIBUTION PROPERTIES
    # ========================================================================
    
    @property
    def TARGET_DISTRIBUTION(self) -> Dict[str, Decimal]:
        """
        Target distribution percentages across categories.
        
        Returns:
            Dictionary mapping category names to Decimal percentages
        
        Example:
            dist = config.TARGET_DISTRIBUTION
            print(f"General: {dist['general'] * 100}%")
        """
        # Load from config if available, otherwise use defaults
        # Note: Database uses administration_target, stewardship_target
        admin_target = self._config.get('administration_target', 0.05)
        steward_target = self._config.get('stewardship_target', 0.30)
        
        # Calculate general as remainder (1.0 - admin - steward)
        general_target = 1.0 - float(admin_target) - float(steward_target)
        
        return {
            'general': Decimal(str(general_target)),
            'stewardship': Decimal(str(steward_target)),
            'administration': Decimal(str(admin_target))
        }
    
    @property
    def REBALANCE_THRESHOLD(self) -> Decimal:
        """
        Threshold for triggering rebalance operations.
        
        Returns:
            Decimal threshold value (e.g., 0.01 = 1%)
        """
        val = self._config.get('rebalance_threshold', '0.01')
        return Decimal(str(val))
    
    # ========================================================================
    # OPERATIONAL PROPERTIES
    # ========================================================================
    
    @property
    def CHECK_INTERVAL(self) -> int:
        """
        General check interval in seconds.
        
        Returns:
            Integer seconds (default: 3600 = 1 hour)
        """
        return int(self._config.get('check_interval', 3600))
    
    # ========================================================================
    # DATABASE PROPERTIES
    # ========================================================================
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Database connection URL.
        
        Returns:
            Database URL string
        
        Note:
            May be empty if connection is managed separately.
        """
        return self._config.get('database_url', '')
    
    # ========================================================================
    # RATE LIMITING PROPERTIES
    # ========================================================================
    
    @property
    def RATE_LIMIT_CALLS(self) -> int:
        """
        Maximum API calls allowed in rate limit period.
        
        Returns:
            Integer call count
        """
        return int(self._config.get('rate_limit_calls', 100))
    
    @property
    def RATE_LIMIT_PERIOD(self) -> int:
        """
        Rate limit period in seconds.
        
        Returns:
            Integer seconds
        """
        return int(self._config.get('rate_limit_period', 60))
    
    # ========================================================================
    # SYNCHRONIZATION PROPERTIES
    # ========================================================================
    
    @property
    def SYNC_BATCH_SIZE(self) -> int:
        """
        Batch size for synchronization operations.
        
        Returns:
            Integer batch size
        """
        return int(self._config.get('sync_batch_size', 200))
    
    @property
    def SYNC_BATCH_DELAY(self) -> float:
        """
        Delay between sync batches in seconds.
        
        Returns:
            Float seconds
        """
        return float(self._config.get('sync_batch_delay', 1.0))
    
    @property
    def SYNC_MAX_ACCOUNTS(self) -> int:
        """
        Maximum accounts to sync in one operation.
        
        Returns:
            Integer account count
        """
        return int(self._config.get('sync_max_accounts', 1000))
    
    # ========================================================================
    # HOLONIC EVALUATION PROPERTIES
    # ========================================================================
    
    @property
    def HOLONIC_WEIGHTS(self) -> Dict[str, float]:
        """
        Weights for holonic evaluation dimensions.
        
        Returns:
            Dictionary mapping dimension names to weight values
        
        Example:
            weights = config.HOLONIC_WEIGHTS
            ubuntu_weight = weights['ubuntu']
        """
        return {
            'autonomy_integration': float(self._config.get('weight_autonomy', 0.25)),
            'multi_scale': float(self._config.get('weight_multiscale', 0.20)),
            'regenerative': float(self._config.get('weight_regenerative', 0.25)),
            'network': float(self._config.get('weight_network', 0.15)),
            'ubuntu': float(self._config.get('weight_ubuntu', 0.15))
        }
    
    # ========================================================================
    # LOGGING PROPERTIES
    # ========================================================================
    
    @property
    def LOG_LEVEL(self) -> str:
        """
        Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        
        Returns:
            Log level string
        """
        return self._config.get('log_level', 'INFO')
    
    @property
    def LOG_FORMAT(self) -> str:
        """
        Log message format string.
        
        Returns:
            Python logging format string
        """
        return self._config.get(
            'log_format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @property
    def LOG_FILE(self) -> str:
        """
        Log file path.
        
        Returns:
            File path string
        """
        return self._config.get('log_file', 'ubec_protocol.log')
    
    # ========================================================================
    # DICTIONARY-STYLE ACCESS METHODS
    # ========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with optional default.
        
        This provides dictionary-style access: config.get('key', 'default')
        
        Args:
            key: Configuration key (lowercase with underscores)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            # Get with default
            timeout = config.get('api_timeout', 30)
            
            # Get required value
            issuer = config.get('ubec_issuer')
            if not issuer:
                raise ValueError("UBEC issuer not configured")
        """
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value
        
        Raises:
            KeyError: If key not found
        
        Example:
            url = config['horizon_url']
            issuer = config['ubec_issuer']
        """
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key
        
        Returns:
            True if key exists
        
        Example:
            if 'optional_feature' in config:
                enable_feature()
        """
        return key in self._config
    
    # ========================================================================
    # TOKEN CONFIGURATION METHODS
    # ========================================================================
    
    def get_token_config(self, token_code: str) -> Dict[str, Any]:
        """
        Get configuration for a specific UBEC token.
        
        Args:
            token_code: Token code ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
        
        Returns:
            Dictionary with token configuration:
            {
                'code': str,
                'issuer': str,
                'element': str,
                'ubuntu_principle': str
            }
        
        Example:
            fire_config = config.get_token_config('UBECtt')
            print(f"Fire token issuer: {fire_config['issuer']}")
            print(f"Ubuntu principle: {fire_config['ubuntu_principle']}")
        """
        # Normalize token code
        token_code = token_code.upper()
        
        # Map tokens to elements and principles
        token_map = {
            'UBEC': {
                'element': 'air',
                'ubuntu_principle': 'diversity',
                'description': 'Gateway & Universal Access'
            },
            'UBECRC': {
                'element': 'water',
                'ubuntu_principle': 'reciprocity',
                'description': 'Flow & Exchange'
            },
            'UBECGPI': {
                'element': 'earth',
                'ubuntu_principle': 'mutualism',
                'description': 'Stability & Value'
            },
            'UBECTT': {
                'element': 'fire',
                'ubuntu_principle': 'regeneration',
                'description': 'Transformation & Action'
            }
        }
        
        if token_code not in token_map:
            raise ValueError(f"Unknown token code: {token_code}")
        
        # Get issuer from config
        issuer_key = f'{token_code.lower()}_issuer'
        issuer = self._config.get(issuer_key, '')
        
        return {
            'code': token_code,
            'issuer': issuer,
            **token_map[token_code]
        }
    
    def get_all_tokens(self) -> List[Dict[str, Any]]:
        """
        Get configuration for all four UBEC tokens.
        
        Returns:
            List of token configuration dictionaries
        
        Example:
            for token in config.get_all_tokens():
                print(f"{token['element']}: {token['code']} ({token['ubuntu_principle']})")
        """
        return [
            self.get_token_config('UBEC'),
            self.get_token_config('UBECrc'),
            self.get_token_config('UBECgpi'),
            self.get_token_config('UBECtt')
        ]
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on configuration service.
        
        This method is discovered by the service registry and called during
        system health checks. It uses the ServiceHealthCheck utility to provide
        standardized health reporting.
        
        Implements Principle #7 (Per-Asset Monitoring) by providing detailed
        configuration service health information.
        
        Returns:
            Health status dictionary:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO 8601),
                'details': {
                    'initialized': bool,
                    'settings_count': int,
                    'required_settings_present': bool,
                    'cache_valid': bool,
                    'last_loaded': str (ISO 8601) or None,
                    'network': str,
                    'horizon_url': str
                }
            }
        
        Health Status Determination:
            - HEALTHY: All required settings present and valid
            - DEGRADED: Optional settings missing but system functional
            - UNHEALTHY: Required settings missing or service not initialized
        
        Example:
            health = await config.health_check()
            
            if health['status'] == 'healthy':
                print("✓ Configuration loaded and valid")
                print(f"  Settings: {health['details']['settings_count']}")
                print(f"  Network: {health['details']['network']}")
            else:
                print(f"✗ Configuration {health['status']}: {health['message']}")
        """
        async def check_required_settings():
            """
            Verify all required settings are present.
            
            Raises:
                Exception: If any required setting is missing
            """
            required = ['horizon_url', 'ubec_code', 'ubec_issuer', 'network']
            missing = [key for key in required if not self._config.get(key)]
            
            if missing:
                raise Exception(f"Missing required settings: {', '.join(missing)}")
            
            return None
        
        async def check_token_issuers():
            """
            Verify all four token issuers are configured.
            
            Raises:
                Exception: If any token issuer is missing
            """
            tokens = ['ubec', 'ubecrc', 'ubecgpi', 'ubectt']
            missing = []
            
            for token in tokens:
                issuer_key = f'{token}_issuer'
                if not self._config.get(issuer_key):
                    missing.append(token.upper())
            
            if missing:
                raise Exception(f"Missing token issuers: {', '.join(missing)}")
            
            return None
        
        # Get cache validity status
        cache_valid = False
        if hasattr(self._config, '_cache_valid'):
            cache_valid = self._config._cache_valid()
        
        # Get last loaded time
        last_loaded = None
        if hasattr(self._config, '_last_loaded') and self._config._last_loaded:
            last_loaded = self._config._last_loaded.isoformat()
        
        # Use ServiceHealthCheck utility (Principle #12: Method Singularity)
        return await ServiceHealthCheck.basic_health_check(
            service_name='config',
            is_initialized=self._initialized,
            additional_checks=[check_required_settings, check_token_issuers],
            settings_count=len(self._config._settings),
            cache_valid=cache_valid,
            last_loaded=last_loaded,
            network=self.NETWORK,
            horizon_url=self.HORIZON_URL,
            has_database=True
        )
    
    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================
    
    async def reload(self) -> None:
        """
        Force reload configuration from database.
        
        This method triggers a fresh load of all configuration from the database,
        invalidating any cached values.
        
        Example:
            # After updating configuration in database
            await config.reload()
            
            # Verify new value
            new_value = config.SOME_SETTING
        """
        await self._config.reload()
        self._initialized = self._config._initialized
        logger.info("Configuration reloaded from database")
    
    async def close(self) -> None:
        """
        Close configuration service.
        
        ConfigurationService doesn't need explicit cleanup, but this method
        is provided for consistency with other services in the registry.
        
        Example:
            # During shutdown
            await config.close()
        """
        # No-op for config, but maintains interface consistency
        logger.debug("Config service closed (no cleanup needed)")
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_display_config(self) -> Dict[str, Any]:
        """
        Get safe-to-display configuration (sensitive values redacted).
        
        This is useful for logging or displaying configuration without
        exposing sensitive information like issuer addresses or API keys.
        
        Returns:
            Dictionary of redacted configuration values
        
        Example:
            display_config = config.get_display_config()
            for key, value in display_config.items():
                print(f"{key}: {value}")
        """
        if hasattr(self._config, 'get_display_config'):
            return self._config.get_display_config()
        
        # Fallback implementation
        def redact(value: str, show_chars: int = 10) -> str:
            if not isinstance(value, str) or len(value) <= show_chars:
                return value
            return value[:show_chars] + '...'
        
        return {
            'network': self.NETWORK,
            'horizon_url': self.HORIZON_URL,
            'ubec_code': self.UBEC_CODE,
            'ubec_issuer': redact(self.UBEC_ISSUER),
            'ubecrc_issuer': redact(self.UBECRC_ISSUER),
            'ubecgpi_issuer': redact(self.UBECGPI_ISSUER),
            'ubectt_issuer': redact(self.UBECTT_ISSUER),
            'settings_count': len(self._config._settings),
            'initialized': self._initialized
        }
    
    def __repr__(self) -> str:
        """
        String representation of Config wrapper.
        
        Returns:
            Descriptive string
        """
        status = "initialized" if self._initialized else "not initialized"
        count = len(self._config._settings)
        return f"<Config: {status}, {count} settings, network={self.NETWORK}>"


# ============================================================================
# BACKWARD COMPATIBILITY (Deprecated)
# ============================================================================

class GlobalConfig:
    """
    Legacy GlobalConfig class for backward compatibility.
    
    DEPRECATED: This class exists only for legacy code support.
    New code should use Config via the service registry.
    
    Migration Path:
        # Old way (deprecated)
        from config.config import GlobalConfig
        config = GlobalConfig()
        
        # New way (correct)
        from core.service_registry import registry
        config = await registry.get('config')
    """
    
    def __init__(self):
        """Initialize GlobalConfig with deprecation warning."""
        self._config: Optional[Config] = None
        logger.warning(
            "GlobalConfig is DEPRECATED. "
            "Use: config = await registry.get('config')"
        )
    
    def _ensure_config(self):
        """Ensure config is set (raises error with migration instructions)."""
        if self._config is None:
            raise RuntimeError(
                "GlobalConfig not initialized. "
                "This class is deprecated. "
                "Please migrate to: config = await registry.get('config')"
            )
    
    def __getattr__(self, name: str) -> Any:
        """Delegate all attribute access to Config."""
        self._ensure_config()
        return getattr(self._config, name)


# ============================================================================
# SERVICE FACTORY (Principle #2: Service Pattern)
# ============================================================================

async def create_config_service(db_manager: Any) -> Config:
    """
    Factory function to create Config service wrapper.
    
    This is the ONLY way to create a Config instance. It creates a
    ConfigurationService from settings.py and wraps it in a Config object
    for property-style access.
    
    Following Principle #2 (Service Pattern) - factory-based instantiation.
    Following Principle #12 (Method Singularity) - one way to create config.
    
    Args:
        db_manager: AsyncDatabaseManager instance (REQUIRED)
    
    Returns:
        Config wrapper around initialized ConfigurationService
    
    Raises:
        ValueError: If db_manager is None
        RuntimeError: If database is unavailable
        ValueError: If required settings are missing
    
    Example:
        # Via service registry (PREFERRED)
        from core.service_registry import registry
        
        # In registry factory
        async def create_config(registry):
            db = await registry.get('database')
            config = await create_config_service(db)
            return config
        
        # Then use throughout application
        config = await registry.get('config')
        
        # Property access
        url = config.HORIZON_URL
        issuer = config.UBEC_ISSUER
        
        # Account access
        admin = config.ACCOUNTS['administration']
        
        # Health check
        health = await config.health_check()
        print(f"Config status: {health['status']}")
    
    Design Notes:
        - Database is REQUIRED (Principle #4: Single Source of Truth)
        - ConfigurationService handles all database interaction
        - Config wrapper provides property-style convenience
        - Health check integrated with service registry
        - All actual configuration logic in settings.py (Principle #8)
    """
    logger.info("Creating config service wrapper...")
    
    # Validate input
    if db_manager is None:
        raise ValueError(
            "Database manager is required. "
            "Database is SINGLE source of truth (Principle #4). "
            "No fallbacks or defaults allowed."
        )
    
    try:
        # Create ConfigurationService (actual implementation from settings.py)
        config_service = await get_system_config(db_manager)
        
        # Wrap it for property-style access
        config_wrapper = Config(config_service)
        
        logger.info(
            f"✓ Config service created: "
            f"{len(config_service._settings)} settings loaded from database"
        )
        
        return config_wrapper
        
    except Exception as e:
        logger.error(f"Failed to create config service: {e}")
        raise


# ============================================================================
# PUBLIC INTERFACE
# ============================================================================

__all__ = [
    'Config',
    'GlobalConfig',  # Deprecated, backward compatibility only
    'create_config_service',
]


# ============================================================================
# STANDALONE EXECUTION PREVENTION (Principle #2: Service Pattern)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UBEC Protocol Suite - Configuration Service Wrapper")
    print("=" * 80)
    print()
    print("This module provides property-style access to ConfigurationService.")
    print("All configuration is loaded from database (Principle #4).")
    print()
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (PREFERRED)")
    print("  from core.service_registry import registry")
    print("  config = await registry.get('config')")
    print()
    print("  # Property access")
    print("  url = config.HORIZON_URL")
    print("  issuer = config.UBEC_ISSUER")
    print("  network = config.NETWORK")
    print()
    print("  # Account access (NEW in v4.1.0)")
    print("  admin = config.ACCOUNTS['administration']")
    print("  steward = config.ACCOUNTS['stewardship']")
    print("  general = config.ACCOUNTS['general']")
    print()
    print("  # Dictionary access")
    print("  url = config['horizon_url']")
    print("  issuer = config.get('ubec_issuer', 'default')")
    print()
    print("  # Health check")
    print("  health = await config.health_check()")
    print("  print(f'Status: {health[\"status\"]}')")
    print()
    print("  # Token configuration")
    print("  fire_token = config.get_token_config('UBECtt')")
    print("  print(f'Fire element: {fire_token[\"ubuntu_principle\"]}')")
    print()
    print("HEALTH CHECK:")
    print("-------------")
    print("The health_check() method is discovered by service registry.")
    print("It uses ServiceHealthCheck utility (Principle #12).")
    print()
    print("=" * 80)
