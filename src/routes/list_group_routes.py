from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from ..core.dependency_containers import Container
from ..schemas.ListGroupSchemas import (
    ListGroupResponse,
    ListGroupUpdate,
    ListGroupCreate,
)
from ..services.service_schemas import TaskListAndListGroups
from ..services.task_list_service import TaskListService

list_group_router = APIRouter(prefix="/groups", tags=["Lists and Groups"])


@list_group_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=TaskListAndListGroups
)
@inject
async def get_all_task_lists_and_groups(
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_lists_and_groups = await task_list_service.get_all()
    return task_lists_and_groups


@list_group_router.get(
    "/{list_group_id}",
    status_code=status.HTTP_200_OK,
    response_model=ListGroupResponse,
)
@inject
async def get_list_group_by_id(
    list_group_id: UUID,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
) -> ListGroupResponse:
    list_group = await task_list_service.get_list_group_by_id(group_id=list_group_id)
    return list_group


@list_group_router.delete(
    "/{list_group_id}",
    status_code=status.HTTP_200_OK,
    response_model=ListGroupResponse,
)
@inject
async def delete_list_group(
    list_group_id: UUID,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.delete_list_group(list_group_id=list_group_id)
    return None


@list_group_router.put("/", response_model=ListGroupResponse)
@inject
async def update_list_group(
    update_schema: ListGroupUpdate,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.update_list_group(update_schema=update_schema)
    return task_list


@list_group_router.post("/", response_model=ListGroupResponse)
@inject
async def create_list_group(
    create_schema: ListGroupCreate,
    task_list_service: Annotated[
        TaskListService, Depends(Provide[Container.task_list_service])
    ],
):
    task_list = await task_list_service.create_list_group(create_schema=create_schema)
    return task_list
