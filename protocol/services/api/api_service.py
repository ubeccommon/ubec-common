#!/usr/bin/env python3
"""
UBEC Backend API Service - Production Version 2.7.0 (ENHANCED HOLONIC SCORES)
==============================================================================
Provides read-only REST API endpoints for public website consumption
with IP-based rate limiting for abuse prevention.

This service exposes specific endpoints for the www server to consume,
providing an abstraction layer between the public website and internal
protocol operations. Integrated with real bioregion tracking, ecoregion
data, and watershed information.

NEW IN v2.7.0 - ENHANCED HOLONIC-SCORES ENDPOINT:
- ✨ NEW: /api/v1/holonic-scores now supports individual account data
  - Added include_accounts=true parameter for full dimension scores
  - Returns all 5 holonic dimensions per account (visualization-ready)
  - Returns all 4 Ubuntu principle scores per account (element-specific)
  - Enables frontend visualization reports equivalent to holonic_visualizer
  - Provides base data for third-party evaluation implementations
- ✨ NEW: Query parameters for /api/v1/holonic-scores:
  - include_accounts: Boolean to include individual account evaluations
  - limit: Maximum accounts to return (default 100, max 500)
  - offset: Pagination offset for accounts
  - category: Filter by holonic category (Observer, Participant, etc.)
- ✨ NEW: Enhanced summary statistics when include_accounts=true:
  - category_distribution: Count per holonic category
  - score_statistics: mean, median, min, max of composite scores
  - dimension_statistics: Statistics per dimension (5 dimensions)
  - ubuntu_principles: Aggregate metrics (4 elements)
- 🎯 BACKWARD COMPATIBLE: Default behavior unchanged (summary only)
- 🎯 Full compliance with all 12 project design principles
- Result: 21 UNIQUE ENDPOINTS (unchanged)

MAINTAINED FROM v2.6.0 - ALIAS REMOVAL (Principle #12 Compliance):
- 🔧 REMOVED: /api/v1/network-status alias (use /api/v1/network)
- 🔧 REMOVED: /api/v1/distributions alias reference (use /api/v1/distribution)
- 🔧 STREAMLINED: Root endpoint now returns concise categorized endpoint listing
- 🔧 ADDED: Missing /api/v1/token-audit/{token_code} to endpoint listing
- 🐛 FIXED: /api/v1/distribution returning zeros for all category amounts
  - Root cause: API used flat keys (account_total, general_percentage) 
  - Service returns nested structure (total_in_accounts, general['percentage'])
  - Fixed: Corrected key mapping to extract nested values properly
  - Added: direct/lp_positions breakdown for stewardship and admin
- 🎯 Full compliance with Principle #12 (Method Singularity) - no duplicate routes
- 🎯 Each endpoint implemented exactly once with single canonical path
- Result: 21 UNIQUE ENDPOINTS (was 23 with aliases counted separately)

MAINTAINED FROM v2.5.8 - TOTAL SUPPLY FIX:
- 🔥 CRITICAL FIX: Total supply now includes liquidity pool reserves
  - Total = account_balances + liquidity_pools.balance
  - Expected ~191,766,039 UBEC (was only showing ~152M)
- ✅ FIXED: Stewardship LP positions include ALL 3 accounts
  - Management, Infrastructure, and Liquidity accounts now all include LP
- ✅ ADDED: LP breakdown for each stewardship account in audit
- ✅ ADDED: total_in_accounts and total_in_liquidity_pools in summary

NEW IN v2.5.7 - API GATEWAY AUTHENTICATION:
- ✨ NEW: APIGatewayAuthMiddleware integration for defense-in-depth security
  - Verifies X-API-Gateway-Key header from authorized gateway
  - IP whitelist verification (optional, configurable)
  - Public paths (/health, /, /api/docs) bypass authentication
  - Environment variables: API_GATEWAY_KEY, API_GATEWAY_IPS
- 🔧 ENHANCED: Standardized health check using ServiceHealthCheck utility
  - Now uses ServiceHealthCheck.api_dependent_health() pattern
  - Complies with Principle #12 (Method Singularity)
  - Provides detailed request/error metrics
- 🎯 Full compliance with all 12 project design principles
- Result: 21 UNIQUE ENDPOINTS (aliases removed in v2.6.0)

MAINTAINED FROM v2.5.6 - LIQUIDITY POOLS ENDPOINT:
- ✨ /api/v1/liquidity-pools endpoint
  - Returns all UBEC liquidity pools with comprehensive details
  - Optional token_code filter (UBEC, UBECrc, UBECgpi, UBECtt)
  - Pool details: id, pair, reserves, total_shares, balance
  - Token info: token_code, element, ubec_position
  - Trading info: fee_bp, trustline_count
  - Participant count from liquidity_pool_owners
  - Summary statistics: total_pools, total_value_locked
  - Source: ubec_main.liquidity_pools table

MAINTAINED FROM v2.5.5 - TOKEN AUDIT ENDPOINT:
- ✨ NEW: /api/v1/token-audit and /api/v1/token-audit/{token_code}
  - Comprehensive token audit for transparency reporting
  - Summary section: total_issued, total_distributed, percentage breakdowns
  - Shows Issuer Account and total tokens issued
  - General Distribution (65%): General account + project accounts
  - Token Ecosystem Stewardship (30%): Management, Infrastructure, Liquidity
  - Liquidity Pool breakdown: unlocked vs locked in pools
  - Administration (5%): General Administration account
  - Compliance status indicators
  - Full disclaimer text
  - Supports all 4 UBEC tokens (UBEC, UBECrc, UBECgpi, UBECtt)
- 🐛 FIXED: /api/v1/tokens returning null issuers and 0 supply/holders
  - Issuers fetched from system_settings table (database is source of truth)
  - Supply/holders calculated from ubec_balances (real-time data)
  - Project accounts fetched from monitored_accounts table

MAINTAINED FROM v2.5.4 - TRADE/EXCHANGE DETAILS:
- Trade operations show exchange direction (e.g., "100 UBEC → 50 UBECrc")

MAINTAINED FROM v2.5.3 - UBEC TOKENS ONLY:
- Filter to only UBEC, UBECrc, UBECgpi, UBECtt tokens (exclude XLM)

MAINTAINED FROM v2.5.2 - OPERATION DETAILS:
- Operations array with type, asset_code, amount, from_account, to_account

NEW IN v2.5.0 - BBOX ENDPOINTS:
- ✨ NEW: /api/v1/bioregions/{gid}/bbox endpoint
  - Provides bounding box coordinates for bioregion boundaries
  - Returns min_x, min_y, max_x, max_y, centroid in EPSG:3857 (meters)
  - Useful for map centering and zoom calculations
  - Source: phenomenal.bioregion_boundaries table
- ✨ NEW: /api/v1/ecoregions/{eco_id}/bbox endpoint
  - Provides bounding box coordinates for WWF Ecoregions 2017
  - Returns bbox with eco_name, biome_name, realm metadata
  - Source: phenomenal.ecoregions_2017 table
- ✨ NEW: /api/v1/watersheds/{feow_id}/bbox endpoint
  - Provides bounding box coordinates for FEOW HydroSHEDS watersheds
  - Returns bbox with area_sqkm and generated name
  - Source: phenomenal.feow_hydrosheds table
- 🎯 All bbox endpoints use ST_Transform(geom, 3857) for WGS 84 / Pseudo-Mercator
- 🎯 Coordinates returned in meters (EPSG:3857) for web mapping compatibility
- 🎯 Full compliance with all 12 project design principles
- 🎯 Integrated rate limiting (100 requests/minute per IP)
- Result: 22 TOTAL ENDPOINTS NOW AVAILABLE

MAINTAINED FROM v2.4.6 - CASE-INSENSITIVE ASSET FILTER:
- 🐛 FIXED: asset_code parameter is now case-insensitive
  - Issue: Database stores 'UBEC' (uppercase) but users may query 'ubec' (lowercase)
  - Solution: Convert asset_code parameter to uppercase before query
  - Impact: Both ?asset_code=ubec and ?asset_code=UBEC now work correctly
  - Result: User-friendly case-insensitive filtering operational

MAINTAINED FROM v2.4.5 - ASSET_CODE FILTER FIX:
- 🐛 FIXED: Imprecise asset_code filtering in /api/v1/transactions/recent
  - Root cause: Used involves_tokens array which contains ALL tokens in transaction
  - Issue: Filtering by asset_code='UBEC' matched transactions with any UBEC operation, even if transaction also had UBECrc/UBECgpi/UBECtt operations
  - Solution: JOIN with stellar_operations table to filter by exact operation asset_code
  - Query: INNER JOIN ubec_main.stellar_operations ON transaction_hash WHERE asset_code = $1
  - Impact: Precise filtering - only returns transactions with operations for specified asset
  - Result: asset_code parameter now provides accurate asset-specific transaction filtering

MAINTAINED FROM v2.4.4 - ACCOUNTS TABLE FIX:
- 🐛 FIXED: column "phenomenal_mode" does not exist
  - Root cause: Endpoints querying phenomenal.accounts table which has wrong schema
  - Correct table: ubec_main.stellar_accounts (not phenomenal.accounts)
  - Fixed: /api/v1/network-status endpoint - use stellar_accounts for participant count
  - Fixed: /api/v1/accounts endpoint - use stellar_accounts with holonic_metrics JOIN
  - Fixed: /api/v1/accounts/{id} endpoint - use stellar_accounts with holonic_metrics JOIN
  - Fixed: Ubuntu scores now from holonic_metrics.ubuntu_alignment_score
  - Impact: Network stats, accounts list, and account details now fully operational
- Result: ALL 19 ENDPOINTS NOW 100% OPERATIONAL

NEW IN v2.4.4 - ACCOUNTS TABLE FIX:
- 🐛 FIXED: column "phenomenal_mode" does not exist
  - Root cause: Endpoints querying phenomenal.accounts table which has wrong schema
  - Correct table: ubec_main.stellar_accounts (not phenomenal.accounts)
  - Fixed: /api/v1/network-status endpoint - use stellar_accounts for participant count
  - Fixed: /api/v1/accounts endpoint - use stellar_accounts with holonic_metrics JOIN
  - Fixed: /api/v1/accounts/{id} endpoint - use stellar_accounts with holonic_metrics JOIN
  - Fixed: Ubuntu scores now from holonic_metrics.ubuntu_alignment_score
  - Impact: Network stats, accounts list, and account details now fully operational
- Result: ALL 19 ENDPOINTS NOW 100% OPERATIONAL

MAINTAINED FROM v2.4.3 - NETWORK STATUS ENDPOINT:
- ✨ NEW: /api/v1/network-status endpoint (alias to /api/v1/network)
  - Provides network statistics and health metrics
  - Returns participant count, bioregion count, transaction volume
  - Calculates network health status based on multiple factors
  - Rate limited to 100 requests/minute per IP
- Result: 19 TOTAL ENDPOINTS NOW AVAILABLE

MAINTAINED FROM v2.4.2 - FINAL TABLE NAME FIX:
- 🐛 FIXED: relation "ubec_main.asset_analysis" does not exist
  - Root cause: Table is named asset_holder_analysis, not asset_analysis
  - Fixed: Both /api/v1/tokens and /api/v1/tokens/{code}/analysis endpoints
  - Fixed: Updated column names (total_holders not holder_count, analysis_date not computed_at)
  - Impact: Token endpoints now fully operational with actual data
- Result: ALL 18 ENDPOINTS NOW 100% OPERATIONAL

MAINTAINED FROM v2.4.1 - CRITICAL PRODUCTION FIXES:
- 🐛 FIXED: Service 'config_service' not found error
  - Root cause: Service registered as 'config' not 'config_service'
  - Fixed: Changed registry.get('config_service') to registry.get('config')
  - Impact: /api/v1/tokens endpoint now operational
- 🐛 FIXED: Column "metric_name" does not exist in ubec_holonic_metrics
  - Root cause: Table has 'principle' column (enum), not 'metric_name'/'metric_value'
  - Fixed: Query now uses principle = 'diversity'/'reciprocity'/'mutualism'/'regeneration'
  - Impact: /api/v1/holonic-scores endpoint now operational
- 🐛 FIXED: Column "tx_type" does not exist in stellar_transactions
  - Root cause: stellar_transactions table doesn't have tx_type column
  - Fixed: Removed tx_type from SELECT and response dictionary
  - Fixed: Changed 'ledger' to correct column name 'ledger_sequence'
  - Impact: /api/v1/transactions/recent endpoint now operational
- Result: ALL 3 FAILING ENDPOINTS NOW 100% OPERATIONAL

NEW IN v2.4.0 - BIOREGION DATA ENHANCEMENT:
- ✨ NEW: /api/v1/bioregion-boundaries endpoint
  - Provides comprehensive bioregion boundary data with full metadata
  - Returns GeoJSON geometries for spatial visualization
  - Includes ecological metadata, token allocations, and community info
  - Source: phenomenal.bioregion_boundaries table
- ✨ NEW: /api/v1/points-of-interest endpoint
  - Provides POI data (farms, community centers, landmarks, resources)
  - Returns GeoJSON point geometries with rich metadata
  - Includes contact info, images, operating hours, UBEC associations
  - Source: phenomenal.points_of_interest table
- 🎯 Both endpoints follow established patterns with explicit schema names
- 🎯 Full compliance with all 12 project design principles
- 🎯 Integrated rate limiting (100 requests/minute per IP)

MAINTAINED FROM v2.3.12 - PRODUCTION DEPLOYMENT FIX:
- 🐛 FIXED: Type cast error in involves_tokens array comparison
  - Root cause: involves_tokens column requires explicit ::text[] cast for && operator
  - Fixed: Added ::text[] cast to both main query (line 904) and count query (line 915)
  - Impact: /api/v1/transactions/recent endpoint now fully operational
- 🐛 FIXED: Missing ecoregions table reference
  - Root cause: Actual table is phenomenal.ecoregions_2017, not topology.ecoregions
  - Fixed: Updated query to use correct phenomenal schema
  - Fixed: Column mapping eco_id::text as eco_code (actual column is eco_id)
  - Impact: /api/v1/ecoregions endpoint now returns proper ecoregion data
- 🐛 FIXED: Missing watersheds table reference
  - Root cause: Actual table is phenomenal.feow_hydrosheds (only 4 columns: id, geom, feow_id, area_skm)
  - Fixed: Using phenomenal.feow_hydrosheds with correct column mapping
  - Fixed: Generated name field from feow_id (table has no name/ecoregion column)
  - Impact: /api/v1/watersheds endpoint now returns watershed boundary data
- 🐛 FIXED: Incorrect await on synchronous config_service.get() calls
  - Root cause: config_service.get() is synchronous method, not async
  - Fixed: Removed await keyword from 4 issuer address config calls (lines 594-597)
  - Impact: /api/v1/tokens endpoint now returns proper token information
- Result: ALL 16 ENDPOINTS NOW 100% OPERATIONAL IN PRODUCTION

MAINTAINED FROM v2.3.11 - SCHEMA ALIGNMENT FIXES:
- 🐛 FIXED: Type "ubec_token[]" does not exist in transactions query
  - Root cause: involves_tokens is simple ARRAY type, not custom enum ubec_token[]
  - Fixed: Removed invalid ::ubec_token[] cast from array comparison
  - Impact: /api/v1/transactions/recent endpoint now works correctly
- 🐛 FIXED: Column "general_circulation_pct" does not exist in distribution_state
  - Root cause: Table is normalized - one row per asset/category combination
  - Actual columns: category, actual_percentage (not _pct columns)
  - Fixed: Added PIVOT query to aggregate categories per token
  - Impact: /api/v1/distribution and /api/v1/distributions endpoints now work

NEW IN v2.3.10 - CRITICAL SCHEMA ALIGNMENT FIXES:
- 🐛 FIXED: Column "diversity_score" does not exist in holonic_metrics table
  - Root cause: Ubuntu principle scores exist in SEPARATE table (ubec_holonic_metrics)
  - Fixed: Query now uses LEFT JOIN to ubec_holonic_metrics table with PIVOT aggregation
  - Fixed: diversity_score, reciprocity_score, mutualism_score, regeneration_score from correct table
  - Impact: /api/v1/holonic-scores endpoint now returns proper Ubuntu principle metrics
- 🐛 FIXED: Column "tx_hash" does not exist in stellar_transactions table  
  - Root cause: Actual column name is "transaction_hash" not "tx_hash"
  - Fixed: Query updated to use correct column name "transaction_hash"
  - Impact: /api/v1/transactions/recent endpoint now works correctly
- 🐛 FIXED: 404 Not Found on /api/v1/distribution endpoint
  - Root cause: Route registered as /api/v1/distributions (plural) not /api/v1/distribution (singular)
  - Fixed: Added alias route for /api/v1/distribution pointing to same handler
  - Impact: Both /api/v1/distribution and /api/v1/distributions now work

MAINTAINED FROM v2.3.9 - GEOMETRY ALIAS FIX:
- 🐛 FIXED: KeyError 'geom' in ecoregions and watersheds endpoints
  - Fixed: ecoregions endpoint now uses row['geometry'] (matches SQL alias)
  - Fixed: watersheds endpoint now uses row['geometry'] (matches SQL alias)
  - Root cause: Queries use ST_AsGeoJSON(geom)::json AS geometry (creates 'geometry' column)
  - Previous error: Code tried to access row['geom'] which doesn't exist in result set
  - Impact: Both geography endpoints now return proper GeoJSON data
  - Result: All 16 endpoints now 100% operational with proper geometry handling

MAINTAINED FROM v2.3.8 - NONE-SAFE CONVERSION FIX:
- 🐛 FIXED: TypeError in get_holonic_scores when no evaluation data exists
  - Added safe_float() and safe_int() helper functions for None handling
  - SQL aggregate functions (AVG, MIN, MAX) return NULL when no data exists
  - NULL values are now safely converted with default values (0.0 for floats, 0 for ints)
  - Resolves: "float() argument must be a string or a real number, not 'NoneType'"
  - Impact: API endpoint now returns valid response even on fresh system with no evaluations

MAINTAINED FROM v2.3.7 - UBUNTU METRICS ENHANCEMENT (reciprocity_health & mutualism_capacity):
- 🎯 ENHANCED: reciprocity_health now returns baseline score from UBECrc balance
  - Returns 0.0-0.2 score for accounts holding UBECrc even without transactions
  - Indicates "readiness for reciprocity" rather than just transaction activity
  - Phased deployment friendly: meaningful scores with limited transaction data
- 🎯 ENHANCED: mutualism_capacity now returns baseline score from account age
  - Returns 0.0-0.2 score for all accounts based on stability/longevity
  - Additional scores for UBECgpi holdings and transaction consistency
  - Recognizes that mutualism includes long-term presence, not just token holdings
- ✅ Resolves: "v2.2.0 metrics not found" warning in deployment verification
- ✅ Both metrics now provide meaningful values even during phased token deployment

MAINTAINED FROM v2.3.6:
- ✅ All 4 tokens always returned (LEFT JOIN pattern)
- ✅ Tokens without analysis data show gracefully with 0 values

MAINTAINED FROM v2.3.5:
- ✅ Window function for getting latest analysis per token
- ✅ Historical data handling for time-series tables
- ✅ Bioregions endpoint method fix (get_all_bioregions)

MAINTAINED FROM v2.3.3:
- ✅ Result dictionary keys match database columns
- ✅ All query column names corrected
- ✅ Malformed column names fixed

MAINTAINED FROM v2.3.2:
- ✅ Distribution endpoint placeholder data
- ✅ Column names match database schema

MAINTAINED FROM v2.3.1:
- ✅ Correct table name: holonic_metrics (not holonic_evaluations)
- ✅ Correct method: db.fetch_all() (not db.fetch())

MAINTAINED FROM v2.3.0:
- ✅ GET /api/v1/ecoregions - Complete implementation
- ✅ GET /api/v1/watersheds - Complete implementation
- ✅ reciprocity_health and mutualism_capacity metrics

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained API service module
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Database-backed with explicit schemas
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Comprehensive health checks
    ✅ #8  No Duplicate Configuration: Configuration from registry
    ✅ #9  Integrated Rate Limiting: IP-based, active (100/min, 1000/hour)
    ✅ #10 Separation of Concerns: API layer isolated from business logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Each endpoint implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage Example:
    ```python
    from core.service_registry import ServiceRegistry
    from services.api.api_service import create_backend_api_service
    
    # Initialize via service registry (proper pattern)
    registry = ServiceRegistry()
    api_service = await registry.get('api_service')
    
    # FastAPI app is available at api_service.app
    # Run with: uvicorn main:app --host 0.0.0.0 --port 8000
    ```

Rate Limiting:
    IP-based rate limiting (no authentication required):
    - Default: 100 requests/minute, 1000 requests/hour per IP
    - Health endpoints: 300 requests/minute (for monitoring)
    - Transaction queries: 60 requests/minute (expensive queries)
    - No API keys required - open access with abuse prevention

Author: UBEC Protocol Development Team
Version: 2.6.0
Updated: 2025-11-29
Changes: 
  v2.6.0 - NO ALIASES: Remove duplicate routes for Principle #12 compliance
         - REMOVED: /api/v1/network-status alias (canonical: /api/v1/network)
         - REMOVED: /api/v1/distributions phantom alias from root endpoint listing
         - STREAMLINED: Root endpoint returns categorized endpoint listing
         - ADDED: /api/v1/token-audit/{token_code} to endpoint listing (was missing)
         - 🐛 FIXED: /api/v1/distribution returning zeros for all category amounts
           - Root cause: API used flat keys but service returns nested structure
           - Fixed: Corrected key mapping (total_in_accounts, general['percentage'], etc.)
           - Added: direct/lp_positions breakdown for stewardship and admin categories
         - COMPLIANCE: Full Principle #12 - each endpoint implemented exactly once
         - Result: 21 UNIQUE ENDPOINTS (no aliases or duplicates)
  v2.5.7 - GATEWAY AUTH: API Gateway Authentication and standardized health checks
         - NEW: APIGatewayAuthMiddleware integration for defense-in-depth security
         - NEW: Verifies X-API-Gateway-Key header from authorized gateway
         - NEW: IP whitelist verification (optional, configurable)
         - ENHANCED: Standardized health check using ServiceHealthCheck.api_dependent_health()
         - ENHANCED: Health check now tracks request_count and error_count metrics
         - COMPLIANCE: Full Principle #12 (Method Singularity) health check pattern
         - ENV: API_GATEWAY_KEY, API_GATEWAY_IPS for configuration
  v2.5.6 - LIQUIDITY POOLS: New endpoint for LP details
         - NEW: /api/v1/liquidity-pools endpoint
         - Returns all UBEC liquidity pools with comprehensive details
         - Optional token_code filter (UBEC, UBECrc, UBECgpi, UBECtt)
         - Pool details: id, pair, reserves, total_shares, balance
         - Token info: token_code, element, ubec_position
         - Trading info: fee_bp, trustline_count
         - Participant count from liquidity_pool_owners table
         - Summary: total_pools, total_value_locked, pools_by_token
         - Rate limited: 60 requests/minute per IP
         - Result: 23 TOTAL ENDPOINTS NOW AVAILABLE
  v2.5.5 - TOKEN AUDIT: Comprehensive token audit endpoint for transparency
         - NEW: /api/v1/token-audit and /api/v1/token-audit/{token_code}
         - Shows Issuer, General Distribution (65%), Stewardship (30%), Admin (5%)
         - Project accounts from monitored_accounts table
         - Liquidity pool breakdown (unlocked vs locked)
         - Compliance indicators and disclaimer
         - 🐛 FIXED: /api/v1/tokens returning null issuers and 0 supply/holders
           - Issuers from system_settings table (database is source of truth)
           - Supply/holders from ubec_balances (real-time data)
           - Distribution accounts from system_settings table
  v2.5.4 - TRADE DETAILS: Include exchange/trade details for swap operations
         - Problem: Trade operations didn't show which token was exchanged for which
         - Solution: Include exchange_source_asset/amount, exchange_dest_asset/amount
         - Added: trade_summary field (e.g., "100 UBEC → 50 UBECrc")
         - Added: is_trade boolean to identify trade operations
         - Impact: Dashboard can now show complete trade direction and amounts
  v2.5.3 - UBEC TOKENS ONLY: Filter transactions to UBEC ecosystem tokens
         - Problem: Dashboard was showing XLM transactions not related to UBEC
         - Solution: Filter to only UBEC, UBECrc, UBECgpi, UBECtt tokens
         - XLM and other non-UBEC tokens are now excluded
         - Added: valid_tokens field in response
         - Added: Validation for asset_code parameter
         - Impact: Dashboard shows only UBEC protocol transactions
  v2.5.2 - OPERATION DETAILS: Include operation-level details for frontend display
         - Problem: Frontend needs type, token, amount, direction per operation
         - Solution: Return operations array with type, asset_code, amount, from/to
         - Added: operations[] array with full details per transaction
         - Added: type (PAYMENT, CREATE_ACCOUNT, CHANGE_TRUST, etc.)
         - Added: from_account and to_account for transfer direction
         - Impact: Dashboard can now show Type, Token, Amount, From→To
         - Result: Complete transaction details with operation-level granularity
  v2.5.1 - TRANSACTIONS DATA FIX: Compute operation_count and involves_tokens dynamically
         - Problem: stellar_transactions table has incomplete data from synchronizer
         - Issue: ledger_sequence=0, involves_tokens=[], operation_count=null
         - Solution: JOIN with stellar_operations to compute values dynamically:
           - operation_count: COUNT(operations) per transaction
           - involves_tokens: array_agg(DISTINCT asset_code) from operations
           - ledger_sequence: COALESCE(ledger, ledger_sequence, 0)
         - Impact: /api/v1/transactions/recent now returns complete transaction data
         - Result: Frontend displays accurate operation counts and token involvement
  v2.5.0 - BBOX ENDPOINTS: Added bounding box endpoints for geographic entities
         - NEW: /api/v1/bioregions/{gid}/bbox - bioregion bounding box
         - NEW: /api/v1/ecoregions/{eco_id}/bbox - ecoregion bounding box
         - NEW: /api/v1/watersheds/{feow_id}/bbox - watershed bounding box
         - All use ST_Transform(geom, 3857) for WGS 84 / Pseudo-Mercator projection
         - Returns min_x, min_y, max_x, max_y, centroid coordinates in meters
         - Useful for web mapping (Google Maps, OpenStreetMap, Leaflet, etc.)
         - Result: 22 TOTAL ENDPOINTS NOW AVAILABLE
  v2.4.6 - CASE-INSENSITIVE ASSET FILTER: Made asset_code parameter case-insensitive
         - Fixed: asset_code='ubec' (lowercase) now works - converts to 'UBEC' internally
         - Solution: asset_code_upper = asset_code.upper() before query
         - Impact: User-friendly - accepts any case for asset_code parameter
         - Result: Both ?asset_code=ubec and ?asset_code=UBEC work correctly
  v2.4.5 - ASSET_CODE FILTER FIX: Corrected transaction filtering logic
         - Fixed: involves_tokens array filtering (imprecise) → stellar_operations JOIN (precise)
         - Root cause: involves_tokens contains ALL tokens, not operation-specific
         - Solution: INNER JOIN with stellar_operations.asset_code for exact filtering
         - Impact: /api/v1/transactions/recent?asset_code=X now returns only X transactions
         - Result: Accurate asset-specific transaction filtering operational
  v2.4.4 - ACCOUNTS TABLE FIX: Corrected phenomenal.accounts → ubec_main.stellar_accounts
         - Fixed: phenomenal.accounts doesn't have required schema
         - Fixed: Use ubec_main.stellar_accounts for all account queries
         - Fixed: /api/v1/network-status uses stellar_accounts for participant count
         - Fixed: /api/v1/accounts endpoint with holonic_metrics JOIN for Ubuntu scores
         - Fixed: /api/v1/accounts/{id} endpoint with proper stellar_accounts columns
         - Impact: Network stats and account endpoints now fully operational
         - Result: ALL 19 ENDPOINTS NOW 100% OPERATIONAL
  v2.4.3 - NETWORK STATUS ENDPOINT: Added frontend-requested endpoint
         - NEW: /api/v1/network-status endpoint (alias to /api/v1/network)
         - Provides comprehensive network statistics and health metrics
         - Rate limited to 100 requests/minute per IP
         - Result: 19 TOTAL ENDPOINTS NOW AVAILABLE
  v2.4.2 - FINAL TABLE NAME FIX: Corrected asset analysis table reference
         - Fixed: asset_analysis → asset_holder_analysis (correct table name)
         - Fixed: Updated column names throughout (total_holders, analysis_date)
         - Fixed: /api/v1/tokens endpoint query
         - Fixed: /api/v1/tokens/{code}/analysis endpoint query
         - Impact: Token data endpoints now return actual holder/supply data
         - Result: ALL 18 ENDPOINTS NOW 100% OPERATIONAL
  v2.4.1 - CRITICAL PRODUCTION FIXES: Fixed 3 failing endpoints
         - Fixed: Service name 'config_service' → 'config' (correct registry key)
         - Fixed: ubec_holonic_metrics query to use 'principle' column (not metric_name)
         - Fixed: stellar_transactions query removed tx_type, use ledger_sequence
         - Impact: /api/v1/tokens, /api/v1/holonic-scores, /api/v1/transactions/recent now operational
         - Result: ALL 18 ENDPOINTS NOW 100% OPERATIONAL
  v2.4.0 - BIOREGION DATA ENHANCEMENT: Added comprehensive geographic data endpoints
         - NEW: /api/v1/bioregion-boundaries endpoint for bioregion boundary data
         - NEW: /api/v1/points-of-interest endpoint for POI data (farms, landmarks, etc.)
         - Both endpoints return GeoJSON geometries with rich metadata
         - Explicit schema names (phenomenal.bioregion_boundaries, phenomenal.points_of_interest)
         - Full compliance with all 12 project design principles
         - Result: 18 TOTAL ENDPOINTS NOW AVAILABLE
  v2.3.12 - PRODUCTION DEPLOYMENT FIX: Critical schema and table corrections
          - Fixed: involves_tokens ::text[] cast for array overlap operator
          - Fixed: ecoregions query → phenomenal.ecoregions_2017 with column mapping
          - Fixed: watersheds query → phenomenal.feow_hydrosheds (only 4 columns available)
          - Fixed: Generated name from feow_id (no ecoregion column in table)
          - Fixed: Removed await from synchronous config_service.get() calls
          - Impact: All 4 failing endpoints now operational (transactions, ecoregions, watersheds, tokens)
          - Result: ALL 16 ENDPOINTS 100% OPERATIONAL IN PRODUCTION
  v2.3.11 - FINAL SCHEMA ALIGNMENT: Fixed remaining database mismatches
          - Fixed: involves_tokens array comparison (removed invalid ::ubec_token[] cast)
          - Fixed: distribution_state query to properly PIVOT normalized data
          - Result: All 16 endpoints now operational with correct schema references
  v2.3.10 - CRITICAL SCHEMA ALIGNMENT: Fixed table/column mismatches
          - Fixed: holonic_metrics query to use LEFT JOIN with ubec_holonic_metrics
          - Fixed: stellar_transactions query to use transaction_hash (not tx_hash)
          - Fixed: Added /api/v1/distribution route alias
          - Result: All remaining endpoint errors resolved
  v2.3.9 - GEOMETRY ALIAS FIX: Fixed KeyError in geography endpoints
         - Fixed: Use row['geometry'] not row['geom'] (matches SQL AS alias)
         - Impact: ecoregions and watersheds endpoints now return GeoJSON correctly
  v2.3.8 - NONE-SAFE CONVERSION: Handle NULL aggregate results gracefully
  v2.3.7 - UBUNTU METRICS ENHANCEMENT: Enhanced reciprocity_health and mutualism_capacity
         - Both metrics now provide meaningful baseline scores during phased deployment
  v2.3.6 - MISSING TOKEN FIX: Ensure all 4 tokens always returned
  v2.3.5 - METHOD NAME FIX: Use correct bioregion_manager method names
  v2.3.3 - COLUMN NAME ALIGNMENT: Match all column names to actual database schema
  v2.3.2 - DISTRIBUTION FIXES: Proper handling of distribution_state table
  v2.3.1 - TABLE NAME FIXES: Use correct table names throughout
  v2.3.0 - COMPLETE IMPLEMENTATION: All endpoints operational with real data
"""

# Standard library imports
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Third-party imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Local imports - API Gateway Authentication (v2.5.7)
from services.api.api_gateway_auth import APIGatewayAuthMiddleware

# Local imports - Standardized Health Check Utility (Principle #12)
from core.utils.service_health import ServiceHealthCheck

# ============================================================================
# Helper Functions
# ============================================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float, handling None.
    
    Args:
        value: Value to convert (can be None, numeric, or string)
        default: Default value if conversion fails or value is None
        
    Returns:
        Float value or default
        
    Example:
        >>> safe_float(None)
        0.0
        >>> safe_float(3.14)
        3.14
        >>> safe_float("invalid", 99.9)
        99.9
    """
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int, handling None.
    
    Args:
        value: Value to convert (can be None, numeric, or string)
        default: Default value if conversion fails or value is None
        
    Returns:
        Integer value or default
        
    Example:
        >>> safe_int(None)
        0
        >>> safe_int(42)
        42
        >>> safe_int("invalid", 999)
        999
    """
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================================
# Service Class
# ============================================================================

class BackendAPIService:
    """
    Backend API Service for UBEC Protocol.
    
    Provides read-only REST API endpoints for public website consumption,
    with comprehensive rate limiting and production-ready error handling.
    
    All endpoints follow the pattern:
    - Explicit schema names in all database queries
    - Async database operations
    - Rate limiting per IP address
    - Proper error handling with structured responses
    - GeoJSON support for spatial data
    
    Attributes:
        app: FastAPI application instance
        registry: Service registry for dependency injection
        logger: Logging instance
        limiter: Rate limiter instance
        
    Example:
        >>> registry = ServiceRegistry()
        >>> api_service = await registry.get('api_service')
        >>> # FastAPI app available at api_service.app
    """
    
    def __init__(self, registry):
        """
        Initialize the Backend API Service.
        
        Args:
            registry: ServiceRegistry instance for dependency injection
        """
        self.registry = registry
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
        # v2.5.7: Add metrics tracking for standardized health checks
        self._request_count = 0
        self._error_count = 0
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="UBEC Backend API",
            description="Read-only API for UBEC Protocol public website",
            version="2.6.0"
        )
        
        # Configure CORS (must be first - handles preflight requests)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["GET"],
            allow_headers=["*"],
        )
        
        # v2.5.7: API Gateway Authentication (defense in depth)
        # Verifies X-API-Gateway-Key header and IP whitelist
        # Public paths (/health, /, /api/docs, etc.) bypass authentication
        self.app.add_middleware(APIGatewayAuthMiddleware)
        
        # Initialize rate limiter
        self.limiter = Limiter(key_func=get_remote_address)
        self.app.state.limiter = self.limiter
        self.app.add_exception_handler(RateLimitExceeded, self._rate_limit_error_handler)
    
    async def initialize(self) -> None:
        """
        Initialize the service and register all endpoints.
        
        Called by service registry during system startup.
        Sets up all API routes with proper rate limiting and error handling.
        """
        if self._initialized:
            return
        
        self.logger.info("Initializing BackendAPIService v2.6.0")
        
        # Register all endpoints
        self._register_endpoints()
        
        self._initialized = True
        self.logger.info("✓ BackendAPIService initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for service registry using standardized ServiceHealthCheck.
        
        v2.5.7: Updated to use ServiceHealthCheck.api_dependent_health() pattern
        for compliance with Principle #12 (Method Singularity).
        
        This service is API-dependent because it serves HTTP requests and
        depends on the database for all data operations.
        
        Returns:
            Dict with comprehensive health status including:
            - status: 'healthy', 'degraded', 'unhealthy', or 'unknown'
            - message: Human-readable status description
            - timestamp: ISO format timestamp
            - details: Service-specific metrics and configuration
        
        Example:
            >>> health = await api_service.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("API service operational")
        """
        # Check database connectivity for API health
        db_accessible = False
        try:
            db = await self.registry.get('database')
            if db:
                # Simple connectivity test
                result = await db.fetch_one("SELECT 1 as ok")
                db_accessible = result is not None
        except Exception as e:
            self.logger.debug(f"Database check in health_check: {e}")
        
        return await ServiceHealthCheck.api_dependent_health(
            service_name='BackendAPIService',
            is_initialized=self._initialized,
            api_url='http://localhost:8000',
            api_accessible=db_accessible,  # API is healthy if DB is accessible
            request_count=self._request_count,
            error_count=self._error_count,
            cache_info={
                'endpoints_count': 21,
                'rate_limiting': 'active',
                'version': '2.7.0',
                'gateway_auth': 'enabled'
            }
        )
    
    def _register_endpoints(self) -> None:
        """
        Register all API endpoints with FastAPI.
        
        All endpoints follow the design pattern:
        - GET only (read-only API)
        - Rate limited per IP
        - Async database operations
        - Explicit schema names in queries
        - Structured error responses
        """
        limiter = self.limiter
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                'service': 'UBEC Backend API',
                'version': '2.7.0',
                'status': 'operational',
                'endpoints': {
                    'system': ['/health'],
                    'network': ['/api/v1/network'],
                    'tokens': [
                        '/api/v1/tokens',
                        '/api/v1/tokens/{token_code}/analysis',
                        '/api/v1/token-audit/{token_code}'
                    ],
                    'accounts': [
                        '/api/v1/accounts',
                        '/api/v1/accounts/{account_id}'
                    ],
                    'distribution': [
                        '/api/v1/distribution',
                        '/api/v1/liquidity-pools'
                    ],
                    'geography': [
                        '/api/v1/bioregions',
                        '/api/v1/bioregions/{gid}/bbox',
                        '/api/v1/bioregion-boundaries',
                        '/api/v1/points-of-interest',
                        '/api/v1/ecoregions',
                        '/api/v1/ecoregions/{eco_id}/bbox',
                        '/api/v1/watersheds',
                        '/api/v1/watersheds/{feow_id}/bbox'
                    ],
                    'analytics': [
                        '/api/v1/holonic-scores',
                        '/api/v1/transactions/recent'
                    ]
                },
                'endpoint_count': 21,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.get("/health")
        @limiter.limit("300/minute")
        async def health_check(request: Request):
            """
            Health check endpoint for monitoring.
            
            Rate limit: 300 requests/minute per IP (generous for monitoring tools)
            
            Returns:
                Health status with service availability
            """
            return {
                'status': 'healthy',
                'service': 'ubec_backend_api',
                'version': '2.7.0',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.get("/api/v1/network", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_network_stats(request: Request) -> Dict:
            """
            Get overall network statistics and health.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - Total participants, bioregions, transactions
            - Ubuntu alignment scores
            - Network health status
            """
            try:
                db = await self.registry.get('database')
                
                # v2.4.4: Use ubec_main.stellar_accounts (correct table)
                # Get participant count
                participant_query = "SELECT COUNT(*) FROM ubec_main.stellar_accounts"
                participant_result = await db.fetch_one(participant_query)
                participant_count = participant_result['count'] if participant_result else 0
                
                # Get bioregion count
                bioregion_query = "SELECT COUNT(*) FROM phenomenal.holons WHERE holon_type = 'bioregion' AND dissolved_at IS NULL"
                bioregion_result = await db.fetch_one(bioregion_query)
                bioregion_count = bioregion_result['count'] if bioregion_result else 0
                
                # Get transaction count
                tx_query = "SELECT COUNT(*) FROM ubec_main.stellar_transactions"
                tx_result = await db.fetch_one(tx_query)
                transaction_count = tx_result['count'] if tx_result else 0
                
                # Get average Ubuntu score from holonic_metrics
                ubuntu_query = """
                    SELECT AVG(ubuntu_alignment_score) as avg_ubuntu_score
                    FROM ubec_main.holonic_metrics
                    WHERE evaluation_date >= NOW() - INTERVAL '7 days'
                """
                ubuntu_result = await db.fetch_one(ubuntu_query)
                avg_ubuntu_score = safe_float(ubuntu_result['avg_ubuntu_score'] if ubuntu_result else None, 0.0)
                
                # Calculate network health
                network_health = self._calculate_network_health(
                    bioregion_count,
                    participant_count,
                    avg_ubuntu_score
                )
                
                return {
                    'network': {
                        'participants': participant_count,
                        'bioregions': bioregion_count,
                        'transactions': transaction_count,
                        'ubuntu_alignment': round(avg_ubuntu_score, 3),
                        'health': network_health
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching network stats: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching network statistics: {str(e)}")
        
        @self.app.get("/api/v1/tokens", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_tokens(request: Request) -> Dict:
            """
            Get all token information including supply and holders.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - Token details (code, name, issuer)
            - Current supply and holder counts
            - Latest analysis if available
            
            SCHEMA FIX v2.5.5: Use system_settings for issuers and ubec_balances for metrics
            - Problem: config_service returning None for issuer addresses
            - Problem: asset_holder_analysis may not have recent data
            - Solution: Query system_settings table for issuer addresses
            - Solution: Calculate total_supply and holder_count from ubec_balances
            """
            try:
                db = await self.registry.get('database')
                
                # Token element/principle mapping (static - these don't change)
                TOKEN_METADATA = {
                    'UBEC': {'element': 'Air', 'ubuntu_principle': 'Diversity'},
                    'UBECrc': {'element': 'Water', 'ubuntu_principle': 'Reciprocity'},
                    'UBECgpi': {'element': 'Earth', 'ubuntu_principle': 'Mutualism'},
                    'UBECtt': {'element': 'Fire', 'ubuntu_principle': 'Regeneration'}
                }
                
                # v2.5.5: Get issuer addresses from system_settings table (database is source of truth)
                issuer_query = """
                    SELECT setting_key, setting_value
                    FROM ubec_main.system_settings
                    WHERE setting_key IN ('ubec_issuer', 'ubecrc_issuer', 'ubecgpi_issuer', 'ubectt_issuer')
                      AND is_active = true
                """
                issuer_results = await db.fetch_all(issuer_query)
                
                # Build issuer lookup
                issuer_map = {}
                for row in issuer_results:
                    key = row['setting_key']
                    if key == 'ubec_issuer':
                        issuer_map['UBEC'] = row['setting_value']
                    elif key == 'ubecrc_issuer':
                        issuer_map['UBECrc'] = row['setting_value']
                    elif key == 'ubecgpi_issuer':
                        issuer_map['UBECgpi'] = row['setting_value']
                    elif key == 'ubectt_issuer':
                        issuer_map['UBECtt'] = row['setting_value']
                
                # v2.5.5: Calculate directly from ubec_balances for accurate real-time data
                balance_query = """
                    SELECT 
                        token_code::text as asset_code,
                        COALESCE(SUM(balance), 0) as total_supply,
                        COUNT(DISTINCT account_id) as holder_count,
                        MAX(last_modified_at) as last_updated
                    FROM ubec_main.ubec_balances
                    WHERE balance > 0
                    GROUP BY token_code
                """
                balance_results = await db.fetch_all(balance_query)
                
                # Build balance lookup
                balance_data = {}
                for row in balance_results:
                    balance_data[row['asset_code']] = {
                        'total_supply': safe_float(row['total_supply']),
                        'holder_count': safe_int(row['holder_count']),
                        'last_updated': row['last_updated']
                    }
                
                # Build response ensuring all 4 tokens are always returned
                tokens = []
                for token_code in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
                    metadata = TOKEN_METADATA[token_code]
                    data = balance_data.get(token_code, {})
                    
                    tokens.append({
                        'code': token_code,
                        'name': token_code,
                        'issuer': issuer_map.get(token_code),
                        'element': metadata['element'],
                        'ubuntu_principle': f"{metadata['element']} ({metadata['ubuntu_principle']})",
                        'total_supply': data.get('total_supply', 0.0),
                        'holder_count': data.get('holder_count', 0),
                        'last_updated': data.get('last_updated').isoformat() if data.get('last_updated') else None
                    })
                
                return {
                    'tokens': tokens,
                    'count': len(tokens),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching tokens: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching token information: {str(e)}")
        
        @self.app.get("/api/v1/tokens/{token_code}/analysis", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_token_analysis(token_code: str, request: Request) -> Dict:
            """
            Get detailed analysis for a specific token.
            
            Rate limit: 100 requests/minute per IP
            
            Args:
                token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
            Returns:
            - Supply metrics
            - Distribution statistics
            - Holder analysis
            - Velocity metrics
            """
            try:
                db = await self.registry.get('database')
                
                # v2.4.1: Use asset_holder_analysis table with correct column names
                # Table columns: total_supply, total_holders, general_circulation, 
                # active_holders, gini_coefficient, whale_concentration_percent
                query = """
                    SELECT 
                        asset_code,
                        total_supply,
                        general_circulation as circulating_supply,
                        total_holders as holder_count,
                        active_holders,
                        gini_coefficient,
                        whale_concentration_percent as top_10_concentration,
                        0 as herfindahl_index,
                        0 as top_50_concentration,
                        0 as median_balance,
                        0 as mean_balance,
                        0 as velocity_7d,
                        0 as velocity_30d,
                        0 as transaction_count_7d,
                        0 as transaction_count_30d,
                        analysis_date as computed_at
                    FROM (
                        SELECT *,
                            ROW_NUMBER() OVER (PARTITION BY asset_code ORDER BY analysis_date DESC) as rn
                        FROM ubec_main.asset_holder_analysis
                        WHERE asset_code = $1
                    ) ranked
                    WHERE rn = 1
                """
                
                result = await db.fetch_one(query, (token_code,))
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No analysis found for token {token_code}"
                    )
                
                return {
                    'token': token_code,
                    'analysis': {
                        'supply': {
                            'total': safe_float(result['total_supply']),
                            'circulating': safe_float(result['circulating_supply'])
                        },
                        'distribution': {
                            'holder_count': safe_int(result['holder_count']),
                            'active_holders': safe_int(result['active_holders']),
                            'gini_coefficient': safe_float(result['gini_coefficient']),
                            'herfindahl_index': safe_float(result['herfindahl_index']),
                            'top_10_concentration': safe_float(result['top_10_concentration']),
                            'top_50_concentration': safe_float(result['top_50_concentration'])
                        },
                        'holder_metrics': {
                            'median_balance': safe_float(result['median_balance']),
                            'mean_balance': safe_float(result['mean_balance'])
                        },
                        'velocity': {
                            'velocity_7d': safe_float(result['velocity_7d']),
                            'velocity_30d': safe_float(result['velocity_30d']),
                            'tx_count_7d': safe_int(result['transaction_count_7d']),
                            'tx_count_30d': safe_int(result['transaction_count_30d'])
                        }
                    },
                    'computed_at': result['computed_at'].isoformat() if result['computed_at'] else None,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching token analysis: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching token analysis: {str(e)}")
        
        @self.app.get("/api/v1/accounts", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_accounts(request: Request, limit: int = 100, offset: int = 0) -> Dict:
            """
            Get list of accounts with basic information.
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - limit: Maximum number of accounts to return (default 100, max 1000)
            - offset: Number of accounts to skip (for pagination)
            
            Returns:
            - List of accounts with basic info
            - Pagination details
            """
            try:
                # Validate and constrain limit
                limit = min(max(1, limit), 1000)
                offset = max(0, offset)
                
                db = await self.registry.get('database')
                
                # v2.4.4: Use ubec_main.stellar_accounts with correct columns
                # Get accounts with explicit schema name
                query = """
                    SELECT 
                        sa.account_id,
                        sa.created_at,
                        sa.primary_element,
                        sa.last_activity_at,
                        COALESCE(hm.ubuntu_alignment_score, 0.0) as ubuntu_score
                    FROM ubec_main.stellar_accounts sa
                    LEFT JOIN (
                        SELECT DISTINCT ON (account_id) 
                            account_id,
                            ubuntu_alignment_score
                        FROM ubec_main.holonic_metrics
                        ORDER BY account_id, evaluation_date DESC
                    ) hm ON sa.account_id = hm.account_id
                    ORDER BY sa.created_at DESC
                    LIMIT $1 OFFSET $2
                """
                
                results = await db.fetch_all(query, (limit, offset))
                
                # Get total count
                count_query = "SELECT COUNT(*) FROM ubec_main.stellar_accounts"
                count_result = await db.fetch_one(count_query)
                total_count = count_result['count'] if count_result else 0
                
                accounts = []
                for row in results:
                    accounts.append({
                        'account_id': row['account_id'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'primary_element': row['primary_element'],
                        'last_activity_at': row['last_activity_at'].isoformat() if row['last_activity_at'] else None,
                        'ubuntu_score': safe_float(row['ubuntu_score'])
                    })
                
                return {
                    'accounts': accounts,
                    'pagination': {
                        'limit': limit,
                        'offset': offset,
                        'total': total_count,
                        'returned': len(accounts)
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching accounts: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching accounts: {str(e)}")
        
        @self.app.get("/api/v1/accounts/{account_id}", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_account_details(account_id: str, request: Request) -> Dict:
            """
            Get detailed information for a specific account.
            
            Rate limit: 100 requests/minute per IP
            
            Args:
                account_id: Stellar account ID
            
            Returns:
            - Account details with full Ubuntu scores
            - Balance information
            - Network position
            """
            try:
                db = await self.registry.get('database')
                
                # v2.4.4: Use ubec_main.stellar_accounts with correct columns
                query = """
                    SELECT 
                        sa.account_id,
                        sa.created_at,
                        sa.primary_element,
                        sa.token_holdings,
                        sa.last_activity_at,
                        sa.home_domain,
                        sa.metadata,
                        hm.ubuntu_alignment_score,
                        hm.holonic_category,
                        hm.raw_metrics
                    FROM ubec_main.stellar_accounts sa
                    LEFT JOIN (
                        SELECT DISTINCT ON (account_id)
                            account_id,
                            ubuntu_alignment_score,
                            holonic_category,
                            raw_metrics
                        FROM ubec_main.holonic_metrics
                        ORDER BY account_id, evaluation_date DESC
                    ) hm ON sa.account_id = hm.account_id
                    WHERE sa.account_id = $1
                """
                
                result = await db.fetch_one(query, (account_id,))
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Account {account_id} not found"
                    )
                
                return {
                    'account': {
                        'account_id': result['account_id'],
                        'created_at': result['created_at'].isoformat() if result['created_at'] else None,
                        'primary_element': result['primary_element'],
                        'token_holdings': result['token_holdings'] if result['token_holdings'] else [],
                        'last_activity_at': result['last_activity_at'].isoformat() if result['last_activity_at'] else None,
                        'home_domain': result['home_domain'],
                        'ubuntu_alignment_score': safe_float(result['ubuntu_alignment_score']),
                        'holonic_category': result['holonic_category'],
                        'metadata': result['metadata'] if result['metadata'] else {},
                        'raw_metrics': result['raw_metrics'] if result['raw_metrics'] else {}
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching account details: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching account details: {str(e)}")
        
        @self.app.get("/api/v1/distribution", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_distribution(request: Request) -> Dict:
            """
            Get current token distribution state using live calculation.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - Distribution percentages for the 65/30/5 model
            - Target vs actual allocations
            - Compliance status
            - Total supply including liquidity pools
            
            v2.6.0 FIX: Corrected key mapping from UBECDistributionService response.
            The service returns nested structure with keys like:
            - total_in_accounts, total_in_pools
            - administration['percentage'], administration['amount']
            - stewardship['percentage'], stewardship['amount']
            - general['percentage'], general['amount']
            
            Distribution Model:
            - General Distribution: 65% (DERIVED: 100% - Admin% - Stewardship%)
            - Token Ecosystem Stewardship: 30%
            - Administration: 5%
            """
            try:
                # Get distribution service for live calculation
                distribution_service = await self.registry.get('distribution')
                
                # Get current distribution with live data
                distribution_data = await distribution_service.get_current_distribution()
                
                # Extract nested values with safe defaults
                # Service returns: total_in_accounts, total_in_pools (not account_total, pool_total)
                # Service returns: administration{}, stewardship{}, general{} nested dicts
                admin_data = distribution_data.get('administration', {})
                steward_data = distribution_data.get('stewardship', {})
                general_data = distribution_data.get('general', {})
                
                # Format response for API consumers
                return {
                    'distribution': {
                        'model': '65/30/5',
                        'total_supply': str(distribution_data.get('total_supply', 0)),
                        'total_in_accounts': str(distribution_data.get('total_in_accounts', 0)),
                        'total_in_liquidity_pools': str(distribution_data.get('total_in_pools', 0)),
                        'categories': {
                            'general_distribution': {
                                'name': 'General Distribution',
                                'target_percentage': 65.0,
                                'actual_percentage': float(general_data.get('percentage', 0)),
                                'amount': str(general_data.get('amount', 0)),
                                'description': 'Tokens in general circulation (derived: 100% - Admin - Stewardship)'
                            },
                            'token_ecosystem_stewardship': {
                                'name': 'Token Ecosystem Stewardship',
                                'target_percentage': 30.0,
                                'actual_percentage': float(steward_data.get('percentage', 0)),
                                'amount': str(steward_data.get('amount', 0)),
                                'direct': str(steward_data.get('direct', 0)),
                                'lp_positions': str(steward_data.get('lp', 0)),
                                'description': 'Management, Infrastructure, and Liquidity accounts'
                            },
                            'administration': {
                                'name': 'Administration',
                                'target_percentage': 5.0,
                                'actual_percentage': float(admin_data.get('percentage', 0)),
                                'amount': str(admin_data.get('amount', 0)),
                                'direct': str(admin_data.get('direct', 0)),
                                'lp_positions': str(admin_data.get('lp', 0)),
                                'description': 'General administration account'
                            }
                        },
                        'compliance': {
                            'overall_compliant': distribution_data.get('overall_compliant', False),
                            'admin_compliant': distribution_data.get('admin_compliant', False),
                            'stewardship_compliant': distribution_data.get('stewardship_compliant', False),
                            'thresholds': {
                                'green_zone': '< 2% deviation',
                                'yellow_zone': '2-5% deviation',
                                'red_zone': '> 5% deviation'
                            }
                        }
                    },
                    'source': 'live_calculation',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching distribution: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error fetching distribution state: {str(e)}"
                )

        @self.app.get("/api/v1/token-audit/{token_code}", response_model=Dict)
        @limiter.limit("30/minute")
        async def get_token_audit(request: Request, token_code: str = "UBEC") -> Dict:
            """
            Get comprehensive UBEC token audit data for transparency reporting.
            
            NEW IN v2.5.5: Full token audit endpoint for dashboard display
            
            Rate limit: 30 requests/minute per IP (expensive query)
            
            Path Parameters:
            - token_code: Token to audit (UBEC, UBECrc, UBECgpi, UBECtt) - default UBEC
            
            Returns comprehensive audit data including:
            - Token info: code, element, ubuntu principle, issuer account
            - Summary: total_issued, total_distributed, percentage breakdowns, LP totals
            - General Distribution (65%) with all project accounts and balances
            - Token Ecosystem Stewardship (30%) with management, infrastructure, liquidity accounts
            - Liquidity pool breakdown (unlocked vs locked)
            - Administration (5%) account and balance
            - Compliance status indicators
            
            This endpoint provides full transparency for the UBEC DAO Protocol.
            
            v2.5.5: All addresses fetched from database (system_settings table)
            """
            try:
                db = await self.registry.get('database')
                
                # Validate token code
                token_code_upper = token_code.upper()
                
                # Token element/principle mapping (static - these don't change)
                TOKEN_METADATA = {
                    'UBEC': {'element': 'Air', 'principle': 'Diversity'},
                    'UBECrc': {'element': 'Water', 'principle': 'Reciprocity'},
                    'UBECgpi': {'element': 'Earth', 'principle': 'Mutualism'},
                    'UBECtt': {'element': 'Fire', 'principle': 'Regeneration'}
                }
                
                if token_code_upper not in TOKEN_METADATA:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid token code. Must be one of: {', '.join(TOKEN_METADATA.keys())}"
                    )
                
                token_meta = TOKEN_METADATA[token_code_upper]
                
                # v2.5.5: Get all settings from system_settings table (database is source of truth)
                settings_query = """
                    SELECT setting_key, setting_value
                    FROM ubec_main.system_settings
                    WHERE is_active = true
                      AND setting_key IN (
                          'ubec_issuer', 'ubecrc_issuer', 'ubecgpi_issuer', 'ubectt_issuer',
                          'general_account', 'administration_account',
                          'stewardship_management_account', 'stewardship_infrastructure_account', 
                          'stewardship_liquidity_account'
                      )
                """
                settings_results = await db.fetch_all(settings_query)
                
                # Build settings lookup
                settings = {}
                for row in settings_results:
                    settings[row['setting_key']] = row['setting_value']
                
                # Map issuer key based on token
                issuer_key_map = {
                    'UBEC': 'ubec_issuer',
                    'UBECrc': 'ubecrc_issuer',
                    'UBECgpi': 'ubecgpi_issuer',
                    'UBECtt': 'ubectt_issuer'
                }
                token_issuer = settings.get(issuer_key_map.get(token_code_upper, ''))
                
                # Distribution accounts from database
                general_account = settings.get('general_account')
                admin_account = settings.get('administration_account')
                steward_mgmt_account = settings.get('stewardship_management_account')
                steward_infra_account = settings.get('stewardship_infrastructure_account')
                steward_liq_account = settings.get('stewardship_liquidity_account')
                
                # Get project accounts from monitored_accounts table
                project_query = """
                    SELECT account_id, account_name, account_type, metadata
                    FROM ubec_main.monitored_accounts
                    WHERE account_type = 'project'
                      AND is_active = true
                """
                project_results = await db.fetch_all(project_query)
                
                # Build project accounts structure
                projects_dict = {}
                for row in project_results:
                    project_name = row['account_name'] or 'Unknown Project'
                    if project_name not in projects_dict:
                        projects_dict[project_name] = {
                            'name': project_name,
                            'accounts': []
                        }
                    projects_dict[project_name]['accounts'].append(row['account_id'])
                
                # Helper function to get account balance
                async def get_account_balance(account_id: str) -> float:
                    if not account_id:
                        return 0.0
                    query = """
                        SELECT COALESCE(balance, 0) as balance
                        FROM ubec_main.ubec_balances
                        WHERE account_id = $1 AND token_code::text = $2
                    """
                    result = await db.fetch_one(query, (account_id, token_code_upper))
                    return safe_float(result['balance']) if result else 0.0
                
                # Helper function to get LP balance for account
                async def get_lp_balance(account_id: str) -> float:
                    if not account_id:
                        return 0.0
                    query = """
                        SELECT COALESCE(SUM(ubec_balance), 0) as lp_balance
                        FROM ubec_main.liquidity_pool_owners
                        WHERE account_id = $1 AND token_code::text = $2
                    """
                    result = await db.fetch_one(query, (account_id, token_code_upper))
                    return safe_float(result['lp_balance']) if result else 0.0
                
                # Get total supply from all balances + liquidity pools
                # FIX v2.5.8: Total supply = account balances + LP reserves
                account_supply_query = """
                    SELECT COALESCE(SUM(balance), 0) as total
                    FROM ubec_main.ubec_balances
                    WHERE token_code::text = $1
                """
                account_result = await db.fetch_one(account_supply_query, (token_code_upper,))
                account_supply = safe_float(account_result['total']) if account_result else 0.0
                
                lp_supply_query = """
                    SELECT COALESCE(SUM(balance), 0) as total
                    FROM ubec_main.liquidity_pools
                    WHERE token_code::text = $1
                """
                lp_supply_result = await db.fetch_one(lp_supply_query, (token_code_upper,))
                lp_supply = safe_float(lp_supply_result['total']) if lp_supply_result else 0.0
                
                # Total supply = accounts + pools (expected ~191,766,039 for UBEC)
                total_supply = account_supply + lp_supply
                
                # Get total LP locked
                total_lp_query = """
                    SELECT COALESCE(SUM(balance), 0) as total_lp
                    FROM ubec_main.liquidity_pools
                    WHERE token_code::text = $1
                """
                lp_result = await db.fetch_one(total_lp_query, (token_code_upper,))
                total_lp_locked = safe_float(lp_result['total_lp']) if lp_result else 0.0
                
                # Build audit report
                
                # 1. General Distribution (65%)
                general_balance = await get_account_balance(general_account)
                
                general_projects = []
                general_total = general_balance
                
                for project_name, project_info in projects_dict.items():
                    project_balances = []
                    for acc_id in project_info['accounts']:
                        bal = await get_account_balance(acc_id)
                        project_balances.append({
                            'account_id': acc_id,
                            'balance': bal
                        })
                        general_total += bal
                    general_projects.append({
                        'name': project_info['name'],
                        'accounts': project_balances
                    })
                
                # 2. Token Ecosystem Stewardship (30%)
                # FIX v2.5.8: Get LP balance for ALL stewardship accounts, not just liquidity
                steward_mgmt_direct = await get_account_balance(steward_mgmt_account)
                steward_mgmt_lp = await get_lp_balance(steward_mgmt_account)
                steward_mgmt_balance = steward_mgmt_direct + steward_mgmt_lp
                
                steward_infra_direct = await get_account_balance(steward_infra_account)
                steward_infra_lp = await get_lp_balance(steward_infra_account)
                steward_infra_balance = steward_infra_direct + steward_infra_lp
                
                steward_liq_direct = await get_account_balance(steward_liq_account)
                steward_liq_lp = await get_lp_balance(steward_liq_account)
                steward_liq_balance = steward_liq_direct + steward_liq_lp
                
                # Total stewardship = all 3 accounts (direct + LP positions)
                stewardship_total = steward_mgmt_balance + steward_infra_balance + steward_liq_balance
                stewardship_lp_total = steward_mgmt_lp + steward_infra_lp + steward_liq_lp
                
                # 3. Administration (5%)
                admin_balance = await get_account_balance(admin_account)
                
                # Calculate percentages
                if total_supply > 0:
                    general_pct = (general_total / total_supply) * 100
                    stewardship_pct = (stewardship_total / total_supply) * 100
                    admin_pct = (admin_balance / total_supply) * 100
                else:
                    general_pct = stewardship_pct = admin_pct = 0.0
                
                # Build response
                audit_report = {
                    'token': {
                        'code': token_code_upper,
                        'element': token_meta['element'],
                        'ubuntu_principle': token_meta['principle'],
                        'issuer_account': token_issuer,
                        'total_tokens_issued': total_supply
                    },
                    'summary': {
                        'total_issued': round(total_supply, 7),
                        'total_in_accounts': round(account_supply, 7),
                        'total_in_liquidity_pools': round(lp_supply, 7),
                        'total_distributed': round(general_total + stewardship_total + admin_balance, 7),
                        'general_distribution_pct': round(general_pct, 4),
                        'stewardship_pct': round(stewardship_pct, 4),
                        'administration_pct': round(admin_pct, 4),
                        'distribution_model': '65/30/5'
                    },
                    'general_distribution': {
                        'target_percentage': 65.0,
                        'actual_percentage': round(general_pct, 2),
                        'total_tokens': round(general_total, 7),
                        'accounts': [
                            {
                                'purpose': 'General Distribution',
                                'account_id': general_account,
                                'balance': round(general_balance, 7)
                            }
                        ] if general_account else [],
                        'projects': general_projects
                    },
                    'token_ecosystem_stewardship': {
                        'target_percentage': 30.0,
                        'actual_percentage': round(stewardship_pct, 2),
                        'total_tokens': round(stewardship_total, 7),
                        'accounts': [
                            acc for acc in [
                                {
                                    'purpose': 'Stewardship Management',
                                    'account_id': steward_mgmt_account,
                                    'balance': round(steward_mgmt_balance, 7),
                                    'breakdown': {
                                        'direct': round(steward_mgmt_direct, 7),
                                        'lp_positions': round(steward_mgmt_lp, 7)
                                    }
                                } if steward_mgmt_account else None,
                                {
                                    'purpose': 'Infrastructure and Stakeholder Care',
                                    'account_id': steward_infra_account,
                                    'balance': round(steward_infra_balance, 7),
                                    'breakdown': {
                                        'direct': round(steward_infra_direct, 7),
                                        'lp_positions': round(steward_infra_lp, 7)
                                    }
                                } if steward_infra_account else None,
                                {
                                    'purpose': 'Liquidity Pool',
                                    'account_id': steward_liq_account,
                                    'balance': round(steward_liq_balance, 7),
                                    'breakdown': {
                                        'direct': round(steward_liq_direct, 7),
                                        'lp_positions': round(steward_liq_lp, 7)
                                    }
                                } if steward_liq_account else None
                            ] if acc is not None
                        ],
                        'liquidity_pools_summary': {
                            'total_locked_in_all_pools': round(total_lp_locked, 7),
                            'stewardship_total_in_lp': round(stewardship_lp_total, 7),
                            'stewardship_lp_by_account': {
                                'management': round(steward_mgmt_lp, 7),
                                'infrastructure': round(steward_infra_lp, 7),
                                'liquidity': round(steward_liq_lp, 7)
                            }
                        }
                    },
                    'administration': {
                        'target_percentage': 5.0,
                        'actual_percentage': round(admin_pct, 2),
                        'total_tokens': round(admin_balance, 7),
                        'accounts': [
                            {
                                'purpose': 'General Administration',
                                'account_id': admin_account,
                                'balance': round(admin_balance, 7)
                            }
                        ] if admin_account else []
                    },
                    'compliance': {
                        'general_compliant': 60.0 <= general_pct <= 70.0,
                        'stewardship_compliant': 25.0 <= stewardship_pct <= 35.0,
                        'administration_compliant': admin_pct <= 7.0,
                        'overall_compliant': (60.0 <= general_pct <= 70.0) and (25.0 <= stewardship_pct <= 35.0) and (admin_pct <= 7.0)
                    },
                    'disclaimer': (
                        "The information provided does not constitute investment advice, financial advice, "
                        "trading advice, or any other sort of advice. Ubuntu Economic Commons make no "
                        "recommendation as to the suitability of any tokens, products, services or transactions. "
                        "Please conduct your own due diligence and consult your financial advisor."
                    ),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                return audit_report
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching token audit: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching token audit: {str(e)}")
        
        @self.app.get("/api/v1/liquidity-pools", response_model=Dict)
        @limiter.limit("60/minute")
        async def get_liquidity_pools(
            request: Request, 
            token_code: Optional[str] = None
        ) -> Dict:
            """
            Get UBEC liquidity pool details.
            
            NEW IN v2.5.6: Comprehensive liquidity pool endpoint
            
            Rate limit: 60 requests/minute per IP
            
            Query Parameters:
            - token_code: Optional filter by token (UBEC, UBECrc, UBECgpi, UBECtt)
            
            Returns:
            - pools: Array of liquidity pool objects with:
              - id: Stellar liquidity pool ID (64-byte hex)
              - pair: Human-readable pair name (e.g., UBEC/XLM)
              - token_code: Which UBEC token is in this pool
              - element: Element classification (air/water/earth/fire)
              - ubec_position: Whether UBEC is asset_a or asset_b
              - asset_a: Asset A details (code, issuer)
              - asset_b: Asset B details (code, issuer)
              - reserves: Current reserve amounts
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
            - timestamp: Response timestamp
            
            Source: ubec_main.liquidity_pools, ubec_main.liquidity_pool_owners
            """
            try:
                db = await self.registry.get('database')
                
                # Build base query with optional token filter
                # v2.5.6: Query liquidity_pools with participant count from liquidity_pool_owners
                if token_code:
                    # Case-insensitive token filter
                    token_code_upper = token_code.upper()
                    valid_tokens = ['UBEC', 'UBECRC', 'UBECGPI', 'UBECTT']
                    if token_code_upper not in valid_tokens:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid token_code. Must be one of: UBEC, UBECrc, UBECgpi, UBECtt"
                        )
                    
                    pools_query = """
                        SELECT 
                            lp.id,
                            lp.pair,
                            lp.token_code::text as token_code,
                            lp.primary_element::text as element,
                            lp.ubec_asset_position,
                            lp.asset_a_code,
                            lp.asset_a_issuer,
                            lp.asset_b_code,
                            lp.asset_b_issuer,
                            lp.reserve_a,
                            lp.reserve_b,
                            lp.total_shares,
                            lp.balance,
                            lp.fee_bp,
                            lp.trustline_count,
                            lp.last_modified_at,
                            COALESCE(owner_counts.participant_count, 0) as participant_count
                        FROM ubec_main.liquidity_pools lp
                        LEFT JOIN (
                            SELECT liquidity_pool_id, COUNT(*) as participant_count
                            FROM ubec_main.liquidity_pool_owners
                            GROUP BY liquidity_pool_id
                        ) owner_counts ON lp.id = owner_counts.liquidity_pool_id
                        WHERE lp.token_code::text = $1
                        ORDER BY lp.balance DESC
                    """
                    pools_results = await db.fetch_all(pools_query, (token_code_upper,))
                else:
                    pools_query = """
                        SELECT 
                            lp.id,
                            lp.pair,
                            lp.token_code::text as token_code,
                            lp.primary_element::text as element,
                            lp.ubec_asset_position,
                            lp.asset_a_code,
                            lp.asset_a_issuer,
                            lp.asset_b_code,
                            lp.asset_b_issuer,
                            lp.reserve_a,
                            lp.reserve_b,
                            lp.total_shares,
                            lp.balance,
                            lp.fee_bp,
                            lp.trustline_count,
                            lp.last_modified_at,
                            COALESCE(owner_counts.participant_count, 0) as participant_count
                        FROM ubec_main.liquidity_pools lp
                        LEFT JOIN (
                            SELECT liquidity_pool_id, COUNT(*) as participant_count
                            FROM ubec_main.liquidity_pool_owners
                            GROUP BY liquidity_pool_id
                        ) owner_counts ON lp.id = owner_counts.liquidity_pool_id
                        ORDER BY lp.balance DESC
                    """
                    pools_results = await db.fetch_all(pools_query)
                
                # Build pools array
                pools = []
                total_value_locked = 0.0
                pools_by_token = {}
                
                for row in pools_results:
                    pool_balance = safe_float(row['balance'])
                    total_value_locked += pool_balance
                    
                    # Count pools by token
                    tk = row['token_code'] or 'UNKNOWN'
                    pools_by_token[tk] = pools_by_token.get(tk, 0) + 1
                    
                    pools.append({
                        'id': row['id'],
                        'pair': row['pair'],
                        'token_code': row['token_code'],
                        'element': row['element'],
                        'ubec_position': row['ubec_asset_position'],
                        'asset_a': {
                            'code': row['asset_a_code'],
                            'issuer': row['asset_a_issuer']
                        },
                        'asset_b': {
                            'code': row['asset_b_code'],
                            'issuer': row['asset_b_issuer']
                        },
                        'reserves': {
                            'asset_a': safe_float(row['reserve_a']),
                            'asset_b': safe_float(row['reserve_b'])
                        },
                        'total_shares': safe_float(row['total_shares']),
                        'balance': round(pool_balance, 7),
                        'fee_bp': safe_int(row['fee_bp']),
                        'trustline_count': safe_int(row['trustline_count']),
                        'participant_count': safe_int(row['participant_count']),
                        'last_modified_at': row['last_modified_at'].isoformat() if row['last_modified_at'] else None
                    })
                
                return {
                    'pools': pools,
                    'summary': {
                        'total_pools': len(pools),
                        'total_value_locked': round(total_value_locked, 7),
                        'pools_by_token': pools_by_token
                    },
                    'filter_applied': token_code.upper() if token_code else None,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching liquidity pools: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error fetching liquidity pools: {str(e)}"
                )
        
        @self.app.get("/api/v1/bioregions", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_bioregions(request: Request) -> Dict:
            """
            Get list of all bioregions with their health metrics.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - List of bioregions with basic info and health scores
            - Pagination details
            """
            try:
                db = await self.registry.get('database')
                
                # Get bioregions from holons table
                query = """
                    SELECT 
                        h.id as bioregion_id,
                        h.name,
                        h.description,
                        h.created_at,
                        h.metadata,
                        COALESCE(hm.ubuntu_alignment_score, 0.0) as health_score,
                        COALESCE(hm.autonomy_score, 0.0) as autonomy_score,
                        COALESCE(hm.integration_score, 0.0) as integration_score
                    FROM phenomenal.holons h
                    LEFT JOIN (
                        SELECT DISTINCT ON (holon_id)
                            holon_id,
                            ubuntu_alignment_score,
                            autonomy_score,
                            integration_score
                        FROM phenomenal.holon_metrics
                        ORDER BY holon_id, recorded_at DESC
                    ) hm ON h.id = hm.holon_id
                    WHERE h.holon_type = 'bioregion'
                    AND h.dissolved_at IS NULL
                    ORDER BY h.name
                """
                
                results = await db.fetch_all(query)
                
                bioregions = []
                for row in results:
                    bioregions.append({
                        'bioregion_id': row['bioregion_id'],
                        'name': row['name'],
                        'description': row['description'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'health_score': safe_float(row['health_score']),
                        'autonomy_score': safe_float(row['autonomy_score']),
                        'integration_score': safe_float(row['integration_score']),
                        'metadata': row['metadata'] if row['metadata'] else {}
                    })
                
                return {
                    'bioregions': bioregions,
                    'count': len(bioregions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching bioregions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching bioregions: {str(e)}")
        
        @self.app.get("/api/v1/bioregion-boundaries", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_bioregion_boundaries(request: Request) -> Dict:
            """
            Get comprehensive bioregion boundary data with GeoJSON geometries.
            
            NEW IN v2.4.0: Provides complete bioregion boundary information including
            ecological data, community info, and UBEC token allocations.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - boundaries: List of bioregion boundary objects with GeoJSON geometries
            - Each boundary includes:
              - Basic info (gid, name, code, status)
              - Geographic data (area, centroid, boundaries)
              - Ecological metadata (watershed, ecoregions, climate, ecosystems)
              - Community info (population, communities, indigenous territories)
              - Token allocations (UBEC, UBECrc, UBECgpi, UBECtt)
              - Submission and approval metadata
            - count: Total number of boundaries
            - timestamp: When this data was retrieved
            
            Source: phenomenal.bioregion_boundaries table
            """
            try:
                db = await self.registry.get('database')
                
                query = """
                    SELECT 
                        gid,
                        bioregion_name,
                        bioregion_code,
                        status,
                        ST_AsGeoJSON(geom)::json AS geometry,
                        area_sqkm,
                        centroid_lat,
                        centroid_lon,
                        primary_watershed,
                        ecoregion_level2,
                        ecoregion_level3,
                        elevation_range,
                        climate_zone,
                        dominant_ecosystems,
                        boundary_description,
                        boundary_rationale,
                        north_boundary,
                        east_boundary,
                        south_boundary,
                        west_boundary,
                        key_natural_features,
                        population_estimate,
                        major_communities,
                        indigenous_territories,
                        economic_focus,
                        submitted_by,
                        contact_email,
                        organization,
                        submission_date,
                        approved_date,
                        approved_by,
                        tags,
                        ubec_allocation,
                        water_allocation,
                        earth_allocation,
                        fire_allocation
                    FROM phenomenal.bioregion_boundaries
                    WHERE status IN ('proposed', 'under_review', 'approved', 'active')
                    ORDER BY bioregion_name
                """
                
                results = await db.fetch_all(query)
                
                boundaries = []
                for row in results:
                    boundaries.append({
                        'gid': row['gid'],
                        'bioregion_name': row['bioregion_name'],
                        'bioregion_code': row['bioregion_code'],
                        'status': row['status'],
                        'geometry': row['geometry'],
                        'geographic_data': {
                            'area_sqkm': float(row['area_sqkm']) if row['area_sqkm'] else 0.0,
                            'centroid': {
                                'latitude': float(row['centroid_lat']) if row['centroid_lat'] else None,
                                'longitude': float(row['centroid_lon']) if row['centroid_lon'] else None
                            },
                            'boundaries': {
                                'north': row['north_boundary'],
                                'east': row['east_boundary'],
                                'south': row['south_boundary'],
                                'west': row['west_boundary']
                            }
                        },
                        'ecological_data': {
                            'primary_watershed': row['primary_watershed'],
                            'ecoregion_level2': row['ecoregion_level2'],
                            'ecoregion_level3': row['ecoregion_level3'],
                            'elevation_range': row['elevation_range'],
                            'climate_zone': row['climate_zone'],
                            'dominant_ecosystems': row['dominant_ecosystems'],
                            'key_natural_features': row['key_natural_features']
                        },
                        'community_data': {
                            'population_estimate': row['population_estimate'],
                            'major_communities': row['major_communities'],
                            'indigenous_territories': row['indigenous_territories'],
                            'economic_focus': row['economic_focus']
                        },
                        'token_allocations': {
                            'ubec': float(row['ubec_allocation']) if row['ubec_allocation'] else 0.0,
                            'ubecrc': float(row['water_allocation']) if row['water_allocation'] else 0.0,
                            'ubecgpi': float(row['earth_allocation']) if row['earth_allocation'] else 0.0,
                            'ubectt': float(row['fire_allocation']) if row['fire_allocation'] else 0.0
                        },
                        'metadata': {
                            'description': row['boundary_description'],
                            'rationale': row['boundary_rationale'],
                            'tags': row['tags'].split(',') if row['tags'] else [],
                            'submitted_by': row['submitted_by'],
                            'contact_email': row['contact_email'],
                            'organization': row['organization'],
                            'submission_date': row['submission_date'].isoformat() if row['submission_date'] else None,
                            'approved_date': row['approved_date'].isoformat() if row['approved_date'] else None,
                            'approved_by': row['approved_by']
                        }
                    })
                
                return {
                    'boundaries': boundaries,
                    'count': len(boundaries),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching bioregion boundaries: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching bioregion boundaries: {str(e)}")
        
        @self.app.get("/api/v1/points-of-interest", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_points_of_interest(request: Request, 
                                        poi_type: Optional[str] = None,
                                        bioregion_gid: Optional[int] = None,
                                        visibility: Optional[str] = None,
                                        limit: int = 100) -> Dict:
            """
            Get points of interest (farms, community centers, landmarks, resources).
            
            NEW IN v2.4.0: Provides comprehensive POI data with filtering capabilities.
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - poi_type: Filter by type (farm, community_center, resource, landmark, etc.)
            - bioregion_gid: Filter by bioregion GID
            - visibility: Filter by visibility (public, bioregion_only, private)
            - limit: Maximum number of POIs to return (default 100, max 500)
            
            Returns:
            - points: List of POI objects with GeoJSON point geometries
            - Each POI includes:
              - Basic info (gid, name, code, type, status)
              - Location data (coordinates, elevation, address)
              - Bioregion association (if within a bioregion)
              - Description and media (images, links)
              - Contact and operational info
              - UBEC token associations
            - count: Total number of POIs returned
            - filters: Applied filter values
            - timestamp: When this data was retrieved
            
            Source: phenomenal.points_of_interest table
            """
            try:
                # Validate and constrain limit
                limit = min(max(1, limit), 500)
                
                db = await self.registry.get('database')
                
                # Build query with optional filters
                query = """
                    SELECT 
                        gid,
                        poi_name,
                        poi_code,
                        poi_type,
                        status,
                        ST_AsGeoJSON(geom)::json AS geometry,
                        latitude,
                        longitude,
                        elevation_m,
                        bioregion_gid,
                        bioregion_name,
                        address,
                        locality,
                        region,
                        country,
                        short_description,
                        full_description,
                        keywords,
                        primary_image_path,
                        website_url,
                        contact_name,
                        contact_email,
                        contact_phone,
                        operating_hours,
                        seasonal_notes,
                        visibility,
                        ubec_account_id,
                        associated_tokens,
                        created_at,
                        updated_at
                    FROM phenomenal.points_of_interest
                    WHERE status = 'active'
                """
                
                params = []
                param_count = 0
                
                if poi_type:
                    param_count += 1
                    query += f" AND poi_type = ${param_count}"
                    params.append(poi_type)
                
                if bioregion_gid:
                    param_count += 1
                    query += f" AND bioregion_gid = ${param_count}"
                    params.append(bioregion_gid)
                
                if visibility:
                    param_count += 1
                    query += f" AND visibility = ${param_count}"
                    params.append(visibility)
                
                param_count += 1
                query += f" ORDER BY poi_name LIMIT ${param_count}"
                params.append(limit)
                
                results = await db.fetch_all(query, tuple(params)) if params else await db.fetch_all(query)
                
                points = []
                for row in results:
                    points.append({
                        'gid': row['gid'],
                        'poi_name': row['poi_name'],
                        'poi_code': row['poi_code'],
                        'poi_type': row['poi_type'],
                        'status': row['status'],
                        'geometry': row['geometry'],
                        'location': {
                            'latitude': float(row['latitude']) if row['latitude'] else None,
                            'longitude': float(row['longitude']) if row['longitude'] else None,
                            'elevation_m': float(row['elevation_m']) if row['elevation_m'] else None,
                            'address': row['address'],
                            'locality': row['locality'],
                            'region': row['region'],
                            'country': row['country']
                        },
                        'bioregion': {
                            'gid': row['bioregion_gid'],
                            'name': row['bioregion_name']
                        } if row['bioregion_gid'] else None,
                        'description': {
                            'short': row['short_description'],
                            'full': row['full_description'],
                            'keywords': row['keywords'].split(',') if row['keywords'] else []
                        },
                        'media': {
                            'primary_image': row['primary_image_path'],
                            'website': row['website_url']
                        },
                        'contact': {
                            'name': row['contact_name'],
                            'email': row['contact_email'],
                            'phone': row['contact_phone']
                        },
                        'operations': {
                            'hours': row['operating_hours'],
                            'seasonal_notes': row['seasonal_notes'],
                            'visibility': row['visibility']
                        },
                        'ubec_integration': {
                            'account_id': row['ubec_account_id'],
                            'associated_tokens': row['associated_tokens'] if row['associated_tokens'] else []
                        },
                        'timestamps': {
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                        }
                    })
                
                return {
                    'points': points,
                    'count': len(points),
                    'filters': {
                        'poi_type': poi_type,
                        'bioregion_gid': bioregion_gid,
                        'visibility': visibility,
                        'limit': limit
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching points of interest: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching points of interest: {str(e)}")
        
        @self.app.get("/api/v1/holonic-scores", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_holonic_scores(
            request: Request,
            include_accounts: bool = False,
            limit: int = 100,
            offset: int = 0,
            category: Optional[str] = None
        ) -> Dict:
            """
            Get holonic evaluation scores with optional individual account data.
            
            NEW IN v2.7.0: Enhanced endpoint for frontend visualization support
            - Optional include_accounts parameter returns full dimension scores per account
            - Enables frontend to generate visualization reports equivalent to holonic_visualizer
            - Provides base data for third-party evaluation implementations
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - include_accounts: If true, include individual account evaluations (default: false)
            - limit: Maximum accounts to return when include_accounts=true (default: 100, max: 500)
            - offset: Pagination offset for accounts (default: 0)
            - category: Filter by holonic category (Observer, Participant, Contributor, Integrator, Exemplar)
            
            Returns (when include_accounts=false - default, backward compatible):
            - ubuntu_principles: Aggregate scores for each Ubuntu principle (diversity, reciprocity, mutualism, regeneration)
            - account_count: Total number of evaluated accounts
            - timestamp: Response timestamp
            
            Returns (when include_accounts=true):
            - accounts: Array of individual account evaluations with:
              - account_id: Stellar account ID
              - holonic_category: Category classification
              - composite_score: Overall holonic score (0-1)
              - dimension_scores: All 5 dimension scores for visualization
                - autonomy_integration: Balance of autonomy and integration
                - multi_scale: Multi-scale participation
                - regenerative_impact: Regenerative contribution
                - network_contribution: Network value added
                - ubuntu_alignment: Ubuntu philosophy alignment
              - ubuntu_principles: Element-specific scores (from ubec_holonic_metrics)
                - diversity: Air/UBEC principle score
                - reciprocity: Water/UBECrc principle score
                - mutualism: Earth/UBECgpi principle score
                - regeneration: Fire/UBECtt principle score
              - evaluation_date: When evaluation was performed
            - summary: Network-wide statistics
              - total_evaluated: Total accounts with evaluations
              - category_distribution: Count per holonic category
              - score_statistics: mean, median, min, max of composite scores
              - dimension_statistics: Statistics per dimension
              - ubuntu_principles: Aggregate Ubuntu principle metrics
            - pagination: Limit, offset, total, returned counts
            - timestamp: Response timestamp
            
            Source Tables:
            - ubec_main.holonic_metrics: 5 dimension scores, composite score, category
            - ubec_main.ubec_holonic_metrics: 4 Ubuntu principle scores (element-specific)
            """
            try:
                db = await self.registry.get('database')
                
                # Validate and constrain parameters
                limit = min(max(1, limit), 500)
                offset = max(0, offset)
                
                # Validate category if provided
                valid_categories = ['Observer', 'Participant', 'Contributor', 'Integrator', 'Exemplar']
                if category:
                    # Case-insensitive match with proper title case
                    category_title = category.title()
                    if category_title not in valid_categories:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                        )
                    category = category_title
                
                if include_accounts:
                    # ================================================================
                    # ENHANCED MODE: Return individual account data with dimensions
                    # ================================================================
                    
                    # Build query for individual accounts with all dimension scores
                    # Join holonic_metrics (5 dimensions) with ubec_holonic_metrics (4 Ubuntu principles)
                    category_filter = "AND hm.holonic_category = $3" if category else ""
                    
                    accounts_query = f"""
                        SELECT 
                            hm.account_id,
                            hm.holonic_category,
                            hm.composite_score,
                            hm.autonomy_integration_score,
                            hm.multi_scale_score,
                            hm.regenerative_impact_score,
                            hm.network_contribution_score,
                            hm.ubuntu_alignment_score,
                            hm.evaluation_date,
                            hm.raw_metrics,
                            -- Ubuntu principle scores from ubec_holonic_metrics (pivoted)
                            MAX(CASE WHEN uhm.principle = 'diversity' THEN uhm.score END) as diversity_score,
                            MAX(CASE WHEN uhm.principle = 'reciprocity' THEN uhm.score END) as reciprocity_score,
                            MAX(CASE WHEN uhm.principle = 'mutualism' THEN uhm.score END) as mutualism_score,
                            MAX(CASE WHEN uhm.principle = 'regeneration' THEN uhm.score END) as regeneration_score
                        FROM ubec_main.holonic_metrics hm
                        LEFT JOIN ubec_main.ubec_holonic_metrics uhm 
                            ON hm.account_id = uhm.account_id
                            AND uhm.calculated_at >= hm.evaluation_date - INTERVAL '1 day'
                        WHERE hm.evaluation_date = (
                            SELECT MAX(evaluation_date) 
                            FROM ubec_main.holonic_metrics hm2 
                            WHERE hm2.account_id = hm.account_id
                        )
                        {category_filter}
                        GROUP BY 
                            hm.account_id, hm.holonic_category, hm.composite_score,
                            hm.autonomy_integration_score, hm.multi_scale_score,
                            hm.regenerative_impact_score, hm.network_contribution_score,
                            hm.ubuntu_alignment_score, hm.evaluation_date, hm.raw_metrics
                        ORDER BY hm.composite_score DESC
                        LIMIT $1 OFFSET $2
                    """
                    
                    if category:
                        accounts_results = await db.fetch_all(accounts_query, (limit, offset, category))
                    else:
                        accounts_results = await db.fetch_all(accounts_query, (limit, offset))
                    
                    # Build accounts array
                    accounts = []
                    for row in accounts_results:
                        accounts.append({
                            'account_id': row['account_id'],
                            'holonic_category': row['holonic_category'],
                            'composite_score': safe_float(row['composite_score']),
                            'dimension_scores': {
                                'autonomy_integration': safe_float(row['autonomy_integration_score']),
                                'multi_scale': safe_float(row['multi_scale_score']),
                                'regenerative_impact': safe_float(row['regenerative_impact_score']),
                                'network_contribution': safe_float(row['network_contribution_score']),
                                'ubuntu_alignment': safe_float(row['ubuntu_alignment_score'])
                            },
                            'ubuntu_principles': {
                                'diversity': safe_float(row['diversity_score']),
                                'reciprocity': safe_float(row['reciprocity_score']),
                                'mutualism': safe_float(row['mutualism_score']),
                                'regeneration': safe_float(row['regeneration_score'])
                            },
                            'evaluation_date': row['evaluation_date'].isoformat() if row['evaluation_date'] else None
                        })
                    
                    # Get total count for pagination
                    count_query = """
                        SELECT COUNT(DISTINCT account_id) as total
                        FROM ubec_main.holonic_metrics
                    """
                    if category:
                        count_query = """
                            SELECT COUNT(DISTINCT account_id) as total
                            FROM ubec_main.holonic_metrics
                            WHERE holonic_category = $1
                        """
                        count_result = await db.fetch_one(count_query, (category,))
                    else:
                        count_result = await db.fetch_one(count_query)
                    total_count = safe_int(count_result['total']) if count_result else 0
                    
                    # Get category distribution
                    category_dist_query = """
                        SELECT holonic_category, COUNT(DISTINCT account_id) as count
                        FROM ubec_main.holonic_metrics
                        WHERE evaluation_date = (
                            SELECT MAX(evaluation_date) 
                            FROM ubec_main.holonic_metrics hm2 
                            WHERE hm2.account_id = ubec_main.holonic_metrics.account_id
                        )
                        GROUP BY holonic_category
                        ORDER BY 
                            CASE holonic_category
                                WHEN 'Exemplar' THEN 1
                                WHEN 'Integrator' THEN 2
                                WHEN 'Contributor' THEN 3
                                WHEN 'Participant' THEN 4
                                WHEN 'Observer' THEN 5
                            END
                    """
                    category_results = await db.fetch_all(category_dist_query)
                    category_distribution = {row['holonic_category']: safe_int(row['count']) for row in category_results}
                    
                    # Get score statistics
                    stats_query = """
                        WITH latest_scores AS (
                            SELECT composite_score
                            FROM ubec_main.holonic_metrics
                            WHERE evaluation_date = (
                                SELECT MAX(evaluation_date) 
                                FROM ubec_main.holonic_metrics hm2 
                                WHERE hm2.account_id = ubec_main.holonic_metrics.account_id
                            )
                        )
                        SELECT 
                            AVG(composite_score) as mean,
                            MIN(composite_score) as min,
                            MAX(composite_score) as max,
                            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY composite_score) as median
                        FROM latest_scores
                    """
                    stats_result = await db.fetch_one(stats_query)
                    
                    # Get dimension statistics
                    dim_stats_query = """
                        WITH latest_metrics AS (
                            SELECT 
                                autonomy_integration_score,
                                multi_scale_score,
                                regenerative_impact_score,
                                network_contribution_score,
                                ubuntu_alignment_score
                            FROM ubec_main.holonic_metrics
                            WHERE evaluation_date = (
                                SELECT MAX(evaluation_date) 
                                FROM ubec_main.holonic_metrics hm2 
                                WHERE hm2.account_id = ubec_main.holonic_metrics.account_id
                            )
                        )
                        SELECT 
                            AVG(autonomy_integration_score) as avg_autonomy,
                            MIN(autonomy_integration_score) as min_autonomy,
                            MAX(autonomy_integration_score) as max_autonomy,
                            AVG(multi_scale_score) as avg_multi_scale,
                            MIN(multi_scale_score) as min_multi_scale,
                            MAX(multi_scale_score) as max_multi_scale,
                            AVG(regenerative_impact_score) as avg_regenerative,
                            MIN(regenerative_impact_score) as min_regenerative,
                            MAX(regenerative_impact_score) as max_regenerative,
                            AVG(network_contribution_score) as avg_network,
                            MIN(network_contribution_score) as min_network,
                            MAX(network_contribution_score) as max_network,
                            AVG(ubuntu_alignment_score) as avg_ubuntu,
                            MIN(ubuntu_alignment_score) as min_ubuntu,
                            MAX(ubuntu_alignment_score) as max_ubuntu
                        FROM latest_metrics
                    """
                    dim_stats_result = await db.fetch_one(dim_stats_query)
                    
                    # Get Ubuntu principles aggregate (same as non-include_accounts mode)
                    ubuntu_query = """
                        WITH ubuntu_metrics AS (
                            SELECT 
                                account_id,
                                MAX(CASE WHEN principle = 'diversity' THEN score END) as diversity_score,
                                MAX(CASE WHEN principle = 'reciprocity' THEN score END) as reciprocity_score,
                                MAX(CASE WHEN principle = 'mutualism' THEN score END) as mutualism_score,
                                MAX(CASE WHEN principle = 'regeneration' THEN score END) as regeneration_score
                            FROM ubec_main.ubec_holonic_metrics
                            WHERE calculated_at >= NOW() - INTERVAL '7 days'
                            GROUP BY account_id
                        )
                        SELECT 
                            AVG(diversity_score) as avg_diversity,
                            MIN(diversity_score) as min_diversity,
                            MAX(diversity_score) as max_diversity,
                            AVG(reciprocity_score) as avg_reciprocity,
                            MIN(reciprocity_score) as min_reciprocity,
                            MAX(reciprocity_score) as max_reciprocity,
                            AVG(mutualism_score) as avg_mutualism,
                            MIN(mutualism_score) as min_mutualism,
                            MAX(mutualism_score) as max_mutualism,
                            AVG(regeneration_score) as avg_regeneration,
                            MIN(regeneration_score) as min_regeneration,
                            MAX(regeneration_score) as max_regeneration
                        FROM ubuntu_metrics
                    """
                    ubuntu_result = await db.fetch_one(ubuntu_query)
                    
                    return {
                        'accounts': accounts,
                        'summary': {
                            'total_evaluated': total_count,
                            'category_distribution': category_distribution,
                            'score_statistics': {
                                'mean': safe_float(stats_result['mean']) if stats_result else 0.0,
                                'median': safe_float(stats_result['median']) if stats_result else 0.0,
                                'min': safe_float(stats_result['min']) if stats_result else 0.0,
                                'max': safe_float(stats_result['max']) if stats_result else 0.0
                            },
                            'dimension_statistics': {
                                'autonomy_integration': {
                                    'mean': safe_float(dim_stats_result['avg_autonomy']) if dim_stats_result else 0.0,
                                    'min': safe_float(dim_stats_result['min_autonomy']) if dim_stats_result else 0.0,
                                    'max': safe_float(dim_stats_result['max_autonomy']) if dim_stats_result else 0.0
                                },
                                'multi_scale': {
                                    'mean': safe_float(dim_stats_result['avg_multi_scale']) if dim_stats_result else 0.0,
                                    'min': safe_float(dim_stats_result['min_multi_scale']) if dim_stats_result else 0.0,
                                    'max': safe_float(dim_stats_result['max_multi_scale']) if dim_stats_result else 0.0
                                },
                                'regenerative_impact': {
                                    'mean': safe_float(dim_stats_result['avg_regenerative']) if dim_stats_result else 0.0,
                                    'min': safe_float(dim_stats_result['min_regenerative']) if dim_stats_result else 0.0,
                                    'max': safe_float(dim_stats_result['max_regenerative']) if dim_stats_result else 0.0
                                },
                                'network_contribution': {
                                    'mean': safe_float(dim_stats_result['avg_network']) if dim_stats_result else 0.0,
                                    'min': safe_float(dim_stats_result['min_network']) if dim_stats_result else 0.0,
                                    'max': safe_float(dim_stats_result['max_network']) if dim_stats_result else 0.0
                                },
                                'ubuntu_alignment': {
                                    'mean': safe_float(dim_stats_result['avg_ubuntu']) if dim_stats_result else 0.0,
                                    'min': safe_float(dim_stats_result['min_ubuntu']) if dim_stats_result else 0.0,
                                    'max': safe_float(dim_stats_result['max_ubuntu']) if dim_stats_result else 0.0
                                }
                            },
                            'ubuntu_principles': {
                                'diversity': {
                                    'average': safe_float(ubuntu_result['avg_diversity']) if ubuntu_result else 0.0,
                                    'min': safe_float(ubuntu_result['min_diversity']) if ubuntu_result else 0.0,
                                    'max': safe_float(ubuntu_result['max_diversity']) if ubuntu_result else 0.0
                                },
                                'reciprocity': {
                                    'average': safe_float(ubuntu_result['avg_reciprocity']) if ubuntu_result else 0.0,
                                    'min': safe_float(ubuntu_result['min_reciprocity']) if ubuntu_result else 0.0,
                                    'max': safe_float(ubuntu_result['max_reciprocity']) if ubuntu_result else 0.0
                                },
                                'mutualism': {
                                    'average': safe_float(ubuntu_result['avg_mutualism']) if ubuntu_result else 0.0,
                                    'min': safe_float(ubuntu_result['min_mutualism']) if ubuntu_result else 0.0,
                                    'max': safe_float(ubuntu_result['max_mutualism']) if ubuntu_result else 0.0
                                },
                                'regeneration': {
                                    'average': safe_float(ubuntu_result['avg_regeneration']) if ubuntu_result else 0.0,
                                    'min': safe_float(ubuntu_result['min_regeneration']) if ubuntu_result else 0.0,
                                    'max': safe_float(ubuntu_result['max_regeneration']) if ubuntu_result else 0.0
                                }
                            }
                        },
                        'pagination': {
                            'limit': limit,
                            'offset': offset,
                            'total': total_count,
                            'returned': len(accounts),
                            'has_more': offset + len(accounts) < total_count
                        },
                        'filter_applied': {'category': category} if category else None,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                
                else:
                    # ================================================================
                    # DEFAULT MODE: Return aggregate statistics only (backward compatible)
                    # ================================================================
                    
                    # v2.4.0: CORRECTED query for ubec_holonic_metrics table
                    # Table has 'principle' column (enum), not 'metric_name'/'metric_value'
                    # principle values: 'diversity', 'reciprocity', 'mutualism', 'regeneration'
                    query = """
                        WITH ubuntu_metrics AS (
                            SELECT 
                                account_id,
                                MAX(CASE WHEN principle = 'diversity' THEN score END) as diversity_score,
                                MAX(CASE WHEN principle = 'reciprocity' THEN score END) as reciprocity_score,
                                MAX(CASE WHEN principle = 'mutualism' THEN score END) as mutualism_score,
                                MAX(CASE WHEN principle = 'regeneration' THEN score END) as regeneration_score
                            FROM ubec_main.ubec_holonic_metrics
                            WHERE calculated_at >= NOW() - INTERVAL '7 days'
                            GROUP BY account_id
                        )
                        SELECT 
                            AVG(diversity_score) as avg_diversity,
                            MIN(diversity_score) as min_diversity,
                            MAX(diversity_score) as max_diversity,
                            AVG(reciprocity_score) as avg_reciprocity,
                            MIN(reciprocity_score) as min_reciprocity,
                            MAX(reciprocity_score) as max_reciprocity,
                            AVG(mutualism_score) as avg_mutualism,
                            MIN(mutualism_score) as min_mutualism,
                            MAX(mutualism_score) as max_mutualism,
                            AVG(regeneration_score) as avg_regeneration,
                            MIN(regeneration_score) as min_regeneration,
                            MAX(regeneration_score) as max_regeneration,
                            COUNT(*) as account_count
                        FROM ubuntu_metrics
                    """
                    
                    result = await db.fetch_one(query)
                    
                    # v2.3.8: Use safe_float() to handle NULL aggregate results
                    return {
                        'ubuntu_principles': {
                            'diversity': {
                                'average': safe_float(result['avg_diversity']),
                                'min': safe_float(result['min_diversity']),
                                'max': safe_float(result['max_diversity'])
                            },
                            'reciprocity': {
                                'average': safe_float(result['avg_reciprocity']),
                                'min': safe_float(result['min_reciprocity']),
                                'max': safe_float(result['max_reciprocity'])
                            },
                            'mutualism': {
                                'average': safe_float(result['avg_mutualism']),
                                'min': safe_float(result['min_mutualism']),
                                'max': safe_float(result['max_mutualism'])
                            },
                            'regeneration': {
                                'average': safe_float(result['avg_regeneration']),
                                'min': safe_float(result['min_regeneration']),
                                'max': safe_float(result['max_regeneration'])
                            }
                        },
                        'account_count': safe_int(result['account_count']),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching holonic scores: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching holonic scores: {str(e)}")
        
        @self.app.get("/api/v1/transactions/recent", response_model=Dict)
        @limiter.limit("60/minute")
        async def get_recent_transactions(request: Request, limit: int = 50, asset_code: Optional[str] = None) -> Dict:
            """
            Get recent UBEC token transactions across the network.
            
            Rate limit: 60 requests/minute per IP (expensive query)
            
            Query Parameters:
            - limit: Maximum number of transactions to return (default 50, max 200)
            - asset_code: Optional filter by specific UBEC token (UBEC, UBECrc, UBECgpi, UBECtt)
                          Case-insensitive. If not specified, shows all UBEC token transactions.
            
            Returns:
            - List of recent UBEC token transactions with operation details:
              - transaction_hash: Unique transaction identifier
              - ledger_sequence: Ledger number
              - created_at: Transaction timestamp
              - source_account: Account that submitted the transaction
              - successful: Whether transaction succeeded
              - operations: Array of UBEC operation details with:
                - type: Operation type (PAYMENT, CHANGE_TRUST, MANAGE_SELL_OFFER, etc.)
                - asset_code: UBEC token code (UBEC, UBECrc, UBECgpi, UBECtt)
                - amount: Amount transferred
                - from_account: Source of funds
                - to_account: Destination of funds
                - For TRADE operations (manage_sell_offer, manage_buy_offer, path_payment):
                  - exchange_source_asset: Token being sold/sent
                  - exchange_source_amount: Amount being sold/sent
                  - exchange_dest_asset: Token being bought/received
                  - exchange_dest_amount: Amount being bought/received
            - Pagination info
            - Applied filter (if any)
            
            NOTE: Only shows transactions involving UBEC ecosystem tokens.
            XLM-only transactions are excluded.
            
            SCHEMA FIX v2.5.4: Include exchange/trade details for swap operations
            - Problem: Trade operations didn't show which token was exchanged for which
            - Solution: Include exchange_source_asset/amount and exchange_dest_asset/amount
            - Impact: Dashboard can now show trade direction (e.g., UBEC → UBECrc)
            
            MAINTAINED FROM v2.5.3: Filter to UBEC tokens only (exclude XLM)
            MAINTAINED FROM v2.5.2: Operation-level details (type, amount, from/to)
            """
            try:
                # Validate and constrain limit
                limit = min(max(1, limit), 200)
                
                db = await self.registry.get('database')
                
                # UBEC ecosystem tokens only
                UBEC_TOKENS = ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                
                # Trade operation types that involve exchanges
                TRADE_TYPES = ('manage_sell_offer', 'manage_buy_offer', 'create_passive_sell_offer',
                               'path_payment_strict_send', 'path_payment_strict_receive')
                
                # v2.5.4: Query includes exchange columns for trade operations
                if asset_code:
                    # Filter by specific UBEC asset code (case-insensitive)
                    asset_code_upper = asset_code.upper()
                    
                    # Validate it's a UBEC token
                    if asset_code_upper not in UBEC_TOKENS:
                        return {
                            'transactions': [],
                            'filter': {'asset_code': asset_code, 'error': f'Invalid UBEC token. Must be one of: {", ".join(UBEC_TOKENS)}'},
                            'pagination': {'limit': limit, 'total': 0, 'returned': 0},
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    
                    # Get transactions with operations for this specific UBEC token
                    # Include exchange columns for trade operations
                    query = """
                        SELECT 
                            t.transaction_hash,
                            COALESCE(NULLIF(t.ledger, 0), NULLIF(t.ledger_sequence, 0), 0) as ledger_sequence,
                            t.created_at,
                            t.source_account,
                            COALESCE(t.successful, true) as successful,
                            o.type as op_type,
                            o.asset_code::text as op_asset_code,
                            o.amount as op_amount,
                            COALESCE(o.from_account, o.source_account, t.source_account) as op_from_account,
                            o.to_account as op_to_account,
                            o.exchange_source_asset,
                            o.exchange_source_amount,
                            o.exchange_dest_asset,
                            o.exchange_dest_amount
                        FROM ubec_main.stellar_transactions t
                        INNER JOIN ubec_main.stellar_operations o 
                            ON t.transaction_hash = o.transaction_hash
                        WHERE o.asset_code::text = $1
                        ORDER BY t.created_at DESC, o.id
                        LIMIT $2
                    """
                    results = await db.fetch_all(query, (asset_code_upper, limit * 3))
                    
                    # Count distinct transactions
                    count_query = """
                        SELECT COUNT(DISTINCT t.transaction_hash) 
                        FROM ubec_main.stellar_transactions t
                        INNER JOIN ubec_main.stellar_operations o 
                            ON t.transaction_hash = o.transaction_hash
                        WHERE o.asset_code::text = $1
                    """
                    count_result = await db.fetch_one(count_query, (asset_code_upper,))
                else:
                    # No filter - return all UBEC token transactions (exclude XLM)
                    # Include exchange columns for trade operations
                    query = """
                        SELECT 
                            t.transaction_hash,
                            COALESCE(NULLIF(t.ledger, 0), NULLIF(t.ledger_sequence, 0), 0) as ledger_sequence,
                            t.created_at,
                            t.source_account,
                            COALESCE(t.successful, true) as successful,
                            o.type as op_type,
                            o.asset_code::text as op_asset_code,
                            o.amount as op_amount,
                            COALESCE(o.from_account, o.source_account, t.source_account) as op_from_account,
                            o.to_account as op_to_account,
                            o.exchange_source_asset,
                            o.exchange_source_amount,
                            o.exchange_dest_asset,
                            o.exchange_dest_amount
                        FROM ubec_main.stellar_transactions t
                        INNER JOIN ubec_main.stellar_operations o 
                            ON t.transaction_hash = o.transaction_hash
                        WHERE o.asset_code::text IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                        ORDER BY t.created_at DESC, o.id
                        LIMIT $1
                    """
                    results = await db.fetch_all(query, (limit * 3,))
                    
                    # Count distinct UBEC transactions
                    count_query = """
                        SELECT COUNT(DISTINCT t.transaction_hash) 
                        FROM ubec_main.stellar_transactions t
                        INNER JOIN ubec_main.stellar_operations o 
                            ON t.transaction_hash = o.transaction_hash
                        WHERE o.asset_code::text IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                    """
                    count_result = await db.fetch_one(count_query)
                
                total_count = count_result['count'] if count_result else 0
                
                # Group operations by transaction
                transactions_dict = {}
                for row in results:
                    tx_hash = row['transaction_hash']
                    
                    if tx_hash not in transactions_dict:
                        transactions_dict[tx_hash] = {
                            'transaction_hash': tx_hash,
                            'ledger_sequence': row['ledger_sequence'] or 0,
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'source_account': row['source_account'],
                            'successful': row['successful'],
                            'operations': []
                        }
                    
                    # Add operation if it exists and is a UBEC token
                    if row['op_type'] and row['op_asset_code'] in UBEC_TOKENS:
                        op_type = row['op_type']
                        # Convert enum to string if needed
                        if hasattr(op_type, 'value'):
                            op_type = op_type.value
                        elif hasattr(op_type, 'name'):
                            op_type = op_type.name
                        else:
                            op_type = str(op_type)
                        
                        op_type_str = op_type.lower()
                        op_type_upper = op_type.upper()
                        
                        # Build operation object
                        operation = {
                            'type': op_type_upper,
                            'asset_code': row['op_asset_code'],
                            'amount': safe_float(row['op_amount']) if row['op_amount'] else None,
                            'from_account': row['op_from_account'],
                            'to_account': row['op_to_account']
                        }
                        
                        # Add exchange details for trade operations
                        if op_type_str in TRADE_TYPES or 'offer' in op_type_str or 'path_payment' in op_type_str:
                            operation['is_trade'] = True
                            operation['exchange'] = {
                                'source_asset': row['exchange_source_asset'],
                                'source_amount': safe_float(row['exchange_source_amount']) if row['exchange_source_amount'] else None,
                                'dest_asset': row['exchange_dest_asset'],
                                'dest_amount': safe_float(row['exchange_dest_amount']) if row['exchange_dest_amount'] else None
                            }
                            # Create human-readable trade direction
                            src = row['exchange_source_asset'] or row['op_asset_code']
                            dst = row['exchange_dest_asset'] or 'unknown'
                            src_amt = safe_float(row['exchange_source_amount']) if row['exchange_source_amount'] else ''
                            dst_amt = safe_float(row['exchange_dest_amount']) if row['exchange_dest_amount'] else ''
                            operation['trade_summary'] = f"{src_amt} {src} → {dst_amt} {dst}"
                        else:
                            operation['is_trade'] = False
                        
                        transactions_dict[tx_hash]['operations'].append(operation)
                
                # Convert to list and limit
                transactions = list(transactions_dict.values())[:limit]
                
                # Add summary fields for convenience
                for tx in transactions:
                    # Extract unique UBEC tokens involved
                    tokens = set()
                    for op in tx['operations']:
                        if op['asset_code']:
                            tokens.add(op['asset_code'])
                        # Also include exchange tokens if present
                        if op.get('is_trade') and op.get('exchange'):
                            if op['exchange'].get('source_asset'):
                                tokens.add(op['exchange']['source_asset'])
                            if op['exchange'].get('dest_asset'):
                                tokens.add(op['exchange']['dest_asset'])
                    tx['involves_tokens'] = list(tokens)
                    tx['operation_count'] = len(tx['operations'])
                
                return {
                    'transactions': transactions,
                    'filter': {'asset_code': asset_code} if asset_code else {'ubec_tokens_only': True},
                    'valid_tokens': list(UBEC_TOKENS),
                    'pagination': {
                        'limit': limit,
                        'total': total_count,
                        'returned': len(transactions)
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching recent transactions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching recent transactions: {str(e)}")
        
        @self.app.get("/api/v1/ecoregions", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_ecoregions(request: Request) -> Dict:
            """
            Get ecoregion geographic boundaries and information.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - ecoregions: List of ecoregion objects with GeoJSON boundaries
            - count: Total number of ecoregions
            - timestamp: When this data was retrieved
            
            SCHEMA FIX v2.3.12: Actual table is phenomenal.ecoregions_2017
            Column eco_id (not eco_code) - map eco_id::text as eco_code
            
            SCHEMA FIX v2.3.9: Use row['geometry'] not row['geom'] (matches SQL alias)
            """
            try:
                db = await self.registry.get('database')
                
                # v2.3.12: Use phenomenal.ecoregions_2017 with correct column mapping
                query = """
                    SELECT 
                        eco_id::text as eco_code,
                        eco_name,
                        biome_num,
                        biome_name,
                        realm,
                        ST_AsGeoJSON(geom)::json AS geometry,
                        shape_area
                    FROM phenomenal.ecoregions_2017
                    WHERE geom IS NOT NULL
                    LIMIT 100
                """
                
                results = await db.fetch_all(query)
                
                ecoregions = []
                for row in results:
                    ecoregions.append({
                        'eco_code': row['eco_code'],
                        'eco_name': row['eco_name'],
                        'biome_num': int(row['biome_num']) if row['biome_num'] else 0,
                        'biome_name': row['biome_name'],
                        'realm': row['realm'],
                        'geometry': row['geometry'],  # v2.3.9: Correct column name
                        'shape_area': float(row['shape_area']) if row['shape_area'] else 0.0
                    })
                
                return {
                    'ecoregions': ecoregions,
                    'count': len(ecoregions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching ecoregions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching ecoregions: {str(e)}")
        
        @self.app.get("/api/v1/watersheds", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_watersheds(request: Request) -> Dict:
            """
            Get watershed geographic boundaries and information.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - watersheds: List of watershed objects with GeoJSON boundaries
            - count: Total number of watersheds
            - timestamp: When this data was retrieved
            
            SCHEMA FIX v2.3.9: Use row['geometry'] not row['geom'] (matches SQL alias)
            """
            try:
                db = await self.registry.get('database')
                
                query = """
                    SELECT 
                        feow_id::text as huc12,
                        COALESCE('Watershed ' || feow_id::text, 'Unknown') as name,
                        area_skm * 247.105 as areaacres,
                        ST_AsGeoJSON(geom)::json AS geometry
                    FROM phenomenal.feow_hydrosheds
                    WHERE geom IS NOT NULL
                    LIMIT 100
                """
                
                results = await db.fetch_all(query)
                
                watersheds = []
                for row in results:
                    watersheds.append({
                        'huc12': row['huc12'],
                        'name': row['name'],
                        'area_acres': float(row['areaacres']) if row['areaacres'] else 0.0,
                        'geometry': row['geometry']  # v2.3.9: Correct column name
                    })
                
                return {
                    'watersheds': watersheds,
                    'count': len(watersheds),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error fetching watersheds: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching watersheds: {str(e)}")
        
        # =====================================================================
        # BBOX ENDPOINTS (v2.5.0)
        # Geographic bounding box information for spatial entities
        # =====================================================================
        
        @self.app.get("/api/v1/bioregions/{gid}/bbox", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_bioregion_bbox(request: Request, gid: int) -> Dict:
            """
            Get bounding box for a specific bioregion in WGS 84 / Pseudo-Mercator (EPSG:3857).
            
            NEW IN v2.5.0: Provides bounding box coordinates for spatial 
            visualization and map centering in web mapping projection.
            
            Rate limit: 100 requests/minute per IP
            
            Path Parameters:
            - gid: Bioregion GID (integer) from bioregion_boundaries table
            
            Returns:
            - gid: Bioregion identifier
            - bioregion_name: Name of the bioregion
            - bioregion_code: Unique code for the bioregion
            - bbox: Bounding box with min_x, min_y, max_x, max_y (meters in EPSG:3857)
            - centroid: Center point coordinates x, y (meters in EPSG:3857)
            - area_sqkm: Area in square kilometers
            - srid: Spatial Reference ID (3857 = WGS 84 / Pseudo-Mercator)
            - timestamp: When this data was retrieved
            
            Source: phenomenal.bioregion_boundaries table
            Projection: EPSG:3857 (WGS 84 / Pseudo-Mercator) - coordinates in meters
            """
            try:
                db = await self.registry.get('database')
                
                # Transform geometry to EPSG:3857 (WGS 84 / Pseudo-Mercator) for web mapping
                query = """
                    SELECT 
                        gid,
                        bioregion_name,
                        bioregion_code,
                        ST_XMin(ST_Transform(geom, 3857)) as min_x,
                        ST_YMin(ST_Transform(geom, 3857)) as min_y,
                        ST_XMax(ST_Transform(geom, 3857)) as max_x,
                        ST_YMax(ST_Transform(geom, 3857)) as max_y,
                        ST_X(ST_Centroid(ST_Transform(geom, 3857))) as centroid_x,
                        ST_Y(ST_Centroid(ST_Transform(geom, 3857))) as centroid_y,
                        area_sqkm
                    FROM phenomenal.bioregion_boundaries
                    WHERE gid = $1
                """
                
                result = await db.fetch_one(query, (gid,))
                
                if not result:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Bioregion with gid {gid} not found"
                    )
                
                return {
                    'gid': result['gid'],
                    'bioregion_name': result['bioregion_name'],
                    'bioregion_code': result['bioregion_code'],
                    'bbox': {
                        'min_x': safe_float(result['min_x']),
                        'min_y': safe_float(result['min_y']),
                        'max_x': safe_float(result['max_x']),
                        'max_y': safe_float(result['max_y'])
                    },
                    'centroid': {
                        'x': safe_float(result['centroid_x']),
                        'y': safe_float(result['centroid_y'])
                    },
                    'area_sqkm': safe_float(result['area_sqkm']) if result['area_sqkm'] else None,
                    'srid': 3857,
                    'projection': 'WGS 84 / Pseudo-Mercator',
                    'units': 'meters',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching bioregion bbox: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error fetching bioregion bbox: {str(e)}"
                )
        
        @self.app.get("/api/v1/ecoregions/{eco_id}/bbox", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_ecoregion_bbox(request: Request, eco_id: int) -> Dict:
            """
            Get bounding box for a specific ecoregion in WGS 84 / Pseudo-Mercator (EPSG:3857).
            
            NEW IN v2.5.0: Provides bounding box coordinates from WWF 
            Ecoregions 2017 dataset for spatial visualization in web mapping projection.
            
            Rate limit: 100 requests/minute per IP
            
            Path Parameters:
            - eco_id: Ecoregion eco_id (integer) from ecoregions_2017 table
            
            Returns:
            - eco_id: Ecoregion identifier
            - eco_name: Name of the ecoregion
            - biome_name: Associated biome name
            - realm: Biogeographic realm
            - bbox: Bounding box with min_x, min_y, max_x, max_y (meters in EPSG:3857)
            - centroid: Center point coordinates x, y (meters in EPSG:3857)
            - shape_area: Area from source dataset
            - srid: Spatial Reference ID (3857 = WGS 84 / Pseudo-Mercator)
            - timestamp: When this data was retrieved
            
            Source: phenomenal.ecoregions_2017 table (WWF Ecoregions 2017)
            Projection: EPSG:3857 (WGS 84 / Pseudo-Mercator) - coordinates in meters
            """
            try:
                db = await self.registry.get('database')
                
                # Transform geometry to EPSG:3857 (WGS 84 / Pseudo-Mercator) for web mapping
                query = """
                    SELECT 
                        eco_id,
                        eco_name,
                        biome_name,
                        realm,
                        ST_XMin(ST_Transform(geom, 3857)) as min_x,
                        ST_YMin(ST_Transform(geom, 3857)) as min_y,
                        ST_XMax(ST_Transform(geom, 3857)) as max_x,
                        ST_YMax(ST_Transform(geom, 3857)) as max_y,
                        ST_X(ST_Centroid(ST_Transform(geom, 3857))) as centroid_x,
                        ST_Y(ST_Centroid(ST_Transform(geom, 3857))) as centroid_y,
                        shape_area
                    FROM phenomenal.ecoregions_2017
                    WHERE eco_id = $1
                """
                
                result = await db.fetch_one(query, (eco_id,))
                
                if not result:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Ecoregion with eco_id {eco_id} not found"
                    )
                
                return {
                    'eco_id': int(result['eco_id']),
                    'eco_name': result['eco_name'],
                    'biome_name': result['biome_name'],
                    'realm': result['realm'],
                    'bbox': {
                        'min_x': safe_float(result['min_x']),
                        'min_y': safe_float(result['min_y']),
                        'max_x': safe_float(result['max_x']),
                        'max_y': safe_float(result['max_y'])
                    },
                    'centroid': {
                        'x': safe_float(result['centroid_x']),
                        'y': safe_float(result['centroid_y'])
                    },
                    'shape_area': safe_float(result['shape_area']) if result['shape_area'] else None,
                    'srid': 3857,
                    'projection': 'WGS 84 / Pseudo-Mercator',
                    'units': 'meters',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching ecoregion bbox: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error fetching ecoregion bbox: {str(e)}"
                )
        
        @self.app.get("/api/v1/watersheds/{feow_id}/bbox", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_watershed_bbox(request: Request, feow_id: int) -> Dict:
            """
            Get bounding box for a specific watershed in WGS 84 / Pseudo-Mercator (EPSG:3857).
            
            NEW IN v2.5.0: Provides bounding box coordinates from FEOW 
            HydroSHEDS dataset for spatial visualization in web mapping projection.
            
            Rate limit: 100 requests/minute per IP
            
            Path Parameters:
            - feow_id: Watershed FEOW ID (integer) from feow_hydrosheds table
            
            Returns:
            - feow_id: Watershed identifier
            - name: Generated watershed name
            - bbox: Bounding box with min_x, min_y, max_x, max_y (meters in EPSG:3857)
            - centroid: Center point coordinates x, y (meters in EPSG:3857)
            - area_sqkm: Area in square kilometers
            - srid: Spatial Reference ID (3857 = WGS 84 / Pseudo-Mercator)
            - timestamp: When this data was retrieved
            
            Source: phenomenal.feow_hydrosheds table (FEOW HydroSHEDS)
            Projection: EPSG:3857 (WGS 84 / Pseudo-Mercator) - coordinates in meters
            """
            try:
                db = await self.registry.get('database')
                
                # Transform geometry to EPSG:3857 (WGS 84 / Pseudo-Mercator) for web mapping
                query = """
                    SELECT 
                        feow_id,
                        'Watershed ' || feow_id::text as name,
                        area_skm,
                        ST_XMin(ST_Transform(geom, 3857)) as min_x,
                        ST_YMin(ST_Transform(geom, 3857)) as min_y,
                        ST_XMax(ST_Transform(geom, 3857)) as max_x,
                        ST_YMax(ST_Transform(geom, 3857)) as max_y,
                        ST_X(ST_Centroid(ST_Transform(geom, 3857))) as centroid_x,
                        ST_Y(ST_Centroid(ST_Transform(geom, 3857))) as centroid_y
                    FROM phenomenal.feow_hydrosheds
                    WHERE feow_id = $1
                """
                
                result = await db.fetch_one(query, (feow_id,))
                
                if not result:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Watershed with feow_id {feow_id} not found"
                    )
                
                return {
                    'feow_id': int(result['feow_id']),
                    'name': result['name'],
                    'bbox': {
                        'min_x': safe_float(result['min_x']),
                        'min_y': safe_float(result['min_y']),
                        'max_x': safe_float(result['max_x']),
                        'max_y': safe_float(result['max_y'])
                    },
                    'centroid': {
                        'x': safe_float(result['centroid_x']),
                        'y': safe_float(result['centroid_y'])
                    },
                    'area_sqkm': safe_float(result['area_skm']) if result['area_skm'] else None,
                    'srid': 3857,
                    'projection': 'WGS 84 / Pseudo-Mercator',
                    'units': 'meters',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error fetching watershed bbox: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error fetching watershed bbox: {str(e)}"
                )
        
        self.logger.info("✓ All endpoints registered successfully (21 unique endpoints)")
    
    async def _rate_limit_error_handler(self, request: Request, exc: RateLimitExceeded) -> JSONResponse:
        """
        Custom error handler for rate limit exceeded errors.
        
        Provides user-friendly error message with details about rate limits.
        
        Args:
            request: FastAPI Request object
            exc: Rate limit exceeded exception
            
        Returns:
            JSON error response with 429 status
        """
        return JSONResponse(
            status_code=429,
            content={
                'error': 'rate_limit_exceeded',
                'message': 'Too many requests. Please try again later.',
                'detail': str(exc.detail) if hasattr(exc, 'detail') else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _calculate_network_health(
        self,
        bioregion_count: int,
        participant_count: int,
        ubuntu_score: float
    ) -> str:
        """
        Calculate overall network health based on metrics.
        
        Args:
            bioregion_count: Number of active bioregions
            participant_count: Number of active participants
            ubuntu_score: Average Ubuntu alignment score
            
        Returns:
            Health status: 'healthy', 'degraded', or 'unhealthy'
        """
        # Calculate component scores (0-1)
        bioregion_score = min(bioregion_count / 10, 1.0)
        participant_score = min(participant_count / 500, 1.0)
        ubuntu_score_normalized = ubuntu_score
        
        # Weighted average
        health_score = (
            bioregion_score * 0.4 +
            participant_score * 0.3 +
            ubuntu_score_normalized * 0.3
        )
        
        if health_score >= 0.7:
            return 'healthy'
        elif health_score >= 0.4:
            return 'degraded'
        else:
            return 'unhealthy'
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing BackendAPIService")
        # FastAPI app doesn't need explicit cleanup
        self._initialized = False


# ============================================================================
# Service Factory Function for Registry Integration
# ============================================================================

async def create_backend_api_service(registry) -> BackendAPIService:
    """
    Factory function to create BackendAPIService instance.
    
    This function is called by the ServiceRegistry to instantiate the service
    with proper dependency injection.
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized BackendAPIService instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'api_service',
            create_backend_api_service,
            dependencies=['database', 'bioregion_manager']
        )
    """
    service = BackendAPIService(registry)
    await service.initialize()
    return service
