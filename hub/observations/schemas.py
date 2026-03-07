"""
Module: observations/schemas.py
Service: hub (iot.ubec.network)
Purpose: Pydantic v2 request/response schemas for the observations module.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from activities.models import ProxemicZone

# Valid language codes — must match DB CHECK constraint exactly
VALID_LANGUAGES = ("de", "en", "pl")


# ── Location ──────────────────────────────────────────────────────────────────

class LocationIn(BaseModel):
    """Lat/lng supplied by the client. Converted to WKT in service layer."""
    model_config = ConfigDict(str_strip_whitespace=True)

    latitude  : float = Field(..., ge=-90,  le=90)
    longitude : float = Field(..., ge=-180, le=180)
    note      : Optional[str] = None  # stored in location_note column


class LocationOut(BaseModel):
    """Lat/lng returned to client. Extracted from PostGIS via ST_X/ST_Y."""
    latitude  : float
    longitude : float


# ── ObservationResponse schemas ───────────────────────────────────────────────

class ObservationResponseIn(BaseModel):
    """One field response submitted with an observation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    field_id      : UUID
    value_text    : Optional[str]  = None
    value_pattern : Optional[UUID] = None


class ObservationResponseOut(BaseModel):
    """One field response as returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id            : UUID
    observation_id: UUID
    field_id      : UUID
    value_text    : Optional[str]
    value_pattern : Optional[UUID]
    created_at    : datetime


# ── Observation schemas ───────────────────────────────────────────────────────

class ObservationCreate(BaseModel):
    """
    Submit a new observation.

    `qualitative_notes` is required — the Goethean design constraint
    that every observation must contain a phenomenological description.
    Structured field responses in `responses` are additional.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    activity_id       : UUID
    observed_at       : datetime
    qualitative_notes : str            = Field(..., min_length=1)
    proxemic_zone     : ProxemicZone
    language          : str            = Field("en", min_length=2, max_length=2)
    location          : Optional[LocationIn]  = None
    device_id         : Optional[UUID]        = None
    responses         : list[ObservationResponseIn] = Field(default_factory=list)

    @field_validator("language")
    @classmethod
    def valid_language(cls, v: str) -> str:
        if v not in VALID_LANGUAGES:
            raise ValueError(f"language must be one of {VALID_LANGUAGES}")
        return v


class ObservationUpdate(BaseModel):
    """Updatable fields — only before validation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    qualitative_notes : Optional[str]          = Field(None, min_length=1)
    location_note     : Optional[str]          = None
    language          : Optional[str]          = Field(None, min_length=2, max_length=2)
    device_id         : Optional[UUID]         = None

    @field_validator("language")
    @classmethod
    def valid_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_LANGUAGES:
            raise ValueError(f"language must be one of {VALID_LANGUAGES}")
        return v


class ObservationOut(BaseModel):
    """Full observation returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id                : UUID
    activity_id       : UUID
    steward_id        : UUID
    observed_at       : datetime
    qualitative_notes : str
    proxemic_zone     : ProxemicZone
    language          : str
    location          : Optional[LocationOut]
    location_note     : Optional[str]
    device_id         : Optional[UUID]
    is_validated      : bool
    validated_by      : Optional[UUID]
    validated_at      : Optional[datetime]
    created_at        : datetime
    updated_at        : datetime
    responses         : list[ObservationResponseOut] = Field(default_factory=list)


class ObservationListOut(BaseModel):
    observations : list[ObservationOut]
    total        : int
    page         : int
    per_page     : int
    pages        : int


class ValidationIn(BaseModel):
    """Body for the validate endpoint."""
    notes : Optional[str] = None
