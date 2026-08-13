#!/usr/bin/env python3
"""
Async Database Manager for UBEC Protocol - Multi-Schema Enhanced Version
=========================================================================
Provides async database access using asyncpg with comprehensive health monitoring
and full multi-schema search path support.

This module implements:
- Async connection pooling with automatic schema management
- Multi-schema search path support (ubec_main, phenomenal, topology, public)
- Query execution with async/await patterns
- Transaction management with context managers
- Automatic parameter placeholder conversion (%s → $1, $2...)
- ISO 8601 datetime string conversion
- Comprehensive health check monitoring
- Database maintenance operations (VACUUM, cleanup)
- Connection testing utilities
- Schema parameter validation

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained database access module
    ✅ 2.  Service Pattern: Factory function for instantiation
    ✅ 3.  Service Registry: Compatible with centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: 100% async/await for all I/O operations
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks with detailed metrics
    ✅ 8.  No Duplicate Config: Single configuration source
    ✅ 9.  Integrated Rate Limiting: Connection pool limits
    ✅ 10. Separation of Concerns: Database logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and examples
    ✅ 12. Method Singularity: Single implementation of each method
════════════════════════════════════════════════════════════════════════════

Usage Example:
    ```python
    from core.db.database_manager import AsyncDatabaseManager
    
    # Create and initialize database manager with multi-schema support
    db = AsyncDatabaseManager(
        host='localhost',
        port=5432,
        database='ubec',
        schema='ubec_main',  # Primary schema for explicit references
        search_path='ubec_main,phenomenal,topology,public',  # Full search path
        user='ubec_app',
        password='your_password'
    )
    
    await db.initialize()
    
    # Execute queries (supports both %s and $1 placeholders)
    # Explicit schema reference (always works)
    results = await db.fetch_all(
        "SELECT * FROM ubec_main.ubec_balances WHERE balance > 0"
    )
    
    # Implicit reference (uses search path)
    results = await db.fetch_all(
        "SELECT * FROM ubec_balances WHERE balance > 0"
    )
    
    # Cross-schema joins (use multi-line strings)
    query = (
        "SELECT ub.*, ph.autonomy_score "
        "FROM ubec_main.ubec_balances ub "
        "LEFT JOIN phenomenal.holons ph "
        "ON ub.account_id = ANY(ph.constituent_accounts)"
    )
    results = await db.fetch_all(query)
    
    # Transaction support
    async with db.transaction() as tx:
        await tx.execute("INSERT INTO ...", (...))
        await tx.execute("UPDATE ...", (...))
        # Auto-commits on success, rolls back on exception
    
    # Health check
    health = await db.health_check()
    if health['status'] == 'healthy':
        print("Database operational")
    
    # Database maintenance
    result = await db.maintenance()
    print(f"Maintenance completed: {result['status']}")
    
    # Cleanup
    await db.close()
    ```

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 2.1.0 (Production Ready with Maintenance)
Date: November 8, 2025
Changes from v2.0.1:
    - Added maintenance() method for database cleanup and optimization
    - Implements VACUUM ANALYZE on high-traffic tables
    - Automated cleanup of old audit logs (>90 days)
    - Automated cleanup of old scheduler execution logs (>30 days)
    - Automated cleanup of stale sync status records (>60 days)
    - Database statistics updates for query optimization
    - Comprehensive error handling and logging
    - Full compliance with all 12 design principles maintained
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple, Union
from contextlib import asynccontextmanager

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("asyncpg not available - install with: pip install asyncpg")


logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_query_placeholders(query: str) -> str:
    """
    Convert psycopg2-style placeholders (%s) to asyncpg-style ($1, $2, etc.).
    
    Implements Principle #12 (Method Singularity): Single placeholder
    conversion implementation for entire system.
    
    Args:
        query: SQL query with %s placeholders
        
    Returns:
        Query with $1, $2, etc. placeholders
        
    Example:
        >>> convert_query_placeholders("SELECT * FROM t WHERE a=%s AND b=%s")
        'SELECT * FROM t WHERE a=$1 AND b=$2'
    """
    if '%s' not in query:
        return query
    
    # Replace %s with incrementing $n
    counter = 1
    def replace_placeholder(match):
        nonlocal counter
        result = f'${counter}'
        counter += 1
        return result
    
    converted = re.sub(r'%s', replace_placeholder, query)
    return converted


def convert_iso8601_to_datetime(value: str) -> datetime:
    """
    Convert ISO 8601 datetime string to Python datetime object.
    
    Handles various ISO 8601 formats:
    - 2024-08-14T11:09:45Z
    - 2024-08-14T11:09:45+00:00
    - 2024-08-14T11:09:45.123456Z
    
    Args:
        value: ISO 8601 formatted datetime string
        
    Returns:
        Python datetime object
        
    Raises:
        ValueError: If string cannot be parsed as datetime
        
    Example:
        >>> dt = convert_iso8601_to_datetime("2024-08-14T11:09:45Z")
        >>> isinstance(dt, datetime)
        True
    """
    try:
        # Handle 'Z' timezone indicator (UTC)
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        
        # Parse with timezone support
        return datetime.fromisoformat(value)
    except Exception as e:
        logger.warning(f"Failed to parse datetime string '{value}': {e}")
        raise ValueError(f"Invalid ISO 8601 datetime string: {value}")


def _is_iso8601_datetime(value: str) -> bool:
    """
    Check if a string looks like an ISO 8601 datetime.
    
    Args:
        value: String to check
        
    Returns:
        True if string matches ISO 8601 datetime pattern
        
    Example:
        >>> _is_iso8601_datetime("2024-08-14T11:09:45Z")
        True
        >>> _is_iso8601_datetime("hello")
        False
    """
    # Pattern: YYYY-MM-DDTHH:MM:SS with optional microseconds and timezone
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    return bool(re.match(iso_pattern, value))


def convert_params_for_asyncpg(params: Union[Tuple, List, Dict]) -> Union[Tuple, List, Dict]:
    """
    Recursively convert parameter values for asyncpg compatibility.
    
    Converts ISO 8601 datetime strings to Python datetime objects.
    asyncpg requires datetime objects, not ISO strings.
    
    Implements Principle #12 (Method Singularity): Single parameter
    conversion implementation for entire system.
    
    Args:
        params: Query parameters (tuple, list, or dict)
        
    Returns:
        Converted parameters with datetime objects replacing ISO strings
        
    Example:
        >>> params = ("UBEC", "2024-08-14T11:09:45Z")
        >>> converted = convert_params_for_asyncpg(params)
        >>> isinstance(converted[1], datetime)
        True
    """
    if isinstance(params, dict):
        return {
            key: convert_params_for_asyncpg(value) 
            if isinstance(value, (dict, list, tuple)) 
            else convert_iso8601_to_datetime(value) 
            if isinstance(value, str) and _is_iso8601_datetime(value)
            else value
            for key, value in params.items()
        }
    elif isinstance(params, (list, tuple)):
        converted = [
            convert_params_for_asyncpg(item)
            if isinstance(item, (dict, list, tuple))
            else convert_iso8601_to_datetime(item)
            if isinstance(item, str) and _is_iso8601_datetime(item)
            else item
            for item in params
        ]
        return tuple(converted) if isinstance(params, tuple) else converted
    else:
        return params


def _validate_params(params: Any, method_name: str) -> Tuple:
    """
    Validate and ensure params is a tuple.
    
    Args:
        params: Parameters to validate
        method_name: Name of calling method (for error messages)
        
    Returns:
        Parameters as tuple
        
    Raises:
        TypeError: If params cannot be converted to tuple
    """
    if params is None:
        return ()
    
    if not isinstance(params, tuple):
        if isinstance(params, list):
            return tuple(params)
        else:
            raise TypeError(
                f"{method_name}: params must be a tuple or list, got {type(params)}"
            )
    
    return params


# ============================================================================
# ASYNC DATABASE MANAGER
# ============================================================================

class AsyncDatabaseManager:
    """
    Async database manager with connection pooling and multi-schema support.
    
    Implements all 12 UBEC design principles for database access.
    Provides async interface to PostgreSQL using asyncpg.
    
    Features:
    - Connection pooling (2-20 connections default)
    - Multi-schema search path (ubec_main, phenomenal, topology, public)
    - Automatic placeholder conversion (%s → $1)
    - ISO 8601 datetime handling
    - Transaction support with context managers
    - Comprehensive health monitoring
    - Database maintenance operations
    
    Attributes:
        host: Database host
        port: Database port
        database: Database name
        schema: Primary schema (for explicit references)
        search_path: Full PostgreSQL search path
        user: Database user
        password: Database password (stored internally)
        min_pool_size: Minimum connections in pool
        max_pool_size: Maximum connections in pool
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = 'ubec',
        schema: str = 'ubec_main',
        search_path: str = 'ubec_main,public',
        user: str = 'ubec_app',
        password: str = '',
        min_pool_size: int = 2,
        max_pool_size: int = 20
    ):
        """
        Initialize database manager.
        
        Does not establish connection - call initialize() to connect.
        
        Args:
            host: PostgreSQL server host
            port: PostgreSQL server port
            database: Database name
            schema: Primary schema for explicit table references
            search_path: Full PostgreSQL search path (comma-separated schemas)
            user: Database username
            password: Database password
            min_pool_size: Minimum number of connections in pool
            max_pool_size: Maximum number of connections in pool
            
        Example:
            >>> db = AsyncDatabaseManager(
            ...     host='localhost',
            ...     port=5432,
            ...     database='ubec',
            ...     schema='ubec_main',
            ...     search_path='ubec_main,phenomenal,topology,public'
            ... )
            >>> await db.initialize()
        """
        self.host = host
        self.port = port
        self.database = database
        self.schema = schema
        self.search_path = search_path
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        
        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False
        
        logger.info(
            f"AsyncDatabaseManager created for {database}.{schema} "
            f"(search_path: {search_path}) "
            f"(pool: {min_pool_size}-{max_pool_size})"
        )
    
    async def initialize(self) -> None:
        """
        Initialize connection pool.
        
        Must be called before using any database operations.
        This method is idempotent - calling it multiple times is safe.
        
        Raises:
            Exception: If connection pool creation fails
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> # Now ready to use
        """
        if self._initialized:
            logger.warning("Database already initialized")
            return
        
        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60
            )
            
            # Test connection and set search path
            async with self._pool.acquire() as conn:
                # Set full search path for this connection
                await conn.execute(f'SET search_path TO {self.search_path}')
                result = await conn.fetchval('SELECT 1')
                if result != 1:
                    raise Exception("Database connection test failed")
            
            self._initialized = True
            logger.info(
                f"Database pool initialized: {self.database}.{self.schema} "
                f"(search_path: {self.search_path}) "
                f"({self.min_pool_size}-{self.max_pool_size} connections)"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """
        Close all database connections and release resources.
        
        Should be called during application shutdown.
        After calling this method, initialize() must be called again
        before using the database.
        
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> # ... use database ...
            >>> await db.close()
        """
        if self._pool:
            await self._pool.close()
            self._initialized = False
            logger.info("Database pool closed")
    
    async def test_connection(self) -> bool:
        """
        Test if database connection is working.
        
        Performs a simple query to verify database connectivity.
        This method is useful for health checks and diagnostics.
        
        Returns:
            True if connection is working, False otherwise
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> if await db.test_connection():
            ...     print("Database is accessible")
        """
        try:
            if not self._initialized:
                return False
            
            # Simple query to test connection
            result = await self.fetch_one("SELECT 1 as test", ())
            return result is not None and result.get('test') == 1
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on database connection.
        
        Implements Principle #7 (Per-Asset Monitoring): Provides detailed
        health metrics for monitoring and alerting.
        
        Returns:
            Dictionary with health check results:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'pool_size': int,
                    'pool_idle': int,
                    'pool_used': int,
                    'pool_max': int,
                    'connection_test': bool,
                    'response_time_ms': float,
                    'database': str,
                    'schema': str,
                    'search_path': str,
                    'host': str,
                    'port': int
                }
            }
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> health = await db.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Response time: {health['details']['response_time_ms']}ms")
            >>> print(f"Search path: {health['details']['search_path']}")
        """
        start_time = datetime.now()
        
        health_info = {
            'status': 'unknown',
            'message': '',
            'timestamp': start_time.isoformat(),
            'details': {
                'initialized': self._initialized,
                'pool_size': 0,
                'pool_idle': 0,
                'pool_used': 0,
                'pool_max': self.max_pool_size,
                'connection_test': False,
                'response_time_ms': 0.0,
                'database': self.database,
                'schema': self.schema,
                'search_path': self.search_path,
                'host': self.host,
                'port': self.port
            }
        }
        
        try:
            # Check if initialized
            if not self._initialized:
                health_info['status'] = 'unhealthy'
                health_info['message'] = 'Database not initialized'
                return health_info
            
            # Check pool status
            if self._pool:
                health_info['details']['pool_size'] = self._pool.get_size()
                health_info['details']['pool_idle'] = self._pool.get_idle_size()
                health_info['details']['pool_used'] = (
                    self._pool.get_size() - self._pool.get_idle_size()
                )
            
            # Test connection with simple query
            test_result = await self.fetch_one("SELECT 1 as test", ())
            
            # Calculate response time
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            health_info['details']['response_time_ms'] = round(response_time, 2)
            
            # Evaluate health status based on test and response time
            if test_result and test_result.get('test') == 1:
                health_info['details']['connection_test'] = True
                
                if response_time < 100:
                    health_info['status'] = 'healthy'
                    health_info['message'] = (
                        f'Database responsive ({response_time:.1f}ms)'
                    )
                elif response_time < 500:
                    health_info['status'] = 'degraded'
                    health_info['message'] = (
                        f'Database slow ({response_time:.1f}ms)'
                    )
                else:
                    health_info['status'] = 'degraded'
                    health_info['message'] = (
                        f'Database very slow ({response_time:.1f}ms)'
                    )
            else:
                health_info['status'] = 'unhealthy'
                health_info['message'] = 'Connection test query failed'
        
        except Exception as e:
            health_info['status'] = 'unhealthy'
            health_info['message'] = f'Health check failed: {str(e)}'
            logger.error(f"Database health check failed: {e}")
        
        return health_info
    
    async def maintenance(self) -> Dict[str, Any]:
        """
        Perform database maintenance operations.
        
        Implements Principle #5 (Strict Async Operations) and Principle #12 
        (Method Singularity) - single maintenance method for all DB operations.
        
        Operations performed:
        1. VACUUM ANALYZE on high-traffic tables
        2. Update table statistics for query optimization
        3. Cleanup old audit logs (>90 days)
        4. Cleanup old scheduler execution logs (>30 days)
        5. Cleanup stale sync status records (>60 days)
        6. Update database-wide statistics
        
        All operations use explicit schema references for reliability.
        
        Returns:
            Dict[str, Any]: Maintenance results with:
            {
                'status': 'success' | 'error',
                'duration_seconds': float,
                'operations': Dict[str, str],  # Operation results
                'records_deleted': Dict[str, int],  # Cleanup counts
                'total_records_deleted': int,
                'timestamp': str  # ISO format
            }
        
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> result = await db.maintenance()
            >>> print(f"Maintenance took {result['duration_seconds']:.2f}s")
            >>> print(f"Audit logs deleted: {result['records_deleted']['audit_logs']}")
            >>> print(f"Total deleted: {result['total_records_deleted']} records")
        
        Raises:
            RuntimeError: If database not initialized
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            start_time = datetime.now()
            operations = {}
            records_deleted = {}
            
            logger.info("Starting database maintenance...")
            
            # ================================================================
            # Operation 1: VACUUM ANALYZE high-traffic tables
            # ================================================================
            
            # Tables identified from schema analysis (see comprehensive doc)
            tables_to_vacuum = [
                'stellar_transactions',   # 74,495 rows - high write volume
                'stellar_operations',     # 434 rows - frequent updates
                'account_balances',       # 651 rows - balance updates
                'holonic_metrics',        # 1,286 rows - evaluation results
                'ubec_balances',          # 651 rows - token balances
                'bioregion_analysis',     # 9,013 rows - analysis results
                'scheduler_execution_log' # Grows continuously
            ]
            
            vacuum_results = []
            for table in tables_to_vacuum:
                try:
                    # VACUUM ANALYZE reclaims space and updates statistics
                    # Use explicit schema reference for reliability
                    await self.execute(
                        f"VACUUM ANALYZE {self.schema}.{table}",
                        ()
                    )
                    vacuum_results.append(f"✓ {table}")
                    logger.debug(f"Vacuumed table: {self.schema}.{table}")
                    
                except Exception as e:
                    vacuum_results.append(f"✗ {table}: {str(e)}")
                    logger.error(f"Error vacuuming {self.schema}.{table}: {e}")
            
            operations['vacuum_analyze'] = ', '.join(vacuum_results)
            
            # ================================================================
            # Operation 2: Cleanup old audit logs (>90 days)
            # ================================================================
            
            cutoff_audit = datetime.now(timezone.utc) - timedelta(days=90)
            
            # Count records to delete
            audit_count_query = f"""
                SELECT COUNT(*) as count
                FROM {self.schema}.ubec_audit_log
                WHERE audited_at < $1
            """
            audit_count_result = await self.fetch_one(audit_count_query, (cutoff_audit,))
            audit_to_delete = audit_count_result.get('count', 0) if audit_count_result else 0
            
            if audit_to_delete > 0:
                audit_delete_query = f"""
                    DELETE FROM {self.schema}.ubec_audit_log
                    WHERE audited_at < $1
                """
                await self.execute(audit_delete_query, (cutoff_audit,))
                records_deleted['audit_logs'] = audit_to_delete
                logger.info(f"Deleted {audit_to_delete} old audit logs")
            else:
                records_deleted['audit_logs'] = 0
                logger.debug("No old audit logs to delete")
            
            operations['cleanup_audit_logs'] = f"✓ Deleted {audit_to_delete} records"
            
            # ================================================================
            # Operation 3: Cleanup old scheduler execution logs (>30 days)
            # ================================================================
            
            cutoff_scheduler = datetime.now(timezone.utc) - timedelta(days=30)
            
            # Count records to delete
            scheduler_count_query = f"""
                SELECT COUNT(*) as count
                FROM {self.schema}.scheduler_execution_log
                WHERE executed_at < $1
            """
            scheduler_count_result = await self.fetch_one(scheduler_count_query, (cutoff_scheduler,))
            scheduler_to_delete = scheduler_count_result.get('count', 0) if scheduler_count_result else 0
            
            if scheduler_to_delete > 0:
                scheduler_delete_query = f"""
                    DELETE FROM {self.schema}.scheduler_execution_log
                    WHERE executed_at < $1
                """
                await self.execute(scheduler_delete_query, (cutoff_scheduler,))
                records_deleted['scheduler_logs'] = scheduler_to_delete
                logger.info(f"Deleted {scheduler_to_delete} old scheduler logs")
            else:
                records_deleted['scheduler_logs'] = 0
                logger.debug("No old scheduler logs to delete")
            
            operations['cleanup_scheduler_logs'] = f"✓ Deleted {scheduler_to_delete} records"
            
            # ================================================================
            # Operation 4: Cleanup stale sync status records (>60 days)
            # ================================================================
            
            cutoff_sync = datetime.now(timezone.utc) - timedelta(days=60)
            
            # Count records to delete (only non-active)
            sync_count_query = f"""
                SELECT COUNT(*) as count
                FROM {self.schema}.sync_status
                WHERE last_sync < $1
                AND status != 'active'
            """
            sync_count_result = await self.fetch_one(sync_count_query, (cutoff_sync,))
            sync_to_delete = sync_count_result.get('count', 0) if sync_count_result else 0
            
            if sync_to_delete > 0:
                sync_delete_query = f"""
                    DELETE FROM {self.schema}.sync_status
                    WHERE last_sync < $1
                    AND status != 'active'
                """
                await self.execute(sync_delete_query, (cutoff_sync,))
                records_deleted['sync_status'] = sync_to_delete
                logger.info(f"Deleted {sync_to_delete} stale sync status records")
            else:
                records_deleted['sync_status'] = 0
                logger.debug("No stale sync status records to delete")
            
            operations['cleanup_sync_status'] = f"✓ Deleted {sync_to_delete} records"
            
            # ================================================================
            # Operation 5: Update database statistics
            # ================================================================
            
            try:
                await self.execute("ANALYZE", ())
                operations['analyze_database'] = "✓ Statistics updated"
                logger.debug("Database statistics updated")
            except Exception as e:
                operations['analyze_database'] = f"✗ Error: {str(e)}"
                logger.error(f"Error updating statistics: {e}")
            
            # ================================================================
            # Calculate duration and return results
            # ================================================================
            
            duration = (datetime.now() - start_time).total_seconds()
            total_deleted = sum(records_deleted.values())
            
            result = {
                'status': 'success',
                'duration_seconds': round(duration, 2),
                'operations': operations,
                'records_deleted': records_deleted,
                'total_records_deleted': total_deleted,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"✓ Database maintenance completed in {duration:.2f}s "
                f"(deleted {total_deleted} records)"
            )
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'duration_seconds': round(duration, 2),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.error(f"Database maintenance failed after {duration:.2f}s: {e}")
            return error_result
    
    @asynccontextmanager
    async def _get_connection(self):
        """
        Get a connection from the pool (internal context manager).
        
        Automatically sets the full search path for the connection.
        Supports UBEC's four-schema architecture (ubec_main, phenomenal, topology, public).
        
        The search path determines how PostgreSQL resolves unqualified table names:
        - Tables referenced without schema (e.g., FROM ubec_balances)
        - Searched in order: ubec_main → phenomenal → topology → public
        - First match is used
        
        Explicit schema references always work regardless of search path:
        - FROM ubec_main.ubec_balances (explicit)
        - FROM phenomenal.holons (explicit)
        
        This is an internal method - use fetch_all, fetch_one, execute instead.
        
        Yields:
            asyncpg.Connection: Database connection with search path configured
            
        Raises:
            RuntimeError: If database not initialized
            
        Example:
            >>> async with self._get_connection() as conn:
            ...     # Connection has search_path set automatically
            ...     result = await conn.fetch("SELECT * FROM ubec_balances")
        """
        if not self._initialized:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        
        async with self._pool.acquire() as conn:
            # Set full search path for this connection
            # Supports multi-schema queries: ubec_main, phenomenal, topology, public
            await conn.execute(f'SET search_path TO {self.search_path}')
            yield conn
    
    async def fetch_all(
        self,
        query: str,
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows from a query.
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Multi-Schema Support:
        - Explicit schema refs work: SELECT * FROM ubec_main.ubec_balances
        - Implicit refs use search path: SELECT * FROM ubec_balances
        - Cross-schema joins supported
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            List of dictionaries, one per row
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> # Explicit schema reference (recommended)
            >>> results = await db.fetch_all(
            ...     "SELECT * FROM ubec_main.ubec_balances WHERE balance > $1",
            ...     (1000,)
            ... )
            >>> 
            >>> # Implicit reference (uses search path)
            >>> results = await db.fetch_all(
            ...     "SELECT * FROM ubec_balances WHERE balance > $1",
            ...     (1000,)
            ... )
            >>> 
            >>> # Cross-schema join
            >>> results = await db.fetch_all('''
            ...     SELECT ub.balance, ph.autonomy_score
            ...     FROM ubec_main.ubec_balances ub
            ...     JOIN phenomenal.holons ph 
            ...         ON ub.account_id = ANY(ph.constituent_accounts)
            ... ''', ())
        """
        params = _validate_params(params, "fetch_all")
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                rows = await conn.fetch(query, *params)
                # Convert Record objects to dictionaries
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error executing fetch_all: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def fetch_one(
        self,
        query: str,
        params: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from a query.
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Multi-Schema Support:
        - Explicit schema refs work: SELECT * FROM ubec_main.ubec_balances
        - Implicit refs use search path: SELECT * FROM ubec_balances
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            Dictionary representing the row, or None if no results
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> # Explicit schema reference
            >>> account = await db.fetch_one(
            ...     "SELECT * FROM ubec_main.ubec_balances WHERE account_id = $1",
            ...     (account_id,)
            ... )
            >>> if account:
            ...     print(account['balance'])
        """
        params = _validate_params(params, "fetch_one")
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                row = await conn.fetchrow(query, *params)
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error executing fetch_one: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def execute(
        self,
        query: str,
        params: Tuple = ()
    ) -> str:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Multi-Schema Support:
        - Explicit schema refs work: INSERT INTO ubec_main.ubec_balances ...
        - Implicit refs use search path: INSERT INTO ubec_balances ...
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            Status string from the database (e.g., "INSERT 0 1")
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> status = await db.execute(
            ...     "INSERT INTO ubec_main.ubec_audit_log (message) VALUES ($1)",
            ...     ('Test message',)
            ... )
            >>> print(status)  # "INSERT 0 1"
        """
        params = _validate_params(params, "execute")
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                status = await conn.execute(query, *params)
                return status
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def execute_many(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Efficient for bulk inserts/updates as it uses a single connection.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params_list: List of parameter tuples
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> await db.execute_many(
            ...     "INSERT INTO ubec_main.ubec_audit_log (message) VALUES ($1)",
            ...     [('Message 1',), ('Message 2',), ('Message 3',)]
            ... )
        """
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings in all parameter sets
            converted_params = [
                convert_params_for_asyncpg(params) 
                for params in params_list
            ]
            
            async with self._get_connection() as conn:
                await conn.executemany(query, converted_params)
                
        except Exception as e:
            logger.error(f"Error executing execute_many: {e}")
            logger.error(f"Query: {query}")
            raise
    
    async def execute_query(
        self,
        query: str,
        params: Tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Generic query execution method (for compatibility).
        
        Provides a unified interface for different query types.
        This method is useful for protocols that need a single entry point.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple
            fetch_one: If True, return single row
            fetch_all: If True, return all rows
            
        Returns:
            Query results based on fetch flags:
            - fetch_one=True: Single row dict or None
            - fetch_all=True: List of row dicts
            - Otherwise: Status string
            
        Example:
            >>> # Fetch one row
            >>> row = await db.execute_query(
            ...     "SELECT * FROM ubec_main.ubec_balances WHERE id = $1",
            ...     (1,),
            ...     fetch_one=True
            ... )
            
            >>> # Fetch all rows
            >>> rows = await db.execute_query(
            ...     "SELECT * FROM ubec_main.ubec_balances",
            ...     (),
            ...     fetch_all=True
            ... )
            
            >>> # Execute non-query
            >>> status = await db.execute_query(
            ...     "INSERT INTO ubec_main.ubec_audit_log (msg) VALUES ($1)",
            ...     ('Test',)
            ... )
        """
        if fetch_one:
            return await self.fetch_one(query, params)
        elif fetch_all:
            return await self.fetch_all(query, params)
        else:
            return await self.execute(query, params)
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.
        
        Automatically commits on success or rolls back on exception.
        Provides a TransactionManager instance with fetch/execute methods.
        Sets full search path for transaction context.
        
        Yields:
            TransactionManager: Transaction manager for this transaction
            
        Example:
            >>> async with db.transaction() as tx:
            ...     await tx.execute(
            ...         "INSERT INTO ubec_main.ubec_audit_log (message) VALUES ($1)",
            ...         ('Starting transaction',)
            ...     )
            ...     await tx.execute(
            ...         "UPDATE ubec_main.ubec_balances SET balance = balance + $1 WHERE id = $2",
            ...         (100, account_id)
            ...     )
            ...     # Auto-commits here if no exception
            
        Raises:
            RuntimeError: If database not initialized
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Set full search path for transaction
            await conn.execute(f'SET search_path TO {self.search_path}')
            async with conn.transaction():
                # Create a temporary database manager for this transaction
                temp_manager = TransactionManager(conn, self.schema, self.search_path)
                yield temp_manager


# ============================================================================
# TRANSACTION MANAGER
# ============================================================================

class TransactionManager:
    """
    Helper class for transaction context.
    
    Provides the same fetch_all, fetch_one, and execute methods as
    AsyncDatabaseManager but within a transaction context.
    
    This class should not be instantiated directly - use
    AsyncDatabaseManager.transaction() instead.
    """
    
    def __init__(self, conn, schema: str, search_path: str):
        """
        Initialize transaction manager.
        
        Args:
            conn: asyncpg connection
            schema: Primary database schema
            search_path: Full PostgreSQL search path
        """
        self.conn = conn
        self.schema = schema
        self.search_path = search_path
    
    async def fetch_all(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            List of dictionaries
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]
    
    async def fetch_one(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            Dictionary or None
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        row = await self.conn.fetchrow(query, *params)
        return dict(row) if row else None
    
    async def execute(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> str:
        """
        Execute query within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            Status string
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        return await self.conn.execute(query, *params)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_database_manager_from_env() -> AsyncDatabaseManager:
    """
    Create database manager from environment variables.
    
    Implements Principle #8 (No Duplicate Config): Centralized configuration
    through environment variables.
    
    Expected environment variables:
        DB_HOST (default: 'localhost')
        DB_PORT (default: '5432')
        DB_NAME (default: 'ubec')
        DB_SCHEMA (default: 'ubec_main')
        DB_SEARCH_PATH (default: '{schema},public' or 'ubec_main,phenomenal,topology,public')
        DB_USER (default: 'ubec_app')
        DB_PASSWORD (default: '')
        DB_MIN_POOL (default: '2')
        DB_MAX_POOL (default: '10')
    
    Returns:
        AsyncDatabaseManager instance (not yet initialized)
        
    Example:
        >>> import os
        >>> os.environ['DB_HOST'] = 'db.example.com'
        >>> os.environ['DB_PASSWORD'] = 'secret'
        >>> os.environ['DB_SEARCH_PATH'] = 'ubec_main,phenomenal,topology,public'
        >>> 
        >>> db = create_database_manager_from_env()
        >>> await db.initialize()
    """
    import os
    
    # Get primary schema
    schema = os.getenv('DB_SCHEMA', 'ubec_main')
    
    # Get search path - supports full multi-schema architecture
    # Default: If not specified, use schema + public
    # For UBEC: Set to 'ubec_main,phenomenal,topology,public' in environment
    search_path = os.getenv(
        'DB_SEARCH_PATH',
        f'{schema},public'  # Backward compatible default
    )
    
    return AsyncDatabaseManager(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'ubec'),
        schema=schema,
        search_path=search_path,
        user=os.getenv('DB_USER', 'ubec_app'),
        password=os.getenv('DB_PASSWORD', ''),
        min_pool_size=int(os.getenv('DB_MIN_POOL', '2')),
        max_pool_size=int(os.getenv('DB_MAX_POOL', '10'))
    )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'AsyncDatabaseManager',
    'TransactionManager',
    'create_database_manager_from_env',
    'convert_query_placeholders',
    'convert_iso8601_to_datetime',
    'convert_params_for_asyncpg'
]
