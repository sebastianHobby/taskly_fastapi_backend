from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel, ConfigDict, AwareDatetime

from src.models.db_models import TaskStatusValues


class TaskResponse(BaseSchemaModel):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_list_id: UUID
    created_date: AwareDatetime
    updated_date: AwareDatetime
    name: str
    status: TaskStatusValues

    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[AwareDatetime] = None
    deadline_date: Optional[AwareDatetime] = None


class TaskCreate(BaseSchemaModel):
    """Schema used by API consumers to create a Task"""

    model_config = ConfigDict(from_attributes=True)

    parent_list_id: UUID
    name: str
    status: Optional[TaskStatusValues] = TaskStatusValues.not_started
    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[AwareDatetime] = None
    deadline_date: Optional[AwareDatetime] = None


class TaskUpdate(BaseSchemaModel):
    """Schema used by API consumers to update a Task"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_list_id: UUID
    name: str
    status: Optional[TaskStatusValues] = TaskStatusValues.not_started
    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[AwareDatetime] = None
    deadline_date: Optional[AwareDatetime] = None
