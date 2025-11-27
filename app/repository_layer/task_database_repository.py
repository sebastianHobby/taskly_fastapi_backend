from typing import Any
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repository_layer.abstract_database_repository import (
    AbstractDatabaseRepository,
    CrudActions,
)
from app.repository_layer.task_filterset import TaskFiltersetRules
from app.repository_layer.models.models import DatabaseBaseModel, Task


class TaskDatabaseRepository(AbstractDatabaseRepository):
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def create_model_obj_from_schema(
        self, schema: BaseSchemaModel
    ) -> DatabaseBaseModel:
        """
        :return: SQLAlchemy model request_data created from the provided dictionary
        :raises: TasklyRepositoryException if the schema class is wrong or can not be mapped
            to database model for any reason
        """
        schema_dict = schema.model_dump()
        model = Task(**schema_dict)
        return model

    async def dump_model_to_dict(self, model: DatabaseBaseModel) -> dict:
        return model.to_dict(nested=False, exclude=None)

    async def validate(
        self,
        request_action: CrudActions,
        request_data: BaseSchemaModel = None,
        request_id: UUID = None,
    ) -> BaseSchemaModel:
        """Used to check any repository level validations for request_data before Insert/Update/Delete done
        need to do basic validations as schema objects NOT checked at this point.
        """
        pass
        # raise NotImplementedError()

    async def validate_filter_params(
        self, filter_params: BaseSchemaModel, action: CrudActions
    ) -> dict:
        """Used to check if filter params are valid, note this is only used in get_multi at the moment
        but filters could also be used for updates,deletes etc in future.
        Returns validated filter_params as dict"""
        return filter_params.model_dump(exclude_none=True)

    async def get_filterset(self, params: dict, session: AsyncSession) -> Any:
        """Returns a SQLAlchemy statement object for the appropriate model class
        e.g.
        base_query = select(Task) # equivalent to select * from [task table]
        filterset  = TaskFilterset(session=session,query=base_query)"""
        base_query = select(Task)
        filterset = TaskFiltersetRules(session=session, query=base_query)
        return filterset

    @property
    async def model_class(self):
        """Return the database model class e.g. return Task"""
        return Task

    @property
    def session_factory(self) -> async_sessionmaker:
        return self._session_factory

    async def post_processing(
        self,
        request_action: CrudActions,
        model: DatabaseBaseModel = None,
        request_data: BaseSchemaModel = None,
        request_id: UUID = None,
    ) -> BaseSchemaModel:
        pass
