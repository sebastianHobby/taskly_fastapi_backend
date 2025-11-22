import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, Column, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


# Mixin and enum classes
class ListStatusValues(Enum):
    not_started = "Not started"
    in_progress = "In progress"
    completed = "Completed"


class TaskListTypes(Enum):
    project = "Project"
    list = "List"


class TaskStatusValues(Enum):
    not_started = "Not started"
    completed = "Completed"


class DatabaseBaseModel(DeclarativeBase):
    pass


class hasCommonDatabaseFields:
    """Defines common fields for all database models"""

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}

    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


# The actual database models
class ListGroup(hasCommonDatabaseFields, DatabaseBaseModel):
    __tablename__ = "task_list_groups"
    name: Mapped[str]


class TaskList(hasCommonDatabaseFields, DatabaseBaseModel):
    """Represents a list of tasks which can be a project or misc list"""

    __tablename__ = "task_lists"
    type: Mapped[
        TaskListTypes
    ]  # See enum for description of the type and associated business rules
    name: Mapped[str]
    notes: Mapped[str] = mapped_column(String, nullable=True)
    deadline_date: Mapped[datetime] = mapped_column(nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    parent_group_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_list_groups.id"), nullable=True
    )
    status: Mapped[ListStatusValues] = mapped_column(nullable=True)


class Task(hasCommonDatabaseFields, DatabaseBaseModel):
    __tablename__ = "tasks"
    name: Mapped[str]
    notes: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    deadline_date: Mapped[datetime] = mapped_column(nullable=True)
    status: Mapped[TaskStatusValues] = mapped_column(
        nullable=True, default=TaskStatusValues.not_started
    )

    parent_list_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_lists.id"), nullable=True
    )
