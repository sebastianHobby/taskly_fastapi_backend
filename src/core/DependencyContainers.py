"""Containers module."""

from dependency_injector import containers, providers
from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import Settings
from .databasemanager import DatabaseManager
from ..filtersets.filtersets import ProjectFilterParams, ProjectFilterSet
from ..models.project_model import *
from ..models.task_model import *
from ..repository.database_repository import DatabaseRepository
from ..schemas.project_schemas import (
    ProjectResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectDelete,
)
from ..schemas.TaskSchemas import (
    TaskResponse,
    TaskUpdate,
    TaskCreate,
    TaskDelete,
)
from ..services.task_service import TasklyTaskService
from ..services.project_service import ProjectService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        packages=["src.routes", "src.repository"], modules=["src.main"]
    )

    config = providers.Configuration(strict=True)
    config.from_pydantic(Settings(), required=True)

    database_manager = providers.ThreadSafeSingleton(
        DatabaseManager, db_url=config.database_url
    )

    # session = database_manager().get_async_session()

    # project_repo = providers.Factory(
    #     FastCRUD[
    #         Project,
    #         ProjectCreate,
    #         ProjectUpdate,
    #         None,
    #         ProjectDelete,
    #         ProjectResponse,
    #     ],
    #     model=Project,
    # )
    #
    task_repo = providers.Factory(
        FastCRUD[
            Task,
            TaskCreate,
            TaskUpdate,
            None,
            TaskDelete,
            TaskResponse,
        ],
        model=Task,
    )

    project_repo = providers.Factory(
        DatabaseRepository[
            Project,
            ProjectCreate,
            ProjectUpdate,
            ProjectResponse,
            ProjectFilterParams,
            ProjectFilterSet,
        ],
        model=Project,
        response_schema=ProjectResponse,
        session_factory=database_manager.provided.get_async_session,
    )

    project_service = providers.Factory(ProjectService, repository=project_repo)

    task_service = providers.Factory(
        TasklyTaskService,
        task_repository=task_repo,
        database_session_factory=database_manager.provided.get_async_session,
    )
