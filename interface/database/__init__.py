"""
UBEC Protocol - Database Package
=================================

Database connection and management modules for the UBEC Protocol.

Modules:
    - ui_db_connection: Async PostgreSQL connection pool management

This project uses the services of Claude and Anthropic PBC.
"""

from .ui_db_connection import (
    init_db_pool,
    close_db_pool,
    get_pool,
    get_db_pool,
    get_db_connection,
    get_db_transaction,
    check_db_health,
    DB_CONFIG,
    AVAILABLE_SCHEMAS
)

__all__ = [
    'init_db_pool',
    'close_db_pool',
    'get_pool',
    'get_db_pool',
    'get_db_connection',
    'get_db_transaction',
    'check_db_health',
    'DB_CONFIG',
    'AVAILABLE_SCHEMAS'
]
