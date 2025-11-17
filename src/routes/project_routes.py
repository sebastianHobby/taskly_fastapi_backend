from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from ..repositories.DatabaseRepository import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
)

from ..repositories.ProjectRepository import ProjectRepository
from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate

project_router = APIRouter()


@project_router.get(
    "/projects", status_code=status.HTTP_200_OK, response_model=list[ProjectGet]
)
def get_projects(project_repository=Depends(ProjectRepository)):
    project_get_schemas = project_repository.get_all()
    return project_get_schemas


@project_router.get(
    "/projects/{project_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectGet,
)
def get_project(project_uuid: UUID, project_repository=Depends(ProjectRepository)):
    try:
        return project_repository.get_one_by_uuid(uuid=project_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="Project not found")


@project_router.post("/projects", response_model=ProjectGet)
def create_project(
    create_schema: ProjectCreate, project_repository=Depends(ProjectRepository)
):
    # Check foreign key for area is valid if provided. Raises 404 error if not found
    try:
        return project_repository.create(create_schema=create_schema)
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )


@project_router.put("/projects", response_model=ProjectGet)
def update_project(
    update_schema: ProjectUpdate, project_repository=Depends(ProjectRepository)
):
    try:
        return project_repository.update(
            update_schema=update_schema, uuid=update_schema.uuid
        )
    except DataModelIntegrityConflictException:
        raise HTTPException(
            status_code=409, detail="Invalid state - check parent_id exists"
        )
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="Project not found")


@project_router.delete("/projects/{project_uuid}")
async def delete_project(
    project_uuid: UUID, project_repository=Depends(ProjectRepository)
):
    try:
        return project_repository.delete(uuid=project_uuid)
    except DataModelNotFound:
        raise HTTPException(status_code=404, detail="Project not found")
