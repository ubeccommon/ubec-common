"""
UBEC API Gateway v1.6.0 - Backend API v2.7.0 Compatibility
==========================================================

API Gateway service that proxies requests to the backend API.
Serves as the public-facing API endpoint at api.ubec.network.

NEW IN v1.6.0 - ENHANCED HOLONIC-SCORES (Backend v2.7.0):
- Added include_accounts parameter for individual account evaluations
- Added limit parameter for pagination (default 100, max 500)
- Added offset parameter for pagination
- Added category parameter to filter by holonic category
- Returns 5 holonic dimension scores per account (visualization-ready)
- Returns 4 Ubuntu principle scores per account (element-specific)
- Enables frontend visualization reports

NEW IN v1.5.0 - ALIAS REMOVAL (Backend v2.7.0 Compliance):
- Removed /v1/network-status alias (use /v1/network only)
- Removed /v1/distributions alias (use /v1/distribution only)
- Complies with Principle #12 (Method Singularity)

Architecture:
    api.ubec.network (this service, port 8002)
        ↓ proxies to (with X-API-Gateway-Key header)
    Backend API (92.205.230.245:8000)

This module implements:
    - Principle #3: Service pattern with centralized execution
    - Principle #5: Strict async operations
    - Principle #10: Separation of concerns (gateway layer)
    - Principle #12: Method Singularity (no duplicate routes)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import aiohttp

# ========================================================================
# CONFIGURATION
# ========================================================================

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://92.205.230.245:8000")
API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY", "")
TIMEOUT = 30

# ========================================================================
# LOGGING
# ========================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log configuration on import
if not API_GATEWAY_KEY:
    logger.warning("API_GATEWAY_KEY not set - backend requests will fail!")
else:
    logger.info(f"API Gateway configured for backend: {BACKEND_API_URL}")

# ========================================================================
# FASTAPI APP
# ========================================================================

app = FastAPI(
    title="UBEC API Gateway",
    description="""
## Ubuntu Bioregional Economic Commons - Public API Gateway

### Base URL
`https://api.ubec.network`

### Available Endpoints (19 total)

**Tokens**
- `GET /v1/tokens` - All UBEC tokens
- `GET /v1/tokens/{code}` - Specific token details
- `GET /v1/tokens/{code}/analysis` - Token analysis

**Network**
- `GET /v1/network` - Network statistics and health

**Accounts**
- `GET /v1/accounts` - Account list with holonic metrics
- `GET /v1/accounts/{account_id}` - Account details

**Analytics**
- `GET /v1/holonic-scores` - Holonic evaluation scores (supports include_accounts=true)
- `GET /v1/transactions/recent` - Recent transactions with operations

**Distribution**
- `GET /v1/distribution` - Distribution compliance
- `GET /v1/token-audit/{code}` - Comprehensive token audit
- `GET /v1/liquidity-pools` - DEX liquidity pools

**Geographic**
- `GET /v1/bioregions` - Bioregion data
- `GET /v1/bioregions/{gid}/bbox` - Bioregion bounding box
- `GET /v1/bioregion-boundaries` - Bioregion boundary geometries
- `GET /v1/points-of-interest` - Points of interest
- `GET /v1/ecoregions` - Ecoregion data
- `GET /v1/ecoregions/{eco_id}/bbox` - Ecoregion bounding box
- `GET /v1/watersheds` - Watershed data
- `GET /v1/watersheds/{feow_id}/bbox` - Watershed bounding box

### Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`
""",
    version="1.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "UBEC DAO Protocol",
        "url": "https://bioregional.ubec.network",
    }
)

# ========================================================================
# MIDDLEWARE
# ========================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ========================================================================
# LIFECYCLE EVENTS
# ========================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Starting UBEC API Gateway v1.5.0")
    logger.info(f"Backend URL: {BACKEND_API_URL}")
    logger.info(f"API Key configured: {'Yes' if API_GATEWAY_KEY else 'NO - WARNING!'}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down UBEC API Gateway")

# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

async def fetch_from_backend(endpoint: str, params: Dict = None) -> Dict:
    """
    Fetch data from backend API with authentication.
    
    Args:
        endpoint: API endpoint path (e.g., "/api/v1/tokens")
        params: Optional query parameters
    
    Returns:
        JSON response from backend
    
    Raises:
        HTTPException: On backend errors or connection issues
    """
    url = f"{BACKEND_API_URL}{endpoint}"
    
    # CRITICAL: Include API Gateway Key for backend authentication
    headers = {
        "X-API-Gateway-Key": API_GATEWAY_KEY,
        "User-Agent": "UBEC-API-Gateway/1.5.0",
        "Accept": "application/json"
    }
    
    logger.debug(f"Backend request: GET {url} params={params}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    logger.error(f"Backend authentication failed for {endpoint} - check API_GATEWAY_KEY")
                    raise HTTPException(
                        status_code=503,
                        detail="Backend authentication failed"
                    )
                elif response.status == 404:
                    logger.warning(f"Backend endpoint not found: {endpoint}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"Endpoint not found: {endpoint}"
                    )
                else:
                    logger.error(f"Backend returned {response.status} for {endpoint}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Backend error: {response.status}"
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Backend connection error for {endpoint}: {e}")
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========================================================================
# ROOT & HEALTH ENDPOINTS
# ========================================================================

@app.get("/", response_class=JSONResponse, include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "UBEC API Gateway",
        "version": "1.5.0",
        "backend_api_version": "2.7.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "health": "/v1/health",
            "network": "/v1/network",
            "tokens": "/v1/tokens",
            "token_audit": "/v1/token-audit/{token_code}",
            "liquidity_pools": "/v1/liquidity-pools",
            "accounts": "/v1/accounts",
            "transactions": "/v1/transactions/recent",
            "bioregions": "/v1/bioregions",
            "ecoregions": "/v1/ecoregions",
            "watersheds": "/v1/watersheds"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_class=JSONResponse, tags=["System"])
async def health():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "ubec-api-gateway",
        "version": "1.5.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/v1/health", response_class=JSONResponse, tags=["System"], summary="Health check")
async def v1_health():
    """Check gateway and backend health."""
    try:
        backend_health = await fetch_from_backend("/health")
        return {
            "gateway_status": "healthy",
            "backend_status": backend_health.get("status", "unknown"),
            "backend_version": "2.7.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Backend health check failed: {e}")
        return {
            "gateway_status": "healthy",
            "backend_status": "unreachable",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ========================================================================
# NETWORK ENDPOINTS
# ========================================================================

@app.get("/v1/network", response_class=JSONResponse, tags=["Network"], summary="Get network stats")
async def get_network_stats():
    """Get network statistics and health."""
    return await fetch_from_backend("/api/v1/network")

# ========================================================================
# TOKEN ENDPOINTS
# ========================================================================

@app.get("/v1/tokens", response_class=JSONResponse, tags=["Tokens"], summary="Get all tokens")
async def get_tokens():
    """Get information about all UBEC tokens."""
    data = await fetch_from_backend("/api/v1/tokens")
    # Handle both formats: {tokens: [...]} or [...]
    if isinstance(data, dict) and "tokens" in data:
        return data["tokens"]
    return data


@app.get("/v1/tokens/{token_code}", response_class=JSONResponse, tags=["Tokens"], summary="Get token details")
async def get_token(token_code: str):
    """Get details for a specific token."""
    data = await fetch_from_backend("/api/v1/tokens")
    tokens = data.get("tokens", data) if isinstance(data, dict) else data
    for token in tokens:
        if token.get("code") == token_code.upper() or token.get("asset_code") == token_code.upper():
            return token
    raise HTTPException(status_code=404, detail=f"Token {token_code} not found")


@app.get("/v1/tokens/{token_code}/analysis", response_class=JSONResponse, tags=["Tokens"], summary="Get token analysis")
async def get_token_analysis(token_code: str):
    """Get detailed analysis for a token."""
    return await fetch_from_backend(f"/api/v1/tokens/{token_code.upper()}/analysis")

# ========================================================================
# ACCOUNT ENDPOINTS
# ========================================================================

@app.get("/v1/accounts", response_class=JSONResponse, tags=["Accounts"], summary="Get accounts")
async def get_accounts(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get list of accounts."""
    return await fetch_from_backend("/api/v1/accounts", {"limit": limit, "offset": offset})


@app.get("/v1/accounts/{account_id}", response_class=JSONResponse, tags=["Accounts"], summary="Get account details")
async def get_account(account_id: str):
    """Get details for a specific account."""
    return await fetch_from_backend(f"/api/v1/accounts/{account_id}")

# ========================================================================
# HOLONIC ENDPOINTS
# ========================================================================

@app.get("/v1/holonic-scores", response_class=JSONResponse, tags=["Holonic"], summary="Get holonic scores")
async def get_holonic_scores(
    include_accounts: bool = Query(default=False, description="Include individual account evaluations"),
    limit: int = Query(default=100, ge=1, le=500, description="Max accounts when include_accounts=true"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    category: Optional[str] = Query(None, description="Filter by holonic category (Observer, Participant, Contributor, Integrator, Exemplar)")
):
    """
    Get Ubuntu principle holonic scores with optional individual account data.
    
    NEW IN v2.7.0:
    - include_accounts=true returns per-account dimension scores for visualization
    - Returns 5 holonic dimensions + 4 Ubuntu principle scores per account
    - Supports pagination and category filtering
    
    Default (include_accounts=false): Returns aggregate statistics only (backward compatible)
    """
    params = {}
    if include_accounts:
        params["include_accounts"] = "true"
        params["limit"] = limit
        params["offset"] = offset
    if category:
        params["category"] = category
    return await fetch_from_backend("/api/v1/holonic-scores", params if params else None)

# ========================================================================
# TRANSACTION ENDPOINTS
# ========================================================================

@app.get("/v1/transactions/recent", response_class=JSONResponse, tags=["Transactions"], summary="Get recent transactions")
async def get_recent_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    asset_code: Optional[str] = Query(None, description="Filter by token")
):
    """Get recent transactions with operation details."""
    params = {"limit": limit}
    if asset_code:
        params["asset_code"] = asset_code.upper()
    return await fetch_from_backend("/api/v1/transactions/recent", params)

# ========================================================================
# DISTRIBUTION ENDPOINTS
# ========================================================================

@app.get("/v1/distribution", response_class=JSONResponse, tags=["Distribution"], summary="Get distribution stats")
async def get_distribution():
    """Get token distribution statistics."""
    return await fetch_from_backend("/api/v1/distribution")


@app.get("/v1/token-audit", response_class=JSONResponse, tags=["Distribution"], summary="Get token audit (default UBEC)")
@app.get("/v1/token-audit/{token_code}", response_class=JSONResponse, tags=["Distribution"], summary="Get token audit")
async def get_token_audit(token_code: str = "UBEC"):
    """
    Get comprehensive token audit data.
    
    UPDATED v1.4.0 - Backend API v2.7.0:
    - Total supply now includes LP reserves (total_in_accounts + total_in_liquidity_pools)
    - Stewardship accounts include breakdown (direct, lp_positions)
    - LP summary includes stewardship_lp_by_account (management, infrastructure, liquidity)
    
    Returns:
        Comprehensive audit data with token info, summary, distribution categories,
        and compliance indicators.
    """
    return await fetch_from_backend(f"/api/v1/token-audit/{token_code.upper()}")


@app.get("/v1/liquidity-pools", response_class=JSONResponse, tags=["Distribution"], summary="Get liquidity pools")
async def get_liquidity_pools(
    token_code: Optional[str] = Query(None, description="Filter by token (UBEC, UBECrc, UBECgpi, UBECtt)")
):
    """
    Get liquidity pool information.
    
    Returns pools with reserves, participants, and summary statistics.
    """
    params = None
    if token_code:
        params = {"token_code": token_code.upper()}
    return await fetch_from_backend("/api/v1/liquidity-pools", params)

# ========================================================================
# BIOREGION ENDPOINTS
# ========================================================================

@app.get("/v1/bioregions", response_class=JSONResponse, tags=["Bioregions"], summary="Get bioregions")
async def get_bioregions(limit: int = Query(default=50, ge=1, le=500)):
    """Get bioregion data."""
    return await fetch_from_backend("/api/v1/bioregions", {"limit": limit})


@app.get("/v1/bioregion-boundaries", response_class=JSONResponse, tags=["Bioregions"], summary="Get bioregion boundaries")
async def get_bioregion_boundaries():
    """Get bioregion boundaries with GeoJSON geometries."""
    return await fetch_from_backend("/api/v1/bioregion-boundaries")


@app.get("/v1/bioregions/{gid}/bbox", response_class=JSONResponse, tags=["Bioregions"], summary="Get bioregion bbox")
async def get_bioregion_bbox(gid: int):
    """Get bounding box for a bioregion (EPSG:3857)."""
    return await fetch_from_backend(f"/api/v1/bioregions/{gid}/bbox")


@app.get("/v1/points-of-interest", response_class=JSONResponse, tags=["Bioregions"], summary="Get POIs")
async def get_pois(
    poi_type: Optional[str] = None,
    bioregion_gid: Optional[int] = None,
    visibility: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500)
):
    """Get points of interest with optional filters."""
    params = {"limit": limit}
    if poi_type:
        params["poi_type"] = poi_type
    if bioregion_gid:
        params["bioregion_gid"] = bioregion_gid
    if visibility:
        params["visibility"] = visibility
    return await fetch_from_backend("/api/v1/points-of-interest", params)

# ========================================================================
# GEOGRAPHIC ENDPOINTS
# ========================================================================

@app.get("/v1/ecoregions", response_class=JSONResponse, tags=["Geographic"], summary="Get ecoregions")
async def get_ecoregions(limit: int = Query(default=50, ge=1, le=500)):
    """Get ecoregion data from Ecoregions2017."""
    return await fetch_from_backend("/api/v1/ecoregions", {"limit": limit})


@app.get("/v1/ecoregions/{eco_id}/bbox", response_class=JSONResponse, tags=["Geographic"], summary="Get ecoregion bbox")
async def get_ecoregion_bbox(eco_id: int):
    """Get bounding box for an ecoregion (EPSG:3857)."""
    return await fetch_from_backend(f"/api/v1/ecoregions/{eco_id}/bbox")


@app.get("/v1/watersheds", response_class=JSONResponse, tags=["Geographic"], summary="Get watersheds")
async def get_watersheds(limit: int = Query(default=50, ge=1, le=500)):
    """Get watershed data from FEOW HydroSHEDS."""
    return await fetch_from_backend("/api/v1/watersheds", {"limit": limit})


@app.get("/v1/watersheds/{feow_id}/bbox", response_class=JSONResponse, tags=["Geographic"], summary="Get watershed bbox")
async def get_watershed_bbox(feow_id: int):
    """Get bounding box for a watershed (EPSG:3857)."""
    return await fetch_from_backend(f"/api/v1/watersheds/{feow_id}/bbox")

# ========================================================================
# SYSTEM ENDPOINTS
# ========================================================================

@app.get("/v1/system/info", response_class=JSONResponse, tags=["System"], summary="Get system info")
async def get_system_info():
    """Get API system information."""
    return {
        "service": "UBEC API Gateway",
        "version": "1.5.0",
        "backend_api_version": "2.7.0",
        "backend_url": BACKEND_API_URL,
        "features": {
            "token_audit_v258": True,
            "lp_breakdown": True,
            "bbox_endpoints": True,
            "gateway_auth": True
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/v1/system/health", response_class=JSONResponse, tags=["System"], summary="Get detailed health")
async def get_system_health():
    """Get detailed health including backend status."""
    health = {
        "api_gateway": "healthy",
        "backend": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    try:
        backend_health = await fetch_from_backend("/health")
        health["backend"] = "healthy"
        health["backend_details"] = backend_health
    except Exception as e:
        health["backend"] = "unhealthy"
        health["backend_error"] = str(e)
    return health


# ========================================================================
# MAIN
# ========================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
