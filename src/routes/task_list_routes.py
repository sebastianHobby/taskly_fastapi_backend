from typing import Annotated, List
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from ..core.dependency_containers import Container
from ..schemas.TaskListSchemas import TaskListResponse, TaskListCreate, TaskListUpdate
from fastapi import APIRouter, Depends, status

from ..services.service_schemas import TaskListAndListGroups
from ..services.task_list_service import TaskListService

task_lists_router = APIRouter(prefix="/lists", tags=["Lists and Groups"])


@task_lists_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=TaskListAndListGroups
)
@inject
async def get_all_task_lists_and_groups(
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_lists_and_groups = await task_list_service.get_multiple()
    return task_lists_and_groups


@task_lists_router.get(
    "/{task_list_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskListResponse,
)
@inject
async def get_task_list(
    task_list_id: UUID,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
) -> TaskListResponse:
    task_list = await task_list_service.get_task_list_by_id(list_id=task_list_id)
    return task_list


@task_lists_router.post("/", response_model=TaskListResponse)
@inject
async def create_task_list(
    create_schema: TaskListCreate,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.create_task_list(create_schema=create_schema)
    return task_list


@task_lists_router.put("/", response_model=TaskListResponse)
@inject
async def update_task_list(
    update_schema: TaskListUpdate,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.update_task_list(update_schema=update_schema)
    return task_list


@task_lists_router.delete("/{task_list_id}")
@inject
async def delete_task_list(
    task_list_id: UUID,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.delete_task_list(task_list_id=task_list_id)
    return None
