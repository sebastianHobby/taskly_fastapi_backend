from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseMixins import (
    HasNameAndOptionalDescription,
    HasId,
    HasCreatedAndUpdateTimestamps,
    DatabaseBaseModel,
)


class View(
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasNameAndOptionalDescription,
    DatabaseBaseModel,
):
    __tablename__ = "views"
    rules_json: Mapped[str] = mapped_column(JSONB, nullable=False)
