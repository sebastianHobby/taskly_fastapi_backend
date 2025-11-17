from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
)

from ..repositories.AreaRepository import *
from ..schemas.AreaSchemas import *

area_router = APIRouter()


@area_router.get("/areas", status_code=status.HTTP_200_OK, response_model=list[AreaGet])
def get_areas(area_repository=Depends(AreaRepository)):
    area_get_schemas = area_repository.get_all()
    return area_get_schemas


@area_router.get(
    "/areas/{area_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=AreaGet,
)
def get_area(area_uuid: UUID, area_repository=Depends(AreaRepository)):
    try:
        return area_repository.get_one_by_uuid(uuid=area_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="area not found")


@area_router.post("/areas", response_model=AreaGet)
def create_area(create_schema: AreaCreate, area_repository=Depends(AreaRepository)):
    # Check foreign key for area is valid if provided. Raises 404 error if not found
    try:
        return area_repository.create(create_schema=create_schema)
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )


@area_router.put("/areas", response_model=AreaGet)
def update_area(update_schema: AreaUpdate, area_repository=Depends(AreaRepository)):
    try:
        return area_repository.update(
            update_schema=update_schema, uuid=update_schema.uuid
        )
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="area not found")


@area_router.delete("/areas/{area_uuid}")
async def delete_area(area_uuid: UUID, area_repository=Depends(AreaRepository)):
    try:
        return area_repository.delete(uuid=area_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="area not found")
