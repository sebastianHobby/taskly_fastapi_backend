from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.models import TaskContainerTypes, Project, Area, Task
from .. import schemas
from ..core.database import get_database_session
from ..core.router_util import get_task_container_by_id, create_uuid_from_string
from ..serviceRepository import CrudFactory

project_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


@project_router.get(
    "/projects", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectGet]
)
async def get_projects(database: SessionDep):
    projects_query = database.query(Project)
    return projects_query.all()


@project_router.get(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProjectGet,
)
async def get_project(database: SessionDep, project_id: str):
    # Validates UUID. Raises 404 error if UUID string is invalid
    ProjectCrudRepository = CrudFactory(Project)
    project = ProjectCrudRepository.get_one_by_id(
        session=database, project_id=project_id, column="id"
    )

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@project_router.post("/projects", response_model=schemas.ProjectGet)
async def create_project(database: SessionDep, project_request: schemas.ProjectCreate):
    # Check foreign key for area is valid if provided. Raises 404 error if not found
    ProjectCrudRepository = CrudFactory(Project)

    # Todo move me to CRUD factory or subclass
    if project_request.parent_id is not None:
        parent = get_task_container_by_id(project_request.parent_id, database)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Parent_id not found"
            )

    # Todo fix me and async database integration in general
    project = await ProjectCrudRepository.create(session=database, data=project_request)

    return project

    # db_project = Project(**project_request.model_dump())
    # db_project.type = TaskContainerTypes.project
    # database.add(db_project)
    # database.commit()
    # return db_project


@project_router.put("/projects", response_model=schemas.ProjectGet)
async def update_project(database: SessionDep, project_request: schemas.ProjectUpdate):
    # Check the ID we are updating exists as task container. This is mandatorty so should always exist.
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


@project_router.delete("/projects/{project_id}")
async def delete_project(database: SessionDep, project_id: str):
    uuid = create_uuid_from_string(project_id)
    project = get_task_container_by_id(uuid, database, TaskContainerTypes.project)
    database.delete(project)
    database.commit()
