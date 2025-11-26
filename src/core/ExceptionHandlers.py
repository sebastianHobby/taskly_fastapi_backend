from urllib.request import Request
from fastapi import HTTPException, FastAPI
from src.core.exceptions import (
    TasklyServiceException,
    TasklyDuplicateData,
    TasklyDataNotFound,
)


def init_exception_handlers(app: FastAPI):
    # Todo find a better way to handle this
    @app.exception_handler(TasklyServiceException)
    async def handle_taskly_service_exception(
        request: Request, exc: TasklyServiceException
    ):
        raise HTTPException(status_code=exc.status, detail=exc.message)

    @app.exception_handler(TasklyDataNotFound)
    async def handle_taskly_service_exception(
        request: Request, exc: TasklyServiceException
    ):
        raise HTTPException(status_code=exc.status, detail=exc.message)

    @app.exception_handler(TasklyDuplicateData)
    async def handle_taskly_service_exception(
        request: Request, exc: TasklyServiceException
    ):
        raise HTTPException(status_code=exc.status, detail=exc.message)
