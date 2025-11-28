import http
from typing import Any, Union

import httpx

from app.core_layer.exceptions import TasklyBaseException


class TasklyServiceException(TasklyBaseException):
    """
    Custom service application exception for standardized error handling.
    Inherits from Taskly base exception which has a global handler registered with
    FastApi for consistent processing.
    This child class can be extended or adapted to give extra service specific info
    Alternatively it can just make it easier to trace errors based on name
    """

    pass


class TasklyServiceValidationError(TasklyServiceException):
    def __init__(self, message):
        self.message = message
        super().__init__(
            error_message=self.message,
            status_code=http.HTTPStatus.UNPROCESSABLE_CONTENT,
        )
