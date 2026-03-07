"""
Module: auth/dependencies.py
Service: hub (iot.ubec.network)
Purpose: FastAPI dependency injection for authentication and authorisation.
         Adapted from old repo: user→steward, sync→async.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.database import get_db
from auth.models import Steward, StewardRole
from auth.services import AuthService, PermissionService

security = HTTPBearer(auto_error=False)


# ── Token data ────────────────────────────────────────────────────────────────

class TokenData:
    def __init__(self, steward_id: str, roles: list[str], permissions: list[str]):
        self.steward_id = steward_id
        self.roles      = roles
        self.permissions = permissions


# ── CurrentSteward ────────────────────────────────────────────────────────────

class CurrentSteward:
    """
    Wraps the authenticated steward with token-derived roles and permissions.
    Available as a FastAPI dependency in any route.
    """
    def __init__(self, steward: Steward, token_data: TokenData):
        self.steward     = steward
        self.id          = steward.id
        self.email       = steward.email
        self.display_name = steward.display_name
        self.roles       = token_data.roles
        self.permissions = token_data.permissions

    def has_permission(self, permission: str) -> bool:
        return PermissionService.has_permission(self.permissions, permission)

    def has_any_permission(self, permissions: list[str]) -> bool:
        return PermissionService.has_any_permission(self.permissions, permissions)

    def has_role(self, role: str) -> bool:
        return PermissionService.has_role(self.roles, role)


# ── Token extraction ──────────────────────────────────────────────────────────

async def get_token_data(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenData]:
    if not credentials:
        return None
    payload = AuthService.decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        return None
    return TokenData(
        steward_id  = payload["sub"],
        roles       = payload.get("roles", []),
        permissions = payload.get("permissions", []),
    )


# ── Steward dependencies ──────────────────────────────────────────────────────

async def get_current_steward_optional(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: AsyncSession = Depends(get_db),
) -> Optional[CurrentSteward]:
    """Return CurrentSteward if authenticated, None if not. For public/optional routes."""
    if not token_data:
        return None
    result = await db.execute(
        select(Steward)
        .where(Steward.id == token_data.steward_id)
        .options(selectinload(Steward.roles).selectinload(StewardRole.role))
    )
    steward = result.scalar_one_or_none()
    if not steward or not steward.is_active:
        return None
    return CurrentSteward(steward, token_data)


async def get_current_steward(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: AsyncSession = Depends(get_db),
) -> CurrentSteward:
    """Return CurrentSteward or raise 401. For protected routes."""
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(
        select(Steward)
        .where(Steward.id == token_data.steward_id)
        .options(selectinload(Steward.roles).selectinload(StewardRole.role))
    )
    steward = result.scalar_one_or_none()
    if not steward:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Steward not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not steward.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Steward account is disabled",
        )
    return CurrentSteward(steward, token_data)


async def get_current_verified_steward(
    current: CurrentSteward = Depends(get_current_steward),
) -> CurrentSteward:
    """Require verified email. Use for endpoints that need confirmed identity."""
    if not current.steward.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not yet verified",
        )
    return current


# ── Permission / role dependency factories ────────────────────────────────────

def require_permission(permission: str):
    """
    Dependency factory: require a specific permission.

    Usage:
        @router.get("/data", dependencies=[Depends(require_permission("observations:create"))])
    """
    async def checker(current: CurrentSteward = Depends(get_current_steward)) -> CurrentSteward:
        if not current.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return current
    return checker


def require_any_permission(permissions: list[str]):
    async def checker(current: CurrentSteward = Depends(get_current_steward)) -> CurrentSteward:
        if not current.has_any_permission(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {permissions}",
            )
        return current
    return checker


def require_role(role: str):
    """
    Dependency factory: require a specific role.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    async def checker(current: CurrentSteward = Depends(get_current_steward)) -> CurrentSteward:
        if not current.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}",
            )
        return current
    return checker


def require_any_role(roles: list[str]):
    async def checker(current: CurrentSteward = Depends(get_current_steward)) -> CurrentSteward:
        if not any(current.has_role(r) for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {roles}",
            )
        return current
    return checker
