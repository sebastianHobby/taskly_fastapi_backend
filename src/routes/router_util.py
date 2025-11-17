from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from src import models
from src.models.TaskContainerModel import TaskContainer


def get_task_container_by_id(uuid: UUID, database: Session) -> TaskContainer:
    parentContainer = None
    if uuid is not None:
        parentContainer = (
            database.query(models.TaskContainer)
            .filter(models.TaskContainer.id == uuid)
            .first()
        )
    return parentContainer


def create_uuid_from_string(sUuid: str):
    try:
        uuid: UUID = UUID(sUuid)
        return uuid
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid UUID input"
        )
