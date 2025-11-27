from typing import Any, Union


class TasklyBaseException(Exception):
    """
    Custom application exception for standardized error handling.

    Attributes:
        error_message (str): Description of the error.
        error (Any, optional): Additional error details (e.g., stack trace, validation issues).
        status_code (int): HTTP status code associated with this error (default is 500).
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
        self.status_code = status_code
        self.error_message = error_message
        self.error = error
        super().__init__(self.error_message)

    def __str__(self) -> str:
        """
        Return a string representation of the error message.

        Returns:
            str: A formatted string containing the error code and message.
        """
        return (
            f"TasklyBaseException(status_code={self.status_code}, "
            f"message='{self.error_message}', "
            f"error={self.error})"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the TasklyBaseException instance.
        Returns:
            str: A string representation of the TasklyBaseException instance.
        """
        return f"TasklyBaseException(error_message={self.error_message}, status_code={self.status_code}, error={self.error})"

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
