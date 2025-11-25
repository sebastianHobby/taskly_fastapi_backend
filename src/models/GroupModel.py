from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseMixins import (
    HasId,
    HasCreatedAndUpdateTimestamps,
    DatabaseBaseModel,
)


class Group(
    DatabaseBaseModel,
    HasId,
    HasCreatedAndUpdateTimestamps,
):
    name: Mapped[str] = mapped_column(TSVECTOR, nullable=False)
    description: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    __tablename__ = "groups"
    __table_args__ = (
        Index(
            "idx_group_name",
            name,
            postgresql_using="gin",
        ),
        Index(
            "idx_group_description",
            description,
            postgresql_using="gin",
        ),
    )
