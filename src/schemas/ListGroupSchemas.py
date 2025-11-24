from uuid import UUID
from datetime import datetime

import pydantic
from pydantic import ConfigDict, AwareDatetime

from pydantic import BaseModel as BaseSchemaModel


class ListGroupResponse(BaseSchemaModel):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_date: AwareDatetime
    updated_datet: AwareDatetime
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


class ListGroupDelete(BaseSchemaModel):
    pass
