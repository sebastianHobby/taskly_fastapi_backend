from enum import Enum
from typing import Annotated, Callable
from typing import (
    Generic,
    Union,
    Optional,
    TypeVar,
)
from uuid import UUID

from dependency_injector.wiring import Provide, inject, Container
from pydantic import BaseModel as BaseSchemaModel, TypeAdapter
from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.core.databasemanager import DatabaseManager
from src.core.exceptions import TasklyDataNotFound
from src.filtersets.filtersets import ProjectFilterSet
from src.models.database_mixins import DatabaseBaseModel


DatabaseModelType = TypeVar("DatabaseModelType", bound=DatabaseBaseModel)
ResponseSchemaType: TypeVar = TypeVar("ResponseSchemaType", bound=BaseSchemaModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchemaModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchemaModel)
FilterQueryParamType = TypeVar("FilterQueryParamType", bound=BaseSchemaModel)
FiltersetType = TypeVar("FiltersetType", bound=BaseSchemaModel)


class DataReturnTypes(Enum):
    dictionary = "dict"
    request_schema = "request_schema"


class DatabaseRepository(
    Generic[
        DatabaseModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ResponseSchemaType,
        FilterQueryParamType,
        FiltersetType,
    ]
):
    """
    Base class for CRUD operations on a model.

    This class provides a set of methods for create, read, update, and delete operations on a given SQLAlchemy model,
    utilizing Pydantic schemas for data validation and serialization.

    Args:
        model: The SQLAlchemy model type.

    Methods:
        create:
            Creates a new record in the database_manager from the provided Pydantic schema.

        select:
            Generates a SQL Alchemy `Select` statement with optional filtering and sorting.

        get:
            Retrieves a single record based on Id


        get_multi:
            Fetches multiple records with optional sorting, pagination, and model conversion.

        update:
            Updates an existing record or multiple records based on specified filters.

        delete:
            Hard deletes a record or multiple records from the database_manager based on provided filters.

    """

    def __init__(
        self,
        model: type[DatabaseModelType],
        response_schema: type[ResponseSchemaType],
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self.model = model
        self.response_schema = response_schema
        self.session_factory = session_factory

    async def create(
        self,
        object: CreateSchemaType,
        commit: bool = True,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Union[ResponseSchemaType, dict]:
        """
        Create a new record in the database_manager.

        Args:
            session: The SQLAlchemy async session.
            object: The Pydantic schema containing the data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            return_type: Enum to choose what format to return data in
        Returns:
            The data type defined in return_type
        """

        session = self.session_factory()

        object_dict = object.model_dump()
        db_object: DatabaseModelType = self.model(**object_dict)
        session.add(db_object)

        if commit:
            await session.commit()
            await session.refresh(db_object)
        else:
            await session.flush()
            await session.refresh(db_object)

        data_dict = db_object.to_dict()
        if return_type is DataReturnTypes.request_schema:
            return self.response_schema(**data_dict)
        elif return_type is DataReturnTypes.dictionary:
            return data_dict
        else:
            raise NotImplementedError

    async def get(
        self,
        primary_key: UUID,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Union[dict | ResponseSchemaType | None]:
        """
        Fetches a single record based on Id

        Args:
            primary_key: UUID of the required resource
            return_type: Enum to choose what format to return data in
        Returns:
            The retrieved data as a Pydantic model if `schema_to_select` is provided else as a dictionary.
        """
        session = self.session_factory()

        db_obj = session.get(self.model, primary_key)
        if db_obj is None:
            return None

        if return_type is DataReturnTypes.request_schema:
            return TypeAdapter.validate_python(list[ResponseSchemaType], db_obj)
        elif return_type is DataReturnTypes.dictionary:
            data_dict = db_obj.to_dict()
            return data_dict
        else:
            raise NotImplementedError

    async def get_multi(
        self,
        filter_params: FilterQueryParamType,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Union[list[dict] | list[ResponseSchemaType]]:
        """
        Fetches multiple records based on filters, supporting sorting, pagination.

        Args:
            filter_params: A schema with filter params.
            return_type: Enum to choose what format to return data in
        Returns:
            A list of the type in return_type
        """
        session = self.session_factory()
        query = select(self.model)
        params = filter_params.model_dump(exclude_none=True)
        filterset_tmp = ProjectFilterSet(session=session, query=query)
        filtered_results = await filterset_tmp.filter(params)

        if return_type is DataReturnTypes.request_schema:
            return TypeAdapter.validate_python(
                list[ResponseSchemaType], filtered_results
            )
        elif return_type is DataReturnTypes.dictionary:
            data_dict = [obj.to_dict() for obj in filtered_results]
            return data_dict
        else:
            raise NotImplementedError

    async def update(
        self,
        update_schema: UpdateSchemaType,
        commit: bool = True,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Optional[Union[dict, ResponseSchemaType]]:
        """
        Updates an existing record or multiple records in the database_manager based on specified filters. This method allows for precise targeting of records to update.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            update_schema: A Pydantic schema  containing the update data.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            return_type: Enum to choose what format to return data in
        Returns:
            The updated record(s) as the type specified in return_type
        """
        session = self.session_factory()
        db_object = session.get(self.model, update_schema.id)

        if db_object is None:
            raise TasklyDataNotFound(id)

        stmt = update(db_object).values(update_schema.model_dump()).returning(db_object)
        result = await session.execute(stmt)

        if commit:
            await session.commit()
            await session.refresh(db_object)
        else:
            await session.flush()
            await session.refresh(db_object)

        if return_type is DataReturnTypes.request_schema:
            return TypeAdapter.validate_python(ResponseSchemaType, result)
        elif return_type is DataReturnTypes.dictionary:
            return result.to_dict
        else:
            raise NotImplementedError

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
        db_object = session.get(self.model, id)
        if db_object is None:
            raise TasklyDataNotFound(id)
        await session.delete(db_object)
        if commit:
            await session.commit()
            await session.refresh(db_object)
        else:
            await session.flush()
            await session.refresh(db_object)
