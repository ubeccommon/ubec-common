#!/usr/bin/env python3
"""
UBEC Protocol - Admin Password Generator
=========================================

Utility to generate secure bcrypt password hashes for admin users.

Usage:
    python generate_admin_password.py
    python generate_admin_password.py --password "your_password"
    python generate_admin_password.py --user admin@ubec.network --password "new_password" --sql

This project uses the services of Claude and Anthropic PBC.
"""

import sys
import secrets
import string
import argparse

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


def generate_random_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if not BCRYPT_AVAILABLE:
        raise RuntimeError("bcrypt required: pip install bcrypt")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    if not BCRYPT_AVAILABLE:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Generate bcrypt password hashes')
    parser.add_argument('--password', '-p', help='Password to hash')
    parser.add_argument('--user', '-u', help='Username/email')
    parser.add_argument('--length', '-l', type=int, default=16, help='Random password length')
    parser.add_argument('--sql', action='store_true', help='Output SQL UPDATE statement')
    
    args = parser.parse_args()
    
    if not BCRYPT_AVAILABLE:
        print("\n❌ bcrypt not installed!")
        print("   pip install bcrypt --break-system-packages")
        return 1
    
    password = args.password or generate_random_password(args.length)
    password_hash = hash_password(password)
    
    print("\n" + "=" * 60)
    print("🔐 UBEC Admin Password Generator")
    print("=" * 60)
    if args.user:
        print(f"\n👤 User: {args.user}")
    print(f"\n🔑 Password: {password}")
    print(f"\n🔒 Hash: {password_hash}")
    
    email = args.user or "admin@ubec.network"
    
    if args.sql:
        print(f"\n📝 SQL:")
        print(f"""
UPDATE ubec_ui.users 
SET password_hash = '{password_hash}',
    password_changed_at = CURRENT_TIMESTAMP
WHERE email = '{email}';
""")
    
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
