from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel as BaseSchemaModel

from src.models.db_models import TaskStatusValues


class TaskResponse(BaseSchemaModel):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    id: UUID
    parent_list_id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    status: TaskStatusValues

    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None


class TaskCreate(BaseSchemaModel):
    """Schema used by API consumers to create a Task"""

    parent_list_id: UUID
    name: str
    status: Optional[TaskStatusValues] = TaskStatusValues.not_started
    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None


class TaskUpdate(BaseSchemaModel):
    """Schema used by API consumers to update a Task"""

    id: UUID
    parent_list_id: UUID
    name: str
    status: Optional[TaskStatusValues] = TaskStatusValues.not_started
    # Optional fields
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
