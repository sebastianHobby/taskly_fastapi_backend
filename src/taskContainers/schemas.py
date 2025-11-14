# Defines schemas (pydantic models) used as views passed in and out of your
# rest API operations.
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AreaGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None
    name: str


class AreaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class AreaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str


class ProjectGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None
    name: str
    description: str | None = None
    is_complete: bool
    deadline_date: datetime | None = None
    last_review_date: datetime | None = None
    area_id: UUID | None = None


class ProjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    is_complete: bool
    deadline_date: datetime | None = None
    area_id: UUID | None = None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None = None
    is_complete: bool | None = None
    deadline_date: datetime | None = None
    area_id: UUID | None = None


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
