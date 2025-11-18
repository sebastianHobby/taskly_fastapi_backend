from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

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


# Dependency functions - used for dependency injection.
def dependency_proj_repository(
    session: Annotated[AbstractServiceRepository, Depends(get_database_session)],
) -> AbstractServiceRepository:
    return DatabaseRepository(
        database_model_class=Project,
        update_schema_class=ProjectUpdate,
        create_schema_class=ProjectCreate,
        public_schema_class=ProjectGet,
        database_session=session,
    )


def dependency_proj_service(
    repository: Annotated[
        AbstractServiceRepository, Depends(dependency_proj_repository)
    ],
) -> ProjectService:
    # Why create Database repository here instead of just having Project Service create the repository?
    # This lets us perform dependency injection later so we can override the database repository
    # with a different repository source (e.g. mock for testing) or change to different
    # Repository (e.g. switch data source to API , file etc) without impacting the
    # code using this dependency - everything depends on an abstract Repository interface
    # so long as our replacement walks,talks and quacks like a duck/Repository we can use it here
    return ProjectService(repository=repository)


# Some important notes
# Error handling is all done by errors.py in root , this allows us to avoid having
# to cater for each error and map to HTTP response code in each function
@project_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=list[ProjectGet]
)
def get_projects(
    project_service: Annotated[ProjectService, Depends(dependency_proj_service)],
):
    return project_service.get_all()


@project_router.get(
    "/{project_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectGet,
)
def get_project(
    project_uuid: UUID,
    project_service: Annotated[ProjectService, Depends(dependency_proj_service)],
):
    return project_service.get_one_by_uuid(uuid=project_uuid)


@project_router.post("/", response_model=ProjectGet)
def create_project(
    create_schema: ProjectCreate,
    project_service: Annotated[ProjectService, Depends(dependency_proj_service)],
):
    return project_service.create(create_schema=create_schema)


@project_router.put("/", response_model=ProjectGet)
def update_project(
    update_schema: ProjectUpdate,
    project_service: Annotated[ProjectService, Depends(dependency_proj_service)],
):
    return project_service.update(update_schema=update_schema, uuid=update_schema.uuid)


@project_router.delete("/{project_uuid}")
async def delete_project(
    project_uuid: UUID,
    project_service: Annotated[ProjectService, Depends(dependency_proj_service)],
):
    return project_service.delete(uuid=project_uuid)
