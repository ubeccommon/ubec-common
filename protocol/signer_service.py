#!/usr/bin/env python3
# /opt/wampum-signer/signer_service.py
"""
UBEC Encrypted Key Signing Service
===================================

Isolated service for signing Stellar transactions.
Keys are encrypted at rest and only decrypted in memory when needed.

Security Features:
- Runs as dedicated unprivileged user
- Keys encrypted with Fernet (AES-128-CBC)
- Master key derived from password via PBKDF2
- Transaction limits enforced
- All operations logged
- Unix socket communication only (no network)

WARNING: This is NOT a hardware enclave. For production with
significant value, use AWS Nitro Enclaves or Intel SGX.
"""

import asyncio
import json
import logging
import os
import sys
import hashlib
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
from decimal import Decimal
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

# Cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Stellar SDK
from stellar_sdk import Keypair, TransactionEnvelope, Network

# Configuration
SOCKET_PATH = "/var/run/wampum-signer/signer.sock"
KEYS_FILE = "/var/lib/wampum-signer/encrypted_keys.json"
LOG_FILE = "/var/log/wampum-signer/signer.log"
LIMITS_FILE = "/var/lib/wampum-signer/limits.json"

# Limits (configurable via limits.json)
DEFAULT_MAX_PER_TRANSACTION = Decimal("10000")  # 10,000 tokens
DEFAULT_MAX_DAILY = Decimal("50000")  # 50,000 tokens/day
DEFAULT_MAX_HOURLY = Decimal("20000")  # 20,000 tokens/hour

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SigningRequest:
    """Request to sign a transaction."""
    transaction_xdr: str
    source_account: str
    network: str  # 'PUBLIC' or 'TESTNET'
    request_id: str
    timestamp: str


@dataclass
class SigningResponse:
    """Response from signing service."""
    success: bool
    request_id: str
    signed_xdr: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class TransactionLimiter:
    """Enforces transaction limits."""
    
    def __init__(self, limits_file: str):
        self.limits_file = limits_file
        self.daily_totals: Dict[str, Decimal] = {}
        self.hourly_totals: Dict[str, Decimal] = {}
        self.last_reset_daily = datetime.now(timezone.utc).date()
        self.last_reset_hourly = datetime.now(timezone.utc).hour
        self._load_limits()
    
    def _load_limits(self):
        """Load limits from config file."""
        if os.path.exists(self.limits_file):
            with open(self.limits_file, 'r') as f:
                config = json.load(f)
                self.max_per_tx = Decimal(str(config.get('max_per_transaction', DEFAULT_MAX_PER_TRANSACTION)))
                self.max_daily = Decimal(str(config.get('max_daily', DEFAULT_MAX_DAILY)))
                self.max_hourly = Decimal(str(config.get('max_hourly', DEFAULT_MAX_HOURLY)))
        else:
            self.max_per_tx = DEFAULT_MAX_PER_TRANSACTION
            self.max_daily = DEFAULT_MAX_DAILY
            self.max_hourly = DEFAULT_MAX_HOURLY
            # Create default limits file
            self._save_default_limits()
    
    def _save_default_limits(self):
        """Save default limits to file."""
        config = {
            'max_per_transaction': str(self.max_per_tx),
            'max_daily': str(self.max_daily),
            'max_hourly': str(self.max_hourly),
            'updated': datetime.now(timezone.utc).isoformat()
        }
        with open(self.limits_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _reset_if_needed(self):
        """Reset counters if time period has elapsed."""
        now = datetime.now(timezone.utc)
        
        # Daily reset
        if now.date() != self.last_reset_daily:
            logger.info(f"Daily limit reset. Previous totals: {self.daily_totals}")
            self.daily_totals = {}
            self.last_reset_daily = now.date()
        
        # Hourly reset
        if now.hour != self.last_reset_hourly:
            logger.info(f"Hourly limit reset. Previous totals: {self.hourly_totals}")
            self.hourly_totals = {}
            self.last_reset_hourly = now.hour
    
    def check_and_record(self, account: str, amount: Decimal) -> tuple[bool, str]:
        """
        Check if transaction is within limits and record it.
        
        Returns (allowed, reason)
        """
        self._reset_if_needed()
        
        # Check per-transaction limit
        if amount > self.max_per_tx:
            return False, f"Amount {amount} exceeds per-transaction limit {self.max_per_tx}"
        
        # Check hourly limit
        current_hourly = self.hourly_totals.get(account, Decimal("0"))
        if current_hourly + amount > self.max_hourly:
            return False, f"Would exceed hourly limit: {current_hourly + amount} > {self.max_hourly}"
        
        # Check daily limit
        current_daily = self.daily_totals.get(account, Decimal("0"))
        if current_daily + amount > self.max_daily:
            return False, f"Would exceed daily limit: {current_daily + amount} > {self.max_daily}"
        
        # Record the transaction
        self.hourly_totals[account] = current_hourly + amount
        self.daily_totals[account] = current_daily + amount
        
        logger.info(f"Transaction recorded: account={account}, amount={amount}, "
                   f"hourly_total={self.hourly_totals[account]}, daily_total={self.daily_totals[account]}")
        
        return True, "OK"


class EncryptedKeyManager:
    """Manages encrypted Stellar keys."""
    
    def __init__(self, keys_file: str, master_password: str):
        self.keys_file = keys_file
        self._fernet = self._derive_fernet(master_password)
        self._keys: Dict[str, str] = {}  # account_id -> secret_key (decrypted)
        self._load_keys()
    
    def _derive_fernet(self, password: str) -> Fernet:
        """Derive Fernet encryption key from password."""
        # Use fixed salt (in production, store salt with encrypted data)
        salt = b'wampum_signer_salt_v1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _load_keys(self):
        """Load and decrypt keys from file."""
        if not os.path.exists(self.keys_file):
            logger.warning(f"Keys file not found: {self.keys_file}")
            return
        
        with open(self.keys_file, 'r') as f:
            encrypted_data = json.load(f)
        
        for account_id, encrypted_key in encrypted_data.get('keys', {}).items():
            try:
                decrypted = self._fernet.decrypt(encrypted_key.encode()).decode()
                # Validate it's a valid Stellar secret key
                keypair = Keypair.from_secret(decrypted)
                if keypair.public_key == account_id:
                    self._keys[account_id] = decrypted
                    logger.info(f"Loaded key for account: {account_id[:8]}...{account_id[-4:]}")
                else:
                    logger.error(f"Key mismatch for account {account_id}")
            except Exception as e:
                logger.error(f"Failed to decrypt key for {account_id}: {e}")
    
    def add_key(self, secret_key: str) -> str:
        """Add a new key (encrypts and saves)."""
        keypair = Keypair.from_secret(secret_key)
        account_id = keypair.public_key
        
        # Store decrypted in memory
        self._keys[account_id] = secret_key
        
        # Save encrypted to file
        self._save_keys()
        
        logger.info(f"Added key for account: {account_id[:8]}...{account_id[-4:]}")
        return account_id
    
    def _save_keys(self):
        """Save encrypted keys to file."""
        encrypted_data = {
            'keys': {},
            'updated': datetime.now(timezone.utc).isoformat(),
            'version': '1.0'
        }
        
        for account_id, secret_key in self._keys.items():
            encrypted_key = self._fernet.encrypt(secret_key.encode()).decode()
            encrypted_data['keys'][account_id] = encrypted_key
        
        with open(self.keys_file, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        
        # Secure file permissions
        os.chmod(self.keys_file, 0o600)
    
    def get_keypair(self, account_id: str) -> Optional[Keypair]:
        """Get keypair for account (returns None if not found)."""
        secret = self._keys.get(account_id)
        if secret:
            return Keypair.from_secret(secret)
        return None
    
    def has_key(self, account_id: str) -> bool:
        """Check if we have a key for this account."""
        return account_id in self._keys
    
    @property
    def accounts(self) -> list:
        """List of account IDs we have keys for."""
        return list(self._keys.keys())


class SigningService:
    """Main signing service."""
    
    def __init__(self, master_password: str):
        self.key_manager = EncryptedKeyManager(KEYS_FILE, master_password)
        self.limiter = TransactionLimiter(LIMITS_FILE)
        logger.info(f"Signing service initialized with {len(self.key_manager.accounts)} keys")
    
    def _extract_amount(self, tx_envelope: TransactionEnvelope) -> Decimal:
        """Extract total amount from transaction operations."""
        total = Decimal("0")
        tx = tx_envelope.transaction
        
        for op in tx.operations:
            # Check for payment operations
            if hasattr(op, 'amount'):
                total += Decimal(str(op.amount))
        
        return total
    
    async def sign_transaction(self, request: SigningRequest) -> SigningResponse:
        """Sign a transaction."""
        logger.info(f"Sign request: id={request.request_id}, account={request.source_account[:8]}...")
        
        try:
            # Check if we have the key
            if not self.key_manager.has_key(request.source_account):
                logger.warning(f"No key for account: {request.source_account}")
                return SigningResponse(
                    success=False,
                    request_id=request.request_id,
                    error=f"No key available for account {request.source_account[:8]}..."
                )
            
            # Parse transaction
            network_passphrase = (
                Network.PUBLIC_NETWORK_PASSPHRASE 
                if request.network == 'PUBLIC' 
                else Network.TESTNET_NETWORK_PASSPHRASE
            )
            tx_envelope = TransactionEnvelope.from_xdr(request.transaction_xdr, network_passphrase)
            
            # Extract amount and check limits
            amount = self._extract_amount(tx_envelope)
            allowed, reason = self.limiter.check_and_record(request.source_account, amount)
            
            if not allowed:
                logger.warning(f"Transaction blocked by limits: {reason}")
                return SigningResponse(
                    success=False,
                    request_id=request.request_id,
                    error=f"Limit exceeded: {reason}"
                )
            
            # Sign the transaction
            keypair = self.key_manager.get_keypair(request.source_account)
            tx_envelope.sign(keypair)
            
            signed_xdr = tx_envelope.to_xdr()
            
            logger.info(f"Transaction signed: id={request.request_id}, amount={amount}")
            
            return SigningResponse(
                success=True,
                request_id=request.request_id,
                signed_xdr=signed_xdr
            )
            
        except Exception as e:
            logger.error(f"Signing failed: {e}", exc_info=True)
            return SigningResponse(
                success=False,
                request_id=request.request_id,
                error=str(e)
            )


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, service: SigningService):
    """Handle a client connection."""
    try:
        # Read request
        data = await reader.read(65536)  # 64KB max
        if not data:
            return
        
        request_data = json.loads(data.decode())
        
        # Handle different commands
        command = request_data.get('command', 'sign')
        
        if command == 'sign':
            request = SigningRequest(**request_data['request'])
            response = await service.sign_transaction(request)
            response_data = asdict(response)
        
        elif command == 'status':
            response_data = {
                'success': True,
                'accounts': len(service.key_manager.accounts),
                'accounts_list': [f"{a[:8]}...{a[-4:]}" for a in service.key_manager.accounts],
                'limits': {
                    'max_per_transaction': str(service.limiter.max_per_tx),
                    'max_daily': str(service.limiter.max_daily),
                    'max_hourly': str(service.limiter.max_hourly)
                }
            }
        
        elif command == 'add_key':
            # Add a new key (requires the secret key)
            secret_key = request_data.get('secret_key')
            if secret_key:
                account_id = service.key_manager.add_key(secret_key)
                response_data = {'success': True, 'account_id': account_id}
            else:
                response_data = {'success': False, 'error': 'No secret_key provided'}
        
        else:
            response_data = {'success': False, 'error': f'Unknown command: {command}'}
        
        # Send response
        writer.write(json.dumps(response_data).encode())
        await writer.drain()
        
    except Exception as e:
        logger.error(f"Client handler error: {e}", exc_info=True)
        try:
            error_response = {'success': False, 'error': str(e)}
            writer.write(json.dumps(error_response).encode())
            await writer.drain()
        except:
            pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    """Main entry point."""
    # Get master password from environment or prompt
    master_password = os.environ.get('WAMPUM_SIGNER_PASSWORD')
    if not master_password:
        import getpass
        master_password = getpass.getpass("Enter master password: ")
    
    if not master_password:
        logger.error("Master password required")
        sys.exit(1)
    
    # Create socket directory
    socket_dir = os.path.dirname(SOCKET_PATH)
    os.makedirs(socket_dir, exist_ok=True)
    
    # Remove existing socket
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    
    # Initialize service
    service = SigningService(master_password)
    
    # Clear password from memory (best effort)
    master_password = None
    
    # Start Unix socket server
    server = await asyncio.start_unix_server(
        lambda r, w: handle_client(r, w, service),
        path=SOCKET_PATH
    )
    
    # Set socket permissions (only ubec user group can connect)
    os.chmod(SOCKET_PATH, 0o660)
    
    logger.info(f"Signing service started on {SOCKET_PATH}")
    
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
