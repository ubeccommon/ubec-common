#!/usr/bin/env python3
#/services/bioregion/bioregion_manager_servcie.py
"""
UBEC Bioregion Manager Service - Production Version 1.2.1
===========================================================
Tracks and manages bioregional holons representing geographic economic communities.

A bioregion is a geographic area defined by natural characteristics (watersheds,
climate, ecosystems) and local culture. This service identifies, tracks, and
analyzes bioregional economic commons within the UBEC network.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained bioregion tracking module
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Database-backed bioregion data
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Health checks with detailed metrics
    ✅ #8  No Duplicate Configuration: Configuration from registry
    ✅ #9  Integrated Rate Limiting: N/A (database-only operations)
    ✅ #10 Separation of Concerns: Bioregion logic isolated
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: Uses ServiceHealthCheck utility
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage Example:
    ```python
    from core.service_registry import ServiceRegistry
    
    # Initialize via service registry (proper pattern)
    registry = ServiceRegistry()
    bioregion_mgr = await registry.get('bioregion_manager')
    
    # Get bioregion count
    count = await bioregion_mgr.get_bioregion_count()
    
    # Get bioregion details
    regions = await bioregion_mgr.get_all_bioregions()
    
    # Scheduled update (for automated refresh)
    result = await bioregion_mgr.update_bioregions()
    
    # Create/update bioregion from network analysis
    await bioregion_mgr.identify_and_create_bioregions()
    ```

Author: UBEC Protocol Development Team
Version: 1.2.1
Created: 2025-11-04
Updated: 2025-11-10

Changes from v1.2.1:
- ✅ FIXED: Enhanced health check interpretation in initialize() method
- ✅ FIXED: Now checks health['status'] instead of non-existent 'connected' field
- ✅ ENHANCED: More nuanced logging levels (DEBUG vs WARNING)
- ✅ ENHANCED: Reduced false warnings during normal initialization timing
- ✅ VERIFIED: Maintains defensive coding while trusting service registry

Changes from v1.2.0:
- ✅ FIXED: Standardized health check using ServiceHealthCheck utility (Principle #12)
- ✅ ADDED: Proper initialization tracking with _initialized flag
- ✅ ADDED: Operation and error count tracking for monitoring
- ✅ ENHANCED: Health check now uses database_dependent_health pattern
- ✅ VERIFIED: All database queries use explicit schema names (phenomenal.holons)

Changes from v1.1.0:
- ✅ ADDED: update_bioregions() method for scheduled execution
- ✅ ENHANCED: Scheduler integration support
- ✅ ENHANCED: Automated bioregion refresh capability
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from decimal import Decimal

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

logger = logging.getLogger(__name__)


class BioregionManager:
    """
    Bioregion Manager Service for UBEC Protocol.
    
    Manages bioregional holons - geographic economic communities defined by
    natural boundaries (watersheds, ecosystems) and cultural characteristics.
    
    A bioregion in UBEC represents:
    - Geographic clustering of economic activity
    - Shared natural resources and boundaries
    - Cultural and local knowledge systems
    - Regenerative economic practices aligned with local ecosystems
    
    This service:
    - Identifies bioregions from network topology and spatial data
    - Tracks bioregion membership and boundaries
    - Calculates bioregion health metrics (autonomy, integration, ubuntu scores)
    - Provides bioregion analytics for dashboard and reporting
    - Supports automated updates via scheduler integration
    
    Attributes:
        db: Database manager instance (injected via registry)
        logger: Logger instance for this service
        _initialized: Service initialization status flag
        _cache: In-memory cache for performance
        _cache_ttl: Cache time-to-live in seconds
        _last_cache_update: Timestamp of last cache update
        _operation_count: Total operations performed
        _error_count: Total errors encountered
        _last_error: Last error message
        _last_error_time: Timestamp of last error
    """
    
    def __init__(self, database_manager):
        """
        Initialize Bioregion Manager.
        
        Args:
            database_manager: AsyncDatabaseManager instance from service registry
        """
        self.db = database_manager
        self.logger = logger
        
        # Initialization tracking
        self._initialized = False
        
        # Simple caching for performance
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 60  # seconds
        self._last_cache_update: Optional[datetime] = None
        
        # Operation tracking for monitoring
        self._operation_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        self.logger.info("BioregionManager initialized")
    
    async def initialize(self) -> None:
        """
        Initialize service and verify database connectivity.
        
        Called by service registry during system startup.
        
        ENHANCED v1.2.1: More nuanced health check interpretation to reduce
        false warnings during normal initialization timing.
        
        Note: Trusts that database service is already initialized by service registry.
        The registry ensures dependencies are initialized in correct order.
        """
        self.logger.info("Initializing BioregionManager service")
        
        # Check database connectivity (non-fatal - trust service registry)
        try:
            health = await self.db.health_check()
            
            # Interpret health status accurately using correct field names
            status = health.get('status', 'unknown')
            details = health.get('details', {})
            
            if status == 'healthy':
                # Database fully operational
                self.logger.debug(
                    f"Database health check: healthy "
                    f"(response: {details.get('response_time_ms', 0):.1f}ms)"
                )
                
            elif status == 'degraded':
                # Database working but slow - not an error
                self.logger.debug(
                    f"Database health check: degraded "
                    f"(continuing - service registry ensures connectivity)"
                )
                
            elif not details.get('initialized', False):
                # Database pool initializing (timing issue - normal during startup)
                self.logger.debug(
                    "Database health check: initializing "
                    "(timing - normal during startup, continuing)"
                )
                
            elif status in ['unhealthy', 'unknown']:
                # Only warn if database appears genuinely unreachable
                # But still continue - trust service registry initialization order
                self.logger.warning(
                    f"Database health check: {status} "
                    "(continuing - trusting service registry initialization order)"
                )
                
        except Exception as e:
            # Health check itself failed - log as debug since we trust registry
            self.logger.debug(
                f"Database health check error during initialization: {e} "
                "(expected during rapid startup - continuing as designed)"
            )
        
        # Verify phenomenal schema exists
        try:
            schema_check = await self.db.fetch_one(
                """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'phenomenal'
                """,
                ()
            )
            
            if not schema_check:
                self.logger.warning("Phenomenal schema not found - bioregion tracking will be limited")
            else:
                self.logger.debug("Phenomenal schema verified")
                
        except Exception as e:
            self.logger.warning(f"Could not verify phenomenal schema: {e}")
        
        # Mark as initialized
        self._initialized = True
        self.logger.info("BioregionManager initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using standardized ServiceHealthCheck utility.
        
        Implements Principle #12 (Method Singularity) by using the shared
        ServiceHealthCheck.database_dependent_health() method instead of
        custom health check implementation.
        
        This implementation follows the health check pattern guide:
        - Uses ServiceHealthCheck.database_dependent_health() for database services
        - Tracks initialization state
        - Includes bioregion-specific context (cache, counts, operations)
        - Tracks operation metrics and error rates
        
        Returns:
            Health status dictionary from ServiceHealthCheck utility:
            {
                'service': 'BioregionManager',
                'version': '1.2.1',
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'database_connected': bool,
                    'phenomenal_schema_available': bool,
                    'bioregion_count': int,
                    'cache_age_seconds': int,
                    'operation_count': int,
                    'error_count': int,
                    'last_error': str,
                    'last_error_time': str (ISO timestamp)
                }
            }
        
        Example:
            >>> health = await bioregion_mgr.health_check()
            >>> if health['status'] == 'healthy':
            ...     print("Bioregion manager operational")
        """
        # Calculate cache age
        cache_age = 0
        if self._last_cache_update:
            cache_age = (datetime.now(timezone.utc) - self._last_cache_update).total_seconds()
        
        # Get bioregion count for health check
        try:
            bioregion_count = await self.get_bioregion_count()
        except Exception as e:
            self.logger.warning(f"Could not get bioregion count in health check: {e}")
            bioregion_count = 0
        
        # Check if phenomenal schema is available
        phenomenal_available = await self._check_phenomenal_schema()
        
        # Use standardized health check utility (Principle #12)
        return await ServiceHealthCheck.database_dependent_health(
            service_name='BioregionManager',
            db_manager=self.db,
            is_initialized=self._initialized,
            operation_count=self._operation_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time,
            # Bioregion-specific context
            phenomenal_schema_available=phenomenal_available,
            bioregion_count=bioregion_count,
            cache_age_seconds=int(cache_age),
            version='1.2.1'
        )
    
    async def _check_phenomenal_schema(self) -> bool:
        """
        Check if phenomenal schema is available.
        
        Returns:
            True if phenomenal schema exists, False otherwise
        """
        try:
            result = await self.db.fetch_one(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'phenomenal'",
                ()
            )
            return result is not None
        except Exception:
            return False
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid based on TTL."""
        if not self._last_cache_update:
            return False
        
        age = (datetime.now(timezone.utc) - self._last_cache_update).total_seconds()
        return age < self._cache_ttl
    
    def _update_cache(self, key: str, value: Any) -> None:
        """Update cache with new value."""
        self._cache[key] = value
        self._last_cache_update = datetime.now(timezone.utc)
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        if self._is_cache_valid() and key in self._cache:
            return self._cache[key]
        return None
    
    def _track_operation(self) -> None:
        """Track successful operation."""
        self._operation_count += 1
    
    def _track_error(self, error: Exception) -> None:
        """Track error occurrence."""
        self._error_count += 1
        self._last_error = str(error)
        self._last_error_time = datetime.now(timezone.utc)
    
    # ========================================================================
    # Core Bioregion Queries
    # ========================================================================
    
    async def get_bioregion_count(self) -> int:
        """
        Get total count of active bioregions.
        
        Bioregions are considered active if they haven't been dissolved.
        Uses explicit schema name (phenomenal.holons) for clarity and reliability.
        
        Returns:
            Count of active bioregions
            
        Example:
            >>> count = await bioregion_mgr.get_bioregion_count()
            >>> print(f"Active bioregions: {count}")
        """
        # Check cache first
        cached = self._get_cached('bioregion_count')
        if cached is not None:
            return cached
        
        try:
            # Query with explicit schema name (phenomenal.holons)
            result = await self.db.fetch_one(
                """
                SELECT COUNT(*) as count 
                FROM phenomenal.holons 
                WHERE holon_type = 'bioregion' 
                  AND dissolved_at IS NULL
                """,
                ()
            )
            
            count = int(result['count']) if result else 0
            
            # Update cache
            self._update_cache('bioregion_count', count)
            
            # Track operation
            self._track_operation()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting bioregion count: {e}")
            self._track_error(e)
            return 0
    
    async def get_all_bioregions(self) -> List[Dict[str, Any]]:
        """
        Get all active bioregions with their details.
        
        Retrieves comprehensive information about each bioregion including:
        - Basic info (id, name, type)
        - Metrics (autonomy, integration scores)
        - Membership (constituent accounts/assets)
        - Temporal data (emergence, stability, dissolution)
        - Ubuntu scores and emergent properties
        
        Uses explicit schema name (phenomenal.holons) for clarity and reliability.
        
        Returns:
            List of bioregion dictionaries with complete details
            
        Example:
            >>> regions = await bioregion_mgr.get_all_bioregions()
            >>> for region in regions:
            ...     print(f"{region['name']}: {region['member_count']} members")
        """
        try:
            # Query with explicit schema name (phenomenal.holons)
            rows = await self.db.fetch_all(
                """
                SELECT 
                    id,
                    holon_name,
                    holon_type,
                    autonomy_score,
                    integration_score,
                    constituent_accounts,
                    constituent_assets,
                    emergent_properties,
                    collective_behavior,
                    ubuntu_scores,
                    emerged_at,
                    stable_from,
                    dissolved_at,
                    array_length(constituent_accounts, 1) as member_count,
                    array_length(constituent_assets, 1) as asset_count,
                    ST_Area(spatial_region::geography) / 1000000.0 as area_km2,
                    ST_AsGeoJSON(spatial_region) as region_geojson
                FROM phenomenal.holons
                WHERE holon_type = 'bioregion'
                  AND dissolved_at IS NULL
                ORDER BY autonomy_score DESC, integration_score DESC
                """,
                ()
            )
            
            bioregions = []
            for row in rows:
                bioregion = {
                    'id': row['id'],
                    'name': row['holon_name'],
                    'type': row['holon_type'],
                    'autonomy_score': float(row['autonomy_score']) if row['autonomy_score'] else 0,
                    'integration_score': float(row['integration_score']) if row['integration_score'] else 0,
                    'member_count': row['member_count'] if row['member_count'] else 0,
                    'asset_count': row['asset_count'] if row['asset_count'] else 0,
                    'area_km2': float(row['area_km2']) if row['area_km2'] else 0,
                    'emerged_at': row['emerged_at'].isoformat() if row['emerged_at'] else None,
                    'stable_from': row['stable_from'].isoformat() if row['stable_from'] else None,
                    'dissolved_at': row['dissolved_at'].isoformat() if row['dissolved_at'] else None,
                    'status': 'active' if not row['dissolved_at'] else 'dissolved',
                    'ubuntu_scores': dict(row['ubuntu_scores']) if row['ubuntu_scores'] else {},
                    'emergent_properties': dict(row['emergent_properties']) if row['emergent_properties'] else {}
                }
                
                # Calculate health rating
                bioregion['health_rating'] = self._calculate_health_rating(bioregion)
                
                bioregions.append(bioregion)
            
            # Track operation
            self._track_operation()
            
            self.logger.info(f"Retrieved {len(bioregions)} bioregions")
            return bioregions
            
        except Exception as e:
            self.logger.error(f"Error getting all bioregions: {e}")
            self._track_error(e)
            return []
    
    async def get_bioregion_by_id(self, bioregion_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific bioregion.
        
        Args:
            bioregion_id: ID of the bioregion holon
            
        Returns:
            Dictionary with bioregion details or None if not found
        """
        try:
            # Query with explicit schema name (phenomenal.holons)
            result = await self.db.fetch_one(
                """
                SELECT 
                    h.id,
                    h.holon_name,
                    h.holon_type,
                    h.autonomy_score,
                    h.integration_score,
                    h.constituent_accounts,
                    h.constituent_assets,
                    h.emergent_properties,
                    h.collective_behavior,
                    h.ubuntu_scores,
                    h.emerged_at,
                    h.stable_from,
                    h.dissolved_at,
                    array_length(h.constituent_accounts, 1) as member_count,
                    array_length(h.constituent_assets, 1) as asset_count,
                    ST_Area(h.spatial_region::geography) / 1000000.0 as area_km2,
                    ST_AsGeoJSON(h.spatial_region) as region_geojson,
                    ST_Centroid(h.spatial_region)::geography as centroid
                FROM phenomenal.holons h
                WHERE h.id = $1
                  AND h.holon_type = 'bioregion'
                """,
                (bioregion_id,)
            )
            
            if not result:
                self.logger.warning(f"Bioregion {bioregion_id} not found")
                return None
            
            bioregion = {
                'id': result['id'],
                'name': result['holon_name'],
                'type': result['holon_type'],
                'autonomy_score': float(result['autonomy_score']) if result['autonomy_score'] else 0,
                'integration_score': float(result['integration_score']) if result['integration_score'] else 0,
                'member_count': result['member_count'] if result['member_count'] else 0,
                'asset_count': result['asset_count'] if result['asset_count'] else 0,
                'area_km2': float(result['area_km2']) if result['area_km2'] else 0,
                'emerged_at': result['emerged_at'].isoformat() if result['emerged_at'] else None,
                'stable_from': result['stable_from'].isoformat() if result['stable_from'] else None,
                'dissolved_at': result['dissolved_at'].isoformat() if result['dissolved_at'] else None,
                'status': 'active' if not result['dissolved_at'] else 'dissolved',
                'ubuntu_scores': dict(result['ubuntu_scores']) if result['ubuntu_scores'] else {},
                'emergent_properties': dict(result['emergent_properties']) if result['emergent_properties'] else {},
                'region_geojson': result['region_geojson']
            }
            
            # Calculate health rating
            bioregion['health_rating'] = self._calculate_health_rating(bioregion)
            
            # Track operation
            self._track_operation()
            
            self.logger.info(f"Retrieved bioregion {bioregion_id}: {bioregion['name']}")
            return bioregion
            
        except Exception as e:
            self.logger.error(f"Error getting bioregion {bioregion_id}: {e}")
            self._track_error(e)
            return None
    
    async def get_bioregion_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all bioregions.
        
        Provides high-level overview including:
        - Total count of bioregions
        - Average metrics (autonomy, integration scores)
        - Total members and assets across all bioregions
        - Geographic coverage statistics
        
        Returns:
            Dictionary with summary statistics
            
        Example:
            >>> summary = await bioregion_mgr.get_bioregion_summary()
            >>> print(f"Total bioregions: {summary['total_count']}")
            >>> print(f"Average autonomy: {summary['avg_autonomy']:.2f}")
        """
        try:
            # Query with explicit schema name (phenomenal.holons)
            result = await self.db.fetch_one(
                """
                SELECT 
                    COUNT(*) as total_count,
                    AVG(autonomy_score) as avg_autonomy,
                    AVG(integration_score) as avg_integration,
                    SUM(array_length(constituent_accounts, 1)) as total_members,
                    SUM(array_length(constituent_assets, 1)) as total_assets,
                    SUM(ST_Area(spatial_region::geography) / 1000000.0) as total_area_km2
                FROM phenomenal.holons
                WHERE holon_type = 'bioregion'
                  AND dissolved_at IS NULL
                """,
                ()
            )
            
            summary = {
                'total_count': int(result['total_count']) if result else 0,
                'avg_autonomy': float(result['avg_autonomy']) if result and result['avg_autonomy'] else 0,
                'avg_integration': float(result['avg_integration']) if result and result['avg_integration'] else 0,
                'total_members': int(result['total_members']) if result and result['total_members'] else 0,
                'total_assets': int(result['total_assets']) if result and result['total_assets'] else 0,
                'total_area_km2': float(result['total_area_km2']) if result and result['total_area_km2'] else 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Track operation
            self._track_operation()
            
            self.logger.info("Bioregion summary generated")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating bioregion summary: {e}")
            self._track_error(e)
            return {
                'total_count': 0,
                'avg_autonomy': 0,
                'avg_integration': 0,
                'total_members': 0,
                'total_assets': 0,
                'total_area_km2': 0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
    
    # ========================================================================
    # Scheduled Operations
    # ========================================================================
    
    async def update_bioregions(self) -> Dict[str, Any]:
        """
        Update bioregion data - scheduled operation for automated refresh.
        
        This method is designed to be called by the scheduler service periodically
        to refresh bioregion analysis and identify new bioregional patterns.
        
        Process:
            1. Clear cache to force fresh analysis
            2. Get current bioregion count
            3. Identify and create new bioregions from network analysis
            4. Clear cache again after updates
            5. Return summary of changes
        
        Returns:
            Dictionary with update results:
                - timestamp: When update completed
                - bioregions_analyzed: Count before update
                - new_bioregions: Number of new bioregions created
                - total_bioregions: Total bioregion count after update
                - cache_cleared: Whether cache was cleared
                - duration_ms: How long update took
                - status: 'success' or 'error'
        
        Raises:
            Does not raise exceptions - returns error status instead
        
        Example:
            # Called by scheduler
            result = await bioregion_mgr.update_bioregions()
            if result['status'] == 'success':
                logger.info(f"Bioregions updated: {result['new_bioregions']} new")
        
        Design Principles:
            - Principle #5: Async operation
            - Principle #12: Method singularity - composes existing methods
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting scheduled bioregion update...")
            
            # Clear cache to force fresh analysis
            self._cache.clear()
            self._last_cache_update = None
            self.logger.debug("Cache cleared")
            
            # Get current bioregion count
            current_count = await self.get_bioregion_count()
            self.logger.debug(f"Current bioregion count: {current_count}")
            
            # Attempt to identify new bioregions
            # Note: identify_and_create_bioregions is currently a placeholder
            # This will be fully implemented when clustering algorithms are ready
            new_bioregions = await self.identify_and_create_bioregions(
                min_members=10,
                min_density=0.3,
                algorithm='spatial_clustering'
            )
            
            # Clear cache again after potential updates
            self._cache.clear()
            self._last_cache_update = None
            
            # Get updated count
            new_count = await self.get_bioregion_count()
            self.logger.debug(f"New bioregion count: {new_count}")
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'bioregions_analyzed': current_count,
                'new_bioregions': len(new_bioregions),
                'total_bioregions': new_count,
                'cache_cleared': True,
                'duration_ms': duration_ms,
                'status': 'success'
            }
            
            self.logger.info(
                f"✓ Bioregion update complete: {len(new_bioregions)} new, "
                f"{new_count} total ({duration_ms:.0f}ms)"
            )
            return result
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Bioregion update failed: {e}"
            self.logger.error(error_msg, exc_info=True)
            self._track_error(e)
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'error',
                'error': str(e),
                'duration_ms': duration_ms
            }
    
    # ========================================================================
    # Bioregion Creation and Management
    # ========================================================================
    
    async def identify_and_create_bioregions(
        self,
        min_members: int = 10,
        min_density: float = 0.3,
        algorithm: str = 'spatial_clustering'
    ) -> List[int]:
        """
        Identify and create bioregions from network analysis.
        
        This method analyzes the account network to identify natural clusters
        that represent bioregional communities based on:
        - Spatial proximity (if position data available)
        - Transaction patterns and relationships
        - Shared assets and economic activity
        - Cultural/natural boundary indicators
        
        Args:
            min_members: Minimum accounts required for a bioregion
            min_density: Minimum connection density threshold
            algorithm: Clustering algorithm ('spatial_clustering', 'community_detection')
            
        Returns:
            List of newly created bioregion IDs
            
        Note:
            This is a complex operation that may take several seconds for large networks.
            Consider running as a background task for production systems.
        """
        self.logger.info(f"Identifying bioregions with algorithm: {algorithm}")
        
        try:
            # TODO: Implement sophisticated clustering algorithms
            # For now, return empty list - this is a placeholder for future enhancement
            self.logger.warning("Bioregion identification not yet implemented - placeholder method")
            return []
            
        except Exception as e:
            self.logger.error(f"Error identifying bioregions: {e}")
            self._track_error(e)
            return []
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_health_rating(self, bioregion: Dict[str, Any]) -> str:
        """
        Calculate overall health rating for a bioregion.
        
        Based on:
        - Integration score (how unified)
        - Autonomy score (how independent)
        - Member count (community size)
        - Ubuntu scores (principle alignment)
        
        Returns:
            Health rating: 'excellent', 'good', 'fair', 'poor'
        """
        integration = bioregion.get('integration_score', 0)
        autonomy = bioregion.get('autonomy_score', 0)
        member_count = bioregion.get('member_count', 0)
        
        # Calculate composite score
        composite = (integration + autonomy) / 2
        
        # Adjust for community size
        if member_count < 10:
            composite *= 0.8  # Penalty for small size
        elif member_count > 50:
            composite *= 1.1  # Bonus for large, stable community
        
        # Determine rating
        if composite >= 0.8:
            return 'excellent'
        elif composite >= 0.6:
            return 'good'
        elif composite >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing BioregionManager service")
        self._cache.clear()
        self._initialized = False


# ============================================================================
# Service Factory Function for Registry Integration
# ============================================================================

async def create_bioregion_manager(registry) -> BioregionManager:
    """
    Factory function to create BioregionManager instance.
    
    This function is called by the ServiceRegistry to instantiate the service
    with proper dependency injection.
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized BioregionManager instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'bioregion_manager',
            create_bioregion_manager,
            dependencies=['database']
        )
    """
    database = await registry.get('database')
    manager = BioregionManager(database)
    await manager.initialize()
    return manager
