from pydantic import ConfigDict

from pydantic import BaseModel

from src.schemas.SchemaMixins import (
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasNameAndOptionalDescription,
)


class GroupSelect(
    BaseModel, HasId, HasCreatedAndUpdateTimestamps, HasNameAndOptionalDescription
):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)


class GroupCreate(BaseModel, HasNameAndOptionalDescription):
    """Schema used by API consumers to create a list group"""

    model_config = ConfigDict(from_attributes=True)


class GroupUpdate(BaseModel, HasId, HasNameAndOptionalDescription):
    """Schema used by API consumers to update a list group"""

    model_config = ConfigDict(from_attributes=True)


class GroupDelete(BaseModel):
    pass
