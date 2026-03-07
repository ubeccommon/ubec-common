"""
Module: activities/routes.py
Service: hub (iot.ubec.network)
Purpose: FastAPI routes for the activities module.
         Prefix: /api/v1/activities
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from activities.models import ActivityScope
from activities.schemas import (
    ActivityCreate, ActivityDetailResponse, ActivityFieldCreate,
    ActivityFieldResponse, ActivityFieldUpdate, ActivityListResponse,
    ActivityResponse, ActivityUpdate, SeedResponse,
)
from activities.services import ActivityService
from auth.database import get_db
from auth.dependencies import CurrentSteward, get_current_steward, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _activity_response(activity) -> ActivityResponse:
    fields = activity.fields if hasattr(activity, "fields") and activity.fields else []
    return ActivityResponse(
        id            = activity.id,
        name          = activity.name,
        slug          = activity.slug,
        description   = activity.description,
        scope         = activity.scope,
        proxemic_zone = activity.proxemic_zone,
        living_lab_id = activity.living_lab_id,
        watershed_id  = activity.watershed_id,
        bioregion_id  = activity.bioregion_id,
        created_by    = activity.created_by,
        starts_at     = activity.starts_at,
        ends_at       = activity.ends_at,
        is_active     = activity.is_active,
        is_template   = activity.is_template,
        pattern_id    = activity.pattern_id,
        metadata      = activity.extra_data,
        created_at    = activity.created_at,
        updated_at    = activity.updated_at,
        field_count   = len(fields),
    )


def _activity_detail_response(activity) -> ActivityDetailResponse:
    fields = activity.fields if hasattr(activity, "fields") and activity.fields else []
    return ActivityDetailResponse(
        id            = activity.id,
        name          = activity.name,
        slug          = activity.slug,
        description   = activity.description,
        scope         = activity.scope,
        proxemic_zone = activity.proxemic_zone,
        living_lab_id = activity.living_lab_id,
        watershed_id  = activity.watershed_id,
        bioregion_id  = activity.bioregion_id,
        created_by    = activity.created_by,
        starts_at     = activity.starts_at,
        ends_at       = activity.ends_at,
        is_active     = activity.is_active,
        is_template   = activity.is_template,
        pattern_id    = activity.pattern_id,
        metadata      = activity.extra_data,
        created_at    = activity.created_at,
        updated_at    = activity.updated_at,
        field_count   = len(fields),
        fields        = [
            ActivityFieldResponse.model_validate(f) for f in fields
        ],
    )


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "module": "activities",
        "version": "1.0.0",
        "database": db_status,
    }


# ── Activity list & create ────────────────────────────────────────────────────

@router.get("", response_model=ActivityListResponse)
async def list_activities(
    scope        : Optional[ActivityScope] = Query(None),
    living_lab_id: Optional[UUID]          = Query(None),
    is_active    : Optional[bool]          = Query(True),
    is_template  : Optional[bool]          = Query(None),
    page         : int                     = Query(1, ge=1),
    per_page     : int                     = Query(20, ge=1, le=100),
    db           : AsyncSession            = Depends(get_db),
):
    """List activities. Public endpoint — no auth required."""
    activities, total = await ActivityService.list(
        db,
        scope         = scope,
        living_lab_id = living_lab_id,
        is_active     = is_active,
        is_template   = is_template,
        page          = page,
        per_page      = per_page,
    )
    return ActivityListResponse(
        activities = [_activity_response(a) for a in activities],
        total      = total,
        page       = page,
        per_page   = per_page,
        pages      = max(1, (total + per_page - 1) // per_page),
    )


@router.post("", response_model=ActivityDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    data    : ActivityCreate,
    current : CurrentSteward = Depends(require_permission("activities:create")),
    db      : AsyncSession   = Depends(get_db),
):
    """Create a new activity. Requires activities:create permission."""
    try:
        activity = await ActivityService.create(db, data, created_by=current.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _activity_detail_response(activity)


# ── Activity detail, update, delete ──────────────────────────────────────────

@router.get("/slug/{slug}", response_model=ActivityDetailResponse)
async def get_activity_by_slug(
    slug: str,
    db  : AsyncSession = Depends(get_db),
):
    """Get a single activity by slug. Public."""
    activity = await ActivityService.get_by_slug(db, slug)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return _activity_detail_response(activity)


@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity(
    activity_id: UUID,
    db         : AsyncSession = Depends(get_db),
):
    """Get a single activity with all fields. Public."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return _activity_detail_response(activity)


@router.patch("/{activity_id}", response_model=ActivityDetailResponse)
async def update_activity(
    activity_id: UUID,
    data       : ActivityUpdate,
    current    : CurrentSteward = Depends(require_permission("activities:manage")),
    db         : AsyncSession   = Depends(get_db),
):
    """Update activity metadata. Requires activities:manage permission."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = await ActivityService.update(db, activity, data)
    return _activity_detail_response(activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_activity(
    activity_id: UUID,
    current    : CurrentSteward = Depends(require_permission("activities:manage")),
    db         : AsyncSession   = Depends(get_db),
):
    """Deactivate an activity (soft delete). Requires activities:manage permission."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    await ActivityService.delete(db, activity)


# ── Field management ──────────────────────────────────────────────────────────

@router.post(
    "/{activity_id}/fields",
    response_model=ActivityFieldResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_field(
    activity_id: UUID,
    data       : ActivityFieldCreate,
    current    : CurrentSteward = Depends(require_permission("activities:manage")),
    db         : AsyncSession   = Depends(get_db),
):
    """Add a field to an activity. Requires activities:manage permission."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    try:
        field = await ActivityService.add_field(db, activity, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ActivityFieldResponse.model_validate(field)


@router.patch(
    "/{activity_id}/fields/{field_id}",
    response_model=ActivityFieldResponse,
)
async def update_field(
    activity_id: UUID,
    field_id   : UUID,
    data       : ActivityFieldUpdate,
    current    : CurrentSteward = Depends(require_permission("activities:manage")),
    db         : AsyncSession   = Depends(get_db),
):
    """Update an activity field. Requires activities:manage permission."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    field = next((f for f in activity.fields if f.id == field_id), None)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    field = await ActivityService.update_field(db, field, data)
    return ActivityFieldResponse.model_validate(field)


@router.delete(
    "/{activity_id}/fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_field(
    activity_id: UUID,
    field_id   : UUID,
    current    : CurrentSteward = Depends(require_permission("activities:manage")),
    db         : AsyncSession   = Depends(get_db),
):
    """Remove a field from an activity. Requires activities:manage permission."""
    activity = await ActivityService.get_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    field = next((f for f in activity.fields if f.id == field_id), None)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    await ActivityService.delete_field(db, field)


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed/13-questions", response_model=SeedResponse, status_code=status.HTTP_200_OK)
async def seed_13_questions(
    current: CurrentSteward = Depends(require_permission("activities:manage")),
    db     : AsyncSession   = Depends(get_db),
):
    """
    Seed the canonical '13 Fragen an den Boden' activity.
    Idempotent — safe to call multiple times.
    Requires activities:manage permission.
    """
    created, skipped = await ActivityService.seed_13_questions(db, created_by=current.id)
    slugs = ["13-fragen-an-den-boden"] if created else []
    return SeedResponse(created=created, skipped=skipped, activities=slugs)
