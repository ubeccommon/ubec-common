# core/db/async_connection.py
"""
Async PostgreSQL Database Connection Module for UBEC Protocol

Fully async database connection implementation using asyncpg.
Supports three user types:
- ubec_app: Main application operations (default)
- ubec_readonly: Read-only access for reporting
- ubec_sync: Blockchain synchronization operations

Environment Variables Required (from .env):
    DB_HOST: Database host
    DB_PORT: Database port
    DB_NAME: Database name
    DB_SCHEMA: Default schema
    DB_USER: Application user
    DB_PASSWORD: Application user password
    DB_READONLY_USER: Read-only user (optional)
    DB_READONLY_PASSWORD: Read-only user password (optional)
    DB_SYNC_USER: Sync user (optional)
    DB_SYNC_PASSWORD: Sync user password (optional)
    DB_SSL_MODE: SSL mode (default: prefer)
    DB_POOL_MIN: Minimum pool connections (default: 2)
    DB_POOL_MAX: Maximum pool connections (default: 20)

Usage:
    # Using AsyncDatabaseConnection
    db = AsyncDatabaseConnection()
    await db.connect()
    results = await db.fetch_all("SELECT * FROM accounts")
    await db.close()
    
    # Context manager (recommended)
    async with AsyncDatabaseConnection() as db:
        results = await db.fetch_all("SELECT * FROM accounts")

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import os
import asyncpg
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def _get_connection_params(user_type='app') -> dict:
    """
    Get database connection parameters for specified user type.
    
    Args:
        user_type (str): Type of user - 'app', 'readonly', or 'sync'
        
    Returns:
        dict: Connection parameters for asyncpg
        
    Raises:
        ValueError: If credentials not configured for user type
    """
    # Base parameters
    params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'ubec'),
    }
    
    # User-specific credentials
    if user_type == 'app':
        params['user'] = os.getenv('DB_USER')
        params['password'] = os.getenv('DB_PASSWORD')
    elif user_type == 'readonly':
        params['user'] = os.getenv('DB_READONLY_USER')
        params['password'] = os.getenv('DB_READONLY_PASSWORD')
    elif user_type == 'sync':
        params['user'] = os.getenv('DB_SYNC_USER')
        params['password'] = os.getenv('DB_SYNC_PASSWORD')
    else:
        raise ValueError(f"Invalid user_type: {user_type}. Must be 'app', 'readonly', or 'sync'")
    
    # Validate credentials
    if not params.get('user') or not params.get('password'):
        raise ValueError(
            f"Database credentials not configured for user_type '{user_type}'. "
            f"Please set DB_{user_type.upper()}_USER and DB_{user_type.upper()}_PASSWORD in .env"
        )
    
    return params


class AsyncDatabaseConnection:
    """
    Async database connection wrapper with query methods.
    
    Provides fully async database operations using asyncpg.
    All I/O operations use async/await patterns per Principle #5.
    
    Example:
        # Manual connection management
        db = AsyncDatabaseConnection()
        await db.connect()
        results = await db.fetch_all("SELECT * FROM accounts")
        await db.close()
        
        # Context manager (recommended)
        async with AsyncDatabaseConnection() as db:
            results = await db.fetch_all("SELECT * FROM accounts")
            account = await db.fetch_one("SELECT * FROM accounts WHERE id = $1", 1)
    """
    
    def __init__(self, user_type='app', schema=None):
        """
        Initialize async database connection.
        
        Args:
            user_type (str): Database user type - 'app', 'readonly', or 'sync'
            schema (str): Database schema to use (default: from DB_SCHEMA env var)
        """
        self.user_type = user_type
        self.schema = schema or os.getenv('DB_SCHEMA', 'ubec_main')
        self.conn: Optional[asyncpg.Connection] = None
        self._connection_params = None
        
    async def connect(self):
        """Establish database connection."""
        if self.conn is not None:
            logger.warning("Connection already established")
            return
        
        try:
            self._connection_params = _get_connection_params(self.user_type)
            self.conn = await asyncpg.connect(**self._connection_params)
            
            # Set search path for schema
            await self.conn.execute(f"SET search_path TO {self.schema}, public")
            
            logger.debug(
                f"AsyncDatabaseConnection established: "
                f"user_type={self.user_type}, schema={self.schema}"
            )
        except Exception as e:
            logger.error(f"Failed to establish async database connection: {e}")
            raise
    
    async def close(self):
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None
            logger.debug("Async database connection closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Execute query and fetch all results.
        
        Args:
            query (str): SQL query to execute (use $1, $2, etc. for parameters)
            *args: Query parameters
            
        Returns:
            list: All result rows as dictionaries
            
        Example:
            results = await db.fetch_all("SELECT * FROM accounts WHERE balance > $1", 100)
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        try:
            rows = await self.conn.fetch(query, *args)
            # Convert asyncpg.Record to dict
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"fetch_all error: {e}")
            raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """
        Execute query and fetch one result.
        
        Args:
            query (str): SQL query to execute (use $1, $2, etc. for parameters)
            *args: Query parameters
            
        Returns:
            dict: Single result row as dictionary, or None
            
        Example:
            account = await db.fetch_one("SELECT * FROM accounts WHERE id = $1", 123)
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        try:
            row = await self.conn.fetchrow(query, *args)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"fetch_one error: {e}")
            raise
    
    async def fetch_val(self, query: str, *args) -> Any:
        """
        Execute query and fetch a single value.
        
        Args:
            query (str): SQL query to execute (use $1, $2, etc. for parameters)
            *args: Query parameters
            
        Returns:
            Any: Single value from the first column of the first row
            
        Example:
            count = await db.fetch_val("SELECT COUNT(*) FROM accounts")
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        try:
            return await self.conn.fetchval(query, *args)
        except Exception as e:
            logger.error(f"fetch_val error: {e}")
            raise
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query (str): SQL query to execute (use $1, $2, etc. for parameters)
            *args: Query parameters
            
        Returns:
            str: Command status (e.g., "INSERT 0 1", "UPDATE 5", "DELETE 3")
            
        Example:
            status = await db.execute(
                "INSERT INTO accounts (name, balance) VALUES ($1, $2)",
                "Alice", 100
            )
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        try:
            return await self.conn.execute(query, *args)
        except Exception as e:
            logger.error(f"execute error: {e}")
            raise
    
    async def execute_query(self, query: str, params: Optional[tuple] = None, 
                          fetch_one: bool = False, fetch_all: bool = True) -> Any:
        """
        Execute a query with flexible result fetching.
        
        Compatibility method for modules expecting this interface.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters (converted to *args)
            fetch_one (bool): Fetch single result
            fetch_all (bool): Fetch all results (ignored if fetch_one=True)
            
        Returns:
            Query results or command status
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        args = params or ()
        
        try:
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    return await self.fetch_one(query, *args)
                elif fetch_all:
                    return await self.fetch_all(query, *args)
                else:
                    await self.conn.execute(query, *args)
                    return None
            else:
                # INSERT, UPDATE, DELETE
                return await self.execute(query, *args)
        except Exception as e:
            logger.error(f"execute_query error: {e}")
            raise
    
    async def execute_transaction(self, queries_and_params: List[tuple]) -> bool:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries_and_params (list): List of (query, params) tuples
            
        Returns:
            bool: True if successful
            
        Example:
            await db.execute_transaction([
                ("INSERT INTO accounts (name) VALUES ($1)", ("Alice",)),
                ("UPDATE balances SET amount = $1 WHERE account_id = $2", (100, 1))
            ])
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        async with self.conn.transaction():
            try:
                for query, params in queries_and_params:
                    await self.conn.execute(query, *params)
                return True
            except Exception as e:
                logger.error(f"Transaction execution error: {e}")
                raise
    
    async def insert(self, table: str, data: Dict[str, Any], 
                    return_id: bool = True) -> Optional[int]:
        """
        Insert a record into a table.
        
        Args:
            table (str): Table name
            data (dict): Column-value pairs to insert
            return_id (bool): Whether to return the inserted ID
            
        Returns:
            int: Inserted ID if return_id=True, None otherwise
            
        Example:
            account_id = await db.insert('accounts', {'name': 'Alice', 'balance': 100})
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        if return_id:
            query += " RETURNING id"
            return await self.fetch_val(query, *values)
        else:
            await self.execute(query, *values)
            return None
    
    async def update(self, table: str, data: Dict[str, Any], 
                    condition: str, condition_params: tuple) -> str:
        """
        Update records in a table.
        
        Args:
            table (str): Table name
            data (dict): Column-value pairs to update
            condition (str): WHERE condition (use $1, $2, etc.)
            condition_params (tuple): Parameters for the condition
            
        Returns:
            str: Command status (e.g., "UPDATE 5")
            
        Example:
            status = await db.update(
                'accounts',
                {'balance': 200},
                'id = $1',
                (123,)
            )
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        set_expressions = [f"{col} = ${i+1}" for i, col in enumerate(data.keys())]
        values = list(data.values()) + list(condition_params)
        
        # Adjust condition parameter numbers
        param_offset = len(data)
        adjusted_condition = condition
        for i in range(len(condition_params), 0, -1):
            adjusted_condition = adjusted_condition.replace(f'${i}', f'${i + param_offset}')
        
        query = f"UPDATE {table} SET {', '.join(set_expressions)} WHERE {adjusted_condition}"
        
        return await self.execute(query, *values)
    
    async def delete(self, table: str, condition: str, condition_params: tuple) -> str:
        """
        Delete records from a table.
        
        Args:
            table (str): Table name
            condition (str): WHERE condition (use $1, $2, etc.)
            condition_params (tuple): Parameters for the condition
            
        Returns:
            str: Command status (e.g., "DELETE 3")
            
        Example:
            status = await db.delete('accounts', 'id = $1', (123,))
        """
        if not self.conn:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        query = f"DELETE FROM {table} WHERE {condition}"
        return await self.execute(query, *condition_params)
    
    async def get_by_id(self, table: str, id_value: Any, 
                       id_field: str = 'id') -> Optional[Dict[str, Any]]:
        """
        Get a record by ID.
        
        Args:
            table (str): Table name
            id_value: ID value to search for
            id_field (str): ID field name (default: 'id')
            
        Returns:
            dict: Record as dictionary, or None if not found
            
        Example:
            account = await db.get_by_id('accounts', 123)
        """
        query = f"SELECT * FROM {table} WHERE {id_field} = $1"
        return await self.fetch_one(query, id_value)


# Backward compatibility adapter for sync code
class DatabaseConnection:
    """
    Sync-to-async adapter for DatabaseConnection.
    
    Provides the same interface as the sync DatabaseConnection but routes
    through AsyncDatabaseConnection. This is for compatibility with existing
    code that expects a sync interface while the system transitions to fully async.
    
    Note: This adapter should be phased out in favor of AsyncDatabaseConnection.
    """
    
    def __init__(self, user_type='app'):
        """Initialize with user type."""
        self.user_type = user_type
        self.async_db = AsyncDatabaseConnection(user_type=user_type)
        self.conn = None  # For compatibility
        logger.warning(
            "DatabaseConnection sync adapter is deprecated. "
            "Use AsyncDatabaseConnection instead."
        )
    
    async def _ensure_connected(self):
        """Ensure async connection is established."""
        if self.async_db.conn is None:
            await self.async_db.connect()
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None):
        """Async fetch_all for compatibility."""
        await self._ensure_connected()
        return await self.async_db.fetch_all(query, *(params or ()))
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None):
        """Async fetch_one for compatibility."""
        await self._ensure_connected()
        return await self.async_db.fetch_one(query, *(params or ()))
    
    async def execute(self, query: str, params: Optional[tuple] = None):
        """Async execute for compatibility."""
        await self._ensure_connected()
        return await self.async_db.execute(query, *(params or ()))
    
    async def execute_query(self, query: str, params: Optional[tuple] = None,
                          fetch_one: bool = False, fetch_all: bool = True):
        """Async execute_query for compatibility."""
        await self._ensure_connected()
        return await self.async_db.execute_query(query, params, fetch_one, fetch_all)
    
    async def close(self):
        """Close async connection."""
        await self.async_db.close()
