from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as BaseSchemaModel


# todo add doc strings documenting error types that these functions can return + what they do
# Child classes should adhere to this even if not enforced
# This interface is more of a helper for dev to read and see what the interface is expected to do
class AbstractServiceRepository(ABC):
    """Base service repository class defining the interface that all service repositories must adhere to"""

    @abstractmethod
    def get(self, uuid: UUID) -> BaseSchemaModel:
        pass

    @abstractmethod
    def get_multiple(self, filters: dict) -> List[BaseSchemaModel]:
        pass

    @abstractmethod
    def create(self, create_schema: BaseSchemaModel) -> BaseSchemaModel:
        """

        :rtype: BaseSchemaModel
        """
        pass

    @abstractmethod
    def update(
        self,
        update_schema: BaseSchemaModel,
    ) -> BaseSchemaModel:
        pass

    @abstractmethod
    def delete(
        self,
        id: UUID,
    ) -> int:
        pass
