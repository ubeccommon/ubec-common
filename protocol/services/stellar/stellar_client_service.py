"""
Stellar Client Service - Production Implementation

Wraps stellar_sdk.ServerAsync with comprehensive health monitoring, rate limiting,
and database-backed configuration.

Design Principles Applied:
- ✅ Principle #2: Service Pattern (no standalone execution)
- ✅ Principle #3: Service Registry for Dependencies (config, rate_limiter)
- ✅ Principle #4: Single Source of Truth (database via config, NO fallbacks)
- ✅ Principle #5: Strict Async Operations (all methods async)
- ✅ Principle #6: No Sync Fallbacks (fails explicitly if config missing)
- ✅ Principle #7: Per-Asset Monitoring (uses ServiceHealthCheck)
- ✅ Principle #9: Integrated Rate Limiting (all API calls rate-limited)
- ✅ Principle #11: Comprehensive Documentation
- ✅ Principle #12: Method Singularity (no duplicate methods)

Critical Fixes in v2.0.3:
- FIXED: Changed rate limiter usage from context manager to acquire() method
- FIXED: Changed config key from 'stellar_horizon_url' to 'horizon_url' (matches database schema) in v2.0.2
- FIXED: Changed config.get_setting() to config['key'] (dictionary access) in v2.0.1
- FIXED: Removed default fallback values (violates Principle #4 and #6) in v2.0.1
- FIXED: Health check now uses correct ServiceHealthCheck.stellar_client_health() signature in v2.0.1
- ENHANCED: Clear error messages when configuration is missing

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.

Version: 2.0.3
Date: October 21, 2025
"""

from typing import Dict, Any, Optional
from stellar_sdk import ServerAsync
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StellarClientService:
    """
    Stellar blockchain client with rate limiting and health monitoring.
    
    Wraps stellar_sdk.ServerAsync to provide:
    - Database-backed configuration (Principle #4)
    - Integrated rate limiting (Principle #9)
    - Standardized health checks (Principle #7)
    - Async-only operations (Principle #5)
    - No fallback values (Principle #6)
    - Proper service lifecycle management
    
    Dependencies:
        - config: Configuration service (loads from database)
        - rate_limiter: Rate limiting service
    
    Usage:
        # Service is created via registry, not directly
        stellar_client = await registry.get("stellar_client")
        ledger = await stellar_client.get_latest_ledger()
        health = await stellar_client.health_check()
        await stellar_client.close()
    """
    
    def __init__(self, config, rate_limiter):
        """
        Initialize Stellar client service.
        
        Args:
            config: Configuration service (from registry)
            rate_limiter: Rate limiter service (from registry)
            
        Note:
            Do NOT call directly. Use service registry factory.
            Call initialize() after construction.
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self._client: Optional[ServerAsync] = None
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[str] = None
        self.horizon_url: Optional[str] = None
        
        logger.info("Stellar client service constructed - call initialize() to complete setup")
    
    # ========================================================================
    # INITIALIZATION (Principle #5: Strict Async)
    # ========================================================================
    
    async def initialize(self) -> None:
        """
        Async initialization of Stellar client.
        
        Loads configuration from database and creates client.
        
        Follows:
            - Principle #4: Database as single source of truth (NO defaults)
            - Principle #6: No sync fallbacks (fails if setting missing)
        
        Raises:
            KeyError: If 'stellar_horizon_url' not in database configuration
            
        Note:
            The KeyError is intentional. It forces proper database configuration
            instead of silently falling back to hardcoded defaults.
        """
        try:
            # Get horizon URL from database via config service
            # Uses dictionary-style access (config is a dict-like object)
            # NO default parameter - database MUST contain this setting
            self.horizon_url = self.config['horizon_url']
            
            if not self.horizon_url:
                raise ValueError(
                    "horizon_url is empty in database. "
                    "Database must contain valid Horizon URL (Principle #4)."
                )
            
            # Create ServerAsync client
            self._client = ServerAsync(horizon_url=self.horizon_url)
            self._initialized = True
            
            logger.info(f"✓ Stellar client initialized: {self.horizon_url}")
            
        except KeyError as e:
            logger.error(
                f"Missing required configuration: {e}. "
                f"Database must contain 'horizon_url' setting (Principle #4). "
                f"Run setup_system_settings.sql to initialize required configuration."
            )
            raise ValueError(
                f"Missing required database configuration: horizon_url. "
                f"Database is the ONLY source of truth (Principle #4). "
                f"No fallback values are used (Principle #6)."
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize Stellar client: {e}")
            raise
    
    # ========================================================================
    # STELLAR API METHODS WITH RATE LIMITING (Principle #9)
    # ========================================================================
    
    async def get_latest_ledger(self) -> Dict[str, Any]:
        """
        Fetch the latest ledger from Stellar Horizon API.
        
        This method is required by health checks and monitoring systems.
        All API calls are rate-limited per Principle #9 using acquire().
        
        Returns:
            dict: Latest ledger data including:
                - sequence: Ledger sequence number
                - hash: Ledger hash
                - closed_at: Timestamp when ledger closed
                - transaction_count: Number of transactions
                - operation_count: Number of operations
                
        Raises:
            RuntimeError: If client not initialized
            Exception: If API call fails
            
        Example:
            ledger = await client.get_latest_ledger()
            print(f"Latest ledger: {ledger['sequence']}")
        """
        if not self._initialized or not self._client:
            raise RuntimeError(
                "Stellar client not initialized. Call initialize() first."
            )
        
        try:
            # Rate-limited API call
            await self.rate_limiter.acquire()
            response = await self._client.ledgers().order(desc=True).limit(1).call()
            self._request_count += 1
            
            if '_embedded' in response and 'records' in response['_embedded']:
                ledger = response['_embedded']['records'][0]
                return {
                    'sequence': ledger.get('sequence'),
                    'hash': ledger.get('hash'),
                    'closed_at': ledger.get('closed_at'),
                    'transaction_count': ledger.get('successful_transaction_count', 0),
                    'operation_count': ledger.get('operation_count', 0)
                }
            else:
                return {}
                    
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Failed to get latest ledger: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """
        Test Stellar network connectivity with rate limiting.
        
        This method is used by health checks to verify Horizon API accessibility.
        Uses the Stellar SDK's root() endpoint which returns network information.
        
        Returns:
            True if connection successful, False otherwise
            
        Note:
            This method does not raise exceptions - it returns False on failure.
            Detailed error information is stored in _last_error for debugging.
        """
        if not self._initialized or not self._client:
            logger.error("Cannot test connection - client not initialized")
            return False
        
        try:
            await self.rate_limiter.acquire()
            await self._client.root().call()
            self._request_count += 1
            return True
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Stellar connection test failed: {e}")
            return False
    
    async def get_network_info(self) -> Dict[str, Any]:
        """
        Get Stellar network information with rate limiting.
        
        Returns:
            Network details including:
                - network_passphrase: Network identifier
                - horizon_version: Horizon API version
                - core_version: Stellar Core version
                - protocol_version: Current protocol version
                
        Raises:
            RuntimeError: If client not initialized
        """
        if not self._initialized or not self._client:
            raise RuntimeError(
                "Stellar client not initialized. Call initialize() first."
            )
        
        try:
            await self.rate_limiter.acquire()
            response = await self._client.root().call()
            self._request_count += 1
            
            return {
                'network_passphrase': response.get('network_passphrase'),
                'horizon_version': response.get('horizon_version'),
                'core_version': response.get('core_version'),
                'protocol_version': response.get('current_protocol_version')
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Failed to get network info: {e}")
            return {}
    
    async def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get account details from Stellar with rate limiting.
        
        Args:
            account_id: Stellar account address (G...)
            
        Returns:
            Account details including balances
            
        Raises:
            RuntimeError: If client not initialized
            Exception: If account not found or API call fails
        """
        if not self._initialized or not self._client:
            raise RuntimeError(
                "Stellar client not initialized. Call initialize() first."
            )
        
        try:
            await self.rate_limiter.acquire()
            response = await self._client.accounts().account_id(account_id).call()
            self._request_count += 1
            return response
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Failed to get account {account_id}: {e}")
            raise
    
    # ========================================================================
    # PROXY TO UNDERLYING CLIENT (Principle #12: Single Implementation)
    # ========================================================================
    
    def __getattr__(self, name):
        """
        Proxy all stellar_sdk methods to underlying client.
        
        WARNING: Proxied methods bypass rate limiting. For production use,
        wrap critical methods explicitly (like get_latest_ledger above).
        
        This allows transparent access to all ServerAsync methods while
        maintaining our wrapper for health checks.
        
        Raises:
            RuntimeError: If client not initialized
            AttributeError: If method doesn't exist on underlying client
        """
        if self._client is None:
            raise RuntimeError(
                "Stellar client not initialized. Call initialize() first."
            )
        return getattr(self._client, name)
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using standardized utility.
        
        Follows Principle #7: Per-Asset Monitoring with execution minimums.
        Uses ServiceHealthCheck utility for consistency (Principle #12).
        
        The health check validates:
        - Service initialization status
        - API connectivity (via test_connection)
        - Rate limiter accessibility
        - Error rates and request statistics
        
        Returns:
            Health status dictionary with standardized format:
            {
                "status": "healthy" | "degraded" | "unhealthy",
                "message": "...",
                "timestamp": "...",
                "details": {
                    "horizon_url": "...",
                    "request_count": ...,
                    "error_count": ...,
                    "error_rate": ...,
                    ...
                }
            }
            
        Example:
            health = await client.health_check()
            if health['status'] != 'healthy':
                logger.warning(f"Stellar client unhealthy: {health['message']}")
        """
        from core.utils.service_health import ServiceHealthCheck
        
        # Call standardized health check utility with explicit parameters
        # The utility performs connectivity tests and evaluates service health
        return await ServiceHealthCheck.stellar_client_health(
            client=self,
            horizon_url=self.horizon_url or "not_initialized",
            initialized=self._initialized,
            request_count=self._request_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time
        )
    
    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================
    
    async def close(self) -> None:
        """
        Close Stellar client connection.
        
        Follows async cleanup pattern (Principle #5).
        Ensures proper resource cleanup during service shutdown.
        
        Note:
            This method is idempotent - safe to call multiple times.
        """
        try:
            if self._client and hasattr(self._client, 'close'):
                await self._client.close()
            
            self._initialized = False
            self._client = None
            
            logger.info("✓ Stellar client closed")
            
        except Exception as e:
            logger.error(f"Error closing Stellar client: {e}")
            # Don't re-raise - cleanup should be best-effort


# ============================================================================
# SERVICE REGISTRY FACTORY (Principle #2 & #3)
# ============================================================================

async def register_factory(config, rate_limiter) -> StellarClientService:
    """
    Factory function for service registry.
    
    This is the ONLY way to create StellarClientService instances.
    
    Follows:
        - Principle #2: Service Pattern with centralized execution
        - Principle #3: Service Registry for Dependencies
        - Principle #4: Single Source of Truth (config from database)
        - Principle #6: No Sync Fallbacks (fails if config invalid)
    
    Dependencies:
        config: Configuration service (provides database-backed settings)
        rate_limiter: Rate limiter service (enforces API rate limits)
    
    Args:
        config: Config service from registry
        rate_limiter: Rate limiter service from registry
    
    Returns:
        Fully initialized StellarClientService instance
        
    Raises:
        ValueError: If required configuration missing from database
        Exception: If initialization fails
    
    Usage (by service registry):
        registry.register(
            "stellar_client",
            register_factory,
            dependencies=["config", "rate_limiter"]
        )
        
        # Later, in application code:
        stellar = await registry.get("stellar_client")
    """
    logger.info("Creating Stellar client service via factory...")
    
    service = StellarClientService(config=config, rate_limiter=rate_limiter)
    await service.initialize()
    
    logger.info("✓ Stellar client service created and initialized")
    
    return service


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'StellarClientService',
    'register_factory'
]
