import os
from typing import Annotated
from uuid import UUID
from uuid import uuid4

from fastapi import Depends

from app.event_handlers import handle
from app.exceptions import NotFoundError
from app.logger import mining_logger
from app.mappers.events import to_mining_event
from app.utils.mining_vsource import MiningAreaVectorSource
from common.enums import MiningAreaType
from common.schemas import RasterCreationAttrs
from dal.events import EventType
from dal.models import MiningArea, MiningSource
from dal.uow import *


class MiningAreaService:
    def __init__(self, uow: Annotated[PostgisUow, Depends(get_uow)]):
        self.uow = uow
        self.mining_repo: MiningAreaRepository = uow.mining
        self.reproject_repo: ReprojectRuleRepository = uow.reproject

    def validate_file(self, path: str) -> MiningAreaVectorSource:
        source = MiningAreaVectorSource.read_file(path, attrs=['geometry', 'Layer'])
        source.validate()

        return source

    async def add_file_source(self, filename, rr_id: UUID) -> MiningSource:
        model = self._make_file_source(filename, rr_id)
        async with self.uow:
            if not await self.reproject_repo.get_by_id(rr_id):
                raise NotFoundError(details=f'No reprojection rule for id: {rr_id}')
            await self.mining_repo.delete_source(rr_id)
            file_source = await self.mining_repo.save_source(model)
            await self.uow.commit()
        return file_source

    async def upload_areas(self, source_id: int, source: MiningAreaVectorSource, rr_id: UUID):
        mining_logger.info('Start mining source processing..')
        source.filter_triangles()
        areas: list[MiningArea] = []
        async with self.uow:
            reproject_rule = await self.reproject_repo.get_by_id(rr_id)
            source.transform((reproject_rule.x, reproject_rule.y))
            mining_logger.info('Transformation done')

            for layer in source.get_layers():
                type_, *name = layer.split('_', maxsplit=1)
                name = name[0] if name else None
                geom = source.get_2d_polygon_from_layer(layer)
                points = source.get_points_from_layer(layer)
                algorithm = f'invdistnn:max_points=3:nodata={-100_000 if type_ == MiningAreaType.YAMA else 200_000}'

                raster_attrs = self._make_raster_attrs(geom, points, algorithm, resolution=0.0001, srs=4326)
                mining_area = self._make_model(name, type_, geom, source_id)

                mining_area = await self.mining_repo.save(mining_area, raster_attrs)
                areas.append(mining_area)
                mining_logger.info(f'Processed {mining_area.name} area')
            await handle(to_mining_event(uuid4(), areas, rr_id, EventType.CREATED), self.uow)
            await self.uow.commit()

        os.remove(source.path)
        mining_logger.info('Done')

    def _make_model(self, name, type_, geom, source_id):
        return MiningArea(
            name=name,
            type=type_,
            geom=geom.wkt,
            source_id=source_id
        )

    def _make_file_source(self, name: str, rr_id: UUID):
        return MiningSource(
            name=name,
            rr_id=rr_id
        )

    def _make_raster_attrs(self, extent, points, algorithm: str, resolution: float, srs: int) -> RasterCreationAttrs:
        minx, miny, maxx, maxy = extent.bounds
        return RasterCreationAttrs(
            point_set=points.wkt,
            algorithm=algorithm,
            minx=minx,
            miny=miny,
            maxx=maxx,
            maxy=maxy,
            resolution=resolution,
            srs=srs
        )
