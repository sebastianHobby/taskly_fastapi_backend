from uuid import UUID

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy_mixins.repr import ReprMixin
from sqlalchemy_mixins.serialize import SerializeMixin

from app.repository_layer.models.model_mixins import (
    HasOptionalStartAndDeadlineDates,
    HasCommonFields,
    HasStatus,
)
from app.repository_layer.models.enumerations import ProjectTypes
import sqlalchemy
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


class Project(
    HasCommonFields,
    HasOptionalStartAndDeadlineDates,
    HasStatus,
    DatabaseBaseModel,
):
    """Represents a project which can contain child projects or tasks.
    Project types such as area are used to apply business rules e.g. an area of focus/life value
    should not have a deadline"""

    __tablename__ = "projects"
    __repr_attrs__ = ["name"]  # we want to display name in repr string
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type: Mapped[ProjectTypes] = mapped_column(
        nullable=False, default=ProjectTypes.project
    )

    child_project = relationship("Project")
    parent_project_id = sqlalchemy.Column(
        sqlalchemy.UUID, sqlalchemy.ForeignKey("projects.id")
    )


class Task(
    HasCommonFields,
    HasStatus,
    HasOptionalStartAndDeadlineDates,
    DatabaseBaseModel,
):
    __repr_attrs__ = ["name"]  # we want to display name in repr string
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    project_id = sqlalchemy.Column(
        sqlalchemy.UUID, sqlalchemy.ForeignKey("projects.id"), nullable=True
    )
    parent_task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    child_task = relationship("Task")
    parent_project = relationship("Project")

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("coalesce(project_id , parent_task_id) is not null"),
    )  # One of the two must be not null


class Filter(
    HasCommonFields,
    DatabaseBaseModel,
):
    __repr_attrs__ = ["name"]  # we want to display name in repr string
    name: Mapped[str] = mapped_column(nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    filter_as_json = sqlalchemy.Column(JSONB, nullable=False)
    __tablename__ = "filters"
