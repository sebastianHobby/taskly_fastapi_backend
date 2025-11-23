from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..core.dependency_containers import Container
from ..schemas.FilterSchemas import FilterCreate
from ..schemas.TaskSchemas import TaskResponse, TaskCreate, TaskUpdate
from fastapi import APIRouter, Depends, status

from ..services.task_service import TaskService

filter_router = APIRouter(prefix="/filters", tags=["Filters"])


@filter_router.post(path="/", status_code=status.HTTP_200_OK)
async def create_filter(
    filter_create: FilterCreate,
):
    print(filter_create)
    return filter_create
