"""
Module: auth/routes/__init__.py
Service: hub (iot.ubec.network)
Purpose: Authentication and authorisation API routes.
         Prefix: /api/v1/auth
         Adapted from old repo: user→steward, sync→async, pydantic v2.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.database import check_db_connection, get_db
from auth.dependencies import (
    CurrentSteward,
    get_current_steward,
    get_current_steward_optional,
    require_permission,
    require_role,
)
from auth.models import Permission, Role, RolePermission, Steward, StewardRole, StewardSession
from auth.schemas import (
    EmailVerificationRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PermissionCheckRequest,
    PermissionCheckResponse,
    PermissionResponse,
    RefreshTokenRequest,
    RoleAssignmentRequest,
    RoleResponse,
    SessionListResponse,
    SessionResponse,
    StewardCreate,
    StewardDetailResponse,
    StewardListResponse,
    StewardResponse,
    StewardUpdate,
    TokenResponse,
)
from auth.services import AuthService, PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["system"])
async def auth_health():
    db_ok = await check_db_connection()
    return {
        "status":   "healthy" if db_ok else "degraded",
        "module":   "auth",
        "version":  "1.0.0",
        "database": "connected" if db_ok else "disconnected",
    }


# ── Registration ──────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=StewardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new steward account",
)
async def register(
    data: StewardCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new steward account.

    - Assigns the default 'member' role
    - Records GDPR consent (required field)
    - Sends verification email when email service is configured
    """
    try:
        steward = await AuthService.create_steward(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Extract roles while session is still open
    roles = steward.role_names

    return StewardResponse(
        id                  = steward.id,
        email               = steward.email,
        full_name           = steward.full_name,
        display_name        = steward.display_name,
        preferred_language  = steward.preferred_language,
        is_active           = steward.is_active,
        email_verified      = steward.email_verified,
        created_at          = steward.created_at,
        roles               = roles,
    )


# ── Login / logout ────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    result = await AuthService.login(db, data, user_agent, ip_address)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, _refresh_token, steward = result
    roles = steward.role_names  # extract while session open inside login()

    return LoginResponse(
        access_token    = access_token,
        expires_in      = AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        steward         = StewardResponse(
            id                  = steward.id,
            email               = steward.email,
            full_name           = steward.full_name,
            display_name        = steward.display_name,
            preferred_language  = steward.preferred_language,
            is_active           = steward.is_active,
            email_verified      = steward.email_verified,
            created_at          = steward.created_at,
            roles               = roles,
        ),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else None
    if token:
        await AuthService.logout(db, token)
    return MessageResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    count = await AuthService.revoke_all_sessions(db, current.id)
    return MessageResponse(message=f"Logged out from {count} sessions")


# ── Password management ───────────────────────────────────────────────────────

@router.post("/password/change", response_model=MessageResponse)
async def change_password(
    data: PasswordChangeRequest,
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    if not AuthService.verify_password(data.current_password, current.steward.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current.steward.password_hash = AuthService.hash_password(data.new_password)
    await db.commit()
    await AuthService.revoke_all_sessions(db, current.id)
    return MessageResponse(message="Password changed successfully")


@router.post("/password/reset-request", response_model=MessageResponse)
async def password_reset_request(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    # Always returns success — prevents email enumeration
    await AuthService.create_password_reset_token(db, data.email)
    return MessageResponse(message="If an account exists with that email, a reset link has been sent")


@router.post("/password/reset-confirm", response_model=MessageResponse)
async def password_reset_confirm(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    success = await AuthService.reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    return MessageResponse(message="Password reset successfully")


# ── Email verification ────────────────────────────────────────────────────────

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    success = await AuthService.verify_email(db, data.token)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
    return MessageResponse(message="Email verified successfully")


# ── Own profile ───────────────────────────────────────────────────────────────

@router.get("/me", response_model=StewardDetailResponse)
async def get_my_profile(current: CurrentSteward = Depends(get_current_steward)):
    s = current.steward
    return StewardDetailResponse(
        id                  = s.id,
        email               = s.email,
        full_name           = s.full_name,
        display_name        = s.display_name,
        preferred_language  = s.preferred_language,
        is_active           = s.is_active,
        email_verified      = s.email_verified,
        created_at          = s.created_at,
        updated_at          = s.updated_at,
        stellar_public_key  = s.stellar_public_key,
        roles               = current.roles,
    )


@router.patch("/me", response_model=StewardDetailResponse)
async def update_my_profile(
    data: StewardUpdate,
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    s = current.steward
    if data.full_name           is not None: s.full_name           = data.full_name
    if data.display_name        is not None: s.display_name        = data.display_name
    if data.preferred_language  is not None: s.preferred_language  = data.preferred_language
    if data.stellar_public_key  is not None: s.stellar_public_key  = data.stellar_public_key
    await db.commit()
    await db.refresh(s)
    return StewardDetailResponse(
        id                  = s.id,
        email               = s.email,
        full_name           = s.full_name,
        display_name        = s.display_name,
        preferred_language  = s.preferred_language,
        is_active           = s.is_active,
        email_verified      = s.email_verified,
        created_at          = s.created_at,
        updated_at          = s.updated_at,
        stellar_public_key  = s.stellar_public_key,
        roles               = current.roles,
    )


@router.get("/me/permissions")
async def get_my_permissions(current: CurrentSteward = Depends(get_current_steward)):
    return {
        "steward_id":   str(current.id),
        "roles":        current.roles,
        "permissions":  current.permissions,
    }


# ── Sessions ──────────────────────────────────────────────────────────────────

@router.get("/me/sessions", response_model=SessionListResponse)
async def get_my_sessions(
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StewardSession).where(
            StewardSession.steward_id   == current.id,
            StewardSession.is_revoked.is_(False),
        ).order_by(StewardSession.last_used_at.desc())
    )
    sessions = result.scalars().all()
    return SessionListResponse(
        sessions=[
            SessionResponse(
                id          = s.id,
                user_agent  = s.user_agent,
                created_at  = s.created_at,
                last_used_at = s.last_used_at,
            )
            for s in sessions
        ],
        total=len(sessions),
    )


@router.delete("/me/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: UUID,
    current: CurrentSteward = Depends(get_current_steward),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StewardSession).where(
            StewardSession.id           == session_id,
            StewardSession.steward_id   == current.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session.is_revoked = True
    await db.commit()
    return MessageResponse(message="Session revoked")


# ── Permission check ──────────────────────────────────────────────────────────

@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
    data: PermissionCheckRequest,
    current: CurrentSteward = Depends(get_current_steward),
):
    return PermissionCheckResponse(
        permission  = data.permission,
        allowed     = current.has_permission(data.permission),
    )


# ── Admin: steward management ─────────────────────────────────────────────────

@router.get(
    "/stewards",
    response_model=StewardListResponse,
    dependencies=[Depends(require_permission("stewards:manage"))],
)
async def list_stewards(
    page:       int             = Query(1, ge=1),
    per_page:   int             = Query(20, ge=1, le=100),
    search:     Optional[str]   = None,
    db:         AsyncSession    = Depends(get_db),
):
    query = select(Steward).options(
        selectinload(Steward.roles).selectinload(StewardRole.role)
    )
    if search:
        like = f"%{search}%"
        query = query.where(
            Steward.email.ilike(like) |
            Steward.full_name.ilike(like) |
            Steward.display_name.ilike(like)
        )

    count_result = await db.execute(query)
    total        = len(count_result.scalars().all())

    paged_result = await db.execute(
        query.offset((page - 1) * per_page).limit(per_page)
    )
    stewards = paged_result.scalars().all()

    return StewardListResponse(
        stewards=[
            StewardResponse(
                id                  = s.id,
                email               = s.email,
                full_name           = s.full_name,
                display_name        = s.display_name,
                preferred_language  = s.preferred_language,
                is_active           = s.is_active,
                email_verified      = s.email_verified,
                created_at          = s.created_at,
                roles               = s.role_names,
            )
            for s in stewards
        ],
        total       = total,
        page        = page,
        per_page    = per_page,
        pages       = (total + per_page - 1) // per_page,
    )


@router.post(
    "/stewards/{steward_id}/roles",
    response_model=MessageResponse,
    dependencies=[Depends(require_permission("stewards:manage"))],
)
async def assign_role(
    steward_id: UUID,
    data:       RoleAssignmentRequest,
    current:    CurrentSteward  = Depends(get_current_steward),
    db:         AsyncSession     = Depends(get_db),
):
    success = await PermissionService.assign_role(db, steward_id, data.role_name, granted_by=current.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found or already assigned")
    return MessageResponse(message=f"Role '{data.role_name}' assigned")


@router.delete(
    "/stewards/{steward_id}/roles/{role_name}",
    response_model=MessageResponse,
    dependencies=[Depends(require_permission("stewards:manage"))],
)
async def remove_role(
    steward_id: UUID,
    role_name:  str,
    db:         AsyncSession = Depends(get_db),
):
    success = await PermissionService.remove_role(db, steward_id, role_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found or not assigned")
    return MessageResponse(message=f"Role '{role_name}' removed")


# ── Roles and permissions (informational) ─────────────────────────────────────

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    current:    Optional[CurrentSteward]    = Depends(get_current_steward_optional),
    db:         AsyncSession                = Depends(get_db),
):
    roles = await PermissionService.get_all_roles(db)
    return [
        RoleResponse(
            id              = r.id,
            name            = r.name,
            display_name    = r.display_name,
            description     = r.description,
            is_system       = r.is_system,
            created_at      = r.created_at,
            permissions     = r.permission_names if current else [],
        )
        for r in roles
    ]


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("stewards:manage"))],
)
async def list_permissions(db: AsyncSession = Depends(get_db)):
    perms = await PermissionService.get_all_permissions(db)
    return [
        PermissionResponse(
            id              = p.id,
            name            = p.name,
            display_name    = p.display_name,
            description     = p.description,
            category        = p.category,
            is_system       = p.is_system,
        )
        for p in perms
    ]
