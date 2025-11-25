from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseMixins import (
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
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
    HasNameAndOptionalDescription,
    HasOptionalStartAndDeadlineDates,
    HasForeignKeyTasklistId,
    DatabaseBaseModel,
):
    __tablename__ = "tasks"
    Index("idx_task_name", "name", postgresql_using="gin")
    Index("idx_task_description", "description", postgresql_using="gin")
