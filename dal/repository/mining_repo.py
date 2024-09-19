from geoalchemy2 import Geometry
from sqlalchemy import func, delete, cast

from common.schemas import RasterCreationAttrs
from dal.models import MiningArea, MiningSource
from dal.repository.base import Repository


class MiningAreaRepository(Repository):
    __rname__ = 'mining'

    async def save(self, model: MiningArea, r_attrs: RasterCreationAttrs):
        model.rast = func.ST_InterpolateRaster(
            cast(r_attrs.point_set, Geometry(srid=4326, geometry_type='MultiPointZ')),
            r_attrs.algorithm,
            func.ST_AddBand(
                func.ST_MakeEmptyRaster(int((r_attrs.maxx - r_attrs.minx) / r_attrs.resolution),
                                        int((r_attrs.maxy - r_attrs.miny) / r_attrs.resolution),
                                        r_attrs.minx, r_attrs.maxy,
                                        r_attrs.resolution, -r_attrs.resolution,
                                        0, 0,
                                        r_attrs.srs),
                r_attrs.band_type)
        )
        self.session.add(model)
        await self.session.flush([model])
        await self.session.refresh(model)
        return model

    async def save_source(self, model: MiningSource) -> MiningSource:
        self.session.add(model)
        await self.session.flush([model])
        await self.session.refresh(model)

        return model

    async def delete_source(self, rr_id):
        stmt = delete(MiningSource).where(MiningSource.rr_id == rr_id)
        await self.session.execute(stmt)
