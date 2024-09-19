from dal.events import *
from dal.models import *


def to_mining_event(message_id: UUID,
                    areas: list[MiningArea],
                    rr_id: UUID,
                    event_type: EventType = EventType.CREATED) -> MiningAreaEvent:
    return MiningAreaEvent(
        message_id=message_id,
        event_type=event_type,
        pit_id=rr_id,
        areas=[MiningAreaAttrs.model_validate(area) for area in areas]
    )


def to_explosion_event(message_id: UUID,
                       area: ExplosionArea,
                       rr_id: UUID,
                       event_type: EventType) -> ExplosionAreaEvent:
    return ExplosionAreaEvent(
        message_id=message_id,
        event_type=event_type,
        pit_id=rr_id,
        area_id=area.id,
        attributes=ExplosionAreaAttrs(**area.__dict__,
                                      staff_area=area.staff_danger_area,
                                      vehicle_area=area.vehicle_danger_area)
    )
