from typing import List, Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from src.core.database import get_database_session
from src.models.db_models import Project, DatabaseBaseModel
from src.repositories.AbstractServiceRepository import AbstractServiceRepository
from src.schemas.ApiBaseSchema import ApiBaseSchema
from typing import List
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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
        database_session: Session,
    ) -> None:
        # self.model_c = ModelCrudFunctions(model_class=Project)
        self.model_class = database_model_class
        self.public_schema = public_schema_class
        self.create_schema = create_schema_class
        self.update_schema = update_schema_class
        # Todo consider making this a input for dependency inversion / DIP - think about benefits vs trade offs first
        self.database_session = database_session
        self.pk_field_name = "id"

    def _get_database_object_by_uuid(self, _uuid: UUID) -> DatabaseBaseModel:
        db_model = self.database_session.get(self.model_class, _uuid)
        if not db_model:
            raise DataModelNotFound()
        return db_model

    def get_one_by_uuid(self, uuid: UUID) -> ApiBaseSchema | None:
        """Fetches one record from the database based on a UUID value in ID column and returns
        it, or returns None if it does not exist.
        Args:
            id ( UUID): value to search for in primary key column
        Raises:
            DataModelNotFound: if no data found
        Returns:
            DataModel: ApiBaseSchema model or None"""
        try:
            # Retrieve object from session if primary key matches id
            db_model = self._get_database_object_by_uuid(_uuid=uuid)
            response_schema = self.public_schema.model_validate(db_model)
        except Exception as e:
            raise

        if response_schema is None:
            raise DataModelNotFound()

        return response_schema

    def get_all(self) -> List[ApiBaseSchema]:
        try:
            q = select(self.model_class)
            results = self.database_session.scalars(q).all()
            response_schemas = []
            for db in results:
                response_schemas.append(self.public_schema.model_validate(db))
        except Exception as e:
            raise
        if response_schemas is None:
            return []
        return response_schemas

    def create(self, create_schema: ApiBaseSchema) -> ApiBaseSchema:
        # Todo implement parent / foreign key errors with helpful text. May require service layer
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
        try:
            db_model = self.model_class(**create_schema.model_dump())
            self.database_session.add(db_model)
            self.database_session.commit()
            self.database_session.refresh(db_model)
            response_schema = self.public_schema.model_validate(db_model)
            return response_schema
        except IntegrityError:
            # Raise nwe
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} conflicts with existing data.",
            )
        except Exception as e:
            raise DataModelException(f"Unknown error occurred: {e}") from e

        new_project = self.data_access.create(
            data=create_schema, session=self.database_session
        )
        return new_project

    def update(self, uuid: UUID, update_schema: ApiBaseSchema) -> ApiBaseSchema:
        try:
            db_model = self._get_database_object_by_uuid(_uuid=uuid)
            update_values_dict = update_schema.model_dump(exclude_unset=True)
            # Update model
            for k, v in update_values_dict.items():
                setattr(db_model, k, v)
            # Commiting session is smart enough to pick up ORM model updates
            self.database_session.commit()
            self.database_session.refresh(db_model)
            return self.public_schema.model_validate(db_model)
        except IntegrityError:
            raise DataModelIntegrityConflictException(
                f"{self.model_class.__tablename__} Id ={UUID} conflict with existing data.",
            )
        except DataModelNotFound:
            raise

    def delete(self, uuid: UUID) -> None:
        try:
            db_model = self._get_database_object_by_uuid(_uuid=uuid)
            self.database_session.delete(db_model)
            self.database_session.commit()
        except Exception as e:
            raise
