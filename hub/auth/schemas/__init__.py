"""
Module: auth/schemas/__init__.py
Service: hub (iot.ubec.network)
Purpose: Pydantic v2 schemas for authentication and authorisation API.
         stewards (not users) throughout.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Steward schemas ───────────────────────────────────────────────────────────

class StewardBase(BaseModel):
    email:              EmailStr
    full_name:          Optional[str]   = Field(None, max_length=255)
    display_name:       Optional[str]   = Field(None, max_length=100)
    preferred_language: str             = Field("en", pattern="^(de|en|pl)$")


class StewardCreate(StewardBase):
    """Schema for registering a new steward account."""
    password:           str             = Field(..., min_length=8, max_length=128)
    gdpr_consent:       bool            = Field(..., description="Steward must explicitly consent to data processing")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("gdpr_consent")
    @classmethod
    def consent_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("GDPR consent is required to create an account")
        return v


class StewardUpdate(BaseModel):
    """Schema for updating steward profile (own profile only)."""
    full_name:          Optional[str]   = Field(None, max_length=255)
    display_name:       Optional[str]   = Field(None, max_length=100)
    preferred_language: Optional[str]   = Field(None, pattern="^(de|en|pl)$")
    stellar_public_key: Optional[str]   = Field(None, min_length=56, max_length=56)


class StewardResponse(StewardBase):
    """Public steward response — safe to return to any authenticated caller."""
    id:             UUID
    is_active:      bool
    email_verified: bool
    created_at:     datetime
    roles:          list[str] = []

    model_config = {"from_attributes": True}


class StewardDetailResponse(StewardResponse):
    """Detailed steward response — returned to self or admin."""
    stellar_public_key: Optional[str]
    updated_at:         Optional[datetime]

    model_config = {"from_attributes": True}


class StewardListResponse(BaseModel):
    stewards:   list[StewardResponse]
    total:      int
    page:       int
    per_page:   int
    pages:      int


# ── Authentication schemas ────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:          EmailStr
    password:       str
    remember_me:    bool = False


class LoginResponse(BaseModel):
    access_token:   str
    token_type:     str = "bearer"
    expires_in:     int             # seconds
    steward:        StewardResponse


class RefreshTokenRequest(BaseModel):
    refresh_token:  str


class TokenResponse(BaseModel):
    access_token:   str
    token_type:     str = "bearer"
    expires_in:     int


# ── Password schemas ──────────────────────────────────────────────────────────

class PasswordChangeRequest(BaseModel):
    current_password:   str
    new_password:       str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token:          str
    new_password:   str = Field(..., min_length=8, max_length=128)


class EmailVerificationRequest(BaseModel):
    token: str


# ── Role schemas ──────────────────────────────────────────────────────────────

class RoleResponse(BaseModel):
    id:             UUID
    name:           str
    display_name:   str
    description:    Optional[str]
    is_system:      bool
    created_at:     datetime
    permissions:    list[str] = []

    model_config = {"from_attributes": True}


class RoleAssignmentRequest(BaseModel):
    role_name: str


# ── Permission schemas ────────────────────────────────────────────────────────

class PermissionResponse(BaseModel):
    id:             UUID
    name:           str
    display_name:   str
    description:    Optional[str]
    category:       Optional[str]
    is_system:      bool

    model_config = {"from_attributes": True}


class PermissionCheckRequest(BaseModel):
    permission: str


class PermissionCheckResponse(BaseModel):
    permission: str
    allowed:    bool


# ── Session schemas ───────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    id:             UUID
    user_agent:     Optional[str]
    created_at:     datetime
    last_used_at:   datetime
    is_current:     bool = False

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions:   list[SessionResponse]
    total:      int


# ── Generic responses ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message:    str
    success:    bool = True
