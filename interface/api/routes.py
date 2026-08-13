"""
API Routes v1.4.0 - Backend API v2.5.8 Compatibility
====================================================

Frontend API routes that proxy to backend protocol server.

NEW IN v1.4.0 - TOKEN AUDIT v2.5.8 SUPPORT:
- Total supply now includes liquidity pool reserves
- Stewardship accounts include per-account LP breakdown
- New summary fields: total_in_accounts, total_in_liquidity_pools
- LP summary structure changed for detailed breakdown

MAINTAINED v1.3.0 - LIQUIDITY POOLS:
- /liquidity-pools - Get all UBEC liquidity pools
- /liquidity-pools?token_code=UBEC - Filter by specific token

MAINTAINED v1.2.0 - TOKEN AUDIT:
- /token-audit - Get UBEC token audit (default)
- /token-audit/{token_code} - Get specific token audit (UBEC, UBECrc, UBECgpi, UBECtt)

MAINTAINED v1.1.1 - TRANSACTIONS v2.5.2:
- /transactions/recent now returns operation-level details
- Includes trade_summary for DEX operations
- Full operation array per transaction

MAINTAINED v1.1.0 - BBOX ENDPOINTS:
- /bioregions/{bioregion_id}/bbox - Get bioregion bounding box for map zoom
- /ecoregions/{eco_id}/bbox - Get ecoregion bounding box for map zoom
- /watersheds/{feow_id}/bbox - Get watershed bounding box for map zoom

This module implements:
    - Principle #3: Service pattern with centralized execution
    - Principle #5: Strict async operations
    - Principle #8: No duplicate configuration

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.backend_client import BackendAPIClient, get_backend_client
from config.settings import settings

logger = logging.getLogger(__name__)

# Create API router (prefix is added in main_web.py)
router = APIRouter(tags=["api"])

# ========================================================================
# TOKEN ENDPOINTS
# ========================================================================

@router.get("/tokens", response_class=JSONResponse, summary="Get all tokens")
async def get_all_tokens(
    client: BackendAPIClient = Depends(get_backend_client)
) -> List[Dict]:
    """
    Get information about all four UBEC tokens.
    
    Returns:
        List of token objects for UBEC, UBECrc, UBECgpi, and UBECtt
    """
    try:
        tokens = await client.get_all_tokens()
        return tokens
    except Exception as e:
        logger.error(f"Error fetching tokens: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch token data")


@router.get("/tokens/{token_code}", response_class=JSONResponse, summary="Get specific token")
async def get_token_by_code(
    token_code: str,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get detailed information about a specific token.
    
    Path Parameters:
        - token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
    
    Returns:
        Token object with details
    """
    try:
        token = await client.get_token_by_code(token_code.upper())
        return token
    except Exception as e:
        logger.error(f"Error fetching token {token_code}: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch token data")


@router.get("/tokens/{token_code}/analysis", response_class=JSONResponse, summary="Get token analysis")
async def get_token_analysis(
    token_code: str,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get detailed analysis for a specific token.
    
    Path Parameters:
        - token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
    
    Returns:
        Analysis object with supply metrics, distribution stats, holder metrics, velocity
    """
    try:
        analysis = await client.get_token_analysis(token_code.upper())
        return analysis
    except Exception as e:
        logger.error(f"Error fetching token analysis for {token_code}: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch token analysis")


# ========================================================================
# NETWORK ENDPOINTS
# ========================================================================

@router.get("/network", response_class=JSONResponse, summary="Get network stats")
@router.get("/network-status", response_class=JSONResponse, summary="Get network status")
async def get_network_stats(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get overall network statistics and health.
    
    Returns:
        Network stats including participant count, bioregion count, 
        transaction count, Ubuntu alignment scores, and health status
    """
    try:
        stats = await client.get_network_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching network stats: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch network statistics")


# ========================================================================
# ACCOUNT ENDPOINTS
# ========================================================================

@router.get("/accounts", response_class=JSONResponse, summary="Get accounts list")
async def get_accounts(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get list of accounts with basic information.
    
    Query Parameters:
        - limit: Maximum number of accounts to return (default 100, max 1000)
        - offset: Number of accounts to skip (for pagination)
    
    Returns:
        List of accounts with pagination info
    """
    try:
        accounts = await client.get_accounts(limit=limit, offset=offset)
        return accounts
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch accounts")


@router.get("/accounts/{account_id}", response_class=JSONResponse, summary="Get account details")
async def get_account_details(
    account_id: str,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get detailed information for a specific account.
    
    Path Parameters:
        - account_id: Stellar account ID
    
    Returns:
        Account details with balances, Ubuntu scores, and network position
    """
    try:
        account = await client.get_account_details(account_id)
        return account
    except Exception as e:
        logger.error(f"Error fetching account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch account details")


# ========================================================================
# HOLONIC ENDPOINTS
# ========================================================================

@router.get("/holonic-scores", response_class=JSONResponse, summary="Get holonic scores")
async def get_holonic_scores(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get holonic scoring metrics including Ubuntu principle scores.
    
    Returns:
        Holonic scores including diversity, reciprocity, mutualism, regeneration
    """
    try:
        scores = await client.get_holonic_scores()
        return scores
    except Exception as e:
        logger.error(f"Error fetching holonic scores: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch holonic scores")


# ========================================================================
# TRANSACTION ENDPOINTS
# ========================================================================

@router.get("/transactions/recent", response_class=JSONResponse, summary="Get recent transactions")
async def get_recent_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    asset_code: Optional[str] = Query(None, description="Filter by UBEC token (UBEC, UBECrc, UBECgpi, UBECtt)"),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get recent transactions with operation-level details.
    
    Query Parameters:
        - limit: Number of transactions (default 20, max 100)
        - asset_code: Optional filter by token (case-insensitive)
    
    Returns:
        List of transactions with operations array including:
        - type, asset_code, amount, from_account, to_account
        - trade_summary for DEX operations (e.g., "100 UBEC → 50 UBECrc")
    """
    try:
        transactions = await client.get_recent_transactions(
            limit=limit, 
            asset_code=asset_code.upper() if asset_code else None
        )
        return transactions
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch transactions")


# ========================================================================
# DISTRIBUTION ENDPOINTS
# ========================================================================

@router.get("/distribution", response_class=JSONResponse, summary="Get distribution stats")
@router.get("/distributions", response_class=JSONResponse, summary="Get distribution stats (alias)")
async def get_distribution_stats(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get token distribution statistics.
    
    Returns:
        Distribution statistics including:
        - total_distributed: Total tokens distributed
        - distribution_by_category: Breakdown by category
        - compliance_status: Compliance with distribution model
    """
    try:
        stats = await client.get_distribution_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching distribution stats: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch distribution statistics")


@router.get("/token-audit", response_class=JSONResponse, summary="Get token audit (default UBEC)")
@router.get("/token-audit/{token_code}", response_class=JSONResponse, summary="Get token audit")
async def get_token_audit(
    token_code: str = "UBEC",
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get comprehensive token audit data for transparency reporting.
    
    UPDATED v1.4.0 - Backend API v2.5.8 Compatibility:
    - Total supply now includes liquidity pool reserves
    - Stewardship accounts include per-account LP breakdown (breakdown.direct, breakdown.lp_positions)
    - New summary fields: total_in_accounts, total_in_liquidity_pools
    - LP summary changed from stewardship_lp_unlocked/locked to stewardship_lp_by_account
    
    Path Parameters:
        - token_code: Token to audit (UBEC, UBECrc, UBECgpi, UBECtt) - default UBEC
    
    Returns:
        Comprehensive audit data including:
        - token: Token info (code, element, ubuntu_principle, issuer, total_tokens_issued)
        - summary: 
            - total_issued (now includes LP reserves)
            - total_in_accounts (NEW v2.5.8)
            - total_in_liquidity_pools (NEW v2.5.8)
            - total_distributed
            - general_distribution_pct, stewardship_pct, administration_pct
            - distribution_model
        - general_distribution: 65% category with accounts and projects
        - token_ecosystem_stewardship: 30% category with accounts
            - Each account now includes 'breakdown' dict with:
              - direct: Direct account balance
              - lp_positions: Balance in liquidity pools
            - liquidity_pools_summary:
              - total_locked_in_all_pools
              - stewardship_total_in_lp
              - stewardship_lp_by_account: {management, infrastructure, liquidity}
        - administration: 5% category with accounts
        - compliance: Compliance status indicators
        - disclaimer: Legal disclaimer text
    """
    try:
        audit = await client.get_token_audit(token_code=token_code)
        return audit
    except Exception as e:
        logger.error(f"Error fetching token audit: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch token audit")


@router.get("/liquidity-pools", response_class=JSONResponse, summary="Get liquidity pools")
async def get_liquidity_pools(
    token_code: Optional[str] = Query(None, description="Filter by token (UBEC, UBECrc, UBECgpi, UBECtt)"),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get UBEC liquidity pool details from Stellar DEX.
    
    Query Parameters:
        - token_code: Optional filter by token (case-insensitive)
    
    Returns:
        - pools: Array of liquidity pool objects with:
          - id: Stellar liquidity pool ID (64-byte hex)
          - pair: Human-readable pair name (e.g., UBEC/XLM)
          - token_code: Which UBEC token is in this pool
          - element: Element classification (air/water/earth/fire)
          - ubec_position: Whether UBEC is asset_a or asset_b
          - asset_a, asset_b: Asset details (code, issuer)
          - reserves: Current reserve amounts (asset_a, asset_b)
          - total_shares: Total pool shares issued
          - balance: Total UBEC tokens in pool
          - fee_bp: Trading fee in basis points
          - trustline_count: Number of trustlines
          - participant_count: Number of LP owners
          - last_modified_at: Last update timestamp
        - summary: Aggregate statistics
          - total_pools: Total number of pools
          - total_value_locked: Sum of UBEC in all pools
          - pools_by_token: Count per token type
        - filter_applied: Token filter if applied
        - timestamp: Response timestamp
    """
    try:
        pools = await client.get_liquidity_pools(
            token_code=token_code.upper() if token_code else None
        )
        return pools
    except Exception as e:
        logger.error(f"Error fetching liquidity pools: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch liquidity pools")


# ========================================================================
# BIOREGION ENDPOINTS
# ========================================================================

@router.get("/bioregions", response_class=JSONResponse, summary="Get bioregions")
async def get_bioregions(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get list of bioregions with health metrics.
    
    Returns:
        List of bioregions with health scores and pagination info
    """
    try:
        bioregions = await client.get_bioregions()
        return bioregions
    except Exception as e:
        logger.error(f"Error fetching bioregions: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch bioregions")


@router.get("/bioregion-boundaries", response_class=JSONResponse, summary="Get bioregion boundaries")
async def get_bioregion_boundaries(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get bioregion boundaries with GeoJSON geometries.
    
    Returns:
        List of bioregion boundaries with full metadata and geometries
    """
    try:
        boundaries = await client.get_bioregion_boundaries()
        return boundaries
    except Exception as e:
        logger.error(f"Error fetching bioregion boundaries: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch bioregion boundaries")


@router.get("/bioregions/{bioregion_id}/bbox", response_class=JSONResponse, summary="Get bioregion bbox")
async def get_bioregion_bbox(
    bioregion_id: int,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get bounding box for a specific bioregion.
    
    Path Parameters:
        - bioregion_id: Bioregion GID
    
    Returns:
        Bounding box with min_x, min_y, max_x, max_y (EPSG:3857 meters)
        and centroid coordinates for map centering
    """
    try:
        bbox = await client.get_bioregion_bbox(bioregion_id)
        return bbox
    except Exception as e:
        logger.error(f"Error fetching bioregion bbox: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch bioregion bounding box")


@router.get("/points-of-interest", response_class=JSONResponse, summary="Get points of interest")
async def get_points_of_interest(
    poi_type: Optional[str] = Query(None, description="Filter by POI type"),
    bioregion_gid: Optional[int] = Query(None, description="Filter by bioregion"),
    visibility: Optional[str] = Query(None, description="Filter by visibility"),
    limit: int = Query(default=100, ge=1, le=500),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get points of interest (farms, community centers, landmarks, resources).
    
    Query Parameters:
        - poi_type: Filter by type (farm, community_center, resource, landmark)
        - bioregion_gid: Filter by bioregion
        - visibility: Filter by visibility (public, bioregion_only, private)
        - limit: Maximum POIs to return (default 100, max 500)
    
    Returns:
        List of POIs with GeoJSON point geometries and metadata
    """
    try:
        pois = await client.get_points_of_interest(
            poi_type=poi_type,
            bioregion_gid=bioregion_gid,
            visibility=visibility,
            limit=limit
        )
        return pois
    except Exception as e:
        logger.error(f"Error fetching POIs: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch points of interest")


# ========================================================================
# GEOGRAPHIC ENDPOINTS
# ========================================================================

@router.get("/ecoregions", response_class=JSONResponse, summary="Get ecoregions")
async def get_ecoregions(
    limit: int = Query(default=50, ge=1, le=500),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get ecoregion data from WWF Ecoregions 2017.
    
    Query Parameters:
        - limit: Maximum ecoregions to return (default 50, max 500)
    
    Returns:
        List of ecoregions with GeoJSON geometries and metadata
    """
    try:
        ecoregions = await client.get_ecoregions(limit=limit)
        return ecoregions
    except Exception as e:
        logger.error(f"Error fetching ecoregions: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch ecoregions")


@router.get("/ecoregions/{eco_id}/bbox", response_class=JSONResponse, summary="Get ecoregion bbox")
async def get_ecoregion_bbox(
    eco_id: int,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get bounding box for a specific ecoregion.
    
    Path Parameters:
        - eco_id: Ecoregion ID
    
    Returns:
        Bounding box with min_x, min_y, max_x, max_y (EPSG:3857 meters)
        and eco_name, biome_name, realm metadata
    """
    try:
        bbox = await client.get_ecoregion_bbox(eco_id)
        return bbox
    except Exception as e:
        logger.error(f"Error fetching ecoregion bbox: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch ecoregion bounding box")


@router.get("/watersheds", response_class=JSONResponse, summary="Get watersheds")
async def get_watersheds(
    limit: int = Query(default=50, ge=1, le=500),
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get watershed data from FEOW HydroSHEDS.
    
    Query Parameters:
        - limit: Maximum watersheds to return (default 50, max 500)
    
    Returns:
        List of watersheds with GeoJSON geometries
    """
    try:
        watersheds = await client.get_watersheds(limit=limit)
        return watersheds
    except Exception as e:
        logger.error(f"Error fetching watersheds: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch watersheds")


@router.get("/watersheds/{feow_id}/bbox", response_class=JSONResponse, summary="Get watershed bbox")
async def get_watershed_bbox(
    feow_id: int,
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Get bounding box for a specific watershed.
    
    Path Parameters:
        - feow_id: FEOW watershed ID
    
    Returns:
        Bounding box with min_x, min_y, max_x, max_y (EPSG:3857 meters)
        and area_sqkm, name metadata
    """
    try:
        bbox = await client.get_watershed_bbox(feow_id)
        return bbox
    except Exception as e:
        logger.error(f"Error fetching watershed bbox: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch watershed bounding box")


# ========================================================================
# HEALTH ENDPOINT
# ========================================================================

@router.get("/health", response_class=JSONResponse, summary="API health check")
async def health_check(
    client: BackendAPIClient = Depends(get_backend_client)
) -> Dict:
    """
    Check API gateway health and backend connectivity.
    
    Returns:
        Health status with timestamp
    """
    try:
        health = await client.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "message": "Backend connectivity issue",
            "timestamp": datetime.now().isoformat()
        }
