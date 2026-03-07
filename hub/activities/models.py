"""
Module: activities/models.py
Service: hub (iot.ubec.network)
Purpose: SQLAlchemy ORM models for activities and activity_fields tables.
         Column names and types match the verified schema exactly.
         Enum values match the PostgreSQL enum types in ubec_hub schema.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    UUID, Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, SmallInteger, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from auth.database import Base


# ── Enums — values must match PostgreSQL enum types exactly ──────────────────

class ActivityScope(str, enum.Enum):
    personal    = "personal"
    living_lab  = "living_lab"
    watershed   = "watershed"
    bioregional = "bioregional"
    network     = "network"


class ProxemicZone(str, enum.Enum):
    intimate = "intimate"
    personal = "personal"
    social   = "social"
    public   = "public"


class FieldType(str, enum.Enum):
    text        = "text"
    integer     = "integer"
    decimal     = "decimal"
    boolean     = "boolean"
    date        = "date"
    datetime    = "datetime"
    select      = "select"
    multiselect = "multiselect"
    scale       = "scale"
    geo_point   = "geo_point"
    image_ref   = "image_ref"
    pattern_ref = "pattern_ref"


# ── Models ────────────────────────────────────────────────────────────────────

class Activity(Base):
    """
    An Activity defines a structured template for steward engagement.
    Activities have a scope (personal → network) and a proxemic zone
    governing data visibility. They carry optional spatial context
    (living_lab, watershed, bioregion) and a set of typed fields.

    Not all activities involve observations — some are purely
    organisational or governance structures.
    """

    __tablename__ = "activities"
    __table_args__ = {"schema": "ubec_hub"}

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(255), nullable=False)
    slug         = Column(String(100), nullable=False, unique=True)
    description  = Column(Text, nullable=True)
    scope        = Column(
        Enum(ActivityScope, name="activity_scope", schema="ubec_hub"),
        nullable=False, default=ActivityScope.personal,
    )
    living_lab_id  = Column(UUID(as_uuid=True), nullable=True)
    watershed_id   = Column(UUID(as_uuid=True), nullable=True)
    bioregion_id   = Column(UUID(as_uuid=True), nullable=True)
    created_by     = Column(UUID(as_uuid=True), ForeignKey("ubec_hub.stewards.id"), nullable=False)
    proxemic_zone  = Column(
        Enum(ProxemicZone, name="proxemic_zone", schema="ubec_hub"),
        nullable=False, default=ProxemicZone.personal,
    )
    starts_at    = Column(DateTime(timezone=True), nullable=True)
    ends_at      = Column(DateTime(timezone=True), nullable=True)
    is_active    = Column(Boolean, nullable=False, default=True)
    is_template  = Column(Boolean, nullable=False, default=False)
    pattern_id   = Column(UUID(as_uuid=True), nullable=True)
    extra_data   = Column("metadata", JSONB, nullable=False, default=dict)
    created_at   = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at   = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    fields   = relationship(
        "ActivityField",
        back_populates="activity",
        cascade="all, delete-orphan",
        order_by="ActivityField.display_order",
    )
    creator  = relationship("Steward", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<Activity {self.slug}>"


class ActivityField(Base):
    """
    A typed field definition belonging to an Activity.
    Fields are ordered by display_order. The field_type enum determines
    how value_text in observation_responses is interpreted.

    label is the canonical (English) label.
    label_de and label_pl provide localised labels for DE and PL stewards.
    options (JSONB) holds choices for select/multiselect fields.
    scale_config (JSONB) holds min/max/step for scale fields.
    validation (JSONB) holds optional validation rules.
    """

    __tablename__ = "activity_fields"
    __table_args__ = {"schema": "ubec_hub"}

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id   = Column(UUID(as_uuid=True), ForeignKey("ubec_hub.activities.id"), nullable=False)
    name          = Column(String(100), nullable=False)
    label         = Column(String(255), nullable=False)
    label_de      = Column(String(255), nullable=True)
    label_pl      = Column(String(255), nullable=True)
    description   = Column(Text, nullable=True)
    field_type    = Column(
        Enum(FieldType, name="field_type", schema="ubec_hub"),
        nullable=False,
    )
    is_required   = Column(Boolean, nullable=False, default=False)
    display_order = Column(SmallInteger, nullable=False, default=0)
    options       = Column(JSONB, nullable=True)
    scale_config  = Column(JSONB, nullable=True)
    unit          = Column(String(50), nullable=True)
    validation    = Column(JSONB, nullable=True)
    pattern_scope = Column(UUID(as_uuid=True), nullable=True)
    created_at    = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relations
    activity = relationship("Activity", back_populates="fields")

    def __repr__(self) -> str:
        return f"<ActivityField {self.activity_id}/{self.name}>"
