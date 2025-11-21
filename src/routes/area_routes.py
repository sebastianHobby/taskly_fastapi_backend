from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..core.dependency_containers import Container
from ..repositories.AbstractRepository import AbstractServiceRepository
from ..schemas.AreaSchemas import AreaGet, AreaCreate, AreaUpdate
from ..services.area_service import AreaService
from fastapi import APIRouter, Depends, Response, status

area_router = APIRouter(prefix="/areas", tags=["Area"])


@area_router.get(path="/", status_code=status.HTTP_200_OK, response_model=list[AreaGet])
@inject
async def get_areas(
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):

    list = await area_service.get_all()
    return list


@area_router.get(
    "/{area_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=AreaGet,
)
@inject
async def get_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    area = await area_service.get_one_by_uuid(uuid=area_uuid)
    return area


@area_router.post("/", response_model=AreaGet)
@inject
async def create_area(
    create_schema: AreaCreate,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    area = await area_service.create(create_schema=create_schema)
    return area


@area_router.put("/", response_model=AreaGet)
@inject
async def update_area(
    update_schema: AreaUpdate,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    area = await area_service.update(update_schema=update_schema)
    return area


@area_router.delete("/{area_uuid}")
@inject
async def delete_area(
    area_uuid: UUID,
    area_service: Annotated[AreaService, Depends(Provide[Container.area_repository])],
):
    area_service.delete(uuid=area_uuid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
