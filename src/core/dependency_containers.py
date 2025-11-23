"""Containers module."""

from contextlib import asynccontextmanager

import fastapi
from dependency_injector import containers, providers
from dependency_injector.providers import contextmanager
from dependency_injector.wiring import required
from fastapi import FastAPI
from sqlalchemy.orm.session import sessionmaker

from .database import Database
from ..models.db_models import *
from ..repositories.DatabaseRepository import (
    DatabaseRepository,
)

from ..schemas.ListGroupSchemas import (
    ListGroupCreate,
    ListGroupResponse,
    ListGroupUpdate,
)
from ..schemas.TaskListSchemas import TaskListResponse, TaskListCreate, TaskListUpdate
from ..schemas.TaskSchemas import (
    TaskResponse,
    TaskUpdate,
    TaskCreate,
)
from ..services.task_list_service import TaskListService
from ..services.task_service import TaskService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.routes.task_list_routes",
            "src.routes.list_group_routes",
            "src.routes.task_routes",
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

    task_list_repository = providers.Factory(
        DatabaseRepository[TaskList, TaskListCreate, TaskListUpdate, TaskResponse],
        database_model_class=TaskList,
        update_schema_class=TaskListUpdate,
        create_schema_class=TaskListCreate,
        response_schema_class=TaskListResponse,
        database_session_factory=database.provided.session,
    )
    list_group_repository = providers.Factory(
        DatabaseRepository[
            ListGroup, ListGroupCreate, ListGroupUpdate, ListGroupResponse
        ],
        database_model_class=ListGroup,
        update_schema_class=TaskListUpdate,
        create_schema_class=ListGroupCreate,
        response_schema_class=ListGroupResponse,
        database_session_factory=database.provided.session,
    )
    task_repository = providers.Factory(
        DatabaseRepository[Task, TaskCreate, TaskUpdate, TaskResponse],
        database_model_class=Task,
        update_schema_class=TaskUpdate,
        create_schema_class=TaskCreate,
        response_schema_class=TaskResponse,
        database_session_factory=database.provided.session,
    )

    task_list_service = providers.Factory(
        TaskListService,
        list_repo=task_list_repository,
        list_group_repo=list_group_repository,
    )
    task_service = providers.Factory(TaskService, task_repo=task_repository)
