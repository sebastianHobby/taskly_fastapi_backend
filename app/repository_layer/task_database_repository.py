from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.repository_layer.abstract_database_repository import (
    AbstractDatabaseRepository,
    CrudActions,
)
from app.repository_layer.models.models import DatabaseBaseModel, Tasks


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
        model = Tasks(**schema.model_dump())
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

    @property
    async def model_class(self):
        """Return the database model class e.g. return Tasks"""
        return Tasks

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
