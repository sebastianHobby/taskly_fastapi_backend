from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, conint, PositiveInt


class CommonSearchFieldsSchema(BaseModel):
    """Defines search fields common to all resources"""

    id: Annotated[UUID, Field(description="The ID of a specific project")] = None
    ids: Annotated[tuple[UUID], Field(description="A list of Ids to return")] = None
    name: Annotated[
        UUID, Field(description="The name of project, case insensitive search")
    ] = None

    page: int = Field(100, ge=1, le=1000, description="The page number to return")
    itemsPerPage: int = Field(50, ge=1, le=200, description="The page number to return")

    @computed_field
    @property
    def pagination(self) -> tuple:
        limit = self.itemsPerPage
        offset = (self.page - 1) * self.itemsPerPage
        return (limit, offset)
