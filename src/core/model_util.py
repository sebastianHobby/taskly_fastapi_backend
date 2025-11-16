from typing import List
from uuid import UUID
from pydantic import BaseModel as ApiSchema

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
from src.core.database import SQLAlchemyBase

from src import models
from src.models import TaskContainerTypes, TaskContainer


class DataModelException(Exception):
    pass


class DataModelIntegrityConflictException(Exception):
    pass


class DataModelNotFound(Exception):
    pass


class ModelCrudFunctions:
    def __init__(self, model_class: SQLAlchemyBase) -> None:
        self.model_class = model_class

    def create(
        self,
        session: AsyncSession,
        data: ApiSchema,
    ) -> SQLAlchemyBase:
        """Accepts a Pydantic model, creates a new record in the database, catches
        any integrity errors, and returns the record.

        Args:
            session (AsyncSession): SQLAlchemy async session
            data (ApiSchema): Pydantic model

        Raises:
            DataModelIntegrityConflictException: if creation conflicts with existing data
            DataModelException: if an unknown error occurs

        Returns:
            DataModel: created SQLAlchemy model
        """
        try:
            db_model = self.model_class(**data.model_dump())
            session.add(db_model)
            session.commit()
            session.refresh(db_model)
            return db_model
        except IntegrityError:
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} conflicts with existing data.",
            )
        except Exception as e:
            raise DataModelException(f"Unknown error occurred: {e}") from e

    async def create_many(
        self,
        session: AsyncSession,
        data: list[ApiSchema],
        return_models: bool = False,
    ) -> list[SQLAlchemyBase] | bool:
        """_summary_

        Args:
            session (AsyncSession): SQLAlchemy async session
            data (list[ApiSchema]): list of Pydantic models
            return_models (bool, optional): Should the created models be returned
                or a boolean indicating they have been created. Defaults to False.

        Raises:
            IntegrityConflictException: if creation conflicts with existing data
            SnippetException: if an unknown error occurs

        Returns:
            list[DataModel] | bool: list of created SQLAlchemy models or boolean
        """
        db_models = [self.model_class(**d.model_dump()) for d in data]
        try:
            session.add_all(db_models)
            session.commit()
        except IntegrityError:
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} conflict with existing data.",
            )
        except Exception as e:
            raise DataModelException(f"Unknown error occurred: {e}") from e

        if not return_models:
            return True

        for m in db_models:
            session.refresh(m)

        return db_models

    def get_one_by_id(
        self,
        session: AsyncSession,
        id: str | UUID,
        column: str = "id",
        with_for_update: bool = False,
    ) -> SQLAlchemyBase:
        """Fetches one record from the database based on a column value and returns
        it, or returns None if it does not exist. Raises an exception if the column
        doesn't exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            id (str | UUID): value to search for in `column`.
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            with_for_update (bool, optional): Should the returned row be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            DataModelException: if the column does not exist on the model

        Returns:
            DataModel: SQLAlchemy model or None
        """
        try:
            q = select(self.model_class).where(getattr(self.model_class, column) == id)
        except AttributeError:
            raise DataModelException(
                f"Column {column} not found on {self.model_class.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = session.execute(q)
        return results.unique().scalar_one_or_none()

    def get_all(
        self,
        session: AsyncSession,
    ) -> List[SQLAlchemyBase]:
        """Fetches all records from the database for Project type

        Args:
            session (AsyncSession): SQLAlchemy async session
        Returns:
            DataModel: SQLAlchemy model or None
        """
        q = select(self.model_class)
        results = session.execute(q)
        return results.unique().scalars().all()

    def get_many_by_ids(
        self,
        session: AsyncSession,
        ids: list[str | UUID] = None,
        column: str = "uuid",
        with_for_update: bool = False,
    ) -> list[SQLAlchemyBase]:
        """Fetches multiple records from the database based on a column value and
        returns them. Raises an exception if the column doesn't exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            ids (list[str  |  UUID], optional): list of values to search for in
                `column`. Defaults to None.
            column (str, optional): the column name in which to search
                Defaults to "uuid".
            with_for_update (bool, optional): Should the returned rows be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            SnippetException: if the column does not exist on the model

        Returns:
            list[SnippetModel]: list of SQLAlchemy models
        """
        q = select(self.model_class)
        if ids:
            try:
                q = q.where(getattr(self.model_class, column).in_(ids))
            except AttributeError:
                raise DataModelException(
                    f"Column {column} not found on {self.model_class.__tablename__}.",
                )

        if with_for_update:
            q = q.with_for_update()

        rows = session.execute(q)
        return rows.unique().scalars().all()

    def update_by_id(
        self,
        session: AsyncSession,
        data: ApiSchema,
        id_: str | UUID,
        column: str = "id",
    ) -> SQLAlchemyBase:
        """Updates a record in the database based on a column value and returns the
        updated record. Raises an exception if the record isn't found or if the
        column doesn't exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            data (SnippetSchema): Pydantic schema for the updated data.
            id_ (str | UUID): value to search for in `column`
            column (str, optional): the column name in which to search
                Defaults to "uuid".
        Raises:
            NotFoundException: if the record isn't found
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            SnippetModel: updated SQLAlchemy model
        """
        db_model = self.get_one_by_id(session=session, id=id_, column=column)

        if not db_model:
            raise DataModelNotFound(
                f"{self.model_class.__tablename__} {column}={id_} not found.",
            )

        values = data.model_dump(exclude_unset=True)
        for k, v in values.items():
            setattr(db_model, k, v)

        try:
            session.commit()
            session.refresh(db_model)
            return db_model
        except IntegrityError:
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} {column}={id_} conflict with existing data.",
            )

    def update_many_by_ids(
        self,
        session: AsyncSession,
        updates: dict[str | UUID, ApiSchema],
        column: str = "id",
        return_models: bool = False,
    ) -> list[SQLAlchemyBase] | bool:
        """Updates multiple records in the database based on a column value and
        returns the updated records. Raises an exception if the column doesn't
        exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            updates (dict[str  |  UUID, SnippetSchema]): dictionary of id_ to
                Pydantic update schema
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            return_models (bool, optional): Should the created models be returned
                or a boolean indicating they have been created. Defaults to False.
                Defaults to False.

        Raises:
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            list[SnippetModel] | bool: list of updated SQLAlchemy models or boolean
        """
        updates = {str(id): update for id, update in updates.items() if update}
        ids = list(updates.keys())
        db_models = self.get_many_by_ids(
            session, ids=ids, column=column, with_for_update=True
        )

        for db_model in db_models:
            values = updates[str(getattr(db_model, column))].model_dump(
                exclude_unset=True
            )
            for k, v in values.items():
                setattr(db_model, k, v)
            session.add(db_model)

        try:
            session.commit()
        except IntegrityError:
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} conflict with existing data.",
            )

        if not return_models:
            return True

        for db_model in db_models:
            session.refresh(db_model)

        return db_models

    async def remove_by_id(
        self,
        session: AsyncSession,
        id_: str | UUID,
        column: str = "uuid",
    ) -> int:
        """Removes a record from the database based on a column value. Raises an
        exception if the column doesn't exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            id (str | UUID): value to search for in `column` and delete
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            SnippetException: if the column does not exist on the model

        Returns:
            int: number of rows removed, 1 if successful, 0 if not. Can be greater
                than 1 if id_ is not unique in the column.
        """
        try:
            query = delete(self.model_class).where(
                getattr(self.model_class, column) == id_
            )
        except AttributeError:
            raise DataModelException(
                f"Column {column} not found on {self.model_class.__tablename__}.",
            )

        rows = session.execute(query)
        session.commit()
        return rows.rowcount

    async def remove_many_by_ids(
        self,
        session: AsyncSession,
        ids: list[str | UUID],
        column: str = "uuid",
    ) -> int:
        """Removes multiple records from the database based on a column value.
        Raises an exception if the column doesn't exist.

        Args:
            session (AsyncSession): SQLAlchemy async session
            ids (list[str  |  UUID]): list of values to search for in `column` and
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            SnippetException: if ids is empty to stop deleting an entire table
            SnippetException: if column does not exist on the model

        Returns:
            int: number of rows removed, 1 or more if successful, 0 if not.
        """
        if not ids:
            raise DataModelException("No ids provided.")

        try:
            query = delete(self.model_class).where(
                getattr(self.model_class, column).in_(ids)
            )
        except AttributeError:
            raise DataModelException(
                f"Column {column} not found on {self.model_class.__tablename__}.",
            )
        rows = session.execute(query)
        return rows.rowcount
