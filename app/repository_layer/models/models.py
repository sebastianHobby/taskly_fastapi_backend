from uuid import UUID

import sqlalchemy
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
    declared_attr,
)
from sqlalchemy_mixins.repr import ReprMixin
from sqlalchemy_mixins.serialize import SerializeMixin

from app.repository_layer.models.model_mixins import (
    HasOptionalStartAndDeadlineDates,
    HasCommonFields,
    HasStatus,
    HasOptionalDescription,
    HasRepeatFields,
)
from app.repository_layer.models.enumerations import ProjectTypes
from sqlalchemy.dialects.postgresql import JSONB


class DatabaseBaseModel(DeclarativeBase, ReprMixin, SerializeMixin):
    """Base model to allow us to define tables. Note we can not add fields here as it's not
    supported by SQL alchemy. SQL alchemy uses this base class as a way to link all metadata for various tables
    (represented by subclasses) together and create database schema.

    Uses sqlalchemy_mixins in 3rd party packager for serialisation (to dict) and pretty error messages
    """

    __abstract__ = True
    __repr__ = ReprMixin.__repr__

    pass


class Projects(
    HasCommonFields,
    HasStatus,
    HasOptionalDescription,
    HasOptionalStartAndDeadlineDates,
    HasRepeatFields,
    DatabaseBaseModel,
):
    """Represents a project which can contain child projects or tasks.
    Projects types such as area are used to apply business rules e.g. an area of focus/life value
    should not have a deadline"""

    __tablename__ = "projects"

    # Fields - Note several fields are inherited as mixin
    type: Mapped[ProjectTypes] = mapped_column(
        nullable=False, default=ProjectTypes.project
    )

    # Relationships
    child_project = relationship("Projects")
    parent_project_id = sqlalchemy.Column(
        sqlalchemy.UUID, sqlalchemy.ForeignKey("projects.id")
    )

    # Used for pretty printing with errors
    __repr_attrs__ = ["name"]  # we want to display name in repr string


class Tasks(
    HasCommonFields,
    HasOptionalDescription,
    HasStatus,
    HasOptionalStartAndDeadlineDates,
    HasRepeatFields,
    DatabaseBaseModel,
):
    __tablename__ = "tasks"

    # Fields - Note several fields are inherited as mixin
    project_id = sqlalchemy.Column(
        sqlalchemy.UUID, sqlalchemy.ForeignKey("projects.id"), nullable=True
    )
    parent_task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    child_task = relationship("Tasks")
    parent_project = relationship("Projects")

    # Define indexes and constraints
    __table_args__ = (
        CheckConstraint("coalesce(project_id , parent_task_id) is not null"),
    )  # One of the two must be not null

    # Used for pretty printing with errors
    __repr_attrs__ = ["name"]  # we want to display name in repr string


class Taskfilters(
    HasCommonFields,
    DatabaseBaseModel,
):
    __tablename__ = "taskfilters"

    # Fields - Note several fields are inherited as mixin
    rules = sqlalchemy.Column(JSONB, nullable=False)

    # Used for pretty printing with errors
    __repr_attrs__ = ["name"]  # we want to display name in repr string
