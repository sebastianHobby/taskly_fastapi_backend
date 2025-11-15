# Defines schemas (pydantic models) used as views passed in and out of your
# rest API operations.
from datetime import date, datetime, time, timedelta
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Defines schemas (pydantic models) used as views passed in and out of your
# rest API operations.
from datetime import datetime
from src.models import TaskContainerTypes
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# Todo find a way to stop type being updateable OR visible/exposed at all to API for update and delete
# Fields common to all task containers. Used to validate response to client/get requests for container.
class TaskContainerGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    id: UUID
    created_at: datetime
    name: str
    # Optional
    updated_at: datetime | None = None
    last_reviewed_date: datetime | None = None
    description: str | None = None
    parent_id: UUID | None = None


# Fields required to update any type of task container.
class TaskContainerCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    name: str
    # Optional
    description: str | None = None
    parent_id: UUID | None = None


# Fields required to update an existing task container.Same fields as update but we add ID.
# Note we do not expose the database generated fields like created_at
class TaskContainerUpdate(TaskContainerCreate):
    model_config = ConfigDict(from_attributes=True)
    # Mandatory fields
    id: UUID


# Now extend the base class create and get object with fields specific to each type of task container
class ProjectGet(TaskContainerGet):
    is_complete: bool
    deadline_date: datetime | None = None
    start_date: datetime | None = None
    type: TaskContainerTypes


class ProjectCreate(TaskContainerCreate):
    is_complete: bool | None = False
    deadline_date: datetime | None = None
    start_date: datetime | None = None


class ProjectUpdate(ProjectCreate):
    # Mandatory fields: Id + values
    id: UUID
    is_complete: bool
    deadline_date: datetime | None = None
    start_date: datetime | None = None


class AreaGet(TaskContainerGet):
    type: TaskContainerTypes
    pass


class AreaCreate(TaskContainerCreate):
    # Area only has the default task container fields with type of area
    pass


class AreaUpdate(AreaCreate):
    # Mandatory fields: Id + all the same fields as create operation
    id: UUID


# Todo refactor task models below
class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    is_complete: bool
    project_id: UUID | None = None
    area_id: UUID | None = None


class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str = Field(min_length=3, max_length=50)
    is_complete: bool = False
    description: str | None = None


class TaskGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None = None
    is_complete: bool
    createdAt: datetime
    updatedAt: datetime | None = None


# class BaseDatabaseModel(SQLModel):
#     """ Fields common to all database models """
#     id: Union[int, None] = Field(default=None, primary_key=True)
#     created_at: Union[datetime.datetime, None] = Field(default=datetime.datetime.now(), nullable=False)
#
# class TaskModel(SQLModel):
#     name: str = Field(index=True)
#     description: Union[str, None] = Field(default=None, index=True)
#     completed: bool = Field(default=False, index=True)
#
#
# class TaskDatabase(TaskModel,BaseDatabaseModel, table=True):
#     pass
