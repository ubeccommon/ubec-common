"""
Module: observations/models.py
Service: hub (iot.ubec.network)
Purpose: SQLAlchemy ORM models for observations and observation_responses.

PostGIS strategy: the `location` column is geography(Point, 4326).
We do NOT use geoalchemy2. Instead:
  - The column is declared as NullType() — SQLAlchemy treats it as opaque.
  - All writes use raw SQL via text() with ST_GeomFromText(WKT, 4326).
  - All reads extract lat/lng via ST_Y/ST_X in explicit select() queries.
  - The ORM `location` attribute is never written via ORM — only via raw SQL.

proxemic_zone reuses the existing PostgreSQL enum type `proxemic_zone`
already declared in the ubec_hub schema. We reference it with
create_constraint=False, schema="ubec_hub" so SQLAlchemy does not try
to CREATE TYPE again.

License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, ForeignKey, String, Text, types
from sqlalchemy.orm import relationship

from auth.database import Base
from activities.models import ProxemicZone


# Reuse the existing proxemic_zone enum — do not create a new type
_proxemic_zone_col = Enum(
    ProxemicZone,
    name="proxemic_zone",
    schema="ubec_hub",
    create_type=False,   # type already exists in DB
)


class Observation(Base):
    """
    A steward's phenomenological record of a place at a moment in time.

    Tied to an Activity (which defines the field structure), but the
    Activities module does not reference observations — the dependency
    is one-way: observations → activities.

    `qualitative_notes` is NOT NULL — enforcing the Goethean design
    constraint that every observation must include a phenomenological
    description, not just structured field responses.

    `location` is a PostGIS geography column handled via raw SQL.
    `language` is constrained to 'de', 'en', 'pl' by DB CHECK constraint.
    """

    __tablename__ = "observations"
    __table_args__ = {"schema": "ubec_hub"}

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id       = Column(UUID(as_uuid=True), nullable=False)
    steward_id        = Column(UUID(as_uuid=True), nullable=False)
    observed_at       = Column(DateTime(timezone=True), nullable=False)
    location          = Column(types.NullType(), nullable=True)   # geography — raw SQL only
    location_note     = Column(Text, nullable=True)
    proxemic_zone     = Column(_proxemic_zone_col, nullable=False)
    qualitative_notes = Column(Text, nullable=False)
    device_id         = Column(UUID(as_uuid=True), nullable=True)
    language          = Column(String(2), nullable=False, default="en")
    is_validated      = Column(Boolean, nullable=False, default=False)
    validated_by      = Column(UUID(as_uuid=True), nullable=True)
    validated_at      = Column(DateTime(timezone=True), nullable=True)
    created_at        = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at        = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    responses = relationship(
        "ObservationResponse",
        back_populates="observation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Observation {self.id} activity={self.activity_id}>"


class ObservationResponse(Base):
    """
    A single field response within an Observation.

    field_id references an ActivityField. value_text stores all field
    type values as text. value_pattern is set only for pattern_ref fields.

    DB enforces UNIQUE (observation_id, field_id) — one response per field.
    """

    __tablename__ = "observation_responses"
    __table_args__ = {"schema": "ubec_hub"}

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_id = Column(UUID(as_uuid=True), ForeignKey("ubec_hub.observations.id"), nullable=False)
    field_id       = Column(UUID(as_uuid=True), nullable=False)
    value_text     = Column(Text, nullable=True)
    value_pattern  = Column(UUID(as_uuid=True), nullable=True)
    created_at     = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    observation = relationship("Observation", back_populates="responses")

    def __repr__(self) -> str:
        return f"<ObservationResponse obs={self.observation_id} field={self.field_id}>"
