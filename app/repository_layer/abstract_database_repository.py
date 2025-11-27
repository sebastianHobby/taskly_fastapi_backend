from abc import abstractmethod, ABC
from enum import Enum
from typing import Sequence, Any, TypedDict
from typing import (
    Union,
)
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repository_layer.models.models import DatabaseBaseModel
from app.repository_layer.repository_exceptions import TasklyRepositoryException


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

    @abstractmethod
    async def validate_filter_params(
        self, filter_params: dict, action: CrudActions
    ) -> dict:
        """Used to check if filter params are valid, note this is only used in get_multi at the moment
        but filters could also be used for updates,deletes etc in future.
        Returns validated filter_params as dict"""
        return filter_params

    @abstractmethod
    async def get_filterset(self, params: dict, session: AsyncSession) -> Any:
        """Returns a SQLAlchemy statement object for the appropriate model class
        e.g.
        base_query = select(Project) # equivalent to select * from [project table]
        filterset  = TaskFilterset(session=session,query=base_query)"""
        pass

    @property
    @abstractmethod
    async def model_class(self):
        """Return the database model class e.g. return Project"""
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
        self, filter_params: BaseSchemaModel, action: CrudActions, session: AsyncSession
    ) -> Sequence[DatabaseBaseModel]:
        """Applies filter rules based on parameters and filterset rules retrieved from get_filterset.
        Returns list of database model objects or empty list"""

        # Make pagination mandatory for all requests.
        if not hasattr(filter_params, "page") or not hasattr(
            filter_params, "itemsPerPage"
        ):
            raise TasklyRepositoryException(
                error_message=f"Mandatory pagination values missing (page and itemsPerPage)",
                status_code=409,
            )

        # Convert pagination values to limit/offset model supported by Filterset utility
        params_dict = filter_params.model_dump(
            exclude_none=True, exclude=("page", "itemsPerPage")
        )
        limit = filter_params.page
        offset = filter_params.itemsPerPage * limit - 1
        params_dict["pagination"] = (limit, offset)

        validated_parms_dict = await self.validate_filter_params(
            filter_params=params_dict, action=action
        )
        # Filterset defines the rules and builds SQL query using SQLAlchemy
        # We use passed in session as the filter may be after an update/have pending data and we do not
        # want to end previous session (e.g. session started by GET)
        filterset = await self.get_filterset(
            session=session, params=validated_parms_dict
        )

        await self.post_processing(
            request_action=CrudActions.FILTER, request_data=filter_params
        )

        return await filterset.filter(validated_parms_dict)

    async def get_multi(
        self,
        filter_params: BaseSchemaModel,
    ) -> list[dict]:
        """
        Fetches multiple records based on filters, supporting sorting, pagination.

        Args:
            filter_params: A schema with filter params.
        Returns:
            A list of dictionaries representing the retrieved records
        """
        session = self.session_factory()
        # Filter method will call validation and post processing which subclasses can override
        # so no calls here for get_multi
        model_list = await self.filter(
            session=session, filter_params=filter_params, action=CrudActions.READ
        )
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

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
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

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

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
