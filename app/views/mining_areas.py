from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks

from app.schemas.mining_areas import MiningSourceSchema
from app.service.mining_area import MiningAreaService
from app.service.utils import upload_file

mining_router = APIRouter(prefix='/mining-areas')


@mining_router.put('/', status_code=202, response_model=MiningSourceSchema)
async def upload_mining_areas(pitid: UUID,
                              file: UploadFile,
                              svc: Annotated[MiningAreaService, Depends()],
                              tasks: BackgroundTasks):
    await upload_file(file, file.filename)
    vector_source = svc.validate_file(file.filename)

    file_meta = await svc.add_file_source(file.filename, pitid)
    tasks.add_task(svc.upload_areas, file_meta.id, vector_source, pitid)

    return file_meta
