from contextlib import AbstractContextManager
from http import HTTPStatus
from typing import Callable, Optional
from uuid import UUID

from fastcrud import FastCRUD
from fastcrud.types import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.schemas.TaskSchemas import TaskResponse, TaskCreate, TaskUpdate
from src.core.exceptions import (
    TasklyServiceException,
    TasklyDataNotFound,
    TasklyDuplicateData,
)


class TasklyTaskService:
    def __init__(
        self,
        database_session_factory: Callable[..., AbstractContextManager[Session]],
        task_repository: FastCRUD,
    ):

        self.repository = task_repository
        self.database_session_factory = database_session_factory

    async def _validate_update_or_create(self, data: Union[TaskUpdate, TaskCreate]):
        """Handles validations done before calling repository to update data.
        Note basic data type validations are already done by pydantic. This logic
        caters for specific business rules and relationships between domain entities"""
        if isinstance(data, TaskUpdate):
            if not await self.exists(id=data.id):
                raise TasklyDataNotFound(id=data.id)
        if await self.exists(name=data.name, parent_group_id=data.project_id):
            raise TasklyDuplicateData(
                message=f"Task '{data.name}' already exists under project '{data.parent_list_id}'",
            )
        elif await self.exists(name=data.name, parent_group_id=data.parent_task_id):
            raise TasklyDuplicateData(
                message=f"Task '{data.name}' already exists under parent task Id '{data.parent_task_id}'",
            )

    async def _validate_delete(self, _id):
        pass

    async def create(
        self, create_schema: CreateSchemaType, commit=True
    ) -> TaskResponse:
        """
        Create a new record in the database_manager.
        Args:
            create_schema: The Pydantic schema containing the data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.

        Returns:
            The created Pydantic model representing the data created
        """
        async with self.database_session_factory() as session:
            await self._validate_update_or_create(data=create_schema)
            res = await self.repository.create(
                db=session,
                object=create_schema,
                commit=commit,
                schema_to_select=TaskResponse,
                return_as_model=True,
            )
            return res

    async def get(self, _id: UUID) -> TaskResponse:
        """
        Create a new record in the database_manager.
        Args:
            _id: The UUID for the requested resource
        Raises:
            MultipleResultsFound if multiple matches for ID found
        Returns:
            The created Pydantic model representing the data created
        """
        async with self.database_session_factory() as session:
            res = await self.repository.get(
                db=session,
                schema_to_select=TaskResponse,
                return_as_model=True,
                one_or_none=True,
                id=_id,
            )
            if not res:
                raise TasklyServiceException(
                    status=HTTPStatus.NOT_FOUND,
                    message=f"Resource for primary_key {_id} not found",
                )
            return res

    async def update(
        self,
        update_schema: TaskCreate,
        commit=True,
    ) -> TaskResponse:
        """
        Updates an existing record or multiple records in the database_manager based on specified filters. This method allows for precise targeting of records to update.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            update_schema: A Pydantic schema containing the update data.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            primary_key: UUID of the record to update.

        Returns:
            The updated record as Pydantic model instance

        Raises:
            MultipleResultsFound: IMore than one record matches the ID given.
            NoResultFound: If no record matches the filters.
            ValueError: If extra fields not present in the model are provided in the update data.
        """
        async with self.database_session_factory() as session:

            await self._validate_update_or_create(data=update_schema)

            res = await self.repository.update(
                db=session,
                object=update_schema,
                allow_multiple=False,
                commit=commit,
                id=update_schema.id,
                schema_to_select=TaskResponse,
                return_as_model=True,
            )

            return res

    async def exists(self, session: AsyncSession = None, **kwargs) -> bool:
        """
        Checks if any records exist that match the given filter conditions.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            **kwargs: Filters to apply to the query, supporting both direct matches and advanced comparison operators
            for refined search criteria.

        Returns:
            `True` if at least one record matches the filter conditions, `False` otherwise.

        Examples:
            Check if a user with a specific ID exists:

            ```python
            exists = await user_crud.exists(session, primary_key=1)
            ```

            Check if any user is older than 30:

            ```python
            exists = await user_crud.exists(session, age__gt=30)
            ```

            Check if any user was registered before Jan 1, 2020:

            ```python
            exists = await user_crud.exists(session, registration_date__lt=datetime(2020, 1, 1))
            ```

            Check if a username other than `admin` exists:

            ```python
            exists = await user_crud.exists(session, username__ne='admin')
            ```
        """
        if session:
            # Calling method has provided session
            res = await self.repository.exists(db=session, **kwargs)
            return res
        else:
            async with self.database_session_factory() as session:
                res = await self.repository.exists(db=session, **kwargs)
                return res

    async def delete(
        self,
        _id: UUID,
        commit: bool = False,
    ) -> None:
        """
        Deletes a record or multiple records from the database_manager based on specified filters.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            _id: UUID of the record to delete
            commit: If `True`, commits the transaction immediately. Default is `True`.
        Returns:
            None

        Raises:
            MultipleResultsFound: If more than one record matches the filters.

        """
        async with self.database_session_factory() as session:
            res = await self.repository.db_delete(
                db=session,
                allow_multiple=False,
                commit=commit,
                id=_id,
            )
            return res

    async def upsert(
        self,
        data: Union[TaskUpdate, TaskCreate],
    ) -> TaskResponse:
        """Update the instance or create it if it doesn't exist.

        Note: This method will perform two transactions to the database_manager (get and create or update).

        Args:
            data: A Pydantic schema instance representing the instance either for update or creation.
        Returns:
            The created or updated instance:
        """
        async with self.database_session_factory() as session:
            await self._validate_update_or_create(data=data)

            res = await self.repository.upsert(
                db=session,
                instance=data,
                schema_to_select=TaskResponse,
                return_as_model=True,
            )
            return res

    async def get_multi(
        self,
        offset: int = 0,
        limit: Optional[int] = 100,
        sort_columns: Optional[Union[str, list[str]]] = None,
        sort_orders: Optional[Union[str, list[str]]] = None,
        return_total_count: bool = True,
        **kwargs: Any,
    ):
        """
        Fetches multiple records based on filters, supporting sorting, pagination.
        For supported filtering details see FastCrud doco at [the Advanced Filters documentation]

        Args:
            offset: Starting index for records to fetch, useful for pagination.
            limit: Maximum number of records to fetch in one call. Use `None` for "no limit", fetching all matching rows.
             Note that in order to use `limit=None`, you'll have to provide a custom endpoint to facilitate it,
             which you should only do if you really seriously want to allow the user to get all the data at once.
            sort_columns: Column names to sort the results by.
            sort_orders: Corresponding sort orders (`"asc"`, `"desc"`) for each column in `sort_columns`.
            return_total_count: If `True`, return the total number of records.
            **kwargs: Filters to apply to the query, including advanced comparison operators for more detailed querying.
        Returns:
            A dictionary containing Dict with "data": Task[SelectSchemaType] and
            "total_count": int
        Raises:
            ValueError: If `limit` or `offset` is negative
        """
        async with self.database_session_factory() as session:
            res = await self.repository.get_multi(
                db=session,
                offset=offset,
                limit=limit,
                schema_to_select=TaskResponse,
                return_as_model=True,
                sort_columns=sort_columns,
                sort_orders=sort_orders,
                return_total_count=return_total_count,
                **kwargs,
            )
            return res

    async def upsert_multi(
        self, instances: list[Union[TaskUpdate, TaskCreate]], commit: bool
    ) -> UpsertMultiResponseModel[TaskResponse]:
        """
        Upsert multiple records in the database_manager. The underlying implementation varies based on the database_manager dialect.

        Args:
            instances: A task of Pydantic schemas representing the instances to upsert.
            commit: If True, commits the transaction immediately. Default is False.

        Returns:
            The upserted records as a dictionary containing the operation results:
                UpsertMultiResponseModel[SelectSchemaType](`Dict[str, Task[SelectSchemaType]]`)
            The dictionary contains keys like "updated" and "created" with tasks of corresponding records.

        Raises:
            ValueError: If the MySQL dialect is used with filters, return_columns, schema_to_select, or return_as_model.
            NotImplementedError: If the database_manager dialect is not supported for upsert multi.
        """
        async with self.database_session_factory() as session:
            for obj in instances:
                await self._validate_update_or_create(data=obj)
            res = await self.repository.upsert_multi(
                db=session,
                instances=instances,
                commit=commit,
                schema_to_select=TaskResponse,
                return_as_model=True,
            )
            return res
