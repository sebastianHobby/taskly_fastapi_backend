from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import schemas, models
from .models import TaskContainerTypes, TaskContainer
from ..core.database import get_database_session

project_router = APIRouter()
area_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


# Helper functions
def get_task_container_by_id(
    uuid: UUID, database: Session, task_container: TaskContainerTypes
) -> TaskContainer:
    parentContainer = None
    if uuid is not None:
        parentContainer = (
            database.query(models.TaskContainer)
            .filter(models.TaskContainer.id == uuid)
            .filter(models.TaskContainer.type == task_container)
            .first()
        )
    if parentContainer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task container id or parent_id is invalid",
        )
    return parentContainer


def create_uuid_from_string(sUUID: str):
    try:
        uuid = UUID(sUUID)
        return uuid
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid UUID input"
        )


@project_router.get(
    "/projects", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectGet]
)
async def get_projects(database: SessionDep):
    projects_query = database.query(models.Project)
    return projects_query.all()


@project_router.get(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProjectGet,
)
async def get_project(database: SessionDep, project_id: str):
    # Validates UUID. Raises 404 error if UUID string is invalid
    uuid = create_uuid_from_string(project_id)
    return get_task_container_by_id(uuid, database, TaskContainerTypes.project)


@project_router.post("/projects", response_model=schemas.ProjectGet)
async def create_project(database: SessionDep, project_request: schemas.ProjectCreate):
    # Check foreign key for area is valid if provided. Raises 404 error if not found
    if project_request.parent_id is not None:
        parent = get_task_container_by_id(
            project_request.parent_id, database, TaskContainerTypes.project
        )

    db_project = models.Project(**project_request.model_dump())
    db_project.type = TaskContainerTypes.project
    database.add(db_project)
    database.commit()
    database.refresh(db_project)
    return db_project


@project_router.put("/projects", response_model=schemas.ProjectGet)
async def update_project(database: SessionDep, project_request: schemas.ProjectUpdate):
    # Check the ID we are updating exists as task container. This is mandatorty so should always exist.
    project = get_task_container_by_id(
        project_request.id, database, TaskContainerTypes.project
    )
    # Check parent ID exists if provided
    if project_request.parent_id:
        get_task_container_by_id(project_request.parent_id, database)

    # Update fields based on request object
    for var, value in project_request.model_dump().items():
        setattr(project, var, value) if value is not None else None
    database.commit()
    database.refresh(project)
    return project


@project_router.delete("/projects/{project_id}")
async def delete_project(database: SessionDep, project_id: str):
    uuid = create_uuid_from_string(project_id)
    project = get_task_container_by_id(uuid, database, TaskContainerTypes.project)
    database.delete(project)
    database.commit()


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
