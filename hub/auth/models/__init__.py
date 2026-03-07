"""
Module: auth/models/__init__.py
Service: hub (iot.ubec.network)
Purpose: SQLAlchemy ORM models for the ubec_hub schema.
         Maps to tables created by ubec_hub_schema.sql.
         stewards (not users), steward_sessions (not user_sessions).
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, String, Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship

from auth.database import Base


# ── Steward ───────────────────────────────────────────────────────────────────

class Steward(Base):
    """
    A steward is a person who takes responsibility for a place, practice,
    or community within UBEC. The word is deliberate — not 'user'.

    Maps to: ubec_hub.stewards
    """
    __tablename__ = "stewards"
    __table_args__ = {"schema": "ubec_hub"}

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email               = Column(String(255), unique=True, nullable=False, index=True)
    password_hash       = Column(String(255), nullable=False)
    full_name           = Column(String(255), nullable=True)
    display_name        = Column(String(100), nullable=True)
    stellar_public_key  = Column(String(56), unique=True, nullable=True)
    preferred_language  = Column(String(2), nullable=False, default="en")
    is_active           = Column(Boolean, nullable=False, default=True)
    email_verified      = Column(Boolean, nullable=False, default=False)

    # GDPR
    gdpr_consent_given  = Column(Boolean, nullable=False, default=False)
    gdpr_consent_at     = Column(DateTime(timezone=True), nullable=True)

    # Email verification and password reset tokens (never exposed in API responses)
    verification_token  = Column(String(255), nullable=True)
    reset_token         = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at          = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at          = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    sessions    = relationship("StewardSession", back_populates="steward", cascade="all, delete-orphan")
    roles       = relationship("StewardRole",    back_populates="steward", cascade="all, delete-orphan",
                               foreign_keys="StewardRole.steward_id")

    def __repr__(self) -> str:
        return f"<Steward {self.email}>"

    @property
    def role_names(self) -> list[str]:
        """Return list of role names. Only call when roles are eagerly loaded."""
        return [sr.role.name for sr in self.roles if sr.role]


# ── StewardSession ────────────────────────────────────────────────────────────

class StewardSession(Base):
    """
    JWT session tracking — one row per active token.
    Enables session revocation without a token blacklist.

    Maps to: ubec_hub.steward_sessions
    """
    __tablename__ = "steward_sessions"
    __table_args__ = {"schema": "ubec_hub"}

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    steward_id      = Column(
        UUID(as_uuid=True),
        ForeignKey("ubec_hub.stewards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash      = Column(String(64), unique=True, nullable=False)   # SHA-256
    ip_address      = Column(INET, nullable=True)                       # only with consent
    user_agent      = Column(Text, nullable=True)
    expires_at      = Column(DateTime(timezone=True), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_used_at    = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Soft revocation flag — set to True on logout
    is_revoked      = Column(Boolean, nullable=False, default=False)

    # Relations
    steward = relationship("Steward", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<StewardSession {self.id}>"


# ── Role ──────────────────────────────────────────────────────────────────────

class Role(Base):
    """
    Role definition for RBAC.
    System roles (member, contributor, steward, admin) are seeded by schema.

    Maps to: ubec_hub.roles
    """
    __tablename__ = "roles"
    __table_args__ = {"schema": "ubec_hub"}

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(50), unique=True, nullable=False, index=True)
    display_name    = Column(String(100), nullable=False)
    description     = Column(Text, nullable=True)
    is_system       = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    stewards    = relationship("StewardRole",    back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    @property
    def permission_names(self) -> list[str]:
        return [rp.permission.name for rp in self.permissions if rp.permission]


# ── StewardRole (junction) ────────────────────────────────────────────────────

class StewardRole(Base):
    """
    Steward ↔ Role many-to-many junction.

    Maps to: ubec_hub.steward_roles
    """
    __tablename__ = "steward_roles"
    __table_args__ = (
        UniqueConstraint("steward_id", "role_id", name="uq_steward_role"),
        {"schema": "ubec_hub"},
    )

    steward_id  = Column(
        UUID(as_uuid=True),
        ForeignKey("ubec_hub.stewards.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id     = Column(
        UUID(as_uuid=True),
        ForeignKey("ubec_hub.roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_by  = Column(UUID(as_uuid=True), ForeignKey("ubec_hub.stewards.id", ondelete="SET NULL"), nullable=True)
    granted_at  = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    steward = relationship("Steward", back_populates="roles", foreign_keys=[steward_id])
    role    = relationship("Role",    back_populates="stewards")

    def __repr__(self) -> str:
        return f"<StewardRole steward={self.steward_id} role={self.role_id}>"


# ── Permission ────────────────────────────────────────────────────────────────

class Permission(Base):
    """
    Fine-grained permission. Naming convention: resource:action.

    Maps to: ubec_hub.permissions
    """
    __tablename__ = "permissions"
    __table_args__ = {"schema": "ubec_hub"}

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(100), unique=True, nullable=False, index=True)
    display_name    = Column(String(255), nullable=False)
    description     = Column(Text, nullable=True)
    category        = Column(String(50), nullable=True)
    is_system       = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


# ── RolePermission (junction) ─────────────────────────────────────────────────

class RolePermission(Base):
    """
    Role ↔ Permission many-to-many junction.

    Maps to: ubec_hub.role_permissions
    """
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        {"schema": "ubec_hub"},
    )

    role_id         = Column(
        UUID(as_uuid=True),
        ForeignKey("ubec_hub.roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id   = Column(
        UUID(as_uuid=True),
        ForeignKey("ubec_hub.permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relations
    role        = relationship("Role",       back_populates="permissions")
    permission  = relationship("Permission", back_populates="roles")

    def __repr__(self) -> str:
        return f"<RolePermission role={self.role_id} permission={self.permission_id}>"
