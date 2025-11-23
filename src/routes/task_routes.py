from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..core.dependency_containers import Container
from ..schemas.TaskSchemas import TaskResponse, TaskCreate, TaskUpdate
from fastapi import APIRouter, Depends, status

from ..services.task_service import TaskService

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=list[TaskResponse]
)
@inject
async def get_all_tasks(
    task_service: Annotated[TaskService, Depends(Provide[Container.task_service])],
):
    task_and_groups = await task_service.get_multiple()
    return task_and_groups


@task_router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
)
@inject
async def get_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_service])],
) -> TaskResponse:
    task_list = await task_service.get_task(task_id=task_id)
    return task_list


@task_router.post("/", response_model=TaskResponse)
@inject
async def create_task(
    create_schema: TaskCreate,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_service])],
):
    task = await task_service.create_task(create_schema=create_schema)
    return task


@task_router.put("/", response_model=TaskResponse)
@inject
async def update_task(
    update_schema: TaskUpdate,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_service])],
):
    task_list = await task_service.update_task(update_schema=update_schema)
    return task_list


@task_router.delete("/{task_id}")
@inject
async def delete_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(Provide[Container.task_service])],
):
    task_list = await task_service.delete_task(task_id=task_id)
    return None
