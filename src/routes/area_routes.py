from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.models import TaskContainerTypes
from .. import schemas
from ..core.database import get_database_session
from ..core.router_util import get_task_container_by_id, create_uuid_from_string

area_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


@area_router.get(
    "/areas", status_code=status.HTTP_200_OK, response_model=list[schemas.AreaGet]
)
async def get_areas(database: SessionDep):
    areas_query = database.query(models.Area)
    return areas_query.all()


@area_router.get(
    "/areas/{area_id}", status_code=status.HTTP_200_OK, response_model=schemas.AreaGet
)
async def get_area(database: SessionDep, area_id: str):
    uuid = create_uuid_from_string(area_id)
    return get_task_container_by_id(uuid, database, TaskContainerTypes.area)


@area_router.post("/areas", response_model=schemas.AreaGet)
async def create_area(database: SessionDep, area_request: schemas.AreaCreate):
    db_area = models.Area(**area_request.model_dump())
    # Check foreign key for area is valid if provided
    database.add(db_area)
    database.commit()
    database.refresh(db_area)
    return db_area


@area_router.put("/areas")
async def update_area(database: SessionDep, area_request: schemas.AreaUpdate):
    area = get_task_container_by_id(area_request.id, database, TaskContainerTypes.area)
    # Update fields based on request object
    for var, value in area_request.model_dump().items():
        setattr(area, var, value) if value is not None else None
    database.commit()
    database.refresh(area)


@area_router.delete("/areas/{area_id}")
async def delete_area(database: SessionDep, area_id: str):
    uuid = create_uuid_from_string(area_id)
    area = get_task_container_by_id(uuid, database, TaskContainerTypes.area)
    database.delete(area)
    database.commit()
    database.refresh(area)
