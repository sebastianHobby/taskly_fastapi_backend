from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ProjectModel import Project
from src.repositories.DatabaseRepository import DatabaseRepository
from src.schemas.ApiBaseSchema import ApiBaseSchema
from src.schemas.ProjectSchemas import ProjectCreate, ProjectGet, ProjectUpdate


class ProjectRepository(DatabaseRepository):
    def __init__(self):
        super().__init__(
            database_model_class=Project,
            create_schema_class=ProjectCreate,
            public_schema_class=ProjectGet,
            update_schema=ProjectUpdate,
        )

    def get_one_by_uuid(self, uuid: UUID) -> ProjectGet | None:
        return super().get_one_by_uuid(uuid=uuid)
        return db_project

    def get_all(self) -> List[ProjectGet]:
        return super().get_all()

    def create(self, create_schema: ProjectCreate) -> ProjectGet:
        return super().create(create_schema=create_schema)

    def update(self, uuid: UUID, update_schema: ProjectUpdate) -> ProjectGet:
        return super().update(update_schema=update_schema, uuid=uuid)

    def delete(self, uuid: UUID) -> None:
        return super().delete(uuid=uuid)
