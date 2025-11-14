from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import schemas, models
from ..core.database import get_database_session

project_router = APIRouter()
area_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


@project_router.get(
    "/projects", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectGet]
)
async def get_all_projects(database: SessionDep):
    projects_query = database.query(models.Project)
    return projects_query.all()


@project_router.get(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProjectGet,
)
async def get_project_by_id(database: SessionDep, project_id: str):
    try:
        uuid = UUID(project_id)
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )

    project = database.query(models.Project).filter(models.Project.id == uuid).first()
    if project is not None:
        return project
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
    )


@project_router.post("/projects", response_model=schemas.ProjectGet)
async def create_project(database: SessionDep, project_request: schemas.ProjectCreate):
    db_project = models.Project(**project_request.model_dump())
    # Check foreign key for area is valid if provided

    if project_request.area_id is not None:
        area = (
            database.query(models.Area)
            .filter(models.Area.id == project_request.area_id)
            .first()
        )
        if area is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Area_id invalid"
            )
    try:
        database.add(db_project)
        database.commit()
        database.refresh(db_project)
    except IntegrityError as e:
        # Database constraint error most likely foreign key does not exist.
        print("Database constraint failed!")
        print(e)
    return db_project


@project_router.put("/projects")
async def update_project(
    database: SessionDep, project_request: schemas.ProjectUpdate, project_id: str
):
    project = (
        database.query(models.Project)
        .filter(models.Project.id == project_request.id)
        .first()
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )
    # Update fields based on request object
    for var, value in project_request.model_dump().items():
        setattr(project, var, value) if value is not None else None
    database.commit()
    database.refresh(project)


@project_router.delete("/projects/{project_id}")
async def delete_project(database: SessionDep, project_id: str):
    try:
        uuid = UUID(project_id)
        project = (
            database.query(models.Project).filter(models.Project.id == uuid).first()
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )

    database.delete(project)
    database.commit()
    database.refresh(project)


@area_router.get(
    "/areas", status_code=status.HTTP_200_OK, response_model=list[schemas.AreaGet]
)
async def get_all_areas(database: SessionDep):
    areas_query = database.query(models.Area)
    return areas_query.all()


@area_router.get(
    "/areas/{area_id}", status_code=status.HTTP_200_OK, response_model=schemas.AreaGet
)
async def get_area_by_id(database: SessionDep, area_id: str):
    try:
        uuid = UUID(area_id)
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="area not found"
        )

    area = database.query(models.Area).filter(models.Area.id == uuid).first()
    if area is not None:
        return area
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="area not found")


@area_router.post("/areas", response_model=schemas.AreaGet)
async def create_area(database: SessionDep, area_request: schemas.AreaCreate):
    db_area = models.Area(**area_request.model_dump())
    # Check foreign key for area is valid if provided
    database.add(db_area)
    database.commit()
    database.refresh(db_area)
    return db_area


@area_router.put("/areas")
async def update_area(
    database: SessionDep, area_request: schemas.AreaUpdate, area_id: str
):
    area = database.query(models.Area).filter(models.Area.id == area_request.id).first()
    if area is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="area not found"
        )
    # Update fields based on request object
    for var, value in area_request.model_dump().items():
        setattr(area, var, value) if value is not None else None
    database.commit()
    database.refresh(area)


@area_router.delete("/areas/{area_id}")
async def delete_area(database: SessionDep, area_id: str):
    try:
        uuid = UUID(area_id)
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="area not found"
        )

    area = database.query(models.Area).filter(models.Area.id == uuid).first()
    if area is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="area not found"
        )

    database.delete(area)
    database.commit()
    database.refresh(area)
