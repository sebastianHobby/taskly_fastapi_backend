"""Services layer is also known as orchestration layer.
API layer (routes) handles web stuff
Service layer handles any business rules and depends on Repository for access to data
API layer/Presentation --> Service Layer --> Repository
Note this is primarily to allow dependency injection and easy mocking/limiting cost of future changes
See https://github.com/cosmicpython/book/blob/master/chapter_04_service_layer.asciidoc
"""

from typing import List, Any, Coroutine

from click import Tuple
from fastapi import HTTPException
from sqlalchemy import UUID

from src.models.db_models import TaskListTypes
from src.repositories.AbstractRepository import AbstractServiceRepository
from src.repositories.RepositoryExceptions import DataModelNotFound
from src.schemas.ListGroupSchemas import (
    ListGroupResponse,
    ListGroupCreate,
    ListGroupUpdate,
)
from src.schemas.TaskListSchemas import TaskListResponse, TaskListCreate, TaskListUpdate
from src.schemas.TaskSchemas import TaskResponse, TaskCreate, TaskUpdate
from src.services.service_schemas import TaskListAndListGroups


class TaskService:
    def __init__(
        self,
        task_repo: AbstractServiceRepository,
    ):
        self.task_repo = task_repo

    async def get_task(self, task_id: UUID) -> TaskResponse:
        """Returns task list by ID or None if data does not exist"""
        result = await self.task_repo.get(id=task_id)
        if result is None:
            raise DataModelNotFound(f"Task with Id {task_id} not found")
        return result

    async def get_all_tasks(self) -> List[TaskResponse]:
        task_list_response = await self.task_repo.get_all()
        return task_list_response

    async def create_task(self, create_schema: TaskCreate) -> TaskResponse:
        res = await self.task_repo.create(create_schema)
        return res

    async def update_task(self, update_schema: TaskUpdate) -> TaskListResponse:
        res = await self.task_repo.update(update_schema=update_schema)
        return res

    async def delete_task(self, task_id: UUID) -> bool:
        """Raises: DataModelNotFound: if no data found"""
        res = await self.task_repo.delete(id=task_id)
        return res
