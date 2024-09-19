from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.schemas.expl_areas import *
from app.service.expl_area import ExplosionAreaService
from app.service.utils import upload_file

expl_router = APIRouter(prefix='/explosion-areas')


@expl_router.post('/', status_code=201, response_model=ExplosionAreaSchema)
async def add_expl_area(pitid: UUID,
                        file: Annotated[UploadFile, File()],
                        name: Annotated[str, Form(min_length=1, max_length=256, pattern=r'\w+')],
                        works_started_at: Annotated[datetime, Form(alias='worksStartedAt')],
                        vehicle_danger_radius: Annotated[float, Form(gt=0, le=2000, alias='vehicleDangerRadius')],
                        staff_danger_radius: Annotated[float, Form(gt=0, le=2000, alias='staffDangerRadius')],
                        svc: Annotated[ExplosionAreaService, Depends()],
                        vehicle_name: Annotated[Optional[str], Form(min_length=1, max_length=256, pattern=r'\w+',
                                                                    alias='vehicleName')] = None):
    await upload_file(file, file.filename)
    schema = CreateExplosionArea(
        name=name,
        works_started_at=works_started_at,
        vehicle_danger_radius=vehicle_danger_radius,
        staff_danger_radius=staff_danger_radius,
        vehicle_name=vehicle_name
    )
    return await svc.add_expl_area(file.filename, schema, pitid)
