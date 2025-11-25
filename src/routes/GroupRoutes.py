from typing import Annotated, Literal
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field

from .utils import generate_multi_get_description
from ..core.DependencyContainers import Container
from ..schemas.GroupSchemas import (
    GroupSelect,
    GroupUpdate,
    GroupCreate,
)
from ..schemas.QueryParamHelper import GroupQueryParams

group_router = APIRouter(prefix="/groups", tags=["Groups"])
group_service = Provide[Container.group_service]


@group_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=GroupSelect
)
async def get(id: UUID):
    return await group_service.get(_id=id)


@group_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupSelect],
    description=(generate_multi_get_description(model_name="Group")),
)
async def get_multi(filter_query: Annotated[GroupQueryParams, Query()]):
    get_all_parameters = filter_query.model_dump(exclude_none=True, exclude_unset=True)
    res = await group_service.get_multi(**get_all_parameters)
    data = res["data"]
    cnt = res["total_count"]
    return data


@group_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=GroupSelect
)
async def create(create_schema: GroupCreate):
    res = await group_service.create(create_schema=create_schema, commit=True)
    return res


@group_router.patch(
    path="/", status_code=status.HTTP_200_OK, response_model=GroupSelect
)
async def update(update_schema: GroupUpdate):
    res = await group_service.update(update_schema=update_schema, commit=True)
    return res


@group_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    res = await group_service.delete(_id=id, commit=True)
    return res
