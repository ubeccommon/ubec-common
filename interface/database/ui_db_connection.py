"""
UBEC Protocol - UI Database Connection
=======================================

Database connection management for the UBEC UI interface.
Uses asyncpg for async PostgreSQL operations.

This module provides connection pooling for the UBEC web interface,
supporting both the UI-specific database and the main UBEC database
for admin functionality.

Configuration via environment variables:
    UI_DB_HOST     - Database host (default: localhost)
    UI_DB_PORT     - Database port (default: 5432)
    UI_DB_NAME     - Database name (default: ubec)
    UI_DB_USER     - Database user (default: ubec_ui_user)
    UI_DB_PASSWORD - Database password
    UI_DB_SCHEMA   - Default schema name (default: ubec_ui)

Supported Schemas:
    - ubec_main: Core protocol tables (tokens, holonic, distributions, admin)
    - phenomenal: Spatial/mapping data (bioregions, POIs)
    - ubec_ui: UI interface data (applications, sessions)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, List

import asyncpg

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Database configuration - supports both UI and main UBEC databases
DB_CONFIG = {
    "host": os.getenv("UI_DB_HOST", os.getenv("DB_HOST", "localhost")),
    "port": int(os.getenv("UI_DB_PORT", os.getenv("DB_PORT", "5432"))),
    "database": os.getenv("UI_DB_NAME", os.getenv("DB_NAME", "ubec")),
    "user": os.getenv("UI_DB_USER", os.getenv("DB_USER", "ubec_ui_user")),
    "password": os.getenv("UI_DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
    "min_size": int(os.getenv("UI_DB_POOL_MIN", "2")),
    "max_size": int(os.getenv("UI_DB_POOL_MAX", "10")),
}

# Default schema for UI operations
DB_SCHEMA = os.getenv("UI_DB_SCHEMA", "ubec_ui")

# All available schemas in the UBEC database
AVAILABLE_SCHEMAS = ["ubec_main", "phenomenal", "ubec_ui"]

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


# =============================================================================
# Connection Pool Management
# =============================================================================

async def init_db_pool() -> asyncpg.Pool:
    """
    Initialize the database connection pool.
    
    Creates a connection pool with the configured parameters.
    The pool is reused for all database operations.
    
    Returns:
        asyncpg.Pool: The initialized connection pool
        
    Raises:
        Exception: If connection fails
    """
    global _pool
    
    if _pool is not None:
        return _pool
    
    try:
        # Build search path with all available schemas
        search_path = ", ".join(AVAILABLE_SCHEMAS + ["public"])
        
        _pool = await asyncpg.create_pool(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            min_size=DB_CONFIG["min_size"],
            max_size=DB_CONFIG["max_size"],
            command_timeout=60,
            ssl=False,  # Disable SSL for localhost connections
            server_settings={
                "search_path": search_path
            }
        )
        logger.info(
            f"UI Database pool initialized: {DB_CONFIG['database']} "
            f"(schemas: {search_path})"
        )
        return _pool
        
    except Exception as e:
        logger.error(f"Failed to initialize UI database pool: {e}")
        raise


async def close_db_pool():
    """
    Close the database connection pool.
    
    Should be called during application shutdown to cleanly
    release all database connections.
    """
    global _pool
    
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("UI Database pool closed")


async def get_pool() -> asyncpg.Pool:
    """
    Get the connection pool, initializing if necessary.
    
    This is the preferred method for obtaining the pool reference
    for use with context managers or direct pool operations.
    
    Returns:
        asyncpg.Pool: The active connection pool
    """
    global _pool
    
    if _pool is None:
        await init_db_pool()
    
    return _pool


async def get_db_pool() -> asyncpg.Pool:
    """
    Get the database connection pool.
    
    Alias for get_pool() - provided for compatibility with
    admin_routes.py and other modules that expect this function name.
    
    Returns:
        asyncpg.Pool: The active connection pool
    """
    return await get_pool()


# =============================================================================
# Connection Context Managers
# =============================================================================

@asynccontextmanager
async def get_db_connection(schema: str = None):
    """
    Get a database connection from the pool.
    
    Args:
        schema: Optional schema to set as search path (default: all schemas)
    
    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM ubec_main.admin_users")
            
        async with get_db_connection(schema="phenomenal") as conn:
            result = await conn.fetch("SELECT * FROM bioregion_boundaries")
    """
    pool = await get_pool()
    conn = await pool.acquire()
    
    try:
        if schema:
            await conn.execute(f"SET search_path TO {schema}, public")
        else:
            # Use all schemas
            search_path = ", ".join(AVAILABLE_SCHEMAS + ["public"])
            await conn.execute(f"SET search_path TO {search_path}")
        yield conn
    finally:
        await pool.release(conn)


@asynccontextmanager
async def get_db_transaction(schema: str = None):
    """
    Get a database connection with transaction.
    
    Args:
        schema: Optional schema to set as search path
    
    Usage:
        async with get_db_transaction() as conn:
            await conn.execute("INSERT INTO ubec_main.admin_audit_log ...")
            await conn.execute("UPDATE ubec_main.admin_users ...")
            # Automatically commits on success, rolls back on exception
    """
    pool = await get_pool()
    conn = await pool.acquire()
    
    try:
        if schema:
            await conn.execute(f"SET search_path TO {schema}, public")
        else:
            search_path = ", ".join(AVAILABLE_SCHEMAS + ["public"])
            await conn.execute(f"SET search_path TO {search_path}")
        async with conn.transaction():
            yield conn
    finally:
        await pool.release(conn)


# =============================================================================
# Schema-Specific Helpers
# =============================================================================

@asynccontextmanager
async def get_ubec_main_connection():
    """
    Get a connection with ubec_main schema as primary search path.
    
    Convenience wrapper for operations on core protocol tables:
    - admin_users, admin_sessions, admin_audit_log
    - ubec_balances, ubec_holonic_metrics
    - stellar_accounts, stellar_transactions
    - beneficiary_applications
    
    Usage:
        async with get_ubec_main_connection() as conn:
            users = await conn.fetch("SELECT * FROM admin_users")
    """
    async with get_db_connection(schema="ubec_main") as conn:
        yield conn


@asynccontextmanager
async def get_phenomenal_connection():
    """
    Get a connection with phenomenal schema as primary search path.
    
    Convenience wrapper for spatial/mapping operations:
    - bioregion_boundaries
    - points_of_interest
    
    Usage:
        async with get_phenomenal_connection() as conn:
            bioregions = await conn.fetch("SELECT * FROM bioregion_boundaries")
    """
    async with get_db_connection(schema="phenomenal") as conn:
        yield conn


# =============================================================================
# Health Check
# =============================================================================

async def check_db_health() -> dict:
    """
    Check database connectivity and return health status.
    
    Performs connectivity test and gathers basic statistics
    from available schemas.
    
    Returns:
        dict with status and details including:
        - status: 'healthy' or 'unhealthy'
        - database: database name
        - schemas: dict of schema statistics
        - error: error message if unhealthy
    """
    try:
        async with get_db_connection() as conn:
            # Basic connectivity test
            result = await conn.fetchval("SELECT 1")
            
            schema_stats = {}
            
            # Check ubec_main schema
            try:
                admin_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM ubec_main.admin_users
                """)
                schema_stats["ubec_main"] = {
                    "status": "available",
                    "admin_users": admin_count
                }
            except Exception:
                schema_stats["ubec_main"] = {"status": "not_available"}
            
            # Check phenomenal schema
            try:
                bioregion_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM phenomenal.bioregion_boundaries
                """)
                schema_stats["phenomenal"] = {
                    "status": "available",
                    "bioregions": bioregion_count
                }
            except Exception:
                schema_stats["phenomenal"] = {"status": "not_available"}
            
            # Check ubec_ui schema
            try:
                app_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM ubec_ui.applications
                """)
                schema_stats["ubec_ui"] = {
                    "status": "available",
                    "applications": app_count
                }
            except Exception:
                schema_stats["ubec_ui"] = {"status": "not_available"}
            
            return {
                "status": "healthy",
                "database": DB_CONFIG["database"],
                "host": DB_CONFIG["host"],
                "schemas": schema_stats
            }
            
    except Exception as e:
        logger.error(f"UI Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": DB_CONFIG["database"],
            "host": DB_CONFIG["host"]
        }


# =============================================================================
# Utility Functions
# =============================================================================

async def execute_query(query: str, *args, schema: str = None) -> List[dict]:
    """
    Execute a query and return results as list of dicts.
    
    Args:
        query: SQL query string
        *args: Query parameters
        schema: Optional schema to use
        
    Returns:
        List of result rows as dictionaries
    """
    async with get_db_connection(schema=schema) as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute_one(query: str, *args, schema: str = None) -> Optional[dict]:
    """
    Execute a query and return single result as dict.
    
    Args:
        query: SQL query string
        *args: Query parameters
        schema: Optional schema to use
        
    Returns:
        Single result row as dictionary, or None
    """
    async with get_db_connection(schema=schema) as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def execute_scalar(query: str, *args, schema: str = None):
    """
    Execute a query and return single scalar value.
    
    Args:
        query: SQL query string
        *args: Query parameters
        schema: Optional schema to use
        
    Returns:
        Single scalar value from first column of first row
    """
    async with get_db_connection(schema=schema) as conn:
        return await conn.fetchval(query, *args)
