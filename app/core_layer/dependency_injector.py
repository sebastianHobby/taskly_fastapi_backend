"""Containers module."""

from dependency_injector import containers, providers

from .config import Settings
from .database import *
from ..repository_layer.project_database_repository import ProjectDatabaseRepository
from ..repository_layer.task_database_repository import TaskDatabaseRepository
from ..service_layer.project_service import ProjectService


class TasklyDependencyContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.routes.project_routes",
            "app.main",
            "app.api.routes.task_routes",
        ],
    )

    config = providers.Configuration(strict=True, pydantic_settings=[settings])

    session_factory = providers.Callable(get_async_session_maker)

    project_repo = providers.Factory(
        ProjectDatabaseRepository, session_factory=session_factory
    )
    project_service = providers.Factory(ProjectService, repository=project_repo)

    task_repo = providers.Factory(
        TaskDatabaseRepository, session_factory=session_factory
    )
    task_service = providers.Factory(ProjectService, repository=task_repo)

    # task_service = providers.Factory(
    #     TasklyTaskService,
    #     task_repository=task_repo,
    #     database_session_factory=async_session_factory
    # )
