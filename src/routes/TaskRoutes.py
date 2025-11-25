from typing import Annotated, Literal
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field

from .utils import generate_multi_get_description
from ..core.DependencyContainers import Container
from ..schemas.QueryParamHelper import TaskQueryParams
from ..schemas.TaskSchemas import (
    TaskSelect,
    TaskUpdate,
    TaskCreate,
)


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_service = Provide[Container.task_service]


@task_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TaskSelect
)
async def get(id: UUID):
    return await task_service.get(_id=id)


@task_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskSelect],
    description=(generate_multi_get_description(model_name="Task")),
)
async def get_multi(filter_query: Annotated[TaskQueryParams, Query()]):
    get_all_parameters = filter_query.model_dump(exclude_none=True, exclude_unset=True)
    res = await task_service.get_multi(**get_all_parameters)
    data = res["data"]
    cnt = res["total_count"]
    return data


@task_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=TaskSelect
)
async def create(create_schema: TaskCreate):
    res = await task_service.create(create_schema=create_schema, commit=True)
    return res


@task_router.patch(path="/", status_code=status.HTTP_200_OK, response_model=TaskSelect)
async def update(update_schema: TaskUpdate):
    res = await task_service.update(update_schema=update_schema, commit=True)
    return res


@task_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    res = await task_service.delete(_id=id, commit=True)
    return res
