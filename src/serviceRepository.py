from typing import TypeAlias, List
from uuid import UUID
from pydantic import BaseModel as ApiSchema
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from .core.database import SQLAlchemyBase
from src.models import Project, Area, Task
from .core.model_util import *
from .schemas import (
    AreaGet,
    AreaUpdate,
    AreaCreate,
    ProjectCreate,
    ProjectGet,
    ProjectUpdate,
    TaskGet,
    TaskCreate,
    TaskUpdate,
)


# Service repository layer sits between our database layer (SQL alchemy models i.e. DAO) and
# REST API data structures defined in schemas i.e. DTOs.
# Client --> Rest API (Schemas) --> Repository (DAO - SQL alchemy Models)


class BaseServiceRepository(ABC):

    @abstractmethod
    def get_one_by_id(self, uuid: UUID, session: AsyncSession) -> ApiSchema:
        pass

    @abstractmethod
    def get_all(self, session: AsyncSession) -> List[ApiSchema]:
        pass

    @abstractmethod
    def search(
        self, filter_schema: ApiSchema, session: AsyncSession
    ) -> List[ApiSchema]:
        pass

    @abstractmethod
    def create(self, create_schema: ApiSchema, session: AsyncSession) -> ApiSchema:
        pass

    @abstractmethod
    def update(
        self, uuid: UUID, update_schema: ApiSchema, session: AsyncSession
    ) -> ApiSchema:
        pass

    @abstractmethod
    def delete(self, uuid: UUID, session: AsyncSession) -> int:
        pass


class ProjectRepository(BaseServiceRepository):
    def __init__(self):
        self.data_access = ModelCrudFunctions(model_class=Project)

    def get_one_by_id(self, id: UUID, session: AsyncSession) -> ProjectGet | None:
        db_project = self.data_access.get_one_by_id(id=id, session=session)
        return db_project

    def get_all(self, session: AsyncSession) -> List[AreaGet]:
        db_projects = self.data_access.get_all(session)
        if db_projects:
            return db_projects
        return []

    def search(self, filter_schema: ApiSchema, session: AsyncSession) -> List[AreaGet]:
        raise NotImplementedError()

    def create(self, create_schema: ProjectCreate, session: AsyncSession) -> ProjectGet:
        new_project = self.data_access.create(data=create_schema, session=session)
        return new_project

    def update(
        self, uuid: UUID, update_schema: ProjectUpdate, session: AsyncSession
    ) -> ProjectGet:
        updated_project = self.data_access.update_by_id(
            id_=uuid, data=update_schema, session=session
        )
        return updated_project

    def delete(self, uuid: UUID, session: AsyncSession) -> int:
        deleted_row_cnt = self.data_access.remove_by_id(
            session=session, id_=uuid, column=""
        )
        return deleted_row_cnt


class TaskRepository(BaseServiceRepository):
    def __init__(self):
        self.data_access = ModelCrudFunctions(model_class=Task)

    def get_one_by_id(self, uuid: UUID, session: AsyncSession) -> TaskGet | None:
        db_task = self.data_access.get_one_by_id(uuid, session)
        return db_task

    def get_all(self, session: AsyncSession) -> List[TaskGet]:
        db_task = self.data_access.get_all(session)
        if db_task:
            return db_task
        return []

    def search(self, filter_schema: ApiSchema, session: AsyncSession) -> List[TaskGet]:
        raise NotImplementedError()

    def create(self, create_schema: TaskCreate, session: AsyncSession) -> TaskGet:
        new_area = self.data_access.create(data=create_schema, session=session)
        return new_area

    def update(
        self, uuid: UUID, update_schema: TaskUpdate, session: AsyncSession
    ) -> TaskGet:
        updated_area = self.data_access.update_by_id(
            id_=uuid, data=update_schema, session=session
        )
        return updated_area

    def delete(self, uuid: UUID, session: AsyncSession) -> int:
        deleted_row_cnt = self.data_access.remove_by_id(
            id_=uuid, session=session, column="id"
        )
        return deleted_row_cnt


class AreaRepository(BaseServiceRepository):
    def __init__(self):
        self.data_access = ModelCrudFunctions(model_class=Area)

    def get_one_by_id(self, uuid: UUID, session: AsyncSession) -> AreaGet | None:
        db_area = self.data_access.get_one_by_id(uuid, session)
        return db_area

    def get_all(self, session: AsyncSession) -> List[AreaGet]:
        db_area = self.data_access.get_all(session)
        if db_area:
            return db_task
        return []

    def search(self, filter_schema: ApiSchema, session: AsyncSession) -> List[AreaGet]:
        raise NotImplementedError()

    def create(self, create_schema: AreaCreate, session: AsyncSession) -> AreaGet:
        new_area = self.data_access.create(data=create_schema, session=session)
        return new_area

    def update(
        self, uuid: UUID, update_schema: AreaUpdate, session: AsyncSession
    ) -> AreaGet:
        updated_area = self.data_access.update_by_id(
            id_=uuid, data=update_schema, session=session
        )
        return updated_area

    def delete(self, uuid: UUID, session: AsyncSession) -> int:
        deleted_row_cnt = self.data_access.remove_by_id(
            id_=uuid, session=session, column="id"
        )
        return deleted_row_cnt
