from enum import Enum
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

    def __init__(
        self,
        error_message: str,
        error: Union[Any, None] = None,
        status_code: int = 500,
    ):
        """
        Initialize an TasklyBaseException instance.

        Args:
            error_message (str): A human-readable message describing the error.
            error (Any, optional): Additional context or request_data about the error.
            status_code (int, optional): HTTP status code to return (default is 500).
        """
        super().__init__(error_message, error, status_code)

    def __str__(self) -> str:
        """
        Return a string representation of the error message.

        Returns:
            str: A formatted string containing the error code and message.
        """
        return (
            f"TasklyRepositoryException(status_code={self.status_code}, "
            f"message='{self.error_message}', "
            f"error={self.error})"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the TasklyBaseException instance.
        Returns:
            str: A string representation of the TasklyBaseException instance.
        """
        return f"TasklyRepositoryException(error_message={self.error_message}, status_code={self.status_code}, error={self.error})"

    def __dict__(self) -> dict:
        """
        Return a dictionary representation of the TasklyBaseException instance.

        Returns:
            dict: A dictionary containing the error code, message, and additional details.
        """
        return {
            "error_message": self.error_message,
            "error": self.error,
        }
