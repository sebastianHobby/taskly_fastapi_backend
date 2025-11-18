from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from ..core.database import get_database_session
from ..models.db_models import Task
from ..schemas.TaskSchemas import *
from ..repositories.AbstractServiceRepository import AbstractServiceRepository
from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
    DatabaseRepository,
)

from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..services.project_service import ProjectService
from ..services.task_service import TaskService

task_router = APIRouter(prefix="/tasks", tags=["Task"])


# Dependency functions - used for dependency injection.
def dependency_task_repository(
    session: Annotated[AbstractServiceRepository, Depends(get_database_session)],
) -> AbstractServiceRepository:
    return DatabaseRepository(
        database_model_class=Task,
        update_schema_class=TaskUpdate,
        create_schema_class=TaskCreate,
        public_schema_class=TaskGet,
        database_session=session,
    )


def dependency_task_service(
    repository: Annotated[
        AbstractServiceRepository, Depends(dependency_task_repository)
    ],
) -> TaskService:
    # Why create Database repository here instead of just having Task Service create the repository?
    # This lets us perform dependency injection later so we can override the database repository
    # with a different repository source (e.g. mock for testing) or change to different
    # Repository (e.g. switch data source to API , file etc) without impacting the
    # code using this dependency - everything depends on an abstract Repository interface
    # so long as our replacement walks,talks and quacks like a duck/Repository we can use it here
    return TaskService(repository=repository)


# Some important notes
# Error handling is all done by errors.py in root , this allows us to avoid having
# to cater for each error and map to HTTP response code in each function
@task_router.get(path="/", status_code=status.HTTP_200_OK, response_model=list[TaskGet])
def get_tasks(
    task_service: Annotated[TaskService, Depends(dependency_task_service)],
):
    return task_service.get_all()


@task_router.get(
    "/{task_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=TaskGet,
)
def get_task(
    task_uuid: UUID,
    task_service: Annotated[TaskService, Depends(dependency_task_service)],
):
    return task_service.get_one_by_uuid(uuid=task_uuid)


@task_router.post("/", response_model=TaskGet)
def create_task(
    create_schema: TaskCreate,
    task_service: Annotated[TaskService, Depends(dependency_task_service)],
):
    return task_service.create(create_schema=create_schema)


@task_router.put("/", response_model=TaskGet)
def update_task(
    update_schema: TaskUpdate,
    task_service: Annotated[TaskService, Depends(dependency_task_service)],
):
    return task_service.update(update_schema=update_schema, uuid=update_schema.uuid)


@task_router.delete("/{task_uuid}")
async def delete_task(
    task_uuid: UUID,
    task_service: Annotated[TaskService, Depends(dependency_task_service)],
):
    return task_service.delete(uuid=task_uuid)
