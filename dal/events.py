from datetime import datetime
from enum import StrEnum
from typing import Literal, Annotated, Optional
from uuid import UUID

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, BeforeValidator, model_validator
from pydantic.alias_generators import to_camel


class EventType(StrEnum):
    CREATED = 'CREATED'
    CHANGED = 'CHANGED'
    DELETED = 'DELETED'


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel,
                              from_attributes=True,
                              populate_by_name=True)


class Event(BaseSchema):
    message_id: UUID
    event_type: EventType
    type: str


class ExplosionAreaEvent(Event):
    area_id: UUID
    type: Literal['EXPLOSION'] = 'EXPLOSION'
    attributes: Optional['ExplosionAreaAttrs'] = None
    pit_id: UUID

    @model_validator(mode='after')
    def check_model(self):
        if self.event_type in [EventType.CREATED, EventType.CHANGED] and not self.attributes:
            raise ValueError('Model must contain attributes for upsert operations')


class MiningAreaEvent(Event):
    type: Literal['MINING'] = 'MINING'
    areas: list['MiningAreaAttrs']
    pit_id: UUID


class ExplosionAreaAttrs(BaseSchema):
    id: UUID
    name: str
    active_from: datetime
    active_to: datetime
    geom: Annotated[str, BeforeValidator(lambda g: to_shape(g).wkt)]
    staff_area: Annotated[str, BeforeValidator(lambda g: to_shape(g).wkt)]
    vehicle_area: Annotated[str, BeforeValidator(lambda g: to_shape(g).wkt)]
    vehicle_name: Optional[str] = None
    created_at: datetime


class MiningAreaAttrs(BaseSchema):
    id: UUID
    name: str
    geom: Annotated[str, BeforeValidator(lambda g: to_shape(g).wkt)]
