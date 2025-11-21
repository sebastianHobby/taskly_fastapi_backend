from contextlib import AbstractContextManager
from typing import List, Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.models.db_models import DatabaseBaseModel
from src.repositories.AbstractRepository import AbstractServiceRepository
from src.schemas.ApiBaseSchema import ApiBaseSchema


class DataModelException(Exception):
    pass


class DataModelIntegrityConflictException(Exception):
    pass


class DataModelNotFound(Exception):
    pass


class DatabaseRepository(AbstractServiceRepository):
    def __init__(
        self,
        database_model_class: DatabaseBaseModel,
        public_schema_class: ApiBaseSchema,
        create_schema_class: ApiBaseSchema,
        update_schema_class: ApiBaseSchema,
        database_session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        # self.model_c = ModelCrudFunctions(model_class=Project)
        self.model_class = database_model_class
        self.public_schema = public_schema_class
        self.create_schema = create_schema_class
        self.update_schema = update_schema_class
        # Todo consider making this a input for dependency inversion / DIP - think about benefits vs trade offs first
        self.database_session_factory = database_session_factory
        self.pk_field_name = "id"

    async def _get_database_object_by_uuid(self, _uuid: UUID) -> DatabaseBaseModel:
        async with self.database_session_factory() as session:
            db_model = session.get(self.model_class, _uuid)
            if not db_model:
                raise DataModelNotFound()
            return db_model

    async def get_one_by_uuid(self, uuid: UUID) -> ApiBaseSchema | None:
        """Fetches one record from the database based on a UUID value in ID column and returns
        it, or returns None if it does not exist.
        Args:
            id ( UUID): value to search for in primary key column
        Raises:
            DataModelNotFound: if no data found
        Returns:
            DataModel: ApiBaseSchema model or None"""
        async with self.database_session_factory() as session:
            try:
                # Retrieve object from session if primary key matches id
                db_model = self._get_database_object_by_uuid(_uuid=uuid)
                response_schema = self.public_schema.model_validate(db_model)
            except Exception as e:
                raise
            if response_schema is None:
                raise DataModelNotFound()

            return response_schema

    async def get_all(self) -> List[ApiBaseSchema]:
        async with self.database_session_factory() as session:
            try:
                q = select(self.model_class)
                results = session.scalars(q).all()
                response_schemas = []
                for db in results:
                    response_schemas.append(self.public_schema.model_validate(db))
            except Exception as e:
                raise
            if response_schemas is None:
                return []
            return response_schemas

    async def create(self, create_schema: ApiBaseSchema) -> ApiBaseSchema:
        """Accepts a Pydantic model, creates a new record in the database, catches
        any integrity errors, and returns the record.

        Args:
            data (ApiSchema): Pydantic model
        Raises:
            DataModelIntegrityConflictException: if creation conflicts with existing data
            DataModelException: if an unknown error occurs

        Returns:
            DataModel: created SQLAlchemy model
        """
        async with self.database_session_factory() as session:
            try:
                db_model = self.model_class(**create_schema.model_dump())
                session.add(db_model)
                session.commit()
                session.refresh(db_model)
                response_schema = self.public_schema.model_validate(db_model)
                return response_schema
            except IntegrityError:
                # Raise nwe
                raise DataModelIntegrityConflictException(
                    f"{self.model_class.__tablename__} conflicts with existing data.",
                )
            except Exception as e:
                raise DataModelException(f"Unknown error occurred: {e}") from e

    async def update(self, uuid: UUID, update_schema: ApiBaseSchema) -> ApiBaseSchema:
        async with self.database_session_factory() as session:
            try:
                db_model = self._get_database_object_by_uuid(_uuid=uuid)
                update_values_dict = update_schema.model_dump(exclude_unset=True)
                # Update model
                for k, v in update_values_dict.items():
                    setattr(db_model, k, v)
                # Commiting session is smart enough to pick up ORM model updates
                session.commit()
                session.refresh(db_model)
                return self.public_schema.model_validate(db_model)
            except IntegrityError:
                raise DataModelIntegrityConflictException(
                    f"{self.model_class.__tablename__} Id ={UUID} conflict with existing data.",
                )
            except DataModelNotFound:
                raise

    async def delete(self, uuid: UUID) -> None:
        async with self.database_session_factory() as session:
            try:
                db_model = self._get_database_object_by_uuid(_uuid=uuid)
                session.delete(db_model)
                session.commit()
            except Exception as e:
                raise
