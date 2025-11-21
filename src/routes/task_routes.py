from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..core.dependency_containers import Container
from ..repositories.AbstractRepository import AbstractServiceRepository
from ..schemas.TaskSchemas import TaskGet, TaskCreate, TaskUpdate
from ..services.task_service import TaskService
from fastapi import APIRouter, Depends, Response, status

task_router = APIRouter(prefix="/tasks", tags=["Task"])


@task_router.get(path="/", status_code=status.HTTP_200_OK, response_model=list[TaskGet])
@inject
async def get_tasks(
    task_service: Annotated[TaskService, Depends(Provide[Container.task_repository])],
):

    list = await task_service.get_all()
    return list


@task_router.get(
    "/{task_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=TaskGet,
)
@inject
async def get_task(
    task_uuid: UUID,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_repository])],
):
    task = await task_service.get_one_by_uuid(uuid=task_uuid)
    return task


@task_router.post("/", response_model=TaskGet)
@inject
async def create_task(
    create_schema: TaskCreate,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_repository])],
):
    task = await task_service.create(create_schema=create_schema)
    return task


@task_router.put("/", response_model=TaskGet)
@inject
async def update_task(
    update_schema: TaskUpdate,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_repository])],
):
    task = await task_service.update(update_schema=update_schema)
    return task


@task_router.delete("/{task_uuid}")
@inject
async def delete_task(
    task_uuid: UUID,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_repository])],
):
    task_service.delete(uuid=task_uuid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
