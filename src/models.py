# Database models
import typing
import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, String, Boolean, types, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import declared_attr
from src.core.database import Base
from enum import Enum

# The code below uses SqlAlchemy to define models which follow the
# Class table inheritance pattern aka joined table inheritance
# See https://ruheni.dev/writing/sql-table-inheritance/ and
# https://ruheni.dev/writing/sql-table-inheritance/ for background


# Mix in classes defined by SqlAlchemy see https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
# Used to add common fields or relationship to tables - i.e. composition (not inheritance)
class HasCommonFields:
    """Defines common fields for all tables"""

    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )


class HasStartDateAndDeadline:
    deadline_date: Mapped[datetime] = mapped_column(nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)


class TaskContainerTypes(Enum):
    project = "project"
    area = "area"


# Base class defining what a task container looks like
# Container examples might be Areas , projects etc
# SQL alchemy framewok sets up single table inheritance
# model to match class hierachy defined here with TaskContainer + Children
# See https://docs.sqlalchemy.org/en/20/orm/inheritance.html
class TaskContainer(Base, HasCommonFields):
    __tablename__ = "task_containers"

    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    last_reviewed_date: Mapped[datetime] = mapped_column(
        nullable=True
    )  # Last user review of this task container
    # Self reference i.e. Adjacent list design pattern for hierarchy structure
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.id"), nullable=True
    )
    children = relationship("TaskContainer")
    # Discriminator attribute
    type: Mapped[TaskContainerTypes]
    __mapper_args__ = {
        "polymorphic_identity": "task_containers",
        "polymorphic_on": "type",
    }


class Area(TaskContainer):
    # Tell SQL alchemy to refer to this table when task_container.type = project
    __mapper_args__ = {"polymorphic_identity": TaskContainerTypes.area}


class Project(TaskContainer, HasStartDateAndDeadline):
    # Tell SQL alchemy to refer to this table when Area.type = project
    __mapper_args__ = {
        "polymorphic_identity": TaskContainerTypes.project,
    }
    # Project specific fields

    is_complete: Mapped[bool] = mapped_column(default=False)


# Now switch to task model
class Task(Base, HasCommonFields, HasStartDateAndDeadline):
    __tablename__ = "tasks"
    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_complete = Column(Boolean, nullable=False, default=False)
    container_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.id"), nullable=True
    )
