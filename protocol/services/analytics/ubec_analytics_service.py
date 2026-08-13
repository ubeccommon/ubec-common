#!/usr/bin/env python3
"""
UBEC Protocol Suite - Analytics Service
========================================
Comprehensive analytics and insights for the UBEC token ecosystem.

Analyzes distribution, holder patterns, transaction trends, and ecosystem health
across all four UBEC elements (Air, Water, Earth, Fire).

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained analytics service with defined boundaries
    ✅ #2  Service Pattern: No standalone execution, used as service only
    ✅ #3  Service Registry: Accessed through service registry pattern
    ✅ #4  Single Source of Truth: All data from database
    ✅ #5  Strict Async Operations: All I/O uses async/await
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Individual token/element tracking with health checks
    ✅ #8  No Duplicate Configuration: No config duplication
    ✅ #9  Integrated Rate Limiting: N/A (read-only database operations)
    ✅ #10 Separation of Concerns: Analytics separated from sync/trading
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Each analysis method implemented once
════════════════════════════════════════════════════════════════════════════

Key Features:
- Token distribution analysis across all 4 elements
- Holder concentration and whale identification
- Transaction pattern analysis and velocity metrics
- Liquidity and supply metrics
- Ecosystem health monitoring
- Time-series trend analysis
- Comparative analytics across tokens
- Export capabilities for external reporting
- Scheduled analytics updates for automation

Four-Element Architecture:
- 🜁 Air (UBEC) - Gateway & Universal Access
- 🜄 Water (UBECrc) - Flow & Exchange
- 🜃 Earth (UBECgpi) - Stability & Value
- 🜂 Fire (UBECtt) - Transformation & Action

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 3.8.0 (Remove Deprecated account_balances References)
Date: November 29, 2025

Changelog v3.8.0:
- 🔥 CRITICAL: Removed deprecated account_balances table references
- ✅ UPDATED: _TableColumns class to mark account_balances as deprecated
- ✅ ADDED: Deprecation warning to get_account_balance_asset_col() method
- ✅ UPDATED: Schema notes to reflect single source of truth (ubec_balances)
- 📝 NOTE: account_balances table is being removed from database
- 📝 NOTE: ubec_balances is synced by blockchain_sync scheduler job
- 📝 NOTE: All balance queries should use ubec_balances exclusively

Previous Changelog v3.7.0:
- 🔥 CRITICAL FIX: Corrected total_accounts query to use stellar_accounts table
- ✅ FIXED: Active accounts can no longer exceed total accounts
- ✅ FIXED: Network activity score now capped at 100 (was 163.5%)
- ✅ ADDED: Data consistency validation and warning logging
- ✅ VERIFIED: Query uses correct table per database schema documentation
- ✅ RESOLVES: asyncpg data integrity issue from analysis_metrics_20251119_120121.log
- ✅ TESTED: Proper account counting across all tables (stellar_accounts: 1,481 rows)
- 📊 CLARIFIED: account_balances uses asset_code, ubec_balances uses token_code

Previous Changelog v3.6.4:
- 🔥 CRITICAL FIX: Corrected column names in active accounts query
- ✅ FIXED: stellar_operations table uses from_account/to_account, not destination
- ✅ VERIFIED: Query now correctly counts senders AND receivers
- ✅ RESOLVES: asyncpg.exceptions.UndefinedColumnError: column "destination" does not exist
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


class TokenCode(str, Enum):
    """Valid UBEC token codes"""
    UBEC = "UBEC"
    UBECRC = "UBECrc"
    UBECGPI = "UBECgpi"
    UBECTT = "UBECtt"


class ElementType(str, Enum):
    """Four-element types"""
    AIR = "air"
    WATER = "water"
    EARTH = "earth"
    FIRE = "fire"


# Element to token mapping
ELEMENT_TOKEN_MAP = {
    ElementType.AIR: TokenCode.UBEC,
    ElementType.WATER: TokenCode.UBECRC,
    ElementType.EARTH: TokenCode.UBECGPI,
    ElementType.FIRE: TokenCode.UBECTT
}

TOKEN_ELEMENT_MAP = {v: k for k, v in ELEMENT_TOKEN_MAP.items()}


# Schema column mapping (Principle #12: Method Singularity)
class _TableColumns:
    """
    Centralized table-to-column mapping for database queries.
    
    This class provides a single source of truth for column names used in
    different tables, implementing Principle #4 (Single Source of Truth) and
    Principle #12 (Method Singularity).
    
    Schema Notes (v3.8.0 - Updated November 29, 2025):
        - ubec_balances: Uses token_code (ENUM: UBEC, UBECrc, UBECgpi, UBECtt) - PRIMARY BALANCE TABLE
        - stellar_accounts: Primary account table - 1,481 rows
        - stellar_operations: Uses source_account, from_account, to_account (NOT destination) - 30,889 rows
        - stellar_transactions: Uses source_account - 98,549 rows
        
    DEPRECATED (v3.8.0):
        - account_balances: REMOVED - was stale and not synced by scheduler
        - Use ubec_balances exclusively for all balance queries
    """
    # Balance table - SINGLE SOURCE OF TRUTH (v3.8.0)
    UBEC_BALANCES_TOKEN_COL = "token_code"      # Token identifier in ubec_balances (ENUM)
    
    # DEPRECATED v3.8.0: account_balances table removed from database
    # Kept for backward compatibility during transition, but raises warning
    ACCOUNT_BALANCES_ASSET_COL = "asset_code"   # DEPRECATED - table removed
    
    # Transaction table
    TRANSACTIONS_ASSET_COL = "asset_code"       # Token identifier in stellar_transactions
    
    # Authorization columns
    AUTHORIZED_COL = "is_authorized"            # Authorization status in ubec_balances
    
    @staticmethod
    def get_balance_token_col() -> str:
        """Get token column name for ubec_balances table."""
        return _TableColumns.UBEC_BALANCES_TOKEN_COL
    
    @staticmethod
    def get_account_balance_asset_col() -> str:
        """
        DEPRECATED v3.8.0: account_balances table has been removed.
        Use get_balance_token_col() with ubec_balances table instead.
        
        This method is kept for backward compatibility during transition
        but will log a deprecation warning.
        
        Returns:
            str: The token_code column name (redirected to ubec_balances)
        """
        import warnings
        warnings.warn(
            "get_account_balance_asset_col() is deprecated. "
            "account_balances table has been removed. "
            "Use get_balance_token_col() with ubec_balances instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Return ubec_balances column for backward compatibility
        return _TableColumns.UBEC_BALANCES_TOKEN_COL
    
    @staticmethod
    def get_transaction_asset_col() -> str:
        """Get asset column name for transaction tables."""
        return _TableColumns.TRANSACTIONS_ASSET_COL
    
    @staticmethod
    def get_authorized_col() -> str:
        """Get authorization column name."""
        return _TableColumns.AUTHORIZED_COL


# ==================== DATA MODELS ====================

@dataclass
class TokenDistribution:
    """Token distribution metrics"""
    token_code: str
    total_supply: Decimal
    total_holders: int
    circulating_supply: Decimal
    concentration_index: float
    top_10_holdings: Decimal
    top_100_holdings: Decimal
    timestamp: str


@dataclass
class HolderAnalysis:
    """Holder concentration analysis"""
    token_code: str
    total_holders: int
    whale_count: int
    whale_percentage: float
    concentration_score: float
    gini_coefficient: float
    timestamp: str


@dataclass
class TransactionMetrics:
    """Transaction velocity and activity metrics"""
    token_code: str
    tx_count_7d: int
    tx_count_30d: int
    tx_count_90d: int
    avg_tx_size: Decimal
    velocity_score: float
    timestamp: str


@dataclass
class LiquidityMetrics:
    """Liquidity and market metrics"""
    token_code: str
    total_liquidity: Decimal
    liquidity_ratio: float
    avg_spread: float
    depth_score: float
    timestamp: str


@dataclass
class EcosystemHealth:
    """Overall ecosystem health metrics"""
    total_accounts: int
    active_accounts: int
    network_activity_score: float
    element_balance_score: float
    timestamp: str


class AnalyticsException(Exception):
    """Analytics service specific exceptions"""
    pass


# ==================== SERVICE CLASS ====================

class UBECAnalyticsService:
    """
    UBEC Analytics Service - Comprehensive ecosystem analytics.
    
    This service provides read-only analytics and insights by querying
    the database. It calculates distribution metrics, holder patterns,
    transaction velocity, and ecosystem health.
    
    The service operates purely in read-only mode and makes NO changes to
    the database, implementing Principle #10 (Separation of Concerns).
    
    Key Capabilities:
    - Token distribution analysis (supply, holders, concentration)
    - Holder concentration analysis (whale detection, Gini coefficient)
    - Transaction velocity and activity metrics
    - Liquidity and market depth analysis
    - Ecosystem health monitoring
    - Comparative analytics across all four tokens
    - Scheduled analytics updates
    
    Design Compliance:
    - ✅ Principle #2: No standalone execution
    - ✅ Principle #3: Accessed via service registry
    - ✅ Principle #4: Database as single source of truth
    - ✅ Principle #5: All operations async
    - ✅ Principle #12: Each analysis method exists once
    
    Schema Usage:
        This service queries the ubec_main schema exclusively.
        All queries use explicit schema names (ubec_main.table_name).
        
    Dependencies:
        - database: AsyncDatabaseManager instance
        - config: Configuration service (optional, for schema name)
    """
    
    def __init__(
        self,
        database,
        config=None,
        cache_ttl: int = 300
    ):
        """
        Initialize analytics service.
        
        Args:
            database: AsyncDatabaseManager instance
            config: Configuration service (optional)
            cache_ttl: Cache time-to-live in seconds (default: 300)
        """
        self._db = database
        self._config = config
        self._cache_ttl = cache_ttl
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._initialized = False
        self._error_count = 0
        self._query_count = 0
        self._last_error = None
        
        # Get schema name from config or use default
        self.db_schema = "ubec_main"
        if config:
            self.db_schema = getattr(config, 'database_schema', 'ubec_main')
        
        logger.info(f"✓ ubec_analytics_service v3.7.0 initialized")
    
    async def initialize(self) -> None:
        """
        Initialize analytics service.
        
        Verifies database connection and required tables exist.
        """
        if self._initialized:
            logger.debug("Analytics service already initialized")
            return
        
        try:
            # Verify database connection
            if not self._db or not hasattr(self._db, 'fetch_one'):
                raise AnalyticsException("Invalid database instance provided")
            
            # Verify schema exists and key tables are accessible
            test_query = f"""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = $1
                AND table_name IN ('stellar_accounts', 'ubec_balances', 'stellar_operations')
            """
            result = await self._db.fetch_one(test_query, (self.db_schema,))
            
            if not result or result['count'] < 3:
                raise AnalyticsException(
                    f"Required tables not found in schema '{self.db_schema}'. "
                    f"Expected 3 tables, found {result['count'] if result else 0}"
                )
            
            self._initialized = True
            logger.info("ubec_analytics_service async initialization complete")
            
        except Exception as e:
            logger.error(f"Analytics service initialization failed: {e}")
            raise AnalyticsException(f"Initialization failed: {e}")
    
    async def close(self) -> None:
        """
        Close analytics service and cleanup resources.
        """
        self._cache.clear()
        self._initialized = False
        logger.info("✓ ubec_analytics_service closed")
    
    # ========================================================================
    # INTERNAL HELPER METHODS
    # ========================================================================
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cached result if still valid."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < self._cache_ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Store result in cache with timestamp."""
        self._cache[key] = (value, datetime.now())
    
    def _record_error(self, error_msg: str) -> None:
        """Record error for health monitoring."""
        self._error_count += 1
        self._last_error = error_msg
        logger.error(error_msg)
    
    async def _execute_query(self, query: str, params: tuple) -> Optional[Dict]:
        """
        Execute query and return single row.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Dict with query results or None
        """
        self._query_count += 1
        try:
            result = await self._db.fetch_one(query, params)
            return dict(result) if result else None
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    async def _execute_query_all(self, query: str, params: tuple) -> List[Dict]:
        """
        Execute query and return all rows.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of dicts with query results
        """
        self._query_count += 1
        try:
            results = await self._db.fetch_all(query, params)
            return [dict(row) for row in results] if results else []
        except Exception as e:
            self._record_error(f"Query execution failed: {e}")
            raise
    
    # ========================================================================
    # HEALTH CHECK (Principle #12: Method Singularity)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health using standardized ServiceHealthCheck utility.
        
        VERIFIED v3.6.2: Uses ServiceHealthCheck.database_dependent_health()
        with proper check functions that return None/dict/Exception (not bool).
        
        Returns:
            Dict with health status:
            {
                'service': 'ubec_analytics_service',
                'status': 'healthy'|'degraded'|'unhealthy',
                'timestamp': ISO timestamp,
                'checks': {...},
                'details': {...}
            }
        """
        
        async def check_database() -> Optional[Dict]:
            """Check database connectivity."""
            try:
                query = f"SELECT 1 FROM {self.db_schema}.stellar_accounts LIMIT 1"
                await self._db.fetch_one(query, ())
                return None  # Success
            except Exception as e:
                return {'error': str(e)}
        
        async def check_data_freshness() -> Optional[Dict]:
            """Check if data is reasonably fresh."""
            try:
                query = f"""
                    SELECT MAX(last_modified_at) as last_update
                    FROM {self.db_schema}.ubec_balances
                """
                result = await self._db.fetch_one(query, ())
                
                if result and result['last_update']:
                    age = datetime.now(timezone.utc) - result['last_update']
                    if age.total_seconds() > 86400:  # 24 hours
                        return {'warning': f'Data is {age.total_seconds()/3600:.1f} hours old'}
                
                return None  # Fresh data
            except Exception as e:
                return {'error': str(e)}
        
        async def check_error_rate() -> Optional[Dict]:
            """Check error rate."""
            if self._query_count > 0:
                error_rate = self._error_count / self._query_count
                if error_rate > 0.1:  # More than 10% errors
                    return {
                        'warning': f'High error rate: {error_rate:.1%}',
                        'error_count': self._error_count,
                        'query_count': self._query_count,
                        'last_error': self._last_error
                    }
            return None  # Error rate acceptable
        
        # Use standardized health check utility (Principle #12)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='ubec_analytics_service',
            version='3.7.0',
            db_manager=self._db,
            check_functions=[
                ('database_connectivity', check_database),
                ('data_freshness', check_data_freshness),
                ('error_rate', check_error_rate)
            ],
            custom_details={
                'schema': self.db_schema,
                'cache_size': len(self._cache),
                'cache_ttl': self._cache_ttl,
                'query_count': self._query_count,
                'error_count': self._error_count
            }
        )
    
    # ========================================================================
    # ECOSYSTEM HEALTH (MAIN ENTRY POINT)
    # ========================================================================
    
    async def get_ecosystem_health(self) -> EcosystemHealth:
        """
        Calculate ecosystem health metrics.
        
        FIXED v3.7.0: Total accounts query now uses stellar_accounts table
        (1,481 rows) instead of ubec_balances to get accurate total count.
        
        FIXED v3.6.4: Query now uses correct stellar_operations column names.
        The table has source_account, from_account, and to_account columns,
        NOT a destination column.
        
        Active Accounts Calculation:
            Counts unique accounts with activity in the last 30 days by examining:
            - source_account: Account initiating the operation
            - from_account: Sender in payment operations  
            - to_account: Receiver in payment operations
        
        Returns:
            EcosystemHealth dataclass with system-wide metrics
        """
        # Check cache
        cache_key = "ecosystem_health"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        logger.info("Calculating ecosystem health...")
        
        try:
            # FIXED v3.7.0: Total accounts from stellar_accounts table
            # This gives us ALL accounts that exist in the system (1,481 accounts)
            # regardless of whether they currently hold tokens
            accounts_query = f"""
                SELECT COUNT(DISTINCT account_id) as total
                FROM {self.db_schema}.stellar_accounts
            """
            accounts_result = await self._execute_query(accounts_query, ())
            total_accounts = accounts_result['total'] if accounts_result else 0
            
            # Active accounts (FIXED v3.6.4: use correct column names)
            # stellar_operations has: source_account, from_account, to_account (NOT destination)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            active_query = f"""
                SELECT COUNT(DISTINCT account_id) as active
                FROM (
                    SELECT source_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= $1
                    AND source_account IS NOT NULL
                    UNION
                    SELECT from_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= $1
                    AND from_account IS NOT NULL
                    UNION
                    SELECT to_account as account_id
                    FROM {self.db_schema}.stellar_operations
                    WHERE created_at >= $1
                    AND to_account IS NOT NULL
                ) combined
            """
            active_result = await self._execute_query(active_query, (thirty_days_ago,))
            active_accounts = active_result['active'] if active_result else 0
            
            # ADDED v3.7.0: Data consistency validation
            if active_accounts > total_accounts:
                logger.warning(
                    f"⚠️  DATA INCONSISTENCY DETECTED: "
                    f"active_accounts ({active_accounts}) > total_accounts ({total_accounts}). "
                    f"This indicates stellar_operations contains accounts not in stellar_accounts. "
                    f"Consider running full account discovery sync."
                )
            
            # FIXED v3.7.0: Network activity score with safety bounds (0-100)
            # Cap at 100% to handle data inconsistencies gracefully
            if total_accounts > 0:
                raw_activity_score = (active_accounts / total_accounts * 100)
                activity_score = min(100.0, raw_activity_score)
                
                if raw_activity_score > 100.0:
                    logger.warning(
                        f"Network activity score capped at 100% "
                        f"(calculated: {raw_activity_score:.2f}%)"
                    )
            else:
                activity_score = 0.0
            
            # Element balance score (FIXED v3.5.9: ensure 0-100 range)
            # Get holder counts for each element
            balance_query = f"""
                SELECT 
                    {_TableColumns.get_balance_token_col()},
                    COUNT(*) as holders
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
                GROUP BY {_TableColumns.get_balance_token_col()}
            """
            balance_results = await self._execute_query_all(balance_query, ())
            
            if balance_results and len(balance_results) > 1:
                holder_counts = [r['holders'] for r in balance_results]
                avg_holders = sum(holder_counts) / len(holder_counts)
                
                # Calculate coefficient of variation (lower = more balanced)
                variance = sum((x - avg_holders) ** 2 for x in holder_counts) / len(holder_counts)
                std_dev = variance ** 0.5
                cv = (std_dev / avg_holders) if avg_holders > 0 else 0
                
                # Convert to 0-100 scale (lower CV = higher score)
                # CV of 0 = perfect balance = 100, CV of 1+ = poor balance = 0
                element_balance_score = max(0.0, min(100.0, 100.0 * (1.0 - min(cv, 1.0))))
            else:
                element_balance_score = 0.0
            
            health = EcosystemHealth(
                total_accounts=total_accounts,
                active_accounts=active_accounts,
                network_activity_score=activity_score,
                element_balance_score=element_balance_score,
                timestamp=datetime.now().isoformat()
            )
            
            # Cache result
            self._set_cache(cache_key, health)
            
            logger.info(f"✓ Ecosystem health calculated: {active_accounts}/{total_accounts} active")
            return health
            
        except Exception as e:
            self._record_error(f"Error calculating ecosystem health: {e}")
            raise AnalyticsException(f"Ecosystem health calculation failed: {e}")
    
    # ========================================================================
    # TOKEN DISTRIBUTION ANALYSIS
    # ========================================================================
    
    async def get_token_distribution(self, token_code: str) -> TokenDistribution:
        """
        Get comprehensive token distribution metrics.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            TokenDistribution dataclass with distribution metrics
        """
        # Validate token code
        try:
            TokenCode(token_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {token_code}")
        
        # Check cache
        cache_key = f"distribution_{token_code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        logger.info(f"Calculating distribution for {token_code}...")
        
        try:
            # Get total supply and holder count
            # Note: ubec_balances uses token_code column (ENUM)
            supply_query = f"""
                SELECT 
                    SUM(balance) as total_supply,
                    COUNT(*) as total_holders,
                    SUM(CASE WHEN balance > 0 THEN balance ELSE 0 END) as circulating_supply
                FROM {self.db_schema}.ubec_balances
                WHERE {_TableColumns.get_balance_token_col()} = $1
            """
            supply_result = await self._execute_query(supply_query, (token_code,))
            
            if not supply_result:
                raise AnalyticsException(f"No data found for token {token_code}")
            
            total_supply = Decimal(str(supply_result['total_supply'] or 0))
            total_holders = supply_result['total_holders'] or 0
            circulating_supply = Decimal(str(supply_result['circulating_supply'] or 0))
            
            # Get top holder concentrations
            top_holders_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE {_TableColumns.get_balance_token_col()} = $1
                AND balance > 0
                ORDER BY balance DESC
                LIMIT 100
            """
            top_holders = await self._execute_query_all(top_holders_query, (token_code,))
            
            top_10_holdings = sum(Decimal(str(h['balance'])) for h in top_holders[:10]) if top_holders else Decimal(0)
            top_100_holdings = sum(Decimal(str(h['balance'])) for h in top_holders) if top_holders else Decimal(0)
            
            # Calculate concentration index (Herfindahl-Hirschman Index)
            if total_supply > 0 and top_holders:
                hhi = sum(
                    (Decimal(str(h['balance'])) / total_supply) ** 2
                    for h in top_holders
                )
                concentration_index = float(hhi * 10000)  # Scale to 0-10000
            else:
                concentration_index = 0.0
            
            distribution = TokenDistribution(
                token_code=token_code,
                total_supply=total_supply,
                total_holders=total_holders,
                circulating_supply=circulating_supply,
                concentration_index=concentration_index,
                top_10_holdings=top_10_holdings,
                top_100_holdings=top_100_holdings,
                timestamp=datetime.now().isoformat()
            )
            
            # Cache result
            self._set_cache(cache_key, distribution)
            
            logger.info(f"✓ Distribution calculated for {token_code}")
            return distribution
            
        except Exception as e:
            self._record_error(f"Error calculating distribution for {token_code}: {e}")
            raise AnalyticsException(f"Distribution calculation failed: {e}")
    
    async def analyze_holder_concentration(self, token_code: str) -> HolderAnalysis:
        """
        Analyze holder concentration and identify whales.
        
        A "whale" is defined as a holder with >= 1% of total supply.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            HolderAnalysis dataclass with concentration metrics
        """
        # Validate token code
        try:
            TokenCode(token_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {token_code}")
        
        logger.info(f"Analyzing holder concentration for {token_code}...")
        
        try:
            # Get distribution first
            dist = await self.get_token_distribution(token_code)
            
            if dist.total_supply == 0:
                return HolderAnalysis(
                    token_code=token_code,
                    total_holders=0,
                    whale_count=0,
                    whale_percentage=0.0,
                    concentration_score=0.0,
                    gini_coefficient=0.0,
                    timestamp=datetime.now().isoformat()
                )
            
            # Identify whales (holders with >= 1% of supply)
            whale_threshold = dist.total_supply * Decimal('0.01')
            whale_query = f"""
                SELECT COUNT(*) as whale_count
                FROM {self.db_schema}.ubec_balances
                WHERE {_TableColumns.get_balance_token_col()} = $1
                AND balance >= $2
            """
            whale_result = await self._execute_query(whale_query, (token_code, float(whale_threshold)))
            whale_count = whale_result['whale_count'] if whale_result else 0
            
            # Calculate whale percentage
            whale_percentage = (whale_count / dist.total_holders * 100) if dist.total_holders > 0 else 0.0
            
            # Calculate Gini coefficient
            balances_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE {_TableColumns.get_balance_token_col()} = $1
                AND balance > 0
                ORDER BY balance ASC
            """
            balances = await self._execute_query_all(balances_query, (token_code,))
            
            if balances and len(balances) > 1:
                sorted_balances = [float(b['balance']) for b in balances]
                n = len(sorted_balances)
                
                # Gini calculation
                numerator = sum(
                    (2 * i - n - 1) * balance
                    for i, balance in enumerate(sorted_balances, 1)
                )
                denominator = n * sum(sorted_balances)
                gini = numerator / denominator if denominator > 0 else 0.0
            else:
                gini = 0.0
            
            # Concentration score (normalized)
            # Higher score = more concentrated
            concentration_score = (
                (dist.concentration_index / 10000 * 0.5) +  # HHI component
                (whale_percentage / 100 * 0.3) +            # Whale percentage component
                (gini * 0.2)                                # Gini component
            ) * 100  # Scale to 0-100
            
            analysis = HolderAnalysis(
                token_code=token_code,
                total_holders=dist.total_holders,
                whale_count=whale_count,
                whale_percentage=whale_percentage,
                concentration_score=min(100.0, concentration_score),
                gini_coefficient=gini,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"✓ Holder concentration analyzed for {token_code}")
            return analysis
            
        except Exception as e:
            self._record_error(f"Error analyzing holder concentration for {token_code}: {e}")
            raise AnalyticsException(f"Holder analysis failed: {e}")
    
    # ========================================================================
    # TRANSACTION VELOCITY METRICS
    # ========================================================================
    
    async def get_transaction_velocity(self, token_code: str) -> TransactionMetrics:
        """
        Calculate transaction velocity and activity metrics.
        
        FIXED v3.6.3: Added missing asset_code filter to prevent PostgreSQL
        parameter type inference errors.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            TransactionMetrics dataclass with velocity metrics
        """
        # Validate token code
        try:
            TokenCode(token_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {token_code}")
        
        logger.info(f"Calculating transaction velocity for {token_code}...")
        
        try:
            now = datetime.now(timezone.utc)
            
            # FIXED v3.6.3: Added asset_code filter to all time-based queries
            # This resolves "could not determine data type of parameter $1" error
            
            # 7-day transactions
            seven_days_ago = now - timedelta(days=7)
            tx_7d_query = f"""
                SELECT COUNT(*) as count, COALESCE(AVG(amount), 0) as avg_amount
                FROM {self.db_schema}.stellar_operations
                WHERE asset_code = $1
                AND created_at >= $2
                AND type = 'payment'
            """
            tx_7d = await self._execute_query(tx_7d_query, (token_code, seven_days_ago))
            
            # 30-day transactions
            thirty_days_ago = now - timedelta(days=30)
            tx_30d_query = f"""
                SELECT COUNT(*) as count
                FROM {self.db_schema}.stellar_operations
                WHERE asset_code = $1
                AND created_at >= $2
                AND type = 'payment'
            """
            tx_30d = await self._execute_query(tx_30d_query, (token_code, thirty_days_ago))
            
            # 90-day transactions
            ninety_days_ago = now - timedelta(days=90)
            tx_90d_query = f"""
                SELECT COUNT(*) as count
                FROM {self.db_schema}.stellar_operations
                WHERE asset_code = $1
                AND created_at >= $2
                AND type = 'payment'
            """
            tx_90d = await self._execute_query(tx_90d_query, (token_code, ninety_days_ago))
            
            tx_count_7d = tx_7d['count'] if tx_7d else 0
            tx_count_30d = tx_30d['count'] if tx_30d else 0
            tx_count_90d = tx_90d['count'] if tx_90d else 0
            avg_tx_size = Decimal(str(tx_7d['avg_amount'])) if tx_7d else Decimal(0)
            
            # Calculate velocity score (0-100)
            # Based on transaction frequency and trend
            if tx_count_90d > 0:
                # Compare 7d vs 30d vs 90d to detect trends
                daily_7d = tx_count_7d / 7
                daily_30d = tx_count_30d / 30
                daily_90d = tx_count_90d / 90
                
                # Velocity increases if recent activity is higher
                trend_factor = 1.0
                if daily_30d > 0:
                    trend_factor += (daily_7d - daily_30d) / daily_30d * 0.5
                
                # Base velocity on daily transaction rate
                base_velocity = min(100.0, daily_7d * 10)  # 10 tx/day = 100 velocity
                velocity_score = max(0.0, min(100.0, base_velocity * trend_factor))
            else:
                velocity_score = 0.0
            
            metrics = TransactionMetrics(
                token_code=token_code,
                tx_count_7d=tx_count_7d,
                tx_count_30d=tx_count_30d,
                tx_count_90d=tx_count_90d,
                avg_tx_size=avg_tx_size,
                velocity_score=velocity_score,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"✓ Transaction velocity calculated for {token_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating velocity for {token_code}: {e}")
            raise AnalyticsException(f"Velocity calculation failed: {e}")
    
    # ========================================================================
    # LIQUIDITY METRICS
    # ========================================================================
    
    async def get_liquidity_metrics(self, token_code: str) -> LiquidityMetrics:
        """
        Calculate liquidity and market depth metrics.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            LiquidityMetrics dataclass with liquidity metrics
        """
        # Validate token code
        try:
            TokenCode(token_code)
        except ValueError:
            raise AnalyticsException(f"Invalid token code: {token_code}")
        
        logger.info(f"Calculating liquidity metrics for {token_code}...")
        
        try:
            # Get distribution data
            dist = await self.get_token_distribution(token_code)
            
            # Calculate liquidity ratio (circulating / total supply)
            liquidity_ratio = (
                float(dist.circulating_supply / dist.total_supply)
                if dist.total_supply > 0 else 0.0
            )
            
            # Get order book depth from stellar_offers
            depth_query = f"""
                SELECT 
                    COUNT(CASE WHEN side = 'buy' THEN 1 END) as buy_orders,
                    COUNT(CASE WHEN side = 'sell' THEN 1 END) as sell_orders,
                    COALESCE(SUM(CASE WHEN side = 'buy' THEN amount END), 0) as buy_volume,
                    COALESCE(SUM(CASE WHEN side = 'sell' THEN amount END), 0) as sell_volume
                FROM {self.db_schema}.stellar_offers
                WHERE selling_asset = $1
                AND status = 'active'
            """
            depth_result = await self._execute_query(depth_query, (token_code,))
            
            if depth_result:
                total_orders = (depth_result['buy_orders'] or 0) + (depth_result['sell_orders'] or 0)
                total_volume = float((depth_result['buy_volume'] or 0) + (depth_result['sell_orders'] or 0))
                
                # Depth score based on order count and volume
                depth_score = min(100.0, (total_orders * 2) + (total_volume / 10000))
            else:
                depth_score = 0.0
            
            # Average spread (simplified - would need actual order book analysis)
            # For now, estimate based on liquidity
            avg_spread = max(0.01, 1.0 - liquidity_ratio) * 5.0  # 0.05-5% spread
            
            # Get total liquidity from pools
            pool_query = f"""
                SELECT COALESCE(SUM(reserves->>'asset_a_amount'), '0')::numeric as pool_liquidity
                FROM {self.db_schema}.stellar_liquidity_pools
                WHERE (reserves->>'asset_a_code' = $1 OR reserves->>'asset_b_code' = $1)
            """
            pool_result = await self._execute_query(pool_query, (token_code,))
            total_liquidity = Decimal(str(pool_result['pool_liquidity'])) if pool_result else Decimal(0)
            
            metrics = LiquidityMetrics(
                token_code=token_code,
                total_liquidity=total_liquidity,
                liquidity_ratio=liquidity_ratio,
                avg_spread=avg_spread,
                depth_score=depth_score,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"✓ Liquidity metrics calculated for {token_code}")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating liquidity for {token_code}: {e}")
            raise AnalyticsException(f"Liquidity calculation failed: {e}")
    
    # ========================================================================
    # MAIN.PY INTERFACE METHODS
    # ========================================================================
    
    async def get_distribution_overview(self) -> Dict[str, Any]:
        """
        Get distribution overview for all tokens.
        
        Main.py interface method.
        
        Returns:
            Dict with distribution data for all four tokens
            
        Example (from main.py):
            overview = await analytics.get_distribution_overview()
            for token, data in overview['tokens'].items():
                print(f"{token}: {data['total_holders']} holders")
        """
        logger.info("Getting distribution overview...")
        
        try:
            overview = {
                'timestamp': datetime.now().isoformat(),
                'tokens': {}
            }
            
            for token in TokenCode:
                try:
                    dist = await self.get_token_distribution(token.value)
                    overview['tokens'][token.value] = asdict(dist)
                except Exception as e:
                    logger.warning(f"Error getting distribution for {token.value}: {e}")
            
            logger.info("✓ Distribution overview generated")
            return overview
            
        except Exception as e:
            self._record_error(f"Error generating distribution overview: {e}")
            raise AnalyticsException(f"Distribution overview failed: {e}")
    
    async def get_top_holders(
        self,
        token_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get top token holders across tokens or for specific token.
        
        Main.py interface method.
        
        Args:
            token_code: Optional token code filter (None for all tokens)
            limit: Maximum number of holders to return per token
            
        Returns:
            List of holder records with balances
            
        Example (from main.py):
            # Top 50 holders across all tokens
            holders = await analytics.get_top_holders(limit=50)
            
            # Top 100 UBEC holders
            ubec_holders = await analytics.get_top_holders(token_code='UBEC', limit=100)
        """
        logger.info(f"Getting top {limit} holders{f' for {token_code}' if token_code else ''}...")
        
        try:
            # Build query with optional token filter
            params = [limit]
            token_filter = ""
            
            if token_code:
                # Validate token code
                try:
                    TokenCode(token_code)
                except ValueError:
                    raise AnalyticsException(f"Invalid token code: {token_code}")
                
                token_filter = f"WHERE b.{_TableColumns.get_balance_token_col()} = $2"
                params.append(token_code)
            
            query = f"""
                WITH total_supply AS (
                    SELECT 
                        {_TableColumns.get_balance_token_col()},
                        SUM(balance) as supply
                    FROM {self.db_schema}.ubec_balances
                    WHERE balance > 0
                    GROUP BY {_TableColumns.get_balance_token_col()}
                )
                SELECT 
                    b.account_id,
                    b.{_TableColumns.get_balance_token_col()} as token_code,
                    b.balance,
                    (b.balance / ts.supply * 100) as balance_pct,
                    b.last_modified_at
                FROM {self.db_schema}.ubec_balances b
                JOIN total_supply ts ON b.{_TableColumns.get_balance_token_col()} = ts.{_TableColumns.get_balance_token_col()}
                WHERE b.balance > 0 {token_filter}
                ORDER BY b.balance DESC
                LIMIT $1
            """
            
            rows = await self._execute_query_all(query, tuple(params))
            
            # Format results
            holders = [
                {
                    'account_id': row['account_id'],
                    'token_code': row['token_code'],
                    'balance': float(row['balance']),
                    'balance_pct': float(row['balance_pct']),
                    'last_modified_at': row['last_modified_at'].isoformat() if row['last_modified_at'] else None
                }
                for row in rows
            ]
            
            logger.info(f"✓ Retrieved {len(holders)} top holders")
            return holders
            
        except Exception as e:
            self._record_error(f"Error getting top holders: {e}")
            raise AnalyticsException(f"Top holders query failed: {e}")
    
    async def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get network-wide metrics and ecosystem health.
        
        Main.py interface method.
        FIXED v3.7.0: Total accounts now correctly counted from stellar_accounts.
        FIXED v3.6.4: Active accounts query now uses correct column names.
        
        Returns:
            Dict with network metrics:
            - total_accounts: Total unique accounts
            - active_accounts: Accounts with activity in last 30 days
            - total_transactions_30d: Transaction count
            - network_activity_score: Activity score (0-100)
            - ecosystem_health: EcosystemHealth dataclass
            
        Example (from main.py):
            metrics = await analytics.get_network_metrics()
            print(f"Network activity: {metrics['network_activity_score']:.1f}/100")
            print(f"Active accounts: {metrics['active_accounts']}/{metrics['total_accounts']}")
        """
        logger.info("Calculating network metrics...")
        
        try:
            # Get ecosystem health (includes active account calculation)
            health = await self.get_ecosystem_health()
            
            # Get transaction count for last 30 days
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            tx_query = f"""
                SELECT COUNT(*) as tx_count
                FROM {self.db_schema}.stellar_operations
                WHERE created_at >= $1
            """
            tx_result = await self._execute_query(tx_query, (thirty_days_ago,))
            tx_count = tx_result['tx_count'] if tx_result else 0
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': health.total_accounts,
                'active_accounts': health.active_accounts,
                'total_transactions_30d': tx_count,
                'network_activity_score': health.network_activity_score,
                'element_balance_score': health.element_balance_score,
                'ecosystem_health': asdict(health)
            }
            
            logger.info("✓ Network metrics calculated")
            return metrics
            
        except Exception as e:
            self._record_error(f"Error calculating network metrics: {e}")
            raise AnalyticsException(f"Network metrics calculation failed: {e}")
    
    # ========================================================================
    # SCHEDULED OPERATIONS (v3.6.0+)
    # ========================================================================
    
    async def update_analytics(self) -> Dict[str, Any]:
        """
        Update all analytics metrics.
        
        This method is designed for scheduled execution by the scheduler service.
        It refreshes key analytics data and returns a summary of the update.
        
        Returns:
            Dict with update summary:
            - timestamp: When update completed
            - metrics_updated: List of updated metric types
            - success: Whether update succeeded
            - errors: Any errors encountered
            
        Example (from scheduler):
            result = await analytics.update_analytics()
            if result['success']:
                logger.info(f"Analytics updated: {result['metrics_updated']}")
        """
        logger.info("Updating analytics metrics...")
        
        errors = []
        metrics_updated = []
        
        try:
            # Update ecosystem health
            try:
                await self.get_ecosystem_health()
                metrics_updated.append('ecosystem_health')
            except Exception as e:
                errors.append(f"ecosystem_health: {e}")
            
            # Update distribution for each token
            for token in TokenCode:
                try:
                    await self.get_token_distribution(token.value)
                    metrics_updated.append(f'distribution_{token.value}')
                except Exception as e:
                    errors.append(f"distribution_{token.value}: {e}")
            
            # Update velocity metrics
            for token in TokenCode:
                try:
                    await self.get_transaction_velocity(token.value)
                    metrics_updated.append(f'velocity_{token.value}')
                except Exception as e:
                    errors.append(f"velocity_{token.value}: {e}")
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'metrics_updated': metrics_updated,
                'success': len(errors) == 0,
                'errors': errors if errors else None
            }
            
            if result['success']:
                logger.info(f"✓ Analytics updated: {len(metrics_updated)} metrics")
            else:
                logger.warning(f"Analytics update completed with {len(errors)} errors")
            
            return result
            
        except Exception as e:
            self._record_error(f"Error updating analytics: {e}")
            raise AnalyticsException(f"Analytics update failed: {e}")
    
    # ========================================================================
    # COMPARATIVE ANALYSIS
    # ========================================================================
    
    async def compare_tokens(self) -> Dict[str, Any]:
        """
        Compare metrics across all four tokens.
        
        Returns:
            Dict with comparative analysis:
            - tokens: Per-token metrics
            - rankings: Tokens ranked by various metrics
            - ecosystem: Overall ecosystem metrics
        """
        logger.info("Comparing tokens...")
        
        try:
            comparison = {
                'timestamp': datetime.now().isoformat(),
                'tokens': {},
                'rankings': {},
                'ecosystem': {}
            }
            
            # Get metrics for each token
            for token in TokenCode:
                try:
                    dist = await self.get_token_distribution(token.value)
                    velocity = await self.get_transaction_velocity(token.value)
                    liquidity = await self.get_liquidity_metrics(token.value)
                    
                    comparison['tokens'][token.value] = {
                        'distribution': asdict(dist),
                        'velocity': asdict(velocity),
                        'liquidity': asdict(liquidity)
                    }
                except Exception as e:
                    logger.warning(f"Error comparing {token.value}: {e}")
            
            # Generate comparative rankings if we have data
            if comparison['tokens']:
                # Rank by holder count
                comparison['rankings']['by_holders'] = sorted(
                    [
                        {
                            'token': token,
                            'holders': data['distribution']['total_holders']
                        }
                        for token, data in comparison['tokens'].items()
                    ],
                    key=lambda x: x['holders'],
                    reverse=True
                )
                
                # Rank by liquidity
                comparison['rankings']['by_liquidity'] = sorted(
                    [
                        {
                            'token': token,
                            'liquidity_ratio': data['liquidity']['liquidity_ratio']
                        }
                        for token, data in comparison['tokens'].items()
                    ],
                    key=lambda x: x['liquidity_ratio'],
                    reverse=True
                )
                
                # Rank by activity (30d transactions)
                comparison['rankings']['by_activity'] = sorted(
                    [
                        {
                            'token': token,
                            'tx_30d': data['velocity']['tx_count_30d']
                        }
                        for token, data in comparison['tokens'].items()
                    ],
                    key=lambda x: x['tx_30d'],
                    reverse=True
                )
            
            logger.info("✓ Token comparison complete")
            return comparison
            
        except Exception as e:
            self._record_error(f"Error comparing tokens: {e}")
            raise AnalyticsException(f"Token comparison failed: {e}")
    
    # ========================================================================
    # EXPORT & REPORTING
    # ========================================================================
    
    async def export_analytics_summary(self) -> Dict[str, Any]:
        """
        Export comprehensive analytics summary for all tokens.
        
        Returns:
            Dict containing all key metrics in exportable format
            
        Example:
            summary = await analytics.export_analytics_summary()
            
            # Save to file
            import json
            with open('ubec_analytics.json', 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        """
        logger.info("Exporting comprehensive analytics summary...")
        
        try:
            summary = {
                'generated_at': datetime.now().isoformat(),
                'ecosystem_health': None,
                'token_distributions': [],
                'holder_concentrations': [],
                'liquidity_metrics': [],
                'token_comparison': None
            }
            
            # Get ecosystem health
            health = await self.get_ecosystem_health()
            summary['ecosystem_health'] = asdict(health)
            
            # Get distributions for all tokens
            for token in TokenCode:
                try:
                    dist = await self.get_token_distribution(token.value)
                    summary['token_distributions'].append(asdict(dist))
                    
                    holder_analysis = await self.analyze_holder_concentration(token.value)
                    summary['holder_concentrations'].append(asdict(holder_analysis))
                    
                    liquidity = await self.get_liquidity_metrics(token.value)
                    summary['liquidity_metrics'].append(asdict(liquidity))
                    
                except Exception as e:
                    logger.warning(f"Error exporting data for {token.value}: {e}")
            
            # Get token comparison
            summary['token_comparison'] = await self.compare_tokens()
            
            logger.info("✓ Analytics summary exported")
            return summary
            
        except Exception as e:
            self._record_error(f"Error exporting analytics summary: {e}")
            raise AnalyticsException(f"Analytics export failed: {e}")


# ==================== MODULE EXPORTS ====================

__all__ = [
    'UBECAnalyticsService',
    'TokenDistribution',
    'HolderAnalysis',
    'TransactionMetrics',
    'LiquidityMetrics',
    'EcosystemHealth',
    'TokenCode',
    'ElementType',
    'AnalyticsException'
]


# ==================== STANDALONE EXECUTION PREVENTION ====================
# Principle #2: Service Pattern - No standalone execution

if __name__ == "__main__":
    print("=" * 80)
    print("UBEC Protocol Suite - Analytics Service")
    print("=" * 80)
    print()
    print("This service provides comprehensive analytics for the UBEC token ecosystem.")
    print("It analyzes distribution, holder patterns, and ecosystem health across all")
    print("four UBEC elements (Air, Water, Earth, Fire).")
    print()
    print("VERSION: 3.7.0 (Data Consistency Fix - Total Accounts Query Correction)")
    print()
    print("🔥 CRITICAL FIX: Total accounts now counted from stellar_accounts table")
    print("✅ RESOLVES: Active accounts > Total accounts data inconsistency")
    print("✅ FIXED: Network activity score capped at 100% (was 163.5%)")
    print("✅ All design principles fully implemented")
    print()
    print("USAGE:")
    print("------")
    print()
    print("  # Via service registry (RECOMMENDED - Principle #3)")
    print("  from core.service_registry import registry")
    print("  analytics = await registry.get('analytics')")
    print()
    print("  # Main.py interface methods")
    print("  result = await analytics.get_distribution_overview()")
    print("  result = await analytics.get_top_holders(limit=50)")
    print("  result = await analytics.get_network_metrics()")
    print()
    print("  # Scheduled operations (v3.6.0+)")
    print("  result = await analytics.update_analytics()")
    print()
    print("  # Health check (VERIFIED CORRECT!)")
    print("  health = await analytics.health_check()")
    print("  print(f'Status: {health[\"status\"]}')")
    print()
    print("  # Proper shutdown")
    print("  await analytics.close()")
    print()
    print("DESIGN PRINCIPLES:")
    print("------------------")
    print("✅ All 12 principles fully implemented")
    print("✅ Proper service registry integration")
    print("✅ Health check using ServiceHealthCheck utility")
    print("✅ Explicit schema names in all queries")
    print("✅ Comprehensive error tracking")
    print("✅ Cache performance monitoring")
    print("✅ Data consistency validation")
    print()
    print("=" * 80)
