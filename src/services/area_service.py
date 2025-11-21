"""Services layer is also known as orchestration layer.
API layer (routes) handles web stuff
Service layer handles any business rules and depends on Repository for access to data
API layer/Presentation --> Service Layer --> Repository
Note this is primarily to allow dependency injection and easy mocking/limiting cost of future changes
See https://github.com/cosmicpython/book/blob/master/chapter_04_service_layer.asciidoc
"""

from typing import List
from sqlalchemy import UUID
from src.repositories.AbstractRepository import AbstractServiceRepository
from src.schemas.AreaSchemas import AreaCreate, AreaUpdate, AreaGet


# Todo document what exceptions can be raised here - use doc strings so shows in IDE
# Todo add some validation for foreign key checks here
# Todo add some basic validation rules like Areas can only have parents of type (Area,Area) not Area
class AreaService:
    def __init__(self, repository: AbstractServiceRepository):
        # Note dependency injection of abstract service repository
        self.repository = repository

    def get_one_by_uuid(self, uuid: UUID) -> AreaGet:
        """Raises: DataModelNotFound: if no data found"""
        return self.repository.get_one_by_uuid(uuid)

    def get_all(self) -> List[AreaGet]:
        return self.repository.get_all()

    def create(self, create_schema: AreaCreate) -> AreaGet:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        return self.repository.create(create_schema)

    def update(self, update_schema: AreaUpdate) -> AreaGet:
        """Raises:
        DataModelIntegrityConflictException: if creation conflicts with existing data
        DataModelException: if an unknown error occurs"""
        return self.repository.update(update_schema)

    def delete(
        self,
        uuid: UUID,
    ) -> None:
        """Raises: DataModelNotFound: if no data found"""
        return self.repository.delete(uuid)
