"""
Module: activities/schemas.py
Service: hub (iot.ubec.network)
Purpose: Pydantic v2 request/response schemas for the activities module.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import re
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from activities.models import ActivityScope, FieldType, ProxemicZone


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(value: str) -> str:
    """Convert a name to a URL-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


# ── ActivityField schemas ─────────────────────────────────────────────────────

class ActivityFieldCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name          : str       = Field(..., min_length=1, max_length=100)
    label         : str       = Field(..., min_length=1, max_length=255)
    label_de      : Optional[str]  = Field(None, max_length=255)
    label_pl      : Optional[str]  = Field(None, max_length=255)
    description   : Optional[str]  = None
    field_type    : FieldType
    is_required   : bool           = False
    display_order : int            = Field(0, ge=0, le=32767)
    options       : Optional[Any]  = None  # JSONB — list of choices for select fields
    scale_config  : Optional[Any]  = None  # JSONB — {min, max, step, labels}
    unit          : Optional[str]  = Field(None, max_length=50)
    validation    : Optional[Any]  = None  # JSONB — {min_length, max_length, pattern, …}
    pattern_scope : Optional[UUID] = None


class ActivityFieldUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label         : Optional[str]  = Field(None, min_length=1, max_length=255)
    label_de      : Optional[str]  = Field(None, max_length=255)
    label_pl      : Optional[str]  = Field(None, max_length=255)
    description   : Optional[str]  = None
    is_required   : Optional[bool] = None
    display_order : Optional[int]  = Field(None, ge=0, le=32767)
    options       : Optional[Any]  = None
    scale_config  : Optional[Any]  = None
    unit          : Optional[str]  = Field(None, max_length=50)
    validation    : Optional[Any]  = None


class ActivityFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id            : UUID
    activity_id   : UUID
    name          : str
    label         : str
    label_de      : Optional[str]
    label_pl      : Optional[str]
    description   : Optional[str]
    field_type    : FieldType
    is_required   : bool
    display_order : int
    options       : Optional[Any]
    scale_config  : Optional[Any]
    unit          : Optional[str]
    validation    : Optional[Any]
    pattern_scope : Optional[UUID]
    created_at    : datetime


# ── Activity schemas ──────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name          : str                 = Field(..., min_length=1, max_length=255)
    slug          : Optional[str]       = Field(None, max_length=100)
    description   : Optional[str]       = None
    scope         : ActivityScope       = ActivityScope.personal
    proxemic_zone : ProxemicZone        = ProxemicZone.personal
    living_lab_id : Optional[UUID]      = None
    watershed_id  : Optional[UUID]      = None
    bioregion_id  : Optional[UUID]      = None
    starts_at     : Optional[datetime]  = None
    ends_at       : Optional[datetime]  = None
    is_template   : bool                = False
    pattern_id    : Optional[UUID]      = None
    metadata      : dict                = Field(default_factory=dict)
    fields        : list[ActivityFieldCreate] = Field(default_factory=list)

    @field_validator("slug", mode="before")
    @classmethod
    def auto_slug(cls, v: Optional[str], info) -> str:
        if v:
            return _slugify(v)
        # will be derived from name in service if still empty
        return v

    @field_validator("ends_at", mode="after")
    @classmethod
    def ends_after_starts(cls, v: Optional[datetime], info) -> Optional[datetime]:
        starts = info.data.get("starts_at")
        if v and starts and v <= starts:
            raise ValueError("ends_at must be after starts_at")
        return v


class ActivityUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name          : Optional[str]       = Field(None, min_length=1, max_length=255)
    description   : Optional[str]       = None
    scope         : Optional[ActivityScope]    = None
    proxemic_zone : Optional[ProxemicZone]     = None
    living_lab_id : Optional[UUID]      = None
    watershed_id  : Optional[UUID]      = None
    bioregion_id  : Optional[UUID]      = None
    starts_at     : Optional[datetime]  = None
    ends_at       : Optional[datetime]  = None
    is_active     : Optional[bool]      = None
    is_template   : Optional[bool]      = None
    pattern_id    : Optional[UUID]      = None
    metadata      : Optional[dict]      = None


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id            : UUID
    name          : str
    slug          : str
    description   : Optional[str]
    scope         : ActivityScope
    proxemic_zone : ProxemicZone
    living_lab_id : Optional[UUID]
    watershed_id  : Optional[UUID]
    bioregion_id  : Optional[UUID]
    created_by    : UUID
    starts_at     : Optional[datetime]
    ends_at       : Optional[datetime]
    is_active     : bool
    is_template   : bool
    pattern_id    : Optional[UUID]
    metadata      : dict
    created_at    : datetime
    updated_at    : datetime
    field_count   : int = 0  # populated by service


class ActivityDetailResponse(ActivityResponse):
    """Full activity with fields included."""
    fields: list[ActivityFieldResponse] = Field(default_factory=list)


class ActivityListResponse(BaseModel):
    activities : list[ActivityResponse]
    total      : int
    page       : int
    per_page   : int
    pages      : int


# ── Seed schema ───────────────────────────────────────────────────────────────

class SeedResponse(BaseModel):
    created   : int
    skipped   : int
    activities: list[str]  # slugs
