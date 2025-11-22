from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict

from pydantic import BaseModel as BaseSchemaModel

from src.models.db_models import TaskListTypes, ListStatusValues


class TaskListResponse(BaseSchemaModel):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    parent_group_id: UUID
    type: TaskListTypes
    name: str

    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    status: Optional[ListStatusValues] = None


class TaskListCreate(BaseSchemaModel):
    """Schema used by API consumers to create a TaskList"""

    model_config = ConfigDict(from_attributes=True)
    parent_group_id: UUID
    type: TaskListTypes
    name: str
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    status: Optional[ListStatusValues] = None


class TaskListUpdate(BaseSchemaModel):
    """Schema used by API consumers to update a TaskList"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    parent_group_id: UUID
    name: str
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    status: Optional[ListStatusValues] = None
    type: TaskListTypes  # Note this allows changing types. Needs appropiate validation.
