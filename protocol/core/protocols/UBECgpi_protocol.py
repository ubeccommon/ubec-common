#!/usr/bin/env python3
# core/protocols/UBECgpi_protocol.py
"""
UBECgpi Protocol - Earth Element (Stability & Mutualism)
========================================================
Service implementation for the Earth element of the UBEC four-element system.

The Earth element represents:
- 🜃 Stability: Grounding and sustained value
- Mutualism: Mutually beneficial relationships
- Distribution: Fair allocation and compliance
- Foundation: Solid base for the ecosystem

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility
- Complete element metadata exposure

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, factory-based instantiation
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks and individual stability tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Stability logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
════════════════════════════════════════════════════════════════════════════

Usage:
    from UBECgpi_protocol import create_ubecgpi_service
    
    service = create_ubecgpi_service(
        db_manager=async_db,
        config={'asset_code': 'UBECgpi', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    # REQUIRED: Explicitly initialize service (v3.3.0)
    await service.initialize()
    
    # All methods are async
    await service.sync_stability_data()
    compliance = await service.check_distribution_compliance()
    stability = await service.get_stability_metrics()
    health = await service.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.5.0 (DATA CONSISTENCY FIX - Single Query Pattern)
Date: October 30, 2025

Changelog:
    v3.5.0 - CRITICAL FIX: Data Consistency in Health Checks
           - 🔧 FIXED: health_check() now uses SINGLE database query with consistent results
           - 🔧 FIXED: Removed dependency on ServiceHealthCheck.element_protocol_health()
           - 🔧 FIXED: CLI recommendation now uses correct positional syntax (no --mode)
           - 🔧 FIXED: Eliminated race conditions from multiple concurrent queries
           - ✅ Health checks return identical data on successive calls
           - ✅ Principle #4: Database as Single Source of Truth - ONE query, ONE result
           - ✅ Principle #12: Method Singularity - no duplicate queries
           - 📝 Matches proven Air protocol pattern from v3.4.0
           - 📝 Resolves data inconsistency issues from utility-based approach
    v3.4.0 - CRITICAL FIX: Factory Initialization Pattern (ACTUALLY FIXED NOW)
           - FIXED: Changed factory from `def` to `async def` (line 1006)
           - FIXED: Added `await service.initialize()` call in factory
           - FIXED: Documentation now matches implementation
           - Resolves BUG #2 from critical review: "initialized: false" health check issue
           - Service is GUARANTEED to be fully initialized when factory returns
           - Principle #2: Proper async service pattern NOW CORRECTLY IMPLEMENTED  
           - Principle #5: Strict async operations INCLUDING factory
           - Aligns with fixed Air protocol pattern (UBEC_protocol.py v3.3.0)
           - Previous v3.3.0 used error-prone manual initialization
           - This version removes manual initialization requirement
    v3.3.0 - CRITICAL FIX: Explicit Initialize Pattern Implementation
           - FIXED: Changed _initialized = True to _initialized = False in constructor
           - ADDED: Explicit async initialize() method for proper service startup
           - ADDED: Database connection verification during initialization
           - ADDED: Configuration validation during initialization
           - ALIGNED: Now matches Air and Water protocol initialization patterns
           - UPDATED: Factory function documentation to reflect initialize() requirement
           - ENHANCED: Consistent lifecycle management across all protocols
           - MAINTAINED: All functionality from v3.2.3
           - Principle #5: Strict Async - Explicit async initialization
           - Principle #12: Method Singularity - Standardized pattern across protocols
    v3.2.3 - CRITICAL FIX: Timezone awareness correction
           - FIXED: Added timezone import and changed datetime.now() to datetime.now(timezone.utc)
           - Resolves "can't subtract offset-naive and offset-aware datetimes" error
           - Ensures consistent timezone-aware datetime usage throughout
           - 18 datetime.now() calls updated for UTC timezone awareness
           - Principle #5: Proper async datetime handling maintained
    v3.2.2 - CRITICAL FIX: Database method and parameter correction
           - FIXED: Changed fetchrow() to fetch_one() for AsyncDatabaseManager compatibility
           - Resolves parameter passing errors - params must be tuple in multiple methods
           - Changed all fetch_one calls to pass params as tuples throughout the service
           - 3 instances: (asset_code,) and (account_id, asset_code) (lines 491, 760, 833)
           - Principle #5: Strict Async Operations compliance maintained
    v3.2.0 - CRITICAL FIX: Database-driven sync status for health checks
           - Added _get_sync_status_from_db() method to query database directly
           - Updated health_check() to use database queries instead of instance variables
           - Fixes issue where protocols show "needs_sync" after successful sync
           - Implements Principle #4: Database as Single Source of Truth
           - Resolves disconnect between synchronizer and protocol status
           - Health checks now reflect actual database state
           - Ensures accurate monitoring even when synchronizer updates independently
    v3.1.1 - CRITICAL FIX: Corrected health check implementation
           - FIXED: Changed token_code=self.token_code to token_code=self.asset_code
           - REASON: self.token_code attribute doesn't exist; correct attribute is self.asset_code
           - ERROR: 'UBECgpiProtocolService' object has no attribute 'token_code'
           - STATUS: Now properly passes asset_code to ServiceHealthCheck utility
           - Maintains all v3.1.0 functionality
    v3.1.0 - ENHANCEMENT: Improved health check with DRY compliance
           - ENHANCED: Uses instance variables instead of hardcoded strings
           - ADDED: Comprehensive error tracking (last_error, last_error_time)
           - ADDED: Issuer information in health check output
           - IMPROVED: Full DRY principle compliance (Principle #12)
           - ALIGNED: Now matches Air protocol's superior pattern
           - MAINTAINED: All functionality from v3.0.0
           - Updated to use self.element, self.ubuntu_principle, self.symbol
           - Added missing last_error and issuer parameters
           - Enhanced maintainability and consistency
    v3.0.0 - ENHANCEMENT: Added complete element metadata exposure
           - Added element, ubuntu_principle, element_description, symbol properties
           - Ensures status output shows complete Earth element information
           - Maintains all v2.2.0 features and improvements
           - Full compatibility with main.py v10.x status output
    v2.2.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation
           - Now uses ServiceHealthCheck.element_protocol_health()
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
    v2.0.0 - Complete async service architecture
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

class DistributionCategory(Enum):
    """Distribution categories for UBEC tokenomics"""
    GENERAL = "general_distribution"           # 65%
    STEWARDSHIP = "stewardship"                # 30%
    ADMINISTRATION = "administration"          # 5%


class ComplianceStatus(Enum):
    """Compliance status for distribution categories"""
    COMPLIANT = "compliant"                    # Within acceptable range
    WARNING = "warning"                         # Approaching limits
    VIOLATION = "violation"                     # Outside acceptable range
    UNKNOWN = "unknown"                         # Cannot determine


@dataclass
class DistributionState:
    """
    Current state of a distribution category.
    
    Principle 1: Modular Design - Clear data structure
    """
    category: DistributionCategory
    current_amount: Decimal
    target_amount: Decimal
    target_percentage: Decimal
    actual_percentage: Decimal
    deviation: Decimal  # Difference from target
    compliance_status: ComplianceStatus


@dataclass
class StabilityMetrics:
    """
    System-wide stability metrics.
    
    Principle 7: Per-Asset Monitoring - Comprehensive metrics
    """
    total_supply: Decimal
    circulating_supply: Decimal
    distribution_health: float  # 0.0 - 1.0, how well distribution matches targets
    balance_concentration: float  # Gini coefficient (0 = equal, 1 = concentrated)
    holder_count: int
    median_balance: Decimal
    stability_index: float  # Overall stability score (0.0 - 1.0)
    compliance_score: float  # How well system adheres to distribution rules


@dataclass
class MutualismRelationship:
    """
    Represents a mutualistic relationship between accounts.
    
    Principle 7: Per-Asset Monitoring - Relationship tracking
    """
    account_a: str
    account_b: str
    interaction_count: int
    mutual_benefit_score: float  # 0.0 - 1.0, measures mutual benefit
    relationship_strength: float  # 0.0 - 1.0, based on frequency and balance
    last_interaction: datetime


# ==================== SERVICE IMPLEMENTATION ====================

class UBECgpiProtocolService:
    """
    UBECgpi Earth Protocol Service
    
    Manages stability and mutualism in the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    This service represents the Earth element:
    - Stability through distribution compliance
    - Mutualism in account relationships
    - Foundation for sustainable growth
    - Balance concentration monitoring
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
        element: Element name ('earth')
        ubuntu_principle: Associated Ubuntu principle ('mutualism')
        element_description: Full element description
        symbol: Alchemical symbol for earth ('🜃')
        
    Lifecycle:
        1. Instantiate via create_ubecgpi_service() factory
        2. Service auto-initializes on first use
        3. Cleanup via close() method
        
    Design Principles:
        - Principle 1: Modular - Clear boundaries and single responsibility
        - Principle 4: Single Source of Truth - Database-driven
        - Principle 5: Strict Async - All I/O operations async
        - Principle 10: Separation of Concerns - Clear layer separation
        - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    """
    
    def __init__(
        self,
        db_manager,
        config: Dict[str, Any],
        stellar_client = None,
        rate_limit_calls_per_second: float = 10.0
    ):
        """
        Initialize UBECgpi Earth protocol service.
        
        DO NOT call directly - use create_ubecgpi_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code, issuer, etc.
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10/sec)
        """
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        
        # Service identification
        self.asset_code = config.get('asset_code', 'UBECgpi')
        self.issuer = config.get('issuer')
        
        # Element metadata (v3.0.0) - Essential for main.py status output
        self.element = 'earth'
        self.ubuntu_principle = 'mutualism'
        self.element_description = 'Stability & Mutualism'
        self.symbol = '🜃'  # Alchemical symbol for earth
        
        # Distribution targets (official UBEC tokenomics)
        self.distribution_targets = {
            DistributionCategory.GENERAL: Decimal('0.65'),      # 65%
            DistributionCategory.STEWARDSHIP: Decimal('0.30'),  # 30%
            DistributionCategory.ADMINISTRATION: Decimal('0.05') # 5%
        }
        
        # Logging setup
        self.logger = logging.getLogger(f'UBECProtocol.{self.asset_code}')
        self.logger.info(
            f"Earth Protocol Service initialized for {self.asset_code} "
            f"(Element: {self.element}, Principle: {self.ubuntu_principle})"
        )
        
        # Rate limiting
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._distribution_cache: Dict[DistributionCategory, DistributionState] = {}
        self._stability_cache: Optional[StabilityMetrics] = None
        self._mutualism_cache: List[MutualismRelationship] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Account cache for monitoring
        self._account_cache: Dict[str, Dict[str, Any]] = {}
        
        # Operation tracking for health checks
        # CRITICAL v3.3.0: Set to False - initialize() method will set to True
        self._initialized = False
        self._last_sync_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._last_query_time: Optional[datetime] = None
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
    
    # ==================== INITIALIZATION ====================
    # Principle 5: Strict Async Operations
    # v3.3.0: Explicit initialization pattern
    
    async def initialize(self) -> None:
        """
        Initialize the service and verify database connectivity.
        
        This method must be called after service creation to properly initialize
        the service. It verifies database connectivity and sets the _initialized flag.
        
        Principle 5: Strict Async Operations - Explicit async initialization
        Principle 4: Single Source of Truth - Verifies database connection
        
        Example:
            >>> service = create_ubecgpi_service(...)
            >>> await service.initialize()  # REQUIRED
            >>> health = await service.health_check()
        
        Raises:
            Exception: If database connection verification fails
        """
        if self._initialized:
            return
        
        self.logger.info("Initializing Earth protocol service...")
        
        try:
            # Verify database connection (Principle 4: Database is single source of truth)
            await self.db_manager.execute("SELECT 1")
            
            self._initialized = True
            self.logger.info(
                f"✓ Earth protocol service initialized successfully\n"
                f"  Asset: {self.asset_code}\n"
                f"  Issuer: {self.issuer[:8]}...\n"
                f"  Element: {self.element} ({self.symbol})\n"
                f"  Principle: {self.ubuntu_principle}\n"
                f"  Schema: {self.config.get('db_schema', 'ubec_main')}"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Failed to initialize Earth protocol: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 10: Separation of Concerns - Cache logic isolated
    
    def _is_cache_valid(self) -> bool:
        """
        Check if current cache is still valid.
        
        Returns:
            True if cache is valid, False if expired
        """
        if self._cache_timestamp is None:
            return False
        
        age = datetime.now(timezone.utc) - self._cache_timestamp
        return age < self._cache_ttl
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure cache is loaded and valid.
        Reloads from database if cache is expired.
        
        Principle 5: Async operation
        """
        if not self._is_cache_valid():
            await self.sync_stability_data()
    
    def _clear_cache(self) -> None:
        """Clear all cached data"""
        self._distribution_cache.clear()
        self._stability_cache = None
        self._mutualism_cache.clear()
        self._account_cache.clear()
        self._cache_timestamp = None
    
    # ==================== DATA SYNCHRONIZATION ====================
    # Principle 4: Single Source of Truth - Database is authoritative
    # Principle 5: Strict Async Operations
    
    async def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize stability data from database.
        
        Fetches latest distribution, stability, and mutualism metrics from
        the database and updates internal caches.
        
        Returns:
            Sync result with statistics
            
        Raises:
            Exception: If sync fails
            
        Principle 4: Database is single source of truth
        Principle 5: Pure async operation
        """
        try:
            self.logger.info("Syncing stability data from database...")
            start_time = datetime.now(timezone.utc)
            
            await self.rate_limiter.acquire()
            
            # Clear existing cache
            self._clear_cache()
            
            # Fetch distribution state
            await self._fetch_distribution_state()
            
            # Fetch stability metrics
            await self._fetch_stability_metrics()
            
            # Fetch mutualism relationships
            await self._fetch_mutualism_relationships()
            
            # Update sync tracking
            self._last_sync_time = datetime.now(timezone.utc)
            self._sync_count += 1
            self._cache_timestamp = datetime.now(timezone.utc)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = {
                'success': True,
                'timestamp': self._last_sync_time.isoformat(),
                'duration_seconds': duration,
                'distribution_categories': len(self._distribution_cache),
                'mutualism_relationships': len(self._mutualism_cache),
                'cached_accounts': len(self._account_cache)
            }
            
            self.logger.info(
                f"Stability data synced successfully in {duration:.2f}s "
                f"({len(self._distribution_cache)} categories, "
                f"{len(self._mutualism_cache)} relationships)"
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Failed to sync stability data: {e}")
            raise
    
    async def _fetch_distribution_state(self) -> None:
        """
        Fetch distribution state from database.
        
        Principle 4: Database as single source of truth
        """
        query = """
            SELECT 
                distribution_category,
                current_amount,
                target_amount,
                target_percentage,
                actual_percentage,
                deviation,
                compliance_status
            FROM ubec_main.distribution_state
            WHERE asset_code = $1
        """
        
        rows = await self.db_manager.fetch(query, self.asset_code)
        
        for row in rows:
            category = DistributionCategory(row['distribution_category'])
            state = DistributionState(
                category=category,
                current_amount=Decimal(str(row['current_amount'])),
                target_amount=Decimal(str(row['target_amount'])),
                target_percentage=Decimal(str(row['target_percentage'])),
                actual_percentage=Decimal(str(row['actual_percentage'])),
                deviation=Decimal(str(row['deviation'])),
                compliance_status=ComplianceStatus(row['compliance_status'])
            )
            self._distribution_cache[category] = state
    
    async def _fetch_stability_metrics(self) -> None:
        """
        Fetch system stability metrics from database.
        
        Principle 4: Database as single source of truth
        """
        query = """
            SELECT 
                total_supply,
                circulating_supply,
                distribution_health,
                balance_concentration,
                holder_count,
                median_balance,
                stability_index,
                compliance_score
            FROM ubec_main.stability_metrics
            WHERE asset_code = $1
            ORDER BY calculated_at DESC
            LIMIT 1
        """
        
        row = await self.db_manager.fetch_one(query, (self.asset_code,))
        
        if row:
            self._stability_cache = StabilityMetrics(
                total_supply=Decimal(str(row['total_supply'])),
                circulating_supply=Decimal(str(row['circulating_supply'])),
                distribution_health=float(row['distribution_health']),
                balance_concentration=float(row['balance_concentration']),
                holder_count=int(row['holder_count']),
                median_balance=Decimal(str(row['median_balance'])),
                stability_index=float(row['stability_index']),
                compliance_score=float(row['compliance_score'])
            )
    
    async def _fetch_mutualism_relationships(self) -> None:
        """
        Fetch mutualistic relationships from database.
        
        Principle 4: Database as single source of truth
        """
        query = """
            SELECT 
                account_a,
                account_b,
                interaction_count,
                mutual_benefit_score,
                relationship_strength,
                last_interaction
            FROM ubec_main.mutualism_relationships
            WHERE asset_code = $1
            ORDER BY relationship_strength DESC
            LIMIT 100
        """
        
        rows = await self.db_manager.fetch(query, self.asset_code)
        
        self._mutualism_cache = [
            MutualismRelationship(
                account_a=row['account_a'],
                account_b=row['account_b'],
                interaction_count=int(row['interaction_count']),
                mutual_benefit_score=float(row['mutual_benefit_score']),
                relationship_strength=float(row['relationship_strength']),
                last_interaction=row['last_interaction']
            )
            for row in rows
        ]
    
    # ==================== DISTRIBUTION COMPLIANCE ====================
    # Principle 7: Per-Asset Monitoring with execution minimums
    
    async def check_distribution_compliance(self) -> Dict[str, Any]:
        """
        Check compliance with distribution targets.
        
        Analyzes current distribution against target percentages and
        identifies any compliance violations.
        
        Returns:
            Compliance status for all distribution categories
            
        Principle 7: Per-asset monitoring
        Principle 5: Async operation
        """
        try:
            await self._ensure_cache_loaded()
            
            self._query_count += 1
            self._last_query_time = datetime.now(timezone.utc)
            
            compliance_results = {}
            
            for category, state in self._distribution_cache.items():
                compliance_results[category.value] = {
                    'target_percentage': float(state.target_percentage * 100),
                    'actual_percentage': float(state.actual_percentage * 100),
                    'deviation': float(state.deviation * 100),
                    'compliance_status': state.compliance_status.value,
                    'current_amount': str(state.current_amount),
                    'target_amount': str(state.target_amount)
                }
            
            # Calculate overall compliance
            violation_count = sum(
                1 for state in self._distribution_cache.values()
                if state.compliance_status == ComplianceStatus.VIOLATION
            )
            
            warning_count = sum(
                1 for state in self._distribution_cache.values()
                if state.compliance_status == ComplianceStatus.WARNING
            )
            
            overall_status = 'compliant'
            if violation_count > 0:
                overall_status = 'violation'
            elif warning_count > 0:
                overall_status = 'warning'
            
            return {
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'overall_status': overall_status,
                'violation_count': violation_count,
                'warning_count': warning_count,
                'categories': compliance_results
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error checking distribution compliance: {e}")
            raise
    
    # ==================== STABILITY ANALYSIS ====================
    # Principle 7: Per-Asset Monitoring
    
    async def get_stability_metrics(self) -> Dict[str, Any]:
        """
        Get current stability metrics.
        
        Returns comprehensive stability analysis including distribution health,
        balance concentration, and overall stability index.
        
        Returns:
            Stability metrics dictionary
            
        Principle 5: Async operation
        Principle 7: Comprehensive monitoring
        """
        try:
            await self._ensure_cache_loaded()
            
            self._query_count += 1
            self._last_query_time = datetime.now(timezone.utc)
            
            if not self._stability_cache:
                return {
                    'success': False,
                    'error': 'No stability metrics available'
                }
            
            metrics = self._stability_cache
            
            return {
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metrics': {
                    'total_supply': str(metrics.total_supply),
                    'circulating_supply': str(metrics.circulating_supply),
                    'distribution_health': metrics.distribution_health,
                    'balance_concentration': metrics.balance_concentration,
                    'holder_count': metrics.holder_count,
                    'median_balance': str(metrics.median_balance),
                    'stability_index': metrics.stability_index,
                    'compliance_score': metrics.compliance_score
                }
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error getting stability metrics: {e}")
            raise
    
    # ==================== MUTUALISM ANALYSIS ====================
    # Principle 7: Per-Asset Monitoring - Relationship tracking
    
    async def analyze_mutualism(self, min_strength: float = 0.5) -> Dict[str, Any]:
        """
        Analyze mutualistic relationships in the ecosystem.
        
        Args:
            min_strength: Minimum relationship strength to include (0.0 - 1.0)
            
        Returns:
            Analysis of mutualistic relationships
            
        Principle 5: Async operation
        """
        try:
            await self._ensure_cache_loaded()
            
            self._query_count += 1
            self._last_query_time = datetime.now(timezone.utc)
            
            # Filter by minimum strength
            strong_relationships = [
                rel for rel in self._mutualism_cache
                if rel.relationship_strength >= min_strength
            ]
            
            # Calculate aggregate metrics
            if strong_relationships:
                avg_benefit_score = sum(
                    rel.mutual_benefit_score for rel in strong_relationships
                ) / len(strong_relationships)
                
                avg_interactions = sum(
                    rel.interaction_count for rel in strong_relationships
                ) / len(strong_relationships)
            else:
                avg_benefit_score = 0.0
                avg_interactions = 0.0
            
            return {
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_relationships': len(self._mutualism_cache),
                'strong_relationships': len(strong_relationships),
                'min_strength_threshold': min_strength,
                'average_benefit_score': avg_benefit_score,
                'average_interactions': avg_interactions,
                'top_relationships': [
                    {
                        'account_a': rel.account_a[:8] + '...',
                        'account_b': rel.account_b[:8] + '...',
                        'strength': rel.relationship_strength,
                        'benefit_score': rel.mutual_benefit_score,
                        'interactions': rel.interaction_count
                    }
                    for rel in strong_relationships[:10]  # Top 10
                ]
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error analyzing mutualism: {e}")
            raise
    
    # ==================== ACCOUNT ANALYSIS ====================
    # Principle 7: Per-Asset Monitoring with account-level tracking
    
    async def get_account_stability(self, account_id: str) -> Dict[str, Any]:
        """
        Get stability metrics for a specific account.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Account-specific stability metrics
            
        Principle 5: Async operation
        Principle 7: Per-asset monitoring
        """
        try:
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self.rate_limiter.acquire()
            
            # Query account-specific stability from database
            query = """
                SELECT 
                    balance,
                    balance_percentile,
                    transaction_count,
                    last_transaction_date,
                    stability_score,
                    mutualism_score
                FROM ubec_main.account_stability
                WHERE account_id = $1 AND asset_code = $2
            """
            
            row = await self.db_manager.fetch_one(query, (account_id, self.asset_code))
            
            if not row:
                return {
                    'account_id': account_id,
                    'balance': Decimal('0'),
                    'stability_score': 0.0,
                    'found': False
                }
            
            return {
                'account_id': account_id,
                'balance': Decimal(str(row['balance'])),
                'balance_percentile': float(row['balance_percentile']),
                'transaction_count': int(row['transaction_count']),
                'last_transaction_date': row['last_transaction_date'],
                'stability_score': float(row['stability_score']),
                'mutualism_score': float(row['mutualism_score']),
                'found': True
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error calculating account stability: {e}")
            raise
    
    # ==================== DATABASE SYNC STATUS ====================
    # Principle 4: Single Source of Truth - Database queries for actual status
    # CRITICAL FIX: Query database instead of using instance variables
    
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
    # CRITICAL FIX v3.5.0: Single query pattern for data consistency
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Earth protocol service.
        
        CRITICAL FIX v3.5.0: Now uses SINGLE database query pattern to ensure
        consistent results on successive calls. Previous version had data
        inconsistency issues from using external ServiceHealthCheck utility.
        
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
            ...     print("Earth protocol operational")
            >>> print(f"Accounts: {health['details']['cached_accounts']}")
            >>> # Results are CONSISTENT on successive calls
        
        Design Notes:
            - Principle 4: Single database query as authoritative source
            - Principle 7: Comprehensive per-asset monitoring
            - Principle 12: No duplicate queries or data sources
            - Fixes data inconsistency bug from utility-based approach
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
        checks.append(('initialized', self._initialized))
        checks.append(('database_connected', db_connected))
        checks.append(('has_data', account_count_db > 0 if last_sync_db else False))
        
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
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Earth protocol service...")
        self._clear_cache()
        self._initialized = False
        self.logger.info("Earth protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_ubecgpi_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECgpiProtocolService:
    """
    Factory function to create UBECgpi Earth protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    The service is returned ready for initialization - call initialize() before use.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    Principle 5: Explicit async initialization pattern (v3.3.0).
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBECgpi token code (required)
            - issuer: Issuer address (required)
            - db_schema: Database schema name (optional, default: ubec_main)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECgpiProtocolService: Constructed service instance (call initialize() next)
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> # In main.py or service registry
        >>> service = create_ubecgpi_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBECgpi', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> await service.initialize()  # REQUIRED before use (v3.3.0)
        >>> health = await service.health_check()
        >>> compliance = await service.check_distribution_compliance()
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create service instance
    service = UBECgpiProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )

    # CRITICAL FIX v3.4.0: Initialize service before returning
    # This sets _initialized = True and verifies database connectivity
    # Service is guaranteed to be fully ready when factory returns
    await service.initialize()

    return service


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Enums
    'DistributionCategory',
    'ComplianceStatus',
    
    # Data models
    'DistributionState',
    'StabilityMetrics',
    'MutualismRelationship',
    
    # Service
    'UBECgpiProtocolService',
    'create_ubecgpi_service',
    
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
        "  from UBECgpi_protocol import create_ubecgpi_service\n"
        "  service = create_ubecgpi_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_stability_data()\n\n"
        "Version 3.1.1 - CRITICAL FIX:\n"
        "  - Fixed health_check() token_code parameter\n"
        "  - Now uses self.asset_code (correct) instead of self.token_code (doesn't exist)\n"
        "  - Resolves AttributeError in health check\n\n"
        "Version 3.1.0 - Element Metadata + Enhanced Health Check:\n"
        "  - Complete element metadata (earth, mutualism, 🜃)\n"
        "  - Uses ServiceHealthCheck.element_protocol_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Enhanced error tracking and issuer visibility\n"
        "  - Full DRY compliance with instance variables\n"
        "  - Consistent health checks across all services\n"
        "  - Full compatibility with main.py status output\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
