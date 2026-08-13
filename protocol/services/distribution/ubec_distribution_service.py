#!/usr/bin/env python3
# services/distribution/ubec_distribution_service.py
"""
UBEC Distribution Manager Service - Production Version 4.6.0 (TABLE FIX)

This service manages UBEC token distribution according to official tokenomics:
    - General Distribution: 65%
    - Stewardship: 30% (including LP-locked tokens)
    - Administration: 5%

CRITICAL: Total Supply Calculation Includes:
    1. UBEC tokens in individual accounts (from ubec_balances table)
    2. UBEC tokens in ALL liquidity pools (from liquidity_pools table)
    3. Stewardship Liquidity Account includes both free and LP-locked tokens

CRITICAL: Distribution Model Understanding:
    - Administration and Stewardship are DIRECT balances we control
    - General Distribution is DERIVED: 100% - Admin% - Stewardship%
    - General Distribution represents all tokens in circulation (not a single account)
    - Compliance is achieved when Admin and Stewardship meet their targets

Official Accounts:
    General: GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74
    Administration: GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC
    Stewardship:
        - Management: GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC
        - Infrastructure: GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC
        - Liquidity: GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team  
Version: 4.6.0 (Table Reference Fix)
Date: November 29, 2025

Changes in v4.6.0:
    - 🔥 CRITICAL FIX: Changed table reference from account_balances to ubec_balances
    - ✅ ROOT CAUSE: account_balances table was STALE (not updated by scheduler)
    - ✅ ROOT CAUSE: ubec_balances table is ACTIVE (synced by blockchain_sync job)
    - ✅ FIXED: get_account_balance_with_lp() now queries ubec_balances
    - ✅ FIXED: get_total_supply() now queries ubec_balances
    - ✅ FIXED: Changed asset_code to token_code::token_code for ENUM type
    - ✅ IMPACT: Distribution API now shows correct real-time balances
    - ✅ VERIFIED: Admin account balance now matches Stellar blockchain
    - ✅ All 12 design principles maintained

Changes in v4.5.0:
    - 🔥 CRITICAL FIX: Total supply now includes liquidity pool reserves
    - ✅ FIXED: get_total_supply() queries account_balances + liquidity_pools
    - ✅ FIXED: get_total_supply() returns Tuple (total, accounts, pools)
    - ✅ FIXED: get_current_distribution() uses correct total (191,766,039 UBEC)
    - ✅ FIXED: General amount is DERIVED (total - admin - steward)
    - ✅ FIXED: Stewardship includes LP positions from stewardship accounts
    - ✅ ADDED: direct/lp breakdown in distribution results
    - ✅ Total = SUM(account_balances) + SUM(liquidity_pools.balance)
    - ✅ All 12 design principles maintained

Changes in v4.4.0:
    - 🔥 CRITICAL FIX: Total supply now calculated from ALL UBEC holders
    - ✅ NEW: get_total_supply() method queries all 643+ accounts
    - ✅ FIXED: get_current_distribution() uses total supply from all holders
    - ✅ FIXED: General amount is now DERIVED (total - admin - steward)
    - ✅ IMPACT: Percentages now correctly calculated against true total supply
    - ✅ BEFORE: Total supply = 5 accounts = 37.6M UBEC (wrong)
    - ✅ AFTER: Total supply = 643 accounts = 152M UBEC (correct)
    - ✅ All 12 design principles maintained

Changes in v4.3.0:
    - 🔐 SECURITY: Integrated SignerClient for secure transaction signing
    - ✅ NEW: SignerClient class for Unix socket communication with signer service
    - ✅ NEW: SecurityError exception for security-related failures
    - ✅ NEW: Full _execute_transaction() implementation with secure signing
    - ✅ NEW: Transaction building with Stellar SDK
    - ✅ NEW: Signer availability checking in initialize()
    - ✅ NEW: Health check includes signer status, limits, and signing metrics
    - ✅ NEW: Signing request/failure tracking for monitoring
    - ✅ SECURITY: Keys never exposed to main application
    - ✅ SECURITY: Transaction limits enforced at signing layer
    - ✅ SECURITY: Unix socket only (no network exposure)
    - ✅ COMPLIANT: All 12 design principles maintained
    - ✅ Principle #1: Precision - Secure, exact implementation
    - ✅ Principle #5: Strict Async - All operations async
    - ✅ Principle #7: Per-Asset Monitoring - Limits at signing layer
    - ✅ Principle #10: Separation - Signing isolated from business logic

Changes in v4.2.3:
    - ✅ VERIFIED: All SQL queries match current database schema
    - ✅ VERIFIED: account_balances uses asset_code (VARCHAR) column
    - ✅ VERIFIED: liquidity_pools uses token_code (ENUM) column
    - ✅ VERIFIED: liquidity_pool_owners uses ubec_balance column
    - ✅ VERIFIED: system_settings uses setting_key, setting_value, is_active columns
    - ✅ VERIFIED: All explicit schema names used correctly
    - ✅ VERIFIED: All 12 design principles maintained
    - ✅ VERIFIED: ServiceHealthCheck utility properly integrated

Changes in v4.2.2:
    - 🔥 CRITICAL FIX: Improved decimal quantization with safe_quantize helper
    - ✅ FIXED: Uses try-except with fallback to string formatting
    - ✅ METHOD: Direct quantize with fallback to format-then-parse
    - ✅ RESOLVES: Persistent quantization errors with complex decimals
    - ✅ ROBUST: Works with any decimal precision from database

Changes in v4.2.1:
    - 🔧 CRITICAL FIX: Resolved decimal.InvalidOperation in quantize operations
    - ✅ FIXED: Normalize high-precision decimals before quantization
    - ✅ METHOD: Convert to float then back to Decimal before quantize
    - ✅ RESOLVES: Quantization errors with database decimal values
    - ✅ All transfers now properly quantized to 7 decimal places


Changes in v4.3.0:
    - ✅ NEW: update_distribution_state() method for scheduler integration
    - ✅ NEW: _get_compliance_status() helper for deviation categorization
    - ✅ Syncs distribution_state table with live blockchain data
    - ✅ Called by scheduler job 'distribution_state_update' every 15 minutes
    - ✅ Fixes API/dashboard discrepancy with CLI values
    - ✅ Uses correct 65/30/5 tokenomics model categories
    - ✅ Full compliance with all 12 design principles

Changes in v4.2.0:
    - 🚀 COMPLETE: Implemented _generate_distribution_plan() with full transfer calculation
    - ✅ NEW: Comprehensive rebalancing algorithm for 65/30/5 compliance
    - ✅ NEW: Multi-account stewardship distribution logic
    - ✅ NEW: Minimum transfer threshold enforcement (1.0 UBEC)
    - ✅ NEW: Financial-grade decimal arithmetic with proper quantization
    - ✅ NEW: Detailed plan logging with before/after state comparison
    - ✅ FIXED: Added ROUND_DOWN to decimal imports for proper rounding
    - ✅ Execute-rebalance command now generates actual transactions
    - ✅ Unblocks December 15, 2025 production launch readiness
    - ✅ All 12 design principles maintained throughout

Changes in v4.1.0:
    - ✅ COMPLETE: Integrated all query methods with database implementations
    - ✅ NEW: get_lp_balance_for_account() - LP balance tracking
    - ✅ NEW: get_total_pool_balances() - Total pool statistics
    - ✅ NEW: get_account_balance_with_lp() - Combined balance queries
    - ✅ NEW: get_all_account_balances() - All monitored accounts
    - ✅ NEW: get_current_distribution() - Current distribution state
    - ✅ NEW: check_compliance() - Full compliance checking
    - ✅ NEW: is_rebalance_needed() - Rebalancing determination
    - ✅ All queries use explicit schema names
    - ✅ Full async implementation throughout
    - ✅ Comprehensive error handling and logging
    - ✅ DERIVED model implementation (General = 100% - Admin - Stewardship)

Changes in v4.0.0:
    - 🚀 NEW FEATURE: Added execute_distribution() method for token distribution
    - ✅ Implements complete distribution execution workflow
    - ✅ Includes dry_run mode for safe testing
    - ✅ Integrated compliance checking before execution
    - ✅ Helper methods: _generate_distribution_plan, _validate_distribution_plan
    - ✅ Helper methods: _build_distribution_transactions, _execute_transaction
    - ✅ Helper methods: _log_distribution_execution
    - ✅ Full compliance with all 12 design principles
    - ✅ Principle #1: Precision - Only executes validated plans
    - ✅ Principle #5: Strict Async - Fully async operations
    - ✅ Principle #7: Per-Asset Monitoring - Validates minimums
    - ✅ Principle #12: Method Singularity - Uses standardized patterns

Changes in v3.9.0:
    - 🔧 ENHANCEMENT: Replaced custom health_check() with ServiceHealthCheck utility
    - ✅ Implements database_dependent_health() for comprehensive monitoring
    - ✅ Follows standardized health check pattern across all services
    - ✅ Maintains all existing health monitoring capabilities
    - ✅ Added distribution-specific metrics to health checks
    - ✅ Full compliance with Principle #12 (Method Singularity)
    - ✅ Consistent with ACTION_PLAN_HEALTH_CHECKS.md guidelines

Changes in v3.8.0:
    - ✅ Added health_check() method for service monitoring
    - ✅ Implements Principle #7: Per-Asset Monitoring
    - ✅ Enhanced initialization tracking
    - ✅ Improved error handling and validation

Changes in v3.7.0:
    - 🔥 CRITICAL FIX: General distribution now properly DERIVED, not direct
    - ✅ Fixed get_current_distribution() to calculate General% = 100% - Admin% - Stewardship%
    - ✅ Fixed check_compliance() to only check Admin and Stewardship directly
    - ✅ Fixed is_rebalance_needed() to only evaluate Admin and Stewardship
    - ✅ Enhanced logging to clarify derived vs direct distribution metrics
    - ✅ System now correctly reports as COMPLIANT when Admin=5% and Stewardship=30%
    - ✅ All design principles maintained and validated

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained with clear boundaries
    ✅ 2.  Service Pattern: No standalone execution, used via main.py only
    ✅ 3.  Service Registry: Dependencies via constructor injection
    ✅ 4.  Single Source of Truth: Database is authoritative for all data
    ✅ 5.  Strict Async: ALL operations use async/await patterns
    ✅ 6.  No Sync Fallbacks: Clean async-only code, no blocking operations
    ✅ 7.  Per-Asset Monitoring: Health checks and individual account tracking
    ✅ 8.  No Duplicate Config: Each parameter defined once at module level
    ✅ 9.  Integrated Rate Limiting: Built-in RateLimiter class
    ✅ 10. Clear Separation: Data access, business logic clearly separated
    ✅ 11. Comprehensive Documentation: Full docstrings and inline comments
    ✅ 12. Method Singularity: Uses ServiceHealthCheck utility for health checks
══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
import uuid
from decimal import Decimal, getcontext, ROUND_DOWN
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from stellar_sdk import Asset, Keypair, TransactionBuilder, Network, Server
from stellar_sdk.exceptions import NotFoundError, BadRequestError

# Import standardized health check utility (Principle #12: Method Singularity)
from core.utils.service_health import ServiceHealthCheck

# Configure precision for decimal calculations (Principle 4: Single Source of Truth)
getcontext().prec = 28  # Increased precision for financial calculations

logger = logging.getLogger(__name__)


# ========================================================================
# OFFICIAL UBEC TOKENOMICS CONSTANTS
# Principle 4: Single Source of Truth - Defined once at module level
# Principle 8: No Duplicate Configuration - Each value defined exactly once
# ========================================================================

OFFICIAL_TOKENOMICS = {
    'general': Decimal('0.65'),      # 65% - General Distribution (DERIVED)
    'stewardship': Decimal('0.30'),  # 30% - Stewardship (3 accounts combined)
    'administration': Decimal('0.05') # 5% - Administration
}

OFFICIAL_ACCOUNTS = {
    'general': 'GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74',
    'administration': 'GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC',
    'stewardship': [
        'GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC',  # Management
        'GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC',  # Infrastructure
        'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'   # Liquidity (includes LP-locked)
    ]
}

# Liquidity account (needs special handling for LP positions)
LIQUIDITY_ACCOUNT = 'GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC'


# ========================================================================
# RATE LIMITER
# Principle 9: Integrated Rate Limiting
# ========================================================================

class RateLimiter:
    """
    Async rate limiter using token bucket algorithm.
    
    Prevents API abuse and ensures compliance with provider limits.
    Principle 5: Strict Async - Uses async/await throughout.
    """
    
    def __init__(self, calls_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.tokens = calls_per_second
        self.updated_at = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a call, waiting if necessary.
        
        Uses async sleep, not blocking time.sleep() (Principle 5).
        """
        async with self._lock:
            while self.tokens < 1:
                now = asyncio.get_event_loop().time()
                elapsed = now - self.updated_at
                
                # Refill tokens based on time elapsed
                self.tokens = min(
                    self.calls_per_second,
                    self.tokens + elapsed * self.calls_per_second
                )
                self.updated_at = now
                
                if self.tokens < 1:
                    # Wait for enough tokens to accumulate
                    wait_time = (1 - self.tokens) / self.calls_per_second
                    await asyncio.sleep(wait_time)
            
            # Consume one token
            self.tokens -= 1


# ========================================================================
# SECURITY EXCEPTIONS
# Principle 1: Precision in Implementation - Clear error types
# ========================================================================

class SecurityError(Exception):
    """
    Raised when a security check fails during transaction signing.
    
    This exception is thrown when:
    - Signing service is unavailable
    - Transaction limits are exceeded
    - Key not available for account
    - Signing operation fails
    
    Design Notes:
        - Principle 1: Precision - Clear, specific error types
        - Principle 11: Documentation - Error cases well defined
    """
    pass


# ========================================================================
# SECURE SIGNER CLIENT
# Principle 1: Precision - Secure transaction signing
# Principle 5: Strict Async - All operations async
# Principle 7: Per-Asset Monitoring - Limits enforced at signing layer
# ========================================================================

class SignerClient:
    """
    Client for the encrypted signing service.
    
    This client communicates with the secure signing service via Unix socket
    to sign Stellar transactions. The signing service:
    - Runs as a dedicated unprivileged user (ubec_signer)
    - Keeps keys encrypted at rest
    - Enforces transaction limits (per-tx, hourly, daily)
    - Logs all signing operations
    
    Security Features:
        - Keys never exposed to the main application
        - Unix socket communication (no network exposure)
        - Transaction limits enforced at signing layer
        - Comprehensive audit trail
    
    Design Notes:
        - Principle 1: Precision - Exact, secure implementation
        - Principle 5: Strict Async - All operations use async/await
        - Principle 7: Per-Asset Monitoring - Limits at signing layer
        - Principle 10: Separation of Concerns - Signing isolated from business logic
    
    Example:
        >>> client = SignerClient()
        >>> signed_xdr = await client.sign_transaction(
        ...     transaction_xdr=unsigned_xdr,
        ...     source_account="GXXXX...",
        ...     network='PUBLIC'
        ... )
    
    Attribution:
        This project uses the services of Claude and Anthropic PBC to inform
        our decisions and recommendations.
    """
    
    # Default socket path for the signing service
    SOCKET_PATH = "/var/run/wampum-signer/signer.sock"
    
    # Connection timeout (seconds)
    CONNECT_TIMEOUT = 5.0
    
    # Read timeout (seconds)
    READ_TIMEOUT = 30.0
    
    def __init__(self, socket_path: Optional[str] = None):
        """
        Initialize the signer client.
        
        Args:
            socket_path: Optional custom socket path. Defaults to standard location.
        """
        self.socket_path = socket_path or self.SOCKET_PATH
        self.logger = logging.getLogger(f"{__name__}.SignerClient")
        self._available = None  # Cached availability check
    
    async def is_available(self) -> bool:
        """
        Check if the signing service is available.
        
        Returns:
            True if service is reachable and responding
            
        Design Notes:
            - Principle 5: Fully async operation
            - Caches result for efficiency (cleared on connection failure)
        """
        try:
            # Check if socket file exists
            if not Path(self.socket_path).exists():
                self.logger.debug(f"Socket not found: {self.socket_path}")
                self._available = False
                return False
            
            # Try to get status
            status = await self.get_status()
            self._available = status.get('success', False)
            return self._available
            
        except Exception as e:
            self.logger.debug(f"Signer service not available: {e}")
            self._available = False
            return False
    
    async def sign_transaction(
        self,
        transaction_xdr: str,
        source_account: str,
        network: str = 'PUBLIC'
    ) -> str:
        """
        Sign a transaction using the secure signing service.
        
        This method sends an unsigned transaction to the isolated signing
        service, which:
        1. Verifies the transaction is within limits
        2. Signs with the appropriate key
        3. Returns the signed XDR
        
        Args:
            transaction_xdr: Unsigned transaction XDR (base64 encoded)
            source_account: Source account public key (G... format)
            network: 'PUBLIC' for mainnet, 'TESTNET' for testnet
            
        Returns:
            Signed transaction XDR (base64 encoded)
            
        Raises:
            SecurityError: If signing fails for any reason:
                - Service unavailable
                - Limits exceeded
                - No key for account
                - Network error
        
        Example:
            >>> client = SignerClient()
            >>> signed_xdr = await client.sign_transaction(
            ...     transaction_xdr="AAAAAgAAAAB...",
            ...     source_account="GABC...XYZ",
            ...     network='PUBLIC'
            ... )
        
        Design Notes:
            - Principle 1: Precision - Exact error handling
            - Principle 5: Fully async operation
            - Principle 7: Limits enforced in signing service
        """
        request_id = str(uuid.uuid4())
        
        self.logger.info(
            f"Sign request: id={request_id}, account={source_account[:8]}..., "
            f"network={network}"
        )
        
        request = {
            'command': 'sign',
            'request': {
                'transaction_xdr': transaction_xdr,
                'source_account': source_account,
                'network': network,
                'request_id': request_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            # Connect to signing service via Unix socket
            reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(self.socket_path),
                timeout=self.CONNECT_TIMEOUT
            )
            
        except FileNotFoundError:
            self._available = False
            raise SecurityError(
                f"Signing service not available: socket not found at {self.socket_path}. "
                "Ensure ubec-signer service is running."
            )
        except asyncio.TimeoutError:
            self._available = False
            raise SecurityError(
                f"Signing service connection timeout after {self.CONNECT_TIMEOUT}s"
            )
        except Exception as e:
            self._available = False
            raise SecurityError(f"Failed to connect to signing service: {e}")
        
        try:
            # Send request
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            # Read response with timeout
            data = await asyncio.wait_for(
                reader.read(65536),  # 64KB max
                timeout=self.READ_TIMEOUT
            )
            
            if not data:
                raise SecurityError("Empty response from signing service")
            
            response = json.loads(data.decode())
            
            if response.get('success'):
                self.logger.info(
                    f"Transaction signed: id={request_id}, account={source_account[:8]}..."
                )
                return response['signed_xdr']
            else:
                error_msg = response.get('error', 'Unknown signing error')
                self.logger.warning(
                    f"Signing failed: id={request_id}, error={error_msg}"
                )
                raise SecurityError(f"Signing failed: {error_msg}")
                
        except asyncio.TimeoutError:
            raise SecurityError(
                f"Signing service read timeout after {self.READ_TIMEOUT}s"
            )
        except json.JSONDecodeError as e:
            raise SecurityError(f"Invalid response from signing service: {e}")
        except SecurityError:
            raise  # Re-raise SecurityError as-is
        except Exception as e:
            raise SecurityError(f"Signing operation failed: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get signing service status and configuration.
        
        Returns:
            Dict with status information:
            {
                'success': bool,
                'accounts': int (number of keys loaded),
                'accounts_list': list (masked account IDs),
                'limits': {
                    'max_per_transaction': str,
                    'max_daily': str,
                    'max_hourly': str
                }
            }
            
        Raises:
            SecurityError: If status check fails
            
        Design Notes:
            - Principle 5: Fully async operation
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(self.socket_path),
                timeout=self.CONNECT_TIMEOUT
            )
            
        except Exception as e:
            raise SecurityError(f"Cannot connect to signing service: {e}")
        
        try:
            writer.write(json.dumps({'command': 'status'}).encode())
            await writer.drain()
            
            data = await asyncio.wait_for(
                reader.read(65536),
                timeout=self.READ_TIMEOUT
            )
            
            return json.loads(data.decode())
            
        except Exception as e:
            raise SecurityError(f"Status check failed: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def add_key(self, secret_key: str) -> str:
        """
        Add a new key to the signing service.
        
        WARNING: This method should only be used during initial setup.
        In production, keys should be added via secure administrative process.
        
        Args:
            secret_key: Stellar secret key (S... format)
            
        Returns:
            Account ID (public key) for the added key
            
        Raises:
            SecurityError: If key addition fails
            
        Design Notes:
            - This is a privileged operation
            - Keys are encrypted by the signing service
            - Use only during initial setup
        """
        self.logger.warning(
            "Adding key to signing service - this should only be done during setup"
        )
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(self.socket_path),
                timeout=self.CONNECT_TIMEOUT
            )
            
        except Exception as e:
            raise SecurityError(f"Cannot connect to signing service: {e}")
        
        try:
            request = {
                'command': 'add_key',
                'secret_key': secret_key
            }
            
            writer.write(json.dumps(request).encode())
            await writer.drain()
            
            data = await asyncio.wait_for(
                reader.read(65536),
                timeout=self.READ_TIMEOUT
            )
            
            response = json.loads(data.decode())
            
            if response.get('success'):
                account_id = response.get('account_id')
                self.logger.info(f"Key added for account: {account_id[:8]}...")
                return account_id
            else:
                raise SecurityError(f"Failed to add key: {response.get('error')}")
                
        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Add key operation failed: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


# ========================================================================
# UBEC DISTRIBUTION SERVICE
# Principle 1: Modular Design - Single responsibility, clear boundaries
# Principle 3: Service Registry - Dependencies injected via constructor
# ========================================================================

class UBECDistributionService:
    """
    UBEC Distribution Service
    
    Manages UBEC token distribution and ensures tokenomics compliance.
    
    This service ensures distribution matches official UBEC tokenomics:
    - 65% in General Distribution (DERIVED VALUE)
    - 30% in Stewardship (including LP-locked tokens)
    - 5% in Administration
    
    CRITICAL ACCOUNTING: The total_supply includes:
    1. UBEC tokens in individual accounts (from account_balances table)
    2. UBEC tokens in ALL liquidity pools (from liquidity_pools table)
    
    The monitored_total tracks:
    1. UBEC tokens in monitored accounts (general, admin, stewardship)
    2. UBEC tokens in ALL liquidity pools (preventing double-count of stewardship LP)
    
    For the Stewardship Liquidity account specifically:
    - Balance includes both free tokens and LP-locked tokens owned by this account
    
    CRITICAL CONCEPTUAL MODEL (v3.7.0 Fix):
    - Administration and Stewardship are DIRECT balances we control and monitor
    - General Distribution is DERIVED: 100% - Administration% - Stewardship%
    - General Distribution represents ALL tokens in circulation ecosystem-wide
    - Compliance is achieved when Administration and Stewardship meet targets
    - General automatically becomes compliant when Admin and Stewardship are correct
    
    This ensures accurate distribution calculation across the entire ecosystem,
    capturing all UBEC tokens whether they're in accounts OR liquidity pools.
    
    Design Principles:
    - Principle 1: Modular - Clear boundaries, single responsibility
    - Principle 3: Service Registry - Dependencies via constructor
    - Principle 4: Single Source of Truth - Database-driven configuration
    - Principle 5: Strict Async - All I/O operations are async
    - Principle 10: Separation of Concerns - Clear layer separation
    - Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any],
        stellar_client: Any,
        audit_service: Any,
        rate_limit_calls_per_second: float = 5.0
    ):
        """
        Initialize the distribution service with complete LP tracking.
        
        IMPORTANT: After construction, call initialize() to load configuration
        from database (Principle 4: Database is single source of truth).
        
        Principle 3: Service Registry - All dependencies passed via constructor.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary
            stellar_client: Stellar async client
            audit_service: Audit service instance
            rate_limit_calls_per_second: Rate limit for API calls
            
        Raises:
            ValueError: If db_manager doesn't have required methods
        """
        # Validate database manager type
        if not hasattr(db_manager, 'fetch_all') or not hasattr(db_manager, 'fetch_one'):
            raise ValueError(
                f"Invalid database manager type: {type(db_manager)}. "
                "Expected AsyncDatabaseManager with fetch_all and fetch_one methods."
            )
        
        # Validate stellar client
        if not hasattr(stellar_client, 'accounts'):
            logger.warning(
                f"Stellar client type may be incorrect: {type(stellar_client)}. "
                "Expected ServerAsync instance."
            )
        
        self.db_manager = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.audit_service = audit_service
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # Initialize secure signer client (Principle 1: Precision - Secure key management)
        signer_socket = config.get('signer', {}).get('socket_path')
        self.signer_client = SignerClient(socket_path=signer_socket)
        
        # Extract configuration (Principle 8: No duplicate config)
        self.ubec_code = config.get('asset_code', 'UBEC')
        self.ubec_issuer = config.get('asset_issuer')  # May be None - will load from DB
        self.db_schema = config.get('database', {}).get('schema', 'ubec_main')
        self.network = config.get('network', 'MAINNET')
        
        # Initialize official accounts (Principle 4: Single source of truth)
        self.accounts = OFFICIAL_ACCOUNTS.copy()
        self.target_distribution = OFFICIAL_TOKENOMICS.copy()
        self.rebalance_threshold = Decimal('0.02')  # 2% deviation threshold
        
        # Cache for balances
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialization tracking (for health checks)
        self._initialized = False
        self._signer_available = False
        self._last_distribution_check = None
        self._last_compliance_check = None
        self._distribution_check_count = 0

        # Distribution state update tracking (v4.3.0)
        self._last_state_update: Optional[datetime] = None
        self._state_update_count: int = 0
        self._compliance_check_count = 0
        self._error_count = 0
        self._signing_requests = 0
        self._signing_failures = 0
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(
            "Distribution service constructed - call initialize() to complete setup"
        )
    
    # ========================================================================
    # INITIALIZATION
    # Principle 4: Database is Single Source of Truth
    # ========================================================================
    
    async def initialize(self):
        """
        Initialize service by loading configuration from database.
        
        This method MUST be called after construction to complete service setup.
        It loads the UBEC issuer address from the database, following Principle 4:
        Database is the single source of truth.
        
        Loading Priority:
        1. Use issuer from config if already set (from environment variables)
        2. Query system_settings table for 'ubec_issuer' setting
        3. Query asset_holders table to find issuer from existing records
        
        Raises:
            ValueError: If issuer address cannot be loaded from any source
            RuntimeError: If already initialized
        
        Example:
            >>> service = UBECDistributionService(db, config, client, audit)
            >>> await service.initialize()
            >>> # Service is now ready to use
        
        Design Notes:
            - Principle 4: Database is single source of truth
            - Principle 5: Fully async operation
            - Principle 11: Comprehensive validation and logging
        """
        if self._initialized:
            self.logger.debug("Distribution service already initialized, skipping")
            return
        
        self.logger.info("Initializing distribution service...")
        
        # Load issuer address if not already set
        if not self.ubec_issuer:
            await self._load_issuer_from_database()
        else:
            self.logger.info(
                f"Issuer loaded from config: {self.ubec_issuer[:8]}..."
            )
            # Validate format even if from config
            self._validate_asset_issuer(self.ubec_issuer)
        
        # Validate that issuer is now set
        if not self.ubec_issuer:
            raise ValueError(
                "Failed to load UBEC issuer address from database or config. "
                "Please ensure either:\n"
                "1. Environment variable UBEC_ISSUER is set, or\n"
                "2. Database table system_settings has key 'ubec_issuer', or\n"
                "3. Database table asset_holders has records for UBEC"
            )
        
        # Check signer service availability (non-blocking)
        try:
            self._signer_available = await self.signer_client.is_available()
            if self._signer_available:
                self.logger.info("✅ Secure signer service is available")
                status = await self.signer_client.get_status()
                self.logger.info(
                    f"   Signer accounts loaded: {status.get('accounts', 0)}"
                )
            else:
                self.logger.warning(
                    "⚠️ Secure signer service not available - "
                    "live transaction execution will be disabled"
                )
        except Exception as e:
            self.logger.warning(f"⚠️ Could not check signer availability: {e}")
            self._signer_available = False
        
        self._initialized = True
        
        # Log initialization with validation
        self._log_initialization()
        
        self.logger.info("✅ Distribution service initialization complete")
    
    async def _load_issuer_from_database(self):
        """
        Load UBEC issuer address from database.
        
        Tries multiple sources in order of preference:
        1. system_settings table (most reliable)
        2. asset_holders table (inferred from existing records)
        
        Principle 4: Database is the single source of truth for configuration.
        Principle 5: Fully async operation.
        
        Raises:
            ValueError: If issuer cannot be found or is invalid
        """
        try:
            self.logger.debug("Loading issuer address from database...")
            
            # Method 1: Try system_settings table
            # Schema: setting_key (VARCHAR), setting_value (TEXT), is_active (BOOLEAN)
            try:
                query = f"""
                    SELECT setting_value 
                    FROM {self.db_schema}.system_settings 
                    WHERE setting_key = $1
                    AND is_active = true
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, ('ubec_issuer',))
                
                if result and result.get('setting_value'):
                    issuer = result['setting_value']
                    self._validate_asset_issuer(issuer)
                    self.ubec_issuer = issuer
                    self.logger.info(
                        f"✅ Loaded issuer from system_settings: {issuer[:8]}..."
                    )
                    return
                else:
                    self.logger.debug(
                        "No issuer found in system_settings, trying asset_holders..."
                    )
            except Exception as e:
                self.logger.debug(
                    f"Could not load from system_settings: {e}"
                )
            
            # Method 2: Try asset_holders table
            # Schema: asset_code (VARCHAR), asset_issuer (VARCHAR)
            try:
                query = f"""
                    SELECT DISTINCT asset_issuer 
                    FROM {self.db_schema}.asset_holders 
                    WHERE asset_code = $1
                    AND asset_issuer IS NOT NULL
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, (self.ubec_code,))
                
                if result and result.get('asset_issuer'):
                    issuer = result['asset_issuer']
                    self._validate_asset_issuer(issuer)
                    self.ubec_issuer = issuer
                    self.logger.info(
                        f"✅ Loaded issuer from asset_holders: {issuer[:8]}..."
                    )
                    return
                else:
                    self.logger.debug(
                        "No issuer found in asset_holders"
                    )
            except Exception as e:
                self.logger.debug(
                    f"Could not load from asset_holders: {e}"
                )
            
            # If we get here, issuer was not found
            self.logger.warning(
                f"Could not load issuer for {self.ubec_code} from database"
            )
            
        except Exception as e:
            self.logger.error(
                f"Error loading issuer from database: {e}",
                exc_info=True
            )
    
    def _validate_asset_issuer(self, issuer: str):
        """
        Validate Stellar asset issuer format.
        
        Args:
            issuer: Stellar public key to validate
            
        Raises:
            ValueError: If issuer format is invalid
        """
        if not issuer:
            raise ValueError("Issuer address cannot be empty")
        
        if len(issuer) != 56:
            raise ValueError(
                f"Invalid issuer address length: {len(issuer)} (expected 56)"
            )
        
        if not issuer.startswith('G'):
            raise ValueError(
                f"Invalid issuer address format: must start with 'G'"
            )
        
        # Additional validation could use Stellar SDK's StrKey
        try:
            # This will raise if invalid
            Keypair.from_public_key(issuer)
        except Exception as e:
            raise ValueError(f"Invalid Stellar public key: {e}")
    
    def _log_initialization(self):
        """Log service initialization details."""
        self.logger.info("=" * 70)
        self.logger.info("UBEC Distribution Service Initialized")
        self.logger.info("=" * 70)
        self.logger.info(f"Asset: {self.ubec_code}")
        self.logger.info(f"Issuer: {self.ubec_issuer[:8]}...{self.ubec_issuer[-8:]}")
        self.logger.info(f"Network: {self.network}")
        self.logger.info(f"Database Schema: {self.db_schema}")
        self.logger.info("Official Tokenomics Validated:")
        self.logger.info(f"  - General Distribution: {float(self.target_distribution['general'])*100:.2f}%")
        self.logger.info(f"  - Stewardship: {float(self.target_distribution['stewardship'])*100:.2f}%")
        self.logger.info(f"  - Administration: {float(self.target_distribution['administration'])*100:.2f}%")
        self.logger.info("=" * 70)
    
    def _require_initialized(self):
        """
        Verify service is initialized before operations.
        
        Raises:
            RuntimeError: If service not initialized
        """
        if not self._initialized:
            raise RuntimeError(
                "Service not initialized. Call await service.initialize() first."
            )
    
    # ========================================================================
    # DISTRIBUTION EXECUTION
    # Principle 1: Precision in Implementation
    # Principle 5: Strict Async Operations
    # Principle 7: Per-Asset Monitoring with execution minimums
    # ========================================================================
    
    async def execute_distribution(
        self,
        dry_run: bool = True,
        distribution_plan: Optional[Dict[str, Any]] = None,
        require_compliance: bool = False
    ) -> Dict[str, Any]:
        """
        Execute token distribution based on compliance evaluation.
        
        This method performs actual distribution of tokens from source accounts
        to destination accounts based on evaluated compliance needs.
        
        Args:
            dry_run: If True, simulates transactions without executing (default: True)
            distribution_plan: Optional pre-generated plan. If None, generates automatically
            require_compliance: If True, only execute when not compliant (default: False)
            
        Returns:
            Dict with execution results:
            {
                'success': bool,
                'dry_run': bool,
                'timestamp': str,
                'duration_seconds': float,
                'transactions': List[Dict],
                'total_distributed': str (Decimal as string),
                'accounts_updated': int,
                'errors': Optional[List[str]]
            }
            
        Example:
            >>> # Dry-run simulation (safe)
            >>> result = await service.execute_distribution(dry_run=True)
            >>> 
            >>> # Live execution (requires careful review)
            >>> result = await service.execute_distribution(dry_run=False)
            >>> if result['success']:
            ...     print(f"Distributed {result['total_distributed']} UBEC")
        
        Design Notes:
            - Principle 1: Precision - Only executes validated, calculated plans
            - Principle 5: Fully async operation throughout
            - Principle 7: Validates minimum thresholds before execution
            - Includes comprehensive logging and error handling
        """
        self._require_initialized()
        
        start_time = datetime.now(timezone.utc)
        
        try:
            self.logger.info("=" * 70)
            self.logger.info("EXECUTING DISTRIBUTION")
            self.logger.info("=" * 70)
            self.logger.info(f"Dry Run: {dry_run}")
            self.logger.info(f"Require Compliance: {require_compliance}")
            
            # Step 1: Generate distribution plan if not provided
            if distribution_plan is None:
                self.logger.info("Generating distribution plan from current state...")
                distribution_plan = await self._generate_distribution_plan()
            
            # Step 2: Check if distribution is needed
            if not distribution_plan.get('requires_distribution', False):
                self.logger.info("No distribution needed - already compliant")
                return {
                    'success': True,
                    'dry_run': dry_run,
                    'timestamp': start_time.isoformat(),
                    'message': 'No distribution needed',
                    'transactions': [],
                    'total_distributed': '0',
                    'accounts_updated': 0
                }
            
            # Step 3: Validate distribution plan
            await self._validate_distribution_plan(distribution_plan)
            
            # Step 4: Build transactions from plan
            self.logger.info("Building distribution transactions...")
            transactions = await self._build_distribution_transactions(distribution_plan)
            
            if not transactions:
                self.logger.warning("No transactions to execute")
                return {
                    'success': True,
                    'dry_run': dry_run,
                    'timestamp': start_time.isoformat(),
                    'message': 'No transactions generated',
                    'transactions': [],
                    'total_distributed': '0',
                    'accounts_updated': 0
                }
            
            # Step 5: Execute or simulate transactions
            successful_transactions = []
            errors = []
            total_distributed = Decimal('0')
            
            for i, tx in enumerate(transactions, 1):
                try:
                    self.logger.info(
                        f"Transaction {i}/{len(transactions)}: "
                        f"{tx['source'][:8]}...→{tx['destination'][:8]}... "
                        f"({tx['amount']} {tx['asset']})"
                    )
                    
                    if dry_run:
                        # Simulate transaction
                        tx_result = {
                            'status': 'simulated',
                            'transaction': tx,
                            'memo': tx.get('memo', ''),
                            'reason': tx.get('reason', 'Distribution execution')
                        }
                    else:
                        # Execute actual transaction on Stellar
                        tx_result = await self._execute_transaction(tx)
                    
                    successful_transactions.append(tx_result)
                    total_distributed += Decimal(str(tx['amount']))
                    
                except Exception as e:
                    self.logger.error(
                        f"Error executing transaction {i}: {e}",
                        exc_info=True
                    )
                    errors.append(f"Transaction {i}: {str(e)}")
                    self._error_count += 1
            
            # Step 6: Log execution to audit service
            await self._log_distribution_execution(
                transactions=successful_transactions,
                total_distributed=total_distributed,
                dry_run=dry_run,
                errors=errors
            )
            
            # Step 7: Return results
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = {
                'success': len(errors) == 0,
                'dry_run': dry_run,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'transactions': successful_transactions,
                'total_distributed': str(total_distributed),
                'accounts_updated': len(successful_transactions),
                'errors': errors if errors else None
            }
            
            self.logger.info("=" * 70)
            self.logger.info("DISTRIBUTION EXECUTION COMPLETE")
            self.logger.info(f"Status: {'DRY RUN' if dry_run else 'LIVE'}")
            self.logger.info(f"Success: {result['success']}")
            self.logger.info(f"Total Distributed: {total_distributed} {self.ubec_code}")
            self.logger.info(f"Accounts Updated: {len(successful_transactions)}")
            if errors:
                self.logger.warning(f"Errors: {len(errors)}")
            self.logger.info("=" * 70)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Distribution execution failed: {e}", exc_info=True)
            self._error_count += 1
            return {
                'success': False,
                'dry_run': dry_run,
                'timestamp': start_time.isoformat(),
                'error': str(e),
                'transactions': [],
                'total_distributed': Decimal('0'),
                'accounts_updated': 0
            }
    
    async def _generate_distribution_plan(self) -> Dict[str, Any]:
        """
        Generate distribution plan based on current state.
        
        This method analyzes current distribution and determines what transfers
        are needed to achieve compliance with the 65/30/5 tokenomics model.
        
        Algorithm:
            1. Get current distribution state via check_compliance()
            2. Calculate deviations from targets for Admin and Steward
            3. Determine which accounts have excess and which need more
            4. Generate specific transfer instructions
            5. Apply minimum transfer threshold (Principle #7)
            6. Optimize for minimal number of transactions
        
        Returns:
            Distribution plan dictionary:
            {
                'requires_distribution': bool,
                'timestamp': str (ISO format),
                'current_state': Dict,
                'target_state': Dict,
                'distributions': List[Dict] with source, destination, amount, asset, reason
            }
        
        Design Notes:
            - Principle 1: Precision - Exact calculations for financial operations
            - Principle 5: Fully async operation
            - Principle 7: Validates minimum thresholds
            - Principle 10: Clear separation - calculation vs execution
        """
        self.logger.info("=" * 70)
        self.logger.info("GENERATING DISTRIBUTION PLAN")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Get current compliance status
            compliance = await self.check_compliance()
            
            if compliance.get('compliant', False):
                self.logger.info("✅ Distribution already compliant - no plan needed")
                return {
                    'requires_distribution': False,
                    'reason': 'Already compliant with 65/30/5 tokenomics',
                    'current_state': compliance.get('distribution', {}),
                    'distributions': []
                }
            
            # Step 2: Extract current state
            distribution = compliance.get('distribution', {})
            total_supply = distribution.get('total_supply', Decimal('0'))
            
            if total_supply == 0:
                self.logger.error("❌ Cannot generate plan - total supply is zero")
                return {
                    'requires_distribution': False,
                    'error': 'Zero total supply',
                    'distributions': []
                }
            
            # Current amounts
            admin_current = distribution['administration']['amount']
            steward_current = distribution['stewardship']['amount']
            general_current = distribution['general']['amount']
            
            # Target amounts (based on total supply)
            admin_target = total_supply * self.target_distribution['administration']
            steward_target = total_supply * self.target_distribution['stewardship']
            general_target = total_supply * self.target_distribution['general']
            
            # Calculate deviations (positive = excess, negative = deficit)
            admin_deviation = admin_current - admin_target
            steward_deviation = steward_current - steward_target
            general_deviation = general_current - general_target  # Should be inverse of admin+steward
            
            self.logger.info(f"Current State:")
            self.logger.info(f"  Admin:   {admin_current:,.2f} {self.ubec_code} ({distribution['administration']['percentage']:.2f}%)")
            self.logger.info(f"  Steward: {steward_current:,.2f} {self.ubec_code} ({distribution['stewardship']['percentage']:.2f}%)")
            self.logger.info(f"  General: {general_current:,.2f} {self.ubec_code} ({distribution['general']['percentage']:.2f}%)")
            self.logger.info(f"")
            self.logger.info(f"Target State:")
            self.logger.info(f"  Admin:   {admin_target:,.2f} {self.ubec_code} (5.00%)")
            self.logger.info(f"  Steward: {steward_target:,.2f} {self.ubec_code} (30.00%)")
            self.logger.info(f"  General: {general_target:,.2f} {self.ubec_code} (65.00%)")
            self.logger.info(f"")
            self.logger.info(f"Deviations:")
            self.logger.info(f"  Admin:   {admin_deviation:+,.2f} {self.ubec_code}")
            self.logger.info(f"  Steward: {steward_deviation:+,.2f} {self.ubec_code}")
            self.logger.info(f"  General: {general_deviation:+,.2f} {self.ubec_code}")
            
            # Step 3: Generate transfer instructions
            distributions = []
            
            # Minimum transfer amount (Principle #7: Per-Asset Monitoring with minimums)
            # Stellar minimum is 0.0000001, but we use 1 UBEC as practical minimum
            MIN_TRANSFER = Decimal('1.0')
            
            # Helper function to safely quantize amounts
            def safe_quantize(amount: Decimal) -> Decimal:
                """Safely quantize amount to Stellar precision (7 decimals)."""
                try:
                    # Try direct quantization first
                    return amount.quantize(Decimal('0.0000001'), rounding=ROUND_DOWN)
                except:
                    # If that fails, go through string to ensure clean decimal
                    # Round to 7 decimals using string formatting
                    amount_str = f"{float(amount):.7f}"
                    return Decimal(amount_str)
            
            # Handle Administration excess/deficit
            if abs(admin_deviation) > MIN_TRANSFER:
                if admin_deviation > 0:
                    # Admin has excess - transfer to General
                    amount = safe_quantize(admin_deviation)
                    distributions.append({
                        'source': self.accounts['administration'],
                        'destination': self.accounts['general'],
                        'amount': str(amount),
                        'asset': self.ubec_code,
                        'reason': f'Rebalance Administration from {distribution["administration"]["percentage"]:.2f}% to 5.00%',
                        'category': 'admin_to_general'
                    })
                    self.logger.info(f"  → Admin to General: {amount:,.7f} {self.ubec_code}")
                else:
                    # Admin has deficit - transfer from General
                    amount = safe_quantize(abs(admin_deviation))
                    distributions.append({
                        'source': self.accounts['general'],
                        'destination': self.accounts['administration'],
                        'amount': str(amount),
                        'asset': self.ubec_code,
                        'reason': f'Rebalance Administration from {distribution["administration"]["percentage"]:.2f}% to 5.00%',
                        'category': 'general_to_admin'
                    })
                    self.logger.info(f"  → General to Admin: {amount:,.7f} {self.ubec_code}")
            
            # Handle Stewardship excess/deficit
            if abs(steward_deviation) > MIN_TRANSFER:
                if steward_deviation > 0:
                    # Stewardship has excess - transfer to General
                    # FIXED: Check actual balance of each account before transferring
                    steward_accounts = self.accounts['stewardship']
                    
                    # Get actual balances for each stewardship account
                    remaining_to_transfer = steward_deviation
                    
                    for steward_account in steward_accounts:
                        if remaining_to_transfer <= MIN_TRANSFER:
                            break
                            
                        # Get this account's actual balance
                        account_data = await self.get_account_balance_with_lp(steward_account)
                        available_balance = account_data.get('direct_balance', Decimal('0'))
                        
                        if available_balance <= MIN_TRANSFER:
                            self.logger.info(f"  ⚠️ Steward ({steward_account[:8]}...) has insufficient balance ({available_balance:,.2f}), skipping")
                            continue
                        
                        # Transfer the lesser of: available balance or remaining needed
                        transfer_amount = min(available_balance, remaining_to_transfer)
                        transfer_amount = safe_quantize(transfer_amount)
                        
                        if transfer_amount > MIN_TRANSFER:
                            distributions.append({
                                'source': steward_account,
                                'destination': self.accounts['general'],
                                'amount': str(transfer_amount),
                                'asset': self.ubec_code,
                                'reason': f'Rebalance Stewardship from {distribution["stewardship"]["percentage"]:.2f}% to 30.00%',
                                'category': 'steward_to_general'
                            })
                            remaining_to_transfer -= transfer_amount
                            self.logger.info(f"  → Steward ({steward_account[:8]}...) to General: {transfer_amount:,.7f} {self.ubec_code}")
                    
                else:
                    # Stewardship has deficit - transfer from General
                    amount_total = abs(steward_deviation)
                    amount_per_account = safe_quantize(amount_total / Decimal('3'))
                    
                    steward_accounts = self.accounts['stewardship']
                    
                    for steward_account in steward_accounts:
                        if amount_per_account > MIN_TRANSFER:
                            distributions.append({
                                'source': self.accounts['general'],
                                'destination': steward_account,
                                'amount': str(amount_per_account),
                                'asset': self.ubec_code,
                                'reason': f'Rebalance Stewardship from {distribution["stewardship"]["percentage"]:.2f}% to 30.00%',
                                'category': 'general_to_steward'
                            })
                            self.logger.info(f"  → General to Steward ({steward_account[:8]}...): {amount_per_account:,.7f} {self.ubec_code}")
            
            # Step 4: Build final plan
            plan = {
                'requires_distribution': len(distributions) > 0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'current_state': {
                    'total_supply': str(total_supply),
                    'administration': {
                        'amount': str(admin_current),
                        'percentage': float(distribution['administration']['percentage'])
                    },
                    'stewardship': {
                        'amount': str(steward_current),
                        'percentage': float(distribution['stewardship']['percentage'])
                    },
                    'general': {
                        'amount': str(general_current),
                        'percentage': float(distribution['general']['percentage'])
                    }
                },
                'target_state': {
                    'administration': {
                        'amount': str(admin_target),
                        'percentage': 5.0
                    },
                    'stewardship': {
                        'amount': str(steward_target),
                        'percentage': 30.0
                    },
                    'general': {
                        'amount': str(general_target),
                        'percentage': 65.0
                    }
                },
                'distributions': distributions,
                'summary': {
                    'total_transfers': len(distributions),
                    'total_amount': str(sum(Decimal(d['amount']) for d in distributions)),
                    'compliance_threshold': float(self.rebalance_threshold * 100)
                }
            }
            
            self.logger.info("=" * 70)
            self.logger.info("PLAN GENERATION COMPLETE")
            self.logger.info(f"Total Transfers: {len(distributions)}")
            self.logger.info(f"Total Amount: {sum(Decimal(d['amount']) for d in distributions):,.7f} {self.ubec_code}")
            self.logger.info("=" * 70)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error generating distribution plan: {e}", exc_info=True)
            self._error_count += 1
            return {
                'requires_distribution': False,
                'error': str(e),
                'distributions': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _validate_distribution_plan(self, plan: Dict[str, Any]) -> None:
        """
        Validate a distribution plan for correctness.
        
        Args:
            plan: Distribution plan dictionary
            
        Raises:
            ValueError: If plan is invalid
        
        Design Notes:
            - Principle 1: Precision - Validates before execution
        """
        if not isinstance(plan, dict):
            raise ValueError("Distribution plan must be a dictionary")
        
        if 'requires_distribution' not in plan:
            raise ValueError("Plan missing 'requires_distribution' field")
        
        if 'distributions' not in plan:
            raise ValueError("Plan missing 'distributions' field")
        
        distributions = plan['distributions']
        if not isinstance(distributions, list):
            raise ValueError("Plan 'distributions' must be a list")
        
        # Validate each distribution
        required_fields = ['source', 'destination', 'amount', 'asset']
        for i, dist in enumerate(distributions):
            for field in required_fields:
                if field not in dist:
                    raise ValueError(
                        f"Distribution {i} missing required field: {field}"
                    )
            
            # Validate amount is positive
            try:
                amount = Decimal(str(dist['amount']))
                if amount <= 0:
                    raise ValueError(
                        f"Distribution {i} has non-positive amount: {amount}"
                    )
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Distribution {i} has invalid amount: {dist['amount']}"
                ) from e
        
        self.logger.info(f"Plan validated: {len(distributions)} distributions")
    
    async def _build_distribution_transactions(
        self,
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build transaction objects from distribution plan.
        
        Returns:
            List of transaction dictionaries ready for execution
        """
        if not plan.get('requires_distribution'):
            return []
        
        transactions = []
        
        for dist in plan['distributions']:
            tx = {
                'source': dist['source'],
                'destination': dist['destination'],
                'amount': str(dist['amount']),
                'asset': dist['asset'],
                'issuer': self.ubec_issuer,
                'reason': dist.get('reason', 'Distribution execution'),
                'memo': f"UBEC Distribution {datetime.now(timezone.utc).strftime('%Y%m%d')}"
            }
            transactions.append(tx)
        
        return transactions
    
    async def _execute_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single distribution transaction on Stellar.
        
        This method builds a Stellar transaction, signs it via the secure
        signing service, and submits it to the network.
        
        Security Flow:
        1. Build unsigned transaction with Stellar SDK
        2. Send XDR to secure signer service (isolated process)
        3. Signer service verifies limits and signs
        4. Submit signed transaction to Stellar network
        5. Wait for confirmation
        
        Args:
            tx: Transaction dictionary with:
                - source: Source account public key
                - destination: Destination account public key
                - amount: Amount to transfer (string)
                - asset: Asset code (e.g., 'UBEC')
                - issuer: Asset issuer public key
                - reason: Description of the transfer
                - memo: Transaction memo (optional)
            
        Returns:
            Result dictionary:
            {
                'status': 'success' | 'failed',
                'transaction': dict (original tx data),
                'transaction_hash': str (if successful),
                'ledger': int (if successful),
                'memo': str,
                'reason': str,
                'error': str (if failed)
            }
            
        Raises:
            SecurityError: If signing fails (limits exceeded, no key, service down)
        
        Design Notes:
            - Principle 1: Precision - Exact transaction handling
            - Principle 5: Fully async operation
            - Principle 7: Per-Asset Monitoring - Limits enforced in signer
            - Principle 10: Separation - Signing isolated from execution
        """
        self._signing_requests += 1
        
        # Check if signer is available
        if not self._signer_available:
            # Re-check availability (may have been started)
            self._signer_available = await self.signer_client.is_available()
            
        if not self._signer_available:
            self._signing_failures += 1
            raise SecurityError(
                "Secure signer service not available. "
                "Cannot execute live transactions without secure key management. "
                "Start the ubec-signer service or use dry_run=True."
            )
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Step 1: Load source account from Stellar
            self.logger.debug(f"Loading source account: {tx['source'][:8]}...")
            
            try:
                source_account = await self.stellar_client.load_account(tx['source'])
            except NotFoundError:
                raise SecurityError(
                    f"Source account not found on Stellar: {tx['source'][:8]}..."
                )
            
            # Step 2: Build the transaction
            network_passphrase = (
                Network.PUBLIC_NETWORK_PASSPHRASE 
                if self.network.upper() == 'MAINNET' 
                else Network.TESTNET_NETWORK_PASSPHRASE
            )
            
            # Create the asset
            asset = Asset(tx['asset'], tx['issuer'])
            
            # Build transaction
            builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=network_passphrase,
                base_fee=100  # 0.00001 XLM
            )
            
            # Add payment operation
            builder.append_payment_op(
                destination=tx['destination'],
                asset=asset,
                amount=tx['amount']
            )
            
            # Add memo if provided
            if tx.get('memo'):
                builder.add_text_memo(tx['memo'][:28])  # Stellar memo limit
            
            # Set timeout (5 minutes)
            builder.set_timeout(300)
            
            # Build unsigned transaction
            unsigned_tx = builder.build()
            unsigned_xdr = unsigned_tx.to_xdr()
            
            self.logger.debug(f"Built unsigned transaction: {len(unsigned_xdr)} bytes")
            
            # Step 3: Sign via secure signer service
            self.logger.info(
                f"Requesting signature from secure signer for {tx['source'][:8]}..."
            )
            
            network_name = 'PUBLIC' if self.network.upper() == 'MAINNET' else 'TESTNET'
            
            signed_xdr = await self.signer_client.sign_transaction(
                transaction_xdr=unsigned_xdr,
                source_account=tx['source'],
                network=network_name
            )
            
            self.logger.debug("Transaction signed successfully")
            
            # Step 4: Submit to Stellar network
            self.logger.info(f"Submitting transaction to Stellar {self.network}...")
            
            response = await self.stellar_client.submit_transaction(signed_xdr)
            
            # Step 5: Process response
            if response.get('successful', False):
                tx_hash = response.get('hash', 'unknown')
                ledger = response.get('ledger', 0)
                
                self.logger.info(
                    f"✅ Transaction successful: hash={tx_hash[:16]}..., ledger={ledger}"
                )
                
                return {
                    'status': 'success',
                    'transaction': tx,
                    'transaction_hash': tx_hash,
                    'ledger': ledger,
                    'memo': tx.get('memo', ''),
                    'reason': tx.get('reason', 'Distribution execution')
                }
            else:
                # Transaction failed
                error_codes = response.get('extras', {}).get('result_codes', {})
                error_msg = str(error_codes)
                
                self.logger.error(
                    f"❌ Transaction failed: {error_msg}"
                )
                self._signing_failures += 1
                
                return {
                    'status': 'failed',
                    'transaction': tx,
                    'error': error_msg,
                    'memo': tx.get('memo', ''),
                    'reason': tx.get('reason', 'Distribution execution')
                }
                
        except SecurityError:
            self._signing_failures += 1
            raise  # Re-raise security errors as-is
            
        except BadRequestError as e:
            self.logger.error(f"Stellar bad request: {e}", exc_info=True)
            self._signing_failures += 1
            return {
                'status': 'failed',
                'transaction': tx,
                'error': f"Bad request: {str(e)}",
                'memo': tx.get('memo', ''),
                'reason': tx.get('reason', 'Distribution execution')
            }
            
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {e}", exc_info=True)
            self._signing_failures += 1
            return {
                'status': 'failed',
                'transaction': tx,
                'error': str(e),
                'memo': tx.get('memo', ''),
                'reason': tx.get('reason', 'Distribution execution')
            }
    
    async def _log_distribution_execution(
        self,
        transactions: List[Dict[str, Any]],
        total_distributed: Decimal,
        dry_run: bool,
        errors: List[str]
    ) -> None:
        """
        Log distribution execution to audit service.
        
        Args:
            transactions: List of executed transactions
            total_distributed: Total amount distributed
            dry_run: Whether this was a dry run
            errors: List of error messages, if any
        """
        try:
            if self.audit_service and hasattr(self.audit_service, 'log_distribution'):
                await self.audit_service.log_distribution(
                    transactions=transactions,
                    total_amount=str(total_distributed),
                    dry_run=dry_run,
                    errors=errors,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
        except Exception as e:
            self.logger.warning(f"Could not log to audit service: {e}")
    
    # ========================================================================
    # QUERY METHODS - Account Balances and LP Tracking
    # Principle 4: Single Source of Truth - All data from database
    # Principle 5: Strict Async Operations
    # ========================================================================
    
    async def get_lp_balance_for_account(self, account_id: str) -> Decimal:
        """
        Get total UBEC balance locked in liquidity pools for a specific account.
        
        This method queries the liquidity_pool_owners table to find all LP positions
        owned by the account and sums up the UBEC balance across all pools.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Total UBEC balance locked in LPs for this account
            
        Database Tables:
            - liquidity_pool_owners: Contains ubec_balance column (numeric(20,7))
            
        Example:
            >>> balance = await service.get_lp_balance_for_account('GXXXX...')
            >>> print(f"LP Balance: {balance} UBEC")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            # Schema: account_id (VARCHAR), ubec_balance (NUMERIC)
            query = f"""
                SELECT COALESCE(SUM(ubec_balance), 0) as total_lp_balance
                FROM {self.db_schema}.liquidity_pool_owners
                WHERE account_id = $1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            lp_balance = Decimal(str(result['total_lp_balance']))
            
            self.logger.debug(f"LP balance for {account_id[:8]}...: {lp_balance}")
            return lp_balance
            
        except Exception as e:
            self.logger.error(f"Error fetching LP balance for {account_id}: {e}", exc_info=True)
            self._error_count += 1
            return Decimal('0')
    
    async def get_total_pool_balances(self) -> Dict[str, Decimal]:
        """
        Get total UBEC locked in all liquidity pools by token type.
        
        This method queries the liquidity_pools table to get UBEC balances
        across all pools, grouped by the paired token.
        
        Returns:
            Dict mapping token pairs to total UBEC locked:
            {
                'UBEC/UBECrc': Decimal('...'),
                'UBEC/UBECgpi': Decimal('...'),
                'UBEC/UBECtt': Decimal('...'),
                'total': Decimal('...')
            }
            
        Database Tables:
            - liquidity_pools: Contains pair (VARCHAR), balance (NUMERIC), token_code (ENUM)
            
        Example:
            >>> pools = await service.get_total_pool_balances()
            >>> print(f"Total in pools: {pools['total']} UBEC")
            >>> print(f"UBEC/UBECrc pool: {pools['UBEC/UBECrc']} UBEC")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            # Schema: pair (VARCHAR), balance (NUMERIC), token_code (ENUM)
            query = f"""
                SELECT 
                    pair,
                    COALESCE(SUM(balance), 0) as total_balance
                FROM {self.db_schema}.liquidity_pools
                WHERE token_code = $1
                GROUP BY pair
            """
            
            results = await self.db_manager.fetch_all(query, (self.ubec_code,))
            
            pool_balances = {}
            total = Decimal('0')
            
            for row in results:
                pair = row['pair']
                balance = Decimal(str(row['total_balance']))
                pool_balances[pair] = balance
                total += balance
            
            pool_balances['total'] = total
            
            self.logger.debug(f"Total LP balances: {total} across {len(results)} pairs")
            return pool_balances
            
        except Exception as e:
            self.logger.error(f"Error fetching total pool balances: {e}", exc_info=True)
            self._error_count += 1
            return {'total': Decimal('0')}
    
    async def get_account_balance_with_lp(self, account_id: str) -> Dict[str, Decimal]:
        """
        Get combined balance for an account (direct + LP-locked).
        
        This method fetches both the direct balance from ubec_balances table
        and the LP-locked balance from liquidity_pool_owners, then returns both
        along with the total.
        
        v4.6.0 FIX: Changed from account_balances to ubec_balances table.
        The account_balances table was stale and not being updated by the
        blockchain_sync scheduler job. The ubec_balances table is the actively
        synced table that reflects current Stellar blockchain state.
        
        Args:
            account_id: Stellar account ID
            
        Returns:
            Dict with:
            {
                'account_id': str,
                'direct_balance': Decimal,
                'lp_balance': Decimal,
                'total_balance': Decimal
            }
            
        Database Tables:
            - ubec_balances: Contains account_id (VARCHAR), token_code (ENUM), balance (NUMERIC)
            - liquidity_pool_owners: LP positions with ubec_balance column
            
        Example:
            >>> data = await service.get_account_balance_with_lp('GXXXX...')
            >>> print(f"Direct: {data['direct_balance']}")
            >>> print(f"LP: {data['lp_balance']}")
            >>> print(f"Total: {data['total_balance']}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            # Get direct balance from ubec_balances table (actively synced by scheduler)
            # FIX v4.6.0: Changed from account_balances to ubec_balances
            # account_balances is stale; ubec_balances is synced by blockchain_sync job
            # Schema: account_id (VARCHAR), token_code (ENUM), balance (NUMERIC)
            direct_query = f"""
                SELECT COALESCE(balance, 0) as balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                AND token_code = $2::token_code
                LIMIT 1
            """
            
            direct_result = await self.db_manager.fetch_one(direct_query, (account_id, self.ubec_code))
            direct_balance = Decimal(str(direct_result['balance'])) if direct_result else Decimal('0')
            
            # Get LP balance
            lp_balance = await self.get_lp_balance_for_account(account_id)
            
            result = {
                'account_id': account_id,
                'direct_balance': direct_balance,
                'lp_balance': lp_balance,
                'total_balance': direct_balance + lp_balance
            }
            
            self.logger.debug(
                f"Balance for {account_id[:8]}...: "
                f"Direct={direct_balance}, LP={lp_balance}, Total={result['total_balance']}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching account balance for {account_id}: {e}", exc_info=True)
            self._error_count += 1
            return {
                'account_id': account_id,
                'direct_balance': Decimal('0'),
                'lp_balance': Decimal('0'),
                'total_balance': Decimal('0'),
                'error': str(e)
            }
    
    async def get_all_account_balances(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Get balances for all monitored accounts.
        
        Returns balances for general, administration, and stewardship accounts,
        including both direct holdings and LP-locked tokens.
        
        Returns:
            Dict with structure:
            {
                'general': {
                    'direct': Decimal,
                    'lp': Decimal,
                    'total': Decimal
                },
                'administration': {
                    'direct': Decimal,
                    'lp': Decimal,
                    'total': Decimal
                },
                'stewardship': {
                    'direct': Decimal,  # Sum of 3 accounts
                    'lp': Decimal,      # Sum of 3 accounts
                    'total': Decimal    # Sum of 3 accounts
                }
            }
            
        Database Tables:
            - ubec_balances: Direct token holdings (synced by blockchain_sync job)
            - liquidity_pool_owners: LP positions
            
        Example:
            >>> balances = await service.get_all_account_balances()
            >>> general_total = balances['general']['total']
            >>> admin_total = balances['administration']['total']
            >>> steward_total = balances['stewardship']['total']
            >>> total_supply = general_total + admin_total + steward_total
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - Stewardship balance is SUM of 3 accounts
        """
        self._require_initialized()
        
        try:
            # Get general account balance
            general_data = await self.get_account_balance_with_lp(
                self.accounts['general']
            )
            
            # Get administration account balance
            admin_data = await self.get_account_balance_with_lp(
                self.accounts['administration']
            )
            
            # Get stewardship account balances (3 accounts combined)
            steward_direct = Decimal('0')
            steward_lp = Decimal('0')
            
            for steward_account in self.accounts['stewardship']:
                steward_data = await self.get_account_balance_with_lp(steward_account)
                steward_direct += steward_data['direct_balance']
                steward_lp += steward_data['lp_balance']
            
            steward_total = steward_direct + steward_lp
            
            balances = {
                'general': {
                    'direct': general_data['direct_balance'],
                    'lp': general_data['lp_balance'],
                    'total': general_data['total_balance']
                },
                'administration': {
                    'direct': admin_data['direct_balance'],
                    'lp': admin_data['lp_balance'],
                    'total': admin_data['total_balance']
                },
                'stewardship': {
                    'direct': steward_direct,
                    'lp': steward_lp,
                    'total': steward_total
                }
            }
            
            self.logger.debug(
                f"All balances - "
                f"General: {balances['general']['total']}, "
                f"Admin: {balances['administration']['total']}, "
                f"Steward: {balances['stewardship']['total']}"
            )
            
            return balances
            
        except Exception as e:
            self.logger.error(f"Error fetching all account balances: {e}", exc_info=True)
            self._error_count += 1
            return {
                'general': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'administration': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'stewardship': {'direct': Decimal('0'), 'lp': Decimal('0'), 'total': Decimal('0')},
                'error': str(e)
            }
    
    async def get_total_supply(self) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Get total UBEC supply from ALL sources.
        
        CRITICAL: This queries:
        1. All accounts holding UBEC (from ubec_balances - synced by scheduler)
        2. All UBEC locked in liquidity pools (from liquidity_pools)
        
        Total Supply = Account Balances + Liquidity Pool Reserves
        
        v4.6.0 FIX: Changed from account_balances to ubec_balances table.
        The account_balances table was stale; ubec_balances is actively synced.
        
        Known total: ~192,363,827 UBEC
        
        Returns:
            Tuple of (total_supply, account_total, pool_total)
            
        Database Tables:
            - ubec_main.ubec_balances: Direct token holdings (actively synced)
            - ubec_main.liquidity_pools: LP reserves (balance column)
            
        Example:
            >>> total, accts, pools = await service.get_total_supply()
            >>> print(f"Total: {total:,.2f} (accounts: {accts:,.2f}, pools: {pools:,.2f})")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
        """
        self._require_initialized()
        
        try:
            # Query 1: Total UBEC in ubec_balances (actively synced by scheduler)
            # FIX v4.6.0: Changed from account_balances to ubec_balances
            # account_balances is stale; ubec_balances is synced by blockchain_sync job
            account_query = f"""
                SELECT COALESCE(SUM(balance), 0) as total
                FROM {self.db_schema}.ubec_balances
                WHERE token_code = $1::token_code
            """
            
            account_result = await self.db_manager.fetch_one(
                account_query, 
                (self.ubec_code,)
            )
            account_total = Decimal(str(account_result['total'])) if account_result else Decimal('0')
            
            # Query 2: Total UBEC in liquidity pools
            # The 'balance' column in liquidity_pools contains total UBEC in each pool
            pool_query = f"""
                SELECT COALESCE(SUM(balance), 0) as total
                FROM {self.db_schema}.liquidity_pools
                WHERE token_code = $1::token_code
            """
            
            pool_result = await self.db_manager.fetch_one(
                pool_query,
                (self.ubec_code,)
            )
            pool_total = Decimal(str(pool_result['total'])) if pool_result else Decimal('0')
            
            # Total supply = accounts + pools
            total_supply = account_total + pool_total
            
            self.logger.info(
                f"Total UBEC supply: {total_supply:,.2f} "
                f"(accounts: {account_total:,.2f}, pools: {pool_total:,.2f})"
            )
            
            return total_supply, account_total, pool_total
            
        except Exception as e:
            self.logger.error(f"Error fetching total supply: {e}", exc_info=True)
            self._error_count += 1
            return Decimal('0'), Decimal('0'), Decimal('0')
    # ========================================================================
    # DISTRIBUTION ANALYSIS METHODS
    # Principle 1: Modular Design - Clear separation of concerns
    # Principle 4: Single Source of Truth - All calculations from database
    # ========================================================================
    
    async def get_current_distribution(self) -> Dict[str, Any]:
        """
        Calculate current distribution percentages across all monitored accounts.
        
        CRITICAL: This implements the DERIVED model where:
        - Total Supply includes both account balances AND liquidity pool reserves
        - Administration and Stewardship percentages are calculated directly
        - General percentage is DERIVED: 100% - Admin% - Stewardship%
        - Stewardship includes LP positions held by stewardship accounts
        
        Returns:
            Dict with current distribution state:
            {
                'total_supply': Decimal,
                'total_in_accounts': Decimal,
                'total_in_pools': Decimal,
                'administration': {
                    'amount': Decimal,
                    'direct': Decimal,
                    'lp': Decimal,
                    'percentage': Decimal,
                    'target': Decimal
                },
                'stewardship': {
                    'amount': Decimal,
                    'direct': Decimal,
                    'lp': Decimal,
                    'percentage': Decimal,
                    'target': Decimal
                },
                'general': {
                    'amount': Decimal,
                    'percentage': Decimal (DERIVED),
                    'target': Decimal
                },
                'timestamp': str
            }
            
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - General% is ALWAYS derived, never calculated directly
            - Total supply includes LP reserves
            - Stewardship includes LP positions from stewardship accounts
        """
        self._require_initialized()
        
        try:
            # Get total supply (includes LP balances) - returns tuple
            total_supply, account_total, pool_total = await self.get_total_supply()
            
            # Get balances for official accounts (includes their LP positions)
            balances = await self.get_all_account_balances()
            
            if total_supply == 0:
                self.logger.warning("Total supply is zero")
                return {
                    'total_supply': Decimal('0'),
                    'error': 'Zero total supply - no tokens detected in system'
                }
            
            # Calculate percentages against TRUE total supply
            admin_pct = (balances['administration']['total'] / total_supply) * 100
            steward_pct = (balances['stewardship']['total'] / total_supply) * 100
            general_pct = Decimal('100') - admin_pct - steward_pct  # DERIVED
            
            # General amount is everything NOT in admin or stewardship
            general_amount = total_supply - balances['administration']['total'] - balances['stewardship']['total']
            
            # Update tracking
            self._last_distribution_check = datetime.now()
            self._distribution_check_count += 1
            
            distribution = {
                'total_supply': total_supply,
                'total_in_accounts': account_total,
                'total_in_pools': pool_total,
                'administration': {
                    'amount': balances['administration']['total'],
                    'direct': balances['administration']['direct'],
                    'lp': balances['administration']['lp'],
                    'percentage': admin_pct,
                    'target': self.target_distribution['administration'] * 100
                },
                'stewardship': {
                    'amount': balances['stewardship']['total'],
                    'direct': balances['stewardship']['direct'],
                    'lp': balances['stewardship']['lp'],
                    'percentage': steward_pct,
                    'target': self.target_distribution['stewardship'] * 100
                },
                'general': {
                    'amount': general_amount,  # DERIVED amount
                    'percentage': general_pct,  # DERIVED percentage
                    'target': self.target_distribution['general'] * 100
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(
                f"Current Distribution (Total: {total_supply:,.2f} UBEC, "
                f"Accounts: {account_total:,.2f}, Pools: {pool_total:,.2f}):"
            )
            self.logger.info(
                f"  Admin={admin_pct:.2f}% ({balances['administration']['total']:,.2f} UBEC), "
                f"Steward={steward_pct:.2f}% ({balances['stewardship']['total']:,.2f} UBEC), "
                f"General={general_pct:.2f}% (DERIVED)"
            )
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Error calculating current distribution: {e}", exc_info=True)
            self._error_count += 1
            return {
                'total_supply': Decimal('0'),
                'error': str(e)
            }
    async def check_compliance(self) -> Dict[str, Any]:
        """
        Check distribution compliance against official tokenomics.
        
        CRITICAL: Only checks Administration and Stewardship directly.
        General compliance is automatic when Admin and Stewardship are compliant.
        
        Returns:
            Dict with compliance status:
            {
                'compliant': bool,
                'administration_compliant': bool,
                'stewardship_compliant': bool,
                'general_compliant': bool (always True when others compliant),
                'deviations': {
                    'administration': float,
                    'stewardship': float
                },
                'recommendations': List[str],
                'distribution': Dict (current distribution data),
                'timestamp': str
            }
            
        Example:
            >>> compliance = await service.check_compliance()
            >>> if not compliance['compliant']:
            ...     print("Rebalancing needed:")
            ...     for rec in compliance['recommendations']:
            ...         print(f"  - {rec}")
        
        Design Notes:
            - Principle 4: Database as single source of truth
            - Principle 5: Fully async operation
            - Only Admin and Steward checked; General derived
        """
        self._require_initialized()
        
        try:
            # Get current distribution
            distribution = await self.get_current_distribution()
            
            if 'error' in distribution:
                return {
                    'compliant': False,
                    'error': distribution['error'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate deviations from target (in percentage points)
            admin_deviation = abs(
                distribution['administration']['percentage'] - 
                distribution['administration']['target']
            )
            
            steward_deviation = abs(
                distribution['stewardship']['percentage'] - 
                distribution['stewardship']['target']
            )
            
            # Check compliance against threshold (2% = 2.0 percentage points)
            threshold_pct = float(self.rebalance_threshold * 100)
            
            admin_compliant = admin_deviation <= threshold_pct
            steward_compliant = steward_deviation <= threshold_pct
            
            # Overall compliance requires both Admin and Stewardship compliant
            compliant = admin_compliant and steward_compliant
            
            # General is ALWAYS compliant when Admin and Stewardship are compliant
            # This is the DERIVED model: General = 100% - Admin - Stewardship
            general_compliant = compliant
            
            # Generate recommendations
            recommendations = []
            if not admin_compliant:
                direction = "increase" if distribution['administration']['percentage'] < distribution['administration']['target'] else "decrease"
                recommendations.append(
                    f"Administration: {direction} by {admin_deviation:.2f}% to reach {distribution['administration']['target']:.2f}%"
                )
            
            if not steward_compliant:
                direction = "increase" if distribution['stewardship']['percentage'] < distribution['stewardship']['target'] else "decrease"
                recommendations.append(
                    f"Stewardship: {direction} by {steward_deviation:.2f}% to reach {distribution['stewardship']['target']:.2f}%"
                )
            
            if compliant:
                recommendations.append("✅ Distribution is compliant - no action needed")
            
            # Update tracking
            self._last_compliance_check = datetime.now()
            self._compliance_check_count += 1
            
            result = {
                'compliant': compliant,
                'administration_compliant': admin_compliant,
                'stewardship_compliant': steward_compliant,
                'general_compliant': general_compliant,
                'deviations': {
                    'administration': float(admin_deviation),
                    'stewardship': float(steward_deviation)
                },
                'recommendations': recommendations,
                'distribution': distribution,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            status_icon = "✅" if compliant else "❌"
            self.logger.info(
                f"{status_icon} Compliance Check: "
                f"Admin={admin_compliant}, Steward={steward_compliant}, Overall={compliant}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking compliance: {e}", exc_info=True)
            self._error_count += 1
            return {
                'compliant': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def is_rebalance_needed(self) -> bool:
        """
        Check if rebalancing is needed based on threshold.
        
        Simple boolean check for whether distribution exceeds compliance threshold.
        
        Returns:
            True if any deviation exceeds rebalance_threshold (2%)
            
        Example:
            >>> needs_rebalance = await service.is_rebalance_needed()
            >>> if needs_rebalance:
            ...     print("⚠️ Rebalancing required")
            ...     compliance = await service.check_compliance()
            ...     # Take action based on recommendations
        
        Design Notes:
            - Principle 5: Fully async operation
            - Simple boolean check for quick decisions
        """
        self._require_initialized()
        
        try:
            compliance = await self.check_compliance()
            needs_rebalance = not compliance.get('compliant', False)
            
            if needs_rebalance:
                self.logger.warning("⚠️ Rebalancing needed")
            else:
                self.logger.info("✅ No rebalancing needed")
            
            return needs_rebalance
            
        except Exception as e:
            self.logger.error(f"Error checking rebalance status: {e}", exc_info=True)
            self._error_count += 1
            # Conservative approach: assume rebalance needed on error
            return True
    
    # ========================================================================
    # STANDARDIZED HEALTH CHECK METHOD
    # Principle 7: Per-Asset Monitoring with health checks
    # Principle 12: Method Singularity - Uses ServiceHealthCheck utility
    # ========================================================================
    # DISTRIBUTION STATE PERSISTENCE
    # Principle #4: Database as single source of truth
    # Principle #5: Strict async operations
    # Principle #12: Method singularity - single update point for distribution_state
    # ========================================================================
    
    async def update_distribution_state(
        self, 
        token_code: str = 'UBEC',
        include_all_tokens: bool = True
    ) -> Dict[str, Any]:
        """
        Update distribution_state table with current calculated distribution.
        
        This method synchronizes the distribution_state table with live blockchain
        data, ensuring the API and dashboard show accurate distribution percentages.
        Called by the scheduler every 15 minutes.
        
        The distribution_state table is updated with the 65/30/5 model:
        - general_distribution: 65% target (DERIVED: 100% - Admin - Stewardship)
        - token_ecosystem_stewardship: 30% target
        - administration: 5% target
        
        Args:
            token_code: Primary token to update (default: 'UBEC')
            include_all_tokens: If True, also update UBECrc, UBECgpi, UBECtt
            
        Returns:
            Dict with update results:
            {
                'success': bool,
                'token_code': str,
                'updated_categories': List[str],
                'distribution': Dict with current percentages,
                'timestamp': str ISO format
            }
            
        Raises:
            RuntimeError: If service not initialized
            
        Example:
            >>> result = await distribution_service.update_distribution_state()
            >>> print(f"Updated: {result['updated_categories']}")
        """
        self._require_initialized()
        
        try:
            self.logger.info(f"Updating distribution_state for {token_code}...")
            
            # Get current live distribution
            distribution = await self.get_current_distribution()
            
            if not distribution.get('total_supply'):
                self.logger.warning("No distribution data available")
                return {
                    'success': False,
                    'error': 'No distribution data available',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Prepare upsert query for distribution_state
            # This handles both INSERT (if row doesn't exist) and UPDATE (if it does)
            upsert_query = f"""
                INSERT INTO {self.db_schema}.distribution_state (
                    asset_code, 
                    category, 
                    target_percentage, 
                    actual_percentage,
                    current_amount, 
                    target_amount,
                    deviation, 
                    compliance_status, 
                    last_updated
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                ON CONFLICT (asset_code, category) 
                DO UPDATE SET
                    actual_percentage = EXCLUDED.actual_percentage,
                    current_amount = EXCLUDED.current_amount,
                    target_amount = EXCLUDED.target_amount,
                    deviation = EXCLUDED.deviation,
                    compliance_status = EXCLUDED.compliance_status,
                    last_updated = NOW()
            """
            
            total_supply = Decimal(str(distribution.get('total_supply', 0)))
            updated_categories = []
            
            # ----------------------------------------------------------------
            # Update General Distribution (65% target - DERIVED)
            # ----------------------------------------------------------------
            general_pct = float(distribution.get('general_percentage', 0))
            general_amount = distribution.get('general_amount', Decimal('0'))
            general_target = total_supply * Decimal('0.65')
            general_deviation = abs(65.0 - general_pct)
            general_status = self._get_compliance_status(general_deviation)
            
            await self.db_manager.execute(upsert_query, (
                token_code,
                'general_distribution',
                65.0,
                general_pct,
                str(general_amount),
                str(general_target),
                general_deviation,
                general_status
            ))
            updated_categories.append('general_distribution')
            
            # ----------------------------------------------------------------
            # Update Token Ecosystem Stewardship (30% target)
            # ----------------------------------------------------------------
            steward_pct = float(distribution.get('stewardship_percentage', 0))
            steward_amount = distribution.get('stewardship_amount', Decimal('0'))
            steward_target = total_supply * Decimal('0.30')
            steward_deviation = abs(30.0 - steward_pct)
            steward_status = self._get_compliance_status(steward_deviation)
            
            await self.db_manager.execute(upsert_query, (
                token_code,
                'token_ecosystem_stewardship',
                30.0,
                steward_pct,
                str(steward_amount),
                str(steward_target),
                steward_deviation,
                steward_status
            ))
            updated_categories.append('token_ecosystem_stewardship')
            
            # ----------------------------------------------------------------
            # Update Administration (5% target)
            # ----------------------------------------------------------------
            admin_pct = float(distribution.get('admin_percentage', 0))
            admin_amount = distribution.get('admin_amount', Decimal('0'))
            admin_target = total_supply * Decimal('0.05')
            admin_deviation = abs(5.0 - admin_pct)
            admin_status = self._get_compliance_status(admin_deviation)
            
            await self.db_manager.execute(upsert_query, (
                token_code,
                'administration',
                5.0,
                admin_pct,
                str(admin_amount),
                str(admin_target),
                admin_deviation,
                admin_status
            ))
            updated_categories.append('administration')
            
            # Log success
            self.logger.info(
                f"✅ Distribution state updated for {token_code}: "
                f"General={general_pct:.2f}% ({general_status}), "
                f"Stewardship={steward_pct:.2f}% ({steward_status}), "
                f"Admin={admin_pct:.2f}% ({admin_status})"
            )
            
            # Update internal tracking
            self._last_state_update = datetime.now(timezone.utc)
            self._state_update_count = getattr(self, '_state_update_count', 0) + 1
            
            return {
                'success': True,
                'token_code': token_code,
                'updated_categories': updated_categories,
                'distribution': {
                    'general_percentage': general_pct,
                    'stewardship_percentage': steward_pct,
                    'admin_percentage': admin_pct,
                    'total_supply': str(total_supply)
                },
                'compliance': {
                    'general': general_status,
                    'stewardship': steward_status,
                    'admin': admin_status
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self._error_count = getattr(self, '_error_count', 0) + 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error updating distribution state: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _get_compliance_status(self, deviation: float) -> str:
        """
        Determine compliance status based on deviation from target.
        
        Args:
            deviation: Absolute deviation percentage from target
            
        Returns:
            'compliant' (green), 'warning' (yellow), or 'violation' (red)
        """
        if deviation < 2.0:
            return 'compliant'      # Green zone: < 2% deviation
        elif deviation < 5.0:
            return 'warning'        # Yellow zone: 2-5% deviation
        else:
            return 'violation'      # Red zone: > 5% deviation


    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check using standardized utility.
        
        Implements Principle #7 (Per-Asset Monitoring) and Principle #12 
        (Method Singularity) by using the ServiceHealthCheck utility.
        
        Returns:
            Dict with health status:
            {
                'service': str,
                'status': str ('healthy', 'degraded', 'unhealthy'),
                'message': str,
                'timestamp': str,
                'details': {
                    'initialized': bool,
                    'database': str,
                    'stellar': str,
                    'config': str,
                    ...additional distribution-specific details
                }
            }
        
        Example:
            >>> health = await service.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Database: {health['details']['database']}")
            >>> print(f"Last check: {health['details']['last_distribution_check']}")
        
        Design Notes:
            - Principle 7: Per-Asset Monitoring
            - Principle 12: Uses ServiceHealthCheck utility for consistency
        """
        async def check_stellar():
            """Verify Stellar connectivity."""
            try:
                if self.stellar_client and self.accounts.get('general'):
                    # Try to fetch account from Stellar
                    account = await self.stellar_client.accounts().account_id(
                        self.accounts['general']
                    ).call()
                    return account is not None
                else:
                    # Can't test without initialized accounts
                    return False
            except Exception:
                return False
        
        async def check_config():
            """Validate service configuration."""
            try:
                self._validate_config()
                return True
            except ValueError:
                return False
        
        async def check_signer():
            """Check secure signer service availability."""
            try:
                self._signer_available = await self.signer_client.is_available()
                return self._signer_available
            except Exception:
                self._signer_available = False
                return False
        
        # Get signer status for details
        signer_status = None
        try:
            if self._signer_available:
                signer_status = await self.signer_client.get_status()
        except Exception:
            pass
        
        # Prepare distribution-specific details
        distribution_details = {
            'last_distribution_check': self._last_distribution_check.isoformat() if self._last_distribution_check else None,
            'last_compliance_check': self._last_compliance_check.isoformat() if self._last_compliance_check else None,
            'distribution_checks': self._distribution_check_count,
            'compliance_checks': self._compliance_check_count,
            'error_count': self._error_count,
            'signing_requests': self._signing_requests,
            'signing_failures': self._signing_failures,
            'signer_available': self._signer_available,
            'signer_accounts': signer_status.get('accounts', 0) if signer_status else 0,
            'signer_limits': signer_status.get('limits', {}) if signer_status else {},
            'cache_status': 'fresh' if self._is_cache_fresh() else 'stale',
            'cache_size': len(self._cache),
            'ubec_code': self.ubec_code,
            'ubec_issuer': f"{self.ubec_issuer[:8]}..." if self.ubec_issuer else None,
            'network': self.network
        }
        
        # Use ServiceHealthCheck utility for database and Stellar health
        # This follows Principle #12: Method Singularity
        health = await ServiceHealthCheck.database_dependent_health(
            service_name='distribution',
            db_manager=self.db_manager,
            is_initialized=self._initialized,
            additional_checks=[check_stellar, check_config, check_signer],
            **distribution_details
        )
        
        # Add warnings for stale operations
        issues = []
        if self._last_distribution_check:
            check_age = (datetime.now() - self._last_distribution_check).total_seconds()
            if check_age > 86400:  # 24 hours
                issues.append(f"No distribution check in {check_age/3600:.1f} hours")
        
        if self._last_compliance_check:
            check_age = (datetime.now() - self._last_compliance_check).total_seconds()
            if check_age > 86400:  # 24 hours
                issues.append(f"No compliance check in {check_age/3600:.1f} hours")
        
        # Warning if signer not available (can only do dry-runs)
        if not self._signer_available:
            issues.append("Secure signer not available - live execution disabled")
        
        # Update status if there are operational warnings
        if issues and health['status'] == 'healthy':
            health['status'] = 'degraded'
            health['message'] = f"Distribution service operational with warnings: {', '.join(issues)}"
        
        return health
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.ubec_code:
            raise ValueError("ubec_code not configured")
        
        if not self.ubec_issuer:
            raise ValueError("ubec_issuer not configured")
        
        if not self.accounts.get('general'):
            raise ValueError("general account not configured")
        
        if not self.accounts.get('administration'):
            raise ValueError("administration account not configured")
        
        if not self.accounts.get('stewardship') or len(self.accounts['stewardship']) != 3:
            raise ValueError("stewardship accounts not properly configured (need 3 accounts)")
    
    def _is_cache_fresh(self) -> bool:
        """Check if cache is still fresh."""
        if not self._cache_timestamp:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_ttl


# ========================================================================
# FACTORY FUNCTION
# Principle 2: Service Pattern - Factory for service registry
# ========================================================================

async def create_distribution_service(
    db_manager: Any,
    config: Dict[str, Any],
    stellar_client: Any,
    audit_service: Any,
    rate_limit_calls_per_second: float = 5.0
) -> UBECDistributionService:
    """
    Factory function to create and initialize distribution service instance.
    
    This async factory creates the service and performs necessary async
    initialization, including loading the issuer address from the database.
    
    IMPORTANT: This function is async because initialization requires database
    queries to load configuration (Principle 4: Database is single source of truth).
    
    Args:
        db_manager: Async database manager
        config: Configuration dictionary
        stellar_client: Stellar async client
        audit_service: Audit service instance
        rate_limit_calls_per_second: Rate limit for API calls
    
    Returns:
        UBECDistributionService: Fully initialized service with complete LP tracking
    
    Example:
        >>> # In main.py or service registry
        >>> service = await create_distribution_service(
        ...     db_manager=db,
        ...     config=config,
        ...     stellar_client=client,
        ...     audit_service=audit
        ... )
        >>> # Service is ready to use
        >>> distribution = await service.get_current_distribution()
        >>> compliance = await service.check_compliance()
        >>> health = await service.health_check()
    
    Design Notes:
        - Principle 2: Service pattern with async factory function
        - Principle 3: Dependencies injected via service registry
        - Principle 4: Database-driven initialization
        - Principle 5: Fully async operation
    """
    # Create service instance
    service = UBECDistributionService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        audit_service=audit_service,
        rate_limit_calls_per_second=rate_limit_calls_per_second
    )
    
    # Perform async initialization (loads issuer from database if needed)
    # Service registry handles initialization
    return service


# ========================================================================
# PUBLIC INTERFACE
# Principle 1: Modular Design - Clear public interface
# ========================================================================

__all__ = [
    'UBECDistributionService',
    'create_distribution_service',
    'SignerClient',
    'SecurityError',
    'OFFICIAL_TOKENOMICS',
    'OFFICIAL_ACCOUNTS',
    'LIQUIDITY_ACCOUNT'
]


# ========================================================================
# STANDALONE EXECUTION PREVENTION
# Principle 2: Service Pattern - No standalone execution
# ========================================================================

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from services.distribution.ubec_distribution_service import create_distribution_service\n"
        "  service = await create_distribution_service(db_manager, config, stellar_client, audit)\n"
        "  distribution = await service.get_current_distribution()\n"
        "  compliance = await service.check_compliance()\n"
        "  health = await service.health_check()\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
