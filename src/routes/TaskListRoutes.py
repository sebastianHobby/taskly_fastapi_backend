from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, status, Query
from fastcrud import FilterConfig
from fastcrud.fastapi_dependencies import create_dynamic_filters
from pydantic import BaseModel, Field

from .utils import generate_multi_get_description
from ..core.DependencyContainers import Container
from ..schemas.ListSchemas import (
    TasklistSelect,
    TasklistUpdate,
    TasklistCreate,
)
from ..schemas.QueryParamHelper import TasklistQueryParams


class ListFilterQueryParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"


tasklist_router = APIRouter(prefix="/lists", tags=["Lists"])
# noinspection DuplicatedCode
tasklist_service = Provide[Container.list_service]


@tasklist_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TasklistSelect
)
async def get(id: UUID):
    return await tasklist_service.get(_id=id)


@tasklist_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[TasklistSelect],
    description=(generate_multi_get_description(model_name="Group")),
)
async def get_multi(filter_query: Annotated[TasklistQueryParams, Query()]):
    get_all_parameters = filter_query.model_dump(exclude_none=True, exclude_unset=True)
    res = await tasklist_service.get_multi(**get_all_parameters)
    data = res["data"]
    cnt = res["total_count"]
    return data


@tasklist_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=TasklistSelect
)
async def create(create_schema: TasklistCreate):
    res = await tasklist_service.create(create_schema=create_schema, commit=True)
    return res


@tasklist_router.patch(
    path="/", status_code=status.HTTP_200_OK, response_model=TasklistSelect
)
async def update(update_schema: TasklistUpdate):
    res = await tasklist_service.update(update_schema=update_schema, commit=True)
    return res


@tasklist_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    res = await tasklist_service.delete(_id=id, commit=True)
    return res
