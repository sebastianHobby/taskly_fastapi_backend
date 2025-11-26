from http import HTTPStatus


class TasklyServiceException(Exception):
    def __init__(self, status: HTTPStatus, message):
        self.status = status
        self.message = message


class TasklyDataNotFound(TasklyServiceException):
    def __init__(self, id):
        super().__init__(
            HTTPStatus.NOT_FOUND, message=f"Resource not found for id '{id}'"
        )


class TasklyDuplicateData(TasklyServiceException):
    def __init__(self, message):
        super().__init__(status=HTTPStatus.CONFLICT, message=message)
