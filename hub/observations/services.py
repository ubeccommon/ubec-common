"""
Module: observations/services.py
Service: hub (iot.ubec.network)
Purpose: Business logic for Observation and ObservationResponse CRUD.

PostGIS pattern used throughout:
  WRITE: INSERT/UPDATE uses ST_GeomFromText('POINT(lon lat)', 4326) via
         raw text() SQL — the ORM never touches the location column.
  READ:  SELECT uses ST_X(location::geometry) AS longitude,
                     ST_Y(location::geometry) AS latitude
         via text() fragments embedded in select() calls.
         When location IS NULL both values are None.

All other columns are handled by the ORM normally.

License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from activities.models import Activity
from observations.models import Observation, ObservationResponse
from observations.schemas import (
    LocationIn, LocationOut, ObservationCreate,
    ObservationOut, ObservationResponseOut, ObservationUpdate,
    ValidationIn,
)

logger = logging.getLogger(__name__)


def _wkt_point(loc: LocationIn) -> str:
    """Convert LocationIn to WKT POINT string. Note: WKT is (lon lat)."""
    return f"POINT({loc.longitude} {loc.latitude})"


async def _read_location(db: AsyncSession, observation_id: UUID) -> LocationOut | None:
    """
    Extract lat/lng from the PostGIS geography column for one observation.
    Returns None if location IS NULL.
    """
    row = await db.execute(
        text("""
            SELECT
                ST_Y(location::geometry) AS latitude,
                ST_X(location::geometry) AS longitude
            FROM ubec_hub.observations
            WHERE id = :id
              AND location IS NOT NULL
        """),
        {"id": str(observation_id)},
    )
    r = row.fetchone()
    if r is None:
        return None
    return LocationOut(latitude=r.latitude, longitude=r.longitude)


async def _build_out(
    db: AsyncSession,
    obs: Observation,
    responses: list[ObservationResponse],
) -> ObservationOut:
    """Assemble ObservationOut from ORM object + responses, fetching location separately."""
    location = await _read_location(db, obs.id)
    return ObservationOut(
        id                = obs.id,
        activity_id       = obs.activity_id,
        steward_id        = obs.steward_id,
        observed_at       = obs.observed_at,
        qualitative_notes = obs.qualitative_notes,
        proxemic_zone     = obs.proxemic_zone,
        language          = obs.language,
        location          = location,
        location_note     = obs.location_note,
        device_id         = obs.device_id,
        is_validated      = obs.is_validated,
        validated_by      = obs.validated_by,
        validated_at      = obs.validated_at,
        created_at        = obs.created_at,
        updated_at        = obs.updated_at,
        responses         = [
            ObservationResponseOut(
                id             = r.id,
                observation_id = r.observation_id,
                field_id       = r.field_id,
                value_text     = r.value_text,
                value_pattern  = r.value_pattern,
                created_at     = r.created_at,
            )
            for r in responses
        ],
    )


class ObservationService:

    # ── Create ────────────────────────────────────────────────────────────────

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        data: ObservationCreate,
        steward_id: UUID,
    ) -> ObservationOut:
        # Verify activity exists
        act_result = await db.execute(
            select(Activity).where(Activity.id == data.activity_id)
        )
        if act_result.scalar_one_or_none() is None:
            raise ValueError(f"Activity {data.activity_id} not found")

        obs_id = uuid4()
        now    = datetime.now(timezone.utc)

        # Build the INSERT via raw SQL to handle the geography column
        if data.location:
            wkt = _wkt_point(data.location)
            await db.execute(
                text("""
                    INSERT INTO ubec_hub.observations
                        (id, activity_id, steward_id, observed_at, location,
                         location_note, proxemic_zone, qualitative_notes,
                         device_id, language, is_validated, created_at, updated_at)
                    VALUES
                        (:id, :activity_id, :steward_id, :observed_at,
                         ST_GeomFromText(:wkt, 4326),
                         :location_note, :proxemic_zone, :qualitative_notes,
                         :device_id, :language, false, :now, :now)
                """),
                {
                    "id"               : str(obs_id),
                    "activity_id"      : str(data.activity_id),
                    "steward_id"       : str(steward_id),
                    "observed_at"      : data.observed_at,
                    "wkt"              : wkt,
                    "location_note"    : data.location.note if data.location else None,
                    "proxemic_zone"    : data.proxemic_zone.value,
                    "qualitative_notes": data.qualitative_notes,
                    "device_id"        : str(data.device_id) if data.device_id else None,
                    "language"         : data.language,
                    "now"              : now,
                },
            )
        else:
            await db.execute(
                text("""
                    INSERT INTO ubec_hub.observations
                        (id, activity_id, steward_id, observed_at,
                         location_note, proxemic_zone, qualitative_notes,
                         device_id, language, is_validated, created_at, updated_at)
                    VALUES
                        (:id, :activity_id, :steward_id, :observed_at,
                         :location_note, :proxemic_zone, :qualitative_notes,
                         :device_id, :language, false, :now, :now)
                """),
                {
                    "id"               : str(obs_id),
                    "activity_id"      : str(data.activity_id),
                    "steward_id"       : str(steward_id),
                    "observed_at"      : data.observed_at,
                    "location_note"    : None,
                    "proxemic_zone"    : data.proxemic_zone.value,
                    "qualitative_notes": data.qualitative_notes,
                    "device_id"        : str(data.device_id) if data.device_id else None,
                    "language"         : data.language,
                    "now"              : now,
                },
            )

        # Insert responses
        responses: list[ObservationResponse] = []
        for r in data.responses:
            resp = ObservationResponse(
                id             = uuid4(),
                observation_id = obs_id,
                field_id       = r.field_id,
                value_text     = r.value_text,
                value_pattern  = r.value_pattern,
                created_at     = now,
            )
            db.add(resp)
            responses.append(resp)

        await db.commit()

        # Reload ORM object (location handled separately)
        obs_result = await db.execute(
            select(Observation)
            .where(Observation.id == obs_id)
            .options(selectinload(Observation.responses))
        )
        obs = obs_result.scalar_one()
        responses = list(obs.responses)

        return await _build_out(db, obs, responses)

    # ── Get by ID ─────────────────────────────────────────────────────────────

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        observation_id: UUID,
    ) -> ObservationOut | None:
        result = await db.execute(
            select(Observation)
            .where(Observation.id == observation_id)
            .options(selectinload(Observation.responses))
        )
        obs = result.scalar_one_or_none()
        if obs is None:
            return None
        return await _build_out(db, obs, list(obs.responses))

    # ── List ──────────────────────────────────────────────────────────────────

    @classmethod
    async def list(
        cls,
        db: AsyncSession,
        *,
        activity_id  : UUID | None = None,
        steward_id   : UUID | None = None,
        is_validated : bool | None = None,
        page         : int = 1,
        per_page     : int = 20,
    ) -> tuple[list[ObservationOut], int]:
        query = select(Observation)

        if activity_id  is not None:
            query = query.where(Observation.activity_id == activity_id)
        if steward_id   is not None:
            query = query.where(Observation.steward_id == steward_id)
        if is_validated is not None:
            query = query.where(Observation.is_validated == is_validated)

        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        query = (
            query
            .order_by(Observation.observed_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .options(selectinload(Observation.responses))
        )
        result  = await db.execute(query)
        obs_list = result.scalars().all()

        out = []
        for obs in obs_list:
            out.append(await _build_out(db, obs, list(obs.responses)))
        return out, total

    # ── Update ────────────────────────────────────────────────────────────────

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        obs: Observation,
        data: ObservationUpdate,
    ) -> ObservationOut:
        if obs.is_validated:
            raise ValueError("Cannot update a validated observation")

        now = datetime.now(timezone.utc)

        if data.qualitative_notes is not None:
            obs.qualitative_notes = data.qualitative_notes
        if data.location_note     is not None:
            obs.location_note     = data.location_note
        if data.language          is not None:
            obs.language          = data.language
        if data.device_id         is not None:
            obs.device_id         = data.device_id

        obs.updated_at = now
        await db.commit()

        result = await db.execute(
            select(Observation)
            .where(Observation.id == obs.id)
            .options(selectinload(Observation.responses))
        )
        obs = result.scalar_one()
        return await _build_out(db, obs, list(obs.responses))

    # ── Validate ──────────────────────────────────────────────────────────────

    @classmethod
    async def validate(
        cls,
        db: AsyncSession,
        obs: Observation,
        validator_id: UUID,
        data: ValidationIn,
    ) -> ObservationOut:
        if obs.is_validated:
            raise ValueError("Observation is already validated")

        now = datetime.now(timezone.utc)

        await db.execute(
            update(Observation)
            .where(Observation.id == obs.id)
            .values(
                is_validated = True,
                validated_by = validator_id,
                validated_at = now,
                updated_at   = now,
            )
        )
        await db.commit()

        result = await db.execute(
            select(Observation)
            .where(Observation.id == obs.id)
            .options(selectinload(Observation.responses))
        )
        obs = result.scalar_one()
        return await _build_out(db, obs, list(obs.responses))

    # ── Delete ────────────────────────────────────────────────────────────────

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        obs: Observation,
        steward_id: UUID,
    ) -> None:
        """Hard delete. Only allowed by the owning steward, and only if not validated."""
        if obs.is_validated:
            raise ValueError("Cannot delete a validated observation")
        if obs.steward_id != steward_id:
            raise PermissionError("Only the observing steward may delete this observation")
        await db.delete(obs)
        await db.commit()

    # ── Upsert responses ──────────────────────────────────────────────────────

    @classmethod
    async def upsert_response(
        cls,
        db: AsyncSession,
        obs: Observation,
        field_id: UUID,
        value_text: str | None,
        value_pattern: UUID | None,
    ) -> ObservationResponse:
        """Add or update a single field response on an existing observation."""
        if obs.is_validated:
            raise ValueError("Cannot modify responses on a validated observation")

        result = await db.execute(
            select(ObservationResponse).where(
                ObservationResponse.observation_id == obs.id,
                ObservationResponse.field_id       == field_id,
            )
        )
        resp = result.scalar_one_or_none()

        if resp:
            resp.value_text    = value_text
            resp.value_pattern = value_pattern
        else:
            resp = ObservationResponse(
                id             = uuid4(),
                observation_id = obs.id,
                field_id       = field_id,
                value_text     = value_text,
                value_pattern  = value_pattern,
                created_at     = datetime.now(timezone.utc),
            )
            db.add(resp)

        await db.commit()
        await db.refresh(resp)
        return resp
