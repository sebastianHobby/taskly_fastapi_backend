from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseMixins import (
    HasOptionalStartAndDeadlineDates,
    HasId,
    HasForeignKeyTasklistId,
    HasCreatedAndUpdateTimestamps,
    HasTaskOrProjectStatus,
    DatabaseBaseModel,
)


class Tasklist(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasOptionalStartAndDeadlineDates,
    DatabaseBaseModel,
    HasTaskOrProjectStatus,
):
    """Represents a list of tasks which can be a project or misc list"""

    name: Mapped[str] = mapped_column(TSVECTOR, nullable=False)
    description: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    __tablename__ = "tasklists"
    __table_args__ = (
        Index(
            "idx_tasklist_name",
            name,
            postgresql_using="gin",
        ),
        Index(
            "idx_tasklist_description",
            description,
            postgresql_using="gin",
        ),
    )
