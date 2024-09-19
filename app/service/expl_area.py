import os
from datetime import timedelta
from uuid import uuid4

from fastapi import Depends

from app.event_handlers import handle
from app.exceptions import *
from app.mappers.events import to_explosion_event
from app.schemas.expl_areas import *
from app.utils.geom import *
from dal.events import EventType
from dal.models import ExplosionArea
from dal.uow import *


class ExplosionAreaService:
    def __init__(self, uow: Annotated[PostgisUow, Depends(get_uow)]):
        self.uow = uow
        self.explosion_repo: ExplosionAreaRepository = self.uow.explosion
        self.reproject_repo: ReprojectRuleRepository = self.uow.reproject

    async def add_expl_area(self, path: str, schema: CreateExplosionArea, reproject_id: UUID) -> ExplosionArea:
        shape = read_polygon_from_file(path)
        async with self.uow:
            geom_shift = await self.reproject_repo.get_by_id(reproject_id)
            if not geom_shift:
                raise NotFoundError(details=f'No reprojection rule found for id: {reproject_id}')
            shape = translate(shape, {'x': geom_shift.x, 'y': geom_shift.y})
            staff_danger_area = make_buffer(shape, schema.staff_danger_radius)
            vehicle_danger_area = make_buffer(shape, schema.vehicle_danger_radius)

            shape, staff_danger_area, vehicle_danger_area = map(reproject, [shape,
                                                                            staff_danger_area,
                                                                            vehicle_danger_area])
            active_to = schema.works_started_at + timedelta(minutes=30)

            model = self._make_model(schema, path, shape, staff_danger_area, vehicle_danger_area, active_to,
                                     reproject_id)
            model = await self.explosion_repo.save(model)

            await handle(to_explosion_event(uuid4(), model, reproject_id, EventType.CREATED), self.uow)
            await self.uow.commit()
        os.remove(path)
        return model

    def _make_model(self, schema: CreateExplosionArea,
                    filename: str,
                    area, staff_danger_area,
                    vehicle_danger_area,
                    active_to: datetime,
                    rr_id: UUID):
        return ExplosionArea(
            name=schema.name,
            geom=area.wkt,
            staff_danger_area=staff_danger_area.wkt,
            vehicle_danger_area=vehicle_danger_area.wkt,
            active_from=schema.works_started_at,
            active_to=active_to,
            vehicle_name=schema.vehicle_name,
            filename=filename,
            rr_id=rr_id
        )
