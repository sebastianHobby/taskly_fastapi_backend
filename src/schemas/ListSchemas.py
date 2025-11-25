from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, Field, AwareDatetime

from pydantic import BaseModel as BaseSchemaModel

from src.schemas.SchemaMixins import (
    HasCreatedAndUpdateTimestamps,
    HasId,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasGroupId,
    HasTaskOrProjectStatus,
)


class TasklistSelect(
    BaseSchemaModel,
    HasId,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasGroupId,
    HasTaskOrProjectStatus,
):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)


class TasklistCreate(
    BaseSchemaModel,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasGroupId,
    HasTaskOrProjectStatus,
):
    """Schema used by API consumers to create a Tasklist"""

    model_config = ConfigDict(from_attributes=True)


class TasklistUpdate(
    BaseSchemaModel,
    HasId,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasGroupId,
    HasTaskOrProjectStatus,
):
    """Schema used by API consumers to update a Tasklist"""

    model_config = ConfigDict(from_attributes=True)


class TasklistDelete(BaseSchemaModel):
    pass
