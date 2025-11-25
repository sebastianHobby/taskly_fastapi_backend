from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

from src.models.DatabaseMixins import (
    HasId,
    HasCreatedAndUpdateTimestamps,
    DatabaseBaseModel,
)


class View(
    HasId,
    HasCreatedAndUpdateTimestamps,
    DatabaseBaseModel,
):
    __tablename__ = "views"
    rules: Mapped[str] = mapped_column(JSONB, nullable=False)
    name: Mapped[str] = mapped_column(TSVECTOR, nullable=False)
    description: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    __table_args__ = (
        Index(
            "idx_view_rules",
            rules,
            postgresql_using="gin",
        ),
    )
