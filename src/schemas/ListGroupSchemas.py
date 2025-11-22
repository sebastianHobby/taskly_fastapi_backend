from uuid import UUID
from datetime import datetime

import pydantic
from pydantic import ConfigDict

from pydantic import BaseModel as BaseSchemaModel


class ListGroupResponse(BaseSchemaModel):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str


class ListGroupCreate(BaseSchemaModel):
    """Schema used by API consumers to create a list group"""

    model_config = ConfigDict(from_attributes=True)
    name: str


class ListGroupUpdate(BaseSchemaModel):
    """Schema used by API consumers to update a list group"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
