from uuid import UUID

from sqlalchemy import Index, ForeignKey, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy_mixins.activerecord import ActiveRecordMixin

from src.models.database_mixins import (
    HasOptionalStartAndDeadlineDates,
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
    DatabaseBaseModel,
    Base,
)
from src.schemas.SchemaMixins import ProjectTypes
import sqlalchemy


class Project(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasOptionalStartAndDeadlineDates,
    HasTaskOrProjectStatus,
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
