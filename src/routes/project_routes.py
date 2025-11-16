import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.models import TaskContainerTypes, Project, Area, Task
from .. import schemas
from ..core.database import get_database_session
from ..core.router_util import get_task_container_by_id, create_uuid_from_string

# from ..serviceRepository import CrudFactory
from ..serviceRepository import ProjectRepository

project_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


@project_router.get(
    "/projects", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectGet]
)
def get_projects(database: SessionDep):
    project_repository = ProjectRepository()
    project_list = project_repository.get_all(session=database)
    if project_list is None:
        return []
    return project_list


@project_router.get(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProjectGet,
)
def get_project(database: SessionDep, project_id: str):
    # Validates UUID. Raises 404 error if UUID string is invalid
    project_repository = ProjectRepository()
    uuid = create_uuid_from_string(project_id)
    project_get_schema = project_repository.get_one_by_id(id=uuid, session=database)

    if project_get_schema is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_get_schema


@project_router.post("/projects", response_model=schemas.ProjectGet)
def create_project(database: SessionDep, project_request: schemas.ProjectCreate):
    # Check foreign key for area is valid if provided. Raises 404 error if not found
    project_repository = ProjectRepository()
    project_get_schema = project_repository.create(
        session=database, create_schema=project_request
    )

    # Todo move me to CRUD factory or subclass
    # if project_request.parent_id is not None:
    #     parent = get_task_container_by_id(project_request.parent_id, database)
    #     if parent is None:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Parent_id not found"
    #         )

    return project_get_schema


#
#
@project_router.put("/projects", response_model=schemas.ProjectGet)
def update_project(database: SessionDep, project_request: schemas.ProjectUpdate):
    project_repository = ProjectRepository()
    project_get_schema = project_repository.update(
        session=database, uuid=project_request.id, update_schema=project_request
    )

    project = get_task_container_by_id(project_request.id, database)
    assert project is not None
    assert project.type == TaskContainerTypes.project

    # Check parent ID exists if provided
    if project_request.parent_id:
        get_task_container_by_id(project_request.parent_id, database)

    # Update fields based on request object
    for var, value in project_request.model_dump().items():
        setattr(project, var, value) if value is not None else None
    database.commit()
    database.refresh(project)
    return project


#
#
# @project_router.delete("/projects/{project_id}")
# async def delete_project(database: SessionDep, project_id: str):
#     uuid = create_uuid_from_string(project_id)
#     project = get_task_container_by_id(uuid, database, TaskContainerTypes.project)
#     database.delete(project)
#     database.commit()
