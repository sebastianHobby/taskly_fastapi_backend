"""Containers module."""

from contextlib import asynccontextmanager
from sys import modules

import fastapi
from dependency_injector import containers, providers
from dependency_injector.providers import contextmanager
from dependency_injector.wiring import required
from fastapi import FastAPI
from fastcrud import FastCRUD
from sqlalchemy.orm.session import sessionmaker

from .config import Settings
from .database import Database
from ..models.GroupModel import *
from ..models.TaskListModel import *
from ..models.TaskModel import *
from ..models.ViewModel import *
from ..schemas.GroupSchemas import (
    GroupCreate,
    GroupSelect,
    GroupUpdate,
    GroupDelete,
)
from ..schemas.ListSchemas import (
    TasklistSelect,
    TasklistCreate,
    TasklistUpdate,
    TasklistDelete,
)
from ..schemas.TaskSchemas import (
    TaskSelect,
    TaskUpdate,
    TaskCreate,
    TaskDelete,
)
from ..services.TaskService import TasklyTaskService
from ..services.GroupService import GroupService
from ..services.TasklistService import TasklistService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        packages=["src.routes"], modules=["src.main"]
    )

    config = providers.Configuration(strict=True)
    config.from_pydantic(Settings(), required=True)

    database = providers.ThreadSafeSingleton(Database, db_url=config.database_url)

    # Testing FastCrud integration
    list_repo = providers.Factory(
        FastCRUD[
            Tasklist,
            TasklistCreate,
            TasklistUpdate,
            None,
            TasklistDelete,
            TasklistSelect,
        ],
        model=Tasklist,
    )

    group_repo = providers.Factory(
        FastCRUD[
            Group,
            GroupCreate,
            GroupUpdate,
            None,
            GroupDelete,
            GroupSelect,
        ],
        model=Group,
    )

    task_repo = providers.Factory(
        FastCRUD[
            Task,
            TaskCreate,
            TaskUpdate,
            None,
            TaskDelete,
            TaskSelect,
        ],
        model=Group,
    )

    list_service = providers.Factory(
        TasklistService,
        list_repository=list_repo,
        database_session_factory=database.provided.session,
    )

    group_service = providers.Factory(
        GroupService,
        group_repository=group_repo,
        database_session_factory=database.provided.session,
    )

    task_service = providers.Factory(
        TasklyTaskService,
        task_repository=task_repo,
        database_session_factory=database.provided.session,
    )
