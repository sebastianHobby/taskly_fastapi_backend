from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, status, Query, Depends

from .utils import generate_multi_get_description
from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.service_layer.schemas.filter_schemas import (
    FilterResponse,
    FilterUpdate,
    FilterCreate,
)
from app.service_layer.filter_service import FilterService
from ...repository_layer.base_filtersets import BaseTasklyFilterParams

filter_router = APIRouter(prefix="/filters", tags=["Filters"])
# noinspection DuplicatedCode
filter_service: FilterService = Provide[TasklyDependencyContainer.filter_service]


@filter_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=FilterResponse
)
async def get(id: UUID):
    return await filter_service.get(id=id)


@filter_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[FilterResponse],
    description=(generate_multi_get_description(model_name="Filter")),
)
async def get_multi(filter_params: Annotated[BaseTasklyFilterParams, Query()]):
    return await filter_service.get_multi(filter_params=filter_params)


@filter_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=FilterResponse
)
async def create(create_schema: FilterCreate):
    return await filter_service.create(create_schema=create_schema, commit=True)


@filter_router.patch(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=FilterResponse
)
async def update(update_schema: FilterUpdate, id: UUID):
    return await filter_service.update(update_schema=update_schema, commit=True, id=id)


@filter_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    return await filter_service.delete(id=id, commit=True)
