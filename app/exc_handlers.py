from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import *


async def handle_invalid_file(_request: Request, exc: InvalidFileError):
    return _make_response(415, exc.details)


async def handle_not_found(_request: Request, exc: NotFoundError):
    return _make_response(404, exc.details)


async def http_exception_handler(_request, exc: StarletteHTTPException):
    return _make_response(exc.status_code, exc.detail)


def _make_response(code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=code,
                        content={'message': detail})
