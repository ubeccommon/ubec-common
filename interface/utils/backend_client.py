"""
Backend API Client v1.6.0 - Backend API v2.7.0 Compatibility
============================================================

HTTP client for communicating with UBEC backend API service.
Provides async methods for all API endpoints with intelligent caching.

NEW IN v1.6.0 - ENHANCED HOLONIC-SCORES (Backend v2.7.0):
- get_holonic_scores() now supports include_accounts parameter
- Added limit, offset, category parameters for pagination/filtering
- Returns 5 holonic dimension scores per account (visualization-ready)
- Returns 4 Ubuntu principle scores per account (element-specific)
- Backward compatible: default behavior unchanged

NEW IN v1.5.0 - BACKEND API v2.6.0 COMPLIANCE:
- Backend removed /api/v1/network-status alias (uses /api/v1/network only)
- get_network_status() still works (calls get_network_stats() internally)
- Complies with Principle #12 (Method Singularity)

FIX IN v1.4.3:
- Fixed get_all_tokens() to handle both raw list and wrapped dict responses
- Gateway returns raw list, backend returns {"tokens": [...]}

FIX IN v1.4.2:
- Added get_network_status() alias for main_web.py compatibility
- Updated get_holonic_scores() to accept optional limit parameter

FIX IN v1.4.1:
- Fixed URL path: removed /api prefix (Gateway uses /v1 directly)
- Frontend BACKEND_API_URL=https://api.ubec.network now works correctly

NEW IN v1.4.0 - BACKEND API v2.5.8 SUPPORT:
- Updated docstrings for token audit v2.5.8 structure
- Total supply now includes LP reserves
- Stewardship accounts include per-account LP breakdown

This module implements:
    - Principle #3: Service pattern with centralized execution
    - Principle #5: Strict async operations
    - Principle #8: No duplicate configuration
    - Principle #9: Integrated rate limiting (via caching)
    - Principle #12: Method Singularity (no duplicate methods)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp

from config.settings import settings

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """
    Async HTTP client for UBEC backend API.
    
    Provides cached access to all backend API endpoints with automatic
    session management and error handling.
    
    Features:
    - Async/await for all operations
    - Response caching with configurable TTL
    - Connection pooling via aiohttp
    - Automatic session lifecycle management
    - Comprehensive error handling
    
    Example:
        async with BackendAPIClient() as client:
            tokens = await client.get_all_tokens()
            audit = await client.get_token_audit("UBEC")
    
    Attributes:
        base_url: Backend API base URL
        timeout: Request timeout in seconds
        cache: In-memory response cache
        cache_times: Cache entry timestamps
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the backend API client.
        
        Args:
            base_url: Override backend API URL (default from settings)
            timeout: Request timeout in seconds (default 30)
        """
        self.base_url = base_url or settings.BACKEND_API_URL
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Simple in-memory cache
        self._cache: Dict[str, Any] = {}
        self._cache_times: Dict[str, datetime] = {}
        
        logger.info(f"BackendAPIClient initialized with base URL: {self.base_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create aiohttp session.
        
        Returns:
            Active aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def _is_cache_valid(self, key: str, ttl: int) -> bool:
        """
        Check if cached response is still valid.
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds
        
        Returns:
            True if cache entry exists and is not expired
        """
        if key not in self._cache_times:
            return False
        age = (datetime.now() - self._cache_times[key]).total_seconds()
        return age < ttl
    
    async def _cached_get(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        ttl: int = 30
    ) -> Dict:
        """
        GET request with caching.
        
        Args:
            endpoint: API endpoint path (e.g., "/v1/tokens")
            params: Optional query parameters
            ttl: Cache TTL in seconds (default 30)
        
        Returns:
            JSON response as dictionary
        
        Raises:
            HTTPException: If request fails
        """
        # Build cache key
        cache_key = f"{endpoint}:{str(params)}"
        
        # Check cache
        if self._is_cache_valid(cache_key, ttl):
            logger.debug(f"Cache hit for {endpoint}")
            return self._cache[cache_key]
        
        # Make request
        session = await self._get_session()
        # Note: API Gateway uses /v1 directly, no /api prefix needed
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Cache response
                self._cache[cache_key] = data
                self._cache_times[cache_key] = datetime.now()
                
                logger.debug(f"Fetched {endpoint} from backend")
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Backend API error for {endpoint}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            raise
    
    # ========================================================================
    # TOKEN ENDPOINTS
    # ========================================================================
    
    async def get_all_tokens(self) -> List[Dict]:
        """
        Get information about all four UBEC tokens.
        
        Returns:
            List of token objects (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Note:
            Handles both response formats:
            - Raw list: [{...}, {...}] (from gateway)
            - Wrapped dict: {"tokens": [{...}]} (from backend direct)
        """
        result = await self._cached_get("/v1/tokens", ttl=60)
        # Handle both raw list and wrapped dict formats
        if isinstance(result, list):
            return result
        return result.get('tokens', [])
    
    async def get_token_by_code(self, token_code: str) -> Dict:
        """
        Get detailed information about a specific token.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
        
        Returns:
            Token object with details
        """
        return await self._cached_get(f"/v1/tokens/{token_code.upper()}", ttl=60)
    
    async def get_token_analysis(self, token_code: str) -> Dict:
        """
        Get detailed analysis for a specific token.
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
        
        Returns:
            Analysis object with supply, distribution, holder metrics
        """
        return await self._cached_get(f"/v1/tokens/{token_code.upper()}/analysis", ttl=60)
    
    # ========================================================================
    # NETWORK ENDPOINTS
    # ========================================================================
    
    async def get_network_stats(self) -> Dict:
        """
        Get overall network statistics and health.
        
        Returns:
            Network stats including participant count, bioregions, 
            transactions, Ubuntu scores, and health status
        """
        return await self._cached_get("/v1/network", ttl=30)
    
    async def get_network_status(self) -> Dict:
        """
        Alias for get_network_stats (backward compatibility with main_web.py).
        
        DEPRECATED in v1.5.0: Backend removed /api/v1/network-status endpoint.
        This alias still works because it calls get_network_stats() internally.
        New code should use get_network_stats() directly.
        
        Returns:
            Network stats including participant count, bioregions, 
            transactions, Ubuntu scores, and health status
        """
        return await self.get_network_stats()
    
    # ========================================================================
    # ACCOUNT ENDPOINTS
    # ========================================================================
    
    async def get_accounts(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        Get list of accounts with basic information.
        
        Args:
            limit: Maximum accounts to return (default 100)
            offset: Pagination offset
        
        Returns:
            Accounts list with pagination info
        """
        return await self._cached_get(
            "/v1/accounts", 
            params={"limit": limit, "offset": offset},
            ttl=30
        )
    
    async def get_account_details(self, account_id: str) -> Dict:
        """
        Get detailed information for a specific account.
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            Account details with balances and Ubuntu scores
        """
        return await self._cached_get(f"/v1/accounts/{account_id}", ttl=30)
    
    # ========================================================================
    # HOLONIC ENDPOINTS
    # ========================================================================
    
    async def get_holonic_scores(
        self, 
        include_accounts: bool = False,
        limit: int = 100,
        offset: int = 0,
        category: str = None
    ) -> Dict:
        """
        Get holonic scoring metrics with optional individual account data.
        
        NEW IN v2.7.0:
        - include_accounts=True returns per-account dimension scores
        - Returns 5 holonic dimensions + 4 Ubuntu principle scores per account
        - Supports pagination and category filtering
        
        Args:
            include_accounts: Include individual account evaluations (default False)
            limit: Max accounts when include_accounts=True (default 100, max 500)
            offset: Pagination offset (default 0)
            category: Filter by holonic category (Observer, Participant, Contributor, Integrator, Exemplar)
        
        Returns:
            When include_accounts=False (default):
                - ubuntu_principles: Aggregate scores
                - account_count: Total evaluated accounts
            
            When include_accounts=True:
                - accounts: Array with per-account scores
                - summary: Category distribution, statistics
                - pagination: Limit, offset, total, has_more
        """
        params = {}
        if include_accounts:
            params["include_accounts"] = "true"
            params["limit"] = min(max(1, limit), 500)
            params["offset"] = max(0, offset)
        if category:
            params["category"] = category
        return await self._cached_get("/v1/holonic-scores", params=params if params else None, ttl=60)
    
    # ========================================================================
    # TRANSACTION ENDPOINTS
    # ========================================================================
    
    async def get_recent_transactions(
        self, 
        limit: int = 20,
        asset_code: Optional[str] = None
    ) -> Dict:
        """
        Get recent transactions with operation details.
        
        Args:
            limit: Number of transactions (default 20)
            asset_code: Optional filter by token
        
        Returns:
            Transactions list with operations array
        """
        params = {"limit": limit}
        if asset_code:
            params["asset_code"] = asset_code.upper()
        return await self._cached_get("/v1/transactions/recent", params=params, ttl=15)
    
    # ========================================================================
    # DISTRIBUTION ENDPOINTS
    # ========================================================================
    
    async def get_distribution_stats(self) -> Dict:
        """
        Get token distribution statistics.
        
        Returns:
            Distribution statistics including tokens and compliance status
        """
        return await self._cached_get("/v1/distribution", ttl=60)
    
    async def get_token_audit(self, token_code: str = "UBEC") -> Dict:
        """
        Get comprehensive token audit data for transparency reporting.
        
        UPDATED v1.4.0 - Backend API v2.5.8 Structure:
        
        The response now includes:
        - token.total_tokens_issued: Includes LP reserves
        - summary.total_in_accounts: Balance in regular accounts
        - summary.total_in_liquidity_pools: Balance locked in LPs
        - token_ecosystem_stewardship.accounts[].breakdown:
            - direct: Direct account balance
            - lp_positions: Balance in liquidity pools
        - token_ecosystem_stewardship.liquidity_pools_summary:
            - total_locked_in_all_pools: All UBEC in all pools
            - stewardship_total_in_lp: Stewardship accounts' LP positions
            - stewardship_lp_by_account: {management, infrastructure, liquidity}
        
        Args:
            token_code: Token to audit (UBEC, UBECrc, UBECgpi, UBECtt)
        
        Returns:
            Dictionary with token info, summary, distribution categories, compliance
        """
        return await self._cached_get(f"/v1/token-audit/{token_code.upper()}", ttl=60)
    
    async def get_liquidity_pools(self, token_code: str = None) -> Dict:
        """
        Get liquidity pool information for UBEC tokens.
        
        Args:
            token_code: Optional filter by token
        
        Returns:
            Dictionary with pools list and summary including:
            - pools[].id, pair, token_code, element
            - pools[].ubec_position, asset_a, asset_b
            - pools[].reserves, total_shares, balance
            - pools[].fee_bp, trustline_count, participant_count
            - summary.total_pools, total_value_locked, pools_by_token
        """
        if token_code:
            return await self._cached_get(f"/v1/liquidity-pools?token_code={token_code.upper()}", ttl=60)
        return await self._cached_get("/v1/liquidity-pools", ttl=60)
    
    # ========================================================================
    # BIOREGION ENDPOINTS
    # ========================================================================
    
    async def get_bioregions(self) -> Dict:
        """
        Get list of bioregions with health metrics.
        
        Returns:
            Bioregions list with health scores
        """
        return await self._cached_get("/v1/bioregions", ttl=60)
    
    async def get_bioregion_boundaries(self) -> Dict:
        """
        Get bioregion boundaries with GeoJSON geometries.
        
        Returns:
            Boundaries list with full metadata
        """
        return await self._cached_get("/v1/bioregion-boundaries", ttl=120)
    
    async def get_bioregion_bbox(self, bioregion_id: int) -> Dict:
        """
        Get bounding box for a specific bioregion.
        
        Args:
            bioregion_id: Bioregion GID
        
        Returns:
            Bbox with min_x, min_y, max_x, max_y (EPSG:3857)
        """
        return await self._cached_get(f"/v1/bioregions/{bioregion_id}/bbox", ttl=300)
    
    async def get_points_of_interest(
        self,
        poi_type: Optional[str] = None,
        bioregion_gid: Optional[int] = None,
        visibility: Optional[str] = None,
        limit: int = 100
    ) -> Dict:
        """
        Get points of interest with optional filters.
        
        Args:
            poi_type: Filter by POI type
            bioregion_gid: Filter by bioregion
            visibility: Filter by visibility
            limit: Maximum POIs to return
        
        Returns:
            POIs list with GeoJSON geometries
        """
        params = {"limit": limit}
        if poi_type:
            params["poi_type"] = poi_type
        if bioregion_gid:
            params["bioregion_gid"] = bioregion_gid
        if visibility:
            params["visibility"] = visibility
        return await self._cached_get("/v1/points-of-interest", params=params, ttl=60)
    
    # ========================================================================
    # GEOGRAPHIC ENDPOINTS
    # ========================================================================
    
    async def get_ecoregions(self, limit: int = 50) -> Dict:
        """
        Get ecoregion data from WWF Ecoregions 2017.
        
        Args:
            limit: Maximum ecoregions to return
        
        Returns:
            Ecoregions list with GeoJSON geometries
        """
        return await self._cached_get("/v1/ecoregions", params={"limit": limit}, ttl=120)
    
    async def get_ecoregion_bbox(self, eco_id: int) -> Dict:
        """
        Get bounding box for a specific ecoregion.
        
        Args:
            eco_id: Ecoregion ID
        
        Returns:
            Bbox with min_x, min_y, max_x, max_y (EPSG:3857)
        """
        return await self._cached_get(f"/v1/ecoregions/{eco_id}/bbox", ttl=300)
    
    async def get_watersheds(self, limit: int = 50) -> Dict:
        """
        Get watershed data from FEOW HydroSHEDS.
        
        Args:
            limit: Maximum watersheds to return
        
        Returns:
            Watersheds list with GeoJSON geometries
        """
        return await self._cached_get("/v1/watersheds", params={"limit": limit}, ttl=120)
    
    async def get_watershed_bbox(self, feow_id: int) -> Dict:
        """
        Get bounding box for a specific watershed.
        
        Args:
            feow_id: FEOW watershed ID
        
        Returns:
            Bbox with min_x, min_y, max_x, max_y (EPSG:3857)
        """
        return await self._cached_get(f"/v1/watersheds/{feow_id}/bbox", ttl=300)
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    async def health_check(self) -> Dict:
        """
        Check API health.
        
        Returns:
            Health status object
        """
        return await self._cached_get("/v1/health", ttl=5)


# ========================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ========================================================================

# Global client instance
_client: Optional[BackendAPIClient] = None


async def get_backend_client() -> BackendAPIClient:
    """
    Get or create global backend client instance.
    
    Returns:
        BackendAPIClient instance
    """
    global _client
    if _client is None:
        _client = BackendAPIClient()
    return _client


async def close_backend_client():
    """Close global backend client instance."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None


# ========================================================================
# TESTING
# ========================================================================

async def test_client():
    """Test the API client against all available endpoints."""
    print("=" * 70)
    print("UBEC Backend API Client Test Suite")
    print("=" * 70)
    
    client = BackendAPIClient()
    
    try:
        # Test 1: Health check
        print("\n[1/12] Testing health check...")
        health = await client.health_check()
        print(f"✓ Health status: {health.get('status', 'unknown')}")
        
        # Test 2: Network stats
        print("\n[2/12] Testing network stats...")
        network = await client.get_network_stats()
        print(f"✓ Participants: {network.get('participants', {}).get('total', 0)}")
        
        # Test 3: All tokens
        print("\n[3/12] Testing token list...")
        tokens = await client.get_all_tokens()
        print(f"✓ Found {len(tokens)} tokens")
        
        # Test 4: Token analysis
        print("\n[4/12] Testing token analysis...")
        analysis = await client.get_token_analysis("UBEC")
        supply = analysis.get('analysis', {}).get('supply', {}).get('total', 0)
        print(f"✓ UBEC total supply: {supply:,.2f}")
        
        # Test 5: Holonic scores
        print("\n[5/12] Testing holonic scores...")
        scores = await client.get_holonic_scores()
        avg_score = scores.get('average_ubuntu_score', 0)
        print(f"✓ Average Ubuntu score: {avg_score:.2f}")
        
        # Test 6: Bioregions
        print("\n[6/12] Testing bioregions...")
        bioregions = await client.get_bioregions()
        count = len(bioregions.get('bioregions', []))
        print(f"✓ Found {count} bioregions")
        
        # Test 7: Recent transactions
        print("\n[7/12] Testing recent transactions...")
        transactions = await client.get_recent_transactions(limit=5)
        tx_count = len(transactions.get('transactions', []))
        print(f"✓ Retrieved {tx_count} transactions")
        
        # Test 8: Distribution stats
        print("\n[8/12] Testing distribution stats...")
        distribution = await client.get_distribution_stats()
        print(f"✓ Got distribution compliance data")
        
        # Test 9: Token audit (v2.5.8 enhanced)
        print("\n[9/12] Testing token audit (v2.5.8)...")
        try:
            audit = await client.get_token_audit("UBEC")
            summary = audit.get('summary', {})
            total_issued = summary.get('total_issued', 0)
            in_accounts = summary.get('total_in_accounts', 0)
            in_pools = summary.get('total_in_liquidity_pools', 0)
            print(f"✓ Total issued: {total_issued:,.2f}")
            print(f"  └ In accounts: {in_accounts:,.2f}")
            print(f"  └ In LP pools: {in_pools:,.2f}")
            
            # Check v2.5.8 stewardship breakdown
            stewardship = audit.get('token_ecosystem_stewardship', {})
            accounts = stewardship.get('accounts', [])
            for acc in accounts:
                breakdown = acc.get('breakdown', {})
                if breakdown:
                    print(f"  ✓ {acc.get('purpose')}: direct={breakdown.get('direct', 0):,.2f}, lp={breakdown.get('lp_positions', 0):,.2f}")
        except Exception as e:
            print(f"⚠ Token audit not available: {e}")
        
        # Test 10: Liquidity pools
        print("\n[10/12] Testing liquidity pools...")
        try:
            pools = await client.get_liquidity_pools()
            pool_count = len(pools.get('pools', [])) if pools else 0
            total_locked = pools.get('summary', {}).get('total_value_locked', 0)
            print(f"✓ Found {pool_count} liquidity pools")
            print(f"  └ Total value locked: {total_locked:,.2f}")
        except Exception as e:
            print(f"⚠ Liquidity pools not available: {e}")
        
        # Test 11: Ecoregions
        print("\n[11/12] Testing ecoregions...")
        try:
            ecoregions = await client.get_ecoregions(limit=5)
            eco_count = len(ecoregions.get('ecoregions', []))
            print(f"✓ Retrieved {eco_count} ecoregions")
        except Exception as e:
            print(f"⚠ Ecoregions not available: {e}")
        
        # Test 12: Watersheds
        print("\n[12/12] Testing watersheds...")
        try:
            watersheds = await client.get_watersheds(limit=5)
            ws_count = len(watersheds.get('watersheds', []))
            print(f"✓ Retrieved {ws_count} watersheds")
        except Exception as e:
            print(f"⚠ Watersheds not available: {e}")
        
        print("\n" + "=" * 70)
        print("✓ All tests completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    """Test the client when run directly."""
    asyncio.run(test_client())
