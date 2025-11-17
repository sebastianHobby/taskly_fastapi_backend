from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict

from src.schemas.ApiBaseSchema import ApiBaseSchema


class TaskContainerGet(ApiBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    uuid: UUID
    created_at: datetime
    name: str
    # Optional
    updated_at: datetime | None = None
    last_reviewed_date: datetime | None = None
    description: str | None = None
    parent_id: UUID | None = None


class TaskContainerCreate(ApiBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    name: str
    # Optional
    description: str | None = None
    parent_id: UUID | None = None


class TaskContainerUpdate(TaskContainerCreate):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    uuid: UUID
