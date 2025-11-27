from typing import Union
from uuid import UUID


from app.repository_layer.task_filterset import TaskFilterParams
from app.repository_layer.abstract_database_repository import (
    AbstractDatabaseRepository,
)
from app.repository_layer.repository_exceptions import TasklyRepositoryException
from app.service_layer.schemas.task_schemas import (
    TaskResponse,
    TaskCreate,
    TaskUpdate,
)
from app.service_layer.service_exceptions import TasklyServiceException


class TaskService:
    def __init__(
        self,
        repository: AbstractDatabaseRepository,
    ):

        self.repository = repository

    async def _validate_update_or_create(self, data: Union[TaskUpdate, TaskCreate]):
        # Todo move validations for just task down a layer
        #  Keep cross model validations here

        """Handles validations done before calling repository_layer to update request_data.
        Note basic request_data type validations are already done by pydantic. This logic
        caters for specific business rules and relationships between domain entities"""
        if isinstance(data, TaskUpdate):
            if not await self.get(id=data.id):
                raise ValueError
        #     raise TasklyDataNotFound(id=data.id)

        # Unique task name for given parent (including null parent or root case)
        # Todo fix me
        # if await self.get(name__match=request_data.name):
        #     raise TasklyDuplicateData(message=f"Task '{request_data.name}' already exists'")

        # Task types only allow certain fields

    async def _validate_delete(self, _id):
        pass

    async def create(
        self,
        create_schema: TaskCreate,
        commit=True,
    ) -> TaskResponse:
        """
        Create a new record in the database_manager.
        Args:
            create_schema: The Pydantic schema containing the request_data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.
        Returns:
            The created request_data in the type specified in return_type
        """
        await self._validate_update_or_create(data=create_schema)
        res = await self.repository.create(
            data=create_schema,
            commit=commit,
        )
        return TaskResponse.model_validate(res)

    async def get(
        self,
        id: UUID,
    ) -> TaskResponse:
        """
        Create a new record in the database_manager.
        Args:
            id: The UUID for the requested resource
        Returns:
            The retrieved request_data in the type specified in return_type or None
        """
        try:
            res = await self.repository.get(primary_key=id)
        except TasklyRepositoryException as e:
            raise TasklyServiceException(
                error_message=e.error_message, status_code=e.status_code
            ) from e

        return TaskResponse.model_validate(res)

    async def update(
        self,
        id: UUID,
        update_schema: TaskUpdate,
        commit=True,
    ) -> TaskResponse:
        """
        Updates an existing record or multiple records in the database_manager based on specified filters. This method allows for precise targeting of records to update.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            update_schema: A Pydantic schema containing the update request_data.
            commit: If `True`, commits the transaction immediately. Default is `True`.

        Returns:
            The updated request_data in the type specified in return_type or None

        Raises:
            TasklyDataNotFound: If no record matches the filters.
        """

        await self._validate_update_or_create(data=update_schema)

        res = await self.repository.update(
            data=update_schema,
            commit=commit,
            id=id,
        )
        return TaskResponse.model_validate(res)

    async def delete(
        self,
        id: UUID,
        commit: bool = False,
    ) -> None:
        """
        Deletes a record or multiple records from the database_manager based on specified filters.

        For filtering details see [the Advanced Filters documentation](../advanced/crud.md/#advanced-filters)

        Args:
            id: UUID of the record to delete
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
        res = await self.repository.delete(commit=commit, id=id)
        return res

    async def get_multi(self, filter_params: TaskFilterParams) -> list[TaskResponse]:
        """
        Fetches multiple records based on filters, supporting sorting and pagination.

        Args:
            filter_params: parameters used to filter and sort including pagination
        Returns:
            A list of the type specified in return_type
        """
        results = await self.repository.get_multi(filter_params=filter_params)
        result_schema = [TaskResponse.model_validate(item) for item in results]
        return result_schema
