from abc import abstractmethod, ABC
from enum import Enum
from typing import Sequence, Any
from typing import (
    Union,
)
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repository_layer.exceptions_repository import TasklyRepositoryException
from app.repository_layer.models.models import DatabaseBaseModel
from app.repository_layer.util_search_manager import (
    RepositoryCommonSearchFieldManager,
)
from app.service_layer.schemas.common_field_search_schema import (
    CommonSearchFieldsSchema,
)


class CrudActions(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    FILTER = "filter"


class AbstractDatabaseRepository(ABC):
    """
    Base class for CRUD operations on a model.

    This class provides a set of methods for create, read, update, and delete operations on a given SQLAlchemy model.

    Methods:
        create:
            Creates a new record in the database the provided Pydantic schema.
        filter:
            Generates a SQL Alchemy `Select` statement based on input filter parameters
        get:
            Retrieves a single record based on Id
        get_multi:
            Fetches multiple records with optional filtering (including sorting and grouping)
        update:
            Updates an existing record or multiple records based on specified filters.

        delete:
            Hard deletes a record or multiple records from the database_manager based on provided filters.

    """

    @abstractmethod
    async def create_model_obj_from_schema(
        self, schema: BaseSchemaModel
    ) -> DatabaseBaseModel:
        """
        :return: SQLAlchemy model request_data created from the provided dictionary
        :raises: TasklyRepositoryException if the schema class is wrong or can not be mapped
            to database model for any reason
        """
        pass

    @abstractmethod
    async def dump_model_to_dict(self, model: DatabaseBaseModel) -> dict:
        return model.to_dict(nested=False, exclude=None)

    @abstractmethod
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

    @property
    @abstractmethod
    async def model_class(self):
        """Return the database model class e.g. return Projects"""
        pass

    @property
    @abstractmethod
    def session_factory(self) -> async_sessionmaker:
        pass

    @abstractmethod
    async def post_processing(
        self,
        request_action: CrudActions,
        model: DatabaseBaseModel = None,
        request_data: BaseSchemaModel = None,
        request_id: UUID = None,
    ) -> BaseSchemaModel:
        pass

    async def _get_by_id(
        self, id: Any, session: AsyncSession, at_least_one_required=True
    ) -> DatabaseBaseModel:
        """Returns exactly one instance of database model based on primary key
        Parameters:
            id - Primary key of the resource
            session - SQLAlchemy session
            at_least_one_required - If true, raise error if no results found
        Raises:
            TasklyRepositoryError if no data is found and at least_one_required is True
        """
        model = await session.get(await self.model_class, id)
        if model is None and at_least_one_required:
            raise TasklyRepositoryException(
                error_message=f"Resource not found with id:{id}", status_code=404
            )
        return model

    async def create(
        self,
        data: BaseSchemaModel,
        commit: bool = True,
    ) -> dict:
        """
        Create a new record in the database_manager.
        Args:
            data: The Pydantic schema containing the request_data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.
        Returns:
            Dictionary of updated request_data
        """

        session = self.session_factory()

        # Hook to allow child classes to implement their own validations
        await self.validate(
            request_data=data, request_action=CrudActions.CREATE, request_id=None
        )

        model = await self.create_model_obj_from_schema(data)
        session.add(model)
        if commit:
            await session.commit()
            await session.refresh(model)
        else:
            await session.flush()
            await session.refresh(model)

        # Hook to allow child classes to perform custom post process
        await self.post_processing(
            model=model, request_action=CrudActions.CREATE, request_data=data
        )
        return await self.dump_model_to_dict(model)

    async def get(
        self,
        primary_key: UUID,
    ) -> Union[dict | None]:
        """
        Fetches a single record based on Id

        Args:
            primary_key: UUID of the required resource
        Returns:
            The retrieved request_data as a dictionary
        """
        session = self.session_factory()

        # Hook to allow child classes to implement their own validations
        await self.validate(
            request_id=primary_key,
            request_action=CrudActions.READ,
        )

        model = await self._get_by_id(session=session, id=primary_key)

        await self.post_processing(
            model=model, request_id=primary_key, request_action=CrudActions.READ
        )

        return await self.dump_model_to_dict(model)

    async def filter(
        self,
        filter_params: CommonSearchFieldsSchema,
        session: AsyncSession = None,
    ) -> Sequence[DatabaseBaseModel]:
        """Applies filter rules based on parameters and filterset rules retrieved from get_filterset.
        Returns list of database model objects or empty list"""

        if not isinstance(filter_params, CommonSearchFieldsSchema):
            # Only allow filters that are a subclass of CommonSearchFieldsSchema
            # This allows us to enforce pagination and a base interface search interface
            # for all models
            raise TasklyRepositoryException(
                error_message="Filter params must be an instance of/subclass instance of CommonSearchFieldsSchema",
                status_code=500,
            )

        if session is None:
            session = self.session_factory()

        base_query = select(await self.model_class)
        filterset = RepositoryCommonSearchFieldManager(
            session=session, query=base_query
        )
        filter_params_dict = filter_params.model_dump(exclude_none=True)
        filtered_result = await filterset.filter(filter_params_dict)
        await self.post_processing(
            request_action=CrudActions.FILTER, request_data=filter_params
        )

        return filtered_result

    async def get_multi(
        self,
        filter_params: CommonSearchFieldsSchema,
    ) -> list[dict]:
        """
        Fetches multiple records based on filters, supporting sorting, pagination.

        Args:
            filter_params: A schema with filter params.
        Returns:
            A list of dictionaries representing the retrieved records
        """
        # Check filter params are valid type.
        session = self.session_factory()
        # Taskfilters method will call validation and post processing which subclasses can override
        # so no calls here for get_multi
        model_list = await self.filter(session=session, filter_params=filter_params)
        model_list_dict = [await self.dump_model_to_dict(model=m) for m in model_list]
        return model_list_dict

    async def update(
        self,
        id: UUID,
        data: BaseSchemaModel,
        commit: bool = True,
    ) -> dict:
        """
        Updates an existing record based on Id

        For filtering details see [the Advanced Taskfilters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            id: Id of the record to update
            commit: If `True`, commits the transaction immediately. Default is `True`.
        Raises:
            TasklyRepositoryException if there is no resource matching the ID provided
        Returns:
            The updated record(s) as the type specified in return_type
        """
        session = self.session_factory()
        model = await self._get_by_id(session=session, id=id)

        # Hook to allow child classes to implement their own validations
        await self.validate(
            request_id=id, request_action=CrudActions.UPDATE, request_data=data
        )

        update_data_as_dict = data.model_dump(exclude_none=True)

        # Update ORM object and the values will be inserted at next commit
        for key, value in update_data_as_dict.items():
            if hasattr(model, key):
                setattr(model, key, value)
            else:
                raise TasklyRepositoryException(
                    error_message=f"Resource {model.__class__.__name__} does not have field {key} "
                )

        if commit:
            await session.commit()
            await session.refresh(model)
        else:
            await session.flush()
            await session.refresh(model)

        await self.post_processing(
            request_action=CrudActions.UPDATE, request_data=data, request_id=id
        )

        return await self.dump_model_to_dict(model)

    async def delete(
        self,
        id: UUID,
        commit: bool = True,
    ) -> None:
        """
        Deletes a record or multiple records from the database_manager based on specified filters.

        For filtering details see [the Advanced Taskfilters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            id: UUID of the resource you wish to delete
            commit: If `True`, commits the transaction immediately. Default is `True`.

        Returns:
            None
        """
        session = self.session_factory()
        # Standard validation applicable to all classes
        model = await self._get_by_id(session=session, id=id)
        # Hook to allow child classes to implement their own validations
        await self.validate(request_id=id, request_action=CrudActions.DELETE)

        await session.delete(model)
        if commit:
            await session.commit()
            await session.refresh(model)
        else:
            await session.flush()
            await session.refresh(model)

        await self.post_processing(request_action=CrudActions.DELETE, request_id=id)
        return None
