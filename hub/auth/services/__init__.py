"""
Module: auth/services/__init__.py
Service: hub (iot.ubec.network)
Purpose: AuthService and PermissionService — core authentication logic.
         Adapted from old repo: user→steward, sync→async, pyjwt v2,
         passlib bcrypt, new schema column names.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
import jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import (
    Permission, Role, RolePermission, Steward,
    StewardRole, StewardSession,
)
from auth.schemas import LoginRequest, StewardCreate
from config import settings

logger = logging.getLogger(__name__)

# ── Config — read from pydantic settings, never raw os.environ ───────────────

SECRET_KEY                  = settings.SECRET_KEY
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS   = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# ── AuthService ───────────────────────────────────────────────────────────────

class AuthService:

    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS   = REFRESH_TOKEN_EXPIRE_DAYS

    # ── Password ──────────────────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            return False

    # ── Tokens ────────────────────────────────────────────────────────────────

    @staticmethod
    def create_access_token(
        steward_id: UUID,
        roles: list[str],
        permissions: list[str],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        now    = datetime.now(timezone.utc)
        expire = now + expires_delta
        payload = {
            "sub":         str(steward_id),
            "roles":       roles,
            "permissions": permissions,
            "exp":         expire,
            "iat":         now,
            "type":        "access",
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(
        steward_id: UUID,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        now    = datetime.now(timezone.utc)
        expire = now + expires_delta
        payload = {
            "sub":  str(steward_id),
            "exp":  expire,
            "iat":  now,
            "type": "refresh",
            "jti":  secrets.token_hex(16),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def hash_token(token: str) -> str:
        """SHA-256 of a token — stored in steward_sessions.token_hash."""
        return hashlib.sha256(token.encode()).hexdigest()

    # ── Steward operations ────────────────────────────────────────────────────

    @classmethod
    async def create_steward(
        cls,
        db: AsyncSession,
        data: StewardCreate,
    ) -> Steward:
        """
        Register a new steward account.
        Assigns the default 'member' role.
        Raises ValueError if email already registered.
        """
        # Check uniqueness
        existing = await db.execute(
            select(Steward).where(Steward.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        now = datetime.now(timezone.utc)
        steward = Steward(
            email               = data.email,
            password_hash       = cls.hash_password(data.password),
            full_name           = data.full_name,
            display_name        = data.display_name,
            preferred_language  = data.preferred_language,
            gdpr_consent_given  = True,
            gdpr_consent_at     = now,
            verification_token  = secrets.token_urlsafe(32),
        )
        db.add(steward)
        await db.flush()  # populate steward.id

        # Assign default 'member' role
        member_role = (await db.execute(
            select(Role).where(Role.name == "member")
        )).scalar_one_or_none()
        if member_role:
            db.add(StewardRole(steward_id=steward.id, role_id=member_role.id))

        await db.commit()
        # Reload with relationships so role_names is available outside the session
        result = await db.execute(
            select(Steward)
            .where(Steward.id == steward.id)
            .options(selectinload(Steward.roles).selectinload(StewardRole.role))
        )
        return result.scalar_one()

    @classmethod
    async def authenticate(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[Steward]:
        """Return Steward if credentials are valid, None otherwise."""
        result = await db.execute(
            select(Steward)
            .where(Steward.email == email)
            .options(selectinload(Steward.roles).selectinload(StewardRole.role))
        )
        steward = result.scalar_one_or_none()
        if not steward or not steward.is_active:
            return None
        if not cls.verify_password(password, steward.password_hash):
            return None
        return steward

    @classmethod
    async def get_steward_permissions(
        cls,
        db: AsyncSession,
        steward: Steward,
    ) -> list[str]:
        """Return all permission names for a steward via their roles."""
        permissions: set[str] = set()
        for sr in steward.roles:
            role = sr.role
            if not role:
                continue
            result = await db.execute(
                select(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id == role.id)
            )
            for perm in result.scalars():
                permissions.add(perm.name)
        return list(permissions)

    @classmethod
    async def login(
        cls,
        db: AsyncSession,
        login_data: LoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[tuple[str, str, Steward]]:
        """
        Authenticate and create a session.
        Returns (access_token, refresh_token, steward) or None.
        """
        steward = await cls.authenticate(db, login_data.email, login_data.password)
        if not steward:
            return None

        roles       = steward.role_names
        permissions = await cls.get_steward_permissions(db, steward)

        if login_data.remember_me:
            access_expires  = timedelta(hours=24)
            refresh_expires = timedelta(days=30)
        else:
            access_expires  = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        access_token  = cls.create_access_token(steward.id, roles, permissions, access_expires)
        refresh_token = cls.create_refresh_token(steward.id, refresh_expires)

        session = StewardSession(
            steward_id  = steward.id,
            token_hash  = cls.hash_token(access_token),
            user_agent  = user_agent[:500] if user_agent else None,
            # ip_address only stored when GDPR consent is confirmed
            ip_address  = ip_address if steward.gdpr_consent_given else None,
            expires_at  = datetime.now(timezone.utc) + refresh_expires,
        )
        db.add(session)
        await db.commit()

        return access_token, refresh_token, steward

    @classmethod
    async def logout(cls, db: AsyncSession, access_token: str) -> bool:
        """Revoke the session associated with this access token."""
        token_hash = cls.hash_token(access_token)
        result = await db.execute(
            select(StewardSession).where(StewardSession.token_hash == token_hash)
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_revoked = True
            await db.commit()
            return True
        return False

    @classmethod
    async def revoke_all_sessions(cls, db: AsyncSession, steward_id: UUID) -> int:
        """Revoke all active sessions for a steward. Returns count."""
        result = await db.execute(
            select(StewardSession).where(
                StewardSession.steward_id == steward_id,
                StewardSession.is_revoked.is_(False),
            )
        )
        sessions = result.scalars().all()
        for s in sessions:
            s.is_revoked = True
        await db.commit()
        return len(sessions)

    # ── Password reset ────────────────────────────────────────────────────────

    @classmethod
    async def create_password_reset_token(
        cls, db: AsyncSession, email: str
    ) -> Optional[str]:
        result = await db.execute(select(Steward).where(Steward.email == email))
        steward = result.scalar_one_or_none()
        if not steward:
            return None
        token = secrets.token_urlsafe(32)
        steward.reset_token         = token
        steward.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        await db.commit()
        return token

    @classmethod
    async def reset_password(
        cls, db: AsyncSession, token: str, new_password: str
    ) -> bool:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Steward).where(
                Steward.reset_token == token,
                Steward.reset_token_expires > now,
            )
        )
        steward = result.scalar_one_or_none()
        if not steward:
            return False
        steward.password_hash       = cls.hash_password(new_password)
        steward.reset_token         = None
        steward.reset_token_expires = None
        await db.commit()
        await cls.revoke_all_sessions(db, steward.id)
        return True

    # ── Email verification ────────────────────────────────────────────────────

    @classmethod
    async def verify_email(cls, db: AsyncSession, token: str) -> bool:
        result = await db.execute(
            select(Steward).where(
                Steward.verification_token == token,
                Steward.email_verified.is_(False),
            )
        )
        steward = result.scalar_one_or_none()
        if not steward:
            return False
        steward.email_verified      = True
        steward.verification_token  = None
        await db.commit()
        return True


# ── PermissionService ─────────────────────────────────────────────────────────

class PermissionService:

    @staticmethod
    def has_permission(permissions: list[str], required: str) -> bool:
        return required in permissions

    @staticmethod
    def has_any_permission(permissions: list[str], required: list[str]) -> bool:
        return any(p in permissions for p in required)

    @staticmethod
    def has_role(roles: list[str], required: str) -> bool:
        return required in roles

    @staticmethod
    async def get_all_roles(db: AsyncSession) -> list[Role]:
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
            .order_by(Role.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_permissions(db: AsyncSession) -> list[Permission]:
        result = await db.execute(select(Permission).order_by(Permission.category, Permission.name))
        return list(result.scalars().all())

    @staticmethod
    async def assign_role(
        db: AsyncSession,
        steward_id: UUID,
        role_name: str,
        granted_by: Optional[UUID] = None,
    ) -> bool:
        role = (await db.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
        if not role:
            return False
        existing = (await db.execute(
            select(StewardRole).where(
                StewardRole.steward_id == steward_id,
                StewardRole.role_id    == role.id,
            )
        )).scalar_one_or_none()
        if existing:
            return False
        db.add(StewardRole(steward_id=steward_id, role_id=role.id, granted_by=granted_by))
        await db.commit()
        return True

    @staticmethod
    async def remove_role(
        db: AsyncSession,
        steward_id: UUID,
        role_name: str,
    ) -> bool:
        role = (await db.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
        if not role:
            return False
        assignment = (await db.execute(
            select(StewardRole).where(
                StewardRole.steward_id == steward_id,
                StewardRole.role_id    == role.id,
            )
        )).scalar_one_or_none()
        if not assignment:
            return False
        await db.delete(assignment)
        await db.commit()
        return True
