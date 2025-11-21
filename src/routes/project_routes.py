from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..core.dependency_containers import Container
from ..repositories.AbstractRepository import AbstractServiceRepository
from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..services.project_service import ProjectService
from fastapi import APIRouter, Depends, Response, status

project_router = APIRouter(prefix="/projects", tags=["Project"])


@project_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=list[ProjectGet]
)
@inject
async def get_projects(
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):

    list = await project_service.get_all()
    return list


@project_router.get(
    "/{project_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectGet,
)
@inject
async def get_project(
    project_uuid: UUID,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    project = await project_service.get_one_by_uuid(uuid=project_uuid)
    return project


@project_router.post("/", response_model=ProjectGet)
@inject
async def create_project(
    create_schema: ProjectCreate,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    project = await project_service.create(create_schema=create_schema)
    return project


@project_router.put("/", response_model=ProjectGet)
@inject
async def update_project(
    update_schema: ProjectUpdate,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    project = await project_service.update(update_schema=update_schema)
    return project


@project_router.delete("/{project_uuid}")
@inject
async def delete_project(
    project_uuid: UUID,
    project_service: Annotated[
        ProjectService, Depends(Provide[Container.project_repository])
    ],
):
    project_service.delete(uuid=project_uuid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
