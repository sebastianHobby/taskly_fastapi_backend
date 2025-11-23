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
from src.services.service_schemas import TaskListAndListGroups


class TaskListService:
    def __init__(
        self,
        list_repo: AbstractServiceRepository,
        list_group_repo: AbstractServiceRepository,
    ):
        self.list_repo = list_repo
        self.list_group_repo = list_group_repo

    async def get_task_list_by_id(self, list_id: UUID) -> TaskListResponse:
        """Returns task list by ID or None if data does not exist"""
        result = await self.list_repo.get(id=list_id)
        if result is None:
            raise DataModelNotFound(f"Task list with Id {list_id} not found")
        return result

    async def get_list_group_by_id(self, group_id: UUID) -> ListGroupResponse:
        """Returns list group by ID or None if data does not exist"""
        result = await self.list_group_repo.get(id=group_id)
        if result is None:
            raise DataModelNotFound(f"List group with Id {group_id} not found")
        return result

    async def get_multiple(self, filters: dict = None) -> type[TaskListAndListGroups]:
        task_list_response = await self.list_repo.get_multiple(filters=filters)
        list_group_response = await self.list_group_repo.get_multiple(filters=filters)
        TaskListAndListGroups.ListGroup = list_group_response
        TaskListAndListGroups.TaskList = task_list_response
        return TaskListAndListGroups

    async def create_task_list(self, create_schema: TaskListCreate) -> TaskListResponse:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        res = await self.list_repo.create(create_schema)
        return res

    async def create_list_group(
        self, create_schema: ListGroupCreate
    ) -> ListGroupResponse:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        res = await self.list_group_repo.create(create_schema)
        return res

    async def update_task_list(self, update_schema: TaskListUpdate) -> TaskListResponse:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        res = await self.list_repo.update(update_schema=update_schema)
        return res

    async def update_list_group(
        self, update_schema: ListGroupUpdate
    ) -> ListGroupResponse:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        res = await self.list_group_repo.update(update_schema=update_schema)
        return res

    async def delete_task_list(self, task_list_id: UUID) -> bool:
        """Raises: DataModelNotFound: if no data found"""
        res = await self.list_repo.delete(id=task_list_id)
        return res

    async def delete_list_group(self, list_group_id: UUID) -> bool:
        """Raises: DataModelNotFound: if no data found"""
        res = await self.list_group_repo.delete(id=list_group_id)
        return res
