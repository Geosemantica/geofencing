import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.exc_handlers import *
from app.health import get_router
from app.tasks import run_interval_tasks
from app.views.expl_areas import expl_router
from app.views.mining_areas import mining_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(run_interval_tasks())

    yield

    scheduler_task.cancel()


app = FastAPI(title='Geofencing Service',
              description='A service that monitors the crossing of zones by subjects',
              lifespan=lifespan)

app.include_router(get_router(), prefix='/-')
app.include_router(expl_router)
app.include_router(mining_router)

app.add_exception_handler(InvalidFileError, handle_invalid_file)
app.add_exception_handler(NotFoundError, handle_not_found)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, port=8001)
