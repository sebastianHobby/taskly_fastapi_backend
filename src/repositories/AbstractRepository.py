from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.ApiBaseSchema import ApiBaseSchema


# todo add doc strings documenting error types that these functions can return + what they do
# Child classes should adhere to this even if not enforced
# This interface is more of a helper for dev to read and see what the interface is expected to do
class AbstractServiceRepository(ABC):
    """Base service repository class defining the interface that all service repositories must adhere to"""

    @abstractmethod
    def get_one_by_uuid(self, uuid: UUID) -> ApiBaseSchema:
        pass

    @abstractmethod
    def get_all(self) -> List[ApiBaseSchema]:
        pass

    @abstractmethod
    def create(self, create_schema: ApiBaseSchema) -> ApiBaseSchema:
        pass

    @abstractmethod
    def update(
        self,
        uuid: UUID,
        update_schema: ApiBaseSchema,
    ) -> ApiBaseSchema:
        pass

    @abstractmethod
    def delete(
        self,
        uuid: UUID,
    ) -> int:
        pass
