import enum
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from geoalchemy2 import Geometry, Raster
from sqlalchemy import TIMESTAMP, Enum, Table, Column, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from common.enums import VehicleWorkType, SubjectType


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        enum.Enum: Enum(enum.Enum, native_enum=False)
    }


explosion_to_subjects = Table(
    "explosion_to_subjects",
    Base.metadata,
    Column('explosion_area_id', ForeignKey('explosion_areas.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)

mining_to_subjects = Table(
    "mining_to_subjects",
    Base.metadata,
    Column('mining_area_id', ForeignKey('mining_areas.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)

pdz_to_subjects = Table(
    "pdz_to_subjects",
    Base.metadata,
    Column('pdz_area_id', ForeignKey('pdz_areas.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)


class ExplosionArea(Base):
    __tablename__ = 'explosion_areas'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    filename: Mapped[str]
    geom = mapped_column(Geometry(geometry_type='Polygon', srid=4326, spatial_index=True, nullable=False))
    vehicle_name: Mapped[Optional[str]]
    active_from: Mapped[datetime]
    active_to: Mapped[datetime]
    staff_danger_area = mapped_column(Geometry(geometry_type='Polygon', srid=4326, spatial_index=True, nullable=False))
    vehicle_danger_area = mapped_column(
        Geometry(geometry_type='Polygon', srid=4326, spatial_index=True, nullable=False))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    rr_id: Mapped[UUID] = mapped_column(ForeignKey('reproject_rules.id'))

    subjects: Mapped[list['Subject']] = relationship(secondary=explosion_to_subjects, back_populates='explosion_areas')


class MiningSource(Base):
    __tablename__ = 'mining_area_sources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    rr_id: Mapped[UUID] = mapped_column(ForeignKey('reproject_rules.id'))


class MiningArea(Base):
    __tablename__ = 'mining_areas'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    geom = mapped_column(Geometry(geometry_type='MultiPolygon', srid=4326, spatial_index=True, nullable=False))
    rast = mapped_column(Raster(spatial_index=True, nullable=False), deferred=True)
    type: Mapped[str]
    source_id: Mapped[int] = mapped_column(ForeignKey('mining_area_sources.id', ondelete='CASCADE'))

    subjects: Mapped[list['Subject']] = relationship(secondary=mining_to_subjects, back_populates='mining_areas')


class PdzArea(Base):
    __tablename__ = 'pdz_areas'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    geom = mapped_column(Geometry(geometry_type='Point', srid=4326, spatial_index=True, nullable=False))

    subjects: Mapped[list['Subject']] = relationship(secondary=pdz_to_subjects, back_populates='pdz_areas')


class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[SubjectType]
    work_status: Mapped[Optional[VehicleWorkType]]
    geom = mapped_column(Geometry(geometry_type='Point', srid=4326, spatial_index=False))
    geolocated_at: Mapped[datetime]

    explosion_areas: Mapped[list[ExplosionArea]] = relationship(secondary=explosion_to_subjects,
                                                                back_populates='subjects')
    mining_areas: Mapped[list[MiningArea]] = relationship(secondary=mining_to_subjects,
                                                          back_populates='subjects')
    pdz_areas: Mapped[list[PdzArea]] = relationship(secondary=pdz_to_subjects,
                                                    back_populates='subjects')


class ReprojectRule(Base):
    __tablename__ = 'reproject_rules'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    x: Mapped[float]
    y: Mapped[float]


class Outbox(Base):
    __tablename__ = 'outbox'

    message_id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(tz=timezone.utc))
    body: Mapped[str]


class Metadata(Base):
    __tablename__ = 'metadata'

    processed_at: Mapped[datetime] = mapped_column(primary_key=True)
