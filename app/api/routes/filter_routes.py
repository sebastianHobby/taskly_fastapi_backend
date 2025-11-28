from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, status, Query

from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.service_layer.taskfilter_service import FilterService
from app.service_layer.schemas.taskfilter_schemas import (
    TaskFilterResponse,
    TaskFilterUpdate,
    TaskFilterCreate,
)
from .utils import generate_multi_get_description
from ...service_layer.schemas.common_field_search_schema import CommonSearchFieldsSchema

filter_router = APIRouter(prefix="/filters", tags=["Taskfilters"])
# noinspection DuplicatedCode
filter_service: FilterService = Provide[TasklyDependencyContainer.filter_service]


@filter_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TaskFilterResponse
)
async def get(id: UUID):
    return await filter_service.get(id=id)


@filter_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskFilterResponse],
    description=(generate_multi_get_description(model_name="Taskfilters")),
)
async def get_multi(
    filter_params: Annotated[CommonSearchFieldsSchema, Query()],
):
    return await filter_service.get_multi(filter_params=filter_params)


@filter_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=TaskFilterResponse
)
async def create(create_schema: TaskFilterCreate):
    return await filter_service.create(create_schema=create_schema, commit=True)


@filter_router.patch(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TaskFilterResponse
)
async def update(update_schema: TaskFilterUpdate, id: UUID):
    return await filter_service.update(update_schema=update_schema, commit=True, id=id)


@filter_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    return await filter_service.delete(id=id, commit=True)
