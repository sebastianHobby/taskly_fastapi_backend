import json
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.repository_layer.models.models import DatabaseBaseModel, Taskfilters
from .abstract_database_repository import AbstractDatabaseRepository, CrudActions
from ..service_layer.schemas.taskfilter_schemas import TaskFilterResponse


class TaskfiltersDatabaseRepository(AbstractDatabaseRepository):
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
        # rules_schema_str = schema.model_dump_json(include=("rules"), exclude_none=True)
        # other_fields_as_dict = schema.model_dump(exclude=("rules"), exclude_none=True)
        # rules_dict = {"rules": rules_schema_str}
        # all_fields = other_fields_as_dict | rules_dict
        # model = Taskfilters(**all_fields)

        model = Taskfilters(
            **schema.model_dump(exclude_none=True, mode="json", round_trip=True)
        )
        return model

    async def dump_model_to_dict(self, model: DatabaseBaseModel) -> dict:
        # Dump database model to dictionary
        model_dump = model.to_dict()

        return model_dump

    async def dump_schema_to_dict(self, schema: BaseSchemaModel) -> dict:
        # Overrides parent class method
        model_as_dict = schema.model_dump(exclude_none=True)

        return model_as_dict

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
        """Return the database model class e.g. return Taskfilters"""
        return Taskfilters

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
