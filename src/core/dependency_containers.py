"""Containers module."""

from dependency_injector import containers, providers

from src.services.project_service import ProjectService
from .database import get_database_session, SessionFactory
from ..models.db_models import *
from ..repositories.DatabaseRepository import (
    DatabaseRepository,
)
from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..schemas.AreaSchemas import *
from ..schemas.TaskContainerSchemas import *
from ..schemas.TaskSchemas import *
from ..services.area_service import AreaService
from ..services.task_service import TaskService


def get_database_session_no_generator():
    db_session = SessionFactory()
    return db_session


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=["src.routes.project_routes"]
    )
    session = providers.Factory(get_database_session_no_generator)

    project_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Project,
        update_schema_class=ProjectUpdate,
        create_schema_class=ProjectCreate,
        public_schema_class=ProjectGet,
        database_session=session,
    )
    area_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Area,
        update_schema_class=AreaUpdate,
        create_schema_class=AreaCreate,
        public_schema_class=AreaGet,
        database_session=session,
    )
    task_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Task,
        update_schema_class=TaskUpdate,
        create_schema_class=TaskCreate,
        public_schema_class=TaskGet,
        database_session=session,
    )

    project_service = providers.Factory(ProjectService, repository=project_repository)
    area_service = providers.Factory(AreaService, repository=area_repository)
    task_service = providers.Factory(TaskService, repository=task_repository)
