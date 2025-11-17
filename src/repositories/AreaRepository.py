from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.AreaModel import Area
from src.repositories import AreaRepository
from src.repositories.DatabaseRepository import DatabaseRepository
from src.schemas.AreaSchemas import AreaCreate, AreaUpdate, AreaGet


class AreaRepository(DatabaseRepository):
    def __init__(self):
        super().__init__(
            database_model_class=Area,
            create_schema_class=AreaCreate,
            public_schema_class=AreaGet,
            update_schema=AreaUpdate,
        )

    def get_one_by_uuid(self, uuid: UUID) -> AreaGet | None:
        return super().get_one_by_uuid(uuid=uuid)
        return db_area

    def get_all(self) -> List[AreaGet]:
        return super().get_all()

    def create(self, create_schema: AreaCreate) -> AreaGet:
        return super().create(create_schema=create_schema)

    def update(self, uuid: UUID, update_schema: AreaUpdate) -> AreaGet:
        return super().update(update_schema=update_schema, uuid=uuid)

    def delete(self, uuid: UUID) -> None:
        return super().delete(uuid=uuid)
