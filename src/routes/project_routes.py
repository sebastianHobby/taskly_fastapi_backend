from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, status, Query
from fastcrud import FilterConfig
from fastcrud.fastapi_dependencies import create_dynamic_filters
from pydantic import BaseModel, Field

from .utils import generate_multi_get_description
from ..filtersets.filtersets import ProjectFilterParams
from ..core.DependencyContainers import Container
from ..repository.database_repository import DatabaseRepository, DataReturnTypes
from ..schemas.project_schemas import (
    ProjectResponse,
    ProjectUpdate,
    ProjectCreate,
)
from ..schemas.QueryParamHelper import TasklistQueryParams
from ..services.project_service import ProjectService

project_router = APIRouter(prefix="/projects", tags=["Projects"])
# noinspection DuplicatedCode
project_service: ProjectService = Provide[Container.project_service]


@project_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse
)
async def get(id: UUID):
    return await project_service.get(id=id, return_type=DataReturnTypes.dictionary)


@project_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[ProjectResponse],
    description=(generate_multi_get_description(model_name="Project")),
)
async def get_multi(filter_params: Annotated[ProjectFilterParams, Query()]):
    return await project_service.get_multi(
        filter_params=filter_params, return_type=DataReturnTypes.dictionary
    )


@project_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse
)
async def create(create_schema: ProjectCreate):
    return await project_service.create(
        create_schema=create_schema, return_type=DataReturnTypes.dictionary, commit=True
    )


@project_router.patch(
    path="/", status_code=status.HTTP_200_OK, response_model=ProjectResponse
)
async def update(update_schema: ProjectUpdate):
    return await project_service.update(
        update_schema=update_schema, commit=True, return_type=DataReturnTypes.dictionary
    )
    return res


@project_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    return await project_service.delete(primary_key=id, commit=True)
