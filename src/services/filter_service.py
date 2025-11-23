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
from src.schemas.FilterSchemas import FilterCreate, FilterResponse
from src.schemas.ListGroupSchemas import (
    ListGroupResponse,
    ListGroupCreate,
    ListGroupUpdate,
)
from src.schemas.TaskListSchemas import TaskListResponse, TaskListCreate, TaskListUpdate
from src.schemas.TaskSchemas import TaskResponse, TaskCreate, TaskUpdate
from src.services.service_schemas import TaskListAndListGroups


class FilterService:
    def __init__(
        self,
        task_repo: AbstractServiceRepository,
    ):
        self.task_repo = task_repo

    async def create_view_filter(self, create_schema: FilterCreate) -> FilterResponse:
        view_filter_name = create_schema.view_filter_name
        task_filter_rules = create_schema.task_filter_rules

        class ViewFilter(hasCommonDatabaseFields, DatabaseBaseModel):
            __tablename__ = "view_filters"
            name: Mapped[str]

        class RuleFilter(hasCommonDatabaseFields, DatabaseBaseModel):
            __tablename__ = "rule_filters"
            name: Mapped[TaskFilterRuleTypes] = mapped_column(unique=True)

        class FilterToRuleFilterLink(hasCommonDatabaseFields, DatabaseBaseModel):
            __tablename__ = "view_filter_to_rule_filter_link"
            filter_id = Column(ForeignKey("view_filters.id"))
            filter_rule_id = Column(ForeignKey("rule_filters.id"))
            filter_rule = relationship(
                "RuleFilter", back_populates="view_filter_to_rule_filter_link"
            )
            user = relationship(
                "ViewFilter", back_populates="view_filter_to_rule_filter_link"
            )

        res = await self.task_repo.create(create_schema)
        return res

    async def get_filter(self, id_: UUID) -> TaskResponse:
        """Returns task list by ID or None if data does not exist"""
        result = await self.task_repo.get(id=id_)
        if result is None:
            raise DataModelNotFound(f"Filter with Id {id_} not found")
        return result

    async def get_multiple(self, filters: dict = None) -> list[TaskResponse]:
        result = await self.task_repo.get_multiple(filters=filters)
        return result

    # async def update_task(self, update_schema: TaskUpdate) -> TaskListResponse:
    #     res = await self.task_repo.update(update_schema=update_schema)
    #     return res
    #
    # async def delete_task(self, task_id: UUID) -> bool:
    #     """Raises: DataModelNotFound: if no data found"""
    #     res = await self.task_repo.delete(id=task_id)
    #     return res
