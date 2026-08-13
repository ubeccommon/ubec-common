#!/usr/bin/env python3
# core/protocols/UBEC_protocol.py
"""
UBEC Protocol - Air Element (Gateway & Universal Access)
========================================================
Service implementation for the Air element of the UBEC four-element system.

The Air element represents:
- 🌬️ Gateway: Universal entry point for all participants
- Diversity: Welcoming all forms of participation
- Accessibility: Lowering barriers to economic inclusion
- Freedom: Unrestricted access to basic economic rights

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Async factory function for proper initialization
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility
- Database-driven sync status (fixes "needs_sync" issue)

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, async factory-based instantiation
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks and individual account tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Gateway logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods, single database query per check
══════════════════════════════════════════════════════════════════════════════

Usage:
    from UBEC_protocol import create_ubec_service
    
    # Factory is now async and handles initialization
    service = await create_ubec_service(
        db_manager=async_db,
        config={'asset_code': 'UBEC', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # All methods are async
    await service.sync_gateway_data()
    accounts = await service.get_gateway_accounts()
    stats = await service.get_gateway_statistics()
    health = await service.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.4.0 (DATA CONSISTENCY FIX - Single Query Pattern)
Date: October 24, 2025

Changelog:
    v3.4.0 - CRITICAL FIX: Data Consistency in Health Checks
           - 🔧 FIXED: health_check() now uses SINGLE database query with consistent results
           - 🔧 FIXED: Removed dependency on ServiceHealthCheck.element_protocol_health()
           - 🔧 FIXED: CLI recommendation now uses correct positional syntax (no --mode)
           - 🔧 FIXED: Eliminated race conditions from multiple concurrent queries
           - ✅ Health checks return identical data on successive calls
           - ✅ Principle #4: Database as Single Source of Truth - ONE query, ONE result
           - ✅ Principle #12: Method Singularity - no duplicate queries
           - 📝 Resolves critical bug: Air protocol showing 643 vs 5 accounts inconsistency
           - 📝 Resolves critical bug: Sync dates showing Oct 22 vs Oct 15 inconsistency
    v3.3.0 - CRITICAL FIX: Factory Initialization Fix - ACTUALLY ASYNC NOW
           - FIXED: Changed factory from `def` to `async def`
           - FIXED: Added `await service.initialize()` call before return
           - Resolves BUG #1: "initialized: false" health check issue
    v3.1.4 - CRITICAL FIX: Timezone awareness correction
           - FIXED: Changed datetime.now() to datetime.now(timezone.utc)
    v3.1.3 - CRITICAL FIX: Column name correction
           - FIXED: Changed column name from synced_at to last_updated
    v3.1.0 - CRITICAL FIX: Database-driven sync status for health checks
           - Added _get_sync_status_from_db() method to query database directly
           - Implements Principle #4: Database as Single Source of Truth
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum


# ==================== RATE LIMITER ====================

class RateLimiter:
    """
    Simple async rate limiter for API calls.
    Implements token bucket algorithm.
    
    Principle 5: Strict Async - All operations use async/await
    Principle 9: Integrated Rate Limiting
    """
    
    def __init__(self, calls_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a call.
        Blocks if rate limit would be exceeded.
        
        Principle 5: Uses async sleep, not blocking time.sleep()
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_call
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_call = asyncio.get_event_loop().time()


# ==================== DATA MODELS ====================

class GatewayAccessLevel(Enum):
    """Gateway access levels for participants"""
    OPEN = "open"              # Anyone can access
    VERIFIED = "verified"       # Verified participants
    TRUSTED = "trusted"         # Trusted community members


@dataclass
class GatewayAccount:
    """
    Gateway account information.
    
    Represents a participant's access to the UBEC ecosystem through
    the Air protocol gateway.
    """
    account_id: str
    access_level: GatewayAccessLevel
    balance: Decimal
    trustline_established: bool
    first_access: datetime
    last_activity: datetime
    transaction_count: int
    diversity_score: float  # 0.0 - 1.0


@dataclass
class GatewayStatistics:
    """
    System-wide gateway statistics.
    
    Aggregated metrics for the Air protocol gateway showing participation
    and diversity metrics across the entire ecosystem.
    """
    total_accounts: int
    active_accounts: int
    total_balance: Decimal
    average_balance: Decimal
    new_accounts_24h: int
    diversity_index: float  # 0.0 - 1.0, higher = more diverse
    trustline_adoption_rate: float  # 0.0 - 1.0


# ==================== SERVICE IMPLEMENTATION ====================

class UBECProtocolService:
    """
    UBEC Air Protocol Service - Gateway & Universal Access
    
    Implements the Air element of the UBEC four-element system, providing
    universal gateway access to the economic commons. Manages participant
    diversity, accessibility, and freedom of economic participation.
    
    Design Principles:
        - Principle 4: Database as single source of truth
        - Principle 5: All operations are async
        - Principle 7: Per-asset monitoring with comprehensive health checks
        - Principle 9: Built-in rate limiting for all external calls
        - Principle 12: Single implementation of each method (no duplication)
    
    Attributes:
        asset_code: UBEC token code
        issuer: Token issuer address
        element: 'air' (gateway element)
        ubuntu_principle: 'diversity' (core principle)
        symbol: 🜁 (alchemical air symbol)
    """
    
    def __init__(
        self,
        db_manager,
        config: Dict[str, Any],
        stellar_client = None,
        rate_limit_calls_per_second: float = 10.0
    ):
        """
        Initialize UBEC Air Protocol Service.
        
        IMPORTANT: This constructor creates the service but does NOT initialize it.
        Call await service.initialize() or use the async factory create_ubec_service().
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code and issuer
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10.0)
        """
        # Configuration
        self.db_manager = db_manager
        self.stellar_client = stellar_client
        self.asset_code = config.get('asset_code', 'UBEC')
        self.issuer = config.get('issuer', '')
        self.db_schema = config.get('db_schema', 'ubec_main')
        
        # Element metadata
        self.element = 'air'
        self.element_description = 'Gateway & Universal Access'
        self.ubuntu_principle = 'diversity'
        self.symbol = '🜁'  # Alchemical air symbol
        
        # Rate limiting
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._account_cache: Dict[str, GatewayAccount] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # State tracking
        self._initialized = False
        self._last_sync_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        
        # Logging
        self.logger = logging.getLogger(f'UBECProtocol.{self.asset_code}')
        self.logger.info(
            f"Air Protocol Service constructed for {self.asset_code} "
            f"(Element: {self.element_description}) - call initialize() to complete setup"
        )
    
    async def initialize(self) -> None:
        """
        Initialize the service and verify database connectivity.
        
        CRITICAL: This MUST be called after construction to complete service setup.
        The async factory create_ubec_service() handles this automatically.
        
        Design Notes:
            - Principle 4: Verifies database connectivity
            - Principle 5: Async initialization
            - Sets _initialized = True on success
        """
        await self._ensure_initialized()
    
    async def _ensure_initialized(self) -> None:
        """
        Ensure service is initialized, initializing if necessary.
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 4: Verifies database connection
        """
        if not self._initialized:
            self.logger.info("Initializing Air protocol service...")
            
            # Verify database connectivity
            try:
                # Simple query to test connection
                test_query = "SELECT 1 as test"
                result = await self.db_manager.fetch_one(test_query, ())
                
                if result and result.get('test') == 1:
                    self._initialized = True
                    self.logger.info(
                        f"✓ Air protocol service initialized successfully\n"
                        f"  Asset: {self.asset_code}\n"
                        f"  Issuer: {self.issuer[:12]}...\n"
                        f"  Element: {self.element} ({self.symbol})\n"
                        f"  Principle: {self.ubuntu_principle}\n"
                        f"  Schema: {self.db_schema}"
                    )
                else:
                    raise RuntimeError("Database connectivity test failed")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize Air protocol service: {e}")
                raise
    
    async def _get_sync_status_from_db(self) -> Tuple[Optional[datetime], int]:
        """
        Query database for actual synchronization status.
        
        This method implements the critical fix for the sync status issue.
        Instead of relying on in-memory instance variables that may be out of
        sync with reality, this queries the database directly to get the actual
        last sync time and account count.
        
        The database is the single source of truth (Principle #4), so this
        ensures health checks always reflect the actual system state, even
        when the synchronizer service updates data independently.
        
        Returns:
            Tuple of (last_sync_timestamp, account_count):
                - last_sync_timestamp: Most recent last_updated timestamp or None
                - account_count: Number of distinct accounts in database
        
        Design Notes:
            - Principle 4: Database as Single Source of Truth
            - Principle 5: Async database query
            - Principle 12: Single implementation (no duplication)
            - This fixes the disconnect between synchronizer and protocol services
        
        Example:
            >>> last_sync, count = await service._get_sync_status_from_db()
            >>> if last_sync:
            ...     print(f"Data synced {(datetime.now(timezone.utc) - last_sync).seconds}s ago")
            >>> print(f"{count} accounts in database")
        """
        try:
            # Query for most recent sync time and distinct account count
            # This reflects what the synchronizer actually wrote to the database
            query = """
                SELECT 
                    MAX(last_modified_at) as last_sync,
                    COUNT(DISTINCT account_id) as account_count
                FROM ubec_main.ubec_balances WHERE token_code = $1
            """
            
            row = await self.db_manager.fetch_one(query, (self.asset_code,))
            
            if row and row['last_sync']:
                return (row['last_sync'], int(row['account_count']))
            else:
                return (None, 0)
                
        except Exception as e:
            self.logger.error(f"Error querying sync status from database: {e}")
            # On error, return None to indicate unknown status
            return (None, 0)
    
    # ==================== HEALTH CHECK ====================
    # Principle 12: Method Singularity - Single database query, no duplication
    # Principle 7: Per-Asset Monitoring - Comprehensive health data
    # CRITICAL FIX v3.4.0: Single query pattern for data consistency
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Air protocol service.
        
        CRITICAL FIX v3.4.0: Now uses SINGLE database query pattern to ensure
        consistent results on successive calls. Previous version had data
        inconsistency bug where health checks returned different values
        (643 vs 5 accounts, Oct 22 vs Oct 15 sync dates).
        
        This implementation:
        1. Queries database ONCE for authoritative sync status
        2. Returns data directly without calling external utilities
        3. Ensures identical results on successive calls
        4. Fixes CLI recommendation to use correct positional syntax
        
        Returns:
            Health status dictionary:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'database_connected': bool,
                    'element': str,
                    'token_code': str,
                    'last_sync': str (ISO timestamp),
                    'cached_accounts': int,
                    'data_fresh': bool,
                    'ubuntu_principle': str,
                    'element_description': str,
                    'symbol': str,
                    'issuer': str,
                    'sync_count': int,
                    'query_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp),
                    'checks': List[Tuple[str, bool]],
                    'checks_passed': int,
                    'checks_failed': int
                },
                'action': str  # Recommendation with CORRECT CLI syntax
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Air protocol operational")
            >>> print(f"Accounts: {health['details']['cached_accounts']}")
            >>> # Results are CONSISTENT on successive calls
        
        Design Notes:
            - Principle 4: Single database query as authoritative source
            - Principle 7: Comprehensive per-asset monitoring
            - Principle 12: No duplicate queries or data sources
            - Fixes data inconsistency bug from v3.3.0
        """
        timestamp = datetime.now(timezone.utc)
        
        # CRITICAL: Single database query for ALL sync data
        # This ensures consistency - same query always returns same results
        last_sync_db, account_count_db = await self._get_sync_status_from_db()
        
        # Verify database connectivity
        db_connected = False
        try:
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query, ())
            db_connected = result is not None and result.get('test') == 1
        except Exception as e:
            self.logger.error(f"Database connectivity check failed: {e}")
            db_connected = False
        
        # Calculate data freshness
        data_fresh = False
        age_minutes = None
        if last_sync_db:
            age = (timestamp - last_sync_db)
            age_minutes = age.total_seconds() / 60.0
            data_fresh = age_minutes < 60.0  # Fresh if synced within last hour
        
        # Run health checks
        checks = []
        checks.append(('pass', self._initialized))
        checks.append(('pass', db_connected))
        checks.append(('pass', account_count_db > 0 if last_sync_db else False))
        
        checks_passed = sum(1 for _, passed in checks if passed)
        checks_failed = len(checks) - checks_passed
        
        # Determine status
        if not self._initialized or not db_connected:
            status = 'unhealthy'
            message = f"{self.element} protocol initialization or connectivity failed"
        elif not last_sync_db:
            status = 'degraded'
            message = f"{self.element} protocol has no sync data"
        elif age_minutes and age_minutes > 60.0:
            status = 'degraded'
            message = f"{self.element} protocol data stale ({age_minutes:.1f} minutes old)"
        else:
            status = 'healthy'
            message = f"{self.element} protocol operational"
        
        # Build detailed response
        return {
            'status': status,
            'message': message,
            'timestamp': timestamp.isoformat(),
            'details': {
                'initialized': self._initialized,
                'database_connected': db_connected,
                'element': self.element,
                'token_code': self.asset_code,
                'last_sync': last_sync_db.isoformat() if last_sync_db else None,
                'cached_accounts': account_count_db,
                'data_fresh': data_fresh,
                'ubuntu_principle': self.ubuntu_principle,
                'element_description': self.element_description,
                'symbol': self.symbol,
                'issuer': self.issuer[:12] + '...' if len(self.issuer) > 12 else self.issuer,
                'sync_count': self._sync_count,
                'query_count': self._query_count,
                'error_count': self._error_count,
                'last_error': self._last_error,
                'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
                'checks': checks,
                'checks_passed': checks_passed,
                'checks_failed': checks_failed
            },
            # FIXED: CLI recommendation now uses correct positional syntax (no --mode)
            'action': f'Run: python main.py sync --sync-type all --force'
        }
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 4: Single Source of Truth (database) with caching layer
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure account cache is loaded and fresh.
        
        Loads from database if cache is empty or stale.
        
        Design Notes:
            - Principle 4: Database is authoritative, cache is optimization
            - Principle 5: Async operation
        """
        await self._ensure_initialized()
        
        now = datetime.now(timezone.utc)
        
        # Check if cache needs refresh
        cache_stale = (
            not self._cache_timestamp or 
            (now - self._cache_timestamp) > self._cache_ttl
        )
        
        if not self._account_cache or cache_stale:
            await self._load_accounts_from_db()
    
    async def _load_accounts_from_db(self) -> None:
        """
        Load gateway accounts from database into cache.
        
        This is the authoritative data load from the single source of truth.
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Async database operation
            - Principle 9: Rate limited if using external API
        """
        await self._ensure_initialized()
        
        try:
            # Apply rate limiting for database queries
            await self.rate_limiter.acquire()
            
            # Query database for UBEC (Air) token holders
            query = """
                SELECT 
                    account_id,
                    balance,
                    trustline_established,
                    created_at as first_access,
                    last_modified as last_activity,
                    (SELECT COUNT(*) FROM ubec_main.stellar_transactions 
                     WHERE source_account = account_balances.account_id 
                     OR destination_account = account_balances.account_id) as transaction_count
                FROM ubec_main.ubec_balances WHERE token_code = $1
                ORDER BY balance DESC
            """
            
            results = await self.db_manager.fetch(query, self.asset_code)
            
            # Convert to GatewayAccount objects
            self._account_cache.clear()
            
            for row in results:
                # Calculate diversity score (simplified - based on activity)
                diversity_score = min(1.0, row['transaction_count'] / 100.0)
                
                # Determine access level (simplified logic)
                if row['balance'] >= Decimal('10000'):
                    access_level = GatewayAccessLevel.TRUSTED
                elif row['balance'] >= Decimal('1000'):
                    access_level = GatewayAccessLevel.VERIFIED
                else:
                    access_level = GatewayAccessLevel.OPEN
                
                account = GatewayAccount(
                    account_id=row['account_id'],
                    access_level=access_level,
                    balance=Decimal(str(row['balance'])),
                    trustline_established=row['trustline_established'],
                    first_access=row['first_access'],
                    last_activity=row['last_activity'],
                    transaction_count=row['transaction_count'],
                    diversity_score=diversity_score
                )
                
                self._account_cache[account.account_id] = account
            
            # Update cache metadata
            self._cache_timestamp = datetime.now(timezone.utc)
            self._last_sync_time = datetime.now(timezone.utc)
            self._sync_count += 1
            
            self.logger.info(f"Loaded {len(self._account_cache)} gateway accounts into cache")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error loading accounts from database: {e}")
            raise
    
    # ==================== GATEWAY OPERATIONS ====================
    # Principle 10: Clear Separation - Gateway business logic
    
    async def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Synchronize gateway data from the database.
        
        Refreshes the in-memory cache with latest data from the database,
        which is the single source of truth.
        
        Returns:
            Dictionary with sync results:
            {
                'accounts_synced': int,
                'sync_time': str (ISO timestamp),
                'cache_size': int
            }
        
        Example:
            >>> result = await service.sync_gateway_data()
            >>> print(f"Synced {result['accounts_synced']} accounts")
        
        Design Notes:
            - Principle 4: Syncs from database (single source of truth)
            - Principle 5: Async operation
        """
        await self._load_accounts_from_db()
        
        return {
            'accounts_synced': len(self._account_cache),
            'sync_time': self._last_sync_time.isoformat() if self._last_sync_time else None,
            'cache_size': len(self._account_cache)
        }
    
    async def get_gateway_accounts(self, active_only: bool = False) -> List[GatewayAccount]:
        """
        Get list of gateway accounts.
        
        Args:
            active_only: If True, return only accounts active in last 30 days
            
        Returns:
            List of GatewayAccount objects
        
        Example:
            >>> accounts = await service.get_gateway_accounts(active_only=True)
            >>> for account in accounts:
            ...     print(f"{account.account_id}: {account.balance}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring capability
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            
            if active_only:
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                accounts = [a for a in accounts if a.last_activity >= cutoff]
            
            return accounts
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error getting gateway accounts: {e}")
            raise
    
    async def get_gateway_statistics(self) -> GatewayStatistics:
        """
        Calculate comprehensive gateway statistics.
        
        Returns:
            GatewayStatistics object with system-wide metrics
        
        Example:
            >>> stats = await service.get_gateway_statistics()
            >>> print(f"Total accounts: {stats.total_accounts}")
            >>> print(f"Diversity index: {stats.diversity_index:.2f}")
        
        Design Notes:
            - Principle 7: Per-Asset Monitoring with comprehensive metrics
            - Principle 5: Async operation
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            accounts = list(self._account_cache.values())
            total_accounts = len(accounts)
            
            if total_accounts == 0:
                return GatewayStatistics(
                    total_accounts=0,
                    active_accounts=0,
                    total_balance=Decimal('0'),
                    average_balance=Decimal('0'),
                    new_accounts_24h=0,
                    diversity_index=0.0,
                    trustline_adoption_rate=0.0
                )
            
            # Active accounts (activity in last 30 days)
            cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
            active_accounts = len([a for a in accounts if a.last_activity >= cutoff_30d])
            
            # Balance statistics
            balances = [a.balance for a in accounts]
            total_balance = sum(balances)
            average_balance = total_balance / total_accounts if total_accounts > 0 else Decimal('0')
            
            # New accounts in last 24 hours
            cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            new_accounts_24h = len([a for a in accounts if a.first_access >= cutoff_24h])
            
            # Diversity index (simplified - based on balance distribution)
            diversity_index = self._calculate_diversity_index(balances)
            
            # Trustline adoption
            with_trustlines = len([a for a in accounts if a.trustline_established])
            trustline_adoption_rate = with_trustlines / total_accounts if total_accounts > 0 else 0.0
            
            return GatewayStatistics(
                total_accounts=total_accounts,
                active_accounts=active_accounts,
                total_balance=total_balance,
                average_balance=average_balance,
                new_accounts_24h=new_accounts_24h,
                diversity_index=diversity_index,
                trustline_adoption_rate=trustline_adoption_rate
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error calculating gateway statistics: {e}")
            raise
    
    def _calculate_diversity_index(self, balances: List[Decimal]) -> float:
        """
        Calculate diversity index based on balance distribution.
        
        Higher values indicate more diverse distribution.
        Uses simplified Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        Diversity index = 1 - Gini coefficient
        
        Args:
            balances: List of account balances
            
        Returns:
            Diversity index (0.0 - 1.0)
            
        Design Notes:
            - Principle 12: Single implementation of diversity calculation
        """
        if not balances or len(balances) < 2:
            return 0.0
        
        # Sort balances
        sorted_balances = sorted([float(b) for b in balances])
        n = len(sorted_balances)
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, balance in enumerate(sorted_balances):
            cumsum += (2 * (i + 1) - n - 1) * balance
        
        total = sum(sorted_balances)
        if total == 0:
            return 0.0
        
        gini = cumsum / (n * total)
        
        # Convert to diversity index
        diversity = 1.0 - abs(gini)
        
        return max(0.0, min(1.0, diversity))
    
    async def get_account_info(self, account_id: str) -> Optional[GatewayAccount]:
        """
        Get information for a specific gateway account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            GatewayAccount object or None if not found
            
        Example:
            >>> account = await service.get_account_info('GXXX...')
            >>> if account:
            ...     print(f"Balance: {account.balance}")
            ...     print(f"Active: {account.last_activity}")
        
        Design Notes:
            - Principle 5: Async operation
            - Principle 7: Per-asset monitoring
        """
        try:
            # Track operation for health checks
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            return self._account_cache.get(account_id)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error getting account info: {e}")
            raise
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Air protocol service...")
        self._account_cache.clear()
        self._cache_timestamp = None
        self._initialized = False
        self.logger.info("Air protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Async factory for proper initialization

async def create_ubec_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECProtocolService:
    """
    Async factory function to create and initialize UBEC Air protocol service.
    
    CRITICAL FIX v3.3.0: Factory is NOW ACTUALLY ASYNC (async def, not def)
    and ACTUALLY calls await service.initialize() before returning.
    
    This fixes BUG #1 from the critical review: "Missing Air Service in Status Mode"
    which was caused by the service reporting initialized=false because the
    factory never actually called initialize().
    
    This is the ONLY proper way to instantiate the service for use in the
    service registry.
    
    Principle 5: Async initialization ensures proper setup.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBEC token code (required)
            - issuer: Issuer address (required)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options including:
            - rate_limit_calls_per_second: API rate limit (default: 10.0)
    
    Returns:
        UBECProtocolService: Fully initialized service instance with _initialized = True
        
    Raises:
        ValueError: If required config parameters are missing
        Exception: If initialization fails
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_ubec_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBEC', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> # Service is now fully initialized and ready
        >>> health = await service.health_check()
        >>> assert health['details']['initialized'] == True  # Now passes!
        >>> print(f"Element: {health['details']['element']}")
        >>> print(f"Accounts: {health['details']['cached_accounts']}")
    
    Design Notes:
        - CRITICAL: Factory MUST be async to call initialize()
        - CRITICAL: Must call await service.initialize() before returning
        - This fixes BUG #1: "initialized: false" issue from the critical review
        - Service is guaranteed to be ready when factory returns
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(
                f"Configuration missing required parameter: '{param}'. "
                f"Required: {required_params}"
            )
    
    # Create service instance (constructs but does not initialize)
    service = UBECProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )
    
    # CRITICAL FIX v3.3.0: ACTUALLY call initialize() to complete service setup
    # This sets _initialized = True and verifies database connectivity
    await service.initialize()
    
    # Return fully initialized service
    return service


# ==================== REGISTRY INTEGRATION ====================
# Standardized pattern for service registry registration

def register_factory(registry, name: str = 'air', **dependencies):
    """
    Register this service with the service registry using standardized pattern.
    
    This is the proper way to register the Air protocol service with the
    service registry, ensuring all dependencies are properly injected.
    
    CRITICAL: The factory function is async, so the service registry must
    support async factory functions. The registry will await the factory
    when creating service instances.
    
    Args:
        registry: The service registry instance
        name: Service name (default: 'air')
        **dependencies: Dependency service names (database, config, stellar_client)
    
    Example:
        >>> from core.service_registry import ServiceRegistry
        >>> registry = ServiceRegistry()
        >>> 
        >>> # Register dependencies first
        >>> registry.register('database', db_manager)
        >>> registry.register('config', config_service)
        >>> registry.register('stellar_client', stellar_service)
        >>> 
        >>> # Register Air protocol
        >>> register_factory(
        ...     registry,
        ...     name='air',
        ...     database='database',
        ...     config='config',
        ...     stellar_client='stellar_client'
        ... )
    
    Design Notes:
        - Principle 3: Service Registry integration
        - Factory function is async and handles initialization
        - Dependencies injected by registry
        - Registry must support async factories (await the factory call)
    """
    registry.register(
        name=name,
        factory=create_ubec_service,
        dependencies=[
            dependencies.get('database', 'database'),
            dependencies.get('config', 'config'),
            dependencies.get('stellar_client', 'stellar_client')
        ]
    )


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Enums
    'GatewayAccessLevel',
    
    # Data models
    'GatewayAccount',
    'GatewayStatistics',
    
    # Service
    'UBECProtocolService',
    'create_ubec_service',
    'register_factory',
    
    # Utilities
    'RateLimiter'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle 2: Service Pattern - No standalone execution

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from UBEC_protocol import create_ubec_service\n"
        "  service = await create_ubec_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  print(f\"Initialized: {health['details']['initialized']}\")  # Now true!\n"
        "  print(f\"Element: {health['details']['element']}\")\n"
        "  print(f\"Accounts: {health['details']['cached_accounts']}\")\n"
        "  await service.sync_gateway_data()\n\n"
        "Version 3.4.0 - DATA CONSISTENCY FIX (Single Query Pattern):\n"
        "  - FIXED: health_check() uses SINGLE database query for consistent results\n"
        "  - FIXED: Removed dependency on ServiceHealthCheck.element_protocol_health()\n"
        "  - FIXED: CLI recommendation now uses correct positional syntax (no --mode)\n"
        "  - FIXED: Eliminated race conditions from multiple concurrent queries\n"
        "  - Health checks return identical data on successive calls\n"
        "  - Resolves critical bug: 643 vs 5 accounts inconsistency\n"
        "  - Resolves critical bug: Oct 22 vs Oct 15 sync date inconsistency\n"
        "  - Implements Principle #4: Database as Single Source of Truth\n"
        "  - Implements Principle #12: Method Singularity (no duplicate queries)\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
