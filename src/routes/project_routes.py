from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from ..core.dependency_containers import Container
from ..core.database import get_database_session
from ..models.db_models import Project
from ..repositories.AbstractServiceRepository import AbstractServiceRepository
from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
    DatabaseRepository,
)

from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..services.project_service import ProjectService


# Todo setup tests for this pattern (API router with prefix) then copy for areas + projects
project_router = APIRouter(prefix="/projects", tags=["Project"])


@project_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=list[ProjectGet]
)
@inject
def get_projects(
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    return project_service.get_all()


@project_router.get(
    "/{project_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectGet,
)
@inject
def get_project(
    project_uuid: UUID,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    return project_service.get_one_by_uuid(uuid=project_uuid)


@project_router.post("/", response_model=ProjectGet)
@inject
def create_project(
    create_schema: ProjectCreate,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    return project_service.create(create_schema=create_schema)


@project_router.put("/", response_model=ProjectGet)
@inject
def update_project(
    update_schema: ProjectUpdate,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    return project_service.update(update_schema=update_schema)


@project_router.delete("/{project_uuid}")
@inject
async def delete_project(
    project_uuid: UUID,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    return project_service.delete(uuid=project_uuid)
