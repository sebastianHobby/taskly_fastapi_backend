from uuid import UUID

import sqlalchemy
from sqlalchemy import Index, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database_mixins import (
    HasOptionalStartAndDeadlineDates,
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
    DatabaseBaseModel,
)


class Task(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
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
