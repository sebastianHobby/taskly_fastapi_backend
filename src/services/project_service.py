from contextlib import AbstractContextManager
from typing import Callable, Optional
from uuid import UUID

from fastcrud.types import *
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session

from src.core.exceptions import (
    TasklyDuplicateData,
    TasklyDataNotFound,
)
from src.filtersets.filtersets import ProjectFilterParams
from src.repository.database_repository import DatabaseRepository, DataReturnTypes
from src.schemas.project_schemas import ProjectResponse, ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(
        self,
        repository: DatabaseRepository,
    ):

        self.repository = repository

    async def _validate_update_or_create(
        self, data: Union[ProjectUpdate, ProjectCreate]
    ):
        """Handles validations done before calling repository to update data.
        Note basic data type validations are already done by pydantic. This logic
        caters for specific business rules and relationships between domain entities"""
        if isinstance(data, ProjectUpdate):
            if not await self.get(id=data.id):
                raise TasklyDataNotFound(id=data.id)

        # Unique project name for given parent (including null parent or root case)
        # Todo fix me
        # if await self.get(name__match=data.name):
        #     raise TasklyDuplicateData(message=f"Project '{data.name}' already exists'")

        # Project types only allow certain fields

    async def _validate_delete(self, _id):
        pass

    async def create(
        self,
        create_schema: CreateSchemaType,
        commit=True,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Union[ProjectResponse | dict]:
        """
        Create a new record in the database_manager.
        Args:
            create_schema: The Pydantic schema containing the data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            return_type: Data type to return results
        Returns:
            The created data in the type specified in return_type
        """
        await self._validate_update_or_create(data=create_schema)
        res = await self.repository.create(
            object=create_schema,
            commit=commit,
            return_type=return_type,
        )
        return res

    async def get(
        self,
        id: UUID,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> Union[ProjectResponse | dict | None]:
        """
        Create a new record in the database_manager.
        Args:
            id: The UUID for the requested resource
            return_type: Data type to return results
        Returns:
            The retrieved data in the type specified in return_type or None
        """

        res = await self.repository.get(primary_key=id, return_type=return_type)
        if not res:
            raise TasklyDataNotFound(id=id)
        return res

    async def update(
        self,
        update_schema: ProjectUpdate,
        commit=True,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ) -> ProjectResponse:
        """
        Updates an existing record or multiple records in the database_manager based on specified filters. This method allows for precise targeting of records to update.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            update_schema: A Pydantic schema containing the update data.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            return_type: Data type to return results

        Returns:
            The updated data in the type specified in return_type or None

        Raises:
            TasklyDataNotFound: If no record matches the filters.
        """

        await self._validate_update_or_create(data=update_schema)

        res = await self.repository.update(
            update_schema=update_schema,
            commit=commit,
            return_type=return_type,
        )
        return res

    async def delete(
        self,
        primary_key: UUID,
        commit: bool = False,
    ) -> None:
        """
        Deletes a record or multiple records from the database_manager based on specified filters.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            primary_key: UUID of the record to delete
            commit: If `True`, commits the transaction immediately. Default is `True`.
        Returns:
            None

        Raises:
            MultipleResultsFound: If more than one record matches the filters.

        Examples:
            Delete a user based on their ID using kwargs:

            ```python
            await user_crud.db_delete(_id=1)

        """
        res = await self.repository.delete(commit=commit, id=primary_key)

        return None

    async def get_multi(
        self,
        filter_params: ProjectFilterParams,
        return_type: DataReturnTypes = DataReturnTypes.dictionary,
    ):
        """
        Fetches multiple records based on filters, supporting sorting and pagination.

        Args:
            session: async database_manager session
            filter_params: parameters used to filter and sort including pagination
            return_type: Data type to return results
        Returns:
            A list of the type specified in return_type
        """
        return await self.repository.get_multi(
            return_type=return_type, filter_params=filter_params
        )
