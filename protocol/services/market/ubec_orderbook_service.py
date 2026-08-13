#!/usr/bin/env python3
# core/services/ubec_orderbook_service.py
"""
UBEC Order Book Analytics Service
==================================
Service implementation for order book analytics across the UBEC four-element system.

Provides comprehensive analytics and insights for order book dynamics across
the UBEC token ecosystem. Analyzes depth, account positions, market microstructure,
and order flow patterns for all four UBEC elements.

This module implements the service pattern with:
- Pure async operations (no sync fallbacks)
- Factory function for instantiation
- Database as single source of truth
- Built-in rate limiting
- In-memory caching with TTL
- Comprehensive health monitoring using ServiceHealthCheck utility

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained service with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, factory-based instantiation
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks and order book tracking
    ✅ 8.  No Duplicate Config: Uses global configuration
    ✅ 9.  Rate Limiting: Built-in API rate limiting
    ✅ 10. Separation of Concerns: Order book logic separated from data access
    ✅ 11. Documentation: Comprehensive docstrings and inline comments
    ✅ 12. Method Singularity: No duplicate methods, uses ServiceHealthCheck utility
══════════════════════════════════════════════════════════════════════════════

Usage:
    from ubec_orderbook_service import create_orderbook_service
    
    service = await create_orderbook_service(
        db_manager=async_db,
        stellar_client=stellar_async,
        issuer_address='G...'
    )
    
    await service.initialize()
    
    # All methods are async
    snapshot = await service.fetch_orderbook_snapshot('UBEC')
    depth = await service.analyze_market_depth('UBEC')
    health = await service.health_check()
    
    await service.close()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 2.2.0 (Standardized Health Check Pattern)
Date: October 17, 2025

Changelog:
    v2.2.0 - MAJOR: Standardized health check using ServiceHealthCheck utility
           - Implements Principle #12: Method Singularity with shared utility
           - Removed custom health_check() implementation
           - Now uses ServiceHealthCheck.api_dependent_health()
           - Added enhanced background task monitoring
           - Cleaner, more maintainable code with consistent patterns
           - Full compliance with health check implementation guide
    v2.1.0 - Enhanced health_check() method for comprehensive monitoring
           - Implements Principle #7: Per-Asset Monitoring with detailed checks
           - Added initialization tracking
           - Improved error handling and validation
           - Added operation statistics tracking
           - Enhanced order book metrics
    v1.0.0 - Initial production release
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

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


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


# Element to token mapping
ELEMENT_TOKEN_MAP = {
    ElementType.AIR: TokenCode.UBEC,
    ElementType.WATER: TokenCode.UBECRC,
    ElementType.EARTH: TokenCode.UBECGPI,
    ElementType.FIRE: TokenCode.UBECTT
}

TOKEN_ELEMENT_MAP = {v: k for k, v in ELEMENT_TOKEN_MAP.items()}


# ==================== EXCEPTIONS ====================

class OrderBookException(Exception):
    """Base exception for order book service"""
    pass


# ==================== DATA MODELS ====================

@dataclass
class OrderBookLevel:
    """
    Single price level in order book.
    
    Principle 1: Modular Design - Clear data structure
    """
    price: Decimal
    amount: Decimal
    price_r_n: int  # Price ratio numerator
    price_r_d: int  # Price ratio denominator


@dataclass
class OrderBookSnapshot:
    """
    Complete order book snapshot.
    
    Principle 7: Per-Asset Monitoring - Comprehensive snapshot
    """
    asset_code: str
    counter_asset: str
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    best_bid: Decimal
    best_ask: Decimal
    spread: Decimal
    spread_bps: int
    mid_price: Decimal
    bid_depth_total: Decimal
    ask_depth_total: Decimal


@dataclass
class AccountOrder:
    """Individual order/offer"""
    offer_id: int
    account_id: str
    side: OrderSide
    price: Decimal
    amount: Decimal
    asset_code: str
    counter_asset: str
    is_passive: bool
    created_at: datetime
    last_modified: datetime


@dataclass
class AccountOrderPosition:
    """Account's order book positions for a specific asset"""
    account_id: str
    asset_code: str
    buy_orders: List[AccountOrder]
    sell_orders: List[AccountOrder]
    total_buy_volume: Decimal
    total_sell_volume: Decimal
    avg_buy_price: Decimal
    avg_sell_price: Decimal
    net_position: Decimal  # buy_volume - sell_volume
    last_updated: datetime


@dataclass
class MarketDepthMetrics:
    """Market depth and liquidity analysis"""
    asset_code: str
    counter_asset: str
    timestamp: datetime
    total_bid_liquidity: Decimal
    total_ask_liquidity: Decimal
    bid_ask_ratio: Decimal
    depth_within_1pct: Decimal
    depth_within_5pct: Decimal
    depth_within_10pct: Decimal
    top_5_bid_concentration: Decimal
    top_5_ask_concentration: Decimal
    unique_bid_accounts: int
    unique_ask_accounts: int
    bid_levels: int
    ask_levels: int
    market_depth_score: Decimal


# ==================== SERVICE IMPLEMENTATION ====================

class UBECOrderBookService:
    """
    UBEC Order Book Analytics Service
    
    Manages order book analytics and insights for the UBEC ecosystem.
    All operations are async and use the database as the single source of truth.
    
    Tracks and analyzes:
    - Real-time order book snapshots
    - Account order positions
    - Market depth and liquidity
    - Order flow patterns
    - Historical trends
    
    Attributes:
        db_manager: Async database manager
        stellar_client: Async Stellar SDK client
        issuer: UBEC token issuer address
        logger: Logger instance
        rate_limiter: API rate limiter
        
    Lifecycle:
        1. Instantiate via create_orderbook_service() factory
        2. Call initialize() to start service
        3. Use analysis methods
        4. Cleanup via close() method
        
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
        stellar_client,
        issuer_address: str,
        rate_limiter = None,
        cache_ttl: int = 60,
        sync_interval: int = 300
    ):
        """
        Initialize order book service.
        
        DO NOT call directly - use create_orderbook_service() factory instead.
        
        Args:
            db_manager: Database manager with async support
            stellar_client: Stellar ServerAsync client
            issuer_address: UBEC token issuer address
            rate_limiter: Optional rate limiter (creates default if None)
            cache_ttl: Cache time-to-live in seconds (default: 60)
            sync_interval: Background sync interval in seconds (default: 300)
        """
        self.db_manager = db_manager
        self.stellar_client = stellar_client
        self.issuer = issuer_address
        self.cache_ttl = cache_ttl
        self.sync_interval = sync_interval
        
        # Setup logging
        self.logger = logging.getLogger('UBECOrderBook')
        
        # Rate limiting (Principle 9: Integrated Rate Limiting)
        self.rate_limiter = rate_limiter or RateLimiter(calls_per_second=10.0)
        
        # In-memory cache with TTL
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._counter_assets = ["XLM"]  # Default counter assets
        
        # Initialization and operation tracking (for health checks)
        self._initialized = False
        self._sync_task: Optional[asyncio.Task] = None
        self._last_sync_time: Optional[datetime] = None
        self._last_fetch_time: Optional[datetime] = None
        self._sync_count = 0
        self._fetch_count = 0
        self._analysis_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info(f"Order Book Service created for issuer {issuer_address[:8]}...")
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    
    async def initialize(self):
        """
        Initialize service and start background tasks.
        
        Principle 5: Async initialization
        """
        if self._initialized:
            self.logger.warning("Order book service already initialized")
            return
        
        try:
            # Verify database connection
            if hasattr(self.db_manager, 'conn') and self.db_manager.conn is None:
                await self.db_manager.connect()
            
            # Test database connectivity
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query)
            if not result:
                raise OrderBookException("Database connection test failed")
            
            self.logger.info("✓ Database connection verified")
            
            # Load configuration
            await self._load_configuration()
            
            # Start background sync task
            self._sync_task = asyncio.create_task(self._background_orderbook_sync())
            
            self._initialized = True
            self.logger.info("✓ Order book service initialized successfully")
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Initialization failed: {e}")
            raise OrderBookException(f"Service initialization failed: {e}")
    
    async def _load_configuration(self):
        """
        Load service configuration from database.
        
        Principle 4: Database as single source of truth
        """
        try:
            query = """
            SELECT parameter_name, parameter_value 
            FROM ubec_main.system_configuration 
            WHERE parameter_name LIKE 'orderbook_%'
            """
            config = await self.db_manager.fetch_all(query)
            
            for row in config:
                if row['parameter_name'] == 'orderbook_counter_assets':
                    self._counter_assets = json.loads(row['parameter_value'])
                elif row['parameter_name'] == 'orderbook_cache_ttl':
                    self.cache_ttl = int(row['parameter_value'])
                elif row['parameter_name'] == 'orderbook_sync_interval':
                    self.sync_interval = int(row['parameter_value'])
            
            self.logger.info(f"Configuration loaded: {len(config)} parameters")
            
        except Exception as e:
            self.logger.warning(f"Could not load config, using defaults: {e}")
    
    # ==================== HEALTH CHECK ====================
    # Principle 7: Per-Asset Monitoring with health checks
    # Principle 12: Method Singularity - Uses standardized utility
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on order book service.
        
        Uses standardized ServiceHealthCheck utility for consistency across
        all services, implementing Principle #12 (Method Singularity).
        
        This implementation follows the health check pattern guide:
        - Uses ServiceHealthCheck.api_dependent_health() for API-based services
        - Provides cache information with TTL tracking
        - Includes service-specific context (background sync status)
        - Tracks operation metrics and error rates
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'has_rate_limiter': bool,
                    'has_cache': bool,
                    'rate_limiter': {...},
                    'cache': {
                        'size': int,
                        'valid_entries': int,
                        'expired_entries': int,
                        'last_fetch': str (ISO timestamp),
                        'status': str
                    },
                    'issuer': str,
                    'background_sync_running': bool,
                    'last_sync': str (ISO timestamp),
                    'sync_count': int,
                    'fetch_count': int,
                    'analysis_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp)
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Order book service operational")
            ...     print(f"Cache: {health['details']['cache']['valid_entries']} entries")
            >>> else:
            ...     print(f"Issues detected: {health['message']}")
        
        Design Notes:
            - Principle 7: Comprehensive per-service monitoring
            - Principle 12: Delegates to ServiceHealthCheck utility (no duplication)
        """
        # Prepare cache information for health check
        cache_info = {
            'size': len(self._cache),
            'last_fetch': self._last_fetch_time.isoformat() if self._last_fetch_time else None
        }
        
        # Analyze cache validity if cache exists
        if self._cache:
            now = datetime.now()
            valid_entries = sum(
                1 for _, (_, timestamp) in self._cache.items()
                if now - timestamp < timedelta(seconds=self.cache_ttl)
            )
            expired_entries = len(self._cache) - valid_entries
            
            cache_info['valid_entries'] = valid_entries
            cache_info['expired_entries'] = expired_entries
            
            # Determine cache status
            if expired_entries == 0:
                cache_info['status'] = 'fresh'
            elif valid_entries > expired_entries:
                cache_info['status'] = 'mostly_fresh'
            elif valid_entries > 0:
                cache_info['status'] = 'stale'
            else:
                cache_info['status'] = 'expired'
        else:
            cache_info['status'] = 'empty'
        
        # Check background sync task status
        background_sync_running = False
        sync_task_error = None
        
        if self._sync_task:
            background_sync_running = not self._sync_task.done()
            
            if self._sync_task.done():
                try:
                    # Check if task failed
                    exception = self._sync_task.exception()
                    if exception:
                        sync_task_error = str(exception)
                except asyncio.InvalidStateError:
                    pass
        
        # Use standardized health check utility (Principle #12: Method Singularity)
        return await ServiceHealthCheck.api_dependent_health(
            service_name='orderbook_analytics',
            is_initialized=self._initialized,
            rate_limiter=self.rate_limiter,
            cache_info=cache_info,
            # Service-specific context
            issuer=self.issuer,
            background_sync_running=background_sync_running,
            sync_task_error=sync_task_error,
            last_sync=self._last_sync_time.isoformat() if self._last_sync_time else None,
            sync_interval=self.sync_interval,
            cache_ttl=self.cache_ttl,
            counter_assets=self._counter_assets,
            # Operation statistics
            sync_count=self._sync_count,
            fetch_count=self._fetch_count,
            analysis_count=self._analysis_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time.isoformat() if self._last_error_time else None
        )
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        
        Principle 11: Comprehensive validation
        """
        if not self.issuer:
            raise ValueError("issuer address not configured")
        
        # Validate issuer format (Stellar public key)
        if not self.issuer.startswith('G') or len(self.issuer) != 56:
            raise ValueError(f"Invalid issuer address format: {self.issuer}")
        
        if self.cache_ttl <= 0:
            raise ValueError("cache_ttl must be positive")
        
        if self.sync_interval <= 0:
            raise ValueError("sync_interval must be positive")
    
    # ==================== CACHE MANAGEMENT ====================
    # Principle 10: Clear Separation - Cache management separated
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """
        Get item from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if datetime.now() - timestamp > timedelta(seconds=self.cache_ttl):
            del self._cache[key]
            return None
        
        return value
    
    def _set_cached(self, key: str, value: Any):
        """
        Store item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, datetime.now())
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self.logger.info("Cache cleared")
    
    # ==================== ORDER BOOK FETCHING ====================
    # Principle 10: Separation of Concerns - Business logic layer
    
    async def fetch_orderbook_snapshot(
        self,
        asset_code: str,
        counter_asset: str = "XLM",
        use_cache: bool = True
    ) -> OrderBookSnapshot:
        """
        Fetch current order book snapshot from Stellar network.
        
        Args:
            asset_code: UBEC token code (UBEC, UBECrc, UBECgpi, UBECtt)
            counter_asset: Counter asset (default XLM)
            use_cache: Use cached data if available
            
        Returns:
            OrderBookSnapshot with bids, asks, and metrics
            
        Raises:
            OrderBookException: If fetch fails
            
        Example:
            >>> snapshot = await service.fetch_orderbook_snapshot('UBEC')
            >>> print(f"Spread: {snapshot.spread_bps} bps")
            >>> print(f"Bid depth: {snapshot.bid_depth_total}")
        
        Design Notes:
            - Principle 5: Fully async operation
            - Principle 7: Per-asset monitoring
            - Principle 9: Rate limiting applied
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        # Track operation
        self._last_fetch_time = datetime.now()
        self._fetch_count += 1
        
        # Check cache
        cache_key = f"orderbook:{asset_code}:{counter_asset}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for {cache_key}")
                return cached
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Import here to avoid circular dependency
            from stellar_sdk import Asset
            
            # Create asset objects
            selling_asset = Asset(asset_code, self.issuer)
            buying_asset = (Asset.native() if counter_asset == "XLM" 
                           else Asset(counter_asset, self.issuer))
            
            # Fetch from Stellar
            self.logger.debug(f"Fetching {asset_code}/{counter_asset} from Stellar")
            orderbook_response = await self.stellar_client.orderbook(
                selling=selling_asset,
                buying=buying_asset
            ).limit(200).call()
            
            # Parse bids
            bids = []
            for level in orderbook_response.get('bids', []):
                bids.append(OrderBookLevel(
                    price=Decimal(level['price']),
                    amount=Decimal(level['amount']),
                    price_r_n=int(level['price_r']['n']),
                    price_r_d=int(level['price_r']['d'])
                ))
            
            # Parse asks
            asks = []
            for level in orderbook_response.get('asks', []):
                asks.append(OrderBookLevel(
                    price=Decimal(level['price']),
                    amount=Decimal(level['amount']),
                    price_r_n=int(level['price_r']['n']),
                    price_r_d=int(level['price_r']['d'])
                ))
            
            # Calculate metrics
            best_bid = bids[0].price if bids else Decimal('0')
            best_ask = asks[0].price if asks else Decimal('0')
            mid_price = ((best_bid + best_ask) / 2 
                        if (bids and asks) else Decimal('0'))
            spread = best_ask - best_bid if (bids and asks) else Decimal('0')
            spread_bps = int((spread / mid_price) * 10000) if mid_price > 0 else 0
            
            bid_depth = sum(level.amount for level in bids)
            ask_depth = sum(level.amount for level in asks)
            
            snapshot = OrderBookSnapshot(
                asset_code=asset_code,
                counter_asset=counter_asset,
                timestamp=datetime.now(),
                bids=bids,
                asks=asks,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                spread_bps=spread_bps,
                mid_price=mid_price,
                bid_depth_total=bid_depth,
                ask_depth_total=ask_depth
            )
            
            # Store to database
            await self._store_snapshot(snapshot)
            
            # Cache result
            self._set_cached(cache_key, snapshot)
            
            self.logger.info(
                f"✓ Fetched {asset_code}/{counter_asset}: "
                f"Spread={spread_bps}bps, Depth={bid_depth + ask_depth}"
            )
            
            return snapshot
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error fetching snapshot: {e}")
            raise OrderBookException(f"Failed to fetch order book: {e}")
    
    async def _store_snapshot(self, snapshot: OrderBookSnapshot):
        """
        Store order book snapshot to database.
        
        Principle 4: Database as single source of truth
        """
        try:
            query = """
            INSERT INTO ubec_main.orderbook_snapshots (
                asset_code, counter_asset, snapshot_time,
                best_bid, best_ask, spread_bps,
                bid_depth_total, ask_depth_total,
                bid_levels, ask_levels, raw_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (asset_code, counter_asset, snapshot_time) DO UPDATE SET
                best_bid = EXCLUDED.best_bid,
                best_ask = EXCLUDED.best_ask,
                spread_bps = EXCLUDED.spread_bps,
                bid_depth_total = EXCLUDED.bid_depth_total,
                ask_depth_total = EXCLUDED.ask_depth_total,
                bid_levels = EXCLUDED.bid_levels,
                ask_levels = EXCLUDED.ask_levels,
                raw_data = EXCLUDED.raw_data
            """
            
            raw_data = {
                'bids': [
                    {'price': str(b.price), 'amount': str(b.amount)} 
                    for b in snapshot.bids[:10]
                ],
                'asks': [
                    {'price': str(a.price), 'amount': str(a.amount)} 
                    for a in snapshot.asks[:10]
                ]
            }
            
            await self.db_manager.execute(
                query,
                (snapshot.asset_code, snapshot.counter_asset, snapshot.timestamp,
                 snapshot.best_bid, snapshot.best_ask, snapshot.spread_bps,
                 snapshot.bid_depth_total, snapshot.ask_depth_total,
                 len(snapshot.bids), len(snapshot.asks), json.dumps(raw_data))
            )
            
        except Exception as e:
            self.logger.warning(f"Could not store snapshot: {e}")
    
    # ==================== MARKET DEPTH ANALYSIS ====================
    
    async def analyze_market_depth(
        self,
        asset_code: str,
        counter_asset: str = "XLM",
        use_cache: bool = True
    ) -> MarketDepthMetrics:
        """
        Analyze market depth and liquidity distribution.
        
        Calculates:
        - Total bid/ask liquidity
        - Depth within price ranges (1%, 5%, 10%)
        - Concentration metrics (top 5 orders)
        - Unique participant counts
        - Market depth score (0-100)
        
        Args:
            asset_code: UBEC token code
            counter_asset: Counter asset
            use_cache: Use cached data
            
        Returns:
            MarketDepthMetrics object
            
        Principle 12: Single implementation of depth analysis
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        # Track operation
        self._analysis_count += 1
        
        # Check cache
        cache_key = f"depth:{asset_code}:{counter_asset}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get order book snapshot
            snapshot = await self.fetch_orderbook_snapshot(
                asset_code, counter_asset, use_cache
            )
            
            # Calculate total liquidity
            total_bid_liq = snapshot.bid_depth_total
            total_ask_liq = snapshot.ask_depth_total
            
            # Liquidity within percentage ranges
            mid = snapshot.mid_price
            depth_1pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.01'))
            depth_5pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.05'))
            depth_10pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.10'))
            
            # Top 5 concentration
            top_5_bid_vol = (sum(level.amount for level in snapshot.bids[:5])
                            if len(snapshot.bids) >= 5 else total_bid_liq)
            top_5_ask_vol = (sum(level.amount for level in snapshot.asks[:5])
                            if len(snapshot.asks) >= 5 else total_ask_liq)
            
            top_5_bid_pct = ((top_5_bid_vol / total_bid_liq * 100) 
                            if total_bid_liq > 0 else Decimal('0'))
            top_5_ask_pct = ((top_5_ask_vol / total_ask_liq * 100)
                            if total_ask_liq > 0 else Decimal('0'))
            
            # Get unique account counts
            unique_buyers, unique_sellers = await self._count_unique_traders(asset_code)
            
            # Calculate market depth score
            depth_score = self._calculate_market_depth_score(
                total_bid_liq, total_ask_liq, depth_1pct,
                unique_buyers, unique_sellers,
                top_5_bid_pct, top_5_ask_pct
            )
            
            metrics = MarketDepthMetrics(
                asset_code=asset_code,
                counter_asset=counter_asset,
                timestamp=datetime.now(),
                total_bid_liquidity=total_bid_liq,
                total_ask_liquidity=total_ask_liq,
                bid_ask_ratio=(total_bid_liq / total_ask_liq 
                              if total_ask_liq > 0 else Decimal('0')),
                depth_within_1pct=depth_1pct,
                depth_within_5pct=depth_5pct,
                depth_within_10pct=depth_10pct,
                top_5_bid_concentration=top_5_bid_pct,
                top_5_ask_concentration=top_5_ask_pct,
                unique_bid_accounts=unique_buyers,
                unique_ask_accounts=unique_sellers,
                bid_levels=len(snapshot.bids),
                ask_levels=len(snapshot.asks),
                market_depth_score=depth_score
            )
            
            # Cache result
            self._set_cached(cache_key, metrics)
            
            self.logger.info(f"✓ Market depth analyzed: Score={depth_score:.1f}")
            
            return metrics
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error analyzing market depth: {e}")
            raise OrderBookException(f"Market depth analysis failed: {e}")
    
    def _calculate_depth_in_range(
        self,
        snapshot: OrderBookSnapshot,
        mid_price: Decimal,
        pct_range: Decimal
    ) -> Decimal:
        """Calculate total liquidity within percentage range of mid price"""
        if mid_price == 0:
            return Decimal('0')
        
        lower_bound = mid_price * (1 - pct_range)
        upper_bound = mid_price * (1 + pct_range)
        
        bid_depth = sum(
            level.amount for level in snapshot.bids
            if level.price >= lower_bound
        )
        ask_depth = sum(
            level.amount for level in snapshot.asks
            if level.price <= upper_bound
        )
        
        return bid_depth + ask_depth
    
    def _calculate_market_depth_score(
        self,
        bid_liquidity: Decimal,
        ask_liquidity: Decimal,
        depth_1pct: Decimal,
        unique_buyers: int,
        unique_sellers: int,
        bid_concentration: Decimal,
        ask_concentration: Decimal
    ) -> Decimal:
        """
        Calculate composite market depth score (0-100).
        
        Principle 12: Single implementation of score calculation
        """
        total_liq = float(bid_liquidity + ask_liquidity)
        liq_score = min(total_liq / 10000, 1.0) * 30
        
        depth_score = min(float(depth_1pct) / 5000, 1.0) * 30
        
        total_traders = unique_buyers + unique_sellers
        participation_score = min(total_traders / 50, 1.0) * 20
        
        avg_concentration = (float(bid_concentration) + float(ask_concentration)) / 2
        concentration_score = max(0, (100 - avg_concentration) / 100) * 20
        
        total_score = Decimal(str(
            liq_score + depth_score + participation_score + concentration_score
        ))
        
        return total_score
    
    async def _count_unique_traders(self, asset_code: str) -> Tuple[int, int]:
        """Count unique buying and selling accounts"""
        try:
            query = """
            SELECT 
                COUNT(DISTINCT CASE WHEN total_buy_orders > 0 THEN account_id END) as buyers,
                COUNT(DISTINCT CASE WHEN total_sell_orders > 0 THEN account_id END) as sellers
            FROM ubec_main.account_order_positions
            WHERE asset_code = $1
            """
            
            result = await self.db_manager.fetch_one(query, (asset_code,))
            
            if result:
                return result['buyers'] or 0, result['sellers'] or 0
            
            return 0, 0
            
        except Exception as e:
            self.logger.warning(f"Could not count traders: {e}")
            return 0, 0
    
    # ==================== BACKGROUND SYNC ====================
    
    async def _background_orderbook_sync(self):
        """
        Background task to periodically sync order book data.
        
        Principle 5: Async background task
        """
        self.logger.info("Starting background sync task")
        
        while self._initialized:
            try:
                # Track operation
                self._last_sync_time = datetime.now()
                self._sync_count += 1
                
                # Sync all UBEC tokens
                for token in TokenCode:
                    try:
                        await self.fetch_orderbook_snapshot(token.value, use_cache=False)
                        await asyncio.sleep(2)  # Small delay between tokens
                    except Exception as e:
                        self.logger.error(f"Sync error for {token.value}: {e}")
                
                # Wait for next sync interval
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Background sync cancelled")
                break
            except Exception as e:
                self._error_count += 1
                self._last_error = str(e)
                self._last_error_time = datetime.now()
                self.logger.error(f"Background sync error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    # ==================== LIFECYCLE CLEANUP ====================
    
    async def close(self):
        """
        Cleanup and close connections.
        
        Principle 5: Async cleanup operation.
        """
        if not self._initialized:
            return
        
        self._initialized = False
        
        # Cancel background task
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        # Clear cache
        self.clear_cache()
        
        self.logger.info("✓ Order book service closed")


# ==================== SERVICE FACTORY ====================
# Principle 2: Service Pattern - Factory for instantiation

async def create_orderbook_service(
    db_manager,
    stellar_client,
    issuer_address: str,
    **kwargs
) -> UBECOrderBookService:
    """
    Factory function to create order book service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Changed to async to allow for future async initialization if needed.
    
    Principle 2: Service pattern with factory function.
    Principle 3: Dependencies injected via service registry.
    
    Args:
        db_manager: Database manager with async support
        stellar_client: Stellar ServerAsync client
        issuer_address: UBEC token issuer address
        **kwargs: Additional configuration options:
            - rate_limiter: Optional rate limiter
            - cache_ttl: Cache TTL in seconds (default: 60)
            - sync_interval: Sync interval in seconds (default: 300)
    
    Returns:
        UBECOrderBookService: Initialized service instance
        
    Raises:
        ValueError: If required parameters are missing
        OrderBookException: If initialization fails
    
    Example:
        >>> service = await create_orderbook_service(
        ...     db_manager=db,
        ...     stellar_client=stellar,
        ...     issuer_address='GDPNB7S3...',
        ...     cache_ttl=120
        ... )
        >>> await service.initialize()
        >>> health = await service.health_check()
    """
    # Validate required parameters
    if not issuer_address:
        raise ValueError("issuer_address is required")
    
    # Create service instance
    service = UBECOrderBookService(
        db_manager=db_manager,
        stellar_client=stellar_client,
        issuer_address=issuer_address,
        rate_limiter=kwargs.get('rate_limiter'),
        cache_ttl=kwargs.get('cache_ttl', 60),
        sync_interval=kwargs.get('sync_interval', 300)
    )
    
    # Note: Caller must call initialize() after creation
    # This allows for flexible initialization timing
    
    return service


# ==================== MODULE EXPORTS ====================
# Principle 1: Modular Design - Clear public interface

__all__ = [
    # Enums
    'TokenCode',
    'ElementType',
    'OrderSide',
    
    # Data models
    'OrderBookLevel',
    'OrderBookSnapshot',
    'AccountOrder',
    'AccountOrderPosition',
    'MarketDepthMetrics',
    
    # Service
    'UBECOrderBookService',
    'create_orderbook_service',
    
    # Exceptions
    'OrderBookException',
    
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
        "  from ubec_orderbook_service import create_orderbook_service\n"
        "  service = await create_orderbook_service(db_manager, stellar_client, issuer)\n"
        "  await service.initialize()\n"
        "  health = await service.health_check()\n"
        "  await service.close()\n\n"
        "Version 2.2.0 - Standardized Health Check Pattern:\n"
        "  - Uses ServiceHealthCheck.api_dependent_health() utility\n"
        "  - Implements Principle #12: Method Singularity\n"
        "  - Consistent health checks across all services\n"
        "  - Enhanced background task monitoring\n"
        "  - Cache validity tracking with TTL awareness\n"
        "  - Cleaner, more maintainable code\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
