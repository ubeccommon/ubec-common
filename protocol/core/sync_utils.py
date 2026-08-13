# core/sync_utils.py
"""
Shared Synchronization Utilities
Common patterns used by all sync operations

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

from typing import Dict, Any, Callable
from datetime import datetime
import asyncio

from config import get_logger


async def execute_sync_operation(
    element_name: str,
    token_code: str,
    sync_function: Callable,
    logger
) -> Dict[str, Any]:
    """
    Generic sync operation executor
    
    Used by all element protocols - NO DUPLICATION
    
    Args:
        element_name: Element name (Air, Water, Earth, Fire)
        token_code: Token code (UBEC, UBECrc, etc.)
        sync_function: Async function to execute
        logger: Logger instance
    
    Returns:
        Standardized sync result dictionary
    """
    logger.info(f"Starting {element_name} ({token_code}) synchronization...")
    
    start_time = datetime.utcnow()
    
    try:
        # Execute sync function
        result = await sync_function()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Standardize result format
        standard_result = {
            'element': element_name.lower(),
            'token': token_code,
            'status': 'success',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            **result  # Merge specific results
        }
        
        logger.info(
            f"  ✓ {element_name} sync complete "
            f"({duration:.2f}s)"
        )
        
        return standard_result
        
    except Exception as e:
        logger.error(f"  ✗ {element_name} sync failed: {e}")
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'element': element_name.lower(),
            'token': token_code,
            'status': 'error',
            'error': str(e),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration
        }
