from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from src.schemas.ApiBaseSchema import ApiBaseSchema


class TaskCreate(ApiBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    is_complete: bool
    parent_id: UUID | None = None


class TaskUpdate(ApiBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    uuid: UUID
    name: str = Field(min_length=3, max_length=50)
    is_complete: bool = False
    description: str | None = None


class TaskGet(ApiBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    uuid: UUID
    parent_id: UUID | None = None
    name: str
    description: str | None = None
    is_complete: bool
    created_at: datetime
    updated_at: datetime | None = None
