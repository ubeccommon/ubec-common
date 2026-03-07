"""
Module: observations/routes.py
Service: hub (iot.ubec.network)
Purpose: FastAPI routes for the observations module.
         Prefix: /api/v1/observations

Route ordering rule: all literal-segment routes before /{observation_id}.

License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.database import get_db
from auth.dependencies import CurrentSteward, get_current_steward, require_permission
from observations.models import Observation
from observations.schemas import (
    ObservationCreate, ObservationListOut, ObservationOut,
    ObservationResponseOut, ObservationUpdate, ValidationIn,
    ObservationResponseIn,
)
from observations.services import ObservationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/observations", tags=["observations"])


# ── Helper ────────────────────────────────────────────────────────────────────

async def _get_obs_or_404(db: AsyncSession, observation_id: UUID) -> Observation:
    result = await db.execute(
        select(Observation)
        .where(Observation.id == observation_id)
        .options(selectinload(Observation.responses))
    )
    obs = result.scalar_one_or_none()
    if obs is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    return obs


# ── Health — must be before /{observation_id} ─────────────────────────────────

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status" : "healthy" if db_status == "connected" else "degraded",
        "module" : "observations",
        "version": "1.0.0",
        "database": db_status,
    }


# ── List & create ─────────────────────────────────────────────────────────────

@router.get("", response_model=ObservationListOut)
async def list_observations(
    activity_id  : Optional[UUID] = Query(None),
    steward_id   : Optional[UUID] = Query(None),
    is_validated : Optional[bool] = Query(None),
    page         : int            = Query(1, ge=1),
    per_page     : int            = Query(20, ge=1, le=100),
    db           : AsyncSession   = Depends(get_db),
    current      : CurrentSteward = Depends(get_current_steward),
):
    """
    List observations. Auth required — proxemic zone filtering is applied
    by the service in a future phase. For now returns all observations
    visible to an authenticated steward.
    """
    obs_list, total = await ObservationService.list(
        db,
        activity_id  = activity_id,
        steward_id   = steward_id,
        is_validated = is_validated,
        page         = page,
        per_page     = per_page,
    )
    return ObservationListOut(
        observations = obs_list,
        total        = total,
        page         = page,
        per_page     = per_page,
        pages        = max(1, (total + per_page - 1) // per_page),
    )


@router.post("", response_model=ObservationOut, status_code=status.HTTP_201_CREATED)
async def create_observation(
    data    : ObservationCreate,
    current : CurrentSteward = Depends(require_permission("observations:create")),
    db      : AsyncSession   = Depends(get_db),
):
    """Submit a new observation. Requires observations:create permission."""
    try:
        obs = await ObservationService.create(db, data, steward_id=current.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return obs


# ── Single observation — /{observation_id} must be last among GET routes ──────

@router.get("/{observation_id}", response_model=ObservationOut)
async def get_observation(
    observation_id: UUID,
    db            : AsyncSession   = Depends(get_db),
    current       : CurrentSteward = Depends(get_current_steward),
):
    """Get a single observation with all responses. Auth required."""
    out = await ObservationService.get_by_id(db, observation_id)
    if out is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    return out


@router.patch("/{observation_id}", response_model=ObservationOut)
async def update_observation(
    observation_id: UUID,
    data          : ObservationUpdate,
    current       : CurrentSteward = Depends(get_current_steward),
    db            : AsyncSession   = Depends(get_db),
):
    """
    Update an observation. Only the owning steward may update.
    Not permitted after validation.
    """
    obs = await _get_obs_or_404(db, observation_id)
    if obs.steward_id != current.id:
        raise HTTPException(status_code=403, detail="Only the observing steward may update this observation")
    try:
        return await ObservationService.update(db, obs, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_observation(
    observation_id: UUID,
    current       : CurrentSteward = Depends(get_current_steward),
    db            : AsyncSession   = Depends(get_db),
):
    """
    Delete an observation. Only the owning steward may delete.
    Not permitted after validation.
    """
    obs = await _get_obs_or_404(db, observation_id)
    try:
        await ObservationService.delete(db, obs, steward_id=current.id)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── Validation — admin/lead_steward action ────────────────────────────────────

@router.post(
    "/{observation_id}/validate",
    response_model=ObservationOut,
)
async def validate_observation(
    observation_id: UUID,
    data          : ValidationIn,
    current       : CurrentSteward = Depends(require_permission("observations:validate")),
    db            : AsyncSession   = Depends(get_db),
):
    """
    Mark an observation as validated. Requires observations:validate permission.
    Validated observations cannot be updated or deleted.
    """
    obs = await _get_obs_or_404(db, observation_id)
    try:
        return await ObservationService.validate(db, obs, validator_id=current.id, data=data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── Response upsert ───────────────────────────────────────────────────────────

@router.put(
    "/{observation_id}/responses/{field_id}",
    response_model=ObservationResponseOut,
)
async def upsert_response(
    observation_id: UUID,
    field_id      : UUID,
    data          : ObservationResponseIn,
    current       : CurrentSteward = Depends(get_current_steward),
    db            : AsyncSession   = Depends(get_db),
):
    """
    Add or update a single field response on an observation.
    Only the owning steward may modify responses.
    Not permitted after validation.
    """
    obs = await _get_obs_or_404(db, observation_id)
    if obs.steward_id != current.id:
        raise HTTPException(status_code=403, detail="Only the observing steward may modify responses")
    try:
        resp = await ObservationService.upsert_response(
            db, obs,
            field_id      = field_id,
            value_text    = data.value_text,
            value_pattern = data.value_pattern,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ObservationResponseOut(
        id             = resp.id,
        observation_id = resp.observation_id,
        field_id       = resp.field_id,
        value_text     = resp.value_text,
        value_pattern  = resp.value_pattern,
        created_at     = resp.created_at,
    )
