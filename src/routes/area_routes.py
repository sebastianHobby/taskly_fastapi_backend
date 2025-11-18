from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from ..core.database import get_database_session
from ..models.db_models import Area
from ..schemas.AreaSchemas import *
from ..repositories.AbstractServiceRepository import AbstractServiceRepository
from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
    DatabaseRepository,
)

from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..services.area_service import AreaService
from ..services.project_service import ProjectService

area_router = APIRouter(prefix="/areas", tags=["Area"])


# Dependency functions - used for dependency injection.
def dependency_area_repository(
    session: Annotated[AbstractServiceRepository, Depends(get_database_session)],
) -> AbstractServiceRepository:
    return DatabaseRepository(
        database_model_class=Area,
        update_schema_class=AreaUpdate,
        create_schema_class=AreaCreate,
        public_schema_class=AreaGet,
        database_session=session,
    )


def dependency_area_service(
    repository: Annotated[
        AbstractServiceRepository, Depends(dependency_area_repository)
    ],
) -> AreaService:
    # Why create Database repository here instead of just having Area Service create the repository?
    # This lets us perform dependency injection later so we can override the database repository
    # with a different repository source (e.g. mock for testing) or change to different
    # Repository (e.g. switch data source to API , file etc) without impacting the
    # code using this dependency - everything depends on an abstract Repository interface
    # so long as our replacement walks,talks and quacks like a duck/Repository we can use it here
    return AreaService(repository=repository)


# Some important notes
# Error handling is all done by errors.py in root , this allows us to avoid having
# to cater for each error and map to HTTP response code in each function
@area_router.get(path="/", status_code=status.HTTP_200_OK, response_model=list[AreaGet])
def get_areas(
    area_service: Annotated[AreaService, Depends(dependency_area_service)],
):
    return area_service.get_all()


@area_router.get(
    "/{area_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=AreaGet,
)
def get_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(dependency_area_service)],
):
    return area_service.get_one_by_uuid(uuid=area_uuid)


@area_router.post("/", response_model=AreaGet)
def create_area(
    create_schema: AreaCreate,
    area_service: Annotated[AreaService, Depends(dependency_area_service)],
):
    return area_service.create(create_schema=create_schema)


@area_router.put("/", response_model=AreaGet)
def update_area(
    update_schema: AreaUpdate,
    area_service: Annotated[AreaService, Depends(dependency_area_service)],
):
    return area_service.update(update_schema=update_schema)


@area_router.delete("/{area_uuid}")
async def delete_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(dependency_area_service)],
):
    return area_service.delete(uuid=area_uuid)
