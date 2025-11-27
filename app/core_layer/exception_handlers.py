# exception_handler.py

import logging
from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from .exceptions import TasklyBaseException

logger = logging.getLogger(__name__)


def generate_error_response(
    status_code: int, error_code: int, message: str, error: Any = None
):
    return JSONResponse(
        status_code=status_code,
        content={"status_code": error_code, "message": message, "error": error},
    )


# 1. Handle standard HTTPExceptions
def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {exc.detail}")
    return generate_error_response(
        status_code=exc.status_code,
        error_code=exc.status_code,
        message="HTTP Exception",
        error=exc.detail,
    )


# 2. Handle validation errors
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation Error", exc_info=exc)
    errors = exc.errors
    return generate_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation Error",
        error=errors,
    )


# 3. Handle our custom TasklyBaseExceptions
def app_exception_handler(request: Request, exc: TasklyBaseException):
    logger.error(f"TasklyBaseException: {exc}")
    return generate_error_response(
        status_code=exc.status_code,
        error_code="Fixme",
        message=exc.error_message,
        error=exc.error,
    )


# 4. Handle generic unhandled exceptions
def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled Exception")
    return generate_error_response(
        status_code=500, error_code=500, message="Internal Server Error", error=str(exc)
    )
