"""Containers module."""

from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from dependency_injector.wiring import required
from fastapi import FastAPI
from sqlalchemy.orm.session import sessionmaker

from src.services.project_service import ProjectService
from .database import Database
from ..models.db_models import *
from ..repositories.DatabaseRepository import (
    DatabaseRepository,
)
from ..schemas.ProjectSchemas import ProjectGet, ProjectCreate, ProjectUpdate
from ..schemas.AreaSchemas import *
from ..schemas.TaskSchemas import *
from ..services.area_service import AreaService
from ..services.task_service import TaskService

#
# @asynccontextmanager
# async def fastapi_app_lifespan_manager():
#     print("hello fast api start")
#     yield
#     print("exit fast api context")


class AppContextManager:
    def __init__(self, host, port, user, password):
        self.app = FastAPI()

    def __enter__(self):
        print(f"Initialising fastAPI inside AppContextManager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.routes.project_routes",
            "src.main",
        ]
    )

    config = providers.Configuration(strict=True)
    config.from_json("src/core/config.json", required=True)

    database = providers.ThreadSafeSingleton(
        Database,
        db_url=config.database.url,
        connection_args=config.database.connection_args,
    )

    project_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Project,
        update_schema_class=ProjectUpdate,
        create_schema_class=ProjectCreate,
        public_schema_class=ProjectGet,
        database_session=database.provided.session,
    )
    area_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Area,
        update_schema_class=AreaUpdate,
        create_schema_class=AreaCreate,
        public_schema_class=AreaGet,
        database_session=database.provided.session,
    )
    task_repository = providers.Factory(
        DatabaseRepository,
        database_model_class=Task,
        update_schema_class=TaskUpdate,
        create_schema_class=TaskCreate,
        public_schema_class=TaskGet,
        database_session=database.provided.session,
    )

    project_service = providers.Factory(ProjectService, repository=project_repository)
    area_service = providers.Factory(AreaService, repository=area_repository)
    task_service = providers.Factory(TaskService, repository=task_repository)
