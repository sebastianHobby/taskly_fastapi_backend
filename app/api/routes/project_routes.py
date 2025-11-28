from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, status, Query, Depends

from .utils import generate_multi_get_description
from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.service_layer.schemas.project_schemas import (
    ProjectResponse,
    ProjectUpdate,
    ProjectCreate,
)
from app.service_layer.project_service import ProjectService
from ...service_layer.schemas.common_field_search_schema import CommonSearchFieldsSchema

project_router = APIRouter(prefix="/projects", tags=["Projects"])
# noinspection DuplicatedCode
project_service = Provide[TasklyDependencyContainer.project_service]


@project_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse
)
async def get(id: UUID):
    return await project_service.get(id=id)


@project_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[ProjectResponse],
    description=(generate_multi_get_description(model_name="Projects")),
)
async def get_multi(
    filter_params: Annotated[CommonSearchFieldsSchema, Query()],
):
    return await project_service.get_multi(filter_params=filter_params)


@project_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse
)
async def create(create_schema: ProjectCreate):
    return await project_service.create(create_schema=create_schema, commit=True)


@project_router.patch(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse
)
async def update(update_schema: ProjectUpdate, id: UUID):
    return await project_service.update(update_schema=update_schema, commit=True, id=id)


@project_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    return await project_service.delete(id=id, commit=True)
