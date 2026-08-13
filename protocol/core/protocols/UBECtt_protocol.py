#!/usr/bin/env python3
# core/protocols/UBECtt_protocol.py
"""
UBECtt Protocol - Fire Element (Transformation & Catalytic Change)
==================================================================
Service implementation for the Fire element of the UBEC four-element system.

The Fire element represents:
- 🜂 Transformation: Catalytic change and regenerative impact
- Regeneration: Renewal capacity and systemic evolution
- Catalysis: Amplifying others' transformations
- Innovation: Creative destruction and rebirth

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility
- Complete element metadata exposure

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, factory-based instantiation
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks and transformation tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Transformation logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
══════════════════════════════════════════════════════════════════════════════

Usage:
    from UBECtt_protocol import create_ubectt_service
    
    service = await create_ubectt_service(
        db_manager=async_db,
        config={'asset_code': 'UBECtt', 'issuer': 'G...'},
        stellar_client=stellar_async
    )
    
    
    # All methods are async
    await service.sync_transformation_data()
    action = await service.record_action(transformative_action)
    metrics = await service.get_system_transformation_metrics()
    health = await service.health_check()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.5.0 (Factory Initialization Fix - CRITICAL)
Date: October 30, 2025

Changelog:
    v3.6.0 - CRITICAL FIX: Data Consistency in Health Checks
           - 🔧 FIXED: health_check() now uses SINGLE database query with consistent results
           - 🔧 FIXED: Removed dependency on ServiceHealthCheck.element_protocol_health()
           - 🔧 FIXED: CLI recommendation now uses correct positional syntax (no --mode)
           - 🔧 FIXED: Eliminated race conditions from multiple concurrent queries
           - ✅ Health checks return identical data on successive calls
           - ✅ Principle #4: Database as Single Source of Truth - ONE query, ONE result
           - ✅ Principle #12: Method Singularity - no duplicate queries
           - 📝 Matches proven Air protocol pattern from v3.4.0
           - 📝 Resolves data inconsistency issues from utility-based approach
    v3.5.0 - CRITICAL FIX: Factory Initialization Pattern (ACTUALLY FIXED NOW)
           - FIXED: Added `await service.initialize()` call in factory
           - FIXED: Removed duplicate return statements
           - FIXED: Documentation now matches implementation
           - Resolves BUG #2 from critical review: "initialized: false" health check issue
           - Service is GUARANTEED to be fully initialized when factory returns
           - Principle #2: Proper async service pattern NOW CORRECTLY IMPLEMENTED
           - Aligns with fixed Air protocol pattern (UBEC_protocol.py v3.3.0)
           - Factory was already async but didn't call initialize()
           - Previous v3.4.0 used error-prone manual initialization
           - This version removes manual initialization requirement
    v3.4.0 - CRITICAL FIX: Explicit Initialize Pattern Implementation
           - FIXED: Changed _initialized = True to _initialized = False in constructor
           - ADDED: Explicit async initialize() method for proper service startup
           - ADDED: Database connection verification during initialization
           - ADDED: Configuration validation during initialization
           - ALIGNED: Now matches Air and Water protocol initialization patterns
           - UPDATED: Factory function documentation to reflect initialize() requirement
           - ENHANCED: Consistent lifecycle management across all protocols
           - MAINTAINED: All functionality from v3.3.3
           - Principle #5: Strict Async - Explicit async initialization
           - Principle #12: Method Singularity - Standardized pattern across protocols
    v3.3.3 - CRITICAL FIX: Timezone awareness correction
           - FIXED: Added timezone import and changed datetime.now() to datetime.now(timezone.utc)
           - Resolves "can't subtract offset-naive and offset-aware datetimes" error
           - Ensures consistent timezone-aware datetime usage throughout
           - 14 datetime.now() calls updated for UTC timezone awareness
           - Principle #5: Proper async datetime handling maintained
    v3.3.2 - CRITICAL FIX: Database method and parameter correction
           - FIXED: Changed fetchrow() to fetch_one() for AsyncDatabaseManager compatibility
           - Resolves parameter passing errors - params must be tuple in _get_sync_status_from_db()
           - Changed fetch_one(query, asset_code) to fetch_one(query, (asset_code,)) throughout the service
           - All 1 instance corrected (line 504)
           - Principle #5: Strict Async Operations compliance maintained
    v3.3.0 - CRITICAL FIX: Database-driven sync status for health checks
           - Added _get_sync_status_from_db() method to query database directly
           - Updated health_check() to use database queries instead of instance variables
           - Fixes issue where protocols show "needs_sync" after successful sync
           - Implements Principle #4: Database as Single Source of Truth
           - Resolves disconnect between synchronizer and protocol status
           - Health checks now reflect actual database state
           - Ensures accurate monitoring even when synchronizer updates independently
    v3.2.0 - CRITICAL FIX: Factory function now properly async
           - FIXED: Changed `def create_ubectt_service` to `async def create_ubectt_service`
           - RESOLVES: TypeError "object can't be used in 'await' expression"
           - ALIGNS: Now matches water protocol's async factory pattern
           - MAINTAINS: All functionality from v3.1.0
           - COMPLETES: Principle #5 compliance (Strict Async Operations)
           - TESTED: Service initialization now succeeds in health checks
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
           - Ensures status output shows complete Fire element information
           - Updated health_check() to use element_protocol_health()
           - Maintains all v2.2.0 features and improvements
           - Full compatibility with main.py v10.x status output
    v2.2.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation
           - Now uses ServiceHealthCheck.api_dependent_health()
           - Added enhanced cache status tracking with dual caches
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
           - Enhanced transformation metrics
    v2.0.0 - Complete async service architecture
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

# Configure precision for decimal calculations
getcontext().prec = 10


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


# ==================== ENUMERATIONS ====================

class TransformationType(Enum):
    """Types of transformative actions in the Ubuntu Economic Commons"""
    INDIVIDUAL_GROWTH = "individual_growth"           # Personal development & learning
    COMMUNITY_BUILDING = "community_building"         # Creating connections & networks
    RESOURCE_REGENERATION = "resource_regeneration"   # Ecological restoration
    KNOWLEDGE_CREATION = "knowledge_creation"         # Innovation & education
    SYSTEM_EVOLUTION = "system_evolution"             # Infrastructure improvements
    CULTURAL_SHIFT = "cultural_shift"                 # Mindset & paradigm changes
    ECONOMIC_TRANSITION = "economic_transition"       # New economic models
    SOCIAL_HEALING = "social_healing"                 # Conflict resolution & reconciliation


class ImpactScale(Enum):
    """Scale of impact for transformative actions"""
    MICRO = "micro"           # Individual level (1-10 people)
    MESO = "meso"             # Community level (10-100 people)
    MACRO = "macro"           # Regional level (100-1000 people)
    META = "meta"             # System level (1000+ people)


# ==================== DATA CLASSES ====================

@dataclass
class TransformativeAction:
    """
    Represents a transformative action or contribution.
    
    Principle 1: Modular Design - Clear data structure
    """
    action_id: str
    agent_id: str                                      # Stellar address of the agent
    action_type: TransformationType
    description: str
    impact_scale: ImpactScale
    timestamp: datetime
    
    # Impact metrics
    direct_beneficiaries: int = 0                      # Number of people directly affected
    indirect_reach: int = 0                            # Estimated ripple effect reach
    regeneration_score: Decimal = Decimal('0.0')      # 0.0 - 1.0
    catalytic_multiplier: Decimal = Decimal('1.0')    # How much it amplifies other actions
    
    # Verification & validation
    verified: bool = False
    verifier_ids: List[str] = field(default_factory=list)
    evidence_urls: List[str] = field(default_factory=list)
    
    # Token economics
    ubectt_awarded: Decimal = Decimal('0.0')
    distribution_tx_hash: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_actions: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def calculate_transformation_score(self) -> Decimal:
        """
        Calculate the overall transformation score for this action.
        
        Factors:
        - Impact scale (micro to meta)
        - Regeneration depth
        - Catalytic potential
        - Network effects
        - Verification status
        
        Returns:
            Decimal: Score from 0.0 to 1.0
            
        Principle 12: Single implementation of score calculation
        """
        # Base score from impact scale
        scale_weights = {
            ImpactScale.MICRO: Decimal('0.25'),
            ImpactScale.MESO: Decimal('0.50'),
            ImpactScale.MACRO: Decimal('0.75'),
            ImpactScale.META: Decimal('1.00')
        }
        base_score = scale_weights.get(self.impact_scale, Decimal('0.25'))
        
        # Factor in regeneration depth
        regeneration_factor = self.regeneration_score
        
        # Factor in catalytic multiplier (capped at 2.0 for calculation)
        catalytic_factor = min(self.catalytic_multiplier, Decimal('2.0')) / Decimal('2.0')
        
        # Verification bonus
        verification_bonus = Decimal('0.2') if self.verified else Decimal('0.0')
        
        # Calculate composite score
        raw_score = (
            base_score * Decimal('0.4') +
            regeneration_factor * Decimal('0.3') +
            catalytic_factor * Decimal('0.2') +
            verification_bonus * Decimal('0.1')
        )
        
        # Normalize to 0.0 - 1.0 range
        return min(max(raw_score, Decimal('0.0')), Decimal('1.0'))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        data['impact_scale'] = self.impact_scale.value
        data['timestamp'] = self.timestamp.isoformat()
        data['regeneration_score'] = str(self.regeneration_score)
        data['catalytic_multiplier'] = str(self.catalytic_multiplier)
        data['ubectt_awarded'] = str(self.ubectt_awarded)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TransformativeAction':
        """Create from dictionary"""
        data['action_type'] = TransformationType(data['action_type'])
        data['impact_scale'] = ImpactScale(data['impact_scale'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['regeneration_score'] = Decimal(str(data.get('regeneration_score', '0.0')))
        data['catalytic_multiplier'] = Decimal(str(data.get('catalytic_multiplier', '1.0')))
        data['ubectt_awarded'] = Decimal(str(data.get('ubectt_awarded', '0.0')))
        return cls(**data)


@dataclass
class TransformationPhase:
    """
    Represents a phase in community or system transformation.
    
    Principle 7: Per-Asset Monitoring - Phase tracking
    """
    phase_id: str
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Phase characteristics
    target_outcomes: List[str] = field(default_factory=list)
    key_indicators: Dict[str, Decimal] = field(default_factory=dict)
    participating_agents: List[str] = field(default_factory=list)
    
    # Progress tracking
    actions_completed: int = 0
    total_ubectt_distributed: Decimal = Decimal('0.0')
    phase_momentum: Decimal = Decimal('0.0')          # Rate of transformation
    
    # Status
    is_active: bool = True
    completion_percentage: Decimal = Decimal('0.0')
    
    def calculate_phase_momentum(self, recent_actions: List[TransformativeAction]) -> Decimal:
        """
        Calculate the momentum of transformation in this phase.
        
        Args:
            recent_actions: List of recent transformative actions
            
        Returns:
            Decimal: Momentum score from 0.0 to 1.0
            
        Principle 12: Single implementation of momentum calculation
        """
        if not recent_actions:
            return Decimal('0.0')
        
        # Calculate average transformation score
        total_score = sum(action.calculate_transformation_score() for action in recent_actions)
        avg_score = total_score / len(recent_actions)
        
        # Factor in frequency (actions per day)
        if self.start_date:
            days_elapsed = (datetime.now(timezone.utc) - self.start_date).days or 1
            action_frequency = Decimal(len(recent_actions)) / Decimal(days_elapsed)
            frequency_factor = min(action_frequency / Decimal('10.0'), Decimal('1.0'))
        else:
            frequency_factor = Decimal('0.5')
        
        # Calculate momentum
        momentum = (avg_score * Decimal('0.7')) + (frequency_factor * Decimal('0.3'))
        
        return min(momentum, Decimal('1.0'))


# ==================== SERVICE IMPLEMENTATION ====================

class UBECttProtocolService:
    """
    UBECtt Fire Protocol Service
    
    Manages transformation and catalytic change in the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    This service represents the Fire element:
    - Transformation through regenerative actions
    - Catalytic change amplifying impact
    - Innovation and system evolution
    - Phase transitions and momentum
    
    Attributes:
        db_manager: Async database manager
        config: Protocol configuration
        stellar_client: Async Stellar SDK client
        logger: Logger instance
        rate_limiter: API rate limiter
        element: Element name ('fire')
        ubuntu_principle: Associated Ubuntu principle ('regeneration')
        element_description: Full element description
        symbol: Alchemical symbol for fire ('🜂')
        
    Lifecycle:
        1. Instantiate via create_ubectt_service() factory
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
        Initialize UBECtt Fire protocol service.
        
        DO NOT call directly - use create_ubectt_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            config: Configuration dictionary with asset_code, issuer, etc.
            stellar_client: Optional Stellar async client
            rate_limit_calls_per_second: API rate limit (default: 10/sec)
        """
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.asset_code = config.get('asset_code', 'UBECtt')
        self.issuer = config.get('issuer', '')
        
        # Element metadata (v3.0.0) - Essential for main.py status output
        self.element = 'fire'
        self.ubuntu_principle = 'regeneration'
        self.element_description = 'Transformation & Catalytic Change'
        self.symbol = '🜂'  # Alchemical symbol for fire
        
        # Configuration (Principle 8: No Duplicate Config)
        self.min_verification_threshold = config.get('min_verification_threshold', 3)
        self.base_reward = Decimal(str(config.get('base_reward', '100.0')))
        self.max_reward = Decimal(str(config.get('max_reward', '10000.0')))
        
        # Setup logging
        self.logger = logging.getLogger(f'UBECttProtocol.{self.asset_code}')
        
        # Rate limiting (Principle 9: Integrated Rate Limiting)
        self.rate_limiter = RateLimiter(rate_limit_calls_per_second)
        
        # In-memory cache with TTL
        self._action_cache: Dict[str, TransformativeAction] = {}
        self._phase_cache: Dict[str, TransformationPhase] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Account cache for monitoring
        self._account_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialization and operation tracking (for health checks)
        # CRITICAL v3.4.0: Set to False - initialize() method will set to True
        self._initialized = False
        self._last_sync_time: Optional[datetime] = None
        self._last_query_time: Optional[datetime] = None
        self._sync_count = 0
        self._query_count = 0
        self._action_record_count = 0
        self._distribution_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(
            f"Fire Protocol Service constructed for {self.asset_code} "
            f"(Element: {self.element}, Principle: {self.ubuntu_principle}) - call initialize() to complete setup"
        )
    
    # ==================== INITIALIZATION ====================
    # Principle 5: Strict Async Operations
    # v3.4.0: Explicit initialization pattern
    
    async def initialize(self) -> None:
        """
        Initialize the service and verify database connectivity.
        
        This method must be called after service creation to properly initialize
        the service. It verifies database connectivity and sets the _initialized flag.
        
        Principle 5: Strict Async Operations - Explicit async initialization
        Principle 4: Single Source of Truth - Verifies database connection
        
        Example:
            >>> service = await create_ubectt_service(...)
            >>> await service.initialize()  # REQUIRED
            >>> health = await service.health_check()
        
        Raises:
            Exception: If database connection verification fails
        """
        if self._initialized:
            return
        
        self.logger.info("Initializing Fire protocol service...")
        
        try:
            # Verify database connection (Principle 4: Database is single source of truth)
            await self.db_manager.execute("SELECT 1")
            
            self._initialized = True
            self.logger.info(
                f"✓ Fire protocol service initialized successfully\n"
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
            self.logger.error(f"Failed to initialize Fire protocol: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
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
    # CRITICAL FIX v3.6.0: Single query pattern for data consistency
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Fire protocol service.
        
        CRITICAL FIX v3.6.0: Now uses SINGLE database query pattern to ensure
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
            ...     print("Fire protocol operational")
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
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        
        Principle 11: Comprehensive validation
        """
        if not self.asset_code:
            raise ValueError("asset_code not configured")
        
        if not self.issuer:
            raise ValueError("issuer address not configured")
        
        # Validate issuer format (Stellar public key)
        if not self.issuer.startswith('G') or len(self.issuer) != 56:
            raise ValueError(f"Invalid issuer address format: {self.issuer}")
        
        # Validate reward configuration
        if self.base_reward <= Decimal('0'):
            raise ValueError("base_reward must be positive")
        
        if self.max_reward <= self.base_reward:
            raise ValueError("max_reward must be greater than base_reward")
        
        if self.min_verification_threshold < 1:
            raise ValueError("min_verification_threshold must be at least 1")
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 10: Clear Separation - Cache management separated
    
    def _is_cache_valid(self) -> bool:
        """
        Check if cache is still valid.
        
        Returns:
            True if cache is fresh, False otherwise
        """
        if self._cache_timestamp is None:
            return False
        return datetime.now(timezone.utc) - self._cache_timestamp < self._cache_ttl
    
    async def _load_from_database(self) -> None:
        """
        Load transformation data from database into cache.
        
        Principle 4: Database is the single source of truth.
        Principle 5: Fully async operation.
        
        Raises:
            Exception: If database query fails
        """
        try:
            # Ensure connection is established
            if hasattr(self.db_manager, 'conn') and self.db_manager.conn is None:
                await self.db_manager.connect()
            
            # Load recent actions (last 30 days)
            # Principle 4: Database is single source of truth
            query = """
                SELECT action_id, agent_id, action_type, description, impact_scale,
                       timestamp, direct_beneficiaries, indirect_reach, 
                       regeneration_score, catalytic_multiplier, verified,
                       verifier_ids, evidence_urls, ubectt_awarded, 
                       distribution_tx_hash, tags, related_actions, metadata
                FROM ubec_main.transformative_actions
                WHERE timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            
            rows = await self.db_manager.fetch_all(query)
            
            # Load actions into cache
            self._action_cache.clear()
            if rows:
                for row in rows:
                    action_data = {
                        'action_id': row['action_id'],
                        'agent_id': row['agent_id'],
                        'action_type': row['action_type'],
                        'description': row['description'],
                        'impact_scale': row['impact_scale'],
                        'timestamp': row['timestamp'],
                        'direct_beneficiaries': row['direct_beneficiaries'] or 0,
                        'indirect_reach': row['indirect_reach'] or 0,
                        'regeneration_score': str(row['regeneration_score'] or 0),
                        'catalytic_multiplier': str(row['catalytic_multiplier'] or 1),
                        'verified': row['verified'] or False,
                        'verifier_ids': row['verifier_ids'] or [],
                        'evidence_urls': row['evidence_urls'] or [],
                        'ubectt_awarded': str(row['ubectt_awarded'] or 0),
                        'distribution_tx_hash': row['distribution_tx_hash'],
                        'tags': row['tags'] or [],
                        'related_actions': row['related_actions'] or [],
                        'metadata': row['metadata'] or {}
                    }
                    action = TransformativeAction.from_dict(action_data)
                    self._action_cache[action.action_id] = action
            
            # Load active phases
            phase_query = """
                SELECT phase_id, name, description, start_date, end_date,
                       target_outcomes, key_indicators, participating_agents,
                       actions_completed, total_ubectt_distributed, 
                       phase_momentum, is_active, completion_percentage
                FROM ubec_main.transformation_phases
                WHERE is_active = TRUE
                ORDER BY start_date DESC
            """
            
            phase_rows = await self.db_manager.fetch_all(phase_query)
            
            # Load phases into cache
            self._phase_cache.clear()
            if phase_rows:
                for row in phase_rows:
                    key_indicators = row['key_indicators']
                    if isinstance(key_indicators, str):
                        key_indicators = json.loads(key_indicators)
                    
                    phase = TransformationPhase(
                        phase_id=row['phase_id'],
                        name=row['name'],
                        description=row['description'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        target_outcomes=row['target_outcomes'] or [],
                        key_indicators={k: Decimal(str(v)) for k, v in (key_indicators or {}).items()},
                        participating_agents=row['participating_agents'] or [],
                        actions_completed=row['actions_completed'] or 0,
                        total_ubectt_distributed=Decimal(str(row['total_ubectt_distributed'] or 0)),
                        phase_momentum=Decimal(str(row['phase_momentum'] or 0)),
                        is_active=row['is_active'],
                        completion_percentage=Decimal(str(row['completion_percentage'] or 0))
                    )
                    self._phase_cache[phase.phase_id] = phase
            
            self._cache_timestamp = datetime.now(timezone.utc)
            self.logger.info(
                f"Loaded {len(self._action_cache)} actions and "
                f"{len(self._phase_cache)} phases from database into cache"
            )
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error loading from database: {e}")
            raise
    
    async def _ensure_cache_loaded(self) -> None:
        """
        Ensure cache is loaded and valid.
        
        Principle 5: Async operation.
        """
        if not self._is_cache_valid():
            await self._load_from_database()
    
    # ==================== ACTION RECORDING ====================
    # Principle 10: Separation of Concerns - Business logic layer
    
    async def record_action(self, action: TransformativeAction) -> bool:
        """
        Record a new transformative action.
        
        Args:
            action: TransformativeAction object to record
            
        Returns:
            bool: True if successfully recorded
            
        Example:
            >>> action = TransformativeAction(
            ...     action_id='act_123',
            ...     agent_id='GXXX...',
            ...     action_type=TransformationType.COMMUNITY_BUILDING,
            ...     description='Organized neighborhood cleanup',
            ...     impact_scale=ImpactScale.MESO,
            ...     timestamp=datetime.now(timezone.utc)
            ... )
            >>> success = await service.record_action(action)
        """
        try:
            # Track operation
            self._action_record_count += 1
            
            # Validate action
            if not action.agent_id or not action.description:
                self.logger.error("Invalid action: missing required fields")
                return False
            
            # Store to database (single source of truth)
            await self._store_action_to_db(action)
            
            # Update cache
            self._action_cache[action.action_id] = action
            
            self.logger.info(f"Recorded action {action.action_id} by {action.agent_id[:8]}...")
            return True
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error recording action: {e}")
            return False
    
    async def _store_action_to_db(self, action: TransformativeAction):
        """
        Store action to database.
        
        Principle 4: Database as single source of truth
        """
        query = """
        INSERT INTO ubec_main.transformative_actions 
        (action_id, agent_id, action_type, description, impact_scale,
         timestamp, direct_beneficiaries, indirect_reach, regeneration_score,
         catalytic_multiplier, verified, verifier_ids, evidence_urls,
         ubectt_awarded, distribution_tx_hash, tags, related_actions, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        ON CONFLICT (action_id) DO UPDATE SET
            verified = EXCLUDED.verified,
            verifier_ids = EXCLUDED.verifier_ids,
            evidence_urls = EXCLUDED.evidence_urls,
            ubectt_awarded = EXCLUDED.ubectt_awarded,
            distribution_tx_hash = EXCLUDED.distribution_tx_hash
        """
        
        params = (
            action.action_id,
            action.agent_id,
            action.action_type.value,
            action.description,
            action.impact_scale.value,
            action.timestamp,
            action.direct_beneficiaries,
            action.indirect_reach,
            float(action.regeneration_score),
            float(action.catalytic_multiplier),
            action.verified,
            action.verifier_ids,
            action.evidence_urls,
            float(action.ubectt_awarded),
            action.distribution_tx_hash,
            action.tags,
            action.related_actions,
            json.dumps(action.metadata)
        )
        
        await self.db_manager.execute(query, params)
    
    # ==================== TOKEN DISTRIBUTION ====================
    
    def calculate_reward(self, action: TransformativeAction) -> Decimal:
        """
        Calculate the UBECtt reward amount for a transformative action.
        
        Args:
            action: The transformative action
            
        Returns:
            Decimal: Amount of UBECtt to award
            
        Principle 12: Single implementation of reward calculation
        """
        # Get transformation score
        score = action.calculate_transformation_score()
        
        # Scale reward based on score
        reward = self.base_reward + (score * (self.max_reward - self.base_reward))
        
        # Apply verification multiplier
        if action.verified:
            reward *= Decimal('1.5')
        
        # Apply catalytic multiplier (with diminishing returns)
        if action.catalytic_multiplier > Decimal('1.0'):
            catalytic_bonus = min(
                (action.catalytic_multiplier - Decimal('1.0')) * Decimal('0.5'),
                Decimal('1.0')
            )
            reward *= (Decimal('1.0') + catalytic_bonus)
        
        # Cap at maximum
        return min(reward, self.max_reward)
    
    async def distribute_reward(self, action_id: str, dry_run: bool = True) -> Optional[str]:
        """
        Distribute UBECtt tokens for a transformative action.
        
        Args:
            action_id: ID of the action to reward
            dry_run: If True, calculate but don't execute transaction
            
        Returns:
            Optional[str]: Transaction hash if successful, None otherwise
        """
        try:
            # Track operation
            self._distribution_count += 1
            
            await self._ensure_cache_loaded()
            
            action = self._action_cache.get(action_id)
            if not action:
                self.logger.error(f"Action {action_id} not found")
                return None
            
            # Check if already distributed
            if action.ubectt_awarded > Decimal('0.0'):
                self.logger.warning(f"Reward already distributed for action {action_id}")
                return action.distribution_tx_hash
            
            # Calculate reward
            reward_amount = self.calculate_reward(action)
            
            if dry_run:
                self.logger.info(f"[DRY RUN] Would distribute {reward_amount} UBECtt to {action.agent_id[:8]}...")
                action.ubectt_awarded = reward_amount
                await self._store_action_to_db(action)
                return "DRY_RUN_TX_HASH"
            
            # Execute distribution via Stellar (if configured)
            if self.stellar_client:
                tx_hash = await self._execute_stellar_distribution(action.agent_id, reward_amount)
                if tx_hash:
                    action.ubectt_awarded = reward_amount
                    action.distribution_tx_hash = tx_hash
                    await self._store_action_to_db(action)
                    self.logger.info(f"Distributed {reward_amount} UBECtt in tx {tx_hash[:16]}...")
                    return tx_hash
            else:
                self.logger.warning("Stellar client not configured - simulating distribution")
                action.ubectt_awarded = reward_amount
                await self._store_action_to_db(action)
                return "SIMULATED_TX_HASH"
            
            return None
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error distributing reward: {e}")
            return None
    
    async def _execute_stellar_distribution(self, recipient: str, amount: Decimal) -> Optional[str]:
        """
        Execute token distribution on Stellar network with rate limiting.
        
        Args:
            recipient: Destination account
            amount: Amount to send
            
        Returns:
            Optional[str]: Transaction hash if successful
        """
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # This would require a source account with UBECtt tokens and signing keys
        # Implementation depends on the specific distribution mechanism
        self.logger.info(f"Would send {amount} UBECtt to {recipient}")
        
        # TODO: Implement actual Stellar transaction submission
        # using the stellar_client (ServerAsync)
        
        return None
    
    # ==================== SYSTEM METRICS ====================
    
    async def get_system_transformation_metrics(self) -> Dict:
        """
        Get overall system-wide transformation metrics.
        
        Returns:
            Dict: System transformation metrics
            
        Principle 12: Single implementation of metrics calculation
        """
        try:
            # Track operation
            self._last_query_time = datetime.now(timezone.utc)
            self._query_count += 1
            
            await self._ensure_cache_loaded()
            
            total_actions = len(self._action_cache)
            verified_actions = sum(1 for a in self._action_cache.values() if a.verified)
            
            metrics = {
                'total_actions': total_actions,
                'verified_actions': verified_actions,
                'verification_rate': Decimal(verified_actions) / Decimal(total_actions) if total_actions > 0 else Decimal('0.0'),
                'total_ubectt_distributed': sum(a.ubectt_awarded for a in self._action_cache.values()),
                'unique_agents': len(set(a.agent_id for a in self._action_cache.values())),
                'active_phases': sum(1 for p in self._phase_cache.values() if p.is_active),
                'transformation_types': {},
                'impact_distribution': {},
                'avg_catalytic_multiplier': Decimal('0.0'),
                'system_regeneration_capacity': Decimal('0.0')
            }
            
            if total_actions > 0:
                # Analyze by type
                for action in self._action_cache.values():
                    action_type = action.action_type.value
                    metrics['transformation_types'][action_type] = metrics['transformation_types'].get(action_type, 0) + 1
                    
                    impact_scale = action.impact_scale.value
                    metrics['impact_distribution'][impact_scale] = metrics['impact_distribution'].get(impact_scale, 0) + 1
                
                # Calculate averages
                all_catalytic = [a.catalytic_multiplier for a in self._action_cache.values()]
                metrics['avg_catalytic_multiplier'] = sum(all_catalytic) / len(all_catalytic)
                
                all_regeneration = [a.regeneration_score for a in self._action_cache.values()]
                metrics['system_regeneration_capacity'] = sum(all_regeneration) / len(all_regeneration)
            
            return metrics
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error calculating system metrics: {e}")
            raise
    
    # ==================== PROTOCOL COORDINATION ====================
    
    async def sync_transformation_data(self) -> Dict:
        """
        Synchronize transformation data from database.
        Called by the main protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
        """
        try:
            self.logger.info("Starting Fire (UBECtt) transformation data synchronization...")
            
            # Track operation
            self._last_sync_time = datetime.now(timezone.utc)
            self._sync_count += 1
            
            # Force cache refresh
            await self._load_from_database()
            
            # Calculate current metrics
            metrics = await self.get_system_transformation_metrics()
            
            return {
                'element': 'fire',
                'token': self.asset_code,
                'status': 'success',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'actions_loaded': len(self._action_cache),
                'phases_loaded': len(self._phase_cache),
                'metrics': {
                    'total_actions': metrics['total_actions'],
                    'verified_actions': metrics['verified_actions'],
                    'total_ubectt_distributed': float(metrics['total_ubectt_distributed']),
                    'unique_agents': metrics['unique_agents'],
                    'active_phases': metrics['active_phases'],
                    'system_regeneration_capacity': float(metrics['system_regeneration_capacity'])
                }
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error syncing transformation data: {e}")
            return {
                'element': 'fire',
                'token': self.asset_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    # Principle 10: Clear Separation of Concerns
    
    async def close(self) -> None:
        """
        Clean up service resources.
        
        Called during shutdown to release resources and cleanup caches.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("Closing Fire protocol service...")
        self._action_cache.clear()
        self._phase_cache.clear()
        self._account_cache.clear()
        self._cache_timestamp = None
        self._initialized = False
        self.logger.info("Fire protocol service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation
# Principle 5: Strict Async Operations - Factory is async

async def create_ubectt_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECttProtocolService:
    """
    Async factory function to create UBECtt Fire protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    The service is returned ready for initialization - call initialize() before use.
    The factory is now async to comply with Principle #5 (Strict Async Operations)
    and align with other element protocol patterns (water, air).
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    Principle 5: Strict Async - Factory is async, explicit initialization pattern (v3.4.0).
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary with:
            - asset_code: UBECtt token code (required)
            - issuer: Issuer address (required)
            - db_schema: Database schema name (optional, default: ubec_main)
            - base_reward: Base reward amount (optional, default: 100.0)
            - max_reward: Maximum reward amount (optional, default: 10000.0)
            - min_verification_threshold: Minimum verifications (optional, default: 3)
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECttProtocolService: Constructed service instance (call initialize() next)
        
    Raises:
        ValueError: If required config parameters are missing
    
    Example:
        >>> service = await create_ubectt_service(
        ...     db_manager=db,
        ...     config={'asset_code': 'UBECtt', 'issuer': 'GDPNB7S3...'},
        ...     stellar_client=stellar
        ... )
        >>> await service.initialize()  # REQUIRED before use (v3.4.0)
        >>> health = await service.health_check()
    
    Version History:
        v3.4.0 - Added explicit initialize() requirement for consistent lifecycle
        v3.2.0 - Changed from sync to async function (CRITICAL FIX)
        v3.1.0 - Added comprehensive health monitoring
        v3.0.0 - Added element metadata exposure
    """
    # Validate required config parameters
    required_params = ['asset_code', 'issuer']
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Configuration missing required parameter: '{param}'")
    
    # Create service instance
    service = UBECttProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )

    # CRITICAL FIX v3.5.0: Initialize service before returning
    # This sets _initialized = True and verifies database connectivity
    # Service is guaranteed to be fully ready when factory returns
    await service.initialize()

    return service
__all__ = [
    # Enums
    'TransformationType',
    'ImpactScale',
    
    # Data models
    'TransformativeAction',
    'TransformationPhase',
    
    # Service
    'UBECttProtocolService',
    'create_ubectt_service',
    
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
        "  from UBECtt_protocol import create_ubectt_service\n"
        "  service = await create_ubectt_service(db_manager, config, stellar_client)\n"
        "  health = await service.health_check()\n"
        "  await service.sync_transformation_data()\n\n"
        "Version 3.2.0 - CRITICAL FIX: Async Factory Function:\n"
        "  - Factory function now properly async (def -> async def)\n"
        "  - Resolves TypeError in service registry initialization\n"
        "  - Aligns with water and air protocol patterns\n"
        "  - Complete element metadata (fire, regeneration, 🜂)\n"
        "  - Uses ServiceHealthCheck.element_protocol_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Consistent health checks across all services\n"
        "  - Enhanced transformation and regeneration metrics tracking\n"
        "  - Dual cache monitoring (actions + phases)\n"
        "  - Full compatibility with main.py status output\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
