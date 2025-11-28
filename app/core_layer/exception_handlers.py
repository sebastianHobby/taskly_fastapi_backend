# exception_handler.py

import logging
from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from .exceptions import TasklyBaseException
from ..service_layer.service_exceptions import TasklyServiceValidationError

logger = logging.getLogger(__name__)


# Todo rebuild error handling - design it with clear seperation and handling


# 2. Handle validation errors
def app_specific_exception_handler(request: Request, exc: TasklyServiceValidationError):
    logger.warning("Validation Error", exc_info=exc)
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.message
    )
