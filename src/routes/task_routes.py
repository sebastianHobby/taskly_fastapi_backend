from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from ..repositories.TaskRepository import TaskRepository
from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
)

from ..repositories.TaskRepository import *
from ..schemas.TaskSchemas import *

task_router = APIRouter()


@task_router.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskGet])
def get_tasks(task_repository=Depends(TaskRepository)):
    task_get_schemas = task_repository.get_all()
    return task_get_schemas


@task_router.get(
    "/tasks/{task_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=TaskGet,
)
def get_task(task_uuid: UUID, task_repository=Depends(TaskRepository)):
    try:
        return task_repository.get_one_by_uuid(uuid=task_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="task not found")


@task_router.post("/tasks", response_model=TaskGet)
def create_task(create_schema: TaskCreate, task_repository=Depends(TaskRepository)):
    # Check foreign key for task is valid if provided. Raises 404 error if not found
    try:
        return task_repository.create(create_schema=create_schema)
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )


@task_router.put("/tasks", response_model=TaskGet)
def update_task(update_schema: TaskUpdate, task_repository=Depends(TaskRepository)):
    try:
        return task_repository.update(
            update_schema=update_schema, uuid=update_schema.uuid
        )
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="task not found")


@task_router.delete("/tasks/{task_uuid}")
async def delete_task(task_uuid: UUID, task_repository=Depends(TaskRepository)):
    try:
        return task_repository.delete(uuid=task_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="task not found")
