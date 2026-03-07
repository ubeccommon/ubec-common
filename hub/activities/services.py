"""
Module: activities/services.py
Service: hub (iot.ubec.network)
Purpose: Business logic for Activity and ActivityField CRUD.
         Includes seed data for "13 Fragen an den Boden" activity.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from activities.models import Activity, ActivityField, ActivityScope, FieldType, ProxemicZone
from activities.schemas import ActivityCreate, ActivityFieldCreate, ActivityFieldUpdate, ActivityUpdate

logger = logging.getLogger(__name__)


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


class ActivityService:

    # ── Activity CRUD ─────────────────────────────────────────────────────────

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        data: ActivityCreate,
        created_by: UUID,
    ) -> Activity:
        slug = data.slug or _slugify(data.name)

        # Ensure slug uniqueness
        existing = await db.execute(
            select(Activity).where(Activity.slug == slug)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Slug '{slug}' is already in use")

        activity = Activity(
            name          = data.name,
            slug          = slug,
            description   = data.description,
            scope         = data.scope,
            proxemic_zone = data.proxemic_zone,
            living_lab_id = data.living_lab_id,
            watershed_id  = data.watershed_id,
            bioregion_id  = data.bioregion_id,
            created_by    = created_by,
            starts_at     = data.starts_at,
            ends_at       = data.ends_at,
            is_active     = True,
            is_template   = data.is_template,
            pattern_id    = data.pattern_id,
            metadata      = data.metadata,
        )
        db.add(activity)
        await db.flush()  # get activity.id before adding fields

        for i, field_data in enumerate(data.fields):
            field = ActivityField(
                activity_id   = activity.id,
                name          = field_data.name,
                label         = field_data.label,
                label_de      = field_data.label_de,
                label_pl      = field_data.label_pl,
                description   = field_data.description,
                field_type    = field_data.field_type,
                is_required   = field_data.is_required,
                display_order = field_data.display_order if field_data.display_order else i,
                options       = field_data.options,
                scale_config  = field_data.scale_config,
                unit          = field_data.unit,
                validation    = field_data.validation,
                pattern_scope = field_data.pattern_scope,
            )
            db.add(field)

        await db.commit()

        result = await db.execute(
            select(Activity)
            .where(Activity.id == activity.id)
            .options(selectinload(Activity.fields))
        )
        return result.scalar_one()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, activity_id: UUID) -> Activity | None:
        result = await db.execute(
            select(Activity)
            .where(Activity.id == activity_id)
            .options(selectinload(Activity.fields))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_slug(cls, db: AsyncSession, slug: str) -> Activity | None:
        result = await db.execute(
            select(Activity)
            .where(Activity.slug == slug)
            .options(selectinload(Activity.fields))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list(
        cls,
        db: AsyncSession,
        *,
        scope: ActivityScope | None = None,
        living_lab_id: UUID | None = None,
        is_active: bool | None = True,
        is_template: bool | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Activity], int]:
        query = select(Activity)

        if scope is not None:
            query = query.where(Activity.scope == scope)
        if living_lab_id is not None:
            query = query.where(Activity.living_lab_id == living_lab_id)
        if is_active is not None:
            query = query.where(Activity.is_active == is_active)
        if is_template is not None:
            query = query.where(Activity.is_template == is_template)

        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        query = (
            query
            .order_by(Activity.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(query)
        activities = result.scalars().all()
        return list(activities), total

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        activity: Activity,
        data: ActivityUpdate,
    ) -> Activity:
        if data.name          is not None: activity.name          = data.name
        if data.description   is not None: activity.description   = data.description
        if data.scope         is not None: activity.scope         = data.scope
        if data.proxemic_zone is not None: activity.proxemic_zone = data.proxemic_zone
        if data.living_lab_id is not None: activity.living_lab_id = data.living_lab_id
        if data.watershed_id  is not None: activity.watershed_id  = data.watershed_id
        if data.bioregion_id  is not None: activity.bioregion_id  = data.bioregion_id
        if data.starts_at     is not None: activity.starts_at     = data.starts_at
        if data.ends_at       is not None: activity.ends_at       = data.ends_at
        if data.is_active     is not None: activity.is_active     = data.is_active
        if data.is_template   is not None: activity.is_template   = data.is_template
        if data.pattern_id    is not None: activity.pattern_id    = data.pattern_id
        if data.metadata      is not None: activity.metadata      = data.metadata

        activity.updated_at = datetime.now(timezone.utc)
        await db.commit()

        result = await db.execute(
            select(Activity)
            .where(Activity.id == activity.id)
            .options(selectinload(Activity.fields))
        )
        return result.scalar_one()

    @classmethod
    async def delete(cls, db: AsyncSession, activity: Activity) -> None:
        """Soft-delete by deactivating. Hard delete is not permitted."""
        activity.is_active = False
        activity.updated_at = datetime.now(timezone.utc)
        await db.commit()

    # ── Field CRUD ────────────────────────────────────────────────────────────

    @classmethod
    async def add_field(
        cls,
        db: AsyncSession,
        activity: Activity,
        data: ActivityFieldCreate,
    ) -> ActivityField:
        # Check unique (activity_id, name)
        existing = await db.execute(
            select(ActivityField).where(
                ActivityField.activity_id == activity.id,
                ActivityField.name == data.name,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Field name '{data.name}' already exists on this activity")

        field = ActivityField(
            activity_id   = activity.id,
            name          = data.name,
            label         = data.label,
            label_de      = data.label_de,
            label_pl      = data.label_pl,
            description   = data.description,
            field_type    = data.field_type,
            is_required   = data.is_required,
            display_order = data.display_order,
            options       = data.options,
            scale_config  = data.scale_config,
            unit          = data.unit,
            validation    = data.validation,
            pattern_scope = data.pattern_scope,
        )
        db.add(field)
        await db.commit()
        await db.refresh(field)
        return field

    @classmethod
    async def update_field(
        cls,
        db: AsyncSession,
        field: ActivityField,
        data: ActivityFieldUpdate,
    ) -> ActivityField:
        if data.label         is not None: field.label         = data.label
        if data.label_de      is not None: field.label_de      = data.label_de
        if data.label_pl      is not None: field.label_pl      = data.label_pl
        if data.description   is not None: field.description   = data.description
        if data.is_required   is not None: field.is_required   = data.is_required
        if data.display_order is not None: field.display_order = data.display_order
        if data.options       is not None: field.options       = data.options
        if data.scale_config  is not None: field.scale_config  = data.scale_config
        if data.unit          is not None: field.unit          = data.unit
        if data.validation    is not None: field.validation    = data.validation

        await db.commit()
        await db.refresh(field)
        return field

    @classmethod
    async def delete_field(cls, db: AsyncSession, field: ActivityField) -> None:
        await db.delete(field)
        await db.commit()

    # ── Seed data ─────────────────────────────────────────────────────────────

    @classmethod
    async def seed_13_questions(
        cls,
        db: AsyncSession,
        created_by: UUID,
    ) -> tuple[int, int]:
        """
        Seed the canonical '13 Fragen an den Boden' activity.
        Returns (created, skipped) count.
        Idempotent — safe to run multiple times.
        """
        SLUG = "13-fragen-an-den-boden"

        existing = await cls.get_by_slug(db, SLUG)
        if existing:
            logger.info("13 Fragen activity already exists, skipping seed")
            return 0, 1

        data = ActivityCreate(
            name          = "13 Fragen an den Boden",
            slug          = SLUG,
            description   = (
                "Die 13 Fragen an den Boden sind eine phänomenologische "
                "Beobachtungsmethode nach Goetheanistischer Tradition. "
                "Stewards beobachten den Boden durch direkte sensorische "
                "Wahrnehmung, bevor sie zu Interpretationen übergehen."
            ),
            scope         = ActivityScope.living_lab,
            proxemic_zone = ProxemicZone.social,
            is_template   = True,
            fields        = _THIRTEEN_QUESTIONS_FIELDS,
        )

        await cls.create(db, data, created_by=created_by)
        logger.info("Seeded 13 Fragen an den Boden activity")
        return 1, 0


# ── Seed field definitions ────────────────────────────────────────────────────
# Based on the canonical 13 Questions to the Soil methodology.
# Each field has trilingual labels (EN canonical, DE primary, PL).
# All fields are text type — phenomenological observation resists
# forced categorisation. qualitative_notes on the observation itself
# carries the steward's holistic reflection.

_THIRTEEN_QUESTIONS_FIELDS: list[ActivityFieldCreate] = [
    ActivityFieldCreate(
        name          = "q01_colour",
        label         = "What colour is the soil?",
        label_de      = "Welche Farbe hat der Boden?",
        label_pl      = "Jaki kolor ma gleba?",
        description   = "Describe the colour(s) you observe. Use your own words.",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 1,
    ),
    ActivityFieldCreate(
        name          = "q02_smell",
        label         = "What does the soil smell like?",
        label_de      = "Wie riecht der Boden?",
        label_pl      = "Jak pachnie gleba?",
        description   = "Describe the smell directly. Earth, mould, sweetness, nothing?",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 2,
    ),
    ActivityFieldCreate(
        name          = "q03_texture",
        label         = "What is the texture of the soil?",
        label_de      = "Wie fühlt sich der Boden an?",
        label_pl      = "Jaka jest struktura gleby?",
        description   = "Rub a small amount between your fingers. Sandy, silty, clayey, crumbly?",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 3,
    ),
    ActivityFieldCreate(
        name          = "q04_life",
        label         = "What life is visible in the soil?",
        label_de      = "Welches Leben ist im Boden sichtbar?",
        label_pl      = "Jakie życie jest widoczne w glebie?",
        description   = "Worms, insects, fungi, roots — what do you actually see?",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 4,
    ),
    ActivityFieldCreate(
        name          = "q05_structure",
        label         = "How does the soil hold together?",
        label_de      = "Wie hält der Boden zusammen?",
        label_pl      = "Jak trzyma się gleba?",
        description   = "Does it crumble, clump, compact? Describe what you observe.",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 5,
    ),
    ActivityFieldCreate(
        name          = "q06_moisture",
        label         = "Is the soil moist or dry?",
        label_de      = "Ist der Boden feucht oder trocken?",
        label_pl      = "Czy gleba jest wilgotna czy sucha?",
        description   = "Describe the moisture you feel. Very dry, moist, wet, waterlogged?",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 6,
    ),
    ActivityFieldCreate(
        name          = "q07_plants",
        label         = "What plants grow here?",
        label_de      = "Welche Pflanzen wachsen hier?",
        label_pl      = "Jakie rośliny tu rosną?",
        description   = "Name or describe the plants you can identify around the observation point.",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 7,
    ),
    ActivityFieldCreate(
        name          = "q08_roots",
        label         = "Are there roots visible?",
        label_de      = "Gibt es Wurzeln zu sehen?",
        label_pl      = "Czy widoczne są korzenie?",
        description   = "Describe what you see — depth, density, thickness, type.",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 8,
    ),
    ActivityFieldCreate(
        name          = "q09_humus_depth",
        label         = "How deep is the humus layer?",
        label_de      = "Wie tief ist die Humusschicht?",
        label_pl      = "Jak głęboka jest warstwa próchnicy?",
        description   = "Estimate the depth of the dark organic layer. Use centimetres or a descriptive term.",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 9,
    ),
    ActivityFieldCreate(
        name          = "q10_stones",
        label         = "Are there stones in the soil?",
        label_de      = "Gibt es Steine im Boden?",
        label_pl      = "Czy w glebie są kamienie?",
        description   = "Describe size, quantity, and type if identifiable.",
        field_type    = FieldType.text,
        is_required   = False,
        display_order = 10,
    ),
    ActivityFieldCreate(
        name          = "q11_water_reaction",
        label         = "How does the soil react to water?",
        label_de      = "Wie reagiert der Boden auf Wasser?",
        label_pl      = "Jak gleba reaguje na wodę?",
        description   = "Add a few drops. Does it absorb quickly, bead up, run off, or form a crust?",
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 11,
    ),
    ActivityFieldCreate(
        name          = "q12_story",
        label         = "What story does the soil tell?",
        label_de      = "Welche Geschichte erzählt der Boden?",
        label_pl      = "Jaką historię opowiada gleba?",
        description   = (
            "Reflect on what the soil reveals about its past and present. "
            "What has happened here? What is happening now?"
        ),
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 12,
    ),
    ActivityFieldCreate(
        name          = "q13_connection",
        label         = "How does the soil connect us?",
        label_de      = "Wie verbindet uns der Boden?",
        label_pl      = "Jak gleba nas łączy?",
        description   = (
            "The final question is relational and reflective. "
            "How do you experience the soil as a commons — connecting people, "
            "place, and the living community?"
        ),
        field_type    = FieldType.text,
        is_required   = True,
        display_order = 13,
    ),
]
