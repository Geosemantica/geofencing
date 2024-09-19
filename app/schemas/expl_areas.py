from datetime import datetime
from typing import Optional, Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.types import wkt


class ExplosionAreaSchema(BaseSchema):
    id: UUID
    filename: str
    name: str
    vehicle_name: Optional[str] = None
    works_started_at: datetime = Field(validation_alias='active_from')
    works_finished_at: datetime = Field(validation_alias='active_to')
    geom: wkt
    vehicle_danger_area: wkt
    staff_danger_area: wkt


class CreateExplosionArea(BaseSchema):
    name: str
    vehicle_name: Optional[str] = None
    works_started_at: datetime
    vehicle_danger_radius: float
    staff_danger_radius: float


class ChangeExplosionAreaBody(BaseSchema):
    name: Annotated[Optional[str], Field(min_length=1, max_length=256, pattern=r'\w+')] = None
    vehicle_name: Annotated[Optional[str], Field(min_length=1, max_length=256, pattern=r'\w+')] = None
    works_started_at: Optional[datetime] = None
    vehicle_danger_radius: Annotated[Optional[float], Field(gt=0, le=2000)] = None
    staff_danger_radius: Annotated[Optional[float], Field(gt=0, le=2000)] = None
