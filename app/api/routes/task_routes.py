from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, status, Query, Depends

from .utils import generate_multi_get_description
from ...repository_layer.task_filterset import TaskFilterParams
from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.service_layer.schemas.task_schemas import (
    TaskResponse,
    TaskUpdate,
    TaskCreate,
)
from app.service_layer.task_service import TaskService

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
# noinspection DuplicatedCode
task_service = Provide[TasklyDependencyContainer.task_service]


@task_router.get(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TaskResponse
)
async def get(id: UUID):
    return await task_service.get(id=id)


@task_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskResponse],
    description=(generate_multi_get_description(model_name="Task")),
)
async def get_multi(filter_params: Annotated[TaskFilterParams, Query()]):
    return await task_service.get_multi(filter_params=filter_params)


@task_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse
)
async def create(create_schema: TaskCreate):
    return await task_service.create(create_schema=create_schema, commit=True)


@task_router.patch(
    path="/{id}", status_code=status.HTTP_200_OK, response_model=TaskResponse
)
async def update(update_schema: TaskUpdate, id: UUID):
    return await task_service.update(update_schema=update_schema, commit=True, id=id)


@task_router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID):
    return await task_service.delete(id=id, commit=True)
