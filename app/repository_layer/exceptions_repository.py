from enum import Enum
from http import HTTPStatus
from typing import Any, Union

from app.core_layer.exceptions import TasklyBaseException


class TasklyRepositoryException(TasklyBaseException):
    """
    Custom repository application exception for standardized error handling.
    Inherits from Taskly base exception which has a global handler registered with
    FastApi for consistent processing.
    This child class can be extended or adapted to give extra repository specific info
    Alternatively it can just make it easier to trace errors based on name
    """

    pass
