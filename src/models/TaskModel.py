from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseMixins import (
    HasOptionalStartAndDeadlineDates,
    HasId,
    HasForeignKeyTasklistId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
    DatabaseBaseModel,
)


class Task(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
    HasOptionalStartAndDeadlineDates,
    HasForeignKeyTasklistId,
    DatabaseBaseModel,
):
    name: Mapped[str] = mapped_column(TSVECTOR, nullable=False)
    description: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    __tablename__ = "tasks"
    __table_args__ = (
        Index(
            "idx_task_name",
            name,
            postgresql_using="gin",
        ),
        Index(
            "idx_task_description",
            description,
            postgresql_using="gin",
        ),
    )
