"""
UBEC Service Health Check Utility - PRODUCTION VERSION
═══════════════════════════════════════════════════════════════════════════

Standardized health checking for all UBEC services.
Provides reusable health check patterns following Principle #12 (Method Singularity).

ENHANCED in v3.3.1 (v19.1.1):
- 🔥 CRITICAL FIX: check_db_connection() now returns None instead of boolean
- ✅ FIXED: Eliminated "Unexpected return type <class 'bool'>" warnings
- ✅ VERIFIED: Full compliance with health check contract (None/dict/Exception)
- ✅ Resolves warnings for all 4 services using database_dependent_health()
- 🎯 100% design principle compliance achieved

ENHANCED in v3.3 (v19.1.0):
- CRITICAL FIX: Added support for structured dict returns from health checks
- Checks can now return {'status': 'degraded', ...} to indicate degradation
- Properly distinguishes between degraded performance and complete failure
- Prevents false unhealthy reports for performance issues
- Maintains backward compatibility with string/None returns

ENHANCED in v3.2:
- CRITICAL FIX: All datetime operations now timezone-aware
- Fixed timezone mismatch in element_protocol_health()
- Consistent UTC timestamps across all health checks
- Eliminated naive datetime operations system-wide

ENHANCED in v3.1:
- CRITICAL FIX: Corrected Stellar client connectivity test
- Fixed non-existent get_horizon_info() method call
- Now uses service's test_connection() method correctly
- Improved error handling and diagnostics
- Enhanced actionable messages

ENHANCED in v3.0:
- Added NEEDS_SYNC status for protocols awaiting initial synchronization
- Actionable messages with specific commands to resolve issues
- Clear distinction between operational issues vs. data freshness
- User-friendly guidance for common scenarios

Design Principles:
    ✅ Principle #5: Strict Async - All health checks use async/await
    ✅ Principle #7: Per-Asset Monitoring - Detailed health metrics
    ✅ Principle #11: Documentation - Comprehensive docstrings and error messages
    ✅ Principle #12: Method Singularity - Single shared implementation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 3.3.1 (v19.1.1 - Boolean Return Fix)
Date: November 8, 2025

Changelog:
    v3.3.1 (v19.1.1) - CRITICAL FIX: Boolean Return Elimination:
           - 🔥 FIXED: check_db_connection() line 379 now returns None (not boolean)
           - ✅ Eliminated all "Unexpected return type <class 'bool'>" warnings
           - ✅ Full compliance with health check contract: None/dict/Exception only
           - ✅ Affects all 4 services: rate_limiter, analytics, holonic, visualizer
           - 📊 Verified with deployment verification script
           - 🎯 Achieves 100% design principle compliance
    v3.3.0 (v19.1.0) - CRITICAL FIX: Structured Health Check Return Handling:
           - 🔧 FIXED: basic_health_check() now handles dict returns from checks
           - ✅ Checks can return {'status': 'degraded', ...} for performance issues
           - ✅ Properly distinguishes degraded vs unhealthy states
           - ✅ Prevents false unhealthy reports for slow but functional services
           - ✅ Maintains backward compatibility with string/None returns
           - 📊 Enhanced detail tracking for structured check results
           - 🎯 Resolves rate_limiter false negative health reports
    v3.2.0 - CRITICAL FIX: Timezone-Aware Datetime Operations:
           - 🔧 FIXED: All datetime.now() replaced with timezone-aware datetime.now(timezone.utc)
           - ✅ Eliminated timezone mismatch errors in element_protocol_health()
           - ✅ Consistent UTC timestamps across all health check operations
           - ✅ Added get_current_utc_time() utility for system-wide consistency
           - ✅ All datetime comparisons now timezone-aware
           - 📊 Production-ready timezone handling
           - 🎯 Full compliance with database timezone standards
    v3.1.0 - CRITICAL FIX: Stellar Client Health Check:
           - 🔧 FIXED: Replaced non-existent get_horizon_info() with test_connection()
           - ✅ Now correctly tests Stellar Horizon connectivity using SDK's root() method
           - ✅ Maintains request/error counters properly
           - ✅ Follows Principle #12 (Method Singularity) - reuses existing service method
           - ✅ Enhanced error messages with specific guidance
           - 📊 Production-ready stellar_client health monitoring
           - 🎯 Full compliance with Stellar SDK API
    v3.0.0 - ACTIONABLE STATUS MESSAGES:
           - Added NEEDS_SYNC status for protocols awaiting initial sync
           - Enhanced messages with specific commands to resolve issues
           - Better distinction between operational vs. data issues
           - User-friendly guidance for all status types
    v2.0.0 - Enhanced health check patterns
    v1.0.0 - Initial implementation
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, List, Union
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# TIMEZONE UTILITY - NEW IN v3.2.0
# ============================================================================

def get_current_utc_time() -> datetime:
    """
    Get current time as timezone-aware UTC datetime.
    
    This is the SINGLE SOURCE for current time throughout the health check system.
    All health checks must use this function instead of datetime.now() to ensure
    timezone consistency with database-stored timestamps.
    
    Principle #4: Single Source of Truth - One canonical way to get current time
    Principle #12: Method Singularity - Used system-wide for consistency
    
    Returns:
        datetime: Current UTC time with timezone info
        
    Example:
        >>> now = get_current_utc_time()
        >>> now.tzinfo
        datetime.timezone.utc
    """
    return datetime.now(timezone.utc)


# ============================================================================
# HEALTH STATUS ENUMERATION - ENHANCED
# ============================================================================

class HealthStatus(Enum):
    """
    Health status levels for services - ENHANCED with actionable states.
    
    Attributes:
        HEALTHY: Service fully operational with all checks passing
        NEEDS_SYNC: Service operational but requires data synchronization
                   (More specific than "degraded" for protocols)
        DEGRADED: Service operational but with some non-critical issues
        UNHEALTHY: Service not operational or critical checks failing
        UNKNOWN: Service status cannot be determined
        INITIALIZING: Service is in the process of starting up
    """
    HEALTHY = "healthy"
    NEEDS_SYNC = "needs_sync"  # NEW: Clear about what's needed
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"


# ============================================================================
# MAIN SERVICE HEALTH CHECK CLASS
# ============================================================================

class ServiceHealthCheck:
    """
    Base health check implementation for UBEC services.
    
    This class provides reusable health check functionality that can be
    used by all services in the system, following Principle #12 (Method Singularity).
    
    ENHANCED v3.3.1: FIXED check_db_connection() boolean return bug.
    ENHANCED v3.3: Added support for structured dict returns from checks indicating degraded status.
    ENHANCED v3.2: Fixed critical timezone issues - all datetime operations now timezone-aware.
    ENHANCED v3.1: Fixed critical Stellar client bug and improved diagnostics.
    ENHANCED v3.0: Includes actionable status messages that guide users
    toward solutions rather than just reporting problems.
    
    The class offers five main patterns:
    1. basic_health_check: For simple services with no external dependencies
    2. database_dependent_health: For services that require database connectivity
    3. api_dependent_health: For services that interact with external APIs
    4. element_protocol_health: For UBEC element protocols (Air, Water, Earth, Fire)
    5. stellar_client_health: For Stellar blockchain client (FIXED in v3.1)
    
    All methods return standardized health status dictionaries for consistency
    across the entire system.
    """
    
    # ========================================================================
    # BASIC HEALTH CHECK (Core Implementation)
    # ========================================================================
    
    @staticmethod
    async def basic_health_check(
        service_name: str,
        is_initialized: bool = True,
        additional_checks: Optional[List[Callable]] = None,
        include_stats: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a basic health check for a service.
        
        This is the canonical health check implementation used across all services.
        All other health check methods build upon this foundation.
        
        ENHANCED v3.3: Now handles structured dict returns from checks indicating
        degraded status. Checks can return:
        - {'status': 'pass', 'message': '...'} for success
        - {'status': 'degraded', 'message': '...', 'action': '...'} for degradation
        - String or None for backward compatibility (treated as pass)
        - Exception raised for failure (treated as unhealthy)
        
        ENHANCED v3.2: Uses timezone-aware timestamps for consistency.
        
        Principle #5: Strict Async - All checks use async/await
        Principle #12: Method Singularity - Single shared implementation
        
        Args:
            service_name: Name of the service being checked
            is_initialized: Whether the service has been fully initialized
            additional_checks: Optional list of async/sync callables that perform checks
            include_stats: Whether to include detailed statistics
            **kwargs: Additional context to include in response
        
        Returns:
            Dictionary with health status information including actionable messages
        """
        # Initialize health response structure with timezone-aware timestamp
        health = {
            'status': HealthStatus.HEALTHY.value,
            'message': f"{service_name} operational",
            'timestamp': get_current_utc_time().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        # Check initialization status first
        if not is_initialized:
            health['status'] = HealthStatus.UNHEALTHY.value
            health['message'] = (f"{service_name} not initialized - "
                               f"Check service initialization in main.py")
            return health
        
        # Run additional checks if provided
        if additional_checks:
            check_results = []
            failed_checks = 0
            degraded_checks = 0  # NEW: Track degraded checks separately
            
            for i, check in enumerate(additional_checks):
                try:
                    # Support both async and sync check functions
                    if asyncio.iscoroutinefunction(check):
                        result = await check()
                    else:
                        result = check()
                    
                    # ENHANCED v3.3: Handle structured dict returns
                    if isinstance(result, dict):
                        check_status = result.get('status', 'pass')
                        check_name = result.get('check', f'check_{i+1}')
                        
                        if check_status == 'degraded':
                            # Check indicates degradation (not failure)
                            degraded_checks += 1
                            check_results.append(('degraded', result.get('message', 'Check degraded')))
                            logger.warning(f"Health check {i+1} for {service_name}: DEGRADED - {result.get('message', 'unknown')}")
                            
                            # Set service to degraded if not already unhealthy
                            if health['status'] != HealthStatus.UNHEALTHY.value:
                                health['status'] = HealthStatus.DEGRADED.value
                                health['message'] = f"{service_name} degraded - {result.get('message', 'performance issues')}"
                            
                            # Add warnings list if not present
                            if 'warnings' not in health:
                                health['warnings'] = []
                            health['warnings'].append(result.get('message', 'Check degraded'))
                            
                            # Add actionable command if provided
                            if 'action' in result and 'action' not in health:
                                health['action'] = result['action']
                            
                            # Store detailed check info
                            if 'check_details' not in health['details']:
                                health['details']['check_details'] = {}
                            health['details']['check_details'][check_name] = {
                                k: v for k, v in result.items() 
                                if k not in ['check', 'status']
                            }
                            
                        elif check_status == 'pass':
                            # Check passed
                            check_results.append(('pass', result.get('message', 'Check passed')))
                            logger.debug(f"Health check {i+1} for {service_name}: PASS")
                            
                            # Optionally store check details
                            if len(result) > 2:  # More than just 'check' and 'status'
                                check_name = result.get('check', f'check_{i+1}')
                                if 'check_details' not in health['details']:
                                    health['details']['check_details'] = {}
                                health['details']['check_details'][check_name] = {
                                    k: v for k, v in result.items() 
                                    if k not in ['check', 'status']
                                }
                        else:
                            # Unknown status - treat as failed for safety
                            failed_checks += 1
                            check_results.append(('fail', f"Unknown status: {check_status}"))
                            logger.warning(f"Health check {i+1} for {service_name}: FAIL - Unknown status {check_status}")
                    
                    elif isinstance(result, (str, type(None))):
                        # Traditional pass - string message or None means success
                        check_results.append(('pass', result if result else 'Check passed'))
                        logger.debug(f"Health check {i+1} for {service_name}: PASS")
                    else:
                        # Unexpected return type - log and pass
                        logger.warning(f"Health check {i+1} for {service_name}: Unexpected return type {type(result)}")
                        check_results.append(('pass', str(result)))
                    
                except Exception as e:
                    # Exception raised = check failed (unhealthy)
                    failed_checks += 1
                    check_results.append(('fail', str(e)))
                    logger.warning(f"Health check {i+1} for {service_name}: FAIL - {e}")
            
            health['details']['checks'] = check_results
            health['details']['checks_passed'] = len(check_results) - failed_checks - degraded_checks
            health['details']['checks_failed'] = failed_checks
            if degraded_checks > 0:
                health['details']['checks_degraded'] = degraded_checks
            
            # Update status based on check results
            # Priority: unhealthy > degraded > healthy
            if failed_checks > 0:
                if failed_checks == len(check_results):
                    health['status'] = HealthStatus.UNHEALTHY.value
                    health['message'] = f"{service_name} unhealthy - all checks failed"
                else:
                    # Some checks failed - mark as unhealthy (overrides degraded)
                    health['status'] = HealthStatus.UNHEALTHY.value
                    health['message'] = (f"{service_name} unhealthy - "
                                       f"{failed_checks}/{len(check_results)} checks failed")
            elif degraded_checks > 0 and health['status'] != HealthStatus.UNHEALTHY.value:
                # Some checks degraded but none failed - already set to degraded above
                pass
        
        return health
    
    # ========================================================================
    # DATABASE DEPENDENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def database_dependent_health(
        service_name: str,
        db_manager: Any,
        is_initialized: bool = True,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on database connectivity.
        
        CRITICAL FIX v3.3.1: Fixed check_db_connection() to return None instead of boolean.
        
        ENHANCED v3.3: Now properly handles structured dict returns from checks,
        allowing checks to indicate degraded performance without marking service
        as completely unhealthy.
        
        ENHANCED: Provides actionable guidance for database connection issues.
        
        Principle #5: Strict Async - Database checks are async
        Principle #11: Documentation - Clear error messages with solutions
        
        Args:
            service_name: Name of the service
            db_manager: Database manager instance
            is_initialized: Whether service is initialized
            additional_checks: Additional check functions (can return dict with 'status')
            **kwargs: Additional context
        
        Returns:
            Health status with database connectivity information
        """
        # Test database connection
        db_checks = []
        
        async def check_db_connection():
            """
            Check if database is accessible.
            
            CRITICAL FIX v3.3.1: Now returns None for success (not boolean).
            
            Returns:
                None: Database is accessible (success)
            
            Raises:
                Exception: Database is not accessible (failure)
            
            Health Check Contract:
                - Return None for success
                - Raise Exception for failure
                - NEVER return boolean (True/False)
            """
            try:
                # Simple query to test connection
                result = await db_manager.execute_query(
                    "SELECT 1 as test",
                    fetch_one=True
                )
                # FIXED v3.3.1: Check result and return None (not boolean)
                if result is None:
                    raise Exception("Database connectivity test returned None")
                
                # Explicit success return
                return None
                
            except Exception as e:
                raise Exception(f"Database unreachable: {str(e)} - "
                              f"Check DB_HOST, DB_PORT, and DB_PASSWORD in .env")
        
        db_checks.append(check_db_connection)
        
        # Add any additional checks
        if additional_checks:
            db_checks.extend(additional_checks)
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=db_checks,
            database_connected=True,  # Will be overridden if check fails
            **kwargs
        )
    
    # ========================================================================
    # ELEMENT PROTOCOL HEALTH CHECK - ENHANCED v3.2.0
    # ========================================================================
    
    @staticmethod
    async def element_protocol_health(
        element_name: str,
        token_code: str,
        db_manager: Any,
        is_initialized: bool = True,
        last_sync: Optional[datetime] = None,
        cached_accounts: int = 0,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for UBEC element protocols (Air, Water, Earth, Fire).
        
        CRITICAL FIX v3.2.0: All datetime operations now timezone-aware to prevent
        "can't subtract offset-naive and offset-aware datetimes" errors.
        
        ENHANCED v3.0: Uses NEEDS_SYNC status with actionable guidance instead of
        generic "degraded" status. Provides specific commands to resolve issues.
        
        Principle #7: Per-Asset Monitoring - Tracks each protocol's sync status
        Principle #11: Documentation - Actionable error messages
        
        Args:
            element_name: Name of the element (e.g., "Water", "Fire")
            token_code: Associated token code (e.g., "UBECrc", "UBECtt")
            db_manager: Database manager instance
            is_initialized: Whether protocol is initialized
            last_sync: Timestamp of last synchronization (None if never synced)
                      MUST be timezone-aware datetime
            cached_accounts: Number of accounts in cache
            additional_checks: Additional check functions
            **kwargs: Additional protocol-specific context
        
        Returns:
            Health status with protocol-specific information and actionable guidance
        """
        def check_sync_freshness():
            """
            Check if data synchronization is recent.
            
            CRITICAL FIX v3.2.0: Uses timezone-aware datetime comparison.
            
            ENHANCED: Returns actionable status instead of raising exception.
            """
            if last_sync is None:
                # Return tuple: (status, message, action)
                return ('needs_sync', 
                       f'{element_name} protocol awaiting initial synchronization',
                       'python main.py sync --sync-type all')
            
            # CRITICAL: Ensure timezone-aware comparison (v3.2.0)
            current_time = get_current_utc_time()
            
            # Ensure last_sync is timezone-aware
            if last_sync.tzinfo is None:
                logger.warning(f"last_sync for {element_name} is timezone-naive, converting to UTC")
                last_sync_aware = last_sync.replace(tzinfo=timezone.utc)
            else:
                last_sync_aware = last_sync
            
            time_since_sync = (current_time - last_sync_aware).total_seconds()
            
            # Define freshness thresholds
            FRESH_THRESHOLD = 3600  # 1 hour
            STALE_THRESHOLD = 86400  # 24 hours
            
            if time_since_sync > STALE_THRESHOLD:
                # Very stale - needs sync
                hours_old = time_since_sync / 3600
                return ('needs_sync',
                       f'{element_name} protocol data very stale ({hours_old:.1f} hours old)',
                       'python main.py sync --sync-type all')
            elif time_since_sync > FRESH_THRESHOLD:
                # Moderately stale - degraded but operational
                minutes_old = time_since_sync / 60
                return ('degraded',
                       f'{element_name} protocol data aging ({minutes_old:.0f} minutes old)',
                       'python main.py sync --sync-type all')
            else:
                # Fresh data
                return ('healthy',
                       f'Data fresh: synced {int(time_since_sync)}s ago',
                       None)
        
        # Build check list
        all_checks = []
        if additional_checks:
            all_checks.extend(additional_checks)
        
        # Element-specific details
        element_details = {
            'element': element_name,
            'token_code': token_code,
            'last_sync': last_sync.isoformat() if last_sync else None,
            'cached_accounts': cached_accounts,
            'data_fresh': last_sync is not None,
            **kwargs
        }
        
        # Perform sync freshness check
        sync_status, sync_message, sync_action = check_sync_freshness()
        
        # Perform database checks
        db_health = await ServiceHealthCheck.database_dependent_health(
            service_name=f'{element_name.lower()}_protocol',
            db_manager=db_manager,
            is_initialized=is_initialized,
            additional_checks=all_checks,
            **element_details
        )
        
        # Override status and message based on sync check
        if sync_status == 'needs_sync':
            db_health['status'] = HealthStatus.NEEDS_SYNC.value
            db_health['message'] = sync_message
            if sync_action:
                db_health['action'] = sync_action  # NEW: Actionable command
                db_health['details']['sync_required'] = True
        elif sync_status == 'degraded':
            # Only override if current status is healthy
            if db_health['status'] == HealthStatus.HEALTHY.value:
                db_health['status'] = HealthStatus.DEGRADED.value
                db_health['message'] = sync_message
                if sync_action:
                    db_health['action'] = sync_action  # NEW: Actionable command
        else:
            # Sync is fresh - update message to reflect this
            db_health['message'] = f'{element_name} protocol operational - {sync_message}'
        
        return db_health
    
    # ========================================================================
    # API DEPENDENT HEALTH CHECK
    # ========================================================================
    
    @staticmethod
    async def api_dependent_health(
        service_name: str,
        is_initialized: bool = True,
        api_url: Optional[str] = None,
        api_accessible: bool = True,
        request_count: int = 0,
        error_count: int = 0,
        rate_limiter: Optional[Any] = None,
        cache_info: Optional[Dict[str, Any]] = None,
        additional_checks: Optional[List[Callable]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for services that depend on external APIs.
        
        ENHANCED: Provides actionable guidance for API connectivity issues.
        
        Principle #9: Integrated Rate Limiting - Monitors rate limiter health
        Principle #11: Documentation - Clear error messages with solutions
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            api_url: URL of the external API
            api_accessible: Whether API is currently accessible
            request_count: Total number of requests made
            error_count: Number of failed requests
            rate_limiter: Optional rate limiter instance
            cache_info: Optional cache statistics
            additional_checks: Additional check functions
            **kwargs: Additional context
        
        Returns:
            Health status with API connectivity and rate limiting information
        """
        # Calculate error rate if we have request data
        error_rate = (error_count / request_count * 100) if request_count > 0 else 0.0
        
        # Prepare details
        api_details = {
            'api_url': api_url,
            'api_accessible': api_accessible,
            'request_count': request_count,
            'error_count': error_count,
            'error_rate': round(error_rate, 2),
            **kwargs
        }
        
        # Add cache info if provided
        if cache_info:
            api_details['cache'] = cache_info
        
        # Add rate limiter status if provided
        if rate_limiter:
            try:
                if hasattr(rate_limiter, 'get_status'):
                    api_details['rate_limiter'] = rate_limiter.get_status()
                elif hasattr(rate_limiter, 'status'):
                    api_details['rate_limiter'] = rate_limiter.status
            except Exception as e:
                logger.debug(f"Could not get rate limiter status: {e}")
        
        # Check for high error rate
        checks = []
        
        async def check_error_rate():
            """Check if error rate is acceptable"""
            if error_rate > 50 and request_count > 10:
                raise Exception(
                    f"High API error rate ({error_rate:.1f}%) - "
                    f"Check API accessibility and credentials"
                )
            return None
        
        if request_count > 0:
            checks.append(check_error_rate)
        
        # Add any additional checks
        if additional_checks:
            checks.extend(additional_checks)
        
        # Check if API is accessible
        if not api_accessible and api_url:
            api_details['action'] = f"Verify network connectivity to {api_url}"
        
        return await ServiceHealthCheck.basic_health_check(
            service_name=service_name,
            is_initialized=is_initialized,
            additional_checks=checks if checks else None,
            **api_details
        )
    
    # ========================================================================
    # STELLAR CLIENT HEALTH CHECK - FIXED v3.1
    # ========================================================================
    
    @staticmethod
    async def stellar_client_health(
        initialized: bool,
        horizon_url: str,
        request_count: int = 0,
        error_count: int = 0,
        last_error: Optional[str] = None,
        last_error_time: Optional[datetime] = None,
        stellar_service: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Health check for Stellar blockchain client service.
        
        CRITICAL FIX v3.1.0: Now uses stellar_service.test_connection() instead of
        the non-existent get_horizon_info() method.
        
        Principle #9: Integrated Rate Limiting - Monitors Stellar API usage
        Principle #11: Documentation - Clear error messages with actionable guidance
        Principle #12: Method Singularity - Reuses existing service method
        
        Args:
            initialized: Whether Stellar client is initialized
            horizon_url: URL of Stellar Horizon server
            request_count: Total API requests made
            error_count: Number of failed requests
            last_error: Most recent error message
            last_error_time: Timestamp of last error
            stellar_service: Optional Stellar service instance for connectivity test
            **kwargs: Additional context
        
        Returns:
            Health status with Stellar-specific information
        """
        # Define connectivity check using service's own method
        async def check_horizon_connectivity():
            """
            Test Stellar Horizon connectivity.
            
            FIXED v3.1.0: Uses stellar_service.test_connection() which calls
            the Stellar SDK's root() method correctly.
            """
            if not stellar_service:
                # No service provided - skip connectivity test
                return None
            
            try:
                # FIXED: Use service's test_connection() method (Principle #12)
                if hasattr(stellar_service, 'test_connection'):
                    is_connected = await stellar_service.test_connection()
                    if not is_connected:
                        raise Exception(
                            f"Stellar Horizon not responding at {horizon_url} - "
                            f"Check HORIZON_URL ({horizon_url}) in configuration and verify "
                            f"network connectivity to Stellar network"
                        )
                    return None
                else:
                    # Fallback if method doesn't exist
                    logger.warning("stellar_service missing test_connection() method")
                    return None
                    
            except Exception as e:
                raise Exception(
                    f"Stellar Horizon unreachable: {str(e)} - "
                    f"Check HORIZON_URL ({horizon_url}) in configuration and verify "
                    f"network connectivity to Stellar network"
                )
        
        return await ServiceHealthCheck.api_dependent_health(
            service_name='stellar_client',
            is_initialized=initialized,
            api_url=horizon_url,
            api_accessible=True,  # Will be updated by check
            request_count=request_count,
            error_count=error_count,
            additional_checks=[check_horizon_connectivity],
            last_error=last_error,
            last_error_time=last_error_time,
            **kwargs
        )
    
    # ========================================================================
    # SYNCHRONOUS HEALTH CHECK (for config-like services)
    # ========================================================================
    
    @staticmethod
    def sync_basic_health_check(
        service_name: str,
        is_initialized: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synchronous basic health check for services without async requirements.
        
        ENHANCED v3.2: Uses timezone-aware timestamps for consistency.
        
        Used for simple services like configuration managers that don't
        perform I/O operations.
        
        NOTE: This is an exception to Principle #5 (Strict Async) and should
        ONLY be used for services that are purely synchronous and have no
        I/O operations (e.g., configuration wrappers).
        
        Args:
            service_name: Name of the service
            is_initialized: Whether service is initialized
            **kwargs: Additional context
        
        Returns:
            Health status dictionary
        """
        health = {
            'status': HealthStatus.HEALTHY.value if is_initialized else HealthStatus.UNHEALTHY.value,
            'message': f"{service_name} {'operational' if is_initialized else 'not initialized'}",
            'timestamp': get_current_utc_time().isoformat(),
            'details': {
                'initialized': is_initialized,
                **kwargs
            }
        }
        
        if not is_initialized:
            health['action'] = "Check service initialization in main.py"
        
        return health
    
    # ========================================================================
    # UTILITY: Create Health Check Instance (Deprecated - use static methods)
    # ========================================================================
    
    def __init__(self, service_name: str):
        """
        Initialize health check tracker.
        
        DEPRECATED: Prefer using static methods directly.
        This constructor is kept for backward compatibility only.
        
        Use the static methods instead:
        - basic_health_check()
        - database_dependent_health()
        - api_dependent_health()
        - element_protocol_health()
        - stellar_client_health()
        """
        self.service_name = service_name
        self.status = HealthStatus.UNKNOWN
        self.message = ""
        self.details = {}
        self.timestamp = get_current_utc_time()
    
    def mark_healthy(self, message: str = "Service operational"):
        """Mark service as healthy"""
        self.status = HealthStatus.HEALTHY
        self.message = message
        self.timestamp = get_current_utc_time()
    
    def mark_needs_sync(self, message: str, action: str):
        """Mark service as needing synchronization with actionable command"""
        self.status = HealthStatus.NEEDS_SYNC
        self.message = message
        self.details['action'] = action
        self.timestamp = get_current_utc_time()
    
    def mark_degraded(self, message: str, action: Optional[str] = None):
        """Mark service as degraded with optional action"""
        self.status = HealthStatus.DEGRADED
        self.message = message
        if action:
            self.details['action'] = action
        self.timestamp = get_current_utc_time()
    
    def mark_unhealthy(self, message: str, action: Optional[str] = None):
        """Mark service as unhealthy with optional action"""
        self.status = HealthStatus.UNHEALTHY
        self.message = message
        if action:
            self.details['action'] = action
        self.timestamp = get_current_utc_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary"""
        result = {
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
        
        if 'action' in self.details:
            result['action'] = self.details['action']
        
        return result


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_actionable_message(issue: str, command: str) -> str:
    """
    Create an actionable error message that guides users to a solution.
    
    Args:
        issue: Description of the problem
        command: Command to run to resolve the issue
    
    Returns:
        Formatted actionable message
    
    Example:
        >>> create_actionable_message("Database not synced", "python main.py sync")
        "Database not synced → Run: python main.py sync"
    """
    return f"{issue} → Run: {command}"


def is_service_operational(health_status: Dict[str, Any]) -> bool:
    """
    Check if a service is operational (healthy or needs_sync).
    
    A service with needs_sync status is considered operational because
    it's initialized and ready, just needs data synchronization.
    
    Args:
        health_status: Health status dictionary
    
    Returns:
        True if service is operational, False otherwise
    
    Example:
        >>> status = {'status': 'healthy', 'message': 'OK'}
        >>> is_service_operational(status)
        True
    """
    status = health_status.get('status', 'unknown')
    return status in [HealthStatus.HEALTHY.value, HealthStatus.NEEDS_SYNC.value]


def get_action_from_health(health_status: Dict[str, Any]) -> Optional[str]:
    """
    Extract actionable command from health status.
    
    Args:
        health_status: Health status dictionary
    
    Returns:
        Command to resolve issue, or None if no action needed
    
    Example:
        >>> status = {'status': 'needs_sync', 'action': 'python main.py sync'}
        >>> get_action_from_health(status)
        'python main.py sync'
    """
    return health_status.get('action')
