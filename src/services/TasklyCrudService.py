"""Services layer is also known as orchestration layer.
API layer (routes) handles web stuff
Service layer handles any business rules and depends on Repository for access to data
API layer/Presentation --> Service Layer --> Repository
Note this is primarily to allow dependency injection and easy mocking/limiting cost of future changes
See https://github.com/cosmicpython/book/blob/master/chapter_04_service_layer.asciidoc
"""

import uuid
from contextlib import AbstractContextManager
from typing import Any, Callable, Generic, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from pydantic import BaseModel as BaseSchemaModel

from src.schemas.TaskListSchemas import TaskListResponse, TaskListCreate
from fastcrud import FastCRUD
from fastcrud.types import *


class TasklyCrudService(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        UpdateSchemaInternalType,
        DeleteSchemaType,
        SelectSchemaType,
    ]
):
    """Defines generic CRUD operations - depends on FastCrud framework as repository.
    When business rules need to be added to service layer specific to a type simply subclass
    this method apply your business rules and call the parent class for basic CRUD.
    Service layer restricts functionality to sensible defaults"""

    def __init__(
        self,
        database_session_factory: Callable[..., AbstractContextManager[Session]],
        fastcrud_repository: FastCRUD,
        select_schema: SelectSchemaType,
    ):

        self.fastcrud_repository = fastcrud_repository
        self.database_session_factory = database_session_factory
        self.select_schema = select_schema

    async def create(
        self, create_schema: CreateSchemaType, commit=True
    ) -> SelectSchemaType:
        """
        Create a new record in the database.
        Args:
            create_schema: The Pydantic schema containing the data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.

        Returns:
            The created Pydantic model representing the data created
        """
        async with self.database_session_factory() as session:

            res = await self.fastcrud_repository.create(
                db=session,
                object=create_schema,
                commit=commit,
                schema_to_select=self.select_schema,
                return_as_model=True,
            )
            return res

    async def get(self, id_: UUID) -> SelectSchemaType:
        """
        Create a new record in the database.
        Args:
            id_: The UUID for the requested resource
        Raises:
            MultipleResultsFound if multiple matches for ID found
        Returns:
            The created Pydantic model representing the data created
        """
        async with self.database_session_factory() as session:

            res = await self.fastcrud_repository.get(
                db=session,
                schema_to_select=self.select_schema,
                return_as_model=True,
                one_or_none=True,
                id=id_,
            )
            return res

    async def update(
        self,
        _id: UUID,
        update_schema: UpdateSchemaType,
        commit=True,
    ) -> SelectSchemaType:
        """
        Updates an existing record or multiple records in the database based on specified filters. This method allows for precise targeting of records to update.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            db: The database session to use for the operation.
            update_schema: A Pydantic schema containing the update data.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            id_: UUID of the record to update.

        Returns:
            The updated record as Pydantic model instance

        Raises:
            MultipleResultsFound: IMore than one record matches the ID given.
            NoResultFound: If no record matches the filters.
            ValueError: If extra fields not present in the model are provided in the update data.
        """
        async with self.database_session_factory() as session:

            res = await self.fastcrud_repository.update(
                db=session,
                object=update_schema,
                allow_multiple=False,
                commit=commit,
                id=_id,
                schema_to_select=self.select_schema,
                return_as_model=True,
            )

            return res

    async def exists(self, **kwargs) -> bool:
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
            exists = await user_crud.exists(db, id=1)
            ```

            Check if any user is older than 30:

            ```python
            exists = await user_crud.exists(db, age__gt=30)
            ```

            Check if any user was registered before Jan 1, 2020:

            ```python
            exists = await user_crud.exists(db, registration_date__lt=datetime(2020, 1, 1))
            ```

            Check if a username other than `admin` exists:

            ```python
            exists = await user_crud.exists(db, username__ne='admin')
            ```
        """
        async with self.database_session_factory() as session:
            res = await self.fastcrud_repository.exists(**kwargs)
            return res

    async def db_delete(
        self,
        _id: UUID,
        commit: bool = False,
    ) -> None:
        """
        Deletes a record or multiple records from the database based on specified filters.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            _id: UUID of the record to delete
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
        async with self.database_session_factory() as session:
            res = await self.fastcrud_repository.delete(
                db=session,
                allow_multiple=False,
                commit=commit,
                id_=_id,
            )
            return res

    async def upsert(
        self,
        data: Union[UpdateSchemaType, CreateSchemaType],
    ) -> SelectSchemaType:
        """Update the instance or create it if it doesn't exist.

        Note: This method will perform two transactions to the database (get and create or update).

        Args:
            data: A Pydantic schema instance representing the instance either for update or creation.
        Returns:
            The created or updated instance:
        """
        async with self.database_session_factory() as session:
            res = await self.fastcrud_repository.upsert(
                db=session,
                instance=data,
                schema_to_select=self.select_schema,
                return_as_model=True,
            )
            return res

    async def get_multi(
        self,
        offset: int = 0,
        limit: Optional[int] = 100,
        sort_columns: Optional[Union[str, list[str]]] = None,
        sort_orders: Optional[Union[str, list[str]]] = None,
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
            **kwargs: Filters to apply to the query, including advanced comparison operators for more detailed querying.
        Returns:
            A dictionary containing Dict with "data": List[SelectSchemaType] and
            "total_count": int
        Raises:
            ValueError: If `limit` or `offset` is negative
        """
        async with self.database_session_factory() as session:
            res = await self.fastcrud_repository.get_multi(
                db=session,
                offset=offset,
                limit=limit,
                schema_to_select=self.select_schema,
                return_as_model=True,
                sort_columns=sort_columns,
                sort_orders=sort_orders,
            )

    async def upsert_multi(
        self, instances: list[Union[UpdateSchemaType, CreateSchemaType]], commit: bool
    ) -> UpsertMultiResponseModel[SelectSchemaType]:
        """
        Upsert multiple records in the database. The underlying implementation varies based on the database dialect.

        Args:
            instances: A list of Pydantic schemas representing the instances to upsert.
            commit: If True, commits the transaction immediately. Default is False.

        Returns:
            The upserted records as a dictionary containing the operation results:
                UpsertMultiResponseModel[SelectSchemaType](`Dict[str, List[SelectSchemaType]]`)
            The dictionary contains keys like "updated" and "created" with lists of corresponding records.

        Raises:
            ValueError: If the MySQL dialect is used with filters, return_columns, schema_to_select, or return_as_model.
            NotImplementedError: If the database dialect is not supported for upsert multi.
        """
        async with self.database_session_factory() as session:
            res = await self.fastcrud_repository.upsert_multi(
                db=session,
                instances=instances,
                commit=commit,
                schema_to_select=self.select_schema,
                return_as_model=True,
            )
            return res


# Todo review below select function from FastCrud for use in filters
# async def select(
#      self,
#      schema_to_select: Optional[type[SelectSchemaType]] = None,
#      sort_columns: Optional[Union[str, list[str]]] = None,
#      sort_orders: Optional[Union[str, list[str]]] = None,
#      **kwargs: Any,
#  ) -> Select:
#      """
#      Constructs a SQL Alchemy `Select` statement with optional column selection, filtering, and sorting.
#
#      This method allows for advanced filtering through comparison operators, enabling queries to be refined beyond simple equality checks.
#
#      For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)
#
#      Args:
#          schema_to_select: Pydantic schema to determine which columns to include in the selection. If not provided, selects all columns of the model.
#          sort_columns: A single column name or list of column names to sort the query results by. Must be used in conjunction with `sort_orders`.
#          sort_orders: A single sort order (`"asc"` or `"desc"`) or a list of sort orders, corresponding to each column in `sort_columns`. If not specified, defaults to ascending order for all `sort_columns`.
#          **kwargs: Filters to apply to the query, including advanced comparison operators for more detailed querying.
#
#      Returns:
#          An SQL Alchemy `Select` statement object that can be executed or further modified.
#
#      Examples:
#          Selecting specific columns with filtering and sorting:
#
#          ```python
#          stmt = await user_crud.select(
#              schema_to_select=ReadUserSchema,
#              sort_columns=['age', 'name'],
#              sort_orders=['asc', 'desc'],
#              age__gt=18,
#          )
#          ```
#
#          Creating a statement to select all users without any filters:
#
#          ```python
#          stmt = await user_crud.select()
#          ```
#
#          Selecting users with a specific `role`, ordered by `name`:
#
#          ```python
#          stmt = await user_crud.select(
#              schema_to_select=UserReadSchema,
#              sort_columns='name',
#              role='admin',
#          )
#          ```
#
#      Note:
#          This method does not execute the generated SQL statement.
#          Use `db.execute(stmt)` to run the query and fetch results.
#      """
#      to_select = extract_matching_columns_from_schema(
#          model=self.model, schema=schema_to_select
#      )
#      filters = self._filter_processor.parse_filters(**kwargs)
#      stmt = select(*to_select).filter(*filters)
#
#      if sort_columns:
#          stmt = self._query_builder.apply_sorting(stmt, sort_columns, sort_orders)
#      return stmt
