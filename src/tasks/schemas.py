# Defines schemas (pydantic models) used as views passed in and out of your
# rest API operations.
from datetime import date, datetime, time, timedelta
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


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
