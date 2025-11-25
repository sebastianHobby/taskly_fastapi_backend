from urllib.request import Request
from fastapi import HTTPException, FastAPI
from src.core.ServiceExceptions import (
    TasklyServiceException,
)


def init_exception_handlers(app: FastAPI):
    @app.exception_handler(TasklyServiceException)
    async def handle_taskly_service_exception(
        request: Request, exc: TasklyServiceException
    ):
        raise HTTPException(status_code=exc.status, detail=exc.message)
