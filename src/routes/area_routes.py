from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from ..core.dependency_containers import Container
from ..repositories.AbstractRepository import AbstractServiceRepository
from ..schemas.AreaSchemas import AreaGet, AreaCreate, AreaUpdate
from ..services.area_service import AreaService

# Todo setup tests for this pattern (API router with prefix) then copy for areas + areas
area_router = APIRouter(prefix="/areas", tags=["Area"])


@area_router.get(path="/", status_code=status.HTTP_200_OK, response_model=list[AreaGet])
@inject
def get_areas(
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):

    return area_service.get_all()


@area_router.get(
    "/{area_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=AreaGet,
)
@inject
def get_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    return area_service.get_one_by_uuid(uuid=area_uuid)


@area_router.post("/", response_model=AreaGet)
@inject
def create_area(
    create_schema: AreaCreate,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    return area_service.create(create_schema=create_schema)


@area_router.put("/", response_model=AreaGet)
@inject
def update_area(
    update_schema: AreaUpdate,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    return area_service.update(update_schema=update_schema)


@area_router.delete("/{area_uuid}")
@inject
async def delete_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    return area_service.delete(uuid=area_uuid)
