from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.TaskModel import Task
from src.repositories.DatabaseRepository import DatabaseRepository
from src.schemas.ApiBaseSchema import ApiBaseSchema
from src.schemas.TaskSchemas import TaskCreate, TaskGet, TaskUpdate


class TaskRepository(DatabaseRepository):
    def __init__(self):
        super().__init__(
            database_model_class=Task,
            create_schema_class=TaskCreate,
            public_schema_class=TaskGet,
            update_schema=TaskUpdate,
        )

    def get_one_by_uuid(self, uuid: UUID) -> TaskGet | None:
        return super().get_one_by_uuid(uuid=uuid)
        return db_task

    def get_all(self) -> List[TaskGet]:
        return super().get_all()

    def create(self, create_schema: TaskCreate) -> TaskGet:
        return super().create(create_schema=create_schema)

    def update(self, uuid: UUID, update_schema: TaskUpdate) -> TaskGet:
        return super().update(update_schema=update_schema, uuid=uuid)

    def delete(self, uuid: UUID) -> None:
        return super().delete(uuid=uuid)
