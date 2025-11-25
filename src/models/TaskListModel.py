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


class Tasklist(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasNameAndOptionalDescription,
    HasOptionalStartAndDeadlineDates,
    DatabaseBaseModel,
    HasTaskOrProjectStatus,
):
    """Represents a list of tasks which can be a project or misc list"""

    __tablename__ = "tasklist"
    Index("idx_tasklist_name", "name", postgresql_using="gin")
    Index("idx_tasklist_description", "description", postgresql_using="gin")
