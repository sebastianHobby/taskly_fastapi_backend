from contextlib import AbstractContextManager
from typing import List, Callable, TypeVar, Generic, Any, Coroutine
from uuid import UUID

from sqlalchemy import select, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import or_
from sqlmodel import Session
from sqlalchemy.orm import DeclarativeBase, DeclarativeMeta

from src.repositories.AbstractRepository import AbstractServiceRepository

from pydantic import BaseModel as BaseSchemaModel

from src.repositories.RepositoryExceptions import (
    DataModelIntegrityConflictException,
    DataModelNotFound,
)

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchema = TypeVar("CreateSchema")
UpdateSchema = TypeVar("UpdateSchema")
ResponseSchema = TypeVar("ResponseSchema")


class DatabaseRepository(
    Generic[ModelType, CreateSchema, UpdateSchema, ResponseSchema],
    AbstractServiceRepository,
):
    def __init__(
        self,
        database_model_class: ModelType,
        response_schema_class: ResponseSchema,
        create_schema_class: CreateSchema,
        update_schema_class: UpdateSchema,
        database_session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        # self.model_c = ModelCrudFunctions(model_class=Project)
        self.model_class = database_model_class
        self.response_schema = response_schema_class
        self.create_schema = create_schema_class
        self.update_schema = update_schema_class
        self.database_session_factory = database_session_factory
        self.pk_field_name = "id"

    def _data_model_to_response_schema(
        self, data_model: ModelType
    ) -> ResponseSchema | None:
        if data_model:
            return self.response_schema.model_validate(data_model)
        return None

    async def get(self, id: UUID) -> ResponseSchema | None:
        async with self.database_session_factory() as session:
            db_model = await session.get(self.model_class, id)
            return self._data_model_to_response_schema(data_model=db_model)

    async def get_multiple(self, filters: dict = None) -> List[ResponseSchema]:
        async with self.database_session_factory() as session:
            q = select(self.model_class)
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field) and value is not None:
                        query = query.filter(getattr(self.model_class, field) == value)

            results = session.scalars(q).all()
            response_schemas: List[BaseSchemaModel] = []
            for db in results:
                response_schemas.append(
                    self._data_model_to_response_schema(data_model=db)
                )
            return response_schemas

    async def create(self, create_schema: CreateSchema) -> ResponseSchema:
        async with self.database_session_factory() as session:
            try:
                db_model = self.model_class(**create_schema.model_dump())
                session.add(db_model)
                await session.commit()

                await session.refresh(db_model)
                return self._data_model_to_response_schema(data_model=db_model)
            except IntegrityError:
                raise DataModelIntegrityConflictException(
                    f"{self.model_class.__tablename__} conflicts with existing data.",
                )

    async def update(self, update_schema: UpdateSchema) -> ResponseSchema:
        async with self.database_session_factory() as session:
            db_model = await session.get(self.model_class, update_schema.id)
            if db_model is None:
                raise DataModelNotFound
            try:
                update_values_dict = update_schema.model_dump(exclude_unset=True)
                for k, v in update_values_dict.items():
                    setattr(db_model, k, v)
                # Commiting session is smart enough to pick up ORM model updates
                session.commit()
                session.refresh(db_model)
                return self._data_model_to_response_schema(data_model=db_model)
            except IntegrityError:
                raise DataModelIntegrityConflictException(
                    f"{self.model_class.__tablename__} Id ={UUID} conflict with existing data.",
                )

    async def delete(self, id: UUID) -> bool:
        async with self.database_session_factory() as session:
            db_model = await session.get(self.model_class, id)
            if db_model is None:
                raise DataModelNotFound
            session.delete(db_model)
            session.commit()
            return True


# async def index(
#     self,
#     params: Params,
#     filters: Optional[Dict[str, Any]] = None,
#     search_fields: Optional[list[str]] = None,
#     search_query: Optional[str] = None,
#     sort_field: Optional[str] = None,
#     sort_order: str = "desc",
#     load_relations: list[str] = None,
# ) -> Page[ModelType]:
#     query = select(self.model)
#
#     # Apply Filters
#     if filters:
#         for field, value in filters.items():
#             if hasattr(self.model, field) and value is not None:
#                 query = query.filter(getattr(self.model, field) == value)
#
#     # Apply Search
#     if search_query and search_fields:
#         search_conditions = [
#             getattr(self.model, field).ilike(f"%{search_query}%")
#             for field in search_fields
#             if hasattr(self.model, field)
#         ]
#         if search_conditions:
#             query = query.filter(or_(*search_conditions))
#
#     # Apply Sorting
#     if sort_field and hasattr(self.model, sort_field):
#         order_func = asc if sort_order.lower() == "asc" else desc
#         query = query.order_by(order_func(getattr(self.model, sort_field)))
#     else:
#         query = query.order_by(desc(self.model.id))
#
#     # Load Relations
#     if load_relations:
#         for relation in load_relations:
#             query = query.options(selectinload(getattr(self.model, relation)))
#
#     return await paginate(self.db, query, params)
